# Response: Unified Hooks System Proposal

## Acknowledgment

The Unified Hooks System proposal presents a well-designed, consistent API for extension points. The `createHooked<THooks>()` pattern offers genuine advantages:

- **Unified API** - One pattern to learn for all extension points
- **Subscribe/unsubscribe** - Clean lifecycle management with cleanup functions
- **Cross-cutting concerns** - `beforeEach()` / `afterEach()` for logging and error handling
- **Graceful deprecation** - Built-in migration path for evolving APIs
- **Type safety** - Generic hook definitions with TypeScript support

These are valuable features. However, for the MFE system specifically, we've chosen a different approach based on **forced explicitness** - abstract methods that clients must implement completely. This response explains the reasoning.

---

## Why Forced Explicitness Matters

### The Core Trade-off

The hooks proposal optimizes for **distributed flexibility** - different modules can subscribe to the same hook from different locations. The current MFE API optimizes for **forced explicitness** - clients must explicitly implement the complete interface.

For systems where **complete and correct implementations matter**, forced explicit contracts are more valuable than optional hook subscriptions.

### Problem: Proving a Negative

Consider understanding whether preload behavior is customized:

#### With Abstract Classes (Explicit)

```typescript
// MfeHandlerAcme.ts - Open this file, see everything
class MfeHandlerAcme extends MfeHandler<MfeEntryMF> {
  async load(entry: MfeEntryMF): Promise<MfeEntryLifecycle> {
    // Custom implementation - VISIBLE
    return this.customLoader.load(entry);
  }

  async preload(entries: MfeEntryMF[]): Promise<void> {
    // MUST be here - abstract methods require implementation
    // Empty body = explicitly "do nothing"
    // Custom logic = explicitly "do this"
  }
}
```

**Question:** Is preload customized?
**Answer:** Open file, find `preload` method (it MUST exist), read the body. Done.

#### With Hooks (Implicit)

```typescript
// mfe-caching/module.ts
mfeHooks.hook('mfe:beforeLoad', (entry) => {
  if (cache.has(entry.id)) return cache.get(entry.id);
});

// analytics/module.ts
mfeHooks.hook('mfe:afterLoad', (entry, lifecycle) => {
  analytics.track('mfe_loaded', { id: entry.id });
});

// Is preload customized? Search the entire codebase...
```

**Question:** Is preload customized?
**Answer:** Search for `'mfe:preload'` across all files. Found nothing? Maybe it's default. Maybe you missed a dynamically registered hook. Maybe it's registered conditionally at runtime.

### The "Forced Explicitness" Principle

Abstract methods **MUST be implemented**. There's no implicit default - clients are forced to explicitly declare how they implement the full interface:

```typescript
abstract class MfeHandler<TEntry extends MfeEntry> {
  abstract load(entry: TEntry): Promise<MfeEntryLifecycle>;
  abstract preload(entries: TEntry[]): Promise<void>;
}

// Client MUST implement both - compiler enforces this
class MfeHandlerAcme extends MfeHandler<MfeEntryMF> {
  async load(entry: MfeEntryMF): Promise<MfeEntryLifecycle> {
    return this.customLoader.load(entry);  // Custom logic
  }

  async preload(entries: MfeEntryMF[]): Promise<void> {
    // Even a no-op must be explicit
    // This tells the reader: "preload intentionally does nothing"
  }
}
```

With hooks, you can only see what IS registered. Everything else is implicit - you must prove a negative across the entire codebase.

| Concern | Abstract Classes | Hooks |
|---------|------------------|-------|
| Full interface implementation | **Required** - compiler enforces | Optional - register what you want |
| See complete contract | One file | Search codebase |
| Explicit "do nothing" | ✓ Empty method body | Not expressible |
| Reason about behavior | Complete picture | Uncertainty |
| New team member onboarding | "Open this class" | "Search for these hooks" |

---

## SOLID Principles Comparison

The hooks proposal suggests it improves SOLID compliance. Let's examine each principle:

### S - Single Responsibility Principle

> "A class should have only one reason to change."

**Both approaches can comply.** SRP depends on implementation discipline, not the pattern.

With abstract classes, companies can use composition:
```typescript
class MfeHandlerAcme extends MfeHandler {
  constructor(
    private cache: CacheService,      // Separate responsibility
    private analytics: AnalyticsService // Separate responsibility
  ) {}
}
```

With hooks, each handler can be a single function. But handlers can also combine concerns.

**Verdict: Tie** - Neither forces good or bad separation.

### O - Open/Closed Principle

> "Software entities should be open for extension, closed for modification."

**Both comply equally.**

- Abstract classes: Open for extension (subclass), closed for modification
- Hooks: Open for extension (register), closed for modification

**Verdict: Tie**

### L - Liskov Substitution Principle

> "Subtypes must be substitutable for their base types."

**Abstract classes provide stronger enforcement.**

