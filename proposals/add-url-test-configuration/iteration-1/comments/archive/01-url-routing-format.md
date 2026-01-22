# Feedback: URL Routing Format

## Issue

The proposal uses **screen-first** URL format: `/{screen}/_test/{scenario}/{params}`

Example: `/chat/_test/empty/100`

## Concern: Ownership Boundary Ambiguity

HAI3 routing model:
- **Framework** controls the first path segment (screen ID)
- **Screen** controls all subsequent segments (internal routing)

```
URL: /chat/thread/123/messages
     └─┬─┘└────────┬─────────┘
   Framework     Screen
```

With screen-first format, `_test` sits in the **screen's domain**:

```
URL: /chat/_test/empty/100
     └─┬─┘└─────┬──────────┘
   Framework   Screen's segments
               ↑
               But _test is a framework concern
```

This creates ambiguity:
1. Framework must peek into screen's path segments to detect `_test`
2. Unclear what the screen receives - does it get `_test/empty/100` or is it stripped?
3. Screen must either be aware of `_test` convention or framework must modify screen's input

## Concern: Collision with Screen-Level Test Routes

Screens may want their own internal test routes:

```
/chat/thread/123          → Normal thread view
/chat/_test/mock-thread   → Screen's internal test view
```

With screen-first format: Is `/chat/_test/...` framework test mode or screen's internal route? Collision.

## Alternative: Prefix Format

`/_test/{screen}/{scenario}/{params}`

Example: `/_test/chat/empty/100`

```
URL: /_test/chat/empty/100
     └──┬─┘└─┬─┘└────┬────┘
    Framework Screen  Test config
```

**Benefits**:
- `_test` is first segment - clearly framework domain
- Screen never sees `_test` - clean boundary
- No collision with screen-level test routes
- Can be handled by separate `testing()` plugin without modifying `navigation()` plugin
- Entire `/_test` namespace excluded in production (not registered)

**Trade-offs**:
- URL reads as "test mode for chat" vs "chat in test mode"
- Browser history doesn't group test URLs with normal URLs
- Can't copy `/chat` portion of URL directly

## Recommendation

Use **prefix format** (`/_test/{screen}/...`) for clear ownership boundaries.

The proposal's rationale for screen-first format mentions "nested screen paths like `/settings/profile`" - but HAI3 doesn't have nested screens at framework level. Each screen handles its own nested routing internally.

## Required Changes

1. Update `design.md` Decision: URL-encoded Configuration to use prefix format
2. Update `spec.md` URL format requirements
3. Update `tasks.md` section 2 (URL parsing functions)
4. Remove references to "nested screen paths" as framework routing concern
