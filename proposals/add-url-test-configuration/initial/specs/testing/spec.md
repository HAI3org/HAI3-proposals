## ADDED Requirements

### Requirement: URL-based Test Route Format

The system SHALL support URL-based test configuration using the `_test` path segment to enable parallel E2E test execution with different mock data states.

#### Scenario: Test URL format parsing
- **GIVEN** a URL path containing `/_test/` segment
- **WHEN** the application parses the URL
- **THEN** it SHALL extract configuration in format `/{screen}/_test/{scenario}/{itemCount}/{tags...}`
- **AND** `screen` SHALL be the target screen path before the `_test` segment (may include nested paths like `/settings/profile`)
- **AND** `scenario` SHALL be a well-known scenario ID or screenset-specific identifier
- **AND** `itemCount` SHALL be an optional positive integer for list size
- **AND** `tags` SHALL be zero or more modifier tags

#### Scenario: Nested screen paths
- **GIVEN** a URL with nested screen path (e.g., `/settings/profile/_test/empty`)
- **WHEN** the URL is parsed
- **THEN** the screen path SHALL be extracted as `/settings/profile`
- **AND** the test configuration SHALL be extracted from segments after `_test`

#### Scenario: Well-known scenario IDs
- **GIVEN** the URL-based test system
- **THEN** it SHALL recognize the following scenario IDs:
  - `empty` - Returns empty data for all endpoints
  - `error` - Returns HTTP 500 for all endpoints
  - `slow` - Adds 2 second delay to responses
  - `very-slow` - Adds 5 second delay to responses
  - `timeout` - Simulates 30 second timeout
  - `not-found` - Returns HTTP 404
  - `unauthorized` - Returns HTTP 401
  - `default` - Uses default mock data

#### Scenario: Well-known modifier tags
- **GIVEN** the URL-based test system
- **THEN** it SHALL recognize the following tags:
  - `slow` - Add network delay
  - `paginated` - Enable pagination
  - `loading` - Show loading states
  - `offline` - Simulate offline mode

#### Scenario: URL building
- **GIVEN** a test configuration object
- **WHEN** calling `buildTestUrl()` with screen, scenario, itemCount, and tags
- **THEN** it SHALL return a valid test URL path in format `/{screen}/_test/{scenario}/{itemCount}/{tags}`
- **AND** empty optional values SHALL be omitted from the path

### Requirement: TestScenarioPlugin for Mock Response Control

The system SHALL provide a `TestScenarioPlugin` class that extends the API plugin architecture to control mock responses at runtime during E2E tests.

#### Scenario: Plugin creation
- **GIVEN** a developer wants to enable test scenario control
- **WHEN** creating a `TestScenarioPlugin` instance
- **THEN** it SHALL accept an optional configuration with `enabled` and `baseDelay` properties
- **AND** it SHALL implement the `RestPluginWithConfig` interface
- **AND** it SHALL expose `registry` and `controller` properties

#### Scenario: Scenario registration
- **GIVEN** a `TestScenarioPlugin` instance
- **WHEN** registering a test scenario via `registry.register()`
- **THEN** the scenario SHALL be stored with its unique ID
- **AND** the scenario SHALL contain endpoint-to-response mappings

#### Scenario: Scenario activation
- **GIVEN** a registered test scenario
- **WHEN** calling `controller.activateScenario(scenarioId)`
- **THEN** the scenario responses SHALL be applied to matching API requests
- **AND** multiple scenarios MAY be active simultaneously
- **AND** later activated scenarios SHALL take precedence

#### Scenario: Per-endpoint override
- **GIVEN** an active test scenario
- **WHEN** calling `controller.setResponse(endpoint, response)`
- **THEN** the specific endpoint response SHALL override scenario responses
- **AND** overrides SHALL have highest priority

#### Scenario: Response resolution priority
- **GIVEN** multiple active scenarios and per-endpoint overrides
- **WHEN** an API request is intercepted
- **THEN** resolution order SHALL be:
  1. Per-endpoint overrides (highest priority)
  2. Active scenarios (later activation wins)
  3. Pass-through to real API (no mock)

#### Scenario: URL pattern matching
- **GIVEN** an endpoint pattern with path parameters (e.g., `/api/items/:id`)
- **WHEN** a request matches the pattern
- **THEN** the configured response SHALL be returned
- **AND** `:param` segments SHALL match any single path segment

