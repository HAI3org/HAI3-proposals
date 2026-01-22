# Design: Embedded Testing Framework

## Context
The project uses pytest + BDD + Playwright for testing (see `.ai/targets/TESTING.md`). Currently, tests are created manually by AI assistants following guidelines. This design introduces autonomous test generation and execution integrated into the OpenSpec workflow.

**Stakeholders**: AI assistants (Windsurf, Cursor, Claude Code), developers reviewing generated tests

## Goals / Non-Goals

**Goals:**
- Automate BDD test generation from OpenSpec proposals and screen implementations
- Ensure locator YAML files stay synchronized with React `data-testid` attributes
- Integrate test execution as a required gate before archiving changes
- Reduce manual effort while maintaining test quality

**Non-Goals:**
- Replace manual test authoring entirely (complex scenarios still need human review)
- Generate unit tests (focus is on E2E/BDD tests only)
- CI/CD integration (local execution only for now)

## Decisions

### Decision 1: Generator Architecture
**What**: Separate generators for each artifact type (Page Objects, Features, Steps, Tests)
**Why**: Modular design allows independent updates and easier debugging
**Alternatives**: Single monolithic generator - rejected for maintainability

### Decision 2: Locator Source of Truth
**What**: YAML files in `tests/locators/` are the source of truth, synced from React `data-testid`
**Why**: Decouples test infrastructure from React implementation details
**Alternatives**: Parse React directly - rejected due to complexity and build dependencies

### Decision 3: AI Workflow Trigger
**What**: Use `/generatetests` workflow command to trigger test generation
**Why**: Explicit trigger gives AI control over when to generate tests
**Alternatives**: Auto-generate on every screen change - rejected as too aggressive

### Decision 4: Test Execution Mode
**What**: Default to headed browser for initial run, headless for verification
**Why**: Visual feedback helps debug failures; headless is faster for CI-like runs
**Alternatives**: Always headless - rejected for debugging difficulty

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Generated tests may have flaky locators | Validator checks YAML against React source |
| Over-generation of trivial tests | AI reviews generated tests before committing |
| Application not running during test execution | Pre-flight check fails fast with clear error |

## Component Structure

```
tests/
├── generators/                    # NEW: Test generation engine
│   ├── __init__.py
│   ├── test_generator.py          # Main orchestrator
│   ├── page_object_generator.py   # Generates Page Objects
│   ├── feature_generator.py       # Generates .feature files
│   └── step_generator.py          # Generates step definitions
├── runner/                        # NEW: Test execution orchestrator
│   ├── __init__.py
│   └── test_runner.py             # Runs tests with reporting
├── utils/
│   ├── locator_extractor.py       # EXISTING
│   ├── locator_loader.py          # EXISTING
│   └── locator_validator.py       # NEW: Validates YAML vs React
```

## Generation Flow

```
1. AI triggers /generatetests for screen {screen_name}
   ↓
2. Validate locators: tests/locators/{screen}.yaml vs React data-testid
   ↓
3. Generate Page Object: tests/pages/{screen}_page.py
   ↓
4. Generate Feature: tests/features/{screen}.feature
   ↓
5. Generate Steps (if needed): tests/steps/{screen}_steps.py
   ↓
6. Generate Test Module: tests/features/test_{screen}.py
   ↓
7. Execute tests with --headed for visual verification
   ↓
8. Report results (pass/fail, screenshots on failure)
```

## Open Questions
- Should we support partial regeneration (e.g., only update feature file)?
- Should generated tests be marked with a comment indicating auto-generation?
