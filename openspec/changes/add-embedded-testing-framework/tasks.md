# Tasks: Add Embedded Testing Framework

## 1. Test Generation Engine
- [ ] 1.1 Create `tests/generators/` directory structure
- [ ] 1.2 Implement `test_generator.py` - parses OpenSpec proposals and generates BDD tests
- [ ] 1.3 Implement `page_object_generator.py` - generates Page Objects from screen source files
- [ ] 1.4 Implement `feature_generator.py` - generates Gherkin feature files from requirements
- [ ] 1.5 Implement `step_generator.py` - generates step definitions from scenarios

## 2. Locator Synchronization
- [ ] 2.1 Create `tests/utils/locator_validator.py` - validates YAML locators match React `data-testid` attributes
- [ ] 2.2 Add CLI command `python -m tests.utils.locator_validator --screen {screen}` for validation
- [ ] 2.3 Integrate locator validation into test generation workflow

## 3. Test Runner Integration
- [ ] 3.1 Create `tests/runner/` directory structure
- [ ] 3.2 Implement `test_runner.py` - orchestrates test execution with headed/headless modes
- [ ] 3.3 Add result reporting with pass/fail summary and screenshots on failure
- [ ] 3.4 Add pre-flight check for application availability at `http://localhost:5173`

## 4. AI Workflow Integration
- [ ] 4.1 Create `/generatetests` workflow in `.windsurf/workflows/generatetests.md`
- [ ] 4.2 Update `.ai/targets/TESTING.md` with autonomous generation section
- [ ] 4.3 Update `openspec/AGENTS.md` Stage 2 with test generation trigger
- [ ] 4.4 Update `openspec/AGENTS.md` Stage 3 with automated test execution gate

## 5. Documentation
- [ ] 5.1 Update `tests/README.md` with generator usage instructions
- [ ] 5.2 Add examples of generated test artifacts