#### Scenario: Reset state
- **GIVEN** active scenarios and endpoint overrides
- **WHEN** calling `controller.reset()`
- **THEN** all active scenarios SHALL be deactivated
- **AND** all endpoint overrides SHALL be cleared

### Requirement: Test Scenario Response Configuration

The system SHALL provide `TestScenarioResponse` type and preset responses for common test scenarios.

#### Scenario: Response configuration properties
- **GIVEN** a `TestScenarioResponse` configuration
- **THEN** it SHALL support:
  - `data` - Response body (JSON-compatible)
  - `statusCode` - HTTP status code (default: 200)
  - `delayMs` - Artificial response delay in milliseconds
  - `errorMessage` - Error message for error responses
  - `headers` - Custom response headers

#### Scenario: Preset responses
- **GIVEN** the `TestScenarioPresets` object
- **THEN** it SHALL provide:
  - `SERVER_ERROR` - HTTP 500 with error message
  - `NOT_FOUND` - HTTP 404 with error message
  - `UNAUTHORIZED` - HTTP 401 with error message
  - `FORBIDDEN` - HTTP 403 with error message
  - `SLOW_NETWORK` - 2000ms delay
  - `VERY_SLOW_NETWORK` - 5000ms delay
  - `TIMEOUT` - 30000ms delay
  - `EMPTY_LIST` - Empty array response
  - `NULL_RESPONSE` - Null response

#### Scenario: Dynamic response generation
- **GIVEN** the `createItemsResponse()` helper
- **WHEN** called with item count and optional factory function
- **THEN** it SHALL return a response with an array of generated items
- **AND** the factory SHALL receive the item index

### Requirement: React Test Configuration Provider

The system SHALL provide React components for integrating URL-based test configuration with HAI3 applications.

#### Scenario: TestConfigProvider wrapping
- **GIVEN** an HAI3 application with test routes enabled
- **WHEN** the app loads on a `/_test/*` URL
- **THEN** `TestConfigProvider` SHALL parse the URL configuration
- **AND** apply mock configurations to the provided controller
- **AND** provide configuration via React context

#### Scenario: useTestConfig hook
- **GIVEN** a component inside `TestConfigProvider`
- **WHEN** calling `useTestConfig()`
- **THEN** it SHALL return:
  - `config` - Parsed URL test configuration
  - `isTestMode` - Whether running in test mode
  - `isConfigured` - Whether configuration has been applied

#### Scenario: Test route navigation
- **GIVEN** a test URL with screen and configuration (e.g., `/chat/_test/empty`)
- **WHEN** the configuration is applied
- **THEN** the app SHALL render the target screen (`/chat`)
- **AND** the mock configuration SHALL be active for the screen
- **AND** the URL SHALL remain as-is (including `_test` segment) for debugging visibility

#### Scenario: TestConfigReady wrapper
- **GIVEN** the `TestConfigReady` component
- **WHEN** test configuration is not yet applied
- **THEN** children SHALL not render (or fallback renders)
- **WHEN** configuration is applied
- **THEN** children SHALL render

### Requirement: Test Data Initialization

The system SHALL provide components for initializing Redux state with test data based on URL configuration.

#### Scenario: TestDataInitializer component
- **GIVEN** `TestDataInitializer` component inside `HAI3Provider`
- **WHEN** running in test mode with a recognized target screen
- **THEN** it SHALL dispatch Redux actions to populate state with test data
- **AND** initialization SHALL happen once per mount

#### Scenario: Screenset-specific test data
- **GIVEN** a screenset with test data configuration (e.g., cyberChat)
- **WHEN** the URL targets that screenset's screen
- **THEN** the appropriate test data initialization function SHALL be called
- **AND** the function SHALL receive the URL test config

#### Scenario: Scenario-based data selection
- **GIVEN** a URL with scenario ID (e.g., `/chat/_test/many-chats`)
- **WHEN** test data is initialized
- **THEN** the scenario-specific data set SHALL be loaded
- **AND** unknown scenarios SHALL fall back to default data

### Requirement: Combinatoric Test Scenario Generation

The system SHALL provide utilities for generating test scenario permutations to support comprehensive test coverage.

#### Scenario: Combinatoric configuration
- **GIVEN** a `CombinatoricConfig` object
- **THEN** it SHALL specify:
  - `itemCounts` - Array of item counts to test (e.g., [0, 1, 10, 100])
  - `delays` - Array of delay values in ms
  - `endpoints` - Array of endpoints to apply scenarios to

