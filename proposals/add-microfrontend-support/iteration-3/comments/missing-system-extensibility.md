# Response: Missing System Extensibility

## Status: Addressed

## Summary

The request for system extensibility (custom loading strategies, preloading, caching, lifecycle hooks) is now addressed through the **MfeHandler abstraction** and **ScreensetsRegistry events**.

## Response

### The Solution: MfeHandler Abstraction

The proposal now exposes `MfeHandler` as a public abstract class that companies can extend:

```typescript
// From mfe-loading.md - Decision 10

abstract class MfeHandler<TEntry extends MfeEntry = MfeEntry> {
  readonly handledBaseTypeId: string;
  readonly priority: number;
  abstract readonly bridgeFactory: MfeBridgeFactory;

  abstract load(entry: TEntry): Promise<MfeEntryLifecycle>;
  abstract preload(entries: TEntry[]): Promise<void>;
}
```

### What Can Be Extended

**1. Custom Loading Strategies**

```typescript
class MfeHandlerPriority extends MfeHandler<MfeEntryMF> {
  async load(entry: MfeEntryMF): Promise<MfeEntryLifecycle> {
    // Priority-based loading with queue management
    await this.priorityQueue.waitForSlot(entry.priority);
    return super.load(entry);
  }
}

class MfeHandlerRouteAware extends MfeHandler<MfeEntryMF> {
  async preload(entries: MfeEntryMF[]): Promise<void> {
    // Route-based preloading
    const currentRoute = this.router.currentRoute;
    const relevantEntries = entries.filter(e =>
      this.routeMatches(e.routes, currentRoute)
    );
    return super.preload(relevantEntries);
  }
}
```

**2. Custom Caching Strategies**

```typescript
class MfeHandlerWithCache extends MfeHandler<MfeEntryMF> {
  private cache = new Map<string, MfeEntryLifecycle>();

  async load(entry: MfeEntryMF): Promise<MfeEntryLifecycle> {
    if (this.cache.has(entry.id)) {
      return this.cache.get(entry.id)!;
    }
    const lifecycle = await super.load(entry);
    this.cache.set(entry.id, lifecycle);
    return lifecycle;
  }
}
```

**3. Custom Preloading Triggers**

```typescript
class MfeHandlerWithSmartPreload extends MfeHandler<MfeEntryMF> {
  async preload(entries: MfeEntryMF[]): Promise<void> {
    // Intersection Observer based preloading
    for (const entry of entries) {
      const container = document.querySelector(`[data-mfe="${entry.id}"]`);
      if (container) {
        this.observer.observe(container, () => super.preload([entry]));
      }
    }
  }
}
```

### Lifecycle Events via ScreensetsRegistry

The proposal also includes event-based extensibility through `ScreensetsRegistry`:

```typescript
// From registry-runtime.md - Decision 17

// ScreensetsRegistry emits events
registry.on('extensionRegistered', ({ extensionId }) => {
  // Custom logic when extension is registered
  analytics.track('mfe_registered', { extensionId });
});

registry.on('extensionUnregistered', ({ extensionId }) => {
  // Custom cleanup logic
  cache.invalidate(extensionId);
});

registry.on('domainRegistered', ({ domainId }) => {
  // Domain registration hook
});
```

### Framework Integration Hook

For framework-level hooks, the `microfrontends()` plugin integrates with HAI3's Flux pattern:

```typescript
// From specs/microfrontends/spec.md

// Effects subscribe to events and can add custom behavior
eventBus.on('mfe/mountRequested', async ({ extensionId }) => {
  // Pre-mount hook
  await analytics.trackMfeLoad(extensionId);

  // Actual mount
  await runtime.mountExtension(extensionId, container);

  // Post-mount hook
  performanceMonitor.recordMountTime(extensionId);
});
```

### Comparison to Suggested Plugin System

| Suggested Approach | Proposal's Approach |
|-------------------|---------------------|
| `ctx.hook('mfe:load', handler)` | `MfeHandler.load()` override |
| `ctx.hook('mfe:preload', handler)` | `MfeHandler.preload()` override |
| `ctx.publicApi.getMfeManifest()` | `manifestFetcher.fetch()` |
| `ctx.publicApi.preloadAsset()` | Custom `MfeHandler.preload()` |

The proposal's approach uses **class inheritance** (MfeHandler) rather than **hook-based plugins**. This provides:
- Strong typing for the extension points
- Clear contract via abstract methods
- Priority-based handler selection
- Full control over loading behavior

### Related Proposal Sections

- [mfe-loading.md - Decision 10: MfeHandler Abstraction and Registry](../proposal/design/mfe-loading.md)
- [registry-runtime.md - Decision 17: Dynamic Registration Model](../proposal/design/registry-runtime.md)
- [specs/microfrontends/spec.md - Effects](../proposal/specs/microfrontends/spec.md)

## Conclusion

The feedback is addressed through:
1. **MfeHandler abstract class** - extensible loading and preloading
2. **MfeBridgeFactory abstract class** - extensible bridge creation
3. **ScreensetsRegistry events** - lifecycle hooks for registration/unregistration
4. **Flux effects** - framework-level integration hooks

The proposal uses class-based extension points rather than hook-based plugins, providing strong typing and clear contracts for customization.
