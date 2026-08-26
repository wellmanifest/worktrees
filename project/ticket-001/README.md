# Ticket 001: Define canonical worktree placement standard

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: BLOCKED
- **Workflow state**: EDIT
- **Created**: 2026-08-26

## Goal and scope

Lifecycle note: the original delivery was merged by PR #3. Further execution
authority moved to ticket-003; this historical ticket must not claim an active
writer lease.

Define a portable, machine-checkable placement contract for temporary linked
Git worktrees used to deliver ticket branches and pull requests. The contract
standardizes paths and leases only; Git transitions remain owned by
`wellmanifest/git-lifecycle`, ticket state remains owned by
`wellmanifest/ticket-lifecycle`, and runtime effects remain owned by Subactor
or another adopting runtime.

## Acceptance criteria

- [ ] AC-01: The canonical POSIX and Windows layouts are documented.
- [ ] AC-02: A JSON Schema describes the complete layout record.
- [ ] AC-03: A dependency-free planner produces canonical paths and branch names.
- [ ] AC-04: Validation rejects repo-local, parallel-root and ticket-drift layouts.
- [ ] AC-05: Unit tests and repository governance checks pass.

## Session authorization and risk

The user explicitly requested creation, standardization and adoption by
`wellmanifest/new-project`. This authorizes implementation and protected
publication for this bounded ticket. It does not authorize deletion or movement
of existing worktrees, secret access, or rewriting existing branches.

## Placement and delivery contract

- HOME: `wellmanifest`
- SHAPE: `domain_pack`
- ADOPT: `wellmanifest/new-project`, `wellmanifest/dsl`, `wellmanifest/logs`
- Runtime owner: `subactor`
- Accepted base: `9adf68fa24dd4c49ef87f51cceeb2ac25c0a2442`
- Target branch: `main`
- Outcome: one versioned, machine-checkable workspace-level location for
  ticket worktrees
- Non-goals: Git effects, lifecycle ownership, migration and cleanup
- Complexity: M; five implementation files, three components, one interface,
  zero runtime dependencies

## Validation

```text
python3 operations/conformance_test.py
python3 -m json.tool models/worktrees.schema.json
./project/governance-check.sh --actor agent
git diff --check
```

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
