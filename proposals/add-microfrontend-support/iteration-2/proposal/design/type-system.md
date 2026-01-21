# Design: Type System and Contract Definitions

This document covers the Type System Plugin architecture and GTS type definitions for MFE contracts.

**Related Documents:**
- [Registry and Runtime](./registry-runtime.md) - Runtime isolation, action mediation, bridges
- [MFE Loading](./mfe-loading.md) - Module Federation loading, error handling, manifest fetching

---

## Context

HAI3 needs to support microfrontend (MFE) architecture where independent applications can be composed into a host application. Each MFE is a separately deployed unit with its own HAI3 state instance. Communication between host and MFE must be explicit, type-safe, and controlled.

The type system for MFE contracts is abstracted through a **Type System Plugin** interface, allowing different type system implementations while shipping GTS as the default.

### Key Principle: Opaque Type IDs

The @hai3/screensets package treats **type IDs as opaque strings**. All type ID understanding (parsing, format validation, building) is delegated to the TypeSystemPlugin. When metadata about a type ID is needed, call plugin methods (`parseTypeId`, `getAttribute`, etc.) directly.

### Stakeholders

- **HAI3 Host Application**: Defines extension domains and orchestrates MFE communication
- **MFE Vendors**: Create independently deployable extensions
- **End Users**: Experience seamless integration of multiple MFEs
- **Type System Providers**: Implement Type System plugin interface for custom type systems

### Constraints

- State isolation: No direct state access between host and MFE
- Type safety: All communication contracts defined via pluggable Type System
- Security: MFEs cannot access host internals
- Performance: Lazy loading of MFE bundles
- Plugin requirement: Type System plugin must be provided at initialization

## Goals / Non-Goals

### Goals

1. **State Isolation**: Each MFE has its own HAI3 state instance
2. **Symmetric Contracts**: Clear bidirectional communication contracts
3. **Contract Validation**: Compile-time and runtime validation of compatibility
4. **Mediated Actions**: Centralized action chain delivery through ActionsChainsMediator
5. **Hierarchical Domains**: Support nested extension points
6. **Pluggable Type System**: Abstract Type System as a plugin with GTS as default
7. **Opaque Type IDs**: Screensets package treats type IDs as opaque strings

### Non-Goals

1. **Direct State Sharing**: No shared Redux store between host and MFE
2. **Event Bus Bridging**: No automatic event propagation across boundaries
3. **Hot Module Replacement**: MFE updates require reload (but hot-swap of extensions IS supported)
4. **Version Negotiation**: Single version per MFE entry
5. **Multiple Concurrent Plugins**: Only one Type System plugin per application instance
6. **Static Extension Registry**: Extensions are NOT known at initialization time (dynamic registration is the model)

---

## Decisions

### Decision 1: Type System Plugin Interface

The @hai3/screensets package defines a `TypeSystemPlugin` interface that abstracts type system operations. This allows different type system implementations while shipping GTS as the default.

The screensets package treats type IDs as **opaque strings**. The plugin is responsible for all type ID parsing, validation, and building.

#### Plugin Interface Definition

