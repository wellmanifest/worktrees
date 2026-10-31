# ticket-023: Select native path style for worktree inventory CLI

- **ID**: ticket-023
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, tests, repair and
protected merge. This bounded source-standard repair resolves a reproduced
prerequisite of governance adoption; it grants no merge approval.

## Goal and scope

The inventory library supports Windows paths, but the CLI defaults to POSIX and
rejects a native Windows primary as non-absolute. Select the host path style in
the CLI, retain the Worktrees v5 schema and read-only behavior, and join version
0.5.4 to this material change. Preserve unknown worktrees and every authority gate.

## Acceptance criteria

- [x] AC-01: The actual inventory CLI produces valid inventories for both native
  Windows and POSIX observations; the Windows regression fails before the fix.
- [ ] AC-02: Domain tests and governance pass; independent exact-head protected
  checks and approval precede merge. Keep this ticket in PUBLICATION until the
  controller's external terminal receipt.

## Local validation

The real inventory CLI probe reproduces the Windows failure on the original
source while POSIX succeeds. After the repair, all 20 domain tests pass,
including both native styles and valid read-only v5 records. The schema parses,
diff checks pass and native governance reports zero errors and warnings.
Protected CI, OneDev and independent exact-head approval remain required;
local results do not grant merge authority.
