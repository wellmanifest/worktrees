# Ticket 025: Harden worktree record validation and git selector isolation

- **ID**: ticket-025
- **Owner**: human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Harden `operations/conformance.py` and keep both `operations/*.py` modules strictly below 500 lines while preserving single-file compatibility for downstream bundlers:

1. Strip inherited `GIT_*` environment variables inside `_git_output` so `registered_worktrees`, `resolve_primary_checkout`, `plan --from-worktree`, and `inventory --from-worktree` cannot be redirected by caller hook selectors.
2. Guard `validate`, `validate_layout`, `validate_inventory`, and `validate_filesystem` against non-dict inputs and malformed `entries`/`anomalies`/`head`/`branch`/boolean flags without raising unhandled `AttributeError` or `TypeError`.
3. Validate non-empty `repository` strings in `plan` and `inventory`, reject duplicate JSON keys via `strict_json_loads`, and fail closed on symlinked or malformed JSON inputs in `conformance.py validate`.

## Acceptance criteria

- [x] AC-01: Both `operations/conformance.py` and `operations/conformance_test.py` stay strictly below 500 lines and pass `python3 operations/conformance_test.py`.
- [x] AC-02: Regression tests verify `GIT_*` selector isolation in `inventory`/`plan`, fail-closed validation on non-dict records, malformed inventory entries, empty `repository`, duplicate JSON keys, and symlinked record files.
- [x] AC-03: Passes `./project/governance-check.sh` and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