```typescript
/**
 * Result of schema validation
 */
interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

interface ValidationError {
  path: string;
  message: string;
  keyword: string;
}

/**
 * Result of compatibility check
 */
interface CompatibilityResult {
  compatible: boolean;
  breaking: boolean;
  changes: CompatibilityChange[];
}

interface CompatibilityChange {
  type: 'added' | 'removed' | 'modified';
  path: string;
  description: string;
}

/**
 * Result of attribute access
 */
interface AttributeResult {
  /** The type ID that was queried */
  typeId: string;
  /** The property path that was accessed */
  path: string;
  /** Whether the attribute was found */
  resolved: boolean;
  /** The value if resolved */
  value?: unknown;
  /** Error message if not resolved */
  error?: string;
}

/**
 * Type System Plugin interface
 * Abstracts type system operations for MFE contracts.
 *
 * The screensets package treats type IDs as OPAQUE STRINGS.
 * All type ID understanding is delegated to the plugin.
 */
interface TypeSystemPlugin {
  /** Plugin identifier */
  readonly name: string;

  /** Plugin version */
  readonly version: string;

  // === Type ID Operations ===

  /**
   * Check if a string is a valid type ID format.
   * Used before any operation that requires a valid type ID.
   */
  isValidTypeId(id: string): boolean;

  /**
   * Build a type ID from plugin-specific options.
   * The options object is plugin-specific and opaque to screensets.
   */
  buildTypeId(options: Record<string, unknown>): string;

  /**
   * Parse a type ID into plugin-specific components.
   * Returns a generic object - the structure is plugin-defined.
   * Use this when you need metadata about a type ID.
   */
  parseTypeId(id: string): Record<string, unknown>;

  // === Schema Registry ===

  /**
   * Register a JSON Schema for a type ID
   */
  registerSchema(typeId: string, schema: JSONSchema): void;

  /**
   * Validate an instance against the schema for a type ID
   */
  validateInstance(typeId: string, instance: unknown): ValidationResult;

  /**
   * Get the schema registered for a type ID
   */
  getSchema(typeId: string): JSONSchema | undefined;

  // === Query ===

  /**
   * Query registered type IDs matching a pattern
   */
  query(pattern: string, limit?: number): string[];

  // === Compatibility (REQUIRED) ===

  /**
   * Check compatibility between two type versions
   */
  checkCompatibility(oldTypeId: string, newTypeId: string): CompatibilityResult;

  // === Attribute Access (REQUIRED for dynamic schema resolution) ===

  /**
   * Get an attribute value from a type using property path.
   * Used for dynamic schema resolution (e.g., getting domain's extensionsUiMeta).
   */
  getAttribute(typeId: string, path: string): AttributeResult;
}
```

#### GTS Plugin Implementation

The GTS plugin implements `TypeSystemPlugin` using `@globaltypesystem/gts-ts`:

```typescript
// packages/screensets/src/mfe/plugins/gts/index.ts
import { Gts, GtsStore, GtsQuery } from '@globaltypesystem/gts-ts';
import type { TypeSystemPlugin, ValidationResult } from '../types';

export function createGtsPlugin(): TypeSystemPlugin {
  const gtsStore = new GtsStore();

  return {
    name: 'gts',
    version: '1.0.0',

    // Type ID operations
    isValidTypeId(id: string): boolean {
      return Gts.isValidGtsID(id);
    },

    buildTypeId(options: Record<string, unknown>): string {
      return Gts.buildGtsID(options);
    },

    parseTypeId(id: string): Record<string, unknown> {
      // GTS-specific parsing - returns vendor, package, namespace, type, version
      const parsed = Gts.parseGtsID(id);
      return {
        vendor: parsed.vendor,
        package: parsed.package,
        namespace: parsed.namespace,
        type: parsed.type,
        version: parsed.version,
        qualifier: parsed.qualifier,
      };
    },

    // Schema registry
    registerSchema(typeId: string, schema: JSONSchema): void {
      gtsStore.register(typeId, schema);
    },

    validateInstance(typeId: string, instance: unknown): ValidationResult {
      const result = gtsStore.validate(typeId, instance);
      return {
        valid: result.valid,
        errors: result.errors.map(e => ({
          path: e.instancePath,
          message: e.message,
          keyword: e.keyword,
        })),
      };
    },

    getSchema(typeId: string): JSONSchema | undefined {
      return gtsStore.getSchema(typeId);
    },

    // Query
    query(pattern: string, limit?: number): string[] {
      return GtsQuery.search(gtsStore, pattern, { limit });
    },

    // Compatibility (REQUIRED)
    checkCompatibility(oldTypeId: string, newTypeId: string) {
      return Gts.checkCompatibility(gtsStore, oldTypeId, newTypeId);
    },

    // Attribute Access (REQUIRED for dynamic schema resolution)
    getAttribute(typeId: string, path: string): AttributeResult {
      const result = gtsStore.getAttribute(typeId, path);
      return {
        typeId,
        path,
        resolved: result !== undefined,
        value: result,
        error: result === undefined ? `Attribute '${path}' not found in type '${typeId}'` : undefined,
      };
    },
  };
}

// Default export for convenience - creates a singleton plugin instance
export const gtsPlugin = createGtsPlugin();
```

