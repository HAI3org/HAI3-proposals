# Missing Abstraction Layer for Module Exports

## Problem

The MFE proposal uses Module Federation's raw `exposes` mechanism without defining what MFEs should export or how the host should use them.

**Module Federation exposes raw JavaScript modules:**
```javascript
// webpack.config.js
exposes: {
  './Dashboard': './src/Dashboard',  // <- What is this? Component? Function? Object?
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

## Comparison with Fragment System

**Fragment System (Explicit Abstractions):**
```typescript
// Clear abstraction - Component vs Method
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

// Manifest explicitly lists components and methods
{
  "entries": [{
    "name": "main",
    "components": [{ "name": "dashboard", "routes": [...] }],
    "methods": [{ "name": "setupAnalytics" }]
  }]
}

// Type-safe loading
const component = await federation.getComponent('analytics', 'dashboard');
await federation.invokeMethod('analytics', 'setupAnalytics', api);
```

**MFE System (Raw Module Exports):**
```typescript
// No abstraction - just raw exports
export default function Dashboard({ bridge }: MfeBridgeProps) {
  return <div>Dashboard</div>;
}

// How to export methods? Not explained
// How to export multiple components? Must create separate exposed modules
// No metadata - routes? config?

// MFE can have multiple entries, each referencing different exposed module
const chartEntry: MfeEntryMF = {
  exposedModule: './ChartWidget',  // <- String reference to webpack exposes key
};

const metricsEntry: MfeEntryMF = {
  exposedModule: './MetricsWidget',  // <- Different exposed module
};

// Host loads and assumes it's a React component
const { component } = await loader.load(chartEntry);
<component bridge={bridge} />  // <- Hope it's the right shape!
```

## What's Missing

**No abstraction layer between Module Federation's raw exports and MFE usage:**

- **Export Shape Specification** - What must the exposed module export? Default export? Named export? What type? What props signature?
- **Type Validation** - How to ensure exported module conforms to expected shape?
- **Metadata** - Where to declare routes, configuration, lifecycle hooks?
- **Framework Adapter** - Fragment System uses `fragmentReactPlugin` to wrap components properly; MFE assumes raw React component
- **Multiple Exports from Single Module** - Cannot expose both component and method from one entry point

## Real-World Use Case

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

## Impact

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

## Recommended Solution

**Use filesystem conventions to define MFE structure**, similar to modern meta-frameworks (Next.js, Remix, SvelteKit):

### Filesystem-Based Convention

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
│   │   │       ├── index.route.tsx      # -> /analytics (base route)
│   │   │       └── settings.route.tsx   # -> /analytics/settings
│   │   └── presentation/
│   │       ├── presentation.component.tsx
│   │       └── routes/
│   │           ├── index.route.tsx      # -> /analytics/presentation (base)
│   │           ├── fullscreen.route.tsx # -> /analytics/presentation/fullscreen
│   │           └── reports/
│   │               ├── index.route.tsx  # -> /analytics/presentation/reports
│   │               └── [id].route.tsx   # -> /analytics/presentation/reports/:id (dynamic)
│   ├── methods/
│   │   └── initialize.method.ts         # Non-route method
│   └── mfe.config.ts
```

**Build tool automatically:**
- Discovers components from `components/` directory structure
- Each component can have its own `routes/` subdirectory
- Generates paths from file path: `components/presentation/routes/reports/[id].route.tsx` -> `/analytics/presentation/reports/:id`
- Routes are scoped per component, making it clear which routes belong to which component
- Extracts metadata from each component and route file
- Creates manifest with all discovered components and their routes

### Entry File Format

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

- **Single source of truth** - Metadata defined once, used in both manifest and runtime code
- **Type safety** - TypeScript ensures consistency between metadata and usage
- **No duplication** - Same constants used in manifest extraction and component logic
- **Manifest always aligned** - Build tool extracts from the same source code that component uses
- **Statically analyzable** - Helper functions are identity functions, build tool can extract values
- **Ergonomic named access** - Use `requiredProperties.user_context` instead of `requiredProperties[0]`
- **Better refactoring** - Rename keys in one place, TypeScript catches all usages

**Key Requirement: Static Analysis**

Regardless of whether metadata is in separate `.json` files or exported from source code, it **MUST be statically analyzable**:

- Literal values: `{ path: '/analytics' }`
- Helper functions: `defineRoutes([...])`
- Exported constants: `export const routes = defineRoutes(...)`
- Dynamic expressions: `{ path: computePath() }` (NOT ALLOWED)
- Runtime values: `{ path: process.env.BASE_PATH }` (NOT ALLOWED)
- Function calls in values: `{ path: getPath() }` (NOT ALLOWED)

The build tool extracts metadata **without executing JavaScript**, generating pure JSON that can be read by any tool (SSR, type registries, dev servers) without loading the MFE code.

**Why This Matters:**
- Metadata defined once -> used in manifest AND runtime code
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

### Build-Time Manifest Generation

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

### Benefits

- **No manual manifest maintenance** - Generated from filesystem + metadata (JSON or extracted from code)
- **Static metadata** - Either pure JSON files or statically extracted from code
- **Clear conventions** - `*.component.tsx` for components, metadata either in `.json` or `export const metadata`
- **Framework adapter via metadata** - Can specify framework in metadata
- **Declarative metadata** - Routes, config extracted to JSON at build time
- **Validation at build time** - Invalid metadata = build failure
- **Tooling-friendly** - Final JSON output readable by any tool without executing code
- **Developer choice** - Can write metadata in JSON files OR in TypeScript (extracted to JSON at build time)
- **Filesystem-based routing** - Optional: Use `routes/` directory structure for automatic route discovery (like Next.js, Remix, SvelteKit)

### Framework Adapter via Metadata

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

## References

- Fragment System: `defineFragmentComponent` / `defineFragmentMethod` pattern
- Module Federation: Raw `exposes` mechanism (no abstraction)
- Related sections:
  - `design.md` - Decision 12: Module Federation 2.0 (shows raw exposes)
  - `design.md` - Decision 14: MFE Bridge Interfaces (assumes React component)
