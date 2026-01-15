# Local Development Comments

This document contains comments related to local development workflow, dev server configuration, and integration testing in the `add-microfrontend-support` proposal. These are essential infrastructure requirements for developing microfrontends as part of the host application, not just developer experience improvements.

---

## 1. Missing Development Workflow and Dev Server Configuration

### Problem

The proposal provides no guidance on how to develop MFEs locally during development. There is no specification for:
- Dev server configuration
- URL overrides for loading local MFEs instead of production CDN URLs
- Hot module replacement (HMR) support
- Proxy configuration for APIs and other services
- How to test MFE integration with host app during development

**Current MfManifest only supports production URLs:**
```typescript
interface MfManifest {
  remoteEntry: string;  // e.g., 'https://cdn.acme.com/analytics/remoteEntry.js'
}

// No mechanism to override this for development
```

### Why Dev Server is Needed

#### 1. Integration Testing with Host Application

**Developers need to test their MFE within the actual host application:**

```typescript
// Host app needs to load local MFE during development
// Production: Load from CDN
const manifest = {
  remoteEntry: 'https://cdn.acme.com/analytics/remoteEntry.js'
};

// Development: Load from localhost dev server
const manifest = {
  remoteEntry: 'http://localhost:3001/remoteEntry.js'  // Local dev server
};

// How to switch between these? Proposal doesn't specify.
```

**Fragment System solution (Proxy Mode):**
```bash
# Start fragment dev server in proxy mode
cd analytics-fragment
npm run dev -- --proxy-target=https://staging.example.com
# → Dev server starts at http://localhost:3001

# Dev server behavior:
# 1. Proxies root request to target environment: GET / → https://staging.example.com/
# 2. Gets host app HTML from target environment
# 3. Serves the HTML to browser
# 4. Intercepts requests to current fragment: /fragments/analytics/* → localhost
# 5. Proxies all other fragments to target: /fragments/billing/* → staging
# 6. Proxies API requests: /api/* → staging

# Result: Full host app loaded from target environment, only analytics fragment local
# No host app code changes needed
# Can use host app debug API to override settings for development
```

#### 2. Versioned Path Handling

**Dev server must serve content at versioned paths matching production:**

```bash
# Production structure:
https://cdn.acme.com/fragments/analytics/main.abc123/manifest.main.abc123.json
https://cdn.acme.com/fragments/analytics/main.abc123/main.main.abc123.js

# Dev server must simulate this:
http://localhost:3001/fragments/analytics/dev/manifest.dev.json
http://localhost:3001/fragments/analytics/dev/main.dev.js

# Fragment System dev server handles:
# - Version path routing (/fragments/{name}/{version}/*)
# - Manifest generation at runtime
# - Entry file serving with hash stripping
```

**Without versioned path support:**
- Dev URLs don't match production structure
- Integration testing not realistic
- Path mismatches cause bugs in production

#### 3. Translation File Hot Reload

**Developers need to see translation changes immediately:**

```bash
# Developer edits translation file
src/translations/en-US.json

# Dev server detects change:
# 1. Triggers page reload
# 2. Serves updated translations from source
# 3. Developer sees new translations instantly

# Fragment System requirement:
# "WHEN a translation file in src/translations/ is modified
#  THEN the server SHALL trigger a full page reload"
```

**Without translation hot reload:**
- Must rebuild to see translation changes
- Slow iteration on internationalization

#### 4. Multi-Fragment Development (One Local, Others Remote)

**Developer works on one fragment while using others from deployed environment:**

```bash
# Start analytics fragment dev server with proxy mode enabled
cd analytics-fragment
npm run dev -- --proxy-target=https://staging.example.com
# → Opens browser at http://localhost:3001/

# What happens:
# 1. Dev server proxies GET / → https://staging.example.com/
# 2. Target environment returns host app HTML
# 3. Host app HTML includes: <script src="/fragments/analytics/main.abc123.js">
# 4. Browser requests /fragments/analytics/* → intercepted by dev server (local)
# 5. Browser requests /fragments/billing/* → proxied to target (remote)
# 6. Browser requests /api/* → proxied to target (backend)

# Result:
# - Full host app from target environment (including real routing, auth, etc.)
# - Only analytics fragment served locally with HMR
# - All other fragments from target environment
# - Real backend APIs
# - Can use host app's debug API to override configs

# Host app's debug API is accessible for runtime configuration overrides
```

**Alternative: Override specific remote fragments**
```bash
# Work on analytics locally, but load billing from another dev server too
cd analytics-fragment
npm run dev -- \
  --proxy-target=https://staging.example.com \
  --override-fragment=billing:http://localhost:3002

# Now both analytics and billing are local, rest from target environment
```

