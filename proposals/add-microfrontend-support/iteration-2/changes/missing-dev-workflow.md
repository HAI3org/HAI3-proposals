# Missing Dev Workflow

Reference: [iteration-1 change](../../iteration-1/changes/missing-dev-workflow.md)

## Problem

In [comments/missing-dev-workflow.md](../../iteration-1/comments/missing-dev-workflow.md) the dev server part is marked as "Out of Scope".

This cannot be the case. MFE in its current shape is just a JS entry file. Without an environment to run these files, development is impossible.

Developers need to:
- Run MFE locally during development
- Test MFE in isolation
- Test MFE integrated with host app
- Debug MFE code

Without tooling guidance, every team will create their own dev setup, leading to:
- Inconsistent approaches
- Repeated effort across teams
- Integration issues discovered late

## Recommended Solution

Add high-level description about MFE bundler part - what parts the system will cover:

1. **What HAI3 provides** (or recommends):
   - Dev server configuration for MFE development
   - Local host app mock/stub for isolated MFE testing
   - Integration testing setup with real host app

2. **What is left to implementers**:
   - CI/CD pipelines
   - Deployment infrastructure
   - Team-specific tooling

The proposal should clarify the boundary between what HAI3 covers and what is left to implementing teams.
