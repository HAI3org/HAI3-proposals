# Feedback: Protocol Support (SSE/WebSocket)

## Decision

**V1 should scope to REST only**, but the design MUST be protocol-agnostic at its core to allow future extension.

## Issue

The proposal focuses on REST mocking but has REST-specific assumptions baked into core abstractions that would block future protocol extension.

## HAI3 Existing Pattern

HAI3 already uses **protocol-specific plugins** - this is correct:

| Protocol | Plugin Base | Hook | Short-Circuit Response |
|----------|-------------|------|------------------------|
| REST | `RestPluginWithConfig` | `onRequest(ctx)` | `{ status, headers, data }` |
| SSE | `SsePluginWithConfig` | `onConnect(ctx)` | `MockEventSource` |

REST returns a single response. SSE returns an event source that emits sequences. These are fundamentally different - separate plugins is the right approach.

## REST-Specific Assumptions in Proposal

| Assumption | Risk Level | Problem |
|------------|------------|---------|
| `TestScenarioPlugin extends RestPluginWithConfig` | **High** | Can't handle SSE streams |
| JSON schema: `"endpoint": "GET /path"` | **High** | HTTP method + path pattern |
| Response: `{ status: 200, data: [...] }` | **High** | HTTP response model |
| `mockMap` key format | **High** | `'METHOD /path'` is REST-only |

## Protocol Differences

```typescript
// REST: single request → single response
{
  "endpoint": "GET /api/sessions",
  "response": { "status": 200, "data": [...] }
}

// SSE: connection → stream of timed events
{
  "stream": "/api/chat/stream",
  "events": [
    { "delay": 0, "data": "{\"type\": \"connected\"}" },
    { "delay": 100, "data": "{\"delta\": \"Hello\"}" },
    { "delay": 200, "event": "done", "data": "" }
  ]
}

// WebSocket (future): bidirectional messages
{
  "connection": "/ws/chat",
  "inbound": [...],   // client → server
  "outbound": [...]   // server → client
}
```

## Recommendation: Protocol-Agnostic Core

### 1. Scenario Definition (Protocol-Agnostic)

```typescript
// Core scenario concept - protocol agnostic
interface TestScenario {
  id: string;
  description?: string;

  // Protocol-specific configurations
  rest?: RestScenarioConfig;      // V1: Implemented
  sse?: SseScenarioConfig;        // V2: Future
  websocket?: WsScenarioConfig;   // V3: Future
}

// REST-specific (V1)
interface RestScenarioConfig {
  responses: Record<string, RestMockResponse>;  // 'METHOD /path' → response
}

// SSE-specific (future)
interface SseScenarioConfig {
  streams: Record<string, SseMockEvent[]>;  // URL → event sequence
}
```

### 2. Protocol-Specific Plugins (Separate)

```typescript
// V1: REST only
export class TestScenarioRestPlugin extends RestPluginWithConfig<TestScenarioConfig> {
  static readonly [MOCK_PLUGIN] = true;

  async onRequest(ctx: RestRequestContext): Promise<...> {
    const scenario = this.getActiveScenario();
    const response = scenario?.rest?.responses[`${ctx.method} ${ctx.url}`];
    // ...
  }
}

// V2: SSE (future)
export class TestScenarioSsePlugin extends SsePluginWithConfig<TestScenarioConfig> {
  static readonly [MOCK_PLUGIN] = true;

  async onConnect(ctx: SseConnectContext): Promise<...> {
    const scenario = this.getActiveScenario();
    const events = scenario?.sse?.streams[ctx.url];
    // ...
  }
}
```

### 3. JSON Schema (Protocol-Aware)

```json
{
  "$schema": "https://hai3.dev/schemas/scenario.json",
  "id": "empty",
  "description": "Empty state for testing",

  "rest": {
    "GET /api/sessions": { "status": 200, "data": [] },
    "GET /api/messages/:id": { "status": 404 }
  },

  "sse": {
    "/api/chat/stream": {
      "events": []
    }
  }
}
```

### 4. URL Activation (Protocol-Agnostic)

URL `/_test/{screen}/{scenario}` activates a **scenario**, not protocol-specific behavior:

```
/_test/chat/empty
  → Activates "empty" scenario
  → REST plugin reads scenario.rest
  → SSE plugin reads scenario.sse (when implemented)
```

### 5. Framework Plugin (Protocol-Agnostic)

```typescript
// testing() plugin manages scenarios, not protocol details
export function testing(config?: TestingPluginConfig): HAI3Plugin {
  return {
    name: 'testing',
    dependencies: ['mock'],
    provides: {
      slices: [testingSlice],  // activeScenarios, overrides
      actions: {
        activateScenario,      // Protocol-agnostic
        deactivateScenario,    // Protocol-agnostic
        setEndpointOverride,   // Could be protocol-aware in V2
      },
    },
  };
}
```

## Required Changes for V1

### 1. Update design.md Non-Goals

```markdown
### Non-Goals
- Not mocking SSE or streaming protocols in V1 (future iteration)
- Not mocking WebSocket connections in V1
```

### 2. Update design.md with Protocol-Agnostic Architecture

Add decision documenting extensible design:

```markdown
### Decision: Protocol-Agnostic Scenario Model

Scenarios are defined with protocol-specific sections, allowing future extension:

- `scenario.rest` - REST request/response pairs (V1)
- `scenario.sse` - SSE event sequences (future)
- `scenario.websocket` - WebSocket message flows (future)

The `testing()` plugin and URL activation are protocol-agnostic.
Protocol-specific behavior is handled by separate plugins.
```

### 3. Rename Plugin

Change from `TestScenarioPlugin` to `TestScenarioRestPlugin` to make REST-specificity explicit.

### 4. Update JSON Schema

Structure as protocol-aware from the start:

```json
{
  "id": "empty",
  "rest": {
    "GET /api/sessions": { "status": 200, "data": [] }
  }
}
```

Not:

```json
{
  "endpoint": "GET /api/sessions",
  "response": { "status": 200, "data": [] }
}
```

### 5. Document Extension Path

Add to design.md:

```markdown
### Future: SSE Support (V2)

When SSE scenarios are needed:
1. Add `TestScenarioSsePlugin extends SsePluginWithConfig`
2. Extend scenario JSON schema with `sse` section
3. Both plugins read from same scenario state
4. URL activation works unchanged
```

## Summary

| Aspect | Current Proposal | Recommended |
|--------|------------------|-------------|
| Plugin name | `TestScenarioPlugin` | `TestScenarioRestPlugin` |
| JSON schema | REST-specific at root | Protocol sections (`rest`, `sse`) |
| Scenario type | Assumes REST | Protocol-agnostic with protocol sections |
| URL activation | Protocol-agnostic ✓ | Keep as-is |
| testing() plugin | Needs review | Ensure protocol-agnostic |

This ensures V1 is REST-only while the architecture supports future protocols without redesign.
