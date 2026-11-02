# Ticket 024: Eliminate hardcoded user home path in conformance test fixtures

- **ID**: ticket-024
- **Owner**: agent:antigravity under SESSION_EXECUTION_AUTHORIZATION
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-02

## Goal and scope

Eliminate hardcoded `/home/tom` user home directory in `operations/conformance_test.py` test fixtures to satisfy `wellmanifest/nohardcode` rule `NOHARDCODE-009`.

## Acceptance criteria

- [x] AC-01: `pytest -q` passes without errors.
- [x] AC-02: `nohardcode_check.py --target .` reports 0 blocking errors.
- [x] AC-03: `./project/governance-check.sh --actor agent` passes with GOV-PASS.

## Participants

- Human participant: session request to audit and eliminate hardcoded paths per wellmanifest standards; no `user-*` file was created or modified.
