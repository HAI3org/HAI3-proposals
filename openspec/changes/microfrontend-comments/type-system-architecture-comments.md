# Type System & Architecture Comments

This document contains comments related to type registration, module exports, component rendering, and Module Federation architecture limitations in the `add-microfrontend-support` proposal.

---

## 1. Undefined Type Registration for Vendor MFEs

### Problem

The proposal shows vendor MFEs using custom GTS type IDs in their contracts:

```typescript
const chartEntry: MfeEntryMF = {
  id: 'gts.acme.analytics.mfe.entry.v1~hai3.mfe.entry_mf.v1:chart',
  requiredProperties: [
    'gts.hai3.screensets.ext.shared_property.v1~:user_context',
  ],
  actions: ['gts.acme.analytics.ext.action.data_updated.v1~'],  // Custom action type!
  domainActions: ['gts.acme.analytics.ext.action.refresh.v1~'], // Custom action type!
  manifest: 'gts.acme.analytics.mfe.mf.v1~',
  exposedModule: './ChartWidget',
};
```

**Issue:** The proposal documents how HAI3 registers its base types (6 core + 2 MF-specific) but **does NOT explain how vendor MFEs register their custom types** like:
- `gts.acme.analytics.ext.action.data_updated.v1~`
- `gts.acme.analytics.ext.action.refresh.v1~`

### The Missing Flow

For type validation to work, JSON Schemas must be registered with the TypeSystemPlugin:

```typescript
// HAI3 registers its types at initialization - DOCUMENTED ✅
function registerHai3Types(plugin: TypeSystemPlugin) {
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.action, mfeGtsSchemas.action);
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.extension, mfeGtsSchemas.extension);
  // ... etc
}

// But how do VENDORS register their types? NOT DOCUMENTED ❌
// Somewhere, this MUST happen:
plugin.registerSchema(
  'gts.acme.analytics.ext.action.data_updated.v1~',
  {
    $id: 'gts://gts.acme.analytics.ext.action.data_updated.v1~',
    $schema: 'https://json-schema.org/draft/2020-12/schema',
    type: 'object',
    properties: {
      timestamp: { type: 'number' },
      metrics: { type: 'object' },
    },
    required: ['timestamp'],
  }
);
```

**Without registration, validation fails:**
```typescript
// When mounting extension
const result = plugin.validateInstance(
  'gts.acme.analytics.ext.action.data_updated.v1~',  // Type ID
  { timestamp: Date.now(), metrics: {...} }           // Payload
);
// ❌ Error: Schema not found for type ID!
```

### Possible Solutions (None Documented)

#### Option 1: Execute MFE Code for Registration

**MFE bundle exports initialization function:**
```typescript
// acme-analytics-mfe/src/init.ts
export function registerAnalyticsTypes(plugin: TypeSystemPlugin) {
  plugin.registerSchema('gts.acme.analytics.ext.action.data_updated.v1~', dataUpdatedSchema);
  plugin.registerSchema('gts.acme.analytics.ext.action.refresh.v1~', refreshSchema);
  plugin.registerSchema('gts.acme.analytics.mfe.entry.v1~', entrySchema);
  // ... register ALL custom types
}

// Host must execute this BEFORE mounting:
import { registerAnalyticsTypes } from 'acme-analytics-mfe/init';

// Load MFE bundle
const container = await loader.load(entry);

// Execute initialization to register types
registerAnalyticsTypes(runtime.typeSystem);

// NOW can mount
runtime.mountExtension(extension);
```

**Implications:**
- ✅ **YES, you MUST execute MFE's JavaScript code BEFORE any validation**
- ✅ MFE must export type registration code
- ❌ Violates "don't execute untrusted code" principle
- ❌ What if registration code has side effects or is malicious?

#### Option 2: Separate Type Definition Files

