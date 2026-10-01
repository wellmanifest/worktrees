# Ticket 019: Allocator result contract: no glob-derived targets, stop on refusal, no hand-moved scaffolds

- **ID**: ticket-019
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-01

## Goal and scope

Close the allocation gap seen on 2026-10-01: a legacy allocator (new-project
0.20.32/0.20.35 in semcod/monag and subactor/reflex) scaffolds tickets in the
primary checkout without a worktree and reports success only as prose. After a
refused allocation an agent inferred "its" ticket from a directory glob and
deleted an existing tracked ticket (restored from Git). The v5 layout document
gains rules 9-13: machine-readable allocation result, identity only from that
result, stop after refusal, destructive effects only on paths the attempt
created, and no hand-moved scaffolds or hand-written leases for legacy
allocators.

## Acceptance criteria

- [x] AC-01: Rules 9-13 in docs/information/worktree-layout.md (version 6).
- [ ] AC-02: wellmanifest/new-project allocator emits the machine-readable result (follow-up).
- [ ] AC-03: Conformance reports adopters whose allocator cannot create v5 worktrees (follow-up).

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
