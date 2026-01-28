# Response: MFE Extensibility

## Status: Partially Addressed (Design Choice)

## Summary

The request for a `createMfe().use(plugin)` pattern is addressed through an alternative architecture: **MfeBridge + React hooks** for framework integration, with extensibility via custom bridge factories.

## Response

### The Proposal's Approach

The proposal takes a different architectural path than the suggested `createMfe().use(mfeReact())` pattern:

1. **Framework-agnostic core**: `MfeEntryLifecycle` with `mount(container, bridge)` and `unmount(container)`
2. **React integration via hooks**: `useMfeBridge()`, `useSharedProperty()`, `useHostAction()`
3. **Extensibility via bridge factories**: Companies extend `MfeBridgeFactory` to inject services

### Why This Approach

The proposal prioritizes:

| Concern | `createMfe().use()` | Bridge + Hooks |
|---------|---------------------|----------------|
| Framework agnostic | Plugin per framework | Core is agnostic, hooks are framework-specific |
| Bundle size | Plugins add abstraction layer | Minimal overhead |
| Flexibility | Constrained by plugin API | Direct access to lifecycle |
| Learning curve | New abstraction to learn | Standard React patterns |

### What the Proposal Provides

**1. React Integration (L3 - @hai3/react)**

```typescript
// From specs/microfrontends/spec.md

function MyMfeComponent() {
  const bridge = useMfeBridge();
  const theme = useSharedProperty('theme');
  const loadPopup = useHostAction(HAI3_ACTION_LOAD_EXT);

  return <div style={{ background: theme.background }}>...</div>;
}
```

**2. MfeEntryLifecycle for Any Framework**

```typescript
// MFE entry point (framework-agnostic)
export const mount = (container: HTMLElement, bridge: MfeBridge) => {
  // React
  ReactDOM.createRoot(container).render(<App bridge={bridge} />);
  // Vue
  createApp(App, { bridge }).mount(container);
  // Svelte
  new App({ target: container, props: { bridge } });
  // Vanilla
  container.innerHTML = `<div>...</div>`;
};
```

**3. Extensibility via Custom Bridge Factories**

```typescript
// Company creates rich bridges with services
class MfeBridgeFactoryAcme extends MfeBridgeFactory<MfeBridgeAcme> {
  create(domainId, entryTypeId, instanceId): MfeBridgeAcme {
    return new MfeBridgeAcme(
      domainId, entryTypeId, instanceId,
      this.localization,  // Company's localization
      this.analytics,     // Company's analytics
      this.theming        // Company's theming
    );
  }
}
```

### What Is NOT Included (By Design)

The proposal does NOT include:
- A `createMfe()` factory abstraction
- A `.use(plugin)` chaining API
- Framework-specific plugin packages (`@hai3/mfe-react`, `@hai3/mfe-vue`)

**Rationale**: The `MfeEntryLifecycle` interface is simple enough (just `mount`/`unmount`) that a factory abstraction adds complexity without proportional benefit. MFE developers can use their framework's standard patterns.

### Future Consideration

If developer experience feedback indicates strong demand for a `createMfe().use()` pattern, it could be added as a **convenience layer** on top of the current architecture without changing the core design.

### Related Proposal Sections

- [mfe-api.md - MfeEntryLifecycle Interface](../proposal/design/mfe-api.md)
- [specs/microfrontends/spec.md - React Hooks](../proposal/specs/microfrontends/spec.md)
- [mfe-loading.md - MfeBridgeFactory](../proposal/design/mfe-loading.md)

## Conclusion

The proposal addresses the underlying needs (framework integration, consistent patterns, extensibility) through a different architecture. The `MfeEntryLifecycle` + React hooks approach provides a simpler, more direct developer experience. Company-specific concerns (localization, analytics, theming) are addressed via custom bridge factories rather than MFE-side plugins.
