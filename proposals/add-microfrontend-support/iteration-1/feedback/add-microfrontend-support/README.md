# Microfrontend Feedback

Comments and feedback on the `add-microfrontend-support` proposal.

---

## Vision

The **Fragment system** is a micro-frontend architecture that enables teams to develop, deploy, and maintain independent pieces of the application separately. Instead of building one monolithic frontend, the application is composed of multiple Fragments, each owned by different teams and deployed on their own schedules.

Key benefits: independent deployments, team autonomy, code isolation, scalable development, and framework-agnostic core.

See [vision/README.md](./vision/README.md) for the full specification, including:
- [Glossary](./vision/glossary.md) - Key terms and definitions
- [Principles](./vision/principles.md) - Core design principles
- [Federation](./vision/federation.md) - The orchestrator service
- [Fragment](./vision/fragment.md) - Fragment structure and development

## Comments to add-microfrontend-support proposal

### Deployment & Versioning

| # | File | Summary |
|---|------|---------|
| 1 | [missing-declarative-metadata.md](./comments/missing-declarative-metadata.md) | MfManifest lacks metadata for routes, feature flags, and translations - preventing SSR optimization and preloading |
| 2 | [package-level-sharing-tree-shaking.md](./comments/package-level-sharing-tree-shaking.md) | Module Federation shares entire packages, losing tree-shaking benefits (500%+ overhead for utility libraries) |
| 3 | [missing-cache-busting-strategy.md](./comments/missing-cache-busting-strategy.md) | No content hash or versioning strategy for remoteEntry URLs - users may get stale code after deployments |

### Local Development

| # | File | Summary |
|---|------|---------|
| 4 | [missing-dev-workflow.md](./comments/missing-dev-workflow.md) | No specification for dev server, URL overrides, HMR, or proxy mode for local MFE development |

### Type System & Architecture

| # | File | Summary |
|---|------|---------|
| 5 | [undefined-vendor-type-registration.md](./comments/undefined-vendor-type-registration.md) | Unclear how vendor MFEs register custom GTS types - no workflow for type schema distribution |
| 6 | [missing-module-export-abstraction.md](./comments/missing-module-export-abstraction.md) | No abstraction layer for Module Federation exports - unclear what MFEs should export and how |
| 7 | [react-version-compatibility.md](./comments/react-version-compatibility.md) | Unclear how different React versions work together - LoadedMfe type assumes direct rendering |
