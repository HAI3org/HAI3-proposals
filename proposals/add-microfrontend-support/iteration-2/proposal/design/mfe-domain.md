# Design: MFE Extension Domain

This document covers the ExtensionDomain type and its usage in the MFE system.

---

## Context

ExtensionDomain defines an extension point where MFEs can be mounted. It acts as the "slot" or "container" concept in the host application. Domains are hierarchical - HAI3 provides base layout domains (sidebar, popup, screen, overlay), and vendor screensets can define their own specialized domains.

The domain establishes the contract with [extensions](./mfe-extension.md) by declaring:
- What [shared properties](./mfe-shared-property.md) it provides
- What [actions](./mfe-actions.md) it can emit to extensions
- What actions it accepts from extensions
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
      "$comment": "Action type IDs domain can emit to extensions"
    },
    "extensionsActions": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.ext.action.v1~*" },
      "$comment": "Action type IDs domain can receive from extensions"
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
  /** SharedProperty type IDs provided to extensions */
  sharedProperties: string[];
  /** Action type IDs domain can emit to extensions */
  actions: string[];
  /** Action type IDs domain can receive from extensions */
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
    'gts.hai3.screensets.ext.shared_property.v1~hai3.screensets.props.user_context.v1',
  ],
  actions: [
    'gts.hai3.screensets.ext.action.v1~acme.dashboard.ext.refresh.v1~',
  ],
  extensionsActions: [
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
};
```

---

## Domain-Specific Supported Actions

Each extension domain declares which HAI3 actions it supports, allowing domains to have different action support based on their layout semantics.

**Why**:
- Not all domains can support all actions semantically
- Screen domain cannot support `unload_ext` - you cannot have "no screen selected"
- Popup, Sidebar, Overlay domains can support both `load_ext` and `unload_ext`
- This enables the mediator to validate action support before delivery

### Domain Actions Field

The `ExtensionDomain` type includes an `actions` field that lists which HAI3 actions (like `HAI3_ACTION_LOAD_EXT`, `HAI3_ACTION_UNLOAD_EXT`) the domain supports:

```typescript
interface ExtensionDomain {
  id: string;
  sharedProperties: string[];
  /** HAI3 actions this domain supports (e.g., load_ext, unload_ext) */
  actions: string[];  // <-- Domain declares supported HAI3 actions
  /** Action type IDs domain can emit to extensions */
  domainActions: string[];
  /** Action type IDs domain can receive from extensions */
  extensionsActions: string[];
  extensionsUiMeta: JSONSchema;
  defaultActionTimeout: number;
}
```

### Base Domain Definitions with Supported Actions

**Popup Domain** - Supports both load and unload (modal can be shown/hidden):
```typescript
const HAI3_POPUP_DOMAIN: ExtensionDomain = {
  id: 'gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.popup.v1~',
  actions: [HAI3_ACTION_LOAD_EXT, HAI3_ACTION_UNLOAD_EXT],  // Both supported
  sharedProperties: [...],
  domainActions: [...],
  extensionsActions: [...],
  extensionsUiMeta: {...},
  defaultActionTimeout: 30000,
};
```

**Sidebar Domain** - Supports both load and unload (panel can be shown/hidden):
```typescript
const HAI3_SIDEBAR_DOMAIN: ExtensionDomain = {
  id: 'gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.sidebar.v1~',
  actions: [HAI3_ACTION_LOAD_EXT, HAI3_ACTION_UNLOAD_EXT],  // Both supported
  sharedProperties: [...],
  domainActions: [...],
  extensionsActions: [...],
  extensionsUiMeta: {...},
  defaultActionTimeout: 30000,
};
```

**Overlay Domain** - Supports both load and unload (overlay can be shown/hidden):
```typescript
const HAI3_OVERLAY_DOMAIN: ExtensionDomain = {
  id: 'gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.overlay.v1~',
  actions: [HAI3_ACTION_LOAD_EXT, HAI3_ACTION_UNLOAD_EXT],  // Both supported
  sharedProperties: [...],
  domainActions: [...],
  extensionsActions: [...],
  extensionsUiMeta: {...},
  defaultActionTimeout: 30000,
};
```

**Screen Domain** - Only supports load (you can navigate TO a screen, but cannot have "no screen"):
```typescript
const HAI3_SCREEN_DOMAIN: ExtensionDomain = {
  id: 'gts.hai3.screensets.ext.domain.v1~hai3.screensets.layout.screen.v1~',
  actions: [HAI3_ACTION_LOAD_EXT],  // NO unload - can't have "no screen selected"
  sharedProperties: [...],
  domainActions: [...],
  extensionsActions: [...],
  extensionsUiMeta: {...},
  defaultActionTimeout: 30000,
};
```

### Action Support Validation

See [MFE Actions - Action Support Validation](./mfe-actions.md#action-support-validation) for the validation implementation.

### Key Principles

1. **`load_ext` is universal**: All domains MUST support `HAI3_ACTION_LOAD_EXT` (it's how extensions are loaded)
2. **`unload_ext` is optional**: Some domains (like screen) cannot semantically support unloading
3. **Domains declare support**: Each domain explicitly lists which HAI3 actions it can handle
4. **Mediator validates**: ActionsChainsMediator checks action support before delivery
5. **Clear error messages**: When an unsupported action is attempted, [UnsupportedDomainActionError](./mfe-errors.md#error-classes) is thrown
