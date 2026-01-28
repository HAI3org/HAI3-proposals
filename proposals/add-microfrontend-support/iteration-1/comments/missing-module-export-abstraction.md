# Response: Missing Module Export Abstraction

## Status: Addressed in Updated Proposal

## Summary

The feedback correctly identified that the original proposal lacked a clear abstraction for what MFEs should export. This has been addressed with the introduction of the `MfeEntryLifecycle` interface.

## Changes Made

### New Interface: MfeEntryLifecycle

```typescript
/**
 * Lifecycle interface for MFE entries.
 * Defines lifecycle methods that any MFE entry must implement,
 * regardless of framework (React, Vue, Angular, Vanilla JS).
 */
interface MfeEntryLifecycle {
  mount(container: HTMLElement, bridge: MfeBridge): void;
  unmount(container: HTMLElement): void;
}
```

### Design Decisions

1. **Name Choice**: `MfeEntryLifecycle` was chosen because:
   - Focuses on lifecycle semantics (mount/unmount)
   - Extensible for future lifecycle methods (`onSuspend`, `onResume`, etc.)
   - Avoids implementation details like "Export" or "Module" in the name

2. **Framework Agnostic**: The interface works with any UI framework:
   - React: `ReactDOM.createRoot(container).render(<App bridge={bridge} />)`
   - Vue 3: `createApp(App, { bridge }).mount(container)`
   - Angular: `platformBrowserDynamic().bootstrapModule(...)`
   - Svelte: `new App({ target: container, props: { bridge } })`
   - Vanilla JS: Direct DOM manipulation

3. **Clear Contract**: MFE developers know exactly what to export - no ambiguity about component vs function vs object.

### Why Not Filesystem Conventions?

The feedback suggested filesystem conventions (like `*.component.tsx`, `*.method.ts`). We rejected this because:

1. **Over-engineering**: Adds complexity without clear benefit for our use case
2. **All entries are UI**: In our model, extensions mount into domains - they're all UI components
3. **Non-UI logic**: Handled through actions chain and `MfeBridge`, not separate "method" exports
4. **Build tool coupling**: Filesystem conventions require specific build tooling

### Updated Files

- `design/mfe-loading.md` - Added `MfeEntryLifecycle` interface definition
- `design/registry-runtime.md` - Framework-specific implementation examples
- `design/type-system.md` - Added interface as runtime contract (not GTS type)
- `specs/screensets/spec.md` - Added validation scenarios
- `specs/microfrontends/spec.md` - Updated container component

## Conclusion

The feedback was valid and has been fully addressed. The `MfeEntryLifecycle` interface provides a clear, framework-agnostic contract for MFE exports.
