# Deployment & Versioning Comments

This document contains comments related to deployment, versioning, cache busting, and declarative metadata in the `add-microfrontend-support` proposal.

---

## 1. Missing Declarative Metadata for Discovery and Preloading

### Problem

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

### Use Cases That Require Advance Metadata

#### Use Case 1: Route-Specific Asset Preloading in SSR

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

// ❌ Cannot discover routes - no route information in manifest
// ❌ Cannot add preload hints - don't know which files are for which routes

// Send HTML without preload hints
res.send(html);

// Browser must:
// 1. Load remoteEntry.js (~10KB)
// 2. Execute JavaScript to discover exposed modules
// 3. Load MFE entry code (no preload = extra round trip)
// 4. Execute code to discover routes
```

**Impact:** Extra round trips, no preload optimization, slower initial navigation.

#### Use Case 2: Feature Flags Visibility for Debugging and Admin

**Fragment System approach:**
```typescript
// Backend/Admin panel: List all fragments and their feature flags
const manifests = await fetchAllManifests();

// Build feature flag usage map
const featureFlagUsage = manifests.map(m => ({
  fragment: m.name,
  flags: m.featureFlags,  // ✅ Declared in manifest
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

// ❌ No featureFlags field in manifest
// ❌ Cannot build feature flag usage map
// ❌ Cannot show what flags each MFE uses

// Must either:
// 1. Maintain separate documentation of flag usage
// 2. Load all MFEs to discover their flags at runtime
// 3. Have no visibility into flag dependencies

// Debug window cannot show flag relationships without loading code
```

**Impact:** Poor debugging experience, no visibility into feature flag usage without loading all MFEs, difficult to audit which features depend on which flags.

#### Use Case 3: Translation File Preloading in SSR

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
// ✅ Already prefetched = instant load
```

**MFE System problem:**
```typescript
// Server-side: Manifest has no translation metadata
const manifest = await fetch('https://api.example.com/mfe-registry/analytics')
  .then(r => r.json());

// ❌ Cannot discover translation files
// ❌ Cannot add preload hints for translations

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

#### Use Case 4: Merged Manifests in SSR for Reduced Round Trips

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
// ✅ All manifests available immediately
// ✅ Can configure routes, check feature flags, discover capabilities
// ✅ Zero extra round trips
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

// ❌ 3 separate round trips
// ❌ Blocks rendering until all manifests fetched
// ❌ Cannot optimize with SSR
```

**Impact:** Extra round trips for each MFE manifest, delayed initialization, cannot leverage SSR to reduce client-side requests.

#### Use Case 5: Route Metadata for Client-Side Parent App Configuration

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
          "meta": { "mode": "fullscreen" }  // ✅ Parent knows to hide menu
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
        meta: route.meta,  // ✅ Parent configures UI based on meta
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

// ❌ Cannot configure parent UI based on route
// ❌ Must wait for MFE to load and communicate preferences

// Sequence with missing metadata:
// 1. User navigates to /analytics/presentation
// 2. Parent app renders with default layout (menu visible)
// 3. Load and mount MFE
// 4. MFE executes, detects it needs fullscreen mode
// 5. MFE communicates via bridge: "hide menu please"
// 6. Parent app hides menu
// Result: Flash of menu before hiding ❌

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

### Comparison with Fragment System

**Fragment System manifest includes:**

```typescript
type FragmentManifest = {
  name: string;
  version: string;
  artifacts: ViteManifest;           // ✅ File mappings
  translations?: FragmentManifestTranslations;  // ✅ Localization files
  entries: FragmentManifestEntry[];   // ✅ Rich entry metadata
  featureFlags: FragmentManifestFeatureFlag[];  // ✅ Required flags
};

type FragmentManifestEntry = {
  name: string;
  file: string;                       // ✅ Entry file path
  components?: FragmentManifestComponent[];  // ✅ Components list
  methods?: FragmentManifestMethod[]; // ✅ Methods list
};

type FragmentManifestComponent = {
  name: string;
  routes?: FragmentRouteRecord[];     // ✅ Route declarations
};

type FragmentRouteRecord = {
  path: string;
  name?: string;
  meta?: Record<string, unknown>;
  file?: string;                      // ✅ Route-specific file
  children?: FragmentRouteRecord[];
};
```

**Benefits:**
- Parent app can read manifest (JSON) without executing JavaScript
- SSR can configure routes and add preload hints
- Backend can make decisions based on feature flags
- Route-specific assets can be preloaded
- All metadata available before loading any code

### What MFE System Needs

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
    files: Record<string, string>;      // locale → translation file URL with content hash
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

### Impact

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

### Recommended Solution

**Proposal should specify:**

1. **Extend MfManifest with declarative metadata:**
   - Routes that MFE handles
   - Feature flags that MFE requires
   - Translation files with content hashes (locale → URL mapping)
   - i18n namespace and default locale
   - Capabilities (domains, plugins, etc.)
   - Entry metadata (beyond just type IDs)

2. **Manifest distribution strategy** (related to Section 1):
   - Manifest must be JSON (not executable code)
   - Manifest must be fetchable independently of remoteEntry.js
   - Backend/SSR must be able to read manifest without loading MFE

3. **SSR integration pattern:**
   - How to add prefetch hints for translation files
   - How to add preload hints for route-specific chunks
   - How to conditionally load based on feature flags

### References

- Fragment System manifest structure with routes, feature flags, and translations
- Related proposal sections:
  - Section 1: Missing Cache Busting Strategy (manifest distribution)
  - `design.md` - Decision 18: Manifest Fetching Strategy
  - `specs/microfrontends/spec.md` - MfManifest type definition
- SSR use cases: Asset preloading with prefetch/modulepreload hints, conditional loading
---

## 2. Module Federation: Package-Level Sharing Prevents Tree-Shaking

### Problem

Module Federation's `shared` configuration operates at the **package level**, not the module/function level. This means when you share a library, you must share the **entire package**, even if each MFE only uses a small subset of its functions.

**From the proposal (Decision 12):**
```javascript
shared: {
  'lodash': { singleton: true, requiredVersion: '^4.17.0' },
  'date-fns': { singleton: true, requiredVersion: '^2.30.0' },
}
```

### The Tree-Shaking Problem

**Module Federation cannot do chunk-level sharing:**

```javascript
// MFE A: only needs format()
import { format } from 'date-fns';

// MFE B: only needs parse()
import { parse } from 'date-fns';

// Both MFEs declare:
shared: {
  'date-fns': { singleton: true, requiredVersion: '^2.30.0' }
}

// What happens:
// 1. Host loads → Downloads ENTIRE date-fns package (~120KB gzipped)
// 2. MFE A needs format() → Uses host's date-fns (entire package!)
// 3. MFE B needs parse() → Uses host's date-fns (entire package!)

// Total downloads: ~120KB gzipped (~500KB uncompressed)
// Actually needed: ~20KB (just format + parse functions)
// Waste: ~100KB (500% overhead!) ❌
```

**Why this happens:**
1. `shared` config works on package names (`'date-fns'`), not individual exports (`'date-fns/format'`)
2. Module Federation resolves dependencies at runtime by package name
3. No metadata about what's actually used within the package
4. Container API exposes whole packages, not individual modules

### Comparison with Standard Build (Fragment System)

**Without Module Federation, standard Vite/Webpack builds with tree-shaking:**

```javascript
// Fragment A: only needs format()
import { format } from 'date-fns';

// Fragment B: only needs parse()
import { parse } from 'date-fns';

// Vite build output:
// Fragment A → chunk-datefns-format.abc123.js (~10KB, only format)
// Fragment B → chunk-datefns-parse.def456.js (~10KB, only parse)

// Deploy to same directory:
// s3://cdn/fragments/chunk-datefns-format.abc123.js
// s3://cdn/fragments/chunk-datefns-parse.def456.js

// Browser behavior:
// 1. Load Fragment A → download chunk-datefns-format.abc123.js (~10KB)
// 2. Load Fragment B → download chunk-datefns-parse.def456.js (~10KB)

// Total downloads: ~20KB (only what's actually needed!)
// Waste: 0KB ✅
```

**Benefits of standard build:**
- ✅ Tree-shaking works naturally
- ✅ Only bundle what's imported
- ✅ Chunks shared via content hash (same code = same hash = cached)
- ✅ No package-level bloat

### Real-World Impact

**lodash:**
```
Full package: ~70KB gzipped (~530KB uncompressed)
Typical usage (3-4 functions): ~3KB gzipped (~10KB uncompressed)

With Module Federation shared:
- Downloads: 70KB gzipped
- Waste: 67KB (96% overhead!)
```

**date-fns:**
```
Full package: ~120KB gzipped (~500KB uncompressed)
Typical usage (format + parse): ~10KB gzipped (~40KB uncompressed)

With Module Federation shared:
- Downloads: 120KB gzipped
- Waste: 110KB (92% overhead!)
```

**Scenario: 5 MFEs each using 3-4 lodash functions:**
```
Standard build (Fragment System):
- Each MFE bundles only what it needs: ~3KB each
- Shared chunks (same functions): cached via content hash
- Total: ~15KB

Module Federation (MFE System):
- Host provides entire lodash: ~70KB
- All MFEs use host's lodash (entire package)
- Total: ~70KB
- Waste: ~55KB (367% overhead!)
```

### Why Module Federation Cannot Fix This

**Fundamental limitations:**

1. **Package-level resolution** - Module Federation's sharing mechanism works on package names, not individual exports
2. **Runtime negotiation** - Versions are negotiated per package at runtime, not per module
3. **Container API** - Module Federation containers expose whole packages
4. **No tree-shaking metadata** - No information about what's actually used within a package

**Cannot do this (even though it would solve the problem):**
```javascript
// Hypothetical granular sharing - NOT SUPPORTED
shared: {
  'date-fns/format': { ... },     // ❌ Can't share subpaths
  'date-fns/parse': { ... },      // ❌ Can't share individual functions
  'lodash/debounce': { ... },     // ❌ Can't share at function level
}
```

### Coordination Overhead

Because sharing is package-level, teams must coordinate on which packages to share:

```
Day 1: Host and MFE A both use lodash
  → Add to shared config: ✅ lodash shared

Day 10: MFE B adds date-fns (host doesn't use it)
  → MFE B bundles entire date-fns in separate chunk (~120KB)
  → Not in host's shared config → no sharing

Day 20: MFE C also adds date-fns
  → If MFE C lists in shared BUT host doesn't:
    - date-fns bundled in MFE B (~120KB)
    - date-fns shared for MFE C (~120KB)
    - Downloaded TWICE! (~240KB total)

Day 30: Realize coordination problem
  → Update host's shared config to include date-fns
  → Redeploy host + all MFEs
  → Complex dependency management across teams
```

### Impact

**This affects:**
- Bundle sizes (massive overhead for libraries with many exports)
- Performance (downloading unused code)
- Coordination overhead (all teams must align on shared packages)
- Scalability (more MFEs = more coordination = more waste)

**Without chunk-level sharing:**
- MFEs download entire packages even if using 1-2 functions
- Tree-shaking benefits lost for shared dependencies
- No optimization for partial usage
- Bundle sizes grow unnecessarily

### Recommended Solution

**Proposal should acknowledge this limitation and either:**
1. Accept the package-level sharing trade-off (document the overhead)
2. Recommend using standard builds with content-hash based sharing instead
3. Provide guidance on minimizing impact (use micro-libraries instead of monoliths)

### References

- Module Federation documentation on shared dependencies
- Related proposal sections:
  - `design.md` - Decision 12: Module Federation 2.0 (shows shared config, doesn't mention tree-shaking loss)
  - Fragment System comparison: Uses standard Vite builds with natural tree-shaking and chunk-level sharing

---

## 3. Missing Cache Busting Strategy for remoteEntry

### Problem

The `MfManifest` type specifies `remoteEntry` as a plain URL without content hash or version parameter:

```typescript
interface MfManifest {
  id: string;
  remoteEntry: string;  // e.g., 'https://cdn.acme.com/analytics/remoteEntry.js'
  remoteName: string;
  sharedDependencies?: SharedDependencyConfig[];
  entries?: string[];
}
```

**Issue:** When MFE code changes (bug fixes, new features, updates), the `remoteEntry` URL remains the same, leading to browser caching problems.

### Scenario: Bug Fix Deployment

```
Day 1: Deploy analytics MFE v1.0.0
  → remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js'
  → Browser caches this file

Day 2: Fix critical bug, deploy v1.0.1
  → remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js' (SAME URL!)
  → Browser serves cached v1.0.0
  → Users don't get the fix ❌
```

### Root Cause

**Deployment versioning is completely separate from GTS type versioning:**

- GTS version (`v1~`, `v2~`) tracks **contract/schema changes**
- Deployment version (1.0.0 → 1.0.1) tracks **implementation changes**

You can have 100 deployments of `gts.acme.analytics.mfe.mf.v1~` without changing the GTS type version, and none of them have automatic cache busting.

### Standard Solutions (Not in Proposal)

#### Option 1: Content Hash in URL
```typescript
// Build output generates hash
remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.a3f5b9c2.js'

// After code changes
remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.d8e2c147.js' // Different URL!
```

**Benefits:**
- ✅ Different URL = No cache collision
- ✅ Can use aggressive caching (`Cache-Control: immutable, max-age=31536000`)
- ✅ Standard webpack/vite output with `[contenthash]`

#### Option 2: Query String Version
```typescript
remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js?v=1.0.1'
```

**Benefits:**
- ✅ Simple to implement
- ⚠️ Less reliable (some proxies ignore query params)

#### Option 3: Version in Path
```typescript
remoteEntry: 'https://cdn.acme.com/analytics/v1.0.1/remoteEntry.js'
```

**Benefits:**
- ✅ Clean URLs
- ✅ CDN-friendly

**Drawbacks:**
- ❌ Prevents chunk-level sharing between versions (similar to Section 2: tree-shaking problem)
- ❌ Each version deploys to a separate directory, so identical chunks from different versions cannot be deduplicated by the browser cache
- ❌ Example: If `v1.0.1/chunk-lodash.abc123.js` and `v1.0.2/chunk-lodash.abc123.js` contain identical code, the browser downloads both because paths differ

### Additional Missing Pieces

The proposal doesn't specify:

1. **Manifest Distribution Strategy**
   - ❌ How do clients get the updated manifest with new `remoteEntry` URL?
   - ❌ Is manifest fetched from API? What caching?
   - ❌ Is manifest bundled? (Defeats independent deployment)

2. **Manifest Caching**
   ```typescript
   // UrlManifestFetcher has fetchOptions but no guidance
   class UrlManifestFetcher {
     constructor(
       private readonly urlResolver: (manifestTypeId: string) => string,
       private readonly fetchOptions?: RequestInit  // ❓ What cache headers?
     ) {}
   }
   ```

3. **HTTP Cache Headers Guidance**
   - ❌ No recommendation for `Cache-Control` headers
   - ❌ No guidance on ETags
   - ❌ No mention of immutable assets

### Impact

**This affects:**
- Bug fix deployments
- Security patches
- Performance improvements
- Any code change that doesn't modify the contract

**Without cache busting:**
- Users may get stale code for hours/days
- Must use aggressive cache invalidation (`no-cache`) = slower loads
- OR accept delayed updates

### Recommended Solution

Add deployment versioning to `MfManifest`:

```typescript
interface MfManifest {
  id: string;                          // GTS type ID (contract version)
  remoteEntry: string;                 // Should include content hash
  remoteName: string;

  // NEW: Deployment metadata
  deploymentVersion?: string;          // Semantic version (e.g., "1.2.3")
  buildHash?: string;                  // Content hash (e.g., "a3f5b9c2")
  buildTimestamp?: number;             // Unix timestamp of build

  sharedDependencies?: SharedDependencyConfig[];
  entries?: string[];
}
```

**And specify:**
1. `remoteEntry` SHOULD include content hash or version parameter
2. Manifest fetch strategy and caching policy
3. Recommended HTTP cache headers:
   - `remoteEntry.js`: `Cache-Control: public, max-age=31536000, immutable`
   - Manifest JSON: `Cache-Control: public, max-age=300` (5 minutes)
4. How clients discover manifest updates

### References

- Module Federation standard practice: Use `[contenthash]` in filename
- Related proposal sections:
  - Section 1: Missing Declarative Metadata (manifest distribution related)
  - `design.md` - Decision 2: GTS Type ID Format (only covers contract versioning)
  - `design.md` - Decision 18: Manifest Fetching Strategy (doesn't address caching)
  - `specs/microfrontends/spec.md` - Requirement: MFE Version Validation (only shared dependencies)
