# Ticket 010: Make repository-local relative worktrees canonical

- **ID**: ticket-010
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-01

## Goal and scope

Publish the breaking `wellmanifest.worktrees/v4` contract. New delivery
worktrees are planned at `<primaryCheckout>/worktrees/<ticket>--<slug>`, leases
at `<primaryCheckout>/.subactor/leases/<ticket>--<slug>.json`, and Git linkage
uses relative paths. The allocator resolves the primary checkout even when its
query starts inside an existing ticket worktree.

Add observation-only inventory for registered v1, v2, v3, v4, `/tmp`,
duplicate and unknown paths. Document and test exact repair after a primary
repository rename without performing migration on any live checkout.

## Acceptance criteria

- [ ] AC-01: POSIX and Windows planners emit only the repository-local v4 path,
      local lease path and `linkMode=relative`.
- [ ] AC-02: inventory classifies all declared legacy/anomaly classes and never
      moves, deletes or repairs an observed checkout.
- [ ] AC-03: a scratch repository fails after relocation with absolute links
      and passes after `git worktree repair --relative-paths`.
- [ ] AC-04: a feature probe rejects Git older than 2.51.0 or installations
      lacking relative-path support.
- [ ] AC-05: domain tests and exact-diff governance checks pass; the material
      PR links issue `wellmanifest/worktrees#13`.

## Authorization and risks

The user explicitly requested implementation, push and PR creation, providing
SESSION_EXECUTION_AUTHORIZATION for the bounded paths in `intent.json`.
Existing worktrees and clones are evidence only: this ticket does not authorize
their movement, repair, cleanup, deletion or branch removal. The present
ticket remains in its final v3-created central worktree until its PR is
terminal.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
