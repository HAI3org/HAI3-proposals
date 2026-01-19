# Principles

## Independent of parent application
The Fragment system is designed to have no direct knowledge of the parent application it runs in. This decoupling ensures that Fragments can be reused across different host applications. Any integration with the parent application is achieved through the plugin API, which allows the host to extend Federation's capabilities and expose custom functionality to Fragments.

## Federation owns implementation, Fragments follow interface
Federation exists as a single instance in the root application and owns all core implementations. Fragments (which can have multiple instances) do not implement their own services but instead consume the interfaces provided by Federation. This ensures consistency across all Fragments and follows the principle of one service per concern: there is one service for backend requests, one for localization, one for feature flags, one for routing, and so on.

## Framework-agnostic core
The core services of both Federation and Fragment packages are framework-agnostic, meaning they don't depend on any specific UI framework like React or Vue. Framework-specific adapters are created as separate packages to bridge the gap between the framework-agnostic core and the actual UI framework being used.
