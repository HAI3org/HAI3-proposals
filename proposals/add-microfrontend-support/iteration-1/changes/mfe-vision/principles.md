# HAI3 Architectural Principles

This document responds to the [feedback's principles](../../feedback/add-microfrontend-support/vision/principles.md) and articulates HAI3's design decisions.

---

## Response to: "Federation owns implementation, Fragments follow interface"

**Feedback's Principle:**
> Federation exists as a single instance in the root application and owns all core implementations. Fragments (which can have multiple instances) do not implement their own services but instead consume the interfaces provided by Federation. This ensures consistency across all Fragments and follows the principle of one service per concern.

**HAI3's Counter-Principle: MFEs Own Their Implementation, Contracts Are Thin**

HAI3 deliberately inverts this relationship. MFEs do not consume services from the host. Each MFE is a fully independent application with its own:

- API client (axios, fetch, or any library)
- Router (React Router, Vue Router, or framework equivalent)
- State management (Redux, Zustand, Pinia, or none)
- Localization
- Any other services it needs

The host provides only **thin public contracts**:

```typescript
// The ONLY interface MFEs must implement
interface MfeEntryLifecycle {
  mount(container: HTMLElement, props: unknown): void;
  unmount(container: HTMLElement): void;
}

// The ONLY communication mechanism
interface MfeBridge {
  dispatch(action: Action): void;
  subscribe(handler: ActionHandler): Subscription;
  getSharedProperty<T>(key: string): T | undefined;
}
```

### Why This Matters

**1. Lower Coupling**

In the feedback's model, if the host's API service changes behavior (error handling, retry logic, caching), every Fragment is affected. MFEs are implicitly coupled to host implementation details.

In HAI3's model, MFEs control their own service versions. Host changes cannot silently break MFEs.

**2. No Diamond Dependency Problem**

```
Feedback's model with version conflicts:
  Host provides API Service v2.0
  Fragment A needs v2.1 features
  Fragment B works only with v1.9
  → Conflict: who wins?

HAI3's model:
  MFE A uses its own API v2.1
  MFE B uses its own API v1.9
  Host doesn't care
  → No conflict
```

**3. True Independence**

An MFE developed by an external vendor doesn't need to understand or integrate with the host's service architecture. It's just a web application that implements `mount()` and `unmount()`.

---

## Response to: "One service per concern"

**Feedback's Principle:**
> There is one service for backend requests, one for localization, one for feature flags, one for routing, and so on.

**HAI3's Counter-Principle: Each MFE Owns Its Concerns**

The "one service per concern" pattern optimizes for consistency and efficiency within a single organization. HAI3 optimizes for independence and isolation across a multi-vendor ecosystem.

### The Trade-off and How We Handle It

**Downside**: Multiple MFEs may make duplicate API requests for the same data.

**Solution**: Private optimization at the library layer, not the contract layer.

```
┌─────────────────────────────────────────────────────────────┐
│                 MFE CODE (unchanged, simple)                │
│  const data = await api.fetch('/users/123');               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              @hai3/api LIBRARY (handles optimization)       │
│  - Each MFE has its own instance                            │
│  - Instances sync cache transparently under the hood        │
│  - Request deduplication across MFE boundaries              │
│  - MFE doesn't know or care about this                      │
└─────────────────────────────────────────────────────────────┘
```

**Key insight**: MFEs can use axios, fetch, or any HTTP client. The system still works, just without cache optimization. This is **opt-in optimization**, not **mandatory coupling**.

---

## Principle: Framework Agnosticism Through Independence

**Feedback's Approach:**
> Framework-specific adapters are created as separate packages to bridge the gap between the framework-agnostic core and the actual UI framework being used.

**HAI3's Approach: No Adapters Needed**

Because MFEs own their implementation, they use their framework's native patterns directly. There's no need for adapter layers that translate between a framework-agnostic core and React/Vue/Angular.

- A React MFE uses React hooks, React Router, React state
- A Vue MFE uses Vue composables, Vue Router, Pinia
- They both implement the same thin lifecycle interface

The framework agnosticism is at the contract level (lifecycle + actions), not at the service level.

---

## Principle: Security Through Isolation

Each MFE operates in isolation:

- Separate credential scopes
- No shared authentication state
- Shadow DOM prevents CSS leakage
- Module Federation's `singleton: false` for runtime isolation

If one MFE is compromised, the blast radius is limited to that MFE's scope.

In a shared service model, a vulnerability in the shared API service affects all Fragments.

---

## When the Feedback's Model Is Better

The feedback's "Federation owns implementation" model is better suited for:

- **Single-organization MFEs** with consistent tooling and governance
- **Performance-critical applications** where memory efficiency is paramount
- **Centralized service management** with lockstep upgrades
- **Teams that share release cycles** and coordinate deployments

---

## When HAI3's Model Is Better

HAI3's "thin contracts + private optimization" model is better suited for:

- **Multi-vendor ecosystems** with third-party MFE developers
- **Framework heterogeneity** (React, Vue, Angular, Svelte coexisting)
- **Independent deployment** schedules across organizational boundaries
- **Security isolation** requirements between MFE boundaries
- **Standard web development** patterns (npm install, standard testing, no host knowledge required)

---

## Summary

| Principle | Feedback's Vision | HAI3's Vision |
|-----------|-------------------|---------------|
| Service ownership | Host owns, MFEs consume | MFEs own, host doesn't know |
| Optimization | At the contract level | At the library level (private) |
| Coupling | Implicit (service interfaces) | Explicit (lifecycle + actions only) |
| Framework integration | Adapters translate core to framework | Each MFE uses framework natively |
| Target scenario | Single organization | Multi-vendor ecosystem |
