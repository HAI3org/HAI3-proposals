# Missing Declarative Metadata for Discovery and Preloading

## Problem

The `MfManifest` type contains only loading configuration (remoteEntry, remoteName, shared dependencies) but lacks declarative metadata that would allow the parent application to discover MFE capabilities, routes, and requirements **before** executing JavaScript code.

**Current MfManifest structure:**

```typescript
interface MfManifest {
  id: string;
  remoteEntry: string;              // Where to load from
  remoteName: string;               // Module Federation name
  sharedDependencies?: SharedDependencyConfig[];  // What to share
  entries?: string[];               // Just type IDs (opaque strings)
}
```

**What's missing:**
- No route information
- No feature flag declarations
- No capabilities metadata
- No translation file declarations
- No way to discover what MFE provides without loading it

## Use Cases That Require Advance Metadata

### Use Case 1: Route-Specific Asset Preloading in SSR

**Fragment System approach:**
```typescript
// Server-side: Download manifest.json (small JSON, no JS execution)
const manifest = await fetch('https://cdn.example.com/fragments/manifest.main.abc123.json')
  .then(r => r.json());

// Discover routes from manifest
const routes = manifest.entries.flatMap(entry =>
  entry.components.flatMap(comp => comp.routes || [])
);

// Add preload hints for current route
const currentRoute = routes.find(r => r.path === req.url);
if (currentRoute && currentRoute.file) {
  html += `<link rel="modulepreload" href="${currentRoute.file}">`;
}

// Send HTML with assets preloaded
res.send(html);
```

**MFE System problem:**
```typescript
// Server-side: Can only download manifest
const manifest = await fetch('https://api.example.com/mfe-registry/analytics')
  .then(r => r.json());

// Cannot discover routes - no route information in manifest
// Cannot add preload hints - don't know which files are for which routes

// Send HTML without preload hints
res.send(html);

// Browser must:
// 1. Load remoteEntry.js (~10KB)
// 2. Execute JavaScript to discover exposed modules
// 3. Load MFE entry code (no preload = extra round trip)
// 4. Execute code to discover routes
```

**Impact:** Extra round trips, no preload optimization, slower initial navigation.

### Use Case 2: Feature Flags Visibility for Debugging and Admin

**Fragment System approach:**
```typescript
// Backend/Admin panel: List all fragments and their feature flags
const manifests = await fetchAllManifests();

// Build feature flag usage map
const featureFlagUsage = manifests.map(m => ({
  fragment: m.name,
  flags: m.featureFlags,  // Declared in manifest
}));

// Display in admin panel:
// Analytics Fragment: ['advanced-analytics', 'export-reports']
// Billing Fragment: ['invoice-export', 'payment-methods-v2']
// Dashboard Fragment: ['widgets-v2', 'custom-layouts']

// Debug window can show:
// - Which fragments are loaded
// - What flags each fragment expects
// - Which flags are currently enabled
// - Mismatches between expected and available flags
```

**MFE System problem:**
```typescript
// Backend/Admin panel: List all MFEs
const manifests = await fetchAllManifests();

// No featureFlags field in manifest
// Cannot build feature flag usage map
// Cannot show what flags each MFE uses

// Must either:
// 1. Maintain separate documentation of flag usage
// 2. Load all MFEs to discover their flags at runtime
// 3. Have no visibility into flag dependencies

// Debug window cannot show flag relationships without loading code
```

**Impact:** Poor debugging experience, no visibility into feature flag usage without loading all MFEs, difficult to audit which features depend on which flags.

### Use Case 3: Translation File Preloading in SSR

**Fragment System approach:**
```typescript
// Fragment manifest declares translations
{
  "name": "analytics",
  "translations": {
    "files": {
      "en": "locales/en.abc123.json",
      "de": "locales/de.def456.json",
      "fr": "locales/fr.ghi789.json"
    },
    "namespace": "analytics"
  }
}

// Server-side: Add preload hints for translation files
const locale = req.headers['accept-language']?.split(',')[0] || 'en';
const translationUrl = manifest.translations?.files[locale];

if (translationUrl) {
  // Add prefetch link for translation file
  html += `<link rel="prefetch" href="${CDN_BASE}/${translationUrl}">`;
}

// Send HTML with preload hints
res.send(html);

// Browser: Translation file prefetched, loads quickly when fragment requests it
const fragment = await loadFragment(manifest.name);
// Fragment requests translations via localization service
// Already prefetched = instant load
```

