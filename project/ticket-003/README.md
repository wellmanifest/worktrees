# Ticket 003: Codify worktree execution boundaries

- **ID**: ticket-003
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-26

## Goal and scope

Define the canonical execution, lease and cleanup handoffs for worktrees without
duplicating Git lifecycle or merge policy.

## Acceptance criteria

- [ ] AC-01: Placement, execution workspace classes and leases have one owner.
- [ ] AC-02: Lifecycle, disposition and cleanup decisions link to their HOME packs.
- [ ] AC-03: Historical worktrees cannot be counted as normative source duplicates.

## Participants

- Human participant: unresolved; no user-* file was created.
- Agent participant: [ai-codex.md](ai-codex.md)
