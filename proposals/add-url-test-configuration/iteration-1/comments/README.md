# Iteration 1 Review

## Status: BLOCK

The proposal has good foundations but requires changes to align with HAI3 architecture.

---

## Critical

### Remove TestDataInitializer

The proposal includes `TestDataInitializer` that populates state directly, bypassing the API layer.

**Problem:** Effects don't fire, side effects are skipped, test code paths diverge from production.

**Fix:** Remove `TestDataInitializer` and `initializeCyberChatTestData()`. Scenarios define mock responses at the API level. Components call normal service methods.

---

## High Priority

### 1. URL Format

**Proposal:** `/{screen}/_test/{scenario}`

**Change to:** `/_test/{screen}/{scenario}`

**Why:** HAI3 framework controls the first path segment. Screens control subsequent segments. Prefix format keeps test routing as framework concern.

---

### 2. MockController → Event-Driven Actions

**Proposal:** Imperative `MockController` class with methods like `enable()`, `disable()`.

**Change to:** Event-driven actions following HAI3's Flux pattern:

```typescript
// Actions emit events
function activateScenario(scenarioId: string): void {
  eventBus.emit(TestingEvents.ScenarioActivated, { scenarioId });
}

// Effects listen and update state
eventBus.on(TestingEvents.ScenarioActivated, ({ scenarioId }) => {
  store.dispatch(addActiveScenario(scenarioId));
});
```

**State shape:**
```typescript
interface TestingState {
  activeScenarios: string[];
  endpointOverrides: Record<string, EndpointOverride>;
}
```

---

### 3. Add testing() Plugin

**Not in proposal.** Add a separate `testing()` framework plugin.

| Plugin | Responsibility |
|--------|----------------|
| `mock()` | Infrastructure - toggle fake data on/off |
| `testing()` | Configuration - scenarios, URL routing, per-endpoint control |

```typescript
createHAI3()
  .use(mock())
  .use(testing())  // depends on mock
  .build();
```

**Why:** Different responsibilities. Industry standard pattern. Allows mock-only usage.

---

### 4. Clarify Package Distribution

**Proposal:** Places components in `@hai3/api` but doesn't specify full distribution.

**Clarify:**

| Layer | Components |
|-------|------------|
| `@hai3/api` (L1) | TestScenarioRestPlugin, TestScenarioPresets, MockDataLoader, FakerProcessor |
| `@hai3/framework` (L2) | testing() plugin, testingSlice, testingEffects, URL utilities |
| `@hai3/react` (L3) | useTestConfig() hook (if needed), re-exports |
| `@hai3/studio` | TestingPanel component |

---

### 5. State Management

**Proposal:** localStorage as primary for MockController preferences.

**Change to:**
- **URL** is primary activation mechanism (`/_test/{screen}/{scenario}`)
- **State slice** holds current config
- **localStorage** is optional "remember preferences" feature

On refresh, URL is reparsed. No persistence required for core functionality.

---

## Medium Priority

### 6. Resolve Priority Chain Inconsistency

**Proposal has internal inconsistency:**
- "Layered Scenario Resolution" decision: **3 tiers**
- "Mock Priority Chain" decision: **8 levels**

**Recommendation:** Go with 3 tiers consistently (matches industry standard):

```
1. Runtime Overrides (highest)  - setEndpointOverride()
2. Active Scenario              - from URL
3. Passthrough (lowest)         - Real API
```

URL params and localStorage are scenario selectors, not separate priority levels.

---

## Low Priority

### 7. Protocol-Agnostic Schema

**Proposal:** JSON schema is REST-specific at root (`"endpoint": "GET /path"`).

**Change to:** Protocol sections for future extensibility:

```json
{ "id": "empty", "rest": { "GET /api/sessions": {...} } }
```

Rename `TestScenarioPlugin` → `TestScenarioRestPlugin`.

Add Non-Goal: "Not mocking SSE/WebSocket in V1".

---

## What's Good (No Changes Needed)

- Plugin-based approach extending existing infrastructure
- JSON mock files for human-readable data
- Development-only guards (`import.meta.env.DEV`)
- Vertical slice ownership (`src/screensets/{name}/mocks/`)
- Faker templates for dynamic data
- 3-tier priority concept (just needs to be applied consistently)

---

## Summary

| Item | Proposal | Change To |
|------|----------|-----------|
| Data flow | TestDataInitializer | Mock at API level |
| URL format | `/{screen}/_test/...` | `/_test/{screen}/...` |
| MockController | Imperative class | Event-driven actions |
| testing() plugin | Not present | Add separate plugin |
| Package distribution | Unclear | Specify L1/L2/L3 |
| State/persistence | localStorage primary | URL primary |
| Priority levels | 3 and 8 (inconsistent) | 3 consistently |
| JSON schema | REST-specific root | Protocol sections |

---

## Next Steps

Address critical and high-priority items, then resubmit for iteration-2 review.
