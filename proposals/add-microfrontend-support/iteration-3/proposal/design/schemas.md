# Design: GTS Schema Definitions

This document contains the JSON Schema definitions for all MFE system types. These schemas are registered with the TypeSystemPlugin for runtime validation.

**Related Documents:**
- [Type System](./type-system.md) - TypeSystemPlugin interface, GTS implementation, contract validation
- [MFE Entry](./mfe-entry-mf.md) - MfeEntry and MfeEntryMF type details
- [MFE Manifest](./mfe-manifest.md) - MfManifest type details
- [MFE Domain](./mfe-domain.md) - ExtensionDomain type details
- [MFE Actions](./mfe-actions.md) - Action and ActionsChain type details
- [MFE Shared Property](./mfe-shared-property.md) - SharedProperty type details

---

## Overview

The MFE type system consists of **6 core types** plus **2 MF-specific types**:

| Category | Type | GTS Type ID |
|----------|------|-------------|
| Core | MFE Entry (Abstract) | `gts.hai3.screensets.mfe.entry.v1~` |
| Core | Extension Domain | `gts.hai3.screensets.ext.domain.v1~` |
| Core | Extension | `gts.hai3.screensets.ext.extension.v1~` |
| Core | Shared Property | `gts.hai3.screensets.ext.shared_property.v1~` |
| Core | Action | `gts.hai3.screensets.ext.action.v1~` |
| Core | Actions Chain | `gts.hai3.screensets.ext.actions_chain.v1~` |
| MF-Specific | MF Manifest | `gts.hai3.screensets.mfe.mf.v1~` |
| MF-Specific | MFE Entry MF (Derived) | `gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~` |

---

## Core Type Schemas

### MFE Entry Schema (Abstract Base)

The base contract type for all MFE entries. Derived types add loader-specific fields.

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

### Extension Domain Schema

Defines an extension point where MFEs can be mounted.

```json
{
  "$id": "gts://gts.hai3.screensets.ext.domain.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "x-gts-ref": "/$id",
      "$comment": "The GTS type ID for this instance"
    },
    "sharedProperties": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.shared_property.v1~*" }
    },
    "actions": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.action.v1~*" },
      "$comment": "Action type IDs that can target extensions in this domain"
    },
    "extensionsActions": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.action.v1~*" },
      "$comment": "Action type IDs extensions can send when targeting this domain"
    },
    "extensionsUiMeta": { "type": "object" },
    "defaultActionTimeout": {
      "type": "number",
      "minimum": 1,
      "$comment": "Default timeout in milliseconds for actions targeting this domain. REQUIRED."
    }
  },
  "required": ["id", "sharedProperties", "actions", "extensionsActions", "extensionsUiMeta", "defaultActionTimeout"]
}
```

### Extension Schema

Binds an MFE entry to a domain.

```json
{
  "$id": "gts://gts.hai3.screensets.ext.extension.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "x-gts-ref": "/$id",
      "$comment": "The GTS type ID for this instance"
    },
    "domain": {
      "x-gts-ref": "gts.hai3.screensets.ext.domain.v1~*",
      "$comment": "ExtensionDomain type ID to mount into"
    },
    "entry": {
      "x-gts-ref": "gts.hai3.screensets.mfe.entry.v1~*",
      "$comment": "MfeEntry type ID to mount"
    },
    "uiMeta": {
      "type": "object",
      "$comment": "Must conform to the domain's extensionsUiMeta schema"
    }
  },
  "required": ["id", "domain", "entry", "uiMeta"]
}
```

### Shared Property Schema

Represents a typed value passed from host to MFE.

```json
{
  "$id": "gts://gts.hai3.screensets.ext.shared_property.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "x-gts-ref": "/$id",
      "$comment": "The GTS type ID for this shared property"
    },
    "value": {
      "$comment": "The shared property value"
    }
  },
  "required": ["id", "value"]
}
```

### Action Schema

A typed message with target and optional payload.

