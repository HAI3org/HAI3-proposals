# Feedback: Event-Driven Architecture Compliance

## Issue

The proposed `MockController` uses imperative methods that bypass HAI3's event-driven Flux architecture.

## HAI3 Pattern

All state changes flow through the event bus:

```
Action (function)
    ↓
eventBus.emit('domain/event', payload)
    ↓
Effect (listens to event)
    ↓
dispatch(reducer(payload))
    ↓
Store state updated
```

**Example** - existing `toggleMockMode`:

```typescript
// Action emits event
function toggleMockMode(enabled: boolean): void {
  eventBus.emit('mock/toggle', { enabled });
}

// Effect listens and coordinates
eventBus.on('mock/toggle', ({ enabled }) => {
  // Iterate services, add/remove plugins
});
```

## Proposal's Approach

`MockController` exposes imperative methods:

```typescript
interface MockController {
  enable(endpoint: string): void;
  disable(endpoint: string): void;
  enableAll(): void;
  disableAll(): void;
  isEnabled(endpoint: string): boolean;
  getState(): MockControllerState;
  reset(): void;
}
```

These methods suggest direct state mutation, not event emission.

## Concerns

1. **Bypasses event bus** - Other parts of the system can't react to mock state changes
2. **No audit trail** - Events provide natural logging/debugging; imperative calls don't
3. **Inconsistent pattern** - Rest of HAI3 uses events; this introduces different pattern
4. **Testing difficulty** - Harder to test event flow when actions are imperative

## Recommendation

Convert `MockController` to event-driven pattern:

```typescript
// Actions (emit events)
function enableMockEndpoint(endpoint: string): void {
  eventBus.emit('mock/endpoint/enable', { endpoint });
}

function disableMockEndpoint(endpoint: string): void {
  eventBus.emit('mock/endpoint/disable', { endpoint });
}

function setMockEndpoints(config: MockEndpointConfig): void {
  eventBus.emit('mock/endpoints/configure', config);
}

// Effects (listen and update state)
eventBus.on('mock/endpoint/enable', ({ endpoint }) => {
  dispatch(setEndpointMockState({ endpoint, enabled: true }));
  // Update plugin state
});

// State access via selectors, not controller methods
const mockState = useAppSelector(state => state.mock.endpoints);
```

## Layer Distribution Analysis

The testing/scenario functionality should have footprints across multiple layers, following the established mock infrastructure pattern.

### Pattern Reference: Existing Mock Infrastructure

| Component | Package | Layer |
|-----------|---------|-------|
| `RestMockPlugin` | `@hai3/api` | L1 |
| `SseMockPlugin` | `@hai3/api` | L1 |
| `MOCK_PLUGIN` symbol | `@hai3/api` | L1 |
| `isMockPlugin()` guard | `@hai3/api` | L1 |
| `mock()` plugin | `@hai3/framework` | L2 |
| `mockSlice` | `@hai3/framework` | L2 |
| `mockEffects` | `@hai3/framework` | L2 |
| `toggleMockMode()` action | `@hai3/framework` | L2 |
| `ApiModeToggle` component | `@hai3/studio` | UI |

### Proposed Testing Infrastructure Distribution

```
┌─────────────────────────────────────────────────────────────────────┐
│  @hai3/studio (UI)                                                   │
│  ├── TestingPanel.tsx        - Scenario selector, endpoint toggles  │
│  └── Uses actions from @hai3/react, state via useAppSelector        │
├─────────────────────────────────────────────────────────────────────┤
│  @hai3/react (L3)                                                    │
│  ├── useTestConfig()         - React hook (if needed)               │
│  └── Re-exports everything from @hai3/framework                     │
├─────────────────────────────────────────────────────────────────────┤
│  @hai3/framework (L2)                                                │
│  ├── testing() plugin        - Plugin factory                       │
│  ├── testingSlice            - Active scenarios, overrides state    │
│  ├── testingEffects          - Event listeners and coordination     │
│  ├── testingEvents           - Event type definitions               │
│  ├── Actions                 - activateScenario, setEndpointOverride│
│  └── URL utilities           - isTestRoute, parseTestUrl, buildTestUrl│
├─────────────────────────────────────────────────────────────────────┤
│  @hai3/api (L1)                                                      │
│  ├── TestScenarioPlugin      - Extends RestPluginWithConfig         │
│  ├── TestScenarioPresets     - SERVER_ERROR, SLOW_NETWORK, etc.     │
│  ├── MockDataLoader          - JSON mock file loading               │
│  ├── FakerProcessor          - {{faker.*}} template processing      │
│  └── Types                   - TestScenario, TestScenarioResponse   │
└─────────────────────────────────────────────────────────────────────┘
```

