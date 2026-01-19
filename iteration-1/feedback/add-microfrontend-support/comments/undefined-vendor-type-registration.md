# Undefined Type Registration for Vendor MFEs

## Problem

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

## The Missing Flow

For type validation to work, JSON Schemas must be registered with the TypeSystemPlugin:

```typescript
// HAI3 registers its types at initialization - DOCUMENTED
function registerHai3Types(plugin: TypeSystemPlugin) {
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.action, mfeGtsSchemas.action);
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.extension, mfeGtsSchemas.extension);
  // ... etc
}

// But how do VENDORS register their types? NOT DOCUMENTED
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
// Error: Schema not found for type ID!
```

## Possible Solutions (None Documented)

### Option 1: Execute MFE Code for Registration

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
- **YES, you MUST execute MFE's JavaScript code BEFORE any validation**
- MFE must export type registration code
- Violates "don't execute untrusted code" principle
- What if registration code has side effects or is malicious?

### Option 2: Separate Type Definition Files

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
- No code execution needed for type registration
- Types can be validated before loading MFE
- Requires separate type registry infrastructure (not specified)
- Violates isolation (host knows MFE's types)
- How are type definitions discovered?

### Option 3: Bundle Types in Manifest

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
- Types bundled with manifest
- No separate fetch needed
- Makes manifest files large
- Still need to register before loading
- Not in current proposal

## Questions

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

## Impact

**This affects:**
- Contract validation (can't validate without schemas)
- Vendor onboarding (how do vendors define types?)
- Type discovery (how does host know what types exist?)

**Without clear specification:**
- Implementers will make different choices
- No standardized vendor workflow
- Unclear boundaries between host and MFE

## Recommended Solution

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

## References

- Related proposal sections:
  - `design.md` - Decision 1: Type System Plugin Interface (defines `registerSchema`)
  - `design.md` - Decision 4: HAI3 Type Registration (only covers base types)
