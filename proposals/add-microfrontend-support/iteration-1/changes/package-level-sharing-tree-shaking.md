# Module Federation: Package-Level Sharing Prevents Tree-Shaking

## Problem

Module Federation's `shared` configuration operates at the **package level**, not the module/function level. This means when you share a library, you must share the **entire package**, even if each MFE only uses a small subset of its functions.

**From the proposal (Decision 12):**
```javascript
shared: {
  'lodash': { singleton: true, requiredVersion: '^4.17.0' },
  'date-fns': { singleton: true, requiredVersion: '^2.30.0' },
}
```

## The Tree-Shaking Problem

**Module Federation cannot do chunk-level sharing:**

```javascript
// MFE A: only needs format()
import { format } from 'date-fns';

// MFE B: only needs parse()
import { parse } from 'date-fns';

// Both MFEs declare:
shared: {
  'date-fns': { singleton: true, requiredVersion: '^2.30.0' }
}

// What happens:
// 1. Host loads -> Downloads ENTIRE date-fns package (~120KB gzipped)
// 2. MFE A needs format() -> Uses host's date-fns (entire package!)
// 3. MFE B needs parse() -> Uses host's date-fns (entire package!)

// Total downloads: ~120KB gzipped (~500KB uncompressed)
// Actually needed: ~20KB (just format + parse functions)
// Waste: ~100KB (500% overhead!)
```

**Why this happens:**
1. `shared` config works on package names (`'date-fns'`), not individual exports (`'date-fns/format'`)
2. Module Federation resolves dependencies at runtime by package name
3. No metadata about what's actually used within the package
4. Container API exposes whole packages, not individual modules

## Comparison with Standard Build (Fragment System)

**Without Module Federation, standard Vite/Webpack builds with tree-shaking:**

```javascript
// Fragment A: only needs format()
import { format } from 'date-fns';

// Fragment B: only needs parse()
import { parse } from 'date-fns';

// Vite build output:
// Fragment A -> chunk-datefns-format.abc123.js (~10KB, only format)
// Fragment B -> chunk-datefns-parse.def456.js (~10KB, only parse)

// Deploy to same directory:
// s3://cdn/fragments/chunk-datefns-format.abc123.js
// s3://cdn/fragments/chunk-datefns-parse.def456.js

// Browser behavior:
// 1. Load Fragment A -> download chunk-datefns-format.abc123.js (~10KB)
// 2. Load Fragment B -> download chunk-datefns-parse.def456.js (~10KB)

// Total downloads: ~20KB (only what's actually needed!)
// Waste: 0KB
```

**Benefits of standard build:**
- Tree-shaking works naturally
- Only bundle what's imported
- Chunks shared via content hash (same code = same hash = cached)
- No package-level bloat

## Real-World Impact

**lodash:**
```
Full package: ~70KB gzipped (~530KB uncompressed)
Typical usage (3-4 functions): ~3KB gzipped (~10KB uncompressed)

With Module Federation shared:
- Downloads: 70KB gzipped
- Waste: 67KB (96% overhead!)
```

**date-fns:**
```
Full package: ~120KB gzipped (~500KB uncompressed)
Typical usage (format + parse): ~10KB gzipped (~40KB uncompressed)

With Module Federation shared:
- Downloads: 120KB gzipped
- Waste: 110KB (92% overhead!)
```

**Scenario: 5 MFEs each using 3-4 lodash functions:**
```
Standard build (Fragment System):
- Each MFE bundles only what it needs: ~3KB each
- Shared chunks (same functions): cached via content hash
- Total: ~15KB

Module Federation (MFE System):
- Host provides entire lodash: ~70KB
- All MFEs use host's lodash (entire package)
- Total: ~70KB
- Waste: ~55KB (367% overhead!)
```

## Why Module Federation Cannot Fix This

**Fundamental limitations:**

1. **Package-level resolution** - Module Federation's sharing mechanism works on package names, not individual exports
2. **Runtime negotiation** - Versions are negotiated per package at runtime, not per module
3. **Container API** - Module Federation containers expose whole packages
4. **No tree-shaking metadata** - No information about what's actually used within a package

**Cannot do this (even though it would solve the problem):**
```javascript
// Hypothetical granular sharing - NOT SUPPORTED
shared: {
  'date-fns/format': { ... },     // Can't share subpaths
  'date-fns/parse': { ... },      // Can't share individual functions
  'lodash/debounce': { ... },     // Can't share at function level
}
```

## Coordination Overhead

Because sharing is package-level, teams must coordinate on which packages to share:

```
Day 1: Host and MFE A both use lodash
  -> Add to shared config: lodash shared

Day 10: MFE B adds date-fns (host doesn't use it)
  -> MFE B bundles entire date-fns in separate chunk (~120KB)
  -> Not in host's shared config -> no sharing

Day 20: MFE C also adds date-fns
  -> If MFE C lists in shared BUT host doesn't:
    - date-fns bundled in MFE B (~120KB)
    - date-fns shared for MFE C (~120KB)
    - Downloaded TWICE! (~240KB total)

Day 30: Realize coordination problem
  -> Update host's shared config to include date-fns
  -> Redeploy host + all MFEs
  -> Complex dependency management across teams
```

## Impact

**This affects:**
- Bundle sizes (massive overhead for libraries with many exports)
- Performance (downloading unused code)
- Coordination overhead (all teams must align on shared packages)
- Scalability (more MFEs = more coordination = more waste)

**Without chunk-level sharing:**
- MFEs download entire packages even if using 1-2 functions
- Tree-shaking benefits lost for shared dependencies
- No optimization for partial usage
- Bundle sizes grow unnecessarily

## Recommended Solution

**Proposal should acknowledge this limitation and either:**
1. Accept the package-level sharing trade-off (document the overhead)
2. Recommend using standard builds with content-hash based sharing instead
3. Provide guidance on minimizing impact (use micro-libraries instead of monoliths)

## References

- Module Federation documentation on shared dependencies
- Related proposal sections:
  - `design.md` - Decision 12: Module Federation 2.0 (shows shared config, doesn't mention tree-shaking loss)
  - Fragment System comparison: Uses standard Vite builds with natural tree-shaking and chunk-level sharing