### Detailed Component Placement

#### @hai3/api (L1) - Protocol Level

**Why here:** Zero @hai3 dependencies. Protocol plugins intercept requests at the lowest level.

```typescript
// packages/api/src/testing/TestScenarioPlugin.ts
export class TestScenarioPlugin extends RestPluginWithConfig<TestScenarioConfig> {
  static readonly [MOCK_PLUGIN] = true;  // Mark as mock plugin

  async onRequest(ctx: RestRequestContext): Promise<RestRequestContext | RestShortCircuitResponse> {
    const scenario = this.config.getActiveScenario?.();
    if (!scenario) return ctx;

    const mockResponse = this.resolveResponse(ctx, scenario);
    if (mockResponse) {
      return new RestShortCircuitResponse(mockResponse);
    }
    return ctx;
  }
}

// packages/api/src/testing/TestScenarioPresets.ts
export const TestScenarioPresets = {
  SERVER_ERROR: { status: 500, delay: 0 },
  SLOW_NETWORK: { delay: 3000 },
  EMPTY_RESPONSE: { data: null },
  // ...
} as const;

// packages/api/src/mocks/MockDataLoader.ts
export class MockDataLoader {
  async load(path: string): Promise<unknown> { /* ... */ }
}

// packages/api/src/mocks/FakerProcessor.ts
export class FakerProcessor {
  process(template: string): unknown { /* ... */ }
}
```

#### @hai3/framework (L2) - Application Level

**Why here:** Owns plugin architecture, effects system, and state management coordination.

```typescript
// packages/framework/src/plugins/testing.ts
export function testing(config?: TestingPluginConfig): HAI3Plugin {
  return {
    name: 'testing',
    dependencies: ['mock', 'routing'],
    provides: {
      slices: [testingSlice],
      effects: [initTestingEffects],
      actions: {
        activateScenario,
        deactivateScenario,
        setEndpointOverride,
        clearEndpointOverride,
        resetScenarios,
      },
    },
    onInit(app) {
      if (!isDevEnvironment()) return;
      if (config?.autoActivateFromUrl !== false && isTestRoute()) {
        const urlConfig = parseTestUrl(window.location.pathname);
        toggleMockMode(true);
        activateScenario(urlConfig.scenario);
      }
    },
  };
}

// packages/framework/src/slices/testingSlice.ts
export const testingSlice = createSlice({
  name: 'testing',
  initialState: {
    activeScenarios: [] as string[],
    endpointOverrides: {} as Record<string, TestScenarioResponse>,
  },
  reducers: {
    setActiveScenarios,
    addEndpointOverride,
    removeEndpointOverride,
    reset,
  },
});

// packages/framework/src/effects/testingEffects.ts
export function initTestingEffects(): () => void {
  const store = getStore();

  const sub1 = eventBus.on(TestingEvents.ScenarioActivated, ({ scenarioId }) => {
    store.dispatch(addActiveScenario(scenarioId));
    configurePluginsForScenario(scenarioId);
  });

  const sub2 = eventBus.on(TestingEvents.EndpointOverrideSet, ({ endpoint, response }) => {
    store.dispatch(setEndpointOverride({ endpoint, response }));
  });

  return () => {
    sub1.unsubscribe();
    sub2.unsubscribe();
  };
}

// packages/framework/src/utils/testUrl.ts
export function isTestRoute(): boolean {
  return window.location.pathname.startsWith('/_test/');
}

export function parseTestUrl(pathname: string): TestUrlConfig {
  // /_test/{screen}/{scenario}?{overrides}
  const match = pathname.match(/^\/_test\/([^/]+)\/([^/?]+)/);
  // ...
}

export function buildTestUrl(config: TestUrlConfig): string {
  return `/_test/${config.screen}/${config.scenario}`;
}
```