**MFE System problem:**
```typescript
// Server-side: Manifest has no translation metadata
const manifest = await fetch('https://api.example.com/mfe-registry/analytics')
  .then(r => r.json());

// Cannot discover translation files
// Cannot add preload hints for translations

// Send HTML without preload hints
res.send(html);

// Browser must:
// 1. Load remoteEntry.js
// 2. Execute MFE code
// 3. MFE requests translations
// 4. Load translation files (no prefetch = extra round trip)
// 5. Re-render with translations
// Result: Extra round trip, delayed rendering
```

**Impact:** Extra round trip for translation loading, no prefetch optimization, delayed MFE rendering.

### Use Case 4: Merged Manifests in SSR for Reduced Round Trips

**Fragment System approach:**
```typescript
// Server-side: Fetch all fragment manifests
const manifests = await Promise.all([
  fetch('https://cdn.example.com/analytics/manifest.main.abc123.json').then(r => r.json()),
  fetch('https://cdn.example.com/billing/manifest.main.def456.json').then(r => r.json()),
  fetch('https://cdn.example.com/dashboard/manifest.main.ghi789.json').then(r => r.json()),
]);

// Merge all manifests into a single object
const mergedManifests = {
  analytics: manifests[0],
  billing: manifests[1],
  dashboard: manifests[2],
};

// Include merged manifests in initial HTML
html += `
  <script>
    window.__FRAGMENT_MANIFESTS__ = ${JSON.stringify(mergedManifests)};
  </script>
`;

// Add preload hints for current route from all manifests
manifests.forEach(manifest => {
  const routes = manifest.entries.flatMap(entry =>
    entry.components.flatMap(comp => comp.routes || [])
  );
  const currentRoute = routes.find(r => r.path === req.url);
  if (currentRoute?.file) {
    html += `<link rel="modulepreload" href="${currentRoute.file}">`;
  }

  // Prefetch translations for current locale
  const locale = req.headers['accept-language']?.split(',')[0] || 'en';
  const translationUrl = manifest.translations?.files[locale];
  if (translationUrl) {
    html += `<link rel="prefetch" href="${CDN_BASE}/${translationUrl}">`;
  }
});

// Send HTML with all manifests included
res.send(html);

// Client-side: No extra requests needed
const manifests = window.__FRAGMENT_MANIFESTS__;
// All manifests available immediately
// Can configure routes, check feature flags, discover capabilities
// Zero extra round trips
```

**MFE System problem:**
```typescript
// Server-side: Cannot merge MFE manifests
// (MfManifest doesn't have enough metadata to be useful)

// Send HTML without manifests
res.send(html);

// Client-side: Must fetch each manifest separately
const analyticsManifest = await fetch('https://api.example.com/mfe-registry/analytics').then(r => r.json());
const billingManifest = await fetch('https://api.example.com/mfe-registry/billing').then(r => r.json());
const dashboardManifest = await fetch('https://api.example.com/mfe-registry/dashboard').then(r => r.json());

// 3 separate round trips
// Blocks rendering until all manifests fetched
// Cannot optimize with SSR
```

**Impact:** Extra round trips for each MFE manifest, delayed initialization, cannot leverage SSR to reduce client-side requests.

### Use Case 5: Route Metadata for Client-Side Parent App Configuration

**Fragment System approach:**
```typescript
// Manifest declares routes with metadata
{
  "name": "analytics",
  "entries": [{
    "components": [{
      "name": "dashboard",
      "routes": [
        {
          "path": "/analytics",
          "meta": { "mode": "default" }
        },
        {
          "path": "/analytics/presentation",
          "meta": { "mode": "fullscreen" }  // Parent knows to hide menu
        },
        {
          "path": "/analytics/embedded",
          "meta": {
            "mode": "embedded",
            "hideHeader": true,
            "hideFooter": true
          }
        }
      ]
    }]
  }]
}

// Client-side: Configure routes with metadata from manifest
manifest.entries.forEach(entry => {
  entry.components?.forEach(comp => {
    comp.routes?.forEach(route => {
      router.addRoute({
        path: route.path,
        meta: route.meta,  // Parent configures UI based on meta
        component: () => loadFragment(manifest.name, comp.name),
      });
    });
  });
});

// Router navigation guard uses meta
router.beforeEach((to, from, next) => {
  // Apply configuration BEFORE loading fragment
  if (to.meta.mode === 'fullscreen') {
    hideMenu();
    hideHeader();
    hideFooter();
  } else {
    showMenu();
    showHeader();
    showFooter();
  }
  next();
});

// Benefits:
// 1. Parent app configures UI before fragment loads
// 2. No flash of wrong layout
// 3. Fragment doesn't need to communicate layout preferences at runtime
```

