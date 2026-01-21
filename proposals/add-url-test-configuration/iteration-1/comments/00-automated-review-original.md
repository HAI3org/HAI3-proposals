# OPENSPEC REVIEW: add-url-test-configuration

## DECISION: BLOCK

---

## BLOCKERS

| # | Section | Blocker Description | Required Resolution |
|---|---------|---------------------|---------------------|
| 1 | tasks.md / spec.md | **Layer violation**: Tasks 3.1-3.9 place React integration (`TestConfigProvider`, `useTestConfig()`) in `@hai3/api` or unclear location. Per `project.md`, React components/hooks belong in `@hai3/react` (L3), not `@hai3/api` (L1). | Move React integration (Section 3: tasks 3.1-3.9) explicitly to `@hai3/react` package. Update spec.md to clarify package location. |
| 2 | spec.md | **Missing layer propagation**: Proposal adds `TestScenarioPlugin` to `@hai3/api` (L1 SDK) but does not specify how this propagates to `@hai3/framework` (L2) and `@hai3/react` (L3) re-exports. Per `project.md` lines 38-43 and 244-262, SDK exports must be re-exported through the layer chain. | Add explicit tasks for re-exporting `TestScenarioPlugin` and related types through `@hai3/framework` and `@hai3/react` package indexes. |
| 3 | design.md / spec.md | **Ambiguous mock source priority**: The priority chain (design.md lines 336-346) lists 8 levels including both `MockController` and URL parameters, but the spec does not clarify how `MockController` interacts with the existing `RestMockPlugin` and `isMockPlugin` framework infrastructure. | Clarify relationship between `MockController`, `TestScenarioPlugin`, and existing `RestMockPlugin`. Specify whether they compose or replace. |
| 4 | tasks.md | **Missing ESLint consideration**: Tasks 7.5-7.7 introduce a "lightweight faker implementation" without addressing whether new dependencies or lint rules are affected. Per GUIDELINES.md line 88, `eslint-disable` comments are blocklisted. | Confirm faker implementation requires no ESLint exceptions. If external faker dependency is used, document it explicitly. |
| 5 | spec.md | **Incomplete type exports**: Spec requires `TestScenarioPlugin`, `TestScenario`, `TestScenarioResponse` etc. to be exported from `@hai3/api` main entry, but does not specify the export structure or whether conditional exports for tree-shaking are needed. | Add specific export requirements matching existing `@hai3/api/src/index.ts` patterns (lines 13-84 show the structure). |

---

## INTENT ALIGNMENT CHECK

| Stated Goal | Proposal Implementation | Verdict |
|-------------|------------------------|---------|
| Parallel E2E test execution with different mock states | URL-based configuration encodes state in URL, allowing multiple browser instances | ALIGNED |
| UI-first development workflow | Granular MockController allows toggling individual endpoints | ALIGNED |
| Human-readable mock data | JSON mock files with schema, variants, and faker templates | ALIGNED |
| Complementary to existing TS mocks (not replacing) | TypeScript mocks take precedence over JSON mocks per priority chain | ALIGNED |
| Tree-shakeable in production | `import.meta.env.DEV` guards proposed, but implementation details incomplete | PARTIAL - needs explicit tree-shaking verification tasks |

---

## SOLID COMPLIANCE REPORT

| Principle | Verdict | Findings | Required Edits (if RISK/FAIL) |
|-----------|---------|----------|-------------------------------|
| SRP | PASS | `TestScenarioPlugin` handles scenario-based mocking. `MockController` handles endpoint toggling. `MockDataLoader` handles JSON loading. Clear separation. | N/A |
| OCP | PASS | Extends existing `RestPluginWithConfig` pattern. New plugin type without modifying existing `RestMockPlugin`. Scenarios registered via registry, not hardcoded. | N/A |
| LSP | PASS | `TestScenarioPlugin extends RestPluginWithConfig<T>` follows existing plugin contract. No behavioral violations detected. | N/A |
| ISP | RISK | `TestScenarioController` interface exposes `activateScenario`, `deactivateScenario`, `setResponse`, `clearResponse`, `reset`. Consider splitting into `ScenarioActivation` and `EndpointOverride` interfaces. | Consider splitting `TestScenarioController` into smaller interfaces if consumers only need subset of functionality. |
| DIP | PASS | High-level `TestConfigProvider` depends on abstract `TestScenarioController` interface, not concrete `TestScenarioPlugin`. Mock resolution follows abstraction-based priority chain. | N/A |

---

## BEST PRACTICES FINDINGS

### Commendations