#### @hai3/react (L3) - React Level

**Why here:** React-specific hooks if needed. Otherwise just re-exports.

```typescript
// packages/react/src/hooks/useTestConfig.ts (optional)
export function useTestConfig() {
  const activeScenarios = useAppSelector(state => state.testing?.activeScenarios ?? []);
  const endpointOverrides = useAppSelector(state => state.testing?.endpointOverrides ?? {});

  return {
    activeScenarios,
    endpointOverrides,
    isTestMode: activeScenarios.length > 0,
  };
}

// packages/react/src/index.ts
export * from '@hai3/framework';  // Re-exports everything including testing
export { useTestConfig } from './hooks/useTestConfig';
```

#### @hai3/studio - Development UI

**Why here:** Developer-facing control panel, similar to existing ApiModeToggle.

```typescript
// packages/studio/src/sections/TestingPanel.tsx
import { useAppSelector, activateScenario, deactivateScenario } from '@hai3/react';

export const TestingPanel: React.FC = () => {
  const activeScenarios = useAppSelector(state => state.testing?.activeScenarios ?? []);
  const endpointOverrides = useAppSelector(state => state.testing?.endpointOverrides ?? {});

  return (
    <div>
      <ScenarioSelector
        active={activeScenarios}
        onActivate={(id) => activateScenario(id)}
        onDeactivate={(id) => deactivateScenario(id)}
      />
      <EndpointOverrideList overrides={endpointOverrides} />
    </div>
  );
};
```

### Why This Distribution

| Decision | Rationale |
|----------|-----------|
| Protocol plugins in L1 | Same as RestMockPlugin - intercepts at request level, no HAI3 deps |
| Plugin + effects in L2 | Framework owns plugin system and event coordination |
| Minimal L3 footprint | Only if React-specific behavior needed; otherwise just re-exports |
| UI in Studio | Follows ApiModeToggle pattern; developer tooling stays in studio |

### What Does NOT Belong in Each Layer

| Layer | Should NOT Include |
|-------|--------------------|
| L1 (@hai3/api) | Event bus usage, state management, URL routing |
| L2 (@hai3/framework) | React components, React hooks |
| L3 (@hai3/react) | Business logic (should be in actions/effects) |
| Studio | Application state logic (should use actions from framework) |

## State Management Design

### testingSlice - Minimal State

```typescript
interface TestingState {
  activeScenarios: string[];                        // IDs of active scenarios
  endpointOverrides: Record<string, EndpointOverride>;  // Runtime overrides
}
```

**What's NOT in state:**
- Scenario definitions (static, in registry)
- Mock response data (generated by plugins per-request)
- Application data (flows through normal API → effects → app state)

### URL as Primary Activation

The URL `/_test/{screen}/{scenario}` is the primary configuration mechanism:

```
Page load: /_test/chat/empty
    ↓
testing() plugin parses URL
    ↓
Emits activateScenario('empty')
    ↓
Effect updates testingSlice
    ↓
Plugin reads activeScenarios on each API request
```

On refresh, URL is reparsed - no persistence needed for core functionality.

### localStorage - Optional Enhancement

localStorage is NOT required for core functionality. It's an optional "remember preferences" feature:

```typescript
// Only if user opts in via Studio toggle
if (userPreferences.rememberOverrides) {
  persistOverride(endpoint, override);
}
```

This follows the existing `mockSlice` pattern which also doesn't persist.

## Required Changes

1. Replace `MockController` class with action functions that emit events
2. Add testing events to `EventPayloadMap` type augmentation
3. Add effects to handle testing events in @hai3/framework
4. Create `testingSlice` for scenario state (separate from existing `mockSlice`)
5. Distribute components across layers as specified above
6. Provide state access via `useAppSelector`, not getter methods
7. URL is primary activation - localStorage is optional enhancement only
