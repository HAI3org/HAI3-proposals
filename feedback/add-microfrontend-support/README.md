# Microfrontend Comments

Comments and feedback on the `add-microfrontend-support` proposal.

---

## Deployment & Versioning

| # | File | Summary |
|---|------|---------|
| 1 | [missing-declarative-metadata.md](./missing-declarative-metadata.md) | MfManifest lacks metadata for routes, feature flags, and translations - preventing SSR optimization and preloading |
| 2 | [package-level-sharing-tree-shaking.md](./package-level-sharing-tree-shaking.md) | Module Federation shares entire packages, losing tree-shaking benefits (500%+ overhead for utility libraries) |
| 3 | [missing-cache-busting-strategy.md](./missing-cache-busting-strategy.md) | No content hash or versioning strategy for remoteEntry URLs - users may get stale code after deployments |

## Local Development

| # | File | Summary |
|---|------|---------|
| 4 | [missing-dev-workflow.md](./missing-dev-workflow.md) | No specification for dev server, URL overrides, HMR, or proxy mode for local MFE development |

## Type System & Architecture

| # | File | Summary |
|---|------|---------|
| 5 | [undefined-vendor-type-registration.md](./undefined-vendor-type-registration.md) | Unclear how vendor MFEs register custom GTS types - no workflow for type schema distribution |
| 6 | [missing-module-export-abstraction.md](./missing-module-export-abstraction.md) | No abstraction layer for Module Federation exports - unclear what MFEs should export and how |
| 7 | [react-version-compatibility.md](./react-version-compatibility.md) | Unclear how different React versions work together - LoadedMfe type assumes direct rendering |
