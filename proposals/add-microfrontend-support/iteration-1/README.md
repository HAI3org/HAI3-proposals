# Add Microfrontend Support - Iteration 1

## Modifications from Initial
- **MfeEntryLifecycle Interface** - New framework-agnostic lifecycle interface replacing React-specific types
- **Framework Examples** - Added mount/unmount examples for React, Vue 3, Svelte, Vanilla JS
- **Internal vs Public API** - Clarified that `MfeLoader`/`LoadedMfe` are internal implementation details
- **Vendor Type Registration** - Added Decision 5 explaining vendor packages, derived types, and polymorphic validation
- **MFE Independence Philosophy** - Added Decision 21 explaining thin public contracts with private optimization layer
- **Architectural Vision Response** - Created vision response comparing HAI3's "independence over integration" model with feedback's "Federation owns implementation" approach

## Current Change Proposals

| Change | Description | Status | Author |
|--------|-------------|--------|--------|
| federation-vision | Alternative architecture vision based on federation model | - | @eddeisling |
| mfe-vision | HAI3's MFE architecture vision and principles | - | @gerabart |
| missing-cache-busting-strategy.md | Cache busting strategy for MFE deployments | Already Addressed<br>see in [comments/missing-cache-busting-strategy.md](./comments/missing-cache-busting-strategy.md) | @eddeisling |
| missing-declarative-metadata.md | Declarative metadata for MFE registration | Design Choice<br>see in [comments/missing-declarative-metadata.md](./comments/missing-declarative-metadata.md) | @eddeisling |
| missing-dev-workflow.md | Local development workflow for MFEs | Out of Scope<br>see in [comments/missing-dev-workflow.md](./comments/missing-dev-workflow.md) | @eddeisling |
| missing-module-export-abstraction.md | Module export abstraction layer | Addressed in Updated Proposal<br>see in [comments/missing-module-export-abstraction.md](./comments/missing-module-export-abstraction.md) | @eddeisling |
| package-level-sharing-tree-shaking.md | Package sharing and tree-shaking concerns | Design Choice<br>see in [comments/package-level-sharing-tree-shaking.md](./comments/package-level-sharing-tree-shaking.md) | @eddeisling |
| react-version-compatibility.md | React version compatibility across MFEs | Addressed in Updated Proposal<br>see in [comments/react-version-compatibility.md](./comments/react-version-compatibility.md) | @eddeisling |
| undefined-vendor-type-registration.md | Vendor type registration process | Addressed in Updated Proposal<br>see in [comments/undefined-vendor-type-registration.md](./comments/undefined-vendor-type-registration.md) | @eddeisling |

## Comments

| File | Topic | Author |
|------|-------|--------|
| missing-cache-busting-strategy.md | Response to cache busting feedback | @gerabart |
| missing-declarative-metadata.md | Response to declarative metadata feedback | @gerabart |
| missing-dev-workflow.md | Response to dev workflow feedback | @gerabart |
| missing-module-export-abstraction.md | Response to module export feedback | @gerabart |
| package-level-sharing-tree-shaking.md | Response to tree-shaking feedback | @gerabart |
| react-version-compatibility.md | Response to React compatibility feedback | @gerabart |
| undefined-vendor-type-registration.md | Response to vendor type registration feedback | @gerabart |
