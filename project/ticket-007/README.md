# Ticket 007: Remove legacy mandatory ticket carriers

- **ID**: ticket-007
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Remove legacy target overrides that require optional participant prose,
changelog and raw log carrier files. Retain only the bounded ticket `README.md`
and machine-readable `intent.json` required by new-project 0.19.18.

## Acceptance criteria

- [ ] AC-01: New tickets require only `README.md` and `intent.json`.
- [ ] AC-02: Agent prose and raw log files remain optional.
- [ ] AC-03: Repository governance passes with this minimal ticket itself.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
