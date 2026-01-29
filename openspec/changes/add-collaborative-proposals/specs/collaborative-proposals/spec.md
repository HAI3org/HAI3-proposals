## ADDED Requirements

### Requirement: Proposal Directory Structure
The system SHALL maintain a `proposals/` directory at the repository root for collaborative proposal development.

Each proposal SHALL be contained in a named subdirectory (`proposals/{proposal-name}/`) with an `initial/` folder and iteration folders (`iteration-1/`, `iteration-2/`, etc.).

#### Scenario: New proposal creation
- **WHEN** a new proposal is initiated
- **THEN** a directory `proposals/{name}/initial/` is created with README.md, proposal/, changes/, and comments/ subdirectories

#### Scenario: Proposal naming
- **WHEN** naming a proposal directory
- **THEN** use kebab-case descriptive names (e.g., `api-authentication`, `data-model-v2`)

---

### Requirement: Iteration Structure
Both `initial/` and `iteration-N/` folders SHALL share the same structure:
- `README.md` - Iteration entrypoint documenting changes and indexing change proposals/comments
- `proposal/` - Current iteration proposal with proposal.md, specs/, and design/
- `changes/` - Change proposals (proposal.md + design.md per change)
- `comments/` - Directory containing comment files

#### Scenario: Initial folder contents
- **WHEN** the initial/ folder is created
- **THEN** it contains README.md, proposal/, changes/, and comments/ directories

#### Scenario: Iteration folder contents
- **WHEN** an iteration-N/ folder is created
- **THEN** it contains README.md, proposal/, changes/, and comments/ directories

#### Scenario: Proposal folder contents
- **WHEN** creating the proposal/ folder
- **THEN** it contains proposal.md, specs/, and design/

---

### Requirement: Proposal Folder Structure
The `proposal/` folder SHALL contain the current iteration's proposal following openspec-inspired conventions.

The proposal folder SHALL contain:
- `proposal.md` - Why the change is needed and what it affects
- `specs/` - Spec files following openspec format (`{capability}/spec.md`)
- `design/` - Technical design documents (one or more .md files)

#### Scenario: Proposal folder structure
- **WHEN** creating the proposal/ folder
- **THEN** it contains proposal.md, specs/ directory, and design/ directory

#### Scenario: Spec format compliance
- **WHEN** writing spec files in proposal/specs/
- **THEN** use openspec spec.md format with `### Requirement:` headers and `#### Scenario:` sections

---

### Requirement: Iteration README
Each iteration's README.md SHALL serve as the entrypoint and index for that iteration.

The README SHALL include:
- Modifications made from the previous iteration (for iteration-1+)
- Table of current change proposals with name, short description, and author
- Table of current comments with filename, author, and topic

#### Scenario: Initial README
- **WHEN** creating initial/ README.md
- **THEN** include empty change and comment tables with instructions for contributors

#### Scenario: Subsequent iteration README
- **WHEN** creating iteration-N README.md
- **THEN** include a "Modifications from Previous Iteration" section listing spec updates based on accepted changes

---

### Requirement: Change Proposals
Change proposals SHALL argue for specific spec modifications using a simplified openspec-inspired structure.

Each change proposal SHALL be a folder (`changes/{change-name}/`) containing:
- `proposal.md` - Why the change is needed and what it affects
- `design.md` - Technical details and rationale

#### Scenario: Creating a change proposal
- **WHEN** a contributor wants to propose a spec change
- **THEN** they create `changes/{change-name}/` folder with proposal.md and design.md
- **AND** add an entry to the iteration README.md in the Current Change Proposals table

#### Scenario: Change proposal scope
- **WHEN** writing a change proposal
- **THEN** it targets a specific area of the spec (not broad, unfocused suggestions)

---

### Requirement: Comment Files
Comment files SHALL allow free-form feedback on the proposal or decisions.

Contributors MAY create comment files named by author (`{author}.md`) or topic (`{topic}.md`).

#### Scenario: Adding a comment
- **WHEN** a contributor wants to provide feedback
- **THEN** they create or update a file in the `comments/` directory

#### Scenario: Comment format
- **WHEN** writing a comment file
- **THEN** standard markdown is used with no required structure

---

### Requirement: Iteration Progression
The system SHALL support progression to new iterations when contributors are ready to incorporate feedback.

When progressing to a new iteration:
- A new iteration folder SHALL be created (`initial/` → `iteration-1/` → `iteration-2/` → ...)
- The proposal/ SHALL be updated based on accepted change proposals
- Implemented or rejected change proposals SHALL be discarded
- Unaddressed change proposals and valid comments SHALL be moved to the new iteration
- The README SHALL document modifications made

#### Scenario: First iteration from initial
- **WHEN** ready to progress from initial/
- **THEN** create iteration-1/ with updated proposal/ reflecting accepted change proposals

#### Scenario: Subsequent iterations
- **WHEN** ready to progress from iteration-N
- **THEN** create iteration-{N+1}/ with updated proposal/ reflecting accepted change proposals

#### Scenario: Change proposal handling on iteration
- **WHEN** creating a new iteration
- **THEN** implemented change proposals are removed, unaddressed change proposals are copied to new iteration

#### Scenario: Comment handling on iteration
- **WHEN** creating a new iteration
- **THEN** comments that are still relevant are moved; addressed comments may be removed

---

### Requirement: Graduation to OpenSpec
When a proposal reaches consensus, it SHALL be eligible for graduation to the openspec specs.

Graduation involves moving the final iteration's `proposal/specs/` directly to `openspec/specs/`.

#### Scenario: Proposal graduation
- **WHEN** a proposal is approved and finalized
- **THEN** the specs from `proposal/specs/` in the last iteration are moved to `openspec/specs/`
- **AND** the proposal may be archived or retained for reference
