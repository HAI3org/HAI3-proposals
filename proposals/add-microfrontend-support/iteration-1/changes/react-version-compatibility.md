# React Version Compatibility and Component Rendering

## Problem

The proposal states that loaded MFEs are "React components" but doesn't explain how version compatibility works when host and MFE use different React versions.

**From the proposal:**
```typescript
interface LoadedMfe {
  /** The loaded React component */
  component: React.ComponentType<MfeBridgeProps>;  // <- Implies direct rendering
}
```

**Recommended configuration (singleton: false):**
```typescript
// Host uses React 18
shared: {
  react: { singleton: false, requiredVersion: '^18.0.0' },
}

// MFE built with React 16
shared: {
  react: { singleton: false, requiredVersion: '^16.14.0' },
}
```

## The Incompatibility Issue

With `singleton: false`, each runtime gets its own React instance:
- Host: React 18.3.0 instance
- MFE: React 16.14.0 instance (if major version mismatch)

**This creates a problem:**

```typescript
// Host (React 18) cannot directly render MFE component (React 16)
function HostApp() {
  const [MfeComponent, setMfeComponent] = useState(null);

  useEffect(() => {
    loader.load(entry).then(({ component }) => {
      setMfeComponent(component);  // React 16 component
    });
  }, []);

  // Cannot render React 16 component in React 18 tree!
  // Different reconciler, different internal APIs, different hooks
  return <div>{MfeComponent && <MfeComponent bridge={bridge} />}</div>;
}
```

**Why it fails:**
- React 16 and React 18 have incompatible internal APIs
- Fiber reconciler is different
- Event system is different
- Hooks implementation is different
- Cannot mix components from different React versions in same tree

## How It Actually Works (Likely via Shadow DOM)

The proposal mentions Shadow DOM but doesn't explain the rendering mechanism:

```typescript
<ShadowDomContainer entryTypeId={...}>
  <MfeComponent bridge={bridge} />  // <- How is this rendered?
</ShadowDomContainer>
```

**Likely implementation:**
```typescript
// 1. Create shadow DOM boundary
const shadowRoot = container.attachShadow({ mode: 'open' });

// 2. MFE renders itself with its own React instance
// NOT by host rendering it in host's React tree
const mfe = await loader.load(entry);

// 3. MFE must have a mount() method, not be a React component
mfe.mount(shadowRoot, { bridge });  // <- MFE uses its React 16 to render

// Host's React 18 never touches MFE's React 16 code
```

## What's Missing in Specification

1. **LoadedMfe type is misleading**
   ```typescript
   // Current (wrong):
   interface LoadedMfe {
     component: React.ComponentType<MfeBridgeProps>;  // Not renderable by host
   }

   // Should be:
   interface LoadedMfe {
     mount: (container: HTMLElement, props: MfeBridgeProps) => void;
     unmount: (container: HTMLElement) => void;
   }
   ```

2. **No specification of what MFE must export**
   - Must export mount/unmount functions?
   - Or React component (and host handles mounting)?
   - How does version isolation actually work?

3. **No framework adapter pattern**
   - MFE says "React component" but could be Vue, Angular, etc.
   - How does host know how to mount?
   - How does MFE declare its framework?

## Comparison with Fragment System

**Fragment System explicitly handles this:**

```typescript
// Fragment declares framework via adapter
export default defineFragmentComponent('dashboard').plugins(
  fragmentReactPlugin(DashboardComponent),  // <- React adapter
);

// Or Vue
export default defineFragmentComponent('settings').plugins(
  fragmentVuePlugin(SettingsComponent),  // <- Vue adapter
);

// Adapter provides mount/unmount interface
interface FragmentAdapter {
  mount(container: HTMLElement, props: any): void;
  unmount(container: HTMLElement): void;
}

// fragmentReactPlugin implementation
class ReactAdapter implements FragmentAdapter {
  mount(container: HTMLElement, props: any) {
    // Uses Fragment's own React version
    const root = ReactDOM.createRoot(container);
    root.render(<Component {...props} />);
  }

  unmount(container: HTMLElement) {
    root.unmount();
  }
}
```

**Benefits:**
- Framework explicitly declared
- Adapter handles mounting with correct version
- Host doesn't need to know Fragment's framework
- Works with any React version, Vue version, etc.
- Clear mount/unmount interface

## Impact

**This affects:**
- Version compatibility (can host and MFE use different React versions?)
- Rendering mechanism (how does host actually render MFE?)
- Type safety (is LoadedMfe.component actually a React component?)
- Framework flexibility (how to support Vue, Angular, etc.?)

**Without clear specification:**
- Unclear if React version mismatches are supported
- Misleading type definition (component vs mount function)
- No guidance for MFE authors on what to export
- No framework adapter pattern for non-React MFEs

## Recommended Solution

**Proposal should specify:**
1. What MFE exposed modules must export (mount/unmount interface? React component?)
2. How host renders MFE (via mount function? via React.createElement?)
3. How React version compatibility is handled (enforce matching versions? allow isolation?)
4. Framework adapter pattern (if MFE can use non-React frameworks)
5. Shadow DOM integration (when/how is it used?)

## References

- Related proposal sections:
  - `design.md` - Decision 12: Module Federation (specifies singleton: false but not rendering)
  - `design.md` - Decision 13: Framework-Agnostic Isolation (says "any framework" but no adapter)
  - `specs/microfrontends/spec.md` - Shadow DOM React Component (shows usage but not mechanism)