**Fragment System approach:**
The fragment development server supports proxying all requests to a target
environment, serving only the current fragment locally while forwarding
everything else (including other fragments, host app, APIs) to the target.
This can be configured via command-line flags or environment variables.

**Why this is powerful:**
- **No host app changes** - Just start fragment dev server with proxy mode
- **Real environment** - Actual host app HTML, routing, auth from target
- **Selective local development** - Only fragments being worked on are local
- **Debug API integration** - Can use host app's debug tools to override settings
- **Fast iteration** - HMR on local fragment, everything else stays stable

### Comparison with Fragment System

**Fragment System dev server provides:**

| Feature | Fragment System | MFE Proposal |
|---------|----------------|--------------|
| **Dev server config** | `fragment()` Vite plugin | Not specified |
| **Versioned path serving** | `/fragments/{name}/{version}/*` | Not specified |
| **Manifest generation** | Dynamic at runtime | Not specified |
| **Entry file serving** | Hash-stripping, source mapping | Not specified |
| **Translation hot reload** | Full page reload on change | Not specified |
| **Environment overrides** | Command-line flags or env vars | Not specified |
| **Proxy mode** | One local, others remote | Not specified |
| **HMR support** | Vite HMR | Not specified |

### What MFE System Needs

**The proposal should specify:**

1. **Dev Server Configuration**
   - Port configuration
   - How to serve at versioned paths
   - How to handle module federation remote loading

2. **URL Override Mechanism**
   ```typescript
   // How to override remoteEntry URL for development
   interface MfManifest {
     remoteEntry: string;
     devRemoteEntry?: string;  // Override for development?
   }

   // Or environment variable approach:
   // MFE_ANALYTICS_URL=http://localhost:3001
   ```

3. **Versioned Path Serving**
   - How dev server serves at versioned paths
   - Manifest generation at runtime vs static
   - Path structure matching production

4. **Multi-MFE Development Workflow (Proxy Mode)**
   - How to proxy host app from target environment
   - How to run one MFE locally while loading others remotely
   - Configuration mechanism (flags, environment variables, etc.)
   - Proxy routing for remote MFEs

5. **HMR with Module Federation**
   - Does Module Federation support HMR?
   - How to configure it?
   - Limitations or caveats?

### Example Development Workflow (What's Missing)

**Fragment System workflow (Proxy Mode):**
```bash
# 1. Start analytics fragment dev server with proxy to target environment
cd analytics-fragment
npm run dev -- --proxy-target=https://staging.example.com
# → Server at http://localhost:3001
# → Opens browser at http://localhost:3001/
# → Proxies host app from target: GET / → https://staging.example.com/
# → Intercepts analytics fragment: /fragments/analytics/* → localhost
# → Proxies everything else to target environment

# 2. Browser loads
# - Host app HTML from target environment ✅
# - Analytics fragment from localhost (HMR enabled) ✅
# - All other fragments from target environment ✅
# - API requests to target backend ✅
# - Auth flows work (real OIDC from target) ✅

# 3. Edit code
vim src/Dashboard.tsx
# → HMR updates browser instantly
# → No rebuild needed
# → Everything else (host, other fragments, APIs) unchanged

# 4. Edit translations
vim src/translations/en-US.json
# → Page reloads with new translations

# 5. Host app debug API is accessible
# Can be used to override configurations during development
```

**MFE System (not specified):**
```bash
# How do you...
# 1. Configure dev server for MFE?
# 2. Override remoteEntry URL for local development?
# 3. Test one MFE locally with others remote (proxy mode)?
# 4. Get HMR working?
# 5. Use host app debug API during development?

# Proposal provides no guidance
```

### Impact

**This affects:**
- **Developer productivity** - Slow feedback loop without HMR and dev server
- **Integration testing** - Difficult to test MFE within host app during development
- **Team collaboration** - No way to work on one MFE while using others from deployed environments
- **Onboarding** - New developers don't know how to set up local development
- **Debugging** - Hard to debug without proper dev environment setup

**Without dev server specification:**
- Teams must invent their own solutions (inconsistent approaches)
- No standard workflow for MFE development
- Integration testing requires full builds and deployments
- Slow iteration cycle hurts productivity

### Recommended Solution

**Proposal should specify:**

1. **Dev server plugin/configuration** for Module Federation
2. **Proxy mode** for loading host app from target environment while serving MFE locally
3. **URL override mechanism** for loading local MFEs
4. **Multi-MFE development workflow** (one local, others remote)
5. **HMR configuration** and limitations
6. **Debug API integration** for runtime configuration overrides

### References

- Fragment System dev server specification
- Module Federation documentation on dev server setup
- Related proposal sections:
  - Section 1: Missing Cache Busting Strategy (manifest URL management)
  - Section 6: Missing Declarative Metadata (manifest generation)
