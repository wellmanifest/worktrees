# Ticket 011: Inventory observed repository names

- **ID**: ticket-011
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-05

## Goal and scope

Fix the reproduced Goal workspace audit crash for the existing .github repository in the owning Worktrees contract. Publish the material 0.4.1 patch through Goal and protected Validator.

## Acceptance criteria

- [x] AC-01: Inventory round-trips observed .github, mixed-case and underscore names on POSIX and Windows.
- [x] AC-02: Allocation restrictions remain enforced; invalid observed basenames fail explicitly.
- [x] AC-03: Schema and documentation describe the distinction; conformance and governance pass before protected publication.

## Authorization

SESSION_EXECUTION_AUTHORIZATION: user requested repair and publication through goal -a, then continued after the workspace audit naming failure was reported. This bounded upstream fix addresses that failure.

## Validation

11 conformance tests passed, including POSIX/Windows observed basenames and unchanged allocation rejection. JSON Schema parsed, invalid-name schema checks passed, and managed governance plus diff whitespace checks passed.
