# Missing Declarative Metadata

Reference: [iteration-1 change](../../iteration-1/changes/missing-declarative-metadata.md)

## Clarification

The feedback in [comments/missing-declarative-metadata.md](../../iteration-1/comments/missing-declarative-metadata.md) misunderstood the proposed change.

### What the comment understood

The change was about declaring **runtime dependencies** (API services, routers, state managers) so the host can provide shared instances:

```
MFE Manifest declares:
  - needs: ApiService v2.3
  - needs: Router v1.0
  - needs: StateManager v3.1
      ↓
Host provides shared instances
```

### What the change actually proposed

The change was about **declarative metadata for discovery** - allowing the parent app to discover MFE capabilities **before** executing JavaScript:

- Routes that MFE handles (for SSR preloading, parent router configuration)
- Feature flags required (for visibility, debugging, conditional loading)
- Translation files (for SSR prefetching)
- Capabilities metadata (domains, plugins)

This is NOT about:
- Declaring runtime dependencies for injection
- Having feature flags, router, or other services as part of HAI3

This IS about:
- Having a legal place in manifest for project-specific declarative metadata
- Allowing discovery of MFE capabilities without loading JavaScript

## Recommended Solution

1. Allow manifest files to include an extensible metadata section where projects can declare their own MFE-specific information (routes, feature flags, translations, etc.) without HAI3 prescribing what that metadata should contain.

2. Add methods for getting metadata from manifest (API to access declared metadata).
