# HAI3 Proposals

This repository contains proposals for HAI3 capabilities. Multiple stakeholders collaboratively develop proposals before they graduate to implementation-ready specs.

## Repository Structure

```
proposals/           # Collaborative proposal design
└── {proposal-name}/
    ├── initial/     # Original proposal
    ├── iteration-1/ # First feedback iteration
    ├── iteration-2/ # Second feedback iteration
    └── ...

openspec/            # Implementation-ready specs and changes
├── specs/           # Approved specifications
└── changes/         # Change proposals for openspec
```

## Proposals Workflow

### Creating a New Proposal

1. Create `proposals/{name}/initial/`
2. Add `proposal/` folder with:
   - `proposal.md` - Why and what
   - `specs/` - Spec files (openspec format)
   - `design/` - Technical design documents
3. Create `README.md` with overview and empty tables
4. Add `changes/` and `comments/` directories
5. Share for review

### Iteration Cycle

1. Contributors add change proposals and comments to current iteration
2. When ready to progress:
   - Create next iteration folder (`iteration-N/`)
   - Copy and update `proposal/` based on accepted change proposals
   - Move unaddressed change proposals/comments to new iteration
   - Update `README.md` documenting modifications made

### Structure Per Iteration

```
iteration-N/
├── README.md        # Modifications from previous, tables for changes/comments
├── proposal/        # Updated proposal content
│   ├── proposal.md
│   ├── specs/
│   └── design/
├── changes/         # Change proposals (folder per change with proposal.md + design.md)
└── comments/        # Open discussion files
```

## Graduation to OpenSpec

When a proposal reaches consensus:

1. Move final `proposal/specs/` directly to `openspec/specs/`
2. Archive or keep `proposals/{name}/` for historical reference
3. Implementation work tracked via openspec

## Current Proposals

| Proposal | Status | Description |
|----------|--------|-------------|
| [add-microfrontend-support](./proposals/add-microfrontend-support) | Iteration 1 | MFE support for HAI3 applications |