1. **URL-based state encoding** - Excellent approach for E2E test isolation. Follows industry best practice for parallel test execution (similar to Playwright's `baseURL` pattern).

2. **Plugin composition over inheritance** - `TestScenarioPlugin` extends existing plugin infrastructure rather than creating parallel systems.

3. **Layered priority resolution** - Clear 8-tier priority chain prevents ambiguity in mock resolution.

4. **Faker template syntax** - `{{faker.*}}` syntax is human-readable and allows dynamic data without code changes.

5. **Development-only guards** - Using `import.meta.env.DEV` for tree-shaking aligns with HAI3 existing patterns.

6. **Vertical slice ownership** - JSON mocks in `src/screensets/{name}/mocks/` follows HAI3's vertical slice architecture.

### Concerns

| Finding | Best Practice Reference | Recommended Proposal Change |
|---------|------------------------|-----------------------------|
| **Singleton MockController** (task 8.5) | HAI3 uses registry pattern with self-registration, not singletons for core functionality. | Consider making `MockController` a class that can be instantiated via registry or plugin pattern. |
| **localStorage persistence** for mock state | Implicit state persistence can cause test flakiness. | Add explicit documentation that E2E tests should use URL params exclusively; localStorage is for developer convenience only. |
| **Missing validation for JSON mock schema** | Task 7.4 mentions validation but no error handling strategy. | Add error handling requirements: what happens when JSON mock fails schema validation? Silent skip or throw? |
| **`$generate` directive introduces DSL** | Custom DSLs increase learning curve. | Document the DSL clearly. Consider limiting to faker-only without custom directives as V1. |
| **89 tests specified** (task 11.5) | Test count is unusual specification; requirements should be behavior-based. | Replace "89 tests" with specific test coverage requirements (e.g., "100% branch coverage for URL parsing"). |

---

## LINTING POLICY ASSESSMENT

- ESLint modifications explicitly permitted: **NO**
- Violations found:
  - Task 7.7 "Create lightweight faker implementation" may require non-trivial code that could trigger complexity warnings
  - No explicit confirmation that faker templates (`{{faker.*}}`) parsing avoids `eval()` or dynamic code execution (which may violate security linting rules)

**Recommendation**: Add explicit task to verify faker implementation passes all existing ESLint rules without exceptions.

---

## LAYER PROPAGATION CHECK

- Affected package(s): `@hai3/api` (L1), `@hai3/react` (L3 - implied), `@hai3/studio` (UI layer)
- Layer hierarchy verified against `openspec/project.md`: **NO**
- Propagation issues:
  1. **L1 to L2**: No task specifies re-exporting testing module from `@hai3/framework`
  2. **L2 to L3**: No task specifies re-exporting from `@hai3/react`
  3. **React components placement**: Tasks 3.x mention React components but don't specify which package they belong to
  4. **Studio integration** (tasks 9.x): Correctly targets `@hai3/studio` package

**Required additions to tasks.md**:
- Add task: "Re-export testing module types and classes from `@hai3/framework` index"
- Add task: "Re-export testing utilities from `@hai3/react` index for convenience"
- Clarify task 3.x: Explicitly state React components go in `@hai3/react` or `src/app/testing/`

---

## ADDITIONAL OBSERVATIONS

1. **Consistency with existing mock infrastructure**: The proposal should explicitly state how `TestScenarioPlugin` relates to existing `RestMockPlugin`. Currently, HAI3 has:
   - `RestMockPlugin` with `MOCK_PLUGIN` symbol marker
   - `toggleMockMode()` action that enables/disables all mock plugins

   The new `TestScenarioPlugin` should either:
   - Also use `MOCK_PLUGIN` symbol and integrate with `toggleMockMode()`
   - Or explicitly state it operates independently

2. **HAI3 Studio mock panel location**: Task 9.5 mentions "Integrate panel with ControlPanel in Studio" - the current `ControlPanel.tsx` already has `ApiModeToggle`. Consider whether the new MockControlPanel should replace or augment this.

3. **Documentation gap**: Design.md mentions `cyberChat` screenset for examples, but HAI3 codebase shows `_blank` and `demo` screensets. Recommend using existing screenset names or noting this is a new screenset to be created.

4. **Event-driven architecture**: HAI3 requires all state changes to go through event bus. Consider whether `MockController` state changes should emit events for consistency with the rest of the framework.

5. **Type safety for faker templates**: The `{{faker.*}}` string interpolation loses TypeScript type safety. Consider providing typed factory alternatives alongside JSON templates for complex scenarios.

---

## Summary

The proposal is architecturally sound and follows most HAI3 patterns correctly. The primary blockers are missing layer propagation specifications and unclear package boundaries for React components. Once these are addressed, the proposal should be ready for implementation.
