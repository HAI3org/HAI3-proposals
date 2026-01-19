# Response: Missing Declarative Metadata

## Status: Design Choice

## Summary

The feedback suggests MFEs should declare their dependencies (API services, routers, state managers) in a manifest so the host can provide optimized shared instances. We intentionally chose a different approach: thin public contracts with optional private optimization libraries.

## The Two Approaches

### Feedback's Suggestion: Declarative Metadata
```
MFE Manifest declares:
  - needs: ApiService v2.3
  - needs: Router v1.0
  - needs: StateManager v3.1
      ↓
Host provides shared instances
      ↓
Optimization through explicit sharing
```

### Our Approach: Thin Contracts + Private Optimization
```
MFE is fully independent:
  - Has own API client
  - Has own router
  - Has own state
      ↓
Libraries handle optimization privately
      ↓
MFE doesn't know about other MFEs
```

## Why We Chose Thin Contracts

### 1. Lower Coupling
- MFEs don't depend on host providing specific service implementations
- Host changes can't silently break MFEs
- Each MFE controls its own service versions

### 2. Easier Versioning
- No "diamond dependency problem" (Host has v2.0, MFE-A wants v2.1, MFE-B wants v1.9)
- MFEs upgrade independently without host coordination
- Simpler compatibility testing (each MFE tests in isolation)

### 3. Better Developer Experience
- Standard web development patterns (npm install, standard testing)
- No need to understand host's service architecture
- MFE is self-contained and locally testable

### 4. Framework Agnosticism
- Each MFE uses its framework's native patterns
- No framework-specific shared services
- Aligns with HAI3's multi-framework support (React, Vue, Angular, Svelte)

### 5. Security Isolation
- Each MFE has isolated credentials
- No shared authentication state leakage
- Limited blast radius if one MFE is compromised

## The Trade-off

**Downside**: Multiple MFEs requesting the same API data will make duplicate requests.

**Solution**: Private optimization layer at the library level, not public contract changes.

```
┌─────────────────────────────────────────────────────────────────┐
│                 MFE CODE (unchanged, simple)                    │
│  const data = await api.fetch('/users/123');                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              @hai3/api LIBRARY (handles optimization)           │
│  - Each MFE has own instance                                    │
│  - Instances sync cache transparently under the hood            │
│  - Request deduplication across MFE boundaries                  │
│  - MFE doesn't know or care about this                          │
└─────────────────────────────────────────────────────────────────┘
```

## Why Not Add Cache Keys to Public Contract?

This would defeat the thin contracts principle. If optimization requires MFE-level declarations, we're back to tight coupling. The optimization must remain at the library level to preserve MFE independence.

## Clarifications on Trade-offs

### Memory Overhead
The concern about duplicate instances is about **runtime memory**, not **bundle size**. Module Federation 2.0 handles bundle sharing at load time - code isn't duplicated on disk/network. Only runtime instances are duplicated in memory.

### Cache Invalidation Complexity
Cache invalidation would be equally complex for a singleton service approach. It's not additional complexity unique to the independent approach - it's a universal caching challenge.

### Opt-in Optimization
MFEs can use axios instead of `@hai3/api` - the system still works, just without cache optimization. This is intentional: graceful degradation over mandatory coupling.

## When Declarative Metadata Would Be Better

The feedback's approach suits different scenarios:
- Single-organization MFEs with consistent tooling
- Performance-critical applications where memory efficiency is paramount
- Centralized service management with lockstep upgrades

HAI3's goals are different:
- Multi-vendor ecosystem with third-party MFE developers
- Framework heterogeneity
- Independent deployment
- Security isolation

## Conclusion

This is an intentional design choice aligned with HAI3's goals of vendor extensibility, framework agnosticism, and independent deployment. Optimization happens at the library layer (private, evolvable) rather than the contract layer (public, coupled).

See **Decision 21: MFE Independence with Thin Public Contracts** in the proposal's `design/registry-runtime.md` for the full specification.