```json
{
  "$id": "gts://gts.hai3.screensets.ext.action.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "type": {
      "x-gts-ref": "/$id",
      "$comment": "Self-reference to this action's type ID"
    },
    "target": {
      "type": "string",
      "oneOf": [
        { "x-gts-ref": "gts.hai3.screensets.ext.domain.v1~*" },
        { "x-gts-ref": "gts.hai3.screensets.ext.extension.v1~*" }
      ],
      "$comment": "Type ID of the target ExtensionDomain or Extension"
    },
    "payload": {
      "type": "object",
      "$comment": "Optional action payload"
    },
    "timeout": {
      "type": "number",
      "minimum": 1,
      "$comment": "Optional timeout override in milliseconds"
    }
  },
  "required": ["type", "target"]
}
```

### Actions Chain Schema

A linked structure of actions with success/failure branches.

```json
{
  "$id": "gts://gts.hai3.screensets.ext.actions_chain.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "action": {
      "type": "object",
      "$ref": "gts://gts.hai3.screensets.ext.action.v1~"
    },
    "next": {
      "type": "object",
      "$ref": "gts://gts.hai3.screensets.ext.actions_chain.v1~"
    },
    "fallback": {
      "type": "object",
      "$ref": "gts://gts.hai3.screensets.ext.actions_chain.v1~"
    }
  },
  "required": ["action"]
}
```

---

## MF-Specific Type Schemas

### MF Manifest Schema

Module Federation configuration for loading MFE bundles.

```json
{
  "$id": "gts://gts.hai3.screensets.mfe.mf.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "x-gts-ref": "/$id",
      "$comment": "The GTS type ID for this instance"
    },
    "remoteEntry": {
      "type": "string",
      "format": "uri",
      "$comment": "URL to the remoteEntry.js file"
    },
    "remoteName": {
      "type": "string",
      "minLength": 1,
      "$comment": "Module Federation container name"
    },
    "sharedDependencies": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string", "$comment": "Package name (e.g., 'react', 'lodash')" },
          "requiredVersion": { "type": "string", "$comment": "Semver range (e.g., '^18.0.0')" },
          "singleton": {
            "type": "boolean",
            "default": false,
            "$comment": "If true, share single instance. Default false = isolated instances."
          }
        },
        "required": ["name", "requiredVersion"]
      },
      "$comment": "Dependencies to share for bundle optimization"
    },
    "entries": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~*" },
      "$comment": "Convenience field for discovery - lists MfeEntryMF type IDs"
    }
  },
  "required": ["id", "remoteEntry", "remoteName"]
}
```

### MFE Entry MF Schema (Derived)

Module Federation implementation extending the base MfeEntry.

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

---

## Schema Registration

All schemas are registered during ScreensetsRegistry initialization:

```typescript
// packages/screensets/src/mfe/init.ts

import { mfeGtsSchemas } from './schemas/gts-schemas';

function registerHai3Types(plugin: TypeSystemPlugin): void {
  // Register core schemas (6 types)
  plugin.registerSchema('gts.hai3.screensets.mfe.entry.v1~', mfeGtsSchemas.mfeEntry);
  plugin.registerSchema('gts.hai3.screensets.ext.domain.v1~', mfeGtsSchemas.extensionDomain);
  plugin.registerSchema('gts.hai3.screensets.ext.extension.v1~', mfeGtsSchemas.extension);
  plugin.registerSchema('gts.hai3.screensets.ext.shared_property.v1~', mfeGtsSchemas.sharedProperty);
  plugin.registerSchema('gts.hai3.screensets.ext.action.v1~', mfeGtsSchemas.action);
  plugin.registerSchema('gts.hai3.screensets.ext.actions_chain.v1~', mfeGtsSchemas.actionsChain);

  // Register MF-specific schemas (2 types)
  plugin.registerSchema('gts.hai3.screensets.mfe.mf.v1~', mfeGtsSchemas.mfManifest);
  plugin.registerSchema(
    'gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~',
    mfeGtsSchemas.mfeEntryMf
  );
}
```
