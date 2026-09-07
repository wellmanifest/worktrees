# Ticket 014: Git feature probe context

- **ID**: ticket-014
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: user requests publication, current Wellmanifest adoption and fixes for confusion during parallel agent work.

## Acceptance criteria

- [x] AC-01: Same feature result inside and outside repositories, including inherited Git selectors; old Git remains unsupported.
- [x] AC-02: Caller files and Git state are unchanged; domain and governance checks pass.

Canonical rationale: [worktree layout](../../docs/information/worktree-layout.md).

Validation: 15 domain tests passed; managed governance and trusted documentation checker passed. Explicit repository probing works from an organization directory without filesystem changes.
