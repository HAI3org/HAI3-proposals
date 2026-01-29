# Change: Introduce Unified Hooks System for All Extension Points

## Why

The HAI3 system currently has multiple extension points scattered across different subsystems. Even when the underlying approach is similar (e.g., class inheritance), each extension point has its own API that developers need to learn. Additionally, each extension point implements its own error handling, ordering, and lifecycle management, leading to inconsistent behavior across the system.

This proposal introduces a **new hooks system** to HAI3 that provides a unified API for all extension points. The initial idea is inspired by [unjs/hookable](https://github.com/unjs/hookable), but that implementation lacks certain features like synchronous hook calls (`callHookSync`). The proposed system extends this concept and offers:

- **Multiple calling strategies**: `callHook` (async-sequence), `callHookParallel` (async-parallel), `callHookSync` (sync-sequence)
- **Proper subscribe/unsubscribe**: `hook()` returns unsubscribe function
- **One-time hooks**: `hookOnce()` for hooks that fire only once
- **Hook ordering**: FIFO by default, with support for priority-based ordering
- **Cross-cutting concerns**: `beforeEach()` / `afterEach()` for logging, error handling, etc.
- **Deprecation support**: `deprecateHook()` for graceful migrations
- **Batch registration**: `addHooks()` for registering multiple hooks at once
- **Type safety**: Full TypeScript support with generic hook definitions

## What Changes

### Problem: Scattered Extension Points Across the System

#### 1. Custom Loading/Caching/Preloading Strategies (Class Inheritance)

```typescript
// Current: extend MfeHandler class and override methods
class MfeHandlerCustom extends MfeHandler<MfeEntryMF> {
  private cache = new Map<string, MfeEntryLifecycle>();

  // Custom loading with caching
  async load(entry: MfeEntryMF): Promise<MfeEntryLifecycle> {
    if (this.cache.has(entry.id)) {
      return this.cache.get(entry.id)!;
    }
    await this.priorityQueue.waitForSlot(entry.priority);
    const lifecycle = await super.load(entry);
    this.cache.set(entry.id, lifecycle);
    return lifecycle;
  }

  // Custom preloading with route filtering
  async preload(entries: MfeEntryMF[]): Promise<void> {
    const currentRoute = this.router.currentRoute;
    const relevantEntries = entries.filter(e =>
      this.routeMatches(e.routes, currentRoute)
    );
    return super.preload(relevantEntries);
  }
}
```

#### 2. Extensibility via Custom Bridge Factories (Class Inheritance)

```typescript
// Current: extend MfeBridgeFactory class
class MfeBridgeFactoryAcme extends MfeBridgeFactory<MfeBridgeAcme> {
  create(domainId, entryTypeId, instanceId): MfeBridgeAcme {
    return new MfeBridgeAcme(
      domainId, entryTypeId, instanceId,
      this.localization,
      this.analytics,
      this.theming
    );
  }
}
```

#### 3. Lifecycle Events via ScreensetsRegistry (Event Emitter Pattern)

```typescript
// Current: event-based extensibility
registry.on('extensionRegistered', ({ extensionId }) => {
  analytics.track('mfe_registered', { extensionId });
});

registry.on('extensionUnregistered', ({ extensionId }) => {
  cache.invalidate(extensionId);
});
```

#### 4. Passing `onRequest` for ApiPlugin (Class-Based Plugin)

```typescript
// Current: class-based plugin with lifecycle methods
class AuthPlugin extends ApiPlugin<{ getToken: () => string | null }> {
  onRequest(ctx: ApiRequestContext) {
    const token = this.config.getToken();
    if (!token) return ctx;
    return {
      ...ctx,
      headers: { ...ctx.headers, Authorization: `Bearer ${token}` }
    };
  }
}
```

#### 5. Framework Integration Hook (Flux Effects Pattern)

```typescript
// Current: effects subscribe to events via eventBus
eventBus.on('mfe/mountRequested', async ({ extensionId }) => {
  // Pre-mount hook
  await analytics.trackMfeLoad(extensionId);

  // Actual mount
  await runtime.mountExtension(extensionId, container);

  // Post-mount hook
  performanceMonitor.recordMountTime(extensionId);
});
```

### Solution: Introduce Unified Hooks System

We propose introducing a new `@hai3/hooks` package (or adding to `@hai3/state`) that provides a `createHooked()` factory function. All extension points would then use the same hook-based API.

#### Proposed Hooks System API

```typescript
// packages/hooks/src/hooked.ts (or packages/state/src/hooked.ts)

export interface Hooked<THooks extends Record<string, any>> {
  /**
   * Register a hook callback for a specific event.
   * Returns an unsubscribe function.
   */
  hook<K extends keyof THooks>(name: K, fn: THooks[K]): () => void;

  /**
   * Register a hook that fires only once.
   */
  hookOnce<K extends keyof THooks>(name: K, fn: THooks[K]): () => void;

  /**
   * Remove a specific hook callback.
   */
  removeHook<K extends keyof THooks>(name: K, fn: THooks[K]): void;

  /**
   * Register multiple hooks at once. Returns cleanup function.
   */
  addHooks(hooks: Partial<THooks>): () => void;

  /**
   * Remove all hooks for all events.
   */
  removeAllHooks(): void;

  /**
   * Mark a hook as deprecated with migration path.
   */
  deprecateHook<K extends keyof THooks>(
    name: K,
    options: { to?: keyof THooks; message?: string }
  ): void;

  /**
   * Call hooks sequentially (async). Each hook awaits before next.
   * Returns array of all hook return values.
   */
  callHook<K extends keyof THooks>(
    name: K,
    ...args: Parameters<THooks[K]>
  ): Promise<ReturnType<THooks[K]>[]>;

  /**
   * Call hooks in parallel (async). All hooks run concurrently.
   * Returns array of all hook return values.
   */
  callHookParallel<K extends keyof THooks>(
    name: K,
    ...args: Parameters<THooks[K]>
  ): Promise<ReturnType<THooks[K]>[]>;

  /**
   * Call hooks synchronously in sequence.
   * Returns array of all hook return values.
   */
  callHookSync<K extends keyof THooks>(
    name: K,
    ...args: Parameters<THooks[K]>
  ): ReturnType<THooks[K]>[];

  /**
   * Register a callback that runs before every hook execution.
   */
  beforeEach(fn: (event: HookEvent<THooks>) => void): () => void;

  /**
   * Register a callback that runs after every hook execution.
   */
  afterEach(fn: (event: HookEvent<THooks>) => void): () => void;
}

export interface HookEvent<THooks> {
  name: keyof THooks;
  args: unknown[];
  context: Record<string, unknown>;
  error?: Error;
}

/**
 * Create a new hooked instance with type-safe hook definitions.
 */
export function createHooked<THooks extends Record<string, any>>(): Hooked<THooks>;
```

### Using the Hooks System in HAI3

#### MFE Hooks (Demonstration)

```typescript
// Example hooks for MFE system - for demonstration purposes only
// Actual hooks would be defined based on real extension point requirements
interface MfeHooks {
  // Loading lifecycle
  'mfe:beforeLoad': (entry: MfeEntry) => MfeEntry | void;
  'mfe:afterLoad': (entry: MfeEntry, lifecycle: MfeEntryLifecycle) => void;
  'mfe:loadError': (entry: MfeEntry, error: Error) => void;

  // Mounting lifecycle
  'mfe:beforeMount': (extension: Extension, container: HTMLElement) => void;
  'mfe:afterMount': (extension: Extension, bridge: MfeBridge) => void;
  'mfe:beforeUnmount': (extensionId: string) => void;
  'mfe:afterUnmount': (extensionId: string) => void;

  // Bridge lifecycle
  'mfe:bridgeCreate': (domainId: string, entryTypeId: string) => MfeBridge | void;
  'mfe:bridgeDispose': (bridge: MfeBridge) => void;

  // Domain lifecycle
  'mfe:domainRegistered': (domain: ExtensionDomain) => void;
  'mfe:domainUnregistered': (domainId: string) => void;

  // Extension lifecycle
  'mfe:extensionRegistered': (extension: Extension) => void;
  'mfe:extensionUnregistered': (extensionId: string) => void;

  // Preloading
  'mfe:preload': (entries: MfeEntry[]) => MfeEntry[];

  // Property updates
  'mfe:propertyUpdate': (domainId: string, propertyTypeId: string, value: unknown) => unknown;
}

const mfeHooks = createHooked<MfeHooks>();

// Consumers can augment the interface to add custom hooks
declare module '@hai3/hooks' {
  interface MfeHooks {
    'mfe:customHook': (data: CustomData) => void;
  }
}
```

#### API Hooks

```typescript
interface ApiHooks {
  'api:beforeRequest': (ctx: ApiRequestContext) => ApiRequestContext | ShortCircuitResponse;
  'api:afterResponse': (ctx: ApiResponseContext, req: ApiRequestContext) => ApiResponseContext;
  'api:onError': (error: Error, req: ApiRequestContext) => Error | ApiResponseContext;
}

const apiHooks = createHooked<ApiHooks>();
```

#### Usage Examples

```typescript
// Custom loading with caching (replaces class inheritance)
mfeHooks.hook('mfe:afterLoad', (entry, lifecycle) => {
  cache.set(entry.id, lifecycle);
});

mfeHooks.hook('mfe:beforeLoad', (entry) => {
  const cached = cache.get(entry.id);
  if (cached) return cached; // Short-circuit loading
});

// Custom preloading (replaces class inheritance)
mfeHooks.hook('mfe:preload', (entries) => {
  const currentRoute = router.currentRoute;
  return entries.filter(e => routeMatches(e.routes, currentRoute));
});

// Analytics tracking (replaces event emitter pattern)
mfeHooks.hook('mfe:extensionRegistered', ({ extension }) => {
  analytics.track('mfe_registered', { extensionId: extension.id });
});

// Custom bridge factory (replaces class inheritance)
mfeHooks.hook('mfe:bridgeCreate', (domainId, entryTypeId) => {
  return new MfeBridgeAcme(domainId, entryTypeId, localization, analytics);
});

// Auth plugin (replaces class-based plugin)
apiHooks.hook('api:beforeRequest', (ctx) => {
  const token = getToken();
  if (!token) return ctx;
  return {
    ...ctx,
    headers: { ...ctx.headers, Authorization: `Bearer ${token}` }
  };
});

// Metrics plugin
apiHooks.hook('api:afterResponse', (ctx, req) => {
  metrics.recordLatency(req.url, Date.now() - req.startTime);
  return ctx;
});
```

### Benefits

#### 1. Consistent API Everywhere

Instead of learning multiple extension point APIs scattered across the system, developers learn ONE unified hooks API that works everywhere.

#### 2. Centralized Hook Execution Strategies

All calling strategies are implemented ONCE in `createHooked()`:

```typescript
// Sync sequential - for validation chains
const results = hooks.callHookSync('mfe:beforeLoad', entry);

// Async sequential - for ordered async operations
const results = await hooks.callHook('mfe:afterLoad', entry, lifecycle);

// Async parallel - for independent async operations
const results = await hooks.callHookParallel('mfe:preload', entries);
```

#### 3. Proper Error Handling in One Place

```typescript
hooks.beforeEach((event) => {
  logger.debug(`Hook ${event.name} starting`, event.args);
});

hooks.afterEach((event) => {
  if (event.error) {
    errorReporter.capture(event.error, { hook: event.name });
  }
});
```

#### 4. Built-in Subscribe/Unsubscribe

```typescript
// Register hook and get cleanup function
const unsubscribe = hooks.hook('mfe:afterLoad', handler);

// Later, when component unmounts or feature is disabled
unsubscribe();
```

#### 5. Hook Ordering

```typescript
// Hooks execute in registration order (FIFO) by default
hooks.hook('mfe:beforeLoad', validateEntry);    // Runs first
hooks.hook('mfe:beforeLoad', transformEntry);   // Runs second
hooks.hook('mfe:beforeLoad', logEntry);         // Runs third

// Priority-based ordering can be added via options
hooks.hook('mfe:beforeLoad', criticalValidation, { priority: 100 });  // Runs first (highest priority)
hooks.hook('mfe:beforeLoad', logging, { priority: -100 });            // Runs last (lowest priority)
```

The system can be extended to support priority-based ordering, allowing hooks to be inserted at specific positions in the execution chain.

#### 6. Graceful Deprecation

```typescript
// Old hook name still works but warns developers
hooks.deprecateHook('mfe:onLoad', { to: 'mfe:afterLoad' });
```

#### 7. Batch Registration for Plugins

```typescript
// Register all hooks for a plugin at once
const unregisterAll = hooks.addHooks({
  'mfe:beforeLoad': validateEntry,
  'mfe:afterLoad': cacheEntry,
  'mfe:loadError': reportError,
});

// Clean up all hooks at once
unregisterAll();
```

### Comparison Table

| Concern | Current (Mixed) | Proposed (Hooks) |
|---------|----------------------|------------------|
| Learning curve | Multiple extension points | 1 unified API |
| Error handling | Implemented per-pattern | Centralized in `createHooked()` |
| Subscribe/unsubscribe | Inconsistent APIs | Built-in, always returns cleanup fn |
| Ordering | Class priority / undefined | Registration order (FIFO), priority can be added |
| Async strategies | Varies per-pattern | `callHook`, `callHookParallel`, `callHookSync` |
| Type safety | Varies | Consistent with generics |
| Testing | Mock classes / complex setup | Simple function mocks |
| Deprecation | Manual per-pattern | Built-in `deprecateHook()` |

### Common Extension Points Base

The hooks system can act as a unified extension points base for the entire HAI3 ecosystem. Plugins can register their own hooks while keeping the same `app.hook()` API:

```typescript
// Base HAI3 app provides core hooks
const app = createHAI3().build();
app.hook('hai3:beforeInit', () => { /* ... */ });
app.hook('hai3:afterInit', () => { /* ... */ });

// Adding microfrontends plugin extends available hooks
const app = createHAI3()
  .use(microfrontends())
  .build();

// Same API, but now microfrontends hooks are available
app.hook('mfe:beforeLoad', (entry) => { /* ... */ });
app.hook('mfe:afterMount', (extension, bridge) => { /* ... */ });

// Adding more plugins extends hooks further
const app = createHAI3()
  .use(microfrontends())
  .use(analytics())
  .build();

app.hook('analytics:trackEvent', (event) => { /* ... */ });
```

This approach allows:
- **Consistent API**: All extension points use `app.hook()` regardless of which plugin provides them
- **Discoverability**: TypeScript autocompletion shows available hooks based on installed plugins
- **Extensibility**: Third-party plugins can add their own hooks using the same pattern

### Decoupled Domain Modules

With class inheritance (e.g., Custom Bridge Factories), all concerns must be combined in one place:

```typescript
// Tightly coupled: localization, analytics, theming all in one class
class MfeBridgeFactoryAcme extends MfeBridgeFactory<MfeBridgeAcme> {
  create(domainId, entryTypeId, instanceId): MfeBridgeAcme {
    return new MfeBridgeAcme(
      domainId, entryTypeId, instanceId,
      this.localization,  // Localization concern
      this.analytics,     // Analytics concern
      this.theming        // Theming concern
    );
  }
}
```

With hooks, each domain module can extend different parts of the system while keeping its code collocated:

```typescript
// localization/module.ts - all localization logic in one place
mfeHooks.hook('mfe:bridgeCreate', () => ({
  localization: {
    t: (key: string) => i18n.translate(key),
    locale: () => i18n.currentLocale,
  },
}));

// analytics/module.ts - all analytics logic in one place
mfeHooks.hook('mfe:bridgeCreate', () => ({
  analytics: {
    track: (event: string) => analytics.track(event),
  },
}));
mfeHooks.hook('mfe:afterMount', (extension) => {
  analytics.track('mfe_mounted', { id: extension.id });
});

// theming/module.ts - all theming logic in one place
mfeHooks.hook('mfe:bridgeCreate', () => ({
  theming: {
    current: themeManager.current,
    apply: (theme: string) => themeManager.apply(theme),
  },
}));
mfeHooks.hook('mfe:propertyUpdate', (domainId, propertyTypeId, value) => {
  if (propertyTypeId === 'theme') themeManager.apply(value);
});

// Bridge creation combines all hook results
const results = await mfeHooks.callHook('mfe:bridgeCreate', domainId, entryTypeId);
const bridge = Object.assign({}, ...results, { builtInMethod });
```

This allows:
- **Separation of concerns**: Each module handles its own domain completely
- **Collocated code**: All analytics logic is in one place, all theming logic in another
- **Independent development**: Teams can work on separate modules without conflicts
- **Easy testing**: Each module can be tested in isolation

### Internal Usage for Higher-Level APIs

The hooks system can be used internally to power higher-level APIs where other patterns (like passing objects or class-based plugins) are more acceptable for the public interface. This allows different API styles to coexist while sharing the same underlying infrastructure:

```typescript
// ApiPlugin class-based pattern uses hooks internally
abstract class ApiPlugin<TConfig = void> {
  constructor(protected readonly config: TConfig) {}

  // Public class-based API
  onRequest?(ctx: ApiRequestContext): ApiRequestContext | void;
  onResponse?(ctx: ApiResponseContext): ApiResponseContext | void;
}

// Internally, the system registers plugin methods as hooks
function registerPlugin(plugin: ApiPlugin) {
  if (plugin.onRequest) {
    apiHooks.hook('api:beforeRequest', plugin.onRequest.bind(plugin));
  }
  if (plugin.onResponse) {
    apiHooks.hook('api:afterResponse', plugin.onResponse.bind(plugin));
  }
}
```

This approach provides:
- **Flexibility**: Different public APIs for different use cases
- **Consistency**: All extension points share the same underlying hook execution, error handling, and ordering
- **Simplicity**: Complex patterns (class inheritance, plugin objects) can be offered where they make sense, while simple hooks are available for straightforward cases