#### Scenario: Generate combinatoric scenarios
- **GIVEN** a combinatoric configuration
- **WHEN** calling `generateCombinatoricScenarios(config)`
- **THEN** it SHALL return all permutations as `TestScenario[]`
- **AND** each scenario SHALL have unique ID (e.g., `combo-items10-delay500`)
- **AND** responses SHALL be applied to all specified endpoints

#### Scenario: Default combinatoric configuration
- **GIVEN** no configuration provided
- **WHEN** calling `generateCombinatoricScenarios()`
- **THEN** it SHALL use `DEFAULT_COMBINATORIC_CONFIG`
- **AND** default item counts SHALL be [0, 1, 10, 50, 100]
- **AND** default delays SHALL be [0, 500, 2000]

#### Scenario: Parameterized scenario helpers
- **GIVEN** scenario generation utilities
- **THEN** the system SHALL provide:
  - `createItemCountScenario(count, endpoint)` - Single item count scenario
  - `withDelay(delayMs, baseResponse)` - Add delay to response

### Requirement: Development-Only Test Infrastructure

The system SHALL ensure test infrastructure is only included in development builds.

#### Scenario: Plugin creation guard
- **GIVEN** the application entry point
- **WHEN** creating `TestScenarioPlugin`
- **THEN** it SHALL only be created when `import.meta.env.DEV` is true
- **AND** production builds SHALL not include the plugin instance

#### Scenario: TestConfigProvider guard
- **GIVEN** the application render logic
- **WHEN** wrapping with `TestConfigProvider`
- **THEN** it SHALL only wrap when `isTestRoute()` returns true
- **AND** non-test routes SHALL render without the provider

#### Scenario: Tree-shaking compatibility
- **GIVEN** test utilities exported from packages
- **WHEN** building for production
- **THEN** unused test exports SHALL be tree-shaken
- **AND** production bundle size SHALL not increase

### Requirement: API Package Testing Exports

The `@hai3/api` package SHALL export testing utilities for E2E test integration.

#### Scenario: Testing module exports
- **GIVEN** the `@hai3/api` package
- **THEN** it SHALL export:
  - `TestScenarioPlugin` class
  - `TestScenarioPresets` object
  - `createItemsResponse` function
  - `TestScenarioPluginConfig` type
  - `TestScenario` type
  - `TestScenarioResponse` type
  - `TestScenarioState` type
  - `TestScenarioRegistry` interface
  - `TestScenarioController` interface

#### Scenario: Package export path
- **GIVEN** consumer code importing from `@hai3/api`
- **WHEN** importing testing utilities
- **THEN** they SHALL be available from the main package export
- **AND** `import { TestScenarioPlugin } from '@hai3/api'` SHALL work

### Requirement: JSON Mock Data Storage

The system SHALL support human-readable JSON files for mock data storage, enabling non-developers to inspect and edit mock responses.

#### Scenario: Mock file structure
- **GIVEN** a screenset with mock data
- **THEN** mock files SHALL be located at `src/screensets/{name}/mocks/`
- **AND** each endpoint SHALL have a dedicated `{name}.mock.json` file
- **AND** a `_index.json` manifest SHALL list all available mocks

#### Scenario: Mock file schema
- **GIVEN** a mock JSON file
- **THEN** it SHALL contain:
  - `endpoint` - The API endpoint pattern (e.g., "GET /api/cyberchat/sessions")
  - `description` - Human-readable description
  - `delay` - Optional response delay in milliseconds
  - `response` - The mock response with `status` and `data`
  - `variants` - Optional named variations (empty, error, etc.)

#### Scenario: Mock data loading
- **GIVEN** JSON mock files in the mocks directory
- **WHEN** the application initializes in development mode
- **THEN** the `MockDataLoader` SHALL load all JSON mock files
- **AND** register them with the `MockRegistry`
- **AND** validate against the mock schema

#### Scenario: TypeScript and JSON coexistence
- **GIVEN** both TypeScript mock functions and JSON mock files exist for the same endpoint
- **WHEN** resolving mock response
- **THEN** TypeScript mock functions SHALL take precedence over JSON mocks
- **AND** JSON mocks SHALL be used as fallback when no TypeScript mock exists

#### Scenario: Dynamic data generation with faker
- **GIVEN** a JSON mock file with `{{faker.*}}` template syntax
- **WHEN** the mock response is generated
- **THEN** faker placeholders SHALL be replaced with generated values
- **AND** `{{faker.string.uuid}}` SHALL generate a random UUID
- **AND** `{{faker.person.fullName}}` SHALL generate a realistic name
- **AND** `{{faker.internet.email}}` SHALL generate an email address
- **AND** `{{faker.date.recent}}` SHALL generate a recent ISO date

