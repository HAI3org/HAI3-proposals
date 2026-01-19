# Response: Missing Cache Busting Strategy

## Status: Already Addressed

## Summary

The cache busting concern is addressed by the existing contract. The `remoteEntry` field is a flexible `string` type that accepts any URL, allowing implementers to choose their preferred cache busting strategy.

## Response

### The Contract is Sufficient

```typescript
interface MfManifest {
  remoteEntry: string;  // Any valid URL
}
```

This contract allows any cache busting approach:

| Strategy | Example | Trade-offs |
|----------|---------|------------|
| Version in path | `/v1.2.3/remoteEntry.js` | Readable, easy debugging |
| Content hash | `/remoteEntry.a3f5b9c2.js` | Automatic, opaque |
| Query string | `/remoteEntry.js?v=1.2.3` | Simple, some CDNs ignore |

### Why This is an Implementation Detail

1. **Contract Flexibility**: The proposal defines WHAT the contract is (`remoteEntry: string`), not HOW vendors implement cache busting
2. **Vendor Responsibility**: MFE vendors are responsible for their deployment strategy, including cache-safe URLs
3. **No Single Best Approach**: Different teams may prefer different strategies based on their CDN, build tools, and debugging needs

### Preferred Approach: Version in Path

We prefer version in path (`/v1.2.3/remoteEntry.js`) over content hash because:

- **Readability**: Immediately clear which version is loaded in DevTools
- **Debugging**: Easy to correlate issues with specific versions
- **Rollback**: Simple to switch to a previous version by changing the path

### Conclusion

No specification changes needed. The flexible contract already supports all cache busting strategies. This is a deployment concern, not an architectural gap.
