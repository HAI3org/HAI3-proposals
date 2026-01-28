# Add Microfrontend Support - Iteration 2

## Proposal Structure

This iteration restructures the proposal documentation for improved readability by splitting large files into focused, topic-specific documents.

### Design Documents

| Document | Description |
|----------|-------------|
| [design.md](./proposal/design.md) | High-level system overview with diagrams |
| [mfe-domain.md](./proposal/design/mfe-domain.md) | ExtensionDomain type (slots for MFEs) |
| [mfe-entry-mf.md](./proposal/design/mfe-entry-mf.md) | MfeEntry and MfeEntryMF types (MFE contracts) |
| [mfe-extension.md](./proposal/design/mfe-extension.md) | Extension type (MFE instances) |
| [mfe-manifest.md](./proposal/design/mfe-manifest.md) | MfManifest type (Module Federation config) |
| [mfe-loading.md](./proposal/design/mfe-loading.md) | Bundle loading and Module Federation |
| [mfe-actions.md](./proposal/design/mfe-actions.md) | Action and ActionsChain types |
| [mfe-shared-property.md](./proposal/design/mfe-shared-property.md) | SharedProperty type |
| [mfe-api.md](./proposal/design/mfe-api.md) | MfeEntryLifecycle and MfeBridge interfaces |
| [mfe-errors.md](./proposal/design/mfe-errors.md) | Error class hierarchy |
| [type-system.md](./proposal/design/type-system.md) | GTS type system and validation |
| [registry-runtime.md](./proposal/design/registry-runtime.md) | Runtime isolation and registration |
| [principles.md](./proposal/design/principles.md) | Design principles |

### Current Change Proposals

| Change | Description | Status | Author |
|--------|-------------|--------|--------|
| [mfe-extensibility.md](./changes/mfe-extensibility.md) | Plugin-based extensibility mechanism | - | @eddeisling |
| [missing-system-extensibility.md](./changes/missing-system-extensibility.md) | System extensibility concerns | - | @eddeisling |
| [missing-declarative-metadata.md](./changes/missing-declarative-metadata.md) | Declarative metadata for MFE registration | - | @eddeisling |
| [missing-dev-workflow.md](./changes/missing-dev-workflow.md) | Local development workflow for MFEs | - | @eddeisling |
| [centralized-services.md](./changes/centralized-services.md) | Centralized services as opt-in company decision | - | @eddeisling |

### Changes from Iteration 1

The following content was extracted from monolithic files into focused documents:

**From type-system.md:**
- GTS schemas → individual type documents (mfe-entry-mf.md, mfe-manifest.md, mfe-domain.md, mfe-extension.md, mfe-shared-property.md, mfe-actions.md)
- TypeScript interfaces → corresponding type documents
- MfeEntryLifecycle → mfe-api.md

**From registry-runtime.md:**
- Decision 10: Actions Chain Mediation → mfe-actions.md
- Decision 11: Hierarchical Extension Domains → mfe-domain.md
- Decision 14: MFE Bridge Interfaces → mfe-api.md
- Decision 17: Explicit Timeout Configuration → mfe-actions.md
- Decision 20: Domain-Specific Supported Actions → mfe-domain.md
- Decision 21: MFE Independence → principles.md

**From mfe-loading.md:**
- Decision 16: Error Class Hierarchy → mfe-errors.md
- MfManifest examples → mfe-manifest.md
- MfeEntryMF examples → mfe-entry-mf.md

**New:**
- design.md - High-level system overview with ASCII diagrams
