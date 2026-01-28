# Design: MFE Domain and Extension

This document covers the ExtensionDomain and Extension types and their usage in the MFE system.

**Related Documents:**
- [MFE Entry](./mfe-entry-mf.md) - MfeEntry contract definition
- [MFE Actions](./mfe-actions.md) - Action types and mediation
- [MFE Shared Property](./mfe-shared-property.md) - Property definitions
- [Type System](./type-system.md) - Contract validation rules

---

## Context

ExtensionDomain defines an extension point where MFE instances can be mounted. Domains can exist at **any level of the hierarchy**:

1. The **host application** can define domains (e.g., sidebar, popup, screen, overlay)
2. An **MFE itself** can define its own domains for nested extensions
3. An MFE can be **both** - an extension to its parent's domain AND a domain provider for its own children

This hierarchical composition enables deeply nested structures where each MFE instance can host additional MFE instances.

The domain defines the contract with [extensions](#extension) by declaring:
- What [shared properties](./mfe-shared-property.md) are provided to MFEs in this domain
- What [action types](./mfe-actions.md) can target extensions in this domain
- What action types extensions can send (when targeting this domain)
- The schema for extension UI metadata (validated against `uiMeta` in [Extension](#extension))

---

## ExtensionDomain

### Definition

**ExtensionDomain**: A GTS type that defines an extension point with its communication contract (shared properties, actions) and UI metadata schema. Extensions mount into domains, and the domain validates that mounted extensions satisfy its contract requirements.

### Extension Domain Schema

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

### TypeScript Interface Definitions

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

## Contract Matching

For an MFE entry to be mountable into a domain, the following subset relationships must hold:

```
+-------------------+                      +-------------------+
|   MfeEntry        |                      |  ExtensionDomain  |
+-------------------+                      +-------------------+
|                   |                      |                   |
| requiredProperties| -----(subset)------> | sharedProperties  |
|                   |   Domain provides    |                   |
|                   |   all required props |                   |
+-------------------+                      +-------------------+
|                   |                      |                   |
| actions           | -----(subset)------> | extensionsActions |
|   (MFE sends)     |   Domain accepts     |   (domain allows) |
|                   |   all MFE actions    |                   |
+-------------------+                      +-------------------+
|                   |                      |                   |
| domainActions     | <----(subset)------- | actions           |
|   (MFE receives)  |   MFE handles all    |   (domain sends)  |
|                   |   domain actions     |                   |
+-------------------+                      +-------------------+
```

**Rules:**
1. `entry.requiredProperties` must be a subset of `domain.sharedProperties`
2. `entry.actions` must be a subset of `domain.extensionsActions`
3. `domain.actions` must be a subset of `entry.domainActions`

See [Type System - Contract Matching](./type-system.md#decision-8-contract-matching-rules) for implementation details.

---

## Hierarchical Extension Domains

Extension domains form a hierarchical structure where domains can exist at any level:

```
HOST APPLICATION
  └── Domain A (host's domain - e.g., sidebar)
        └── Extension 1 (MFE instance that is ALSO a domain provider)
              └── Domain B (MFE's own domain - e.g., widget-slot)
                    └── Extension 2 (nested MFE instance)
                          └── Domain C (can go deeper...)
                                └── Extension 3 (deeply nested MFE)
```

HAI3 provides base layout domains for the host level, and any MFE can define its own domains for nested composition. Base domains are registered via the Type System plugin.

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

---

## Extension

### Definition

**Extension**: A GTS type that binds an MfeEntry to an ExtensionDomain, creating a concrete MFE instance. It includes UI metadata that must conform to the domain's `extensionsUiMeta` schema.

Extension is the binding type that connects an [MFE entry](./mfe-entry-mf.md) to an extension domain, creating a concrete MFE **instance**. While MfeEntry defines what an MFE can do (its contract) and ExtensionDomain defines where MFE instances can mount (the slot), Extension creates the actual instance by specifying which entry mounts into which domain, along with UI metadata specific to that mounting.

**Instance-level isolation (default)**: With HAI3's default handler (`MfeHandlerMF`), each Extension creates an isolated MFE instance. Mounting the same MFE entry twice (via two different Extension registrations) creates two completely independent runtime instances - they cannot access each other's state, styles, or internal data. Custom handlers can implement different isolation strategies (e.g., allowing internal MFE instances to share resources).

Extensions are registered dynamically at runtime and can be added/removed at any time during the application lifecycle.

### Extension Schema

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

### TypeScript Interface Definition

```typescript
/**
 * Binds an MFE entry to an extension domain
 * GTS Type: gts.hai3.screensets.ext.extension.v1~
 */
interface Extension {
  /** The GTS type ID for this extension */
  id: string;
  /** ExtensionDomain type ID to mount into */
  domain: string;
  /** MfeEntry type ID to mount */
  entry: string;
  /** UI metadata instance conforming to domain's extensionsUiMeta schema */
  uiMeta: Record<string, unknown>;
}
```

### Extension Example

```typescript
const analyticsExtension: Extension = {
  id: 'gts.hai3.screensets.ext.extension.v1~acme.dashboard.widgets.analytics.v1~',
  domain: 'gts.hai3.screensets.ext.domain.v1~acme.dashboard.layout.widget_slot.v1~',
  entry: 'gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~acme.analytics.mfe.chart.v1',
  uiMeta: {
    title: 'Analytics Dashboard',
    icon: 'chart-line',
    size: 'large',
  },
};
```
