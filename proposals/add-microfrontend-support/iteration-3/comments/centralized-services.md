# Response: Centralized Services

## Status: Addressed

## Summary

The request for centralized services (router, API, etc.) to be available via MfeBridge is now addressed through the **MfeBridgeFactory** abstraction and custom handler architecture.

## Response

### The Solution: Custom Bridge Factories

The proposal now includes `MfeBridgeFactory` as an abstract factory that companies can extend to inject shared services into bridges for their internal MFEs.

```typescript
// From mfe-loading.md - Decision 10

abstract class MfeBridgeFactory<TBridge extends MfeBridge = MfeBridge> {
  abstract create(domainId: string, entryTypeId: string, instanceId: string): TBridge;
  abstract dispose(bridge: TBridge): void;
}

// Company's rich bridge factory
class MfeBridgeFactoryAcme extends MfeBridgeFactory<MfeBridgeAcme> {
  constructor(
    private router: Router,
    private apiClient: ApiClient,
    private analytics: AnalyticsService
  ) { super(); }

  create(domainId: string, entryTypeId: string, instanceId: string): MfeBridgeAcme {
    return new MfeBridgeAcme(
      domainId, entryTypeId, instanceId,
      this.router,      // Shared router
      this.apiClient,   // Shared API client
      this.analytics    // Shared analytics
    );
  }
}
```

### How It Works

1. **Default behavior (3rd-party MFEs)**: `MfeBridgeFactoryDefault` creates thin bridges with only the minimal contract (shared properties, actions). This maintains isolation and security for untrusted code.

2. **Custom behavior (internal MFEs)**: Companies create custom handlers with custom bridge factories that inject shared services. Internal MFEs receive rich bridges with access to centralized services.

3. **Handler registration**: Custom handlers are registered with higher priority, ensuring internal MFE entries get the rich bridges:

```typescript
// Register company handler with higher priority
registry.register(new MfeHandlerAcme(typeSystem, router, apiClient)); // priority: 100
registry.register(new MfeHandlerMF(typeSystem));                      // priority: 0 (fallback)
```

### Architecture Alignment

This approach:
- **Preserves HAI3's thin contract principle** as the default for 3rd-party MFEs
- **Enables companies to add centralized services** for their internal MFEs
- **Uses type hierarchy** to route entries to appropriate handlers
- **Keeps the decision at the company level** - they choose what to share

### Related Proposal Sections

- [mfe-loading.md - Decision 10: MfeHandler Abstraction and Registry](../proposal/design/mfe-loading.md)
- [principles.md - Default Architecture: Thin Contracts, Full Ownership](../proposal/design/principles.md)

## Conclusion

The feedback is fully addressed. Companies can now inject centralized services into bridges for their internal MFEs through custom `MfeBridgeFactory` implementations, while maintaining the thin contract default for 3rd-party MFEs.