**Fetch type definitions separately as JSON:**
```typescript
// Fetch from type registry
const response = await fetch(
  'https://registry.acme.com/types/gts.acme.analytics.mfe.mf.v1~/schemas.json'
);

const typeDefinitions = await response.json();
// {
//   'gts.acme.analytics.ext.action.data_updated.v1~': { $id: ..., type: 'object', ... },
//   'gts.acme.analytics.ext.action.refresh.v1~': { ... },
// }

// Register types BEFORE loading MFE code
for (const [typeId, schema] of Object.entries(typeDefinitions)) {
  plugin.registerSchema(typeId, schema);
}

// NOW load the MFE
await loader.load(entry);
```

**Implications:**
- ✅ No code execution needed for type registration
- ✅ Types can be validated before loading MFE
- ❌ Requires separate type registry infrastructure (not specified)
- ❌ Violates isolation (host knows MFE's types)
- ❌ How are type definitions discovered?

#### Option 3: Bundle Types in Manifest

**Embed schemas in MfManifest:**
```typescript
interface MfManifest {
  id: string;
  remoteEntry: string;
  remoteName: string;

  // NEW: Type definitions
  typeDefinitions?: Record<string, JSONSchema>;

  sharedDependencies?: SharedDependencyConfig[];
  entries?: string[];
}

const analyticsManifest: MfManifest = {
  id: 'gts.acme.analytics.mfe.mf.v1~',
  remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js',
  remoteName: 'acme_analytics',
  typeDefinitions: {
    'gts.acme.analytics.ext.action.data_updated.v1~': { /* schema */ },
    'gts.acme.analytics.ext.action.refresh.v1~': { /* schema */ },
    'gts.acme.analytics.mfe.entry.v1~': { /* schema */ },
  },
};
```

**Implications:**
- ✅ Types bundled with manifest
- ✅ No separate fetch needed
- ❌ Makes manifest files large
- ❌ Still need to register before loading
- ❌ Not in current proposal

### Questions

1. **When are vendor types registered?**
   - At MFE build time?
   - At host startup?
   - At MFE load time?
   - At mount time?

2. **Where are vendor type schemas stored?**
   - In MFE bundle code?
   - In separate JSON files?
   - In manifest?
   - In external registry?

3. **Who registers vendor types?**
   - MFE itself (via exported function)?
   - Host (after fetching schemas)?
   - Loader (automatically)?
   - Manual registration by integrator?

### Impact

**This affects:**
- Contract validation (can't validate without schemas)
- Vendor onboarding (how do vendors define types?)
- Type discovery (how does host know what types exist?)

**Without clear specification:**
- Implementers will make different choices
- No standardized vendor workflow
- Unclear boundaries between host and MFE

### Recommended Solution

The proposal should specify:

1. **Type Definition Format**
   ```typescript
   // Standardized type definition bundle
   interface MfeTypeDefinitions {
     version: string;  // Format version
     types: Record<string, JSONSchema>;
   }
   ```

2. **Distribution Strategy**
   - Option A: Separate `types.[contenthash].json` alongside `remoteEntry.[contenthash].js` (with content hashing for cache busting)
   - Option B: Embedded in manifest
   - Option C: Centralized type registry

3. **Registration Flow**
   ```typescript
   // 1. Fetch manifest
   const manifest = await manifestFetcher.fetch(manifestTypeId);

   // 2. Fetch type definitions (BEFORE loading code)
   const types = await fetchTypeDefinitions(manifest);

   // 3. Register types in isolated plugin
   for (const [typeId, schema] of Object.entries(types)) {
     mfeRuntime.typeSystem.registerSchema(typeId, schema);
   }

   // 4. NOW load MFE code
   const container = await loader.loadRemoteContainer(manifest);

   // 5. Validate and mount
   runtime.mountExtension(extension);
   ```

### References

- Related proposal sections:
  - `design.md` - Decision 1: Type System Plugin Interface (defines `registerSchema`)
  - `design.md` - Decision 4: HAI3 Type Registration (only covers base types)

---

## 2. Missing Abstraction Layer for Module Exports

### Problem

The MFE proposal uses Module Federation's raw `exposes` mechanism without defining what MFEs should export or how the host should use them.

**Module Federation exposes raw JavaScript modules:**
```javascript
// webpack.config.js
exposes: {
  './Dashboard': './src/Dashboard',  // ← What is this? Component? Function? Object?
}
```

**The proposal assumes but doesn't specify:**
```typescript
// Implied but not documented:
// 1. Exposed module MUST export a React component as default export
// 2. Component MUST accept MfeBridgeProps
// 3. No way to export multiple things (components + methods)
// 4. No metadata (routes, config, etc.)
```

### Comparison with Fragment System

**Fragment System (Explicit Abstractions):**
```typescript
// ✅ Clear abstraction - Component vs Method
export const dashboard = defineFragmentComponent('dashboard')
  .plugins(
    fragmentReactPlugin(DashboardComponent),
    fragmentRouterPlugin({ routes }),
    fragmentLocalizationPlugin(),
  );

export const setupAnalytics = defineFragmentMethod('setupAnalytics')
  .callback((fragment, app) => {
    app.hook('pageView', (page) => { /* ... */ });
  });

// ✅ Manifest explicitly lists components and methods
{
  "entries": [{
    "name": "main",
    "components": [{ "name": "dashboard", "routes": [...] }],
    "methods": [{ "name": "setupAnalytics" }]
  }]
}

// ✅ Type-safe loading
const component = await federation.getComponent('analytics', 'dashboard');
await federation.invokeMethod('analytics', 'setupAnalytics', api);
```

**MFE System (Raw Module Exports):**
```typescript
// ❌ No abstraction - just raw exports
export default function Dashboard({ bridge }: MfeBridgeProps) {
  return <div>Dashboard</div>;
}

// ❌ How to export methods? Not explained
// ❌ How to export multiple components? Must create separate exposed modules
// ❌ No metadata - routes? config?

// MFE can have multiple entries, each referencing different exposed module
const chartEntry: MfeEntryMF = {
  exposedModule: './ChartWidget',  // ← String reference to webpack exposes key
};

const metricsEntry: MfeEntryMF = {
  exposedModule: './MetricsWidget',  // ← Different exposed module
};

// Host loads and assumes it's a React component
const { component } = await loader.load(chartEntry);
<component bridge={bridge} />  // ← Hope it's the right shape!
```

### What's Missing

**No abstraction layer between Module Federation's raw exports and MFE usage:**

- **Export Shape Specification** - What must the exposed module export? Default export? Named export? What type? What props signature?
- **Type Validation** - How to ensure exported module conforms to expected shape?
- **Metadata** - Where to declare routes, configuration, lifecycle hooks?
- **Framework Adapter** - Fragment System uses `fragmentReactPlugin` to wrap components properly; MFE assumes raw React component
- **Multiple Exports from Single Module** - Cannot expose both component and method from one entry point

### Real-World Use Case

In Fragment System, a common pattern is to export both a component (for rendering) and a method (for startup initialization) from the same entry:

```typescript
// Fragment entry exports BOTH
export const dashboard = defineFragmentComponent('dashboard')
  .plugins(fragmentReactPlugin(DashboardComponent));

export const initialize = defineFragmentMethod('initialize')
  .callback((fragment, app) => {
    // Setup code that runs at application startup
    app.registerGlobalHandlers();
    app.subscribeToEvents();
  });

// Usage:
// 1. At app startup: invoke 'initialize' method
await federation.invokeMethod('analytics', 'initialize', app);

// 2. Later, when navigating: render 'dashboard' component
const component = await federation.getComponent('analytics', 'dashboard');
component.mount('#app');
```

**MFE System cannot express this pattern:**

```typescript
// Need TWO separate entries
const dashboardEntry: MfeEntryMF = {
  exposedModule: './Dashboard',  // Component
  // ... UI contract
};

const initEntry: MfeEntryMF = {
  exposedModule: './Initialize',  // ??? Method? Function? Object?
  // ... what contract for non-UI code?
};

// Problems:
// 1. MfeEntry contract is designed for UI (requiredProperties, domainActions)
// 2. No clear way to load and invoke './Initialize' as a method
// 3. Must create separate webpack expose for each
// 4. No type system for non-component exports
```

### Impact

**This affects:**
- Type safety (can't enforce component shape)
- Security (no validation of exports)
- Developer experience (unclear what to export)
- Composition (hard to export multiple things)
- Metadata (no way to declare routes, config)

**Without abstraction layer:**
- Every MFE must know undocumented conventions
- Host must trust MFE exports the right thing
- No standardized way to export methods
- No framework adapter for different UI libs

### Recommended Solution

**Use filesystem conventions to define MFE structure**, similar to modern meta-frameworks (Next.js, Remix, SvelteKit):

#### Filesystem-Based Convention

**Flat Structure:**
```
analytics-mfe/
├── src/
│   ├── entries/
│   │   ├── dashboard.component.tsx      # Component implementation
│   │   ├── dashboard.component.json     # Component metadata (Option A)
│   │   ├── initialize.method.ts         # Method implementation
│   │   └── initialize.method.json       # Method metadata (Option A)
│   └── mfe.config.ts                    # MFE-level configuration
```

**Filesystem Routing (Per-Component Routes):**
```
analytics-mfe/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── dashboard.component.tsx  # Component implementation
│   │   │   └── routes/                  # Routes for this component
│   │   │       ├── index.route.tsx      # → /analytics (base route)
│   │   │       └── settings.route.tsx   # → /analytics/settings
│   │   └── presentation/
│   │       ├── presentation.component.tsx
│   │       └── routes/
│   │           ├── index.route.tsx      # → /analytics/presentation (base)
│   │           ├── fullscreen.route.tsx # → /analytics/presentation/fullscreen
│   │           └── reports/
│   │               ├── index.route.tsx  # → /analytics/presentation/reports
│   │               └── [id].route.tsx   # → /analytics/presentation/reports/:id (dynamic)
│   ├── methods/
│   │   └── initialize.method.ts         # Non-route method
│   └── mfe.config.ts
```

**Build tool automatically:**
- Discovers components from `components/` directory structure
- Each component can have its own `routes/` subdirectory
- Generates paths from file path: `components/presentation/routes/reports/[id].route.tsx` → `/analytics/presentation/reports/:id`
- Routes are scoped per component, making it clear which routes belong to which component
- Extracts metadata from each component and route file
- Creates manifest with all discovered components and their routes

#### Entry File Format

**Option A: Metadata in Separate JSON Files**

**Component Implementation (`dashboard.component.tsx`):**
```typescript
// Pure component implementation, no metadata
export default function Dashboard({ bridge }: MfeBridgeProps) {
  return <div>Dashboard</div>;
}
```

**Component Metadata (`dashboard.component.json`):**
```json
{
  "routes": [
    { "path": "/analytics", "meta": { "mode": "default" } },
    { "path": "/analytics/presentation", "meta": { "mode": "fullscreen" } }
  ],
  "requiredProperties": ["gts.hai3.screensets.ext.shared_property.v1~:user_context"],
  "actions": ["gts.acme.analytics.ext.action.data_updated.v1~"],
  "domainActions": ["gts.acme.analytics.ext.action.refresh.v1~"]
}
```

**Option B: Metadata in Source Code (Statically Analyzable, Used in Runtime)**

**Component with Inline Metadata (`dashboard.component.tsx`):**
```typescript
import { defineRoutes, defineRequiredProperties, defineActions, defineDomainActions } from '@hai3/mfe-helpers';

// Define metadata using helper functions for type safety
// These are statically analyzable AND usable at runtime
// Option 1: Explicit route definitions
export const routes = defineRoutes([
  { path: '/analytics', meta: { mode: 'default' } },
  { path: '/analytics/presentation', meta: { mode: 'fullscreen' } }
]);

// Option 2: Filesystem-based routing (see "Filesystem Routing" section above)
// When using routes/ directory structure, no need to manually define routes
// Build tool automatically discovers routes from file paths

export const requiredProperties = defineRequiredProperties({
  user_context: 'gts.hai3.screensets.ext.shared_property.v1~:user_context'
});

export const actions = defineActions({
  data_updated: 'gts.acme.analytics.ext.action.data_updated.v1~'
});

export const domainActions = defineDomainActions({
  refresh: 'gts.acme.analytics.ext.action.refresh.v1~'
});

// Component implementation can reference the same metadata
export default function Dashboard({ bridge }: MfeBridgeProps) {
  // Access user context from bridge using type-safe named reference
  const userContext = bridge.getProperty(requiredProperties.user_context);

  // Emit action using type-safe named reference
  bridge.emitAction(actions.data_updated, { timestamp: Date.now() });

  // Handle domain action
  bridge.onDomainAction(domainActions.refresh, () => {
    // Refresh logic
  });

  return <div>Dashboard</div>;
}
```

**Helper Functions (Type Guards & Static Analysis Markers):**
```typescript
// @hai3/mfe-helpers
export function defineRoutes<T extends readonly RouteDefinition[]>(routes: T): T {
  return routes; // Identity function, exists only for type guard and static analysis marker
}

export function defineRequiredProperties<T extends Record<string, string>>(props: T): T {
  return props; // Returns object with named keys for ergonomic access
}

export function defineActions<T extends Record<string, string>>(actions: T): T {
  return actions;
}

export function defineDomainActions<T extends Record<string, string>>(actions: T): T {
  return actions;
}
```

**Build Tool Extracts to JSON:**
```json
// dashboard.component.meta.json (generated at build time)
// Build tool converts object values to array for manifest
{
  "routes": [
    { "path": "/analytics", "meta": { "mode": "default" } },
    { "path": "/analytics/presentation", "meta": { "mode": "fullscreen" } }
  ],
  "requiredProperties": ["gts.hai3.screensets.ext.shared_property.v1~:user_context"],
  "actions": ["gts.acme.analytics.ext.action.data_updated.v1~"],
  "domainActions": ["gts.acme.analytics.ext.action.refresh.v1~"]
}
```

**Benefits of This Approach:**

- ✅ **Single source of truth** - Metadata defined once, used in both manifest and runtime code
- ✅ **Type safety** - TypeScript ensures consistency between metadata and usage
- ✅ **No duplication** - Same constants used in manifest extraction and component logic
- ✅ **Manifest always aligned** - Build tool extracts from the same source code that component uses
- ✅ **Statically analyzable** - Helper functions are identity functions, build tool can extract values
- ✅ **Ergonomic named access** - Use `requiredProperties.user_context` instead of `requiredProperties[0]`
- ✅ **Better refactoring** - Rename keys in one place, TypeScript catches all usages

**Key Requirement: Static Analysis**

Regardless of whether metadata is in separate `.json` files or exported from source code, it **MUST be statically analyzable**:

- ✅ Literal values: `{ path: '/analytics' }`
- ✅ Helper functions: `defineRoutes([...])`
- ✅ Exported constants: `export const routes = defineRoutes(...)`
- ❌ Dynamic expressions: `{ path: computePath() }`
- ❌ Runtime values: `{ path: process.env.BASE_PATH }`
- ❌ Function calls in values: `{ path: getPath() }`

The build tool extracts metadata **without executing JavaScript**, generating pure JSON that can be read by any tool (SSR, type registries, dev servers) without loading the MFE code.

**Why This Matters:**
- Metadata defined once → used in manifest AND runtime code
- No risk of manifest/code misalignment
- TypeScript type safety ensures correctness
- Build tool verifies at compile time

**Method Implementation (`initialize.method.ts`):**
```typescript
// Pure method implementation, no metadata
export default function initialize(bridge: MfeBridgeProps, app: AppContext) {
  app.registerGlobalHandlers();
  app.subscribeToEvents();
}
```

**Method Metadata (`initialize.method.json`):**
```json
{
  "lifecycle": "startup",
  "timeout": 5000
}
```

#### Build-Time Manifest Generation

The build tool (webpack/vite plugin) **reads or extracts JSON metadata** and generates manifest:

```typescript
// Generated at build time from filesystem + JSON metadata files
const manifest: MfManifest = {
  id: 'gts.acme.analytics.mfe.mf.v1~',
  remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.[hash].js',
  remoteName: 'acme_analytics',
  entries: [
    {
      typeId: 'gts.acme.analytics.mfe.entry.v1~:dashboard',
      type: 'component',
      exposedModule: './entries/dashboard.component',
      routes: [
        { path: '/analytics', meta: { mode: 'default' } },
        { path: '/analytics/presentation', meta: { mode: 'fullscreen' } }
      ],
      requiredProperties: ['gts.hai3.screensets.ext.shared_property.v1~:user_context'],
      actions: ['gts.acme.analytics.ext.action.data_updated.v1~'],
      domainActions: ['gts.acme.analytics.ext.action.refresh.v1~']
    },
    {
      typeId: 'gts.acme.analytics.mfe.entry.v1~:initialize',
      type: 'method',
      exposedModule: './entries/initialize.method',
      lifecycle: 'startup',
      timeout: 5000
    }
  ]
};
```

#### Benefits

- ✅ **No manual manifest maintenance** - Generated from filesystem + metadata (JSON or extracted from code)
- ✅ **Static metadata** - Either pure JSON files or statically extracted from code
- ✅ **Clear conventions** - `*.component.tsx` for components, metadata either in `.json` or `export const metadata`
- ✅ **Framework adapter via metadata** - Can specify framework in metadata
- ✅ **Declarative metadata** - Routes, config extracted to JSON at build time
- ✅ **Validation at build time** - Invalid metadata = build failure
- ✅ **Tooling-friendly** - Final JSON output readable by any tool without executing code
- ✅ **Developer choice** - Can write metadata in JSON files OR in TypeScript (extracted to JSON at build time)
- ✅ **Filesystem-based routing** - Optional: Use `routes/` directory structure for automatic route discovery (like Next.js, Remix, SvelteKit)

#### Framework Adapter via Metadata

**Vue Component (`settings.component.vue`):**
```vue
<template>
  <div>Settings</div>
</template>

<script>
export default {
  name: 'Settings'
};
</script>
```

**Vue Metadata (`settings.component.json`):**
```json
{
  "framework": "vue",
  "routes": [{ "path": "/settings" }]
}
```

**This approach is proven** - Next.js uses filesystem conventions (`app/`, `pages/`), Remix uses route files, SvelteKit uses `+page.svelte`. The build tool discovers structure automatically and generates manifest.

### References

- Fragment System: `defineFragmentComponent` / `defineFragmentMethod` pattern
- Module Federation: Raw `exposes` mechanism (no abstraction)
- Related sections:
  - `design.md` - Decision 12: Module Federation 2.0 (shows raw exposes)
  - `design.md` - Decision 14: MFE Bridge Interfaces (assumes React component)

---

## 3. React Version Compatibility and Component Rendering

### Problem

The proposal states that loaded MFEs are "React components" but doesn't explain how version compatibility works when host and MFE use different React versions.

**From the proposal:**
```typescript
interface LoadedMfe {
  /** The loaded React component */
  component: React.ComponentType<MfeBridgeProps>;  // ← Implies direct rendering
}
```

**Recommended configuration (singleton: false):**
```typescript
// Host uses React 18
shared: {
  react: { singleton: false, requiredVersion: '^18.0.0' },
}

// MFE built with React 16
shared: {
  react: { singleton: false, requiredVersion: '^16.14.0' },
}
```

### The Incompatibility Issue

With `singleton: false`, each runtime gets its own React instance:
- Host: React 18.3.0 instance
- MFE: React 16.14.0 instance (if major version mismatch)

**This creates a problem:**

```typescript
// ❌ Host (React 18) cannot directly render MFE component (React 16)
function HostApp() {
  const [MfeComponent, setMfeComponent] = useState(null);

  useEffect(() => {
    loader.load(entry).then(({ component }) => {
      setMfeComponent(component);  // React 16 component
    });
  }, []);

  // ❌ Cannot render React 16 component in React 18 tree!
  // Different reconciler, different internal APIs, different hooks
  return <div>{MfeComponent && <MfeComponent bridge={bridge} />}</div>;
}
```

**Why it fails:**
- React 16 and React 18 have incompatible internal APIs
- Fiber reconciler is different
- Event system is different
- Hooks implementation is different
- Cannot mix components from different React versions in same tree

### How It Actually Works (Likely via Shadow DOM)

The proposal mentions Shadow DOM but doesn't explain the rendering mechanism:

```typescript
<ShadowDomContainer entryTypeId={...}>
  <MfeComponent bridge={bridge} />  // ← How is this rendered?
</ShadowDomContainer>
```

**Likely implementation:**
```typescript
// 1. Create shadow DOM boundary
const shadowRoot = container.attachShadow({ mode: 'open' });

// 2. MFE renders itself with its own React instance
// NOT by host rendering it in host's React tree
const mfe = await loader.load(entry);

// 3. MFE must have a mount() method, not be a React component
mfe.mount(shadowRoot, { bridge });  // ← MFE uses its React 16 to render

// Host's React 18 never touches MFE's React 16 code
```

### What's Missing in Specification

1. **LoadedMfe type is misleading**
   ```typescript
   // Current (wrong):
   interface LoadedMfe {
     component: React.ComponentType<MfeBridgeProps>;  // ❌ Not renderable by host
   }

   // Should be:
   interface LoadedMfe {
     mount: (container: HTMLElement, props: MfeBridgeProps) => void;
     unmount: (container: HTMLElement) => void;
   }
   ```

2. **No specification of what MFE must export**
   - Must export mount/unmount functions?
   - Or React component (and host handles mounting)?
   - How does version isolation actually work?

3. **No framework adapter pattern**
   - MFE says "React component" but could be Vue, Angular, etc.
   - How does host know how to mount?
   - How does MFE declare its framework?

### Comparison with Fragment System

**Fragment System explicitly handles this:**

```typescript
// Fragment declares framework via adapter
export default defineFragmentComponent('dashboard').plugins(
  fragmentReactPlugin(DashboardComponent),  // ← React adapter
);

// Or Vue
export default defineFragmentComponent('settings').plugins(
  fragmentVuePlugin(SettingsComponent),  // ← Vue adapter
);

// Adapter provides mount/unmount interface
interface FragmentAdapter {
  mount(container: HTMLElement, props: any): void;
  unmount(container: HTMLElement): void;
}

// fragmentReactPlugin implementation
class ReactAdapter implements FragmentAdapter {
  mount(container: HTMLElement, props: any) {
    // Uses Fragment's own React version
    const root = ReactDOM.createRoot(container);
    root.render(<Component {...props} />);
  }

  unmount(container: HTMLElement) {
    root.unmount();
  }
}
```

**Benefits:**
- ✅ Framework explicitly declared
- ✅ Adapter handles mounting with correct version
- ✅ Host doesn't need to know Fragment's framework
- ✅ Works with any React version, Vue version, etc.
- ✅ Clear mount/unmount interface

### Impact

**This affects:**
- Version compatibility (can host and MFE use different React versions?)
- Rendering mechanism (how does host actually render MFE?)
- Type safety (is LoadedMfe.component actually a React component?)
- Framework flexibility (how to support Vue, Angular, etc.?)

**Without clear specification:**
- Unclear if React version mismatches are supported
- Misleading type definition (component vs mount function)
- No guidance for MFE authors on what to export
- No framework adapter pattern for non-React MFEs

### Recommended Solution

**Proposal should specify:**
1. What MFE exposed modules must export (mount/unmount interface? React component?)
2. How host renders MFE (via mount function? via React.createElement?)
3. How React version compatibility is handled (enforce matching versions? allow isolation?)
4. Framework adapter pattern (if MFE can use non-React frameworks)
5. Shadow DOM integration (when/how is it used?)

### References

- Related proposal sections:
  - `design.md` - Decision 12: Module Federation (specifies singleton: false but not rendering)
  - `design.md` - Decision 13: Framework-Agnostic Isolation (says "any framework" but no adapter)
  - `specs/microfrontends/spec.md` - Shadow DOM React Component (shows usage but not mechanism)

---
