# Response: Missing Dev Workflow and Dev Server Configuration

## Status: Out of Scope

## Summary

The feedback requests specification for dev server configuration, URL overrides, HMR, and proxy mode for local MFE development. These are valid developer experience concerns but are outside the scope of this architecture proposal.

## Why Out of Scope

This proposal defines the **runtime architecture** for MFE integration:
- Type system contracts (TypeSystemPlugin, GTS types)
- Runtime lifecycle (ScreensetsRegistry, MfeBridge)
- Communication patterns (actions, shared properties)
- Isolation model (Shadow DOM, singleton:false)

The feedback requests **development tooling**:
- Dev server configuration
- Hot Module Replacement (HMR)
- Proxy mode for local development
- URL overrides for loading local MFEs

| In Scope (This Proposal) | Out of Scope (Tooling) |
|--------------------------|------------------------|
| MfeEntryLifecycle interface | Dev server setup |
| MfManifest contract | HMR configuration |
| ScreensetsRegistry API | Proxy mode |
| TypeSystemPlugin interface | URL overrides |
| Module Federation shared config | Local development workflow |

## Existing Solutions

Module Federation + Vite/Webpack already provide dev server capabilities:
- `@originjs/vite-plugin-federation` supports HMR
- Webpack Dev Server works with Module Federation
- Environment variables can override `remoteEntry` URLs

The runtime contracts defined in this proposal (`MfeEntryLifecycle`, `MfeBridge`, etc.) work unchanged in both development and production environments.

## Future Work

Development tooling and workflow documentation can be addressed in a separate proposal or documentation effort. This would cover:
- Recommended dev server configuration
- Local MFE development patterns
- Testing strategies for MFE integration
- Debug tooling

## Conclusion

The feedback raises valid developer experience concerns, but they are tooling and workflow concerns rather than architectural concerns. This proposal focuses on defining the runtime contracts and interfaces. Development tooling can be built on top of these contracts and documented separately.
