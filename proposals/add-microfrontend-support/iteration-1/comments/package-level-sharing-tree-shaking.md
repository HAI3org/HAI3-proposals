# Response: Package-Level Sharing / Tree-Shaking

## Status: Design Choice

## Summary

The feedback correctly identifies that Module Federation 2.0 shares entire packages rather than individual exports, which can impact bundle size. This is a known limitation that we accept for now, with the architecture designed to accommodate alternatives in the future if needed.

## The Limitation

Module Federation 2.0 shares at the package level:
- If an MFE uses `lodash/debounce`, the entire `lodash` package is shared
- This can result in larger bundles than optimal tree-shaking would produce

## Why We Accept This (For Now)

1. **MF 2.0 is battle-tested** - Provides reliable code sharing and isolation semantics
2. **Real-world impact is unproven** - This may not be a significant issue in practice
3. **Premature optimization** - Don't over-engineer for hypothetical problems

## Architecture Supports Future Alternatives

The GTS derived type system allows introducing alternative MFE entry types without breaking changes:

```
Base type:     gts.hai3.screensets.mfe.entry.v1~
                         │
                         ├── gts.hai3.screensets.mfe.entry.v1~hai3.mf2.*.v1~
                         │   └── Current: Module Federation 2.0 based
                         │
                         └── gts.hai3.screensets.mfe.entry.v1~hai3.esm.*.v1~
                             └── Future (if needed): ESM-based with tree-shaking
```

The runtime contracts remain unchanged:
- `MfeEntryLifecycle` interface (mount/unmount)
- `MfeBridge` for communication
- `ScreensetsRegistry` for registration

Only the loading mechanism would differ between entry types.

## Decision

If MF 2.0's tree-shaking limitation becomes a measurable real-world performance issue, a new derived entry type can be introduced. Until then, we proceed with the proven MF 2.0 approach.

## Conclusion

This is an intentional design choice: accept a known limitation of a battle-tested technology, while ensuring the architecture can evolve if that limitation proves problematic in practice.
