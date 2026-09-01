# Ticket 004: Canonicalize nested repository worktree layout

- **ID**: ticket-004
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Replace the flat shared worktree namespace with one deterministic repository
subdirectory per primary checkout:

`<workspace>/.worktrees/<repo>/<ticket-NNN>--<slug>`.

Keep leases outside delivery directories under
`<workspace>/.worktrees/.leases/<repo>/`. Publish a versioned layout query and
validation contract; do not move or delete existing worktrees automatically.

## Acceptance criteria

- [ ] AC-01: POSIX and Windows plans use the repository-nested layout.
- [ ] AC-02: Separate repositories may use the same ticket and slug without a
      path collision.
- [ ] AC-03: Flat, repo-local, parallel-root and ticket/branch-drift layouts
      fail deterministic validation.
- [ ] AC-04: The contract documents compatibility risks and a safe,
      observation-first migration route.
- [ ] AC-05: Unit and repository governance checks pass.

## Authorization and risks

The user explicitly requested execution and protected publication. This grants
SESSION_EXECUTION_AUTHORIZATION for the bounded paths in `intent.json`. It does
not authorize moving or deleting existing worktrees, deleting branches,
accessing secrets or bypassing protected review.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
