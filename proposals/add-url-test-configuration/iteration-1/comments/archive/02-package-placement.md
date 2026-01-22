# Feedback: Package Placement and Layer Architecture

## Issue

The proposal places components across packages without clear alignment to HAI3's layer architecture, and doesn't specify where React components should live.

## HAI3 Layer Model

```
@hai3/react (L3)
  ├── Own: HAI3Provider, useNavigation(), useTheme(), hooks
  └── Re-exports: EVERYTHING from @hai3/framework

@hai3/framework (L2)
  ├── Own: plugins, presets, effects, slices, URL/routing utilities
  └── Re-exports: EVERYTHING from L1 packages

@hai3/api, @hai3/state, @hai3/screensets, @hai3/i18n (L1)
  └── Own: Zero @hai3 dependencies
```

**Key principles:**
- Each layer fully covers the layer below via re-exports
- Users pick ONE layer and import everything from that layer
- No mixing imports from different layers

## Proposal's Current State

The proposal doesn't clearly specify package locations. Some components are mentioned for `@hai3/api`, but React components and URL utilities have no explicit location.

## Recommendation: Distribute Across Existing Packages

Following the established pattern (how mock infrastructure is distributed), testing functionality should be distributed across existing packages:

### Proposed Distribution

```
@hai3/api (L1)
├── src/testing/
│   ├── TestScenarioPlugin.ts      # Extends RestPluginWithConfig
│   ├── TestScenarioPresets.ts     # SERVER_ERROR, SLOW_NETWORK, etc.
│   ├── types.ts                   # TestScenario, TestScenarioResponse
│   └── index.ts
├── src/mocks/
│   ├── MockDataLoader.ts          # Loads JSON mock files
│   ├── FakerProcessor.ts          # {{faker.*}} template processing
│   └── types.ts                   # MockFileSchema, etc.
└── src/index.ts                   # Exports testing module

@hai3/framework (L2)
├── src/plugins/
│   └── testing.ts                 # testing() plugin
├── src/effects/
│   └── testingEffects.ts          # Event handlers for test scenarios
├── src/utils/
│   └── testUrl.ts                 # isTestRoute(), parseTestUrl(), buildTestUrl()
└── src/index.ts                   # Re-exports testing + own utilities

@hai3/react (L3)
├── src/hooks/
│   └── useTestConfig.ts           # If React-specific hook needed
└── src/index.ts                   # Re-exports from framework
```

### Why This Distribution

| Component | Layer | Rationale |
|-----------|-------|-----------|
| `TestScenarioPlugin` | L1 (`@hai3/api`) | Protocol plugin like `RestMockPlugin`, no @hai3 deps |
| `TestScenarioPresets` | L1 (`@hai3/api`) | Constants, no deps |
| `MockDataLoader` | L1 (`@hai3/api`) | Loads data for plugins |
| `FakerProcessor` | L1 (`@hai3/api`) | Template processing, no deps |
| `testing()` plugin | L2 (`@hai3/framework`) | Framework plugin like `mock()` |
| URL parsing utilities | L2 (`@hai3/framework`) | Routing is framework concern |
| Test effects | L2 (`@hai3/framework`) | Event bus + effects pattern |
| `useTestConfig()` | L3 (`@hai3/react`) | React hook (if needed) |

### Why NOT a Separate `@hai3/testing` Package

| Argument For Separate | Counter-Argument |
|-----------------------|------------------|
| "All testing in one place" | Discoverability via docs, not package structure |
| "Optional dependency" | Tree-shaking with `import.meta.env.DEV` achieves same result |
| "Clear boundary" | Boundary is "dev-only", not "separate package" |
| "Easier to exclude" | Apps rarely exclude - they just don't use it |

A separate package would also:
- Add package versioning/publishing overhead
- Potentially break "single import source" principle
- Not follow established patterns (mock infrastructure is distributed)

### Follows Existing Patterns

Current mock infrastructure distribution:

| Component | Package | Layer |
|-----------|---------|-------|
| `RestMockPlugin` | `@hai3/api` | L1 |
| `SseMockPlugin` | `@hai3/api` | L1 |
| `mock()` plugin | `@hai3/framework` | L2 |
| `toggleMockMode()` | `@hai3/framework` | L2 |

Testing is an extension of mocking. Same pattern applies.

## Required Changes to Proposal

### 1. Update `design.md`

Add a section specifying package distribution:

```markdown
### Decision: Package Distribution

Testing functionality is distributed across HAI3 layers following the mock infrastructure pattern:

- **@hai3/api (L1)**: TestScenarioPlugin, TestScenarioPresets, MockDataLoader, FakerProcessor
- **@hai3/framework (L2)**: testing() plugin, URL parsing, testingEffects
- **@hai3/react (L3)**: useTestConfig() hook (if React-specific behavior needed)

Each layer re-exports from the layer below, maintaining the single import source principle.
```

### 2. Update `tasks.md`

Reorganize tasks by package:

```markdown
## @hai3/api Tasks (L1)

### Testing Module
- [ ] Create TestScenarioPlugin extending RestPluginWithConfig
- [ ] Create TestScenarioPresets constants
- [ ] Create TestScenario and TestScenarioResponse types
- [ ] Export testing module from package index

### Mock Data Loading
- [ ] Create MockDataLoader for JSON mock files
- [ ] Create FakerProcessor for {{faker.*}} templates
- [ ] Create mock file schema types
- [ ] Export mock utilities from package index

## @hai3/framework Tasks (L2)

### Testing Plugin
- [ ] Create testing() plugin with dependencies on mock, routing
- [ ] Create testingEffects for event handling
- [ ] Create URL parsing utilities (isTestRoute, parseTestUrl, buildTestUrl)
- [ ] Re-export @hai3/api testing module
- [ ] Export testing plugin and utilities from package index

## @hai3/react Tasks (L3)

### React Integration
- [ ] Create useTestConfig() hook if React-specific behavior needed
- [ ] Re-export testing from @hai3/framework
```

### 3. Update `spec.md`

Update the "API Package Testing Exports" requirement to reflect the full distribution:

```markdown
### Requirement: Testing Infrastructure Distribution

Testing infrastructure SHALL be distributed across HAI3 layers:

#### @hai3/api exports (L1)
- `TestScenarioPlugin` class
- `TestScenarioPresets` object
- `MockDataLoader` class
- `FakerProcessor` class
- All related types

#### @hai3/framework exports (L2)
- `testing()` plugin function
- `isTestRoute()` utility
- `parseTestUrl()` utility
- `buildTestUrl()` utility
- Re-exports all @hai3/api testing exports

#### @hai3/react exports (L3)
- `useTestConfig()` hook (if applicable)
- Re-exports all @hai3/framework testing exports
```

## Implementation Example

```typescript
// User code - React app
import {
  HAI3Provider,
  createHAI3,
  testing,              // From framework, re-exported by react
  TestScenarioPlugin,   // From api → framework → react
  isTestRoute,          // From framework → react
} from '@hai3/react';

const app = createHAI3()
  .use(testing())  // Enables test route handling
  .build();
```

Single import source maintained. Layer architecture respected.
