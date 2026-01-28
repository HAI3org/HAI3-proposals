# Add Microfrontend Support - Iteration 3 (Revised)

## Overview

This iteration represents a comprehensive revision of the MFE proposal with significant improvements to consistency, terminology, and architecture documentation.

## Key Improvements in This Revision

### 1. Isolation Framing (Conceptual Clarification)

**Before:** Isolation was stated as an absolute architectural requirement.

**After:** Isolation is correctly framed as the **default behavior** enforced by HAI3's default handler (`MfeHandlerMF`). Custom handlers can implement different isolation strategies for internal MFEs.

This change affects all documents and provides flexibility for enterprises to share state between trusted internal MFEs when beneficial.

### 2. Instance-Level Isolation (Conceptual Clarification)

**Before:** "Each MFE is isolated"

**After:** "Each MFE **instance** is isolated" - even multiple instances of the same MFE entry are isolated from each other with the default handler.

### 3. Hierarchical Domains (Conceptual Clarification)

**Before:** Domains described as slots only in the host application.

**After:** Domains can exist at **any level**. MFEs can be BOTH extensions (to parent domain) AND domain providers (for child MFEs). This enables deep nesting.

### 4. Decision Numbering (Sequential)

Fixed duplicate and non-sequential decision numbers:
- Decisions 1-9: type-system.md
- Decisions 10-12: mfe-loading.md
- Decisions 13-17: registry-runtime.md

### 5. Cross-Reference Accuracy

Fixed all mismatched references between files (e.g., "Decision 11" pointing to Decision 10 anchor).

### 6. Method Signature Consistency

Fixed `MfeBridgeFactory.create()` signature mismatch between proposal.md and mfe-loading.md.

### 7. Terminology Standardization

- Standardized "Instance-Level Isolation" terminology
- Standardized singleton behavior descriptions
- Consistent MFE/Microfrontend usage

### 8. New Documentation Files

- **glossary.md** - Key terms and definitions
- **schemas.md** - All JSON Schema definitions (split from type-system.md)
- **overview.md** - High-level architecture overview with diagrams

### 9. File Restructuring

- Merged `mfe-extension.md` into `mfe-domain.md` (related concepts)
- Added `specs/` directory with formal requirements

## Proposal Structure

```
proposal/
├── proposal.md          # Main proposal document
├── tasks.md             # Implementation tasks (21 phases)
├── design/              # Design documents (14 files)
│   ├── overview.md      # Architecture overview with diagrams
│   ├── glossary.md      # Key terms and definitions
│   ├── principles.md    # Design principles
│   ├── type-system.md   # TypeSystemPlugin and GTS
│   ├── schemas.md       # JSON Schema definitions
│   ├── mfe-domain.md    # Domain and Extension types
│   ├── mfe-entry-mf.md  # MfeEntry and MfeEntryMF types
│   ├── mfe-manifest.md  # MfManifest type
│   ├── mfe-loading.md   # Handler architecture and loading
│   ├── mfe-actions.md   # Action and ActionsChain types
│   ├── mfe-shared-property.md  # SharedProperty type
│   ├── mfe-api.md       # MfeEntryLifecycle and MfeBridge
│   ├── mfe-errors.md    # Error class hierarchy
│   └── registry-runtime.md  # Runtime isolation and registration
└── specs/               # Formal requirements
    ├── screensets/
    │   └── spec.md      # @hai3/screensets requirements
    └── microfrontends/
        └── spec.md      # @hai3/framework requirements
```

## Design Documents Summary

