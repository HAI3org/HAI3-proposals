# Design: MFE API

This document covers the MFE Bridge interfaces, MfeEntryLifecycle interface, and framework-specific implementation examples.

---

## Context

The MFE API defines the runtime contract between host and MFE. It consists of:
- **MfeEntryLifecycle**: The interface every MFE must export (mount/unmount methods)
- **MfeBridge**: The communication channel passed to MFEs for host interaction
- **MfeBridgeConnection**: Extended bridge interface used by the host to manage MFE communication

These interfaces are framework-agnostic - MFEs can use React, Vue, Angular, Svelte, or vanilla JS while implementing the same lifecycle contract. The MfeBridge allows MFEs to request [actions](./mfe-actions.md) and subscribe to [shared properties](./mfe-shared-property.md).

## Definition

**MfeEntryLifecycle**: A runtime interface (not a GTS type) that defines `mount()` and `unmount()` methods every MFE must implement to integrate with the host.

**MfeBridge**: A read-only interface exposed to MFE components for requesting host actions and subscribing to [shared properties](./mfe-shared-property.md).

**MfeBridgeConnection**: An extended bridge interface used by the host to send [actions chains](./mfe-actions.md) to MFEs and manage the communication lifecycle.

---

## MfeEntryLifecycle Interface

```typescript
/**
 * Lifecycle interface for MFE entries.
 * Defines lifecycle methods that any MFE entry must implement,
 * regardless of framework (React, Vue, Angular, Vanilla JS).
 *
 * The name "MfeEntryLifecycle" is chosen because:
 * - It focuses on lifecycle semantics (mount/unmount)
 * - It's extensible for future lifecycle methods (onSuspend, onResume, etc.)
 * - It doesn't include implementation details like "Export" or "Module" in the name
 *
 * NOTE: This is a runtime interface for MFE entries, NOT a GTS type.
 * It is not registered in the Type System - it's a TypeScript interface for code contracts.
 *
 * Example implementations:
 * - React MFE: Uses ReactDOM.createRoot(container).render(<App bridge={bridge} />)
 * - Vue MFE: Uses createApp(App, { bridge }).mount(container)
 * - Angular MFE: Uses platformBrowserDynamic().bootstrapModule(...)
 * - Svelte MFE: Uses new App({ target: container, props: { bridge } })
 * - Vanilla JS: Directly manipulates DOM
 */
interface MfeEntryLifecycle {
  /**
   * Mount the MFE into a container element.
   * @param container - The DOM element to mount into (typically a shadow root)
   * @param bridge - The MfeBridge for host-MFE communication
   */
  mount(container: HTMLElement, bridge: MfeBridge): void;

  /**
   * Unmount the MFE from a container element.
   * Called when the extension is unloaded or the container is removed.
   * Should clean up all DOM content and unsubscribe from bridge.
   * @param container - The DOM element to unmount from
   */
  unmount(container: HTMLElement): void;
}
```

---

## MFE Bridge Interfaces

The MFE Bridge provides a bidirectional communication channel between host and MFE. The bridge is created by the host when mounting an extension and passed to the MFE component via props.

### MfeBridge Interface

```typescript
// packages/screensets/src/mfe/bridge/types.ts

/**
 * Read-only bridge interface exposed to MFE components.
 * MFEs use this to communicate with the host.
 */
interface MfeBridge {
  /** The entry type ID for this MFE instance */
  readonly entryTypeId: string;

  /** The domain type ID this MFE is mounted in */
  readonly domainId: string;

  /**
   * Request an action from the host.
   * The bridge validates the payload against the action's schema before sending.
   * @param actionTypeId - Action type ID (must be in entry's actions list)
   * @param payload - Action payload (validated against action schema)
   * @returns Promise that resolves when host acknowledges receipt
   */
  requestHostAction(actionTypeId: string, payload?: unknown): Promise<void>;

  /**
   * Subscribe to a shared property from the domain.
   * @param propertyTypeId - SharedProperty type ID
   * @param callback - Called with current value and on subsequent updates
   * @returns Unsubscribe function
   */
  subscribeToProperty(
    propertyTypeId: string,
    callback: (value: unknown) => void
  ): () => void;

  /**
   * Get current value of a shared property.
   * @param propertyTypeId - SharedProperty type ID
   * @returns Current value or undefined if not set
   */
  getProperty(propertyTypeId: string): unknown;

  /**
   * Subscribe to all shared properties at once.
   * @param callback - Called with property map on any property update
   * @returns Unsubscribe function
   */
  subscribeToAllProperties(
    callback: (properties: Map<string, unknown>) => void
  ): () => void;
}
```

