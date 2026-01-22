# URL-based Test Configuration and Granular Mock Control - Design

Technical patterns and architecture decisions for URL-based mock configuration, granular mock control, and UI-first development workflow.

## Context

HAI3 applications need:
- **Deterministic, isolated test environments** for E2E testing with parallel execution
- **UI-first development workflow** - build UI before backend exists, gradually enable real APIs
- **Human-readable mock data** - inspectable and editable by designers and product managers
- **Granular control** - toggle individual endpoints between mock and real backend

## Goals / Non-Goals

### Goals
- Enable parallel E2E test execution with URL-encoded mock configuration
- Support UI-first development with gradual backend integration
- Provide human-readable JSON mock storage that can be version controlled
- Enable per-endpoint mock toggle without code changes
- Provide framework-level primitives for test scenario management
- Support combinatoric test generation for comprehensive coverage
- Keep test infrastructure tree-shakeable in production builds

### Non-Goals
- Not providing E2E test runner infrastructure (covered by e2e-testing spec)
- Not replacing existing TypeScript mock functions (complementary, both supported)
- Not handling visual regression testing
- Not providing mock server (mocks run in-browser)

## Architecture Overview

### Test Configuration Flow

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                           Application Layer                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │ main.tsx: Conditional test wrapper based on isTestRoute()           │      │
│  │ URL: /{screen}/_test/{scenario}/{itemCount}/{tags}                  │      │
│  └─────────────────────────────────────────────────────────────────────┘      │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         React Integration Layer                               │
│  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ TestConfigProvider│  │ TestDataInitializer│  │  useTestConfig() hook    │  │
│  │ Parses URL config │  │ Populates Redux    │  │  Access config in comp   │  │
│  └───────────────────┘  └────────────────────┘  └──────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         API Testing Module (@hai3/api)                        │
│  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ TestScenarioPlugin│  │ TestScenarioPresets│  │  createItemsResponse()   │  │
│  │ Intercepts REST   │  │ Error, delay,      │  │  Generate mock lists     │  │
│  │ Pattern matching  │  │ empty presets      │  │  with factories          │  │
│  └───────────────────┘  └────────────────────┘  └──────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Granular Mock Control Flow

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                    Mock Data Storage (Human-Readable)                         │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │ src/screensets/{name}/mocks/                                        │      │
│  │   ├── sessions.mock.json    ← GET /api/cyberchat/sessions           │      │
│  │   ├── messages.mock.json    ← GET /api/cyberchat/messages/:id       │      │
│  │   └── _index.json           ← Mock manifest with metadata           │      │
│  └─────────────────────────────────────────────────────────────────────┘      │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         Mock Registry (@hai3/api)                             │
│  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │  MockDataLoader   │  │   MockRegistry     │  │    MockController        │  │
│  │  Loads JSON files │  │   Stores all mocks │  │    Per-endpoint toggle   │  │
│  │  Validates schema │  │   Pattern matching │  │    URL/localStorage      │  │
│  └───────────────────┘  └────────────────────┘  └──────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         HAI3 Studio Panel                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │ Mock Control Panel                                                  │      │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │      │
│  │ │ Endpoint                          │ Mock │ Real │ Status        │ │      │
│  │ ├─────────────────────────────────────────────────────────────────┤ │      │
│  │ │ GET /api/cyberchat/sessions       │  ●   │  ○   │ ✓ Mocked      │ │      │
│  │ │ GET /api/cyberchat/messages/:id   │  ●   │  ○   │ ✓ Mocked      │ │      │
│  │ │ POST /api/cyberchat/chat/stream   │  ○   │  ●   │ → Real API    │ │      │
│  │ └─────────────────────────────────────────────────────────────────┘ │      │
│  └─────────────────────────────────────────────────────────────────────┘      │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Decisions

### Decision: URL-encoded Configuration

**Context**: Tests need different mock data states (empty, error, slow, etc.) and must run in parallel.

**Decision**: Encode mock configuration in the URL path at `/_test/` prefix.

**Rationale**:
- Global mock state prevents parallel test execution
- URL-based config allows multiple browser instances with different states
- Configuration is visible and debuggable in browser address bar
- Enables deterministic test reproduction by sharing URL
- Natural fit with E2E testing where navigation is URL-based

