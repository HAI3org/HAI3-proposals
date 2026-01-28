# Design: Collaborative Proposal Framework

## Context
This repository manages proposals for Cyber Fabric. Multiple stakeholders need to collaboratively develop proposals before they become implementation specs. GitHub's PR-based workflow fragments context across forks, making LLM-assisted review difficult.

## Goals
- Enable multiple contributors to discuss and refine proposals in a single repository
- Preserve iteration history and change proposal rationale
- Allow LLM tools to access full proposal context in one location
- Integrate with existing openspec workflow (proposals graduate to openspec specs)

## Non-Goals
- CLI tooling (start with documentation conventions)
- Automated state management
- Replacing openspec for implementation tracking

## Decisions

### Decision: Separate `proposals/` directory
**Rationale**: Keep collaborative design separate from implementation-ready specs.
- `proposals/` = work-in-progress, collaborative design
- `openspec/specs/` = approved specs ready for implementation

### Decision: Initial + iteration-based structure
**Rationale**: Separates the initial proposal from feedback iterations.
- `initial/` contains the original proposal
- `iteration-N/` folders capture feedback cycles
- Clear progression: initial/ → iteration-1/ → iteration-2/ → graduation
- Each iteration is a complete snapshot preserving history

### Decision: Change proposals use simplified openspec-inspired structure
**Rationale**: Change proposals need structure for clarity but don't need full openspec overhead.
- One folder per change proposal (`changes/{change-name}/`)
- Each folder contains: `proposal.md` and `design.md` (both required)
- No `tasks.md` or `specs/` - these are discussion documents, not implementation-ready changes
- Lighter weight than full openspec, but still organized

### Decision: Comments folder for open discussion
**Rationale**: Comments allow free-form feedback without formal change proposal structure.
- Contributors create personal comment files (`{author}.md` or `{topic}.md`)
- Comments may spawn change proposals or inform next iteration
- Lower barrier than formal change proposals

## Directory Structure

```
proposals/
└── {proposal-name}/
    ├── initial/                   # Initial proposal
    │   ├── README.md              # Proposal overview and empty tables
    │   ├── proposal/              # Initial proposal content
    │   │   ├── proposal.md        # Why and what
    │   │   ├── specs/             # Spec files (openspec format)
    │   │   │   └── {capability}/
    │   │   │       └── spec.md
    │   │   └── design/            # Technical design documents
    │   │       └── *.md
    │   ├── changes/               # Change proposals
    │   │   └── {change-name}/
    │   │       ├── proposal.md    # Why and what
    │   │       └── design.md      # Technical details
    │   └── comments/              # Reviewer feedback
    │       └── {author-or-topic}.md
    ├── iteration-1/               # First feedback iteration
    │   ├── README.md              # Documents modifications from initial
    │   ├── proposal/              # Updated proposal
    │   ├── changes/               # New/carried change proposals
    │   └── comments/              # New/carried comments
    ├── iteration-2/
    │   └── ...
    └── ...
```

## File Formats

### README.md (Iteration Entrypoint)
```markdown
# {Proposal Name} - Iteration {N}

## Modifications from Previous Iteration
- [List modifications made to spec based on iteration N-1 change proposals]

## Current Change Proposals

| Change | Description | Author |
|--------|-------------|--------|
| use-grpc | Switch from REST to gRPC for service communication | @alice |
| add-caching | Add Redis caching layer | @bob |

## Comments

| File | Author | Topic |
|------|--------|-------|
| alice.md | @alice | Concerns about migration path |
| performance.md | @bob | Performance benchmarks |
```

### Change Proposal Format
Each change proposal is a folder with proposal.md and design.md:

```
changes/{change-name}/
├── proposal.md    # Required
└── design.md      # Required
```

**proposal.md**:
```markdown
# Change: {Change Name}

## Why
{1-2 sentences on problem/opportunity}

## What Changes
- {Bullet list of proposed spec modifications}

## Impact
- Affected specs: {list capabilities}
```

**design.md**:
```markdown
## Context
{Background and constraints}

## Proposal
{Detailed explanation of the change}

## Rationale
{Why this improves the spec}

## Alternatives Considered
{Other approaches and why not chosen}
```

### Comment File Format
No strict format. Contributors write markdown with their thoughts, questions, concerns, or suggestions.

### Proposal Folder Format
The `proposal/` folder contains the current iteration's full proposal:

```
proposal/
├── proposal.md        # Why and what
├── specs/             # Spec files
│   └── {capability}/
│       └── spec.md    # Openspec format
└── design/            # Technical design
    └── *.md           # One or more design docs
```

**proposal.md**: Same format as change proposal (Why, What Changes, Impact)

**specs/**: Follow openspec `spec.md` format:
- `### Requirement: {Name}` headers
- `#### Scenario:` for each scenario

**design/**: Technical design documents (can be multiple files for complex proposals)

## Lifecycle

### Creating a New Proposal
1. Create `proposals/{name}/initial/`
2. Create `proposal/` with proposal.md, specs/, and design/
3. Create README.md with empty tables
4. Share for review

### Iteration Cycle
1. Contributors add change proposals and comments to current iteration
2. When ready to progress:
   - Create next iteration folder (initial/ → iteration-1/ → iteration-2/ → ...)
   - Copy and update proposal/ based on accepted change proposals
   - Move unaddressed change proposals/comments to new iteration
   - Discard implemented or rejected change proposals
   - Update README.md documenting modifications made

### Graduation to OpenSpec
When proposal reaches consensus:
1. Move final `proposal/specs/` directly to `openspec/specs/`
2. Archive or keep `proposals/{name}/` for historical reference

## Risks / Trade-offs

### Risk: Iteration proliferation
**Mitigation**: Encourage batching change proposals before creating new iterations. No hard rules on when to iterate.

### Risk: Change proposals become stale
**Mitigation**: README.md tracks change proposals and their status. Contributors should review and update regularly.

### Risk: Duplicate discussions
**Mitigation**: README.md serves as index. Check existing change proposals/comments before adding new ones.

## Open Questions
- Should there be a maximum number of iterations before forcing a decision?
- Should comments have explicit "addressed" markers?
