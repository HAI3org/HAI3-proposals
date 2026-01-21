# Iteration 1 Review Comments

## Review Status: BLOCK

The proposal has architectural merit but requires changes before implementation.

## Files

| File | Topic | Severity |
|------|-------|----------|
| [01-url-routing-format.md](./01-url-routing-format.md) | URL format should use prefix (`/_test/...`) | High |
| [02-package-placement.md](./02-package-placement.md) | Distribute across L1/L2/L3 layers | High |
| [03-event-driven-architecture.md](./03-event-driven-architecture.md) | MockController must use event bus | High |
| [04-priority-chain-complexity.md](./04-priority-chain-complexity.md) | Simplify 8-level priority to 3-4 | Medium |
| [05-protocol-support.md](./05-protocol-support.md) | Clarify REST-only scope for V1 | Low |
| [06-data-flow-architecture.md](./06-data-flow-architecture.md) | Remove TestDataInitializer | **Critical** |
| [07-solid-and-best-practices.md](./07-solid-and-best-practices.md) | SOLID analysis and best practices | Low |
| [08-plugin-architecture.md](./08-plugin-architecture.md) | Separate `testing()` plugin from `mock()` | High |
| [00-automated-review-original.md](./00-automated-review-original.md) | Original automated review | Reference |

## Summary of Required Changes

### Critical

1. **Remove `TestDataInitializer`** - Test data must flow through API layer, not directly to state

### High Priority

2. **Change URL format** to prefix (`/_test/{screen}/...`) for clear ownership boundaries
3. **Distribute across layers** - Follow HAI3 layer architecture:
   - `@hai3/api` (L1): TestScenarioPlugin, presets, MockDataLoader, FakerProcessor
   - `@hai3/framework` (L2): testing() plugin, URL parsing, effects
   - `@hai3/react` (L3): useTestConfig() hook (if needed)
4. **Create separate `testing()` plugin** - Do not merge into `mock()`:
   - `mock()` = infrastructure (toggle fake data on/off)
   - `testing()` = configuration (scenarios, URL routing, per-endpoint control)
   - `testing()` depends on `mock()`
5. **Convert MockController** to event-driven pattern:
   - Actions emit events (activateScenario, setEndpointOverride)
   - Effects listen and coordinate (testingEffects)
   - State via testingSlice (not class methods)
   - UI in `@hai3/studio` (TestingPanel component)

### Medium Priority

6. **Simplify priority chain** from 8 levels to 3 (industry standard):
   - Runtime overrides → Active scenario → Passthrough
   - URL params and localStorage are scenario selectors, not priority levels
   - Unify TS + JSON mocks at registration time

### Low Priority

7. **Ensure protocol-agnostic design** for future extension:
   - Rename `TestScenarioPlugin` → `TestScenarioRestPlugin`
   - JSON schema should use protocol sections (`rest`, `sse`) not REST-specific root
   - Scenario type should be protocol-agnostic with protocol-specific configs
   - Add Non-Goal: "Not mocking SSE/WebSocket in V1"
8. **Address ISP concern** - consider splitting `TestScenarioController` interface

## Key Architectural Decisions

### URL Format: Use Prefix

`/_test/{screen}/{scenario}` instead of `/{screen}/_test/{scenario}`

**Rationale**: HAI3 framework controls first path segment (screen ID). Screens control subsequent segments. Prefix format keeps test routing as framework concern with clear ownership boundary.

### Package Placement: Distribute Across Layers

Follow existing mock infrastructure pattern:
- Protocol plugins → `@hai3/api` (L1)
- Framework plugins → `@hai3/framework` (L2)
- React hooks → `@hai3/react` (L3)

**Rationale**: Maintains single import source principle. Users import from one layer only. Tree-shaking handles dev-only code exclusion. Do NOT create separate `@hai3/testing` package.

### Plugin Architecture: Separate mock() and testing()

```
┌─────────────────────────────────────┐
│  testing()                          │  ← Scenario configuration
│  - URL-based activation             │
│  - Scenario management              │
│  - Per-endpoint overrides           │
├─────────────────────────────────────┤
│  mock()                             │  ← Mock infrastructure
│  - Enable/disable fake data         │
│  - Plugin lifecycle                 │
└─────────────────────────────────────┘
```

**Rationale**: Different responsibilities (infrastructure vs configuration). Industry standard pattern. Respects HAI3's composable plugin model. Allows mock-only usage for simple development.

### Data Flow: Mock at API Level

Test scenarios should activate mock plugins, not inject data into state directly.

**Rationale**: Preserves event-driven data flow. Effects fire normally. Side effects (analytics, logging) work in test mode.

## What's Good

- Plugin-based approach extends existing infrastructure
- JSON mock files enable non-developer collaboration
- Development-only guards for tree-shaking
- Vertical slice ownership for mock data
- Faker templates for dynamic test data
- TestScenarioPlugin extending RestPluginWithConfig follows existing patterns

## Next Steps

Author should address high-priority items and resubmit for iteration-2 review.