**Format**: `/{screen}/_test/{scenario}/{itemCount}/{tags...}`

**Rationale for screen-first format**:
- Screen path comes first, matching natural navigation structure
- `_test` segment acts as a marker, not a prefix - easier to recognize and strip
- URL reads naturally: "chat screen with empty test data"
- Allows nested screen paths: `/settings/profile/_test/empty`
- Simpler routing: screen component receives `_test/*` as nested route

**Examples**:
- `/chat/_test/empty` - Empty data for chat screen
- `/chat/_test/standard/100/slow` - Standard scenario, 100 items, slow network
- `/chat/_test/error` - Server error scenario
- `/settings/profile/_test/unauthorized` - Unauthorized scenario for nested screen

### Decision: Plugin-based Mock Control

**Context**: HAI3 uses a plugin architecture for API request/response modification.

**Decision**: Implement `TestScenarioPlugin` as a `RestPluginWithConfig` extension.

**Rationale**:
- Leverages existing plugin infrastructure
- Consistent with other mock plugins (RestMockPlugin)
- Allows composition with other plugins
- Clear extension point via `TestScenarioController` interface

**Implementation**:
```typescript
class TestScenarioPlugin extends RestPluginWithConfig<TestScenarioPluginConfig>
  implements TestScenarioController {

  activateScenario(scenarioId: string): void
  deactivateScenario(scenarioId: string): void
  setResponse(endpoint: string, response: TestScenarioResponse): void
  clearResponse(endpoint: string): void
  reset(): void
}
```

### Decision: Layered Scenario Resolution

**Context**: Multiple scenarios may be active, and per-endpoint overrides need highest priority.

**Decision**: Three-tier priority for response resolution:
1. Per-endpoint overrides (highest)
2. Active scenarios (later activation wins)
3. Pass-through (no mock, real API)

**Rationale**:
- Per-endpoint overrides allow fine-grained control in tests
- Scenario stacking enables complex test setups
- Pass-through is safe default when no mock configured

### Decision: React Context for Configuration

**Context**: Test configuration needs to be accessible throughout the component tree.

**Decision**: Provide `TestConfigProvider` context and `useTestConfig()` hook.

**Rationale**:
- Standard React pattern for cross-cutting concerns
- Allows conditional rendering based on test mode
- Enables screenset-specific test data initialization
- Clean separation from production code paths

### Decision: Development-Only Test Routes

**Context**: Test routes and infrastructure should not be in production builds.

**Decision**: Guard test routes and plugin creation with `import.meta.env.DEV`.

**Rationale**:
- Tree-shaking removes test code in production
- No runtime overhead in production builds
- Clear development/production separation
- Test infrastructure doesn't increase bundle size

### Decision: Combinatoric Configuration

**Context**: Testing all combinations of data sizes, delays, and error states manually is tedious.

**Decision**: Provide utility functions for generating test configuration permutations.

**Rationale**:
- Reduces boilerplate in parameterized tests
- Ensures consistent boundary condition coverage
- Pre-built configs provide starting points
- Integration with E2E test framework pytest parametrization

### Decision: JSON Mock Data Storage

**Context**: Current TypeScript mock functions are powerful but not human-readable for non-developers.

**Decision**: Support JSON mock files alongside TypeScript mock functions.

**File Structure**:
```
src/screensets/cyberChat/mocks/
├── _index.json              # Manifest: lists all mocks, metadata
├── sessions.mock.json       # Mock for GET /api/cyberchat/sessions
├── messages.mock.json       # Mock for GET /api/cyberchat/messages/:id
└── scenarios/               # Named scenarios for different states
    ├── empty.json           # Empty state responses
    └── many-chats.json      # 100 chat sessions
```

**Mock File Schema** (`sessions.mock.json`):
```json
{
  "$schema": "https://hai3.dev/schemas/mock.json",
  "endpoint": "GET /api/cyberchat/sessions",
  "description": "Returns list of chat sessions",
  "delay": 100,
  "response": {
    "status": 200,
    "data": [
      { "id": "session-1", "title": "Code Review", "messages": [] }
    ]
  },
  "variants": {
    "empty": { "data": [] },
    "error": { "status": 500, "data": { "error": "Server Error" } }
  }
}
```

