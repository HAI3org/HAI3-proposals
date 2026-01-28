# Change: Add Collaborative Proposal Framework

## Why
Multiple contributors need to collaboratively design and iterate on proposals before they become implementation-ready specs. The current GitHub workflow makes it difficult to:
- Keep all proposal files in one place for LLM-assisted review (forks create scattered context)
- Track discussion threads alongside spec content
- Iterate on proposals based on feedback without losing history

## What Changes
- Add a `proposals/` directory at repository root for collaborative spec design
- Define iteration-based workflow:
  - `initial/` for the original proposal
  - `iteration-N/` for feedback iterations
  - Each folder contains: proposal/, changes/, comments/, README.md
  - Progression: initial/ → iteration-1/ → iteration-2/ → graduation
- Establish conventions for progressing through iterations
- **NOT** adding CLI tooling (documentation convention only for now)

## Impact
- Affected specs: None (new capability)
- Affected code: None (documentation/convention only)
- New directory: `proposals/` at repository root
