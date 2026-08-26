# Ticket 002: Bootstrap repository CI required checks

- **ID**: ticket-002
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-26

## Goal and scope

Add the repository-owned CI workflow omitted during the initial package
bootstrap. Its two job display names must exactly match the immutable
`.governance/required-checks.json` declaration. The ticket does not change the
adopted governance package or external GitHub rulesets.

The repository manifest assigns `.github/**` to the `infrastructure`
workstream; that existing ownership is used without widening it.

## Acceptance criteria

- [ ] AC-01: Repository governance passes with the published CI workflow.
- [ ] AC-02: The workflow publishes exactly `test` and `windows-governance`.

## Session authorization

The user's request to create and publish the standard includes the minimum
repository bootstrap required for protected delivery. No destructive action,
secret access or external ruleset mutation is authorized.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
