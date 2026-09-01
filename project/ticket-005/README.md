# Ticket 005: Upgrade governance to material-delivery standard

- **ID**: ticket-005
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Upgrade the repository's immutable `wellmanifest/new-project` adoption from
0.18.10 to 0.19.18. The new gate permits bounded intent in the first material
commit, rejects carrier-only delivery, uses external terminal receipts and
ships the canonical worktree layout checker projection.

## Acceptance criteria

- [ ] AC-01: Goal reports an immutable, published 0.19.18 adoption with no
      managed-file drift.
- [ ] AC-02: The deterministic governance gate accepts the atomic adoption.
- [ ] AC-03: Required-check projection and repository tests remain green.

## Authorization and non-goals

The request to execute this cleanup provides SESSION_EXECUTION_AUTHORIZATION
for the exact adoption diff. It does not authorize moving worktrees, changing
the worktree domain contract, or creating a repository-only closure commit.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
