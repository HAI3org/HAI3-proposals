# Missing System Extensibility

Reference: [iteration-1 mfe-loading.md](../../iteration-1/proposal/design/mfe-loading.md)

## Problem

In `mfe-loading.md`, `MfeLoader` is marked as internal and not part of the public API:

> **Note on MfeLoader/LoadedMfe:** These are **internal implementation details** of the ScreensetsRegistry, not part of the public API.

This means there is no possibility to extend the system. For example:
- What exactly will be preloaded
- How preloading is triggered
- Custom loading strategies (e.g., priority-based, route-based)
- Custom caching strategies

The system is closed for extension in areas where different projects may have different needs.

## Recommended Solution

Introduce a plugin system with hooks to extend system behavior.

Example - plugin with preload hook:

```typescript
import { createScreensetsPlugin } from '@hai3/screensets';

export function createLocalizationPlugin(i18next?: i18n) {
  return createScreensetsPlugin('localization', (ctx) => {
    // Hook into lifecycle events
    ctx.hook('mfe:load', onMfeLoad);
    ctx.hook('mfe:preload', onMfePreload);

    async function onMfePreload(mfeName: string, config: PreloadConfig) {
      if (!config.language) {
        return;
      }

      // Custom preload logic for translations
      const manifest = ctx.publicApi.getMfeManifest(mfeName);
      const translationFile = manifest.translations?.[config.language];

      if (translationFile) {
        await ctx.publicApi.preloadAsset(translationFile, { as: 'fetch' });
      }
    }

    async function onMfeLoad(mfe: MfeInstance) {
      // Set up localization when MFE loads
      await setupLocalization(mfe);
    }

    // Return public API for this plugin
    return {
      getLocales,
    };

    function getLocales(mfeName: string) {
      // ...
    }
  });
}

// Usage
screensets.use(createLocalizationPlugin(i18next));
```

This approach:
- Provides `ctx.hook(event, handler)` for lifecycle hooks
- Allows plugins to extend preloading, loading, and other behaviors
- Keeps core implementation internal while exposing extension points
