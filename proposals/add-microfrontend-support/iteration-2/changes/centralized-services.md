# Centralized Services

References:
- [iteration-1 federation-vision](../../iteration-1/changes/federation-vision/README.md)
- [iteration-1 mfe-vision principles](../../iteration-1/changes/mfe-vision/principles.md)

## Overview

HAI3's model of "thin contracts + private optimization" as described in the principles document provides a solid default approach. This design keeps the core framework flexible and allows MFEs to remain independent.

However, some organizations may benefit from having centralized services (router, api, etc.) available for direct access from the MfeBridge. This should be possible as an opt-in extension rather than being prevented by the framework.

The decision of whether to expose centralized services is ultimately a company-level choice based on their specific architecture needs and trade-offs.

## Recommended Solution

Implement [missing-system-extensibility.md](./missing-system-extensibility.md) to allow plugins to extend the bridge API.

This approach:
- Preserves HAI3's thin contract principle as the default
- Enables companies to add services to the bridge based on their specific needs
- Allows organizations to decide their own trade-offs between isolation and convenience