**Dynamic Data Generation** (faker templates):
```json
{
  "endpoint": "GET /api/cyberchat/sessions",
  "response": {
    "data": {
      "$generate": {
        "count": 10,
        "template": {
          "id": "{{faker.string.uuid}}",
          "title": "{{faker.lorem.sentence}}",
          "createdAt": "{{faker.date.recent}}",
          "user": {
            "name": "{{faker.person.fullName}}",
            "email": "{{faker.internet.email}}"
          }
        }
      }
    }
  }
}
```

**Supported Faker Methods**:
- `{{faker.string.uuid}}` - Random UUID
- `{{faker.person.fullName}}` - Full name
- `{{faker.internet.email}}` - Email address
- `{{faker.lorem.sentence}}` - Random sentence
- `{{faker.lorem.paragraph}}` - Random paragraph
- `{{faker.date.recent}}` - Recent ISO date
- `{{faker.number.int(min, max)}}` - Random integer

**Rationale**:
- Human-readable: designers and PMs can inspect/edit mock data
- Version controlled: changes tracked in git
- IDE support: JSON schema provides autocomplete
- Dynamic: faker templates generate realistic test data
- Coexistence: TypeScript mocks still work for complex conditional logic
- Discoverable: `_index.json` manifest lists all available mocks

### Decision: Granular Mock Controller

**Context**: Need to toggle individual endpoints between mock and real backend during development.

**Decision**: Implement `MockController` with three control layers:
1. **URL parameters** (highest priority) - for E2E tests and sharing
2. **localStorage** (persisted) - for developer preferences
3. **Defaults** (lowest priority) - from mock manifest

**URL Parameter Format**:
```
# Enable specific mocks (others pass to real API)
/chat?mock=sessions,messages

# Disable specific mocks (use real API for these)
/chat?real=sessions

# All mocked (default in dev)
/chat?mock=all

# All real (test real backend)
/chat?mock=none
```

**Rationale**:
- URL-shareable: developers can share specific mock states
- Persistent: localStorage remembers preferences across reloads
- Gradual: start all mocked, enable real APIs one by one
- Testable: E2E tests can specify exact mock configuration

### Decision: HAI3 Studio Mock Panel

**Context**: Developers need visual control over mock state without editing code or URLs.

**Decision**: Add "Mock Control" panel to HAI3 Studio with:
- List of all registered mock endpoints
- Toggle switch per endpoint (Mock/Real)
- Status indicator (mocked, real, error, loading)
- Quick actions: "Mock All", "Real All", "Reset"
- View/edit mock data inline (read-only in panel, click to open JSON file)

**Rationale**:
- Visual feedback on current mock state
- Quick toggle without URL manipulation
- Debug visibility: see which endpoints are mocked
- Integration with existing Studio infrastructure

### Decision: Mock Priority Chain

**Context**: Multiple sources can define mock behavior (JSON, TypeScript, scenarios, overrides).

**Decision**: Establish clear priority order for mock resolution:

```
1. Per-endpoint runtime overrides (highest) - TestScenarioController.setResponse()
2. Active test scenario responses - TestScenarioController.activateScenario()
3. MockController enabled/disabled state
4. URL parameters (?mock=, ?real=)
5. localStorage preferences
6. TypeScript mock functions (mockMap)
7. JSON mock files
8. Pass-through to real API (lowest)
```

**Rationale**:
- Predictable: developers know what takes precedence
- Layered: each layer can override the one below
- Flexible: supports all use cases from simple to complex

## Risks / Trade-offs

### Risk: URL Length Limits
**Mitigation**: Keep URL segments short (scenario IDs, numbers, single tags). Complex configurations use scenario registry lookup.

### Risk: Test/Production Divergence
**Mitigation**: Test scenarios should mirror realistic data shapes. Use same data generators as development mocks.

### Trade-off: Additional Bundle in Development
**Accepted**: Test infrastructure adds ~5KB to dev bundle. Acceptable for improved testing capabilities.

## Resolved Questions

- **Scenario definitions shareable across screensets?** → No, keep screenset-specific for vertical slice isolation
- **Dynamic generation in JSON mocks?** → Yes, support `{{faker.*}}` syntax for generated data
- **Mock panel request/response history?** → No, keep panel simple (use browser DevTools for debugging)
- **Conditional responses based on request body?** → No, use TypeScript mocks for complex logic

## Open Questions

(None currently)
