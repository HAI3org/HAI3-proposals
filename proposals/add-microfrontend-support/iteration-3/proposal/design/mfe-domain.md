# Design: MFE Extension Domain

This document covers the ExtensionDomain type and its usage in the MFE system.

---

## Context

ExtensionDomain defines an extension point where MFEs can be mounted. It acts as the "slot" or "container" concept in the host application. Domains are hierarchical - HAI3 provides base layout domains (sidebar, popup, screen, overlay), and vendor screensets can define their own specialized domains.

The domain defines the contract with [extensions](./mfe-extension.md) by declaring:
- What [shared properties](./mfe-shared-property.md) are provided to MFEs in this domain
- What [action types](./mfe-actions.md) can target extensions in this domain
- What action types extensions can send (when targeting this domain)
- The schema for extension UI metadata (validated against `uiMeta` in [Extension](./mfe-extension.md))

## Definition

**ExtensionDomain**: A GTS type that defines an extension point with its communication contract (shared properties, actions) and UI metadata schema. Extensions mount into domains, and the domain validates that mounted extensions satisfy its contract requirements.

---

## Extension Domain Schema (Base)

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
      "$comment": "Default timeout in milliseconds for actions targeting this domain. REQUIRED. All actions use this unless they specify their own timeout override."
    }
  },
  "required": ["id", "sharedProperties", "actions", "extensionsActions", "extensionsUiMeta", "defaultActionTimeout"]
}
```

## TypeScript Interface Definition

```typescript
/**
 * Defines an extension point (domain) where MFEs can be mounted
 * GTS Type: gts.hai3.screensets.ext.domain.v1~
 */
interface ExtensionDomain {
  /** The GTS type ID for this domain */
  id: string;
  /** SharedProperty type IDs provided to MFEs in this domain */
  sharedProperties: string[];
  /** Action type IDs that can target extensions in this domain */
  actions: string[];
  /** Action type IDs extensions can send when targeting this domain */
  extensionsActions: string[];
  /** JSON Schema for UI metadata extensions must provide */
  extensionsUiMeta: JSONSchema;
  /** Default timeout for actions targeting this domain (milliseconds, REQUIRED) */
  defaultActionTimeout: number;
}
```

---

## Hierarchical Extension Domains

Extension domains can be hierarchical. HAI3 provides base layout domains, and vendor screensets can define their own. Base domains are registered via the Type System plugin.

### Base Layout Domains

When using GTS plugin, base domains follow the format `gts.hai3.screensets.ext.domain.<layout>.v1~`:
- `gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.sidebar.v1~` - Sidebar panels
- `gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.popup.v1~` - Modal popups
- `gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.screen.v1~` - Full screen views
- `gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.overlay.v1~` - Floating overlays

### Vendor-Defined Domains

Vendors define their own domains following the GTS type ID format:

```typescript
// Example: Dashboard screenset defines widget slot domain
// Type ID: gts.hai3.screensets.ext.domain.v1~acme.dashboard.layout.widget_slot.v1~

const widgetSlotDomain: ExtensionDomain = {
  id: 'gts.hai3.screensets.ext.domain.v1~acme.dashboard.layout.widget_slot.v1~',
  sharedProperties: [
    // Properties provided to MFEs in this domain
    'gts.hai3.screensets.ext.shared_property.v1~hai3.screensets.props.user_context.v1',
  ],
  actions: [
    // Action types that can target extensions in this domain
    'gts.hai3.screensets.ext.action.v1~acme.dashboard.ext.refresh.v1~',
  ],
  extensionsActions: [
    // Action types extensions can send when targeting this domain
    'gts.hai3.screensets.ext.action.v1~acme.dashboard.ext.data_update.v1~',
  ],
  extensionsUiMeta: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      icon: { type: 'string' },
      size: { enum: ['small', 'medium', 'large'] },
    },
    required: ['title', 'size'],
  },
  defaultActionTimeout: 30000,
};
```

---

## Domain-Specific Layout Semantics

Different domain layouts have different semantics for extension lifecycle:

- **Popup, Sidebar, Overlay** - Can be shown/hidden (extension can be loaded/unloaded)
- **Screen** - Always has a screen selected (can navigate between screens, but can't have "no screen")

The ActionsChainsMediator handles these semantics when processing actions. See [MFE Actions](./mfe-actions.md) for details on action chain execution.
