# Ticket 009: Adopt new-project 0.19.22 before Worktrees v4

- **ID**: ticket-009
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Adopt the published, immutable `wellmanifest/new-project` 0.19.22 package at
`f7fe7163e886d5540cedf83d383b6dd99daafd7c` before changing the Worktrees
domain contract. The adoption refreshes only the package-managed governance
projection; Worktrees remains at its current domain version.

## Acceptance criteria

- [ ] AC-01: `goal governance adopt --check` reports no managed drift for the
      exact published revision.
- [ ] AC-02: the Worktrees domain tests remain green.
- [ ] AC-03: the exact governed diff passes the agent gate.
- [ ] AC-04: issue `wellmanifest/worktrees#12` is linked by the material PR.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