### Decision 2: GTS Type ID Format and Registration

The GTS type ID format follows the structure: `gts.<vendor>.<package>.<namespace>.<type>.v<MAJOR>[.<MINOR>]~`

#### HAI3 GTS Type IDs

The type system is organized into **6 core types** that define the contract model, plus **2 MF-specific types** for Module Federation loading:

**Core Types (6 total):**

| Type | GTS Type ID | Purpose |
|------|-------------|---------|
| MFE Entry (Abstract) | `gts.hai3.screensets.mfe.entry.v1~` | Pure contract type (abstract base) |
| Extension Domain | `gts.hai3.screensets.ext.domain.v1~` | Extension point contract |
| Extension | `gts.hai3.screensets.ext.extension.v1~` | Extension binding |
| Shared Property | `gts.hai3.screensets.ext.shared_property.v1~` | Property definition |
| Action | `gts.hai3.screensets.ext.action.v1~` | Action type with target and self-id |
| Actions Chain | `gts.hai3.screensets.ext.actions_chain.v1~` | Action chain for mediation |

**MF-Specific Types (2 total):**

| Type | GTS Type ID | Purpose |
|------|-------------|---------|
| MF Manifest | `gts.hai3.screensets.mfe.mf.v1~` | Module Federation manifest (standalone) |
| MFE Entry MF (Derived) | `gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~` | Module Federation entry with manifest reference |

#### Why This Structure Eliminates Parallel Hierarchies

The previous design had parallel hierarchies:
- `MfeDefinition` (abstract) -> `MfeDefinitionMF` (derived)
- `MfeEntry` (pure contract)

This created redundancy because both hierarchies needed to track entries. The new design:

1. **Makes MfeEntry the abstract base** for entry contracts
2. **Adds MfeEntryMF as derived** that references its MfManifest
3. **MfManifest is standalone** containing Module Federation config
4. **Extension binds to MfeEntry** (or its derived types)

Benefits:
- **No parallel hierarchies**: Only one entry hierarchy
- **Future-proof**: ESM loader would add `MfeEntryEsm` derived type with its own manifest reference
- **Clear ownership**: Entry owns its contract AND references its manifest

#### Complete GTS JSON Schema Definitions

The schema definitions are distributed across the following files:

- **MFE Entry Schema (Abstract Base)**: See [MFE Entry](./mfe-entry-mf.md#mfe-entry-schema-abstract-base)
- **MFE Entry MF Schema (Derived)**: See [MFE Entry](./mfe-entry-mf.md#mfe-entry-mf-schema-derived---module-federation)
- **MF Manifest Schema (Standalone)**: See [MFE Manifest](./mfe-manifest.md#mf-manifest-schema-standalone)
- **Extension Domain Schema (Base)**: See [MFE Domain](./mfe-domain.md#extension-domain-schema-base)
- **Extension Schema**: See [MFE Extension](./mfe-extension.md#extension-schema)
- **Shared Property Schema**: See [MFE Shared Property](./mfe-shared-property.md#shared-property-schema)
- **Action Schema**: See [MFE Actions](./mfe-actions.md#action-schema)
- **Actions Chain Schema**: See [MFE Actions](./mfe-actions.md#actions-chain-schema)
- **MfeEntry Type Hierarchy**: See [MFE Entry](./mfe-entry-mf.md#mfeentry-type-hierarchy)

### Decision 3: Internal TypeScript Type Definitions

The MFE system uses internal TypeScript interfaces with a simple `id: string` field as the identifier. When metadata is needed about a type ID, call `plugin.parseTypeId(id)` directly.

#### TypeScript Interface Definitions

All MFE types use `id: string` as their identifier. The interface definitions are distributed across the following files:

- **MfeEntry / MfeEntryMF**: See [MFE Entry](./mfe-entry-mf.md#typescript-interface-definitions)
- **MfManifest / SharedDependencyConfig**: See [MFE Manifest](./mfe-manifest.md#typescript-interface-definitions)
- **ExtensionDomain**: See [MFE Domain](./mfe-domain.md#typescript-interface-definition)
- **Extension**: See [MFE Extension](./mfe-extension.md#typescript-interface-definition)
- **SharedProperty**: See [MFE Shared Property](./mfe-shared-property.md#typescript-interface-definition)
- **Action / ActionsChain**: See [MFE Actions](./mfe-actions.md#typescript-interface-definitions)
- **MfeEntryLifecycle**: See [MFE API](./mfe-api.md#mfeentrylifecycle-interface)

### Decision 4: HAI3 Type Registration via Plugin

When initializing the ScreensetsRegistry with the GTS plugin, HAI3 types are registered. There are 6 core types plus 2 MF-specific types:

```typescript
// packages/screensets/src/mfe/init.ts

import { mfeGtsSchemas } from './schemas/gts-schemas';

/** GTS Type IDs for HAI3 MFE core types (6 types) */
const HAI3_CORE_TYPE_IDS = {
  mfeEntry: 'gts.hai3.screensets.mfe.entry.v1~',
  extensionDomain: 'gts.hai3.screensets.ext.domain.v1~',
  extension: 'gts.hai3.screensets.ext.extension.v1~',
  sharedProperty: 'gts.hai3.screensets.ext.shared_property.v1~',
  action: 'gts.hai3.screensets.ext.action.v1~',
  actionsChain: 'gts.hai3.screensets.ext.actions_chain.v1~',
} as const;

/** GTS Type IDs for MF-specific types (2 types) */
const HAI3_MF_TYPE_IDS = {
  mfManifest: 'gts.hai3.screensets.mfe.mf.v1~',
  mfeEntryMf: 'gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~',
} as const;

function registerHai3Types(
  plugin: TypeSystemPlugin
): { core: typeof HAI3_CORE_TYPE_IDS; mf: typeof HAI3_MF_TYPE_IDS } {
  // Register core schemas (6 types)
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.mfeEntry, mfeGtsSchemas.mfeEntry);
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.extensionDomain, mfeGtsSchemas.extensionDomain);
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.extension, mfeGtsSchemas.extension);
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.sharedProperty, mfeGtsSchemas.sharedProperty);
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.action, mfeGtsSchemas.action);
  plugin.registerSchema(HAI3_CORE_TYPE_IDS.actionsChain, mfeGtsSchemas.actionsChain);

  // Register MF-specific schemas (2 types)
  plugin.registerSchema(HAI3_MF_TYPE_IDS.mfManifest, mfeGtsSchemas.mfManifest);
  plugin.registerSchema(HAI3_MF_TYPE_IDS.mfeEntryMf, mfeGtsSchemas.mfeEntryMf);

  return { core: HAI3_CORE_TYPE_IDS, mf: HAI3_MF_TYPE_IDS };
}
```

### Decision 5: Vendor Type Registration

Vendors (third-party MFE providers) deliver complete packages containing derived types and instances that extend HAI3's base types. This section explains how vendor packages integrate with the GTS type system.

#### Vendor Package Concept

A vendor package is a self-contained bundle that includes:

1. **Derived Type Definitions (schemas)** - Vendor-specific types that extend HAI3 base types
2. **Well-Known Instances** - Pre-defined MFE entries, manifests, extensions, and actions

All vendor package identifiers follow the pattern `~<vendor>.<package>.*.*v*` as a GTS qualifier suffix.

```
┌─────────────────────────────────────────────────────────────┐
│                    VENDOR PACKAGE                           │
│                  (e.g., acme-analytics)                     │
├─────────────────────────────────────────────────────────────┤
│  Derived Types (schemas):                                   │
│  - gts.hai3.screensets.ext.action.v1~acme.analytics.*.*.v1~│
│  - gts.hai3.screensets.mfe.entry.v1~acme.analytics.*.*.v1~ │
│                                                             │
│  Instances:                                                 │
│  - MFE entries, manifests, extensions, actions              │
│  - All IDs ending with ~acme.analytics.*.*v*                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ (delivery mechanism
                              │  out of scope)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    HAI3 RUNTIME                             │
├─────────────────────────────────────────────────────────────┤
│  TypeSystemPlugin.registerSchema() ← vendor type schemas    │
│  ScreensetsRegistry.register*()    ← vendor instances       │
│  Polymorphic validation via GTS derived type IDs            │
└─────────────────────────────────────────────────────────────┘
```

#### Derived Types and Polymorphic Validation

Vendor types are **derived types** that extend HAI3 base types using GTS's type derivation mechanism. The derived type ID includes both the base type and the vendor qualifier:

```
Base type:    gts.hai3.screensets.ext.action.v1~
                              │
                              ▼ (extends)
Derived type: gts.hai3.screensets.ext.action.v1~acme.analytics.ext.data_updated.v1~
              └──────────── base ────────────┘└────────── vendor qualifier ─────────┘
```

GTS supports **polymorphic schema resolution**: when the mediator validates an action payload, it uses the derived type's schema (which includes vendor-specific fields) while still recognizing the instance as conforming to the base action contract.

#### Example: Vendor Derived Action Type

A vendor (Acme Analytics) defines a custom action with a vendor-specific payload schema:

```typescript
// Vendor-defined derived action type
const acmeDataUpdatedActionTypeId =
  'gts.hai3.screensets.ext.action.v1~acme.analytics.ext.data_updated.v1~';

// Vendor-specific schema extending base Action
const acmeDataUpdatedSchema: JSONSchema = {
  "$id": "gts://gts.hai3.screensets.ext.action.v1~acme.analytics.ext.data_updated.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "allOf": [
    { "$ref": "gts://gts.hai3.screensets.ext.action.v1~" }
  ],
  "properties": {
    "payload": {
      "type": "object",
      "properties": {
        "datasetId": { "type": "string" },
        "metrics": {
          "type": "array",
          "items": { "type": "string" }
        },
        "timestamp": { "type": "number" }
      },
      "required": ["datasetId", "metrics"]
    }
  }
};

// Vendor registers their derived type schema
plugin.registerSchema(acmeDataUpdatedActionTypeId, acmeDataUpdatedSchema);
```

When an action instance uses this derived type ID, the mediator:
1. Recognizes it as an Action (from the base type prefix)
2. Validates the payload using the derived type's schema (with vendor-specific fields)
3. Routes it through the standard action mediation flow

#### Key Points

1. **Vendor types are DERIVED types** - They extend HAI3 base types (e.g., `gts.hai3.screensets.ext.action.v1~`) with a vendor qualifier suffix
2. **GTS polymorphic schema resolution** - The mediator validates payloads using the most specific (derived) type's schema while maintaining base type compatibility
3. **Delivery mechanism is out of scope** - HOW vendor packages are delivered to the HAI3 runtime is not defined by this proposal
4. **Interfaces for registration** - The proposal defines the registration interfaces (`TypeSystemPlugin.registerSchema()`, `ScreensetsRegistry.register*()`) that vendor packages use, not the delivery mechanism

#### Vendor Registration Flow

```typescript
// After vendor package is loaded (delivery mechanism out of scope):

// 1. Register vendor's derived type schemas
plugin.registerSchema(
  'gts.hai3.screensets.ext.action.v1~acme.analytics.ext.data_updated.v1~',
  acmeDataUpdatedSchema
);
plugin.registerSchema(
  'gts.hai3.screensets.mfe.entry.v1~acme.analytics.mfe.chart_widget.v1~',
  acmeChartWidgetEntrySchema
);

// 2. Register vendor's instances
registry.registerManifest(acmeManifest);
registry.registerEntry(acmeChartWidgetEntry);
registry.registerExtension(acmeChartExtension);
```

### Decision 6: ScreensetsRegistry Configuration

The ScreensetsRegistry requires a Type System plugin at initialization:

```typescript
// packages/screensets/src/mfe/runtime/config.ts

/**
 * Configuration for the ScreensetsRegistry
 */
interface ScreensetsRegistryConfig {
  /** Required: Type System plugin for type handling */
  typeSystem: TypeSystemPlugin;

  /** Optional: Custom error handler */
  onError?: (error: MfeError) => void;

  /** Optional: Custom loading state component */
  loadingComponent?: React.ComponentType;

  /** Optional: Custom error fallback component */
  errorFallbackComponent?: React.ComponentType<{ error: MfeError; retry: () => void }>;

  /** Optional: Enable debug logging */
  debug?: boolean;

  /** MFE loader configuration (enables hosting nested MFEs) */
  mfeLoader?: MfeLoaderConfig;

  /** Initial parent bridge (if loaded as MFE) */
  parentBridge?: MfeBridgeConnection;
}

/**
 * Create the ScreensetsRegistry with required Type System plugin
 */
function createScreensetsRegistry(
  config: ScreensetsRegistryConfig
): ScreensetsRegistry {
  const { typeSystem, ...options } = config;

  // Validate plugin
  if (!typeSystem) {
    throw new Error('ScreensetsRegistry requires a typeSystem');
  }

  // Register HAI3 types (6 core + 2 MF-specific)
  const typeIds = registerHai3Types(typeSystem);

  return new ScreensetsRegistry(typeSystem, typeIds, options);
}

// Usage with GTS (default)
import { gtsPlugin } from '@hai3/screensets/plugins/gts';

const runtime = createScreensetsRegistry({
  typeSystem: gtsPlugin,
  debug: process.env.NODE_ENV === 'development',
});

// Usage with custom plugin
import { customPlugin } from './my-custom-plugin';

const runtimeWithCustomPlugin = createScreensetsRegistry({
  typeSystem: customPlugin,
});
```

### Decision 7: Framework Plugin Model (No Static Configuration)

**Key Principles:**
- Screensets is CORE to HAI3 - automatically initialized, NOT a plugin
- The microfrontends plugin enables MFE capabilities with NO static configuration
- All MFE registrations (manifests, extensions, domains) happen dynamically at runtime

The @hai3/framework microfrontends plugin requires NO configuration. It simply enables MFE capabilities and wires the ScreensetsRegistry into the Flux data flow pattern:

```typescript
// packages/framework/src/plugins/microfrontends/index.ts

/**
 * Microfrontends plugin - enables MFE capabilities.
 * NO configuration required or accepted.
 * All MFE registration happens dynamically at runtime.
 */
function microfrontends(): FrameworkPlugin {
  return {
    name: 'microfrontends',

    setup(framework) {
      // Screensets runtime is already initialized by HAI3 core
      // We just need to get the reference and wire it into Flux
      const runtime = framework.get<ScreensetsRegistry>('screensetsRegistry');

      // Register MFE actions and effects
      framework.registerActions(mfeActions);
      framework.registerEffects(mfeEffects);
      framework.registerSlice(mfeSlice);

      // Base domains (sidebar, popup, screen, overlay) are registered
      // dynamically at runtime, not via static configuration
    },
  };
}

// App initialization example - screensets is CORE, not a plugin
import { createHAI3, microfrontends } from '@hai3/framework';

// Screensets is CORE - automatically initialized by createHAI3()
const app = createHAI3()
  .use(microfrontends())  // No configuration - just enables MFE capabilities
  .build();

// All registration happens dynamically at runtime via actions:
// - mfeActions.registerDomain({ domain })
// - mfeActions.registerExtension({ extension })
// - mfeActions.registerManifest({ manifest })

// Or via runtime API:
// - runtime.registerDomain(domain)
// - runtime.registerExtension(extension)
// - runtime.registerManifest(manifest)

// Example: Register base domains dynamically after app initialization
eventBus.on('app/ready', () => {
  mfeActions.registerDomain(HAI3_SIDEBAR_DOMAIN);
  mfeActions.registerDomain(HAI3_POPUP_DOMAIN);
  mfeActions.registerDomain(HAI3_SCREEN_DOMAIN);
  mfeActions.registerDomain(HAI3_OVERLAY_DOMAIN);
});
```

### Decision 8: Contract Matching Rules

For an MFE entry to be mountable into an extension domain, the following conditions must ALL be true:

```
1. entry.requiredProperties  SUBSET_OF  domain.sharedProperties
   (domain provides all required properties)

2. entry.actions             SUBSET_OF  domain.extensionsActions
   (domain can receive all actions entry emits)

3. domain.actions            SUBSET_OF  entry.domainActions
   (entry can handle all actions domain emits)
```

**Validation Implementation:**
```typescript
interface ContractValidationResult {
  valid: boolean;
  errors: ContractError[];
}

interface ContractError {
  type: 'missing_property' | 'unsupported_action' | 'unhandled_domain_action';
  details: string;
}

function validateContract(
  entry: MfeEntry,
  domain: ExtensionDomain
): ContractValidationResult {
  const errors: ContractError[] = [];

  // Rule 1: Required properties
  for (const prop of entry.requiredProperties) {
    if (!domain.sharedProperties.includes(prop)) {
      errors.push({
        type: 'missing_property',
        details: `Entry requires property '${prop}' not provided by domain`
      });
    }
  }

  // Rule 2: Entry actions
  for (const action of entry.actions) {
    if (!domain.extensionsActions.includes(action)) {
      errors.push({
        type: 'unsupported_action',
        details: `Entry emits action '${action}' not accepted by domain`
      });
    }
  }

  // Rule 3: Domain actions
  for (const action of domain.actions) {
    if (!entry.domainActions.includes(action)) {
      errors.push({
        type: 'unhandled_domain_action',
        details: `Domain emits action '${action}' not handled by entry`
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}
```

### Decision 9: Dynamic uiMeta Validation via Attribute Selector

**Problem:** An `Extension` instance has a `domain` field containing a type ID reference, and its `uiMeta` property must conform to that domain's `extensionsUiMeta` schema. This cannot be expressed as a static JSON Schema constraint because the domain reference is a dynamic value.

**Solution:** Use the plugin's `getAttribute()` method to resolve the domain's `extensionsUiMeta` schema at runtime.

**Implementation:**

```typescript
/**
 * Validate Extension's uiMeta against its domain's extensionsUiMeta schema
 */
function validateExtensionUiMeta(
  plugin: TypeSystemPlugin,
  extension: Extension
): ValidationResult {
  // 1. Get the domain's extensionsUiMeta schema using getAttribute
  const schemaResult = plugin.getAttribute(extension.domain, 'extensionsUiMeta');

  if (!schemaResult.resolved) {
    return {
      valid: false,
      errors: [{
        path: 'domain',
        message: `Cannot resolve extensionsUiMeta from domain '${extension.domain}'`,
        keyword: 'x-gts-attr',
      }],
    };
  }

  // 2. The resolved value is the JSON Schema for uiMeta
  const extensionsUiMetaSchema = schemaResult.value as JSONSchema;

  // 3. Create a temporary type for validation
  const tempTypeId = `${extension.id}:uiMeta:validation`;
  plugin.registerSchema(tempTypeId, extensionsUiMetaSchema);

  // 4. Validate extension.uiMeta against the resolved schema
  const result = plugin.validateInstance(tempTypeId, extension.uiMeta);

  // 5. Transform errors to include context
  return {
    valid: result.valid,
    errors: result.errors.map(e => ({
      ...e,
      path: `uiMeta.${e.path}`,
      message: `uiMeta validation failed against ${extension.domain}@extensionsUiMeta: ${e.message}`,
    })),
  };
}
```

**Integration Point:**

The ScreensetsRegistry calls `validateExtensionUiMeta()` during extension registration, after contract matching validation:

```typescript
// In ScreensetsRegistry.registerExtension()
const contractResult = validateContract(entry, domain);
if (!contractResult.valid) {
  throw new ContractValidationError(contractResult.errors);
}

const uiMetaResult = validateExtensionUiMeta(this.typeSystem, extension);
if (!uiMetaResult.valid) {
  throw new UiMetaValidationError(uiMetaResult.errors);
}

// Contract and uiMeta both valid, proceed with registration
```