**MFE System problem:**
```typescript
// Manifest provides no route metadata
{
  "remoteEntry": "https://cdn.acme.com/analytics/remoteEntry.js",
  "entries": ["gts.acme.analytics.mfe.entry.v1~hai3.mfe.entry_mf.v1:dashboard"]
}

// Cannot configure parent UI based on route
// Must wait for MFE to load and communicate preferences

// Sequence with missing metadata:
// 1. User navigates to /analytics/presentation
// 2. Parent app renders with default layout (menu visible)
// 3. Load and mount MFE
// 4. MFE executes, detects it needs fullscreen mode
// 5. MFE communicates via bridge: "hide menu please"
// 6. Parent app hides menu
// Result: Flash of menu before hiding

// Must maintain separate configuration:
const routeConfig = {
  '/analytics': { mfe: 'analytics', meta: { mode: 'default' } },
  '/analytics/presentation': { mfe: 'analytics', meta: { mode: 'fullscreen' } },
  '/analytics/embedded': { mfe: 'analytics', meta: { mode: 'embedded', hideHeader: true } },
};

// Problems:
// 1. Configuration separate from MFE (duplication)
// 2. Can drift out of sync with MFE's actual routes
// 3. Manual maintenance required
```

**Impact:**
- **Layout flashing** - Parent app cannot configure UI before MFE loads, causing visual flicker
- **Runtime communication overhead** - MFE must communicate layout preferences via bridge after loading
- **Configuration drift** - Route metadata maintained separately from MFE, can become stale

## Comparison with Fragment System

**Fragment System manifest includes:**

```typescript
type FragmentManifest = {
  name: string;
  version: string;
  artifacts: ViteManifest;           // File mappings
  translations?: FragmentManifestTranslations;  // Localization files
  entries: FragmentManifestEntry[];   // Rich entry metadata
  featureFlags: FragmentManifestFeatureFlag[];  // Required flags
};

type FragmentManifestEntry = {
  name: string;
  file: string;                       // Entry file path
  components?: FragmentManifestComponent[];  // Components list
  methods?: FragmentManifestMethod[]; // Methods list
};

type FragmentManifestComponent = {
  name: string;
  routes?: FragmentRouteRecord[];     // Route declarations
};

type FragmentRouteRecord = {
  path: string;
  name?: string;
  meta?: Record<string, unknown>;
  file?: string;                      // Route-specific file
  children?: FragmentRouteRecord[];
};
```

**Benefits:**
- Parent app can read manifest (JSON) without executing JavaScript
- SSR can configure routes and add preload hints
- Backend can make decisions based on feature flags
- Route-specific assets can be preloaded
- All metadata available before loading any code

## What MFE System Needs

**Add declarative metadata to MfManifest:**

```typescript
interface MfManifest {
  id: string;
  remoteEntry: string;
  remoteName: string;
  sharedDependencies?: SharedDependencyConfig[];

  // NEW: Declarative metadata
  entries?: MfManifestEntryMetadata[];  // Rich metadata instead of just type IDs
  featureFlags?: string[];              // Required feature flags
  translations?: {
    files: Record<string, string>;      // locale -> translation file URL with content hash
    namespace: string;                   // i18n namespace for this MFE
    defaultLocale?: string;              // Fallback locale
  };
  capabilities?: {
    routes?: RouteDefinition[];         // What routes this MFE handles
    supportedDomains?: string[];        // What domains it supports
    requiredPlugins?: string[];         // What plugins it needs
  };
}

interface MfManifestEntryMetadata {
  typeId: string;                       // The GTS type ID
  name: string;                         // Human-readable name
  exposedModule: string;                // Module Federation module name
  routes?: RouteDefinition[];           // Routes for this entry
  requiredProperties?: string[];        // Required shared properties
  actions?: string[];                   // Actions it emits
  domainActions?: string[];             // Domain actions it handles
}

interface RouteDefinition {
  path: string;
  name?: string;
  meta?: Record<string, unknown>;
  chunkFile?: string;                   // Specific chunk for this route
}
```

