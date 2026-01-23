# Design: MFE Entry (Module Federation)

This document covers the MfeEntry and MfeEntryMF types and their usage in the MFE system.

---

## Context

MfeEntry defines the contract that an MFE declares with its hosting [domain](./mfe-domain.md). It specifies what [properties](./mfe-shared-property.md) the MFE requires/accepts and what [action types](./mfe-actions.md) it can send (to its domain) and receive (when targeted). The entry is referenced by [Extension](./mfe-extension.md) to bind an MFE implementation to a specific domain.

MfeEntry is abstract - it defines only the communication contract. MfeEntryMF is the concrete derived type that adds Module Federation-specific [loading](./mfe-loading.md) configuration ([manifest](./mfe-manifest.md) reference, exposed module path).

## Definition

**MfeEntry**: An abstract base GTS type defining the communication contract of an MFE - required/optional properties and bidirectional action capabilities.

**MfeEntryMF**: A derived GTS type extending MfeEntry with Module Federation 2.0 loading configuration - references an MfManifest and specifies the exposed module path.

---

## MFE Entry Schema (Abstract Base)

MfeEntry is the **abstract base type** for all entry contracts. It defines ONLY the communication interface (properties, actions). Derived types add loader-specific fields.

```json
{
  "$id": "gts://gts.hai3.screensets.mfe.entry.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "x-gts-ref": "/$id",
      "$comment": "The GTS type ID for this instance"
    },
    "requiredProperties": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.shared_property.v1~*" },
      "$comment": "SharedProperty type IDs that MUST be provided by the domain"
    },
    "optionalProperties": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.shared_property.v1~*" },
      "$comment": "SharedProperty type IDs that MAY be provided by the domain"
    },
    "actions": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.action.v1~*" },
      "$comment": "Action type IDs this MFE can send (when targeting its domain)"
    },
    "domainActions": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.action.v1~*" },
      "$comment": "Action type IDs this MFE can receive (when targeted by actions chains)"
    }
  },
  "required": ["id", "requiredProperties", "actions", "domainActions"]
}
```

## MFE Entry MF Schema (Derived - Module Federation)

The Module Federation derived type adds fields specific to Webpack 5 / Rspack Module Federation 2.0 implementation.

```json
{
  "$id": "gts://gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "allOf": [
    { "$ref": "gts://gts.hai3.screensets.mfe.entry.v1~" }
  ],
  "properties": {
    "manifest": {
      "x-gts-ref": "gts.hai3.screensets.mfe.mf.v1~*",
      "$comment": "Reference to MfManifest type ID containing Module Federation config"
    },
    "exposedModule": {
      "type": "string",
      "minLength": 1,
      "$comment": "Module Federation exposed module name (e.g., './ChartWidget')"
    }
  },
  "required": ["manifest", "exposedModule"]
}
```

## MfeEntry Type Hierarchy

```
gts.hai3.screensets.mfe.entry.v1~ (Base - Abstract Contract)
  |-- id: string (GTS type ID)
  |-- requiredProperties: x-gts-ref[] -> gts.hai3.screensets.ext.shared_property.v1~*
  |-- optionalProperties?: x-gts-ref[] -> gts.hai3.screensets.ext.shared_property.v1~*
  |-- actions: x-gts-ref[] -> gts.hai3.screensets.ext.action.v1~*
  |-- domainActions: x-gts-ref[] -> gts.hai3.screensets.ext.action.v1~*
  |
  +-- gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~ (Module Federation)
        |-- (inherits contract fields from base)
        |-- manifest: x-gts-ref -> gts.hai3.screensets.mfe.mf.v1~*
        |-- exposedModule: string

gts.hai3.screensets.mfe.mf.v1~ (Standalone - Module Federation Config)
  |-- id: string (GTS type ID)
  |-- remoteEntry: string (URL)
  |-- remoteName: string
  |-- sharedDependencies?: SharedDependencyConfig[] (code sharing + optional instance sharing)
  |     |-- name: string
  |     |-- requiredVersion: string
  |     |-- singleton?: boolean (default: false = isolated instances)
  |-- entries?: x-gts-ref[] -> gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~*
```

## TypeScript Interface Definitions

```typescript
/**
 * Defines an entry point with its communication contract (PURE CONTRACT - Abstract Base)
 * GTS Type: gts.hai3.screensets.mfe.entry.v1~
 */
interface MfeEntry {
  /** The GTS type ID for this entry */
  id: string;
  /** SharedProperty type IDs that MUST be provided by domain */
  requiredProperties: string[];
  /** SharedProperty type IDs that MAY be provided by domain (optional field) */
  optionalProperties?: string[];
  /** Action type IDs this MFE can send (when targeting its domain) */
  actions: string[];
  /** Action type IDs this MFE can receive (when targeted by actions chains) */
  domainActions: string[];
}

/**
 * Module Federation 2.0 implementation of MfeEntry
 * GTS Type: gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~
 */
interface MfeEntryMF extends MfeEntry {
  /** Reference to MfManifest type ID containing Module Federation config */
  manifest: string;
  /** Module Federation exposed module name (e.g., './ChartWidget') */
  exposedModule: string;
}
```

## Example MfeEntryMF Instance

```typescript
const chartEntry: MfeEntryMF = {
  id: 'gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~acme.analytics.mfe.chart.v1',
  requiredProperties: [
    'gts.hai3.screensets.ext.shared_property.v1~hai3.screensets.props.user_context.v1',
    'gts.hai3.screensets.ext.shared_property.v1~hai3.screensets.props.selected_date_range.v1',
  ],
  optionalProperties: [
    'gts.hai3.screensets.ext.shared_property.v1~hai3.screensets.props.theme.v1',
  ],
  actions: ['gts.hai3.screensets.ext.action.v1~acme.analytics.ext.data_updated.v1~'],
  domainActions: ['gts.hai3.screensets.ext.action.v1~acme.analytics.ext.refresh.v1~'],
  manifest: 'gts.hai3.screensets.mfe.mf.v1~acme.analytics.mfe.manifest.v1',
  exposedModule: './ChartWidget',
};
```
