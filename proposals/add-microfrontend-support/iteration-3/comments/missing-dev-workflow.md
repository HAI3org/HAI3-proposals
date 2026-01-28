# Response: Missing Dev Workflow

## Status: Acknowledged - Intentionally Out of Scope

## Summary

The request for dev workflow documentation (dev server, local testing, integration testing) is acknowledged as a valid concern but is intentionally out of scope for this proposal.

## Response

### Why Out of Scope

This proposal focuses on the **runtime architecture** for MFE support:
- Type system abstraction
- Loading and lifecycle management
- Bridge communication
- Domain and extension model
- Actions chain mediation

**Developer tooling** (dev servers, testing setups, debugging tools) is a separate concern that:
1. Depends on bundler choice (Vite, webpack, Rspack)
2. Varies by company toolchain
3. Has established patterns in the Module Federation ecosystem

### What the Proposal DOES Specify

The proposal specifies the **contracts** that tooling must satisfy:

| Contract | Specification |
|----------|--------------|
| MFE bundle format | Module Federation 2.0 remote entry |
| Exposed module interface | `MfeEntryLifecycle` with `mount`/`unmount` |
| Manifest format | `MfManifest` JSON structure |
| Bridge interface | `MfeBridge` for MFE-to-host communication |

Any dev tooling that produces artifacts conforming to these contracts will work.

### What Is Left to Implementation Phase

The following should be addressed during **implementation**, not in this architectural proposal:

**1. Dev Server Configuration**
```typescript
// Example Vite config for MFE development
// This is implementation guidance, not architectural specification
export default defineConfig({
  plugins: [
    federation({
      name: 'acme_analytics',
      filename: 'remoteEntry.js',
      exposes: {
        './Dashboard': './src/Dashboard.tsx',
      },
      shared: ['react', 'react-dom', '@hai3/screensets'],
    }),
  ],
});
```

**2. Local Testing Recommendations**
- Mock `MfeBridge` for isolated MFE testing
- Mock `ScreensetsRegistry` for integration testing
- Shadow DOM polyfill for JSDOM environments

**3. Integration Testing Setup**
- Host app test harness
- MFE contract validation
- Actions chain testing utilities

### Recommended Follow-Up

After this proposal is approved, a separate **Developer Tooling Guide** should be created covering:

1. **Vite/webpack configuration templates** for MFE development
2. **Mock implementations** for testing (`MockMfeBridge`, `MockScreensetsRegistry`)
3. **Example project structure** for MFE repositories
4. **CI/CD patterns** for MFE deployment
5. **Debugging guide** for actions chains and bridge communication

### Related Proposal Sections

- [mfe-loading.md - Decision 11: Module Federation 2.0](../proposal/design/mfe-loading.md) - Specifies the bundler integration point
- [mfe-api.md - MfeEntryLifecycle](../proposal/design/mfe-api.md) - Specifies what MFE bundles must export
- [mfe-manifest.md - MfManifest](../proposal/design/mfe-manifest.md) - Specifies the manifest format

## Conclusion

The feedback is valid - developers need tooling guidance. However, this proposal establishes the **architectural contracts** that tooling must satisfy. The actual tooling documentation should be created as a follow-up deliverable during implementation, once the contracts are finalized.

This separation ensures:
1. The architecture is not coupled to specific tooling choices
2. Tooling can evolve independently
3. Companies can use their preferred bundlers/dev servers