```typescript
// Abstract class - TypeScript enforces contract at compile time
abstract class MfeHandler<TEntry extends MfeEntry> {
  abstract load(entry: TEntry): Promise<MfeEntryLifecycle>;
  abstract preload(entries: TEntry[]): Promise<void>;
}

// Subclass MUST implement ALL abstract methods with correct signatures
// Won't compile otherwise - no way to "forget" part of the contract
class MfeHandlerAcme extends MfeHandler<MfeEntryMF> {
  // ERROR if load() is missing - compiler enforces completeness
  // ERROR if return type is wrong - compiler enforces correctness
}
```

```typescript
// Hooks - weaker enforcement
hooks.hook('mfe:beforeLoad', (entry) => {
  return { wrong: 'type' };  // May not be caught until runtime
});

// Nothing forces you to register all hooks
// Nothing forces correct return types
// Multiple hooks return values collected into array - caller handles mixed types
```

**Verdict: Abstract Classes** - Compiler enforces complete and correct contract implementation.

### I - Interface Segregation Principle

> "Clients should not be forced to depend on interfaces they don't use."

**The methods ARE used.** The `ScreensetsRegistry` uses both `load()` and `preload()` methods. ISP is not violated - the registry uses all methods it depends on.

The actual advantage of abstract classes here is **forced explicit implementation**:

```typescript
// Client MUST implement the full interface - no implicit behavior
// Even "do nothing" must be written explicitly
class MfeHandlerAcme extends MfeHandler<MfeEntryMF> {
  async load(entry) { /* must be here */ }
  async preload(entries) { /* must be here - even if empty */ }
}
```

With hooks, you can register some hooks and not others. There's no way to express "I've considered all extension points and here's my complete implementation."

**Verdict: Abstract Classes** - Forces clients to explicitly implement the full interface.

### D - Dependency Inversion Principle

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."

**Both can comply, but abstract classes make dependencies more explicit.**

```typescript
// Current - dependencies visible at construction
class ScreensetsRegistry {
  constructor(
    private typeSystem: TypeSystemPlugin,     // Visible abstraction
    private bridgeFactory: MfeBridgeFactory,  // Visible abstraction
  ) {}
}
```

```typescript
// With hooks - dependencies are implicit
class ScreensetsRegistry {
  constructor(private hooks: Hooked<MfeHooks>) {}

  async loadEntry(entry: MfeEntry) {
    // What hooks are registered? Not visible at construction time
    await this.hooks.callHook('mfe:beforeLoad', entry);
  }
}
```

**Verdict: Abstract Classes** - Dependencies are explicit in constructor.

### Summary

| Principle | Abstract Classes | Hooks | Verdict |
|-----------|------------------|-------|---------|
| **S** - Single Responsibility | Implementation choice | Implementation choice | **Tie** |
| **O** - Open/Closed | Both comply | Both comply | **Tie** |
| **L** - Liskov Substitution | Compiler-enforced | Convention-based | **Abstract Classes** |
| **I** - Interface Segregation | N/A - both comply | N/A - both comply | **Tie** |
| **D** - Dependency Inversion | Explicit abstractions | Hook system | **Abstract Classes** |

---

## The MFE Proposal Already Allows Hooks

A key insight: **The MFE proposal defines abstract contracts, not implementation mandates.**

Companies are free to use hooks internally within their handler/factory implementations:

```typescript
// Company CHOOSES to use hooks internally - the MFE proposal allows this!
class MfeBridgeFactoryAcme extends MfeBridgeFactory<MfeBridgeAcme> {
  private hooks = createHooked<AcmeBridgeHooks>();

  constructor() {
    // Different teams register their enrichments
    this.hooks.hook('bridge:enrich', localizationModule.enrichBridge);
    this.hooks.hook('bridge:enrich', analyticsModule.enrichBridge);
    this.hooks.hook('bridge:enrich', themingModule.enrichBridge);
  }

  create(domainId: string, entryTypeId: string, instanceId: string): MfeBridgeAcme {
    const base = new MfeBridgeAcme(domainId, entryTypeId, instanceId);
    const enrichments = this.hooks.callHookSync('bridge:enrich', base);
    return Object.assign(base, ...enrichments);
  }

  dispose(bridge: MfeBridgeAcme): void {
    this.hooks.callHookSync('bridge:dispose', bridge);
  }
}
```

The MFE proposal provides the **abstraction** (what). Companies provide the **implementation** (how). Nothing prevents using hooks as the implementation strategy.

---

## Why Different Patterns Were Chosen

The MFE proposal uses different patterns deliberately, based on requirements:

### MfeHandler - Abstract Class

**Why:** Priority-based selection requires a registry pattern.

```typescript
abstract class MfeHandler<TEntry extends MfeEntry> {
  abstract readonly priority: number;
  abstract canHandle(entry: MfeEntry): entry is TEntry;
  abstract load(entry: TEntry): Promise<MfeEntryLifecycle>;
}
```

Handlers compete by priority - the registry selects the highest-priority handler that can handle each entry. This is a **selection** problem, not a **notification** problem. Hooks don't fit.

### MfeBridgeFactory - Abstract Class

**Why:** Generic return type enforces type safety.

