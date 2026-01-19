# Iteration 1: Feedback Review

This folder contains the first iteration of external feedback review for the `add-microfrontend-support` proposal.

## Structure

```
iteration-1/
├── README.md                        # This file
├── feedback/                        # External feedback received
│   └── add-microfrontend-support/
│       ├── README.md                # Feedback index
│       ├── comments/                # Individual feedback items
│       └── vision/                  # Reviewer's reference architecture
├── responses/                       # Our responses to feedback
│   ├── README.md                    # Summary table
│   └── comments/                    # Individual responses
└── updated-proposal/                # Proposal after addressing feedback
    ├── proposal.md
    ├── design/
    ├── specs/
    └── tasks.md
```

## Feedback Summary

7 feedback items were received covering:

| Category | Items |
|----------|-------|
| Deployment & Versioning | Cache busting, declarative metadata, tree-shaking |
| Local Development | Dev workflow, dev server |
| Type System & Architecture | Vendor type registration, module export abstraction, React compatibility |

## Response Status

| Status | Count |
|--------|-------|
| Addressed | 3 |
| Already Addressed | 1 |
| Out of Scope | 1 |
| Pending | 2 |

See [responses/README.md](./responses/README.md) for detailed status.

## Key Changes in This Iteration

1. **MfeEntryLifecycle Interface** - New framework-agnostic lifecycle interface replacing React-specific types
2. **Framework Examples** - Added mount/unmount examples for React, Vue 3, Svelte, Vanilla JS
3. **Internal vs Public API** - Clarified that `MfeLoader`/`LoadedMfe` are internal implementation details
4. **Vendor Type Registration** - Added Decision 5 explaining vendor packages, derived types, and polymorphic validation
