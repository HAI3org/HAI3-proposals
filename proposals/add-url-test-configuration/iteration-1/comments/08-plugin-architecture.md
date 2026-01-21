# Feedback: Plugin Architecture - Separate `mock()` and `testing()` Plugins

## Decision

Testing functionality should be implemented as a **separate `testing()` plugin** that depends on the existing `mock()` plugin, NOT merged into `mock()`.

## Rationale

### 1. Different Responsibilities

| Plugin | Responsibility |
|--------|----------------|
| `mock()` | Mock infrastructure - intercept API calls, return fake data |
| `testing()` | Test configuration - determine WHICH fake data for WHICH test case |

**Analogy**: Database driver vs seed data
- Driver = infrastructure for database access
- Seeds = configuration of what data exists
- These are separate concerns in every framework

### 2. Different Change Drivers

**When mock logic changes:**
- Adding WebSocket protocol support
- Changing plugin activation mechanism
- New mock plugin types

**When testing logic changes:**
- New scenario types
- URL format changes
- Data generation methods
- Scenario composition rules

Different change reasons = low cohesion if merged.

### 3. Industry Standard

| Framework | Mocking | Test Data/Fixtures |
|-----------|---------|-------------------|
| Angular | `HttpClientTestingModule` | Separate fixtures |
| Cypress | `cy.intercept()` | `cy.fixture()` - separate |
| Playwright | `page.route()` | Test fixtures - separate |
| Jest | `jest.mock()` | Test data - user managed |
| MSW | Mock handlers | Response generators - separate |

Mocking infrastructure and test data configuration are **consistently separate** across the industry.

### 4. Layered Architecture

```
┌─────────────────────────────────────┐
│  testing()                          │  ← Scenario configuration
│  - Which scenarios are active       │
│  - URL-based activation             │
│  - Per-endpoint overrides           │
├─────────────────────────────────────┤
│  mock()                             │  ← Mock infrastructure
│  - Enable/disable fake data         │
│  - Plugin lifecycle management      │
│  - Protocol-level interception      │
├─────────────────────────────────────┤
│  API Services                       │  ← Real API calls
│  - RestProtocol, SseProtocol        │
└─────────────────────────────────────┘
```

`testing()` is a layer ON TOP of `mock()`, not alongside it.

### 5. Valid Use Case for Mock-Only

| Use Case | Needs Mock? | Needs Scenarios? |
|----------|-------------|------------------|
| Developer building UI | Yes | No |
| Developer testing edge cases | Yes | Yes |
| E2E test | Yes | Yes |

Developers building UI need mocking but NOT scenario complexity. Separate plugins respect this.

### 6. Interface Segregation

**Merged (bad):**
```typescript
// Simple mock users get bloated interface
interface MockPlugin {
  toggleMockMode(enabled: boolean): void;
  activateScenario(id: string): void;      // Don't need
  deactivateScenario(id: string): void;    // Don't need
  setEndpointOverride(...): void;          // Don't need
  parseTestUrl(url: string): TestConfig;   // Don't need
  // ...
}
```

**Separate (good):**
```typescript
interface MockPlugin {
  toggleMockMode(enabled: boolean): void;
}

interface TestingPlugin {
  activateScenario(id: string): void;
  deactivateScenario(id: string): void;
  // ...
}
```

### 7. Plugin Model Fit

HAI3 favors small, focused, composable plugins:

```typescript
createHAI3()
  .use(screensets())   // Focused: screenset management
  .use(themes())       // Focused: theme management
  .use(mock())         // Focused: fake data infrastructure
  .use(testing())      // Focused: test scenario configuration
  .build();
```

Each plugin is a capability you opt into.

### 8. Future Extensibility

```
                    ┌─ testing()        (E2E scenarios)
                    │
mock() ─────────────┼─ visualTesting()  (future: visual regression)
                    │
                    └─ perfTesting()    (future: performance scenarios)
```

Separate plugins allow clean extension without bloating `mock()`.

## Proposed Plugin Structure

### `mock()` Plugin (Existing - No Changes)

```typescript
// packages/framework/src/plugins/mock.ts
export function mock(config?: MockPluginConfig): HAI3Plugin {
  return {
    name: 'mock',
    dependencies: ['effects'],
    provides: {
      slices: [mockSlice],
      actions: { toggleMockMode },
    },
    onInit() {
      initMockEffects();
      if (config?.enabledByDefault ?? isDevEnvironment()) {
        toggleMockMode(true);
      }
    },
  };
}
```

### `testing()` Plugin (New)

