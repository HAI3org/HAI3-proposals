# Response: Missing Declarative Metadata

## Status: Addressed

## Summary

The request for extensible metadata in manifests (for routes, feature flags, translations, etc.) is addressed through the **GTS type system's extensibility** and the **MfManifest schema design**.

## Response

### Understanding the Request

The feedback clarified that this is about **declarative metadata for discovery** - allowing parent apps to discover MFE capabilities before executing JavaScript:

- Routes the MFE handles (for SSR preloading, parent router configuration)
- Feature flags required (for visibility, debugging, conditional loading)
- Translation files (for SSR prefetching)
- Capabilities metadata (domains, plugins)

### The Solution: GTS Type Extensibility

The proposal's GTS type system already supports this through **derived types**:

```typescript
// HAI3's base MfManifest (thin, stable)
// gts.hai3.screensets.mfe.mf.v1~
interface MfManifest {
  id: string;
  remoteEntry: string;
  remoteName: string;
  sharedDependencies?: SharedDependencyConfig[];
  entries?: string[];
}

// Company's extended MfManifest with metadata
// gts.hai3.screensets.mfe.mf.v1~acme.corp.mfe.manifest_extended.v1~
interface MfManifestAcme extends MfManifest {
  // Discovery metadata
  routes?: RouteDeclaration[];
  featureFlags?: string[];
  translations?: Record<string, string>;
  capabilities?: string[];

  // SSR hints
  ssrPreload?: {
    assets: string[];
    data: string[];
  };
}
```

### How It Works

**1. Define Extended Manifest Type**

Companies register their extended manifest schema with GTS:

```typescript
// Register extended manifest type
plugin.registerSchema({
  id: 'gts.hai3.screensets.mfe.mf.v1~acme.corp.mfe.manifest_extended.v1~',
  schema: {
    allOf: [
      { $ref: 'gts.hai3.screensets.mfe.mf.v1~' },  // Inherit base
      {
        properties: {
          routes: { type: 'array', items: { $ref: '#/definitions/RouteDeclaration' } },
          featureFlags: { type: 'array', items: { type: 'string' } },
          translations: { type: 'object', additionalProperties: { type: 'string' } }
        }
      }
    ]
  }
});
```

**2. Access Metadata Before Loading**

```typescript
// Fetch manifest metadata without loading MFE JavaScript
const manifest = await manifestFetcher.fetch(manifestTypeId);

// Access declarative metadata
const routes = (manifest as MfManifestAcme).routes;
const featureFlags = (manifest as MfManifestAcme).featureFlags;
const translations = (manifest as MfManifestAcme).translations;

// SSR: Prefetch translations
if (translations?.['en']) {
  await prefetch(translations['en']);
}

// Router: Register routes
if (routes) {
  parentRouter.registerMfeRoutes(manifest.id, routes);
}
```

**3. TypeInstanceProvider for Discovery**

The `TypeInstanceProvider` interface allows companies to implement their own manifest discovery:

```typescript
// Company's backend-driven provider
class BackendTypeInstanceProvider implements TypeInstanceProvider {
  async fetchManifests(): Promise<MfManifestAcme[]> {
    // Returns manifests with all metadata
    // Parent app can inspect before loading JavaScript
  }
}
```

### Why This Approach

| Aspect | Benefit |
|--------|---------|
| **No HAI3 opinion on metadata** | HAI3 doesn't prescribe what metadata to include |
| **Type-safe extension** | GTS schema inheritance ensures type safety |
| **Discovery without execution** | Manifests are JSON, no JS execution needed |
| **Company control** | Each company defines their metadata schema |

### Related Proposal Sections

- [type-system.md - Decision 5: Vendor Type Registration](../proposal/design/type-system.md)
- [mfe-manifest.md - MfManifest Type](../proposal/design/mfe-manifest.md)
- [mfe-loading.md - Decision 12: Manifest Fetching Strategy](../proposal/design/mfe-loading.md)

## Conclusion

The feedback is addressed through GTS type extensibility. Companies can extend `MfManifest` with any declarative metadata they need (routes, feature flags, translations, capabilities) without HAI3 prescribing the schema. The manifest is JSON, so discovery happens without JavaScript execution.
