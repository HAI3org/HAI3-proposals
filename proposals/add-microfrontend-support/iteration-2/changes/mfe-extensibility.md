# MFE Extensibility

## Overview

The MFE system provides a plugin-based extensibility mechanism. While MFEs can implement `mount`/`unmount` lifecycle methods manually, the plugin system provides standardized integrations out of the box.

## Motivation

Without plugins, every MFE developer would need to:
- Manually wire up SharedProperties to their framework's reactivity system
- Manually handle bridge communication
- Manually implement correct cleanup on unmount
- Risk inconsistent implementations across MFEs

## Plugin Types

### Generic plugins (shipped by HAI3)
- React integration (officially supported)

Other framework integrations (Vue, Angular, Svelte) can be implemented using the plugin API.

### Company-specific plugins (created by organizations)
- Localization
- Theming
- Analytics and telemetry
- Error handling patterns

These plugins use `MfeBridge` internally to access shared properties and actions. The plugin system provides a unified way to attach multiple plugins in the same manner, allowing companies to enforce consistent patterns across all their MFEs.

## Design

The plugin system provides:
1. **Core `createMfe()` factory** - framework-agnostic base
2. **Official framework plugins** - React, Vue, etc.
3. **Custom plugin API** - for company-specific extensions

### Example
```typescript
// Core abstraction (framework-agnostic)
interface MfeEntryLifecycle {
  mount(container: HTMLElement, bridge: MfeBridge): void;
  unmount(container: HTMLElement): void;
}

import { createMfe } from '@hai3/mfe';

// React plugin (shipped by HAI3)
import { mfeReact } from '@hai3/mfe-react';

export default createMfe().use(mfeReact(<MyReactComponent />));

// Vue plugin (created by company)
import { mfeVue } from '@acme/mfe-vue';
import { mfeLocalization } from '@acme/mfe-localization';

export default createMfe()
  .use(mfeVue(MyVueComponent))
  .use(mfeLocalization()); // Subscribes to locale changes via MfeBridge, provides locale library, etc.

// Also possible to export raw object, but not recommended
const customMfe: MfeEntryLifecycle = { ... };
```

## Benefits

- Core system remains framework-agnostic
- Official plugins provide convenience for common frameworks
- Open plugin API allows extension for any framework or use case
