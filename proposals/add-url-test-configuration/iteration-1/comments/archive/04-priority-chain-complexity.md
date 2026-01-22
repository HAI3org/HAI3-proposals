# Feedback: Mock Priority Chain Complexity

## Issue

The proposal defines an 8-level priority chain for mock resolution:

1. Per-endpoint runtime overrides (`TestScenarioController.setResponse`)
2. Active test scenario responses
3. MockController enabled/disabled state
4. URL parameters (`?mock=`, `?real=`)
5. localStorage preferences
6. TypeScript mock functions
7. JSON mock files
8. Pass-through to real API

## Industry Comparison

Every major mocking framework uses **2-3 conceptual levels**, not 8:

| Framework | Priority Model | Levels |
|-----------|---------------|--------|
| [MSW](https://mswjs.io/docs/best-practices/network-behavior-overrides/) | Registration order + `.use()` overrides | 2-3 |
| [Playwright](https://playwright.dev/docs/mock) | Reverse registration (last wins) | 2-3 |
| [Cypress](https://docs.cypress.io/api/commands/intercept) | Recent first + propagation control | 2-3 |
| [Mirage JS](https://www.smashingmagazine.com/2020/06/mirage-javascript-timing-response-passthrough/) | Handlers first, passthrough last | 2 |
| [WireMock](https://wiremock.org/docs/stubbing/) | Numeric priority (1=highest, 5=default) | 2-3 |
| **Proposal** | 8-level chain with multiple dimensions | **8** |

### Industry Standard Pattern

```
┌─────────────────────────────────────┐
│  1. Specific/Runtime Overrides      │  ← Highest priority
│     - Test-specific handlers        │
│     - MSW .use(), Cypress latest    │
├─────────────────────────────────────┤
│  2. Default/Initial Handlers        │  ← Base mock configuration
│     - Registered at setup           │
│     - General mock responses        │
├─────────────────────────────────────┤
│  3. Passthrough                     │  ← Lowest priority
│     - Real API calls                │
└─────────────────────────────────────┘
```

### What Industry Leaders Say

**MSW**: "Runtime handlers added via `.use()` prepend to the list, taking priority. Order is left-to-right."

**Playwright**: "When several routes match, they run in reverse registration order. Last registered can always override previous ones."

**WireMock**: "Higher priority (lower number) matched first. Default priority is 5. Use catch-all stubs at low priority."

**Mirage JS**: "Put all passthrough config at the bottom of your routes, to give your route handlers precedence."

## Proposal vs Industry Analysis

| Proposal Level | Industry Equivalent | Assessment |
|----------------|---------------------|------------|
| 1. Per-endpoint overrides | Runtime override | ✓ Keep |
| 2. Active scenario | Default handlers | ✓ Keep |
| 3. MockController state | N/A | ✗ Merge with scenario |
| 4. URL parameters | N/A | ✗ Controls scenario, not separate level |
| 5. localStorage | N/A | ✗ Controls scenario, not separate level |
| 6. TypeScript mocks | Default handlers | ✗ Unify with JSON at registration |
| 7. JSON mocks | Default handlers | ✗ Unify with TS at registration |
| 8. Passthrough | Passthrough | ✓ Keep |

## Concerns

### Redundant Levels

Several levels express the same concept differently:

| Levels | Overlap |
|--------|---------|
| 3, 4, 5 | Three ways to say "which endpoints are mocked" |
| 6, 7 | Two mock data sources that should be unified at registration |
| 1, 2 | Both are "scenario" concepts |

### Debugging Difficulty

When a request returns unexpected data, developer must check 8 places to understand why. Industry standard is 2-3 places.

### Specification Ambiguity

The spec doesn't clarify edge cases:
- What if URL says `?mock=sessions` but localStorage says `sessions` is disabled?
- What if TypeScript mock exists but JSON mock has different data?
- What if scenario activates endpoint but MockController disabled it?

No major framework has these ambiguities because they don't create overlapping control mechanisms.

## Recommendation

Align with industry standard - **3 levels**:

```
1. Runtime Overrides (highest priority)
   - Per-endpoint overrides via setEndpointOverride action
   - Test-specific modifications during execution

2. Active Scenario (base configuration)
   - URL activates scenario: /_test/{screen}/{scenario}
   - Scenario defines complete mock config
   - TS + JSON unified at registration time, not resolution time
   - URL params (?mock=endpoint) modify scenario, not separate level
   - localStorage persists scenario choice, not separate level

3. Passthrough (lowest priority)
   - No matching mock → real API
```

### URL Params and localStorage

These should be **scenario selectors**, not resolution levels:

```
/_test/chat/empty              → Activate "empty" scenario
/_test/chat/empty?persist=true → Activate + save to localStorage
/_test/chat/custom?only=sessions,messages → Scenario with endpoint filter
```

### TS and JSON Mock Unification

Unify at **registration time**, not resolution time:

```typescript
// During service initialization
const mockPlugin = new TestScenarioPlugin({
  scenarios: {
    'empty': loadScenario('empty'),  // Merges TS + JSON internally
  }
});

// loadScenario unifies:
// - JSON from src/screensets/chat/mocks/empty.json
// - TS overrides from src/screensets/chat/mocks/empty.ts (if exists)
// Result: single unified scenario definition
```

## Required Changes

1. **Reduce priority chain** from 8 to 3 levels (matches industry standard)
2. **Unify JSON and TS mocks** at registration time, not resolution time
3. **Reclassify URL params** as scenario modifiers, not separate priority level
4. **Reclassify localStorage** as persistence mechanism, not priority level
5. **Remove MockController state** as separate level - scenario activation handles this
6. **Document clear precedence** with examples showing the 3-level model
7. **Add debug logging** to show which level resolved the mock (like MSW does)
