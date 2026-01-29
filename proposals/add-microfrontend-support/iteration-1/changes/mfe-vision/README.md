# HAI3 Architectural Vision

This document responds to the [vision](../../feedback/add-microfrontend-support/vision/README.md) presented in the feedback and articulates HAI3's architectural philosophy for micro-frontend integration.

## Core Philosophy: Independence Over Integration

HAI3 takes a fundamentally different approach from traditional micro-frontend architectures. While the feedback's vision describes a **centralized service model** ("Federation owns implementation, Fragments follow interface"), HAI3 implements a **distributed independence model** with thin public contracts.

## The Two Models Compared

### Feedback's Model: Centralized Services

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST (FEDERATION)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Shared Services (single instances)                  │   │
│  │  - API Service                                       │   │
│  │  - Router                                            │   │
│  │  - State Manager                                     │   │
│  │  - Localization                                      │   │
│  │  - Feature Flags                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│              ┌────────────┼────────────┐                   │
│              │            │            │                   │
│              ▼            ▼            ▼                   │
│         ┌────────┐   ┌────────┐   ┌────────┐              │
│         │Fragment│   │Fragment│   │Fragment│              │
│         │   A    │   │   B    │   │   C    │              │
│         │        │   │        │   │        │              │
│         │(uses   │   │(uses   │   │(uses   │              │
│         │ host   │   │ host   │   │ host   │              │
│         │services)   │services)   │services)              │
│         └────────┘   └────────┘   └────────┘              │
└─────────────────────────────────────────────────────────────┘

Fragments depend on host providing specific service implementations.
```

### HAI3's Model: Independent MFEs with Thin Contracts

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST APPLICATION                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Thin Public Contracts Only:                         │   │
│  │  - MfeEntryLifecycle (mount/unmount)                 │   │
│  │  - MfeBridge (communication)                         │   │
│  │  - Actions (events)                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│              ┌────────────┼────────────┐                   │
│              │            │            │                   │
│              ▼            ▼            ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │     MFE A    │ │     MFE B    │ │     MFE C    │       │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │       │
│  │ │Own API   │ │ │ │Own API   │ │ │ │Own API   │ │       │
│  │ │Own Router│ │ │ │Own Router│ │ │ │Own Router│ │       │
│  │ │Own State │ │ │ │Own State │ │ │ │Own State │ │       │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘

Each MFE is self-contained. The host only knows about lifecycle and actions.
```

## Why Independence?

HAI3 is designed for a **multi-vendor ecosystem**. The requirements differ fundamentally from a single-organization micro-frontend architecture:

| Scenario | Feedback's Model | HAI3's Model |
|----------|-----------------|--------------|
| Single organization, consistent tooling | Ideal | Works |
| Multiple vendors, different tech stacks | Fragile | Ideal |
| Independent deployment schedules | Requires coordination | Truly independent |
| MFE developed by external team | Must learn host services | Standard web development |
| Security isolation between MFEs | Shared state risks | Strong isolation |

## Table of Contents

| Document | Description |
|----------|-------------|
| [Principles](./principles.md) | Core design principles: thin contracts, private optimization, framework agnosticism |

## Response to Feedback's Principles

See [principles.md](./principles.md) for a detailed response to the feedback's architectural principles.
