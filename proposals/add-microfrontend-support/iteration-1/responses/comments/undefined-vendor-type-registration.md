# Response: Undefined Vendor Type Registration

## Status: Addressed in Updated Proposal

## Summary

The feedback asked how vendor MFEs register custom GTS types. This was based on a misunderstanding of how GTS derived types work. The proposal has been updated to clarify the vendor package model.

## The Misunderstanding

The feedback assumed vendor types like `gts.acme.analytics.ext.action.data_updated.v1~` are standalone types requiring separate registration. This is incorrect.

**Vendor types are DERIVED types** extending HAI3 base types:

```
Base type:     gts.hai3.screensets.ext.action.v1~
                         ↓ extends
Derived type:  gts.hai3.screensets.ext.action.v1~acme.analytics.ext.data_updated.v1~
               └──────────── base ────────────┘└────────── vendor qualifier ─────────┘
```

## The Actual Model

### Vendor Packages

Vendors provide complete packages containing:
- **Derived type definitions** (schemas) extending HAI3 base types
- **Well-known instances** (MFE entries, manifests, extensions, actions)
- All with IDs following the pattern `~<vendor>.*.*.*v*`

### Diagram (Added to Proposal)

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

### Polymorphic Schema Resolution

GTS supports polymorphic schema resolution. When an action instance arrives:

```typescript
{
  type: 'gts.hai3.screensets.ext.action.v1~acme.analytics.ext.data_updated.v1~',
  target: '...',
  payload: { datasetId: 'ds-123', metrics: {...} }
}
```

The mediator:
1. Recognizes this as a derived type of `gts.hai3.screensets.ext.action.v1~`
2. Resolves the payload schema from the derived type definition
3. Validates the payload polymorphically

## Why Feedback's Options Were Not Needed

The feedback suggested:
- **Option A**: Execute MFE code for registration → Not needed, types are data
- **Option B**: Separate type registry → Not needed, TypeSystemPlugin handles this
- **Option C**: Bundle types in manifest → Partially correct, but broader - vendor packages

## What's In Scope vs Out of Scope

| In Scope | Out of Scope |
|----------|--------------|
| `TypeSystemPlugin.registerSchema()` interface | How packages are delivered to runtime |
| `ScreensetsRegistry.register*()` interface | Package manager backend |
| GTS derived type format | Package storage/versioning |
| Polymorphic validation | Upload workflows |

## Changes Made

Added **Decision 5: Vendor Type Registration** to `design/type-system.md` with:
- Vendor package concept and diagram
- GTS derived type explanation with visual
- Example vendor action type with payload schema
- Registration flow code example

## Conclusion

The proposal now clearly explains that vendor types are derived types provided in vendor packages. The delivery mechanism is intentionally out of scope - the proposal defines the interfaces for registration, not the infrastructure for delivery.
