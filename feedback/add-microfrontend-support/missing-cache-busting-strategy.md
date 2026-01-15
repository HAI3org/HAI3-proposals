# Missing Cache Busting Strategy for remoteEntry

## Problem

The `MfManifest` type specifies `remoteEntry` as a plain URL without content hash or version parameter:

```typescript
interface MfManifest {
  id: string;
  remoteEntry: string;  // e.g., 'https://cdn.acme.com/analytics/remoteEntry.js'
  remoteName: string;
  sharedDependencies?: SharedDependencyConfig[];
  entries?: string[];
}
```

**Issue:** When MFE code changes (bug fixes, new features, updates), the `remoteEntry` URL remains the same, leading to browser caching problems.

## Scenario: Bug Fix Deployment

```
Day 1: Deploy analytics MFE v1.0.0
  -> remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js'
  -> Browser caches this file

Day 2: Fix critical bug, deploy v1.0.1
  -> remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js' (SAME URL!)
  -> Browser serves cached v1.0.0
  -> Users don't get the fix
```

## Root Cause

**Deployment versioning is completely separate from GTS type versioning:**

- GTS version (`v1~`, `v2~`) tracks **contract/schema changes**
- Deployment version (1.0.0 -> 1.0.1) tracks **implementation changes**

You can have 100 deployments of `gts.acme.analytics.mfe.mf.v1~` without changing the GTS type version, and none of them have automatic cache busting.

## Standard Solutions (Not in Proposal)

### Option 1: Content Hash in URL
```typescript
// Build output generates hash
remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.a3f5b9c2.js'

// After code changes
remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.d8e2c147.js' // Different URL!
```

**Benefits:**
- Different URL = No cache collision
- Can use aggressive caching (`Cache-Control: immutable, max-age=31536000`)
- Standard webpack/vite output with `[contenthash]`

### Option 2: Query String Version
```typescript
remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js?v=1.0.1'
```

**Benefits:**
- Simple to implement
- Less reliable (some proxies ignore query params)

### Option 3: Version in Path
```typescript
remoteEntry: 'https://cdn.acme.com/analytics/v1.0.1/remoteEntry.js'
```

**Benefits:**
- Clean URLs
- CDN-friendly

**Drawbacks:**
- Prevents chunk-level sharing between versions (similar to tree-shaking problem)
- Each version deploys to a separate directory, so identical chunks from different versions cannot be deduplicated by the browser cache
- Example: If `v1.0.1/chunk-lodash.abc123.js` and `v1.0.2/chunk-lodash.abc123.js` contain identical code, the browser downloads both because paths differ

## Additional Missing Pieces

The proposal doesn't specify:

1. **Manifest Distribution Strategy**
   - How do clients get the updated manifest with new `remoteEntry` URL?
   - Is manifest fetched from API? What caching?
   - Is manifest bundled? (Defeats independent deployment)

2. **Manifest Caching**
   ```typescript
   // UrlManifestFetcher has fetchOptions but no guidance
   class UrlManifestFetcher {
     constructor(
       private readonly urlResolver: (manifestTypeId: string) => string,
       private readonly fetchOptions?: RequestInit  // What cache headers?
     ) {}
   }
   ```

3. **HTTP Cache Headers Guidance**
   - No recommendation for `Cache-Control` headers
   - No guidance on ETags
   - No mention of immutable assets

## Impact

**This affects:**
- Bug fix deployments
- Security patches
- Performance improvements
- Any code change that doesn't modify the contract

**Without cache busting:**
- Users may get stale code for hours/days
- Must use aggressive cache invalidation (`no-cache`) = slower loads
- OR accept delayed updates

## Recommended Solution

Add deployment versioning to `MfManifest`:

```typescript
interface MfManifest {
  id: string;                          // GTS type ID (contract version)
  remoteEntry: string;                 // Should include content hash
  remoteName: string;

  // NEW: Deployment metadata
  deploymentVersion?: string;          // Semantic version (e.g., "1.2.3")
  buildHash?: string;                  // Content hash (e.g., "a3f5b9c2")
  buildTimestamp?: number;             // Unix timestamp of build

  sharedDependencies?: SharedDependencyConfig[];
  entries?: string[];
}
```

**And specify:**
1. `remoteEntry` SHOULD include content hash or version parameter
2. Manifest fetch strategy and caching policy
3. Recommended HTTP cache headers:
   - `remoteEntry.js`: `Cache-Control: public, max-age=31536000, immutable`
   - Manifest JSON: `Cache-Control: public, max-age=300` (5 minutes)
4. How clients discover manifest updates

## References

- Module Federation standard practice: Use `[contenthash]` in filename
- Related proposal sections:
  - Missing Declarative Metadata (manifest distribution related)
  - `design.md` - Decision 2: GTS Type ID Format (only covers contract versioning)
  - `design.md` - Decision 18: Manifest Fetching Strategy (doesn't address caching)
  - `specs/microfrontends/spec.md` - Requirement: MFE Version Validation (only shared dependencies)
