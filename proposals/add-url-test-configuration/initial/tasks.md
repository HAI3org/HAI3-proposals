# URL-based Test Configuration - Tasks

## 1. API Testing Module (@hai3/api)

- [ ] 1.1 Create `TestScenarioResponse` type with data, statusCode, delayMs, errorMessage, headers
- [ ] 1.2 Create `TestScenario` type with id, description, and responses map
- [ ] 1.3 Create `TestScenarioState` type for tracking active scenarios and overrides
- [ ] 1.4 Create `TestScenarioRegistry` interface for scenario registration
- [ ] 1.5 Create `TestScenarioController` interface for runtime manipulation
- [ ] 1.6 Implement `TestScenarioPresets` constants (SERVER_ERROR, NOT_FOUND, UNAUTHORIZED, etc.)
- [ ] 1.7 Implement `createItemsResponse()` helper for generating mock lists
- [ ] 1.8 Implement `TestScenarioPlugin` class extending `RestPluginWithConfig`
- [ ] 1.9 Implement URL pattern matching in plugin (`:param` syntax)
- [ ] 1.10 Export testing module from `@hai3/api` package index

## 2. URL Test Configuration Parsing

- [ ] 2.1 Define `TEST_ROUTE_SEGMENT` constant (`_test`)
- [ ] 2.2 Create `UrlTestConfig` interface with `screenPath`, `scenarioId`, `itemCount`, `tags`, `mockControl`
- [ ] 2.3 Define `UrlScenarioIds` well-known scenario constants
- [ ] 2.4 Define `UrlTestTags` well-known modifier tag constants
- [ ] 2.5 Implement `parseUrlTestConfig()` for browser environment
- [ ] 2.6 Implement `parsePathname()` for pure path parsing
- [ ] 2.7 Implement `buildTestUrl()` for constructing test URLs with new format
- [ ] 2.8 Implement `isTestRoute()` utility function
- [ ] 2.9 Implement `getScreenPath()` for extracting target screen
- [ ] 2.10 Implement `getResponseModifiers()` for converting tags to response modifiers

## 3. React Integration

- [ ] 3.1 Create `TestConfigContext` with `UrlTestConfig`, `isTestMode`, `isConfigured`
- [ ] 3.2 Implement `useTestConfig()` hook
- [ ] 3.3 Implement `TestConfigProvider` component with URL parsing on mount
- [ ] 3.4 Implement mock response generation based on URL config
- [ ] 3.5 Implement scenario activation and endpoint overrides
- [ ] 3.6 Remove navigation logic (screen is now part of URL path)
- [ ] 3.7 Implement `TestConfigReady` wrapper component
- [ ] 3.8 Create `TestDataInitializer` component for Redux state population
- [ ] 3.9 Implement screenset-specific test data initialization (cyberChat example)

## 4. Test Scenario Registry

- [ ] 4.1 Create generic scenarios (EMPTY_DATA, SERVER_ERROR, SLOW_NETWORK, UNAUTHORIZED)
- [ ] 4.2 Create `createItemCountScenario()` parameterized generator
- [ ] 4.3 Create `withDelay()` response wrapper
- [ ] 4.4 Define `CombinatoricConfig` type
- [ ] 4.5 Implement `generateCombinatoricScenarios()` for test permutations
- [ ] 4.6 Create screenset-specific scenarios (CHAT_SCENARIOS, DEMO_SCENARIOS)
- [ ] 4.7 Create `ALL_SCENARIOS` registry and lookup functions

## 5. Application Integration

- [ ] 5.1 Update `main.tsx` to conditionally wrap with `TestConfigProvider`
- [ ] 5.2 Create `TestScenarioPlugin` instance in development mode only
- [ ] 5.3 Pass plugin controller to `TestConfigProvider`
- [ ] 5.4 Add `TestDataInitializer` inside HAI3Provider

## 6. CyberChat Test Data (Example Implementation)

- [ ] 6.1 Create `mockData` object with standard and many-chats scenarios
- [ ] 6.2 Implement data generators (generateSession, generateProject, generateSkill)
- [ ] 6.3 Implement `initializeCyberChatTestData()` for Redux state initialization
- [ ] 6.4 Implement `isCyberChatScreen()` for screenset detection

## 7. JSON Mock Data Storage

- [ ] 7.1 Define JSON mock file schema types (`MockFileSchema`, `MockResponse`)
- [ ] 7.2 Create `MockDataLoader` class for loading JSON mock files
- [ ] 7.3 Create `MockIndexSchema` type for `_index.json` manifest
- [ ] 7.4 Implement JSON mock file validation in MockDataLoader
- [ ] 7.5 Implement faker template processor (`{{faker.*}}` syntax)
- [ ] 7.6 Implement `$generate` directive for bulk data generation
- [ ] 7.7 Create lightweight faker implementation (no external dependency)
- [ ] 7.8 Create example JSON mock files for cyberChat screenset
- [ ] 7.9 Export mock utilities from `@hai3/api` package

## 8. Granular Mock Controller

- [ ] 8.1 Create `MockController` class with enable/disable per-endpoint
- [ ] 8.2 Implement URL parameter parsing for `?mock=` and `?real=` in `UrlTestConfig`
- [ ] 8.3 Implement localStorage persistence for mock preferences
- [ ] 8.4 Implement priority chain resolution (URL > localStorage > defaults)
- [ ] 8.5 Export `mockController` singleton instance
- [ ] 8.6 Add `MockControllerState` and `EndpointMockState` types

## 9. HAI3 Studio Mock Panel

- [ ] 9.1 Create `MockControlPanel` component
- [ ] 9.2 Add endpoint list with toggle switches
- [ ] 9.3 Add status indicators (mocked/real with color coding)
- [ ] 9.4 Add bulk actions (Mock All, Real All, Reset)
- [ ] 9.5 Integrate panel with ControlPanel in Studio
- [ ] 9.6 Add i18n translations for mock control

## 10. Documentation

- [ ] 10.1 Add JSDoc comments to MockController
- [ ] 10.2 Add JSDoc comments to FakerProcessor
- [ ] 10.3 Add JSDoc comments to MockDataLoader
- [ ] 10.4 Document URL format in urlTestConfig.ts
- [ ] 10.5 Document JSON mock file format in types.ts
- [ ] 10.6 Test patterns documented in design.md (GUIDELINES.md update optional)

## 11. Testing

- [ ] 11.1 Add unit tests for URL parsing functions (27 tests)
- [ ] 11.2 Add unit tests for TestScenarioPlugin (25 tests)
- [ ] 11.3 Add unit tests for MockController (21 tests)
- [ ] 11.4 Add unit tests for FakerProcessor (16 tests)
- [ ] 11.5 All 89 tests passing
- [ ] 11.6 Production build verified (tree-shaking via dev-only guards)
