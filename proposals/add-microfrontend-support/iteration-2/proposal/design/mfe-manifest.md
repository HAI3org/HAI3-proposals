# Design: MFE Manifest

This document covers the MfManifest type and its usage in the MFE system.

---

## Context

MfManifest is a standalone configuration type that contains Module Federation-specific settings for [loading](./mfe-loading.md) MFE bundles. While [MfeEntryMF](./mfe-entry-mf.md) defines the communication contract of an MFE, MfManifest provides the technical details needed to load and initialize the remote bundle (URL, container name, shared dependencies).

Multiple MfeEntryMF instances can reference the same MfManifest when they are exposed modules from the same federated container.

## Definition

**MfManifest**: A GTS type containing Module Federation 2.0 configuration - the remote entry URL, container name, shared dependency settings, and an optional list of entry type IDs for discovery.

---

## MF Manifest Schema (Standalone)

MfManifest is a **standalone type** containing Module Federation configuration.

```json
{
  "$id": "gts://gts.hai3.screensets.mfe.mf.v1~",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "x-gts-ref": "/$id",
      "$comment": "The GTS type ID for this instance"
    },
    "remoteEntry": {
      "type": "string",
      "format": "uri",
      "$comment": "URL to the remoteEntry.js file"
    },
    "remoteName": {
      "type": "string",
      "minLength": 1,
      "$comment": "Module Federation container name"
    },
    "sharedDependencies": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string", "$comment": "Package name (e.g., 'react', 'lodash')" },
          "requiredVersion": { "type": "string", "$comment": "Semver range (e.g., '^18.0.0')" },
          "singleton": {
            "type": "boolean",
            "default": false,
            "$comment": "If true, share single instance. Default false = code shared but instances isolated."
          }
        },
        "required": ["name", "requiredVersion"]
      },
      "$comment": "Dependencies to share for bundle optimization. singleton defaults to false (isolated instances)."
    },
    "entries": {
      "type": "array",
      "items": { "x-gts-ref": "gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~*" },
      "$comment": "Convenience field for discovery - lists MfeEntryMF type IDs"
    }
  },
  "required": ["id", "remoteEntry", "remoteName"]
}
```

## TypeScript Interface Definitions

```typescript
/**
 * Module Federation manifest containing shared configuration
 * GTS Type: gts.hai3.screensets.mfe.mf.v1~
 */
interface MfManifest {
  /** The GTS type ID for this manifest */
  id: string;
  /** URL to the remoteEntry.js file */
  remoteEntry: string;
  /** Module Federation container name */
  remoteName: string;
  /** Optional override for shared dependency configuration */
  sharedDependencies?: SharedDependencyConfig[];
  /** Convenience field for discovery - lists MfeEntryMF type IDs */
  entries?: string[];
}

/**
 * Configuration for a shared dependency in Module Federation.
 *
 * Module Federation shared dependencies provide TWO independent benefits:
 * 1. **Code/bundle sharing** - Download the code once, cache it (performance)
 * 2. **Runtime instance isolation** - Control whether instances are shared or isolated
 *
 * These benefits are NOT mutually exclusive! The `singleton` parameter controls
 * instance behavior while code sharing always provides the bundle optimization.
 *
 * - `singleton: false` (DEFAULT) = Code shared, instances ISOLATED per MFE
 * - `singleton: true` = Code shared, instance SHARED across all consumers
 *
 * HAI3 Recommendation:
 * - Use `singleton: false` (default) for anything with state (React, @hai3/*, GTS)
 * - Use `singleton: true` ONLY for truly stateless utilities (lodash, date-fns)
 */
interface SharedDependencyConfig {
  /** Package name (e.g., 'react', 'lodash', '@hai3/screensets') */
  name: string;
  /** Semver range (e.g., '^18.0.0', '^4.17.0') */
  requiredVersion: string;
  /**
   * Whether to share a single instance across all consumers.
   * Default: false (each consumer gets its own isolated instance)
   *
   * - false: Code is shared (cached), but each MFE gets its OWN instance
   * - true: Code is shared AND the same instance is used everywhere
   *
   * IMPORTANT: Only set to true for truly stateless utilities (lodash, date-fns).
   * Libraries with state (React, Redux, GTS, @hai3/*) should use false.
   */
  singleton?: boolean;
}
```

## Example MfManifest Instance

```typescript
const analyticsManifest: MfManifest = {
  id: 'gts.hai3.screensets.mfe.mf.v1~acme.analytics.mfe.manifest.v1',
  remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js',
  remoteName: 'acme_analytics',
  // sharedDependencies configures Module Federation code sharing.
  // Two benefits are controlled independently:
  // 1. Code sharing (always) - download once, cache it
  // 2. Instance sharing (singleton flag) - share instance or isolate
  sharedDependencies: [
    // React/ReactDOM: Code shared for bundle optimization, but singleton: false
    // ensures each MFE gets its own React instance (isolation preserved)
    { name: 'react', requiredVersion: '^18.0.0', singleton: false },
    { name: 'react-dom', requiredVersion: '^18.0.0', singleton: false },
    // Stateless utilities: singleton: true is safe (no state to isolate)
    { name: 'lodash', requiredVersion: '^4.17.0', singleton: true },
    { name: 'date-fns', requiredVersion: '^2.30.0', singleton: true },
    // @hai3/* packages: Must use singleton: false for runtime isolation
    // Or omit entirely if this MFE doesn't need to share code with host
    // { name: '@hai3/screensets', requiredVersion: '^1.0.0', singleton: false },
  ],
  entries: [
    'gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~acme.analytics.mfe.chart.v1',
    'gts.hai3.screensets.mfe.entry.v1~hai3.screensets.mfe.entry_mf.v1~acme.analytics.mfe.metrics.v1',
  ],
};
```