```typescript
// packages/framework/src/plugins/testing.ts
export interface TestingPluginConfig {
  /** Auto-activate scenario from URL (default: true) */
  autoActivateFromUrl?: boolean;
  /** Custom scenario definitions */
  scenarios?: Record<string, TestScenario>;
  /** Default scenario when none specified */
  defaultScenario?: string;
}

export function testing(config?: TestingPluginConfig): HAI3Plugin {
  return {
    name: 'testing',
    dependencies: ['mock', 'routing'],  // Explicit dependency on mock

    provides: {
      slices: [testingSlice],
      actions: {
        activateScenario,
        deactivateScenario,
        setEndpointOverride,
        clearEndpointOverride,
        resetScenarios,
      },
    },

    onInit(app) {
      // Skip in production
      if (!isDevEnvironment()) return;

      // Initialize effects
      cleanup = initTestingEffects();

      // Register custom scenarios
      if (config?.scenarios) {
        for (const [id, scenario] of Object.entries(config.scenarios)) {
          scenarioRegistry.register(id, scenario);
        }
      }

      // Auto-activate from URL
      if (config?.autoActivateFromUrl !== false && isTestRoute()) {
        const urlConfig = parseTestUrl(window.location.pathname);

        // Ensure mock mode is on
        toggleMockMode(true);

        // Activate scenario
        activateScenario(urlConfig.scenario);
      }
    },

    onDestroy() {
      cleanup?.();
    },
  };
}
```

### Relationship

```typescript
// testing() automatically ensures mock() is active when scenarios are used
function activateScenario(scenarioId: string): void {
  const state = getStore().getState();

  // Ensure mock mode is enabled
  if (!state.mock.enabled) {
    toggleMockMode(true);
  }

  // Emit scenario activation event
  eventBus.emit(TestingEvents.ScenarioActivated, { scenarioId });
}
```

## Required Changes to Proposal

### 1. Update `design.md`

Add decision documenting the two-plugin architecture:

```markdown
### Decision: Separate mock() and testing() Plugins

Testing functionality is implemented as a separate `testing()` plugin that depends on `mock()`.

**Rationale:**
- Different responsibilities (infrastructure vs configuration)
- Follows industry patterns (all major frameworks separate these concerns)
- Respects HAI3's composable plugin model
- Allows mock-only usage for simple development scenarios

**Relationship:**
- `mock()` provides infrastructure (toggle fake data on/off)
- `testing()` provides configuration (which scenarios, URL routing)
- `testing()` depends on `mock()` (declared in plugin dependencies)
```

### 2. Update `tasks.md`

Organize tasks by plugin:

```markdown
## mock() Plugin (Existing - Minimal Changes)

- [ ] Ensure mockSlice and toggleMockMode work as-is
- [ ] Verify isMockPlugin() type guard works with TestScenarioPlugin
- [ ] No new functionality needed in mock() plugin

## testing() Plugin (New)

### Plugin Infrastructure
- [ ] Create testing() plugin factory function
- [ ] Declare dependencies: ['mock', 'routing']
- [ ] Create testingSlice for scenario state
- [ ] Create testingEffects for event handling

### Actions
- [ ] Create activateScenario action
- [ ] Create deactivateScenario action
- [ ] Create setEndpointOverride action
- [ ] Create clearEndpointOverride action
- [ ] Create resetScenarios action

### URL Handling
- [ ] Create isTestRoute() utility
- [ ] Create parseTestUrl() utility
- [ ] Create buildTestUrl() utility
- [ ] Implement auto-activation from URL in onInit

### Scenario Registry
- [ ] Create scenarioRegistry for scenario definitions
- [ ] Register built-in scenarios (empty, error, slow, etc.)
- [ ] Support custom scenario registration via config
```

### 3. Update `spec.md`

Add requirements for the testing plugin:

```markdown
### Requirement: testing() Framework Plugin

The system SHALL provide a `testing()` framework plugin for test scenario management.

#### Scenario: Plugin registration
- **GIVEN** an HAI3 application
- **WHEN** using the `testing()` plugin
- **THEN** it SHALL declare dependencies on `mock` and `routing` plugins
- **AND** the framework SHALL ensure mock() is initialized before testing()

#### Scenario: Automatic mock activation
- **GIVEN** the `testing()` plugin is active
- **WHEN** a test scenario is activated
- **THEN** mock mode SHALL be automatically enabled if not already
- **AND** the scenario's mock responses SHALL be applied

#### Scenario: Plugin isolation
- **GIVEN** an application using only `mock()` without `testing()`
- **WHEN** the developer toggles mock mode
- **THEN** basic mock functionality SHALL work without scenario infrastructure
- **AND** no testing-related code SHALL be included in the bundle
```

## Usage Examples

### Simple Mock (No Scenarios)

```typescript
const app = createHAI3()
  .use(mock())  // Just basic mock toggle
  .build();

// Toggle in HAI3 Studio or code
app.actions.toggleMockMode(true);
```

### Full Testing Support

```typescript
const app = createHAI3()
  .use(mock())
  .use(testing({
    scenarios: {
      'many-items': manyItemsScenario,
      'slow-network': slowNetworkScenario,
    },
  }))
  .build();

// URL: /_test/chat/empty
// Or programmatically:
app.actions.activateScenario('empty');
```
