# Glossary

- `Federation` - A service that runs in the root application (also called the "host application") and is responsible for loading, initializing, and managing Fragments. It handles versioning, routing, preloading of assets, and provides a set of interfaces that Fragments can use to interact with the host application. Think of it as the "orchestrator" that coordinates all the micro-frontends.

- `Fragment` - A self-contained, independently deployable unit of UI functionality (micro-frontend) that is built specifically to be consumed by Federation. Each Fragment can contain components, methods, routes, and translations. For example, a "User Settings" Fragment might include a settings page component, several sub-routes for different settings categories, and its own translation files.

- `Manifest` - A JSON file (`manifest.{version}.json`) that describes a Fragment's contents and structure. Federation reads this file to understand what components, methods, routes, and translations the Fragment provides, and how to load them.

- `Entry Point` - A JavaScript file that serves as the main access point for a Fragment. A Fragment can have multiple entry points, each exposing different components and methods. For example, a Fragment might have a `main` entry point for the full UI and a `widget` entry point for an embeddable mini-version.

- `Component` - A UI element exported by a Fragment that can be rendered by the host application. Components are referenced by name and can optionally define their own routing structure.

- `Method` - A function exported by a Fragment that can be invoked by the host application. Methods allow Fragments to extend the application's functionality without rendering UI. For example, a Fragment might export a method that registers event handlers or modifies application behavior.

- `Plugin` - An extension mechanism that allows the host application to expose APIs and functionality to Fragments. Plugins provide services like routing, localization, feature flags, and network requests that Fragments can use.

- `Preloading` - The process of downloading Fragment assets (JavaScript, CSS, translations) before they are actually needed. This improves perceived performance by having resources ready when the user navigates to a Fragment.

- `Subfragment` - A Fragment that is instantiated and used by another Fragment, enabling composition of micro-frontends. For example, a "Dashboard" Fragment might embed a "Charts" Fragment within itself.

- `SSR (Server-Side Rendering)` - The process of rendering the initial HTML on the server before sending it to the browser. In the Fragment system, SSR is used to add preload hints and prepare Fragment routes before the page loads.

- `CDN (Content Delivery Network)` - A distributed network of servers that hosts and delivers Fragment assets (JS, CSS, translations). Fragments are deployed to the CDN, and both the server and browser download Fragment files from it.
