# MFE System Design Overview

This document provides a high-level overview of the Microfrontend (MFE) system architecture.

---

## What is the MFE System?

The MFE system allows independent UI components (microfrontends) to be loaded into a host application at runtime. Each MFE is developed, deployed, and versioned independently, but they all work together within the host.

**Key Benefits:**
- Teams can develop and deploy independently
- MFEs can use different frameworks (React, Vue, Svelte, etc.)
- Components are isolated - one MFE cannot break another
- New features can be added without redeploying the host

---

## Core Concepts

```
┌────────────────────────────────────────────────────────────────┐
│                       HOST APPLICATION                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      DOMAIN (Slot)                       │  │
│  │                                                          │  │
│  │  "Where MFEs can mount"                                  │  │
│  │  - Provides shared properties (user, theme, etc.)        │  │
│  │  - Defines supported action types (contract)             │  │
│  │                                                          │  │
│  │  ┌─────────────────┐  ┌─────────────────┐                │  │
│  │  │   EXTENSION A   │  │   EXTENSION B   │                │  │
│  │  │                 │  │                 │                │  │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │                │  │
│  │  │  │    MFE    │  │  │  │    MFE    │  │                │  │
│  │  │  │  (React)  │  │  │  │   (Vue)   │  │                │  │
│  │  │  └───────────┘  │  │  └───────────┘  │                │  │
│  │  └─────────────────┘  └─────────────────┘                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### The Three Main Types

| Type | What it is | Analogy |
|------|-----------|---------|
| [**Domain**](./design/mfe-domain.md) | A slot where MFEs can be placed | A power outlet |
| [**Entry**](./design/mfe-entry-mf.md) | The MFE's contract (what it needs and provides) | A plug specification |
| [**Extension**](./design/mfe-extension.md) | The actual MFE instance mounted in a domain | A plugged-in device |

---

## How MFEs Communicate

MFEs don't talk directly to each other. Each MFE has its own **Bridge** to the host. All communication goes through the host.

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│    MFE A    │      │     HOST     │      │    MFE B    │
│             │      │              │      │             │
│             │◀─────│──(properties)│─────▶│             │
│             │      │              │      │             │
│  (request)  │─────▶│              │◀─────│  (request)  │
│             │◀─────│(chains both  │─────▶│             │
│             │      │    ways)     │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
    Bridge A                                  Bridge B
     (own)                                     (own)
```

### Two Communication Mechanisms

1. **[Shared Properties](./design/mfe-shared-property.md)** - One-way: host → MFEs
   - User context, theme, selected items
   - MFEs subscribe and react to changes

2. **[Actions Chains](./design/mfe-actions.md)** - Bidirectional: routed to targets
   - ActionsChains are sent to targets (domains or extensions)
   - ActionsChainsMediator routes chains to targets based on `action.target`
   - Action types in contracts define what targets can send/receive; ActionsChains are the messages

---

## How MFEs are Loaded

MFEs are loaded on-demand using [Module Federation](./design/mfe-loading.md). The host doesn't bundle MFE code - it fetches it at runtime.

```
┌─────────────────┐         ┌─────────────────┐
│   HOST APP      │         │   CDN / Server  │
│                 │         │                 │
│  "Load chart    │  HTTP   │  ┌───────────┐  │
│   widget"       │────────▶│  │ Chart MFE │  │
│                 │         │  │  Bundle   │  │
│                 │◀────────│  └───────────┘  │
│  ┌───────────┐  │         │                 │
│  │ Chart MFE │  │         │  ┌───────────┐  │
│  │ (loaded)  │  │         │  │ Table MFE │  │
│  └───────────┘  │         │  │  Bundle   │  │
│                 │         │  └───────────┘  │
└─────────────────┘         └─────────────────┘
```

The [MfManifest](./design/mfe-manifest.md) tells the loader where to find the MFE bundle and what dependencies it shares with the host.

---

## Runtime Isolation

Each MFE runs in isolation. This means:

- **Separate state** - MFE A cannot access MFE B's React state
- **Separate styles** - CSS from one MFE doesn't leak to another (Shadow DOM)
- **Separate errors** - If MFE A crashes, MFE B keeps working

```
┌──────────────────────────────────────────────┐
│                    HOST                      │
│                                              │
│  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Shadow DOM       │  │ Shadow DOM       │  │
│  │ ┌──────────────┐ │  │ ┌──────────────┐ │  │
│  │ │   MFE A      │ │  │ │   MFE B      │ │  │
│  │ │              │ │  │ │              │ │  │
│  │ │ Own React    │ │  │ │ Own Vue      │ │  │
│  │ │ Own styles   │ │  │ │ Own styles   │ │  │
│  │ │ Own state    │ │  │ │ Own state    │ │  │
│  │ └──────────────┘ │  │ └──────────────┘ │  │
│  └──────────────────┘  └──────────────────┘  │
│                                              │
└──────────────────────────────────────────────┘
```

---

## MFE Lifecycle

```
    ┌─────────┐
    │ DEFINE  │  Developer creates MfeEntry (contract)
    └────┬────┘  and MfManifest (loading config)
         │
         ▼
    ┌─────────┐
    │ REGISTER│  Host registers Extension (binds entry to domain)
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  LOAD   │  Bundle fetched via Module Federation
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  MOUNT  │  MFE's mount() called with container and bridge
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  RUN    │  MFE renders UI, subscribes to properties,
    └────┬────┘  communicates via actions chains
         │
         ▼
    ┌─────────┐
    │ UNMOUNT │  MFE's unmount() called, cleanup performed
    └─────────┘
```

See [MFE API](./design/mfe-api.md) for the mount/unmount interface that MFEs must implement.

---

## Error Handling

When things go wrong, the system provides [specific error types](./design/mfe-errors.md):

| Error | When it happens |
|-------|-----------------|
| `MfeLoadError` | Bundle failed to load (network, 404, etc.) |
| `ContractValidationError` | MFE doesn't match domain's requirements |
| `ChainExecutionError` | Action chain failed during execution |
| `UnsupportedDomainActionError` | Action not supported by target domain |

---

## Design Documents

For detailed specifications, see:

| Document | Description |
|----------|-------------|
| [mfe-domain.md](./design/mfe-domain.md) | Extension domains (slots for MFEs) |
| [mfe-entry-mf.md](./design/mfe-entry-mf.md) | MFE entry contracts |
| [mfe-extension.md](./design/mfe-extension.md) | Extensions (MFE instances) |
| [mfe-manifest.md](./design/mfe-manifest.md) | Module Federation configuration |
| [mfe-loading.md](./design/mfe-loading.md) | Bundle loading and isolation |
| [mfe-actions.md](./design/mfe-actions.md) | Action types and actions chains |
| [mfe-shared-property.md](./design/mfe-shared-property.md) | Shared properties |
| [mfe-api.md](./design/mfe-api.md) | MFE lifecycle and bridge interfaces |
| [mfe-errors.md](./design/mfe-errors.md) | Error class hierarchy |
| [type-system.md](./design/type-system.md) | GTS type system and validation |
| [registry-runtime.md](./design/registry-runtime.md) | Runtime isolation and registration |
| [principles.md](./design/principles.md) | Design principles |
