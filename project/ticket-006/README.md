# Ticket 006: Separate domain tests from range-aware governance

- **ID**: ticket-006
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Make the required `test` job test the worktrees domain contract. Keep
repository-governance evaluation exclusively in the managed
`governance / enforce` job, which supplies the exact PR base/head range.

## Acceptance criteria

- [ ] AC-01: `test` runs the Python conformance suite and validates the schema.
- [ ] AC-02: The managed range-aware governance job remains the only governance
      evaluator in pull-request CI.
- [ ] AC-03: All four declared required checks pass.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
