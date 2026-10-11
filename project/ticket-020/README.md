# Ticket 020: add-stale-registration-and-merged-leftover-anomalies

- **ID**: ticket-020
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-11

## Goal and scope

Standardize `stale-registration` and `merged-leftover` anomaly classifications in `models/worktrees.schema.json`, `operations/conformance.py`, `operations/conformance_test.py`, and `docs/information/worktree-layout.md`.
Enables automation runtimes and fleet tools (`diagit`, `subactor`) to deterministically report stale git worktree registrations and clean merged worktree leftovers awaiting lifecycle retirement.

## Acceptance criteria

- [x] AC-01: `models/worktrees.schema.json` declares `stale-registration` and `merged-leftover` in `anomalies` schema.
- [x] AC-02: `operations/conformance.py` supports detecting and rebuilding `stale-registration` and `merged-leftover` inventory anomalies.
- [x] AC-03: `operations/conformance_test.py` validates inventory anomaly detection and deterministic validation.
- [x] AC-04: `docs/information/worktree-layout.md` documents both anomalies in the inventory table.
- [x] AC-05: `./project/governance-check.sh` passes with 0 errors and 0 warnings.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
