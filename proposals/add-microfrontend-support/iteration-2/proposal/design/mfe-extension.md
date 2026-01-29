# Design: MFE Extension

This document covers the Extension type and its usage in the MFE system.

---

## Context

Extension is the binding type that connects an [MFE entry](./mfe-entry-mf.md) to an [extension domain](./mfe-domain.md). While MfeEntry defines what an MFE can do (its contract) and ExtensionDomain defines where MFEs can mount (the slot), Extension creates the actual instance by specifying which entry mounts into which domain, along with UI metadata specific to that mounting.

Extensions are registered dynamically at runtime and can be added/removed at any time during the application lifecycle.

## Definition

**Extension**: A GTS type that binds an MfeEntry to an ExtensionDomain, creating a concrete MFE instance. It includes UI metadata that must conform to the domain's `extensionsUiMeta` schema.

---

## Extension Schema

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

## TypeScript Interface Definition

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
