# Embedded Testing Framework

## ADDED Requirements

### Requirement: Test Generation Engine
The system SHALL provide a test generation engine that creates BDD test artifacts from screen implementations and OpenSpec proposals.

#### Scenario: Generate tests for new screen
- **WHEN** AI triggers `/generatetests` workflow for screen `{screen_name}`
- **THEN** system generates Page Object in `tests/pages/{screen}_page.py`
- **AND** system generates Feature file in `tests/features/{screen}.feature`
- **AND** system generates Step definitions in `tests/steps/{screen}_steps.py` (if needed)
- **AND** system generates Test module in `tests/features/test_{screen}.py`

#### Scenario: Generate tests with existing locators
- **WHEN** `tests/locators/{screen}.yaml` exists with valid locators
- **THEN** generated Page Object uses `LOCATORS_YAML` attribute
- **AND** generated Page Object uses `self.get_locator()` for element access

### Requirement: Locator Synchronization Validation
The system SHALL validate that YAML locator files are synchronized with React `data-testid` attributes.

#### Scenario: Validate locators match React source
- **WHEN** AI runs `python -m tests.utils.locator_validator --screen {screen}`
- **THEN** system compares `tests/locators/{screen}.yaml` with React component `data-testid` attributes
- **AND** system reports any missing, stale, or mismatched locators

#### Scenario: Validation fails on mismatch
- **WHEN** YAML contains testid not present in React source
- **THEN** system reports stale locator with file path and line number
- **AND** system exits with non-zero status

#### Scenario: Validation fails on missing locator
- **WHEN** React source contains `data-testid` not present in YAML
- **THEN** system reports missing locator with suggested YAML entry
- **AND** system exits with non-zero status

### Requirement: Test Runner Integration
The system SHALL provide a test runner that executes generated tests with configurable browser modes.

#### Scenario: Run tests with headed browser
- **WHEN** AI runs `python -m tests.runner.test_runner --screen {screen} --headed`
- **THEN** system launches visible browser
- **AND** system executes all tests in `tests/features/test_{screen}.py`
- **AND** system reports pass/fail summary

#### Scenario: Run tests headless
- **WHEN** AI runs `python -m tests.runner.test_runner --screen {screen}`
- **THEN** system executes tests without visible browser
- **AND** system captures screenshots on failure

#### Scenario: Pre-flight check fails
- **WHEN** application is not running at `http://localhost:5173`
- **THEN** system reports error "Application not available"
- **AND** system exits without running tests

### Requirement: AI Workflow Integration
The system SHALL integrate test generation and execution into the OpenSpec workflow via AI commands.

#### Scenario: Trigger test generation via workflow
- **WHEN** AI invokes `/generatetests` with screen name
- **THEN** system validates locators
- **AND** system generates test artifacts
- **AND** system executes tests with headed browser
- **AND** system reports results

#### Scenario: Test execution gate before archiving
- **WHEN** AI attempts to archive a change with associated screen tests
- **THEN** system MUST execute tests first
- **AND** system MUST pass all tests before archiving proceeds
