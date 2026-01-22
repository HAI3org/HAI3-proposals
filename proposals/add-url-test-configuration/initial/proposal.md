# Change: Add URL-based Test Configuration and Granular Mock Control

## Why

HAI3 applications need to support:

1. **Parallel E2E test execution** with different mock data configurations - currently global mock state prevents running multiple browser instances with different test scenarios simultaneously.

2. **UI-first development workflow** - ability to build UI components before backend APIs exist, then gradually switch individual endpoints from mock to real backend as implementation progresses.

3. **Human-readable mock data** - current TypeScript function-based mocks are not easily inspectable or editable by non-developers; JSON-based storage would enable better collaboration.

4. **Granular mock control** - toggle individual API endpoints between mock and real backend without affecting others.

## What Changes

- **ADDED** URL-based test configuration system in `@hai3/api` package
  - `TestScenarioPlugin` - REST plugin for scenario-based mock response control
  - `TestScenarioController` interface for runtime mock manipulation
  - `TestScenarioPresets` - Predefined response presets (errors, delays, empty states)

- **ADDED** Human-readable mock data storage
  - JSON mock files at `src/screensets/{name}/mocks/*.json`
  - Mock schema with request/response pairs, delays, and metadata
  - TypeScript loader for JSON mock files with type safety

- **ADDED** Granular mock endpoint control
  - `MockController` for per-endpoint enable/disable
  - URL parameter override: `?mock=sessions,messages` or `?real=chat/stream`
  - Persistent mock preferences via localStorage
  - HAI3 Studio panel integration for visual mock toggle

- **ADDED** URL test route parsing at application level
  - URL format: `/{screen}/_test/{scenario}/{itemCount}/{tags...}`
  - `UrlTestConfig` parser for extracting configuration from URL
  - Well-known scenario IDs and modifier tags

- **ADDED** React integration for test configuration
  - `TestConfigProvider` - Context provider for URL-based configuration
  - `TestDataInitializer` - Component for initializing Redux state with test data
  - `useTestConfig()` hook for accessing configuration in components

- **ADDED** Combinatoric test scenario generation utilities
  - `generateCombinatoricScenarios()` for creating test permutations
  - `CombinatoricConfig` type for defining test dimensions
  - Pre-built scenario generators for common test patterns

## Impact

- Affected specs: `testing` (new), `api` (minor extension), `studio` (minor extension)
- Affected code:
  - `packages/api/src/testing/` - New testing module
  - `packages/api/src/mocks/` - Mock data loading and registry
  - `packages/studio/` - Mock control panel
  - `src/app/testing/` - Application-level test utilities
  - `src/app/main.tsx` - Conditional test provider wrapping
  - `src/screensets/*/mocks/` - JSON mock data files
- Breaking changes: None (additive feature, existing TS mocks continue to work)
- Dependencies: None (uses existing @hai3/api plugin architecture)
