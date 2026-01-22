# Feedback: Data Flow Architecture

## Issue

The proposal introduces `TestDataInitializer` that populates store directly, bypassing the API layer.

## HAI3 Data Flow

Normal data flow in HAI3:

```
Component calls service method
    ↓
Service executes via protocol (REST/SSE)
    ↓
Protocol plugins intercept (including mock plugins)
    ↓
Response returned (real or mocked)
    ↓
Service emits event via eventBus
    ↓
Effect listens to event
    ↓
Effect dispatches to store
    ↓
Component re-renders via selector
```

## Proposal's Approach

From tasks.md:
- Task 3.8: `TestDataInitializer` component for store state population
- Task 6.3: `initializeCyberChatTestData()` for store state initialization

This creates a parallel data path:

```
TestDataInitializer
    ↓
Dispatch directly to store (bypasses API)
    ↓
Component re-renders
```

## Why This Is Problematic

1. **Effects don't fire** - Effects that listen to API events won't trigger
2. **Side effects skipped** - Analytics, logging, caching tied to API events won't run
3. **Different code paths** - Test data takes different path than production data
4. **Behavior divergence** - Tests may pass but production fails (or vice versa)

## Example

```typescript
// Normal flow
class SessionsService {
  async loadSessions() {
    const sessions = await this.protocol.get('/sessions');
    eventBus.emit('sessions/loaded', sessions);  // Effects react to this
    return sessions;
  }
}

// Effect listens
eventBus.on('sessions/loaded', (sessions) => {
  dispatch(setSessions(sessions));
  analytics.track('sessions_loaded', { count: sessions.length });  // Side effect
});

// TestDataInitializer bypasses all of this
dispatch(setSessions(testData));  // No event, no analytics, no effects
```

## Recommendation

Test data should flow through the **same path** as production data:

```typescript
// Correct: Mock at API level
const testPlugin = new TestScenarioPlugin({
  scenarios: {
    'empty': {
      'GET /api/sessions': () => []
    },
    'many-sessions': {
      'GET /api/sessions': () => generateSessions(100)
    }
  }
});

// Then normal flow works:
// 1. Component calls sessionsService.loadSessions()
// 2. Mock plugin intercepts, returns test data
// 3. Service emits 'sessions/loaded' event
// 4. Effects fire (analytics, etc.)
// 5. store updated via normal dispatch
// 6. Component re-renders
```

The URL test config should **activate mock scenarios**, not inject data directly.

## State Management Clarification

### What Goes in testingSlice

```typescript
interface TestingState {
  activeScenarios: string[];                          // Which scenarios are active
  endpointOverrides: Record<string, EndpointOverride>; // Runtime overrides
}
```

### What Does NOT Go in State

| Data | Where It Belongs | Why |
|------|------------------|-----|
| Scenario definitions | Registry (static) | Loaded at init, doesn't change |
| Mock response templates | JSON/TS files | Configuration, not runtime state |
| Generated mock data | Plugin memory | Created per-request by faker |
| Application data | Normal app slices | Flows through API → effects |

### URL as Primary Activation

```
/_test/chat/empty → activateScenario('empty') → testingSlice updated
```

On refresh, URL is reparsed. No localStorage required for core functionality.

localStorage is an optional "remember preferences" enhancement, not core infrastructure.

## Required Changes

1. **Remove** `TestDataInitializer` component from proposal
2. **Remove** `initializeCyberChatTestData()` and similar functions
3. Test scenarios should define mock responses at API level
4. Components should call normal service methods
5. Mock plugins return test data through normal flow
6. Document that test mode activates scenarios, doesn't inject state
7. **testingSlice is minimal** - only active scenarios and overrides
8. **URL is primary activation** - localStorage is optional enhancement
