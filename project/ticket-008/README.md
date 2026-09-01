# Ticket 008: Reserve collision-proof branch worktree namespace

- **ID**: ticket-008
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Reserve `.worktrees/.branches/<repo>/<ticket-NNN>--<slug>` for linked branch
worktrees so legacy repository symlinks under `.worktrees/<repo>` cannot redirect
them into a primary checkout.

## Acceptance criteria

- [ ] AC-01: Planning and validation use the reserved `.branches` namespace.
- [ ] AC-02: A symlink in any canonical path component is rejected fail-closed.
- [ ] AC-03: Existing legacy worktrees are reported but never moved automatically.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
