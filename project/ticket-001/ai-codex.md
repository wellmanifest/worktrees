---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-001
---
# Participant: codex (AI agent)

## Understanding

The organization currently uses repo-local `.worktrees`, a parallel
`subactor-worktrees` root, workspace-level `.worktrees`, and accidentally nested
roots. The standard must select one portable layout without absorbing Git or
ticket lifecycle responsibilities.

## Execution plan

1. Specify the canonical workspace-level layout and ownership boundaries.
2. Publish a schema and pure planner/validator for POSIX and Windows paths.
3. Prove representative valid and invalid layouts and run governance checks.

## Actual changes

- Initialized the bounded ticket and recorded SESSION_EXECUTION_AUTHORIZATION
  from the request to execute this work.
- Defined a workspace-level `.worktrees` root, deterministic worktree names,
  lease locations and ticket branch names.
- Added a machine-readable schema and dependency-free conformance CLI.
- Added unit coverage for POSIX, Windows and known layout drift patterns.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