```typescript
abstract class MfeBridgeFactory<TBridge extends MfeBridge> {
  abstract create(...): TBridge;  // Return type is explicit and typed
}
```

With hooks:
```typescript
const results = hooks.callHook('mfe:bridgeCreate', ...);
const bridge = Object.assign({}, ...results);  // Type is `{}` - lost!
```

### ScreensetsRegistry Events - Event Emitter

**Why:** Observation shouldn't affect lifecycle.

```typescript
registry.on('extensionRegistered', ({ extensionId }) => {
  analytics.track('mfe_registered', { extensionId });
});
```

These are **notifications** - observers watch but don't modify behavior. Event emitters are the correct pattern for observation.

---

## Pattern Choice Summary

| Extension Point | Pattern | Why Not Hooks? |
|-----------------|---------|----------------|
| `MfeHandler` | Abstract class | Priority-based selection needs registry |
| `MfeBridgeFactory` | Abstract class | Generic return type enforces type safety |
| `ScreensetsRegistry` events | Event emitter | Observation shouldn't affect lifecycle |

---

## Decoupled Domain Modules Revisited

The hooks proposal shows this example:

```typescript
// localization/module.ts
mfeHooks.hook('mfe:bridgeCreate', () => ({
  localization: { t: (key) => i18n.translate(key) }
}));

// analytics/module.ts
mfeHooks.hook('mfe:bridgeCreate', () => ({
  analytics: { track: (event) => analytics.track(event) }
}));
```

This IS achievable with the current proposal. Companies use composition inside their factory:

```typescript
class MfeBridgeFactoryAcme extends MfeBridgeFactory<MfeBridgeAcme> {
  constructor(
    private localizationModule: LocalizationModule,
    private analyticsModule: AnalyticsModule,
    private themingModule: ThemingModule,
  ) {}

  create(domainId, entryTypeId, instanceId): MfeBridgeAcme {
    return new MfeBridgeAcme(
      domainId, entryTypeId, instanceId,
      // Each module is separate - just injected via DI
      this.localizationModule.createBridgeExtension(),
      this.analyticsModule.createBridgeExtension(),
      this.themingModule.createBridgeExtension(),
    );
  }
}
```

The difference:
- **Hooks:** Modules register themselves, factory doesn't know what's included, nothing enforces completeness
- **Abstract class + DI:** Factory MUST implement `create()`, explicitly declares dependencies, compiler enforces the contract

For a system where **complete and correct implementations matter**, forced explicit contracts are more valuable than implicit hook aggregation.

---

## Recommendation

### For the MFE Proposal

**No changes needed.** The architecture prioritizes forced explicitness, which is the correct choice for a complicated system like MFE where:

- Multiple teams will implement handlers
- Understanding complete behavior is critical for debugging
- New team members need to onboard quickly
- Compile-time contract enforcement prevents runtime surprises

### For the Hooks Request

**Not a HAI3 concern.** None of HAI3's base approaches would use hooks - the framework deliberately chooses explicit contracts at all abstraction boundaries.

Companies that prefer hooks internally can bring their own library (e.g., [unjs/hookable](https://github.com/unjs/hookable)):

```typescript
// Company brings their own hooks library
import { createHooks } from 'hookable';

// Use it inside their implementation if they prefer
class MfeBridgeFactoryAcme extends MfeBridgeFactory {
  private hooks = createHooks<AcmeBridgeHooks>();
  // ...
}
```

HAI3 provides the **abstraction boundary** (what to implement). Companies choose their **internal patterns** (how to implement). If a company wants hooks internally, they're free to use any hooks library - it's an implementation detail invisible to HAI3

---

## Summary

| Question | Answer |
|----------|--------|
| Is the hooks system a good idea? | **Yes** - valuable utility for many use cases |
| Does MFE proposal allow hooks? | **Yes** - companies can use hooks internally |
| Should MFE mandate hooks at the abstraction boundary? | **No** - forced explicitness is more valuable |
| Are the pattern choices correct? | **Yes** - each serves a specific architectural need |
| Should HAI3 provide a hooks package? | **No** - HAI3's base approaches don't use hooks |
| Does MFE proposal need changes? | **No** |

---

## Closing Thought

The hooks system is a valuable pattern for the right problems. HAI3 deliberately chooses abstract classes at its abstraction boundaries because **forced explicitness** is the priority for a framework that multiple companies will build upon.

Abstract methods **must** be implemented. There's no implicit behavior, no "forgot to register a hook", no uncertainty about what a client does or doesn't handle. Every implementation explicitly declares its complete behavior - even "do nothing" must be written.

Companies implementing HAI3's abstractions are free to use hooks, DI, composition, or any other pattern internally - that's an implementation detail invisible to the framework. HAI3 provides the **what** (abstract contracts that must be fully implemented). Companies choose the **how** (implementation patterns).

For a framework where multiple teams will implement handlers and factories, where understanding complete behavior is critical for debugging, and where the compiler should catch incomplete implementations - forced explicit contracts are more valuable than optional hook subscriptions.