### MfeBridgeConnection Interface

```typescript
/**
 * Extended bridge interface used by the host to manage MFE communication.
 * Created by ScreensetsRegistry when mounting an extension.
 */
interface MfeBridgeConnection extends MfeBridge {
  /** Unique instance ID for this bridge connection */
  readonly instanceId: string;

  /**
   * Send an actions chain to the MFE.
   * Used for domain-to-extension communication.
   * @param chain - ActionsChain to deliver
   * @param options - Optional per-request execution options (override defaults)
   * @returns ChainResult indicating execution outcome
   */
  sendActionsChain(chain: ActionsChain, options?: ChainExecutionOptions): Promise<ChainResult>;

  /**
   * Update a shared property value.
   * Notifies all subscribers in the MFE.
   * @param propertyTypeId - SharedProperty type ID
   * @param value - New property value
   */
  updateProperty(propertyTypeId: string, value: unknown): void;

  /**
   * Register handler for actions coming from the MFE.
   * @param handler - Callback invoked when MFE requests host action
   */
  onHostAction(
    handler: (actionTypeId: string, payload: unknown) => Promise<void>
  ): void;

  /**
   * Clean up the bridge connection.
   * Unsubscribes all listeners and releases resources.
   */
  dispose(): void;
}
```

### Bridge Creation Flow

```typescript
// When mounting an extension - the public API handles loading and mounting internally
const bridge = await runtime.mountExtension(extensionId, container);

// Internally, the runtime:
// 1. Loads the MFE bundle via MfeLoader (internal implementation detail)
// 2. Gets the MfeEntryLifecycle from the loaded module
// 3. Calls lifecycle.mount(container, bridge)
// 4. Returns the bridge for host-MFE communication

// When unmounting - also handled by the public API
await runtime.unmountExtension(extensionId);
// Internally calls lifecycle.unmount(container) and cleans up bridge
```

---

## Framework-Specific MFE Implementation Examples

**React MFE:**
```typescript
// mfe-entry.tsx - React MFE export
import { createRoot, Root } from 'react-dom/client';
import { MfeBridge } from '@hai3/screensets';
import { App } from './App';

let root: Root | null = null;

export function mount(container: HTMLElement, bridge: MfeBridge): void {
  root = createRoot(container);
  root.render(<App bridge={bridge} />);
}

export function unmount(container: HTMLElement): void {
  root?.unmount();
  root = null;
}
```

**Vue 3 MFE:**
```typescript
// mfe-entry.ts - Vue 3 MFE export
import { createApp, App as VueApp } from 'vue';
import { MfeBridge } from '@hai3/screensets';
import App from './App.vue';

let app: VueApp | null = null;

export function mount(container: HTMLElement, bridge: MfeBridge): void {
  app = createApp(App, { bridge });
  app.mount(container);
}

export function unmount(container: HTMLElement): void {
  app?.unmount();
  app = null;
}
```

**Svelte MFE:**
```typescript
// mfe-entry.ts - Svelte MFE export
import { MfeBridge } from '@hai3/screensets';
import App from './App.svelte';

let component: App | null = null;

export function mount(container: HTMLElement, bridge: MfeBridge): void {
  component = new App({
    target: container,
    props: { bridge }
  });
}

export function unmount(container: HTMLElement): void {
  component?.$destroy();
  component = null;
}
```

**Vanilla JS MFE:**
```typescript
// mfe-entry.ts - Vanilla JS MFE export
import { MfeBridge } from '@hai3/screensets';

export function mount(container: HTMLElement, bridge: MfeBridge): void {
  container.innerHTML = '<div class="my-widget">Loading...</div>';

  // Subscribe to properties
  bridge.subscribeToProperty(
    'gts.hai3.screensets.ext.shared_property.v1~hai3.screensets.props.theme.v1',
    (theme) => {
      container.style.background = theme === 'dark' ? '#333' : '#fff';
    }
  );
}

export function unmount(container: HTMLElement): void {
  container.innerHTML = '';
}
```
