# Ticket 012: Repository-local hidden worktrees

- **ID**: ticket-012
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-07

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requested implementation and rollout of `[repo]/.worktrees/<ticket>--<slug>` across the related standards. This authorizes the bounded standard change and protected publication, including this ticket in the explicitly requested new location. Independent exact-head review remains required.

Canonical result: [worktree layout](../../docs/information/worktree-layout.md). Cross-repository rollout is owned by subactor/docs.

## Acceptance criteria

- [ ] AC-01: New v5 POSIX and Windows plans use `.worktrees`, preserve ticket-derived names, relative links and local leases; v4 inventory remains read-only.
- [ ] AC-02: Domain tests and governance pass; protected publication produces an observed merge receipt.