| Document | Description |
|----------|-------------|
| [overview.md](./proposal/design/overview.md) | High-level architecture with 6 diagrams |
| [glossary.md](./proposal/design/glossary.md) | 14 key terms with definitions |
| [principles.md](./proposal/design/principles.md) | Core design principles |
| [type-system.md](./proposal/design/type-system.md) | TypeSystemPlugin interface, GTS implementation |
| [schemas.md](./proposal/design/schemas.md) | 8 JSON Schema definitions |
| [mfe-domain.md](./proposal/design/mfe-domain.md) | Domain, Extension types, hierarchical composition |
| [mfe-entry-mf.md](./proposal/design/mfe-entry-mf.md) | MfeEntry (abstract) and MfeEntryMF (derived) |
| [mfe-manifest.md](./proposal/design/mfe-manifest.md) | Module Federation configuration |
| [mfe-loading.md](./proposal/design/mfe-loading.md) | MfeHandler abstraction, handler registry, loading |
| [mfe-actions.md](./proposal/design/mfe-actions.md) | Actions, ActionsChain, mediation |
| [mfe-shared-property.md](./proposal/design/mfe-shared-property.md) | Shared properties between host and MFEs |
| [mfe-api.md](./proposal/design/mfe-api.md) | MfeEntryLifecycle, MfeBridge, MfeBridgeConnection |
| [mfe-errors.md](./proposal/design/mfe-errors.md) | Error class hierarchy |
| [registry-runtime.md](./proposal/design/registry-runtime.md) | Instance isolation, dynamic registration |

## Decisions Index

| # | Decision | Document |
|---|----------|----------|
| 1 | Type System Plugin Interface | type-system.md |
| 2 | GTS Type ID Format | type-system.md |
| 3 | Internal TypeScript Type Definitions | type-system.md |
| 4 | HAI3 Type Registration | type-system.md |
| 5 | Vendor Type Registration | type-system.md |
| 6 | ScreensetsRegistry Configuration | type-system.md |
| 7 | Framework Plugin Model | type-system.md |
| 8 | Contract Matching Rules | type-system.md |
| 9 | Dynamic uiMeta Validation | type-system.md |
| 10 | MfeHandler Abstraction and Registry | mfe-loading.md |
| 11 | Module Federation 2.0 for Bundle Loading | mfe-loading.md |
| 12 | Manifest Fetching Strategy | mfe-loading.md |
| 13 | Instance-Level Isolation | registry-runtime.md |
| 14 | Framework-Agnostic Isolation Model | registry-runtime.md |
| 15 | Error Class Hierarchy | mfe-errors.md |
| 16 | Shadow DOM Utilities | registry-runtime.md |
| 17 | Dynamic Registration Model | registry-runtime.md |

## Responses to Iteration-2 Feedback

This section addresses feedback raised in iteration-2. Each response explains how the current proposal handles the concern.

| Feedback | Status | Response |
|----------|--------|----------|
| [Centralized Services](./comments/centralized-services.md) | **Addressed** | Custom `MfeBridgeFactory` allows injecting shared services for internal MFEs |
| [MFE Extensibility](./comments/mfe-extensibility.md) | **Partially Addressed** | Uses Bridge + React hooks pattern instead of `createMfe().use()` |
| [Missing Declarative Metadata](./comments/missing-declarative-metadata.md) | **Addressed** | GTS type extensibility allows extending `MfManifest` with custom metadata |
| [Missing Dev Workflow](./comments/missing-dev-workflow.md) | **Out of Scope** | Tooling docs to be created during implementation phase |
| [Missing System Extensibility](./comments/missing-system-extensibility.md) | **Addressed** | `MfeHandler` abstract class + `ScreensetsRegistry` events provide extension points |

### Summary

- **3 concerns fully addressed** through architectural changes (centralized services, declarative metadata, system extensibility)
- **1 concern addressed via alternative approach** (MFE extensibility uses hooks instead of plugins)
- **1 concern intentionally deferred** (dev workflow - implementation phase deliverable)

---

## Review Status

**Status:** APPROVED

The proposal has been reviewed for:
- Completeness
- Architecture quality
- SOLID compliance (all 5 principles pass)
- Consistency across all documents
- Cross-reference accuracy
- Best practices alignment

No blockers identified.
