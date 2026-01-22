# Change: Add Embedded Testing Framework

## Why
Currently, BDD tests are created manually following `.ai/targets/TESTING.md` guidelines. This proposal introduces an embedded testing framework that autonomously generates and executes pytest + BDD + Playwright tests based on new or updated feature requirements, reducing manual effort and ensuring consistent test coverage.

## What Changes
- Add test generation engine that reads OpenSpec proposals and creates BDD tests automatically
- Add test runner integration that executes generated tests as part of the proposal workflow
- Add locator synchronization validation to ensure `data-testid` attributes are synced to YAML
- Integrate test generation into Stage 2 (Implementation) of OpenSpec workflow
- Integrate test execution into Stage 3 (Archiving) as a required gate

## Impact
- Affected specs: New `embedded-testing` capability
- Affected code:
  - `tests/` - New generator utilities and enhanced infrastructure
  - `.ai/targets/TESTING.md` - Updated with autonomous generation workflow
  - `openspec/AGENTS.md` - Updated Stage 2/3 with test automation steps