**Example usage:**

```typescript
// Manifest with metadata (JSON, no JS execution)
{
  "id": "gts.acme.analytics.mfe.mf.v1~",
  "remoteEntry": "https://cdn.acme.com/analytics/remoteEntry.abc123.js",
  "remoteName": "acme_analytics",
  "featureFlags": ["advanced-analytics", "export-reports"],
  "translations": {
    "files": {
      "en": "https://cdn.acme.com/analytics/locales/en.abc123.json",
      "de": "https://cdn.acme.com/analytics/locales/de.def456.json",
      "fr": "https://cdn.acme.com/analytics/locales/fr.ghi789.json"
    },
    "namespace": "analytics",
    "defaultLocale": "en"
  },
  "capabilities": {
    "routes": [
      { "path": "/analytics", "name": "dashboard", "chunkFile": "src_Dashboard_js.def456.js" },
      { "path": "/analytics/reports", "name": "reports", "chunkFile": "src_Reports_js.ghi789.js" }
    ],
    "supportedDomains": ["screen", "dialog"],
    "requiredPlugins": ["router", "feature-flags", "network"]
  },
  "entries": [
    {
      "typeId": "gts.acme.analytics.mfe.entry.v1~hai3.mfe.entry_mf.v1:dashboard",
      "name": "dashboard",
      "exposedModule": "./Dashboard",
      "routes": [{ "path": "/analytics" }],
      "requiredProperties": ["gts.hai3.screensets.ext.shared_property.v1~:user_context"],
      "actions": ["gts.acme.analytics.ext.action.data_updated.v1~"]
    }
  ]
}

// Now parent app can:
// 1. Check feature flags before loading
if (manifest.featureFlags?.some(flag => !currentFlags[flag])) {
  return null;  // Don't load MFE
}

// 2. Add prefetch hints for translation files (SSR)
const currentLocale = getUserLocale();
const translationUrl = manifest.translations?.files[currentLocale]
  || manifest.translations?.files[manifest.translations?.defaultLocale];

if (translationUrl) {
  html += `<link rel="prefetch" href="${translationUrl}">`;
}

// 3. Add preload hints for current route
const route = manifest.capabilities.routes.find(r => r.path === currentPath);
if (route?.chunkFile) {
  html += `<link rel="modulepreload" href="${route.chunkFile}">`;
}

// 4. Discover capabilities without loading
console.log('Supports domains:', manifest.capabilities.supportedDomains);
console.log('Needs plugins:', manifest.capabilities.requiredPlugins);
console.log('Supports locales:', Object.keys(manifest.translations?.files || {}));
```

## Impact

**This affects:**
- SSR performance (cannot add preload hints for translations and route chunks)
- Asset loading (cannot preload route-specific chunks or translation files)
- Conditional loading (cannot check feature flags before loading)
- Developer experience (must maintain separate route configuration)
- Discoverability (cannot know what MFE provides without loading it)
- Initial render (extra round trips for assets, delayed rendering)

**Without declarative metadata:**
- Must load JavaScript to discover capabilities
- Extra round trips for route and translation files
- Cannot optimize asset preloading with prefetch/modulepreload hints
- Cannot prevent unnecessary loads based on feature flags
- Route configuration separate from MFE (duplication risk)

## Recommended Solution

**Proposal should specify:**

1. **Extend MfManifest with declarative metadata:**
   - Routes that MFE handles
   - Feature flags that MFE requires
   - Translation files with content hashes (locale -> URL mapping)
   - i18n namespace and default locale
   - Capabilities (domains, plugins, etc.)
   - Entry metadata (beyond just type IDs)

2. **Manifest distribution strategy** (related to cache busting):
   - Manifest must be JSON (not executable code)
   - Manifest must be fetchable independently of remoteEntry.js
   - Backend/SSR must be able to read manifest without loading MFE

3. **SSR integration pattern:**
   - How to add prefetch hints for translation files
   - How to add preload hints for route-specific chunks
   - How to conditionally load based on feature flags

## References

- Fragment System manifest structure with routes, feature flags, and translations
- Related proposal sections:
  - Cache busting strategy (manifest distribution)
  - `design.md` - Decision 18: Manifest Fetching Strategy
  - `specs/microfrontends/spec.md` - MfManifest type definition
- SSR use cases: Asset preloading with prefetch/modulepreload hints, conditional loading