#### Scenario: Bulk data generation
- **GIVEN** a JSON mock with `$generate` directive
- **WHEN** the mock response is generated
- **THEN** the system SHALL create `count` items using the `template`
- **AND** each item SHALL have unique faker-generated values

#### Scenario: Faker generation is deterministic per session
- **GIVEN** faker-based mock data
- **WHEN** the same mock is requested multiple times in a session
- **THEN** the generated values SHALL remain consistent
- **AND** reloading the page MAY generate new values

### Requirement: Granular Mock Controller

The system SHALL provide a `MockController` for toggling individual API endpoints between mock and real backend.

#### Scenario: Enable specific mocks via URL
- **GIVEN** a URL with `?mock=sessions,messages` parameter
- **WHEN** the application loads
- **THEN** only the specified endpoints SHALL be mocked
- **AND** all other endpoints SHALL pass through to real API

#### Scenario: Disable specific mocks via URL
- **GIVEN** a URL with `?real=sessions` parameter
- **WHEN** the application loads
- **THEN** the specified endpoints SHALL pass through to real API
- **AND** all other endpoints SHALL remain mocked

#### Scenario: Mock all endpoints
- **GIVEN** a URL with `?mock=all` parameter
- **WHEN** the application loads
- **THEN** all registered mock endpoints SHALL be active

#### Scenario: Disable all mocks
- **GIVEN** a URL with `?mock=none` parameter
- **WHEN** the application loads
- **THEN** no mocks SHALL be active
- **AND** all requests SHALL pass through to real API

#### Scenario: localStorage persistence
- **GIVEN** a developer toggles mock state via Studio panel
- **WHEN** the page is reloaded
- **THEN** the mock preferences SHALL be restored from localStorage
- **AND** URL parameters SHALL override localStorage if present

#### Scenario: MockController API
- **GIVEN** the `MockController` instance
- **THEN** it SHALL provide:
  - `enable(endpoint: string)` - Enable mock for endpoint
  - `disable(endpoint: string)` - Disable mock for endpoint
  - `enableAll()` - Enable all mocks
  - `disableAll()` - Disable all mocks
  - `isEnabled(endpoint: string)` - Check if endpoint is mocked
  - `getState()` - Get current mock state for all endpoints
  - `reset()` - Reset to default state

### Requirement: HAI3 Studio Mock Panel

The system SHALL provide a visual panel in HAI3 Studio for controlling mock state.

#### Scenario: Mock panel display
- **GIVEN** HAI3 Studio is open
- **WHEN** the developer opens the Mock Control panel
- **THEN** it SHALL display a list of all registered mock endpoints
- **AND** each endpoint SHALL show current state (Mocked/Real)
- **AND** each endpoint SHALL have a toggle switch

#### Scenario: Toggle mock state
- **GIVEN** the Mock Control panel is open
- **WHEN** the developer clicks the toggle for an endpoint
- **THEN** the mock state SHALL change immediately
- **AND** the preference SHALL be persisted to localStorage
- **AND** subsequent API calls SHALL use the new state

#### Scenario: Bulk actions
- **GIVEN** the Mock Control panel is open
- **THEN** it SHALL provide:
  - "Mock All" button - Enable all mocks
  - "Real All" button - Disable all mocks
  - "Reset" button - Reset to default preferences

#### Scenario: Status indicators
- **GIVEN** the Mock Control panel is open
- **THEN** each endpoint SHALL show status:
  - Green checkmark - Currently mocked
  - Blue arrow - Passing to real API
  - Red indicator - Last request failed
  - Spinner - Request in progress

### Requirement: Mock Priority Resolution

The system SHALL resolve mock responses following a defined priority chain.

#### Scenario: Priority order
- **GIVEN** multiple mock sources are configured
- **WHEN** an API request is made
- **THEN** the system SHALL check sources in order:
  1. Per-endpoint runtime overrides (TestScenarioController.setResponse)
  2. Active test scenario responses
  3. MockController enabled/disabled state
  4. URL parameters (?mock=, ?real=)
  5. localStorage preferences
  6. TypeScript mock functions
  7. JSON mock files
  8. Pass-through to real API

#### Scenario: First match wins
- **GIVEN** a mock source provides a response
- **WHEN** resolving the mock
- **THEN** lower priority sources SHALL NOT be consulted
- **AND** the response SHALL be returned immediately
