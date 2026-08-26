# Wellmanifest Worktrees Standard

Version: 0.1.0-dev

## Purpose

This domain pack defines where an automation runtime may place a temporary
linked Git worktree for a ticket branch. It makes the relationship among a
repository, ticket, branch, worktree and lease deterministic and auditable.

This standard is query-only. It does not execute Git, create directories,
acquire credentials, publish branches or remove existing worktrees.

## Canonical layout

Given workspace root `<workspace>`, repository name `<repo>`, ticket identifier
`ticket-NNN` and normalized slug `<slug>`, the required layout is:

```text
<workspace>/
|-- <repo>/
`-- .worktrees/
    |-- .leases/
    |   `-- <repo>--ticket-NNN--<slug>.json
    `-- <repo>--ticket-NNN--<slug>/
```

The corresponding branch is `ticket/NNN-<slug>`.

Example:

```text
/home/tom/github/wellmanifest/new-project
/home/tom/github/wellmanifest/.worktrees/new-project--ticket-127--worktrees-standard
/home/tom/github/wellmanifest/.worktrees/.leases/new-project--ticket-127--worktrees-standard.json
ticket/127-worktrees-standard
```

The same segments apply on Windows with the native separator.

## Normative rules

1. The worktree root MUST be `<workspace>/.worktrees` and MUST be a sibling of
   the primary repository checkout.
2. A worktree directory MUST be named
   `<repo>--<ticket-id>--<slug>`.
3. A lease MUST use the same stem under `.worktrees/.leases` and the `.json`
   suffix.
4. A ticket branch MUST be named `ticket/NNN-<slug>` and MUST identify the same
   ticket and slug as the worktree.
5. One unit of delivery MUST map to one ticket, one branch, one worktree and one
   lease. A runtime MUST NOT create competing writable worktrees for the same
   unit of delivery.
6. Repository-local `<repo>/.worktrees`, parallel roots such as
   `<workspace>-worktrees`, nested `.worktrees/.worktrees`, temporary system
   directories and independent duplicate clones MUST NOT be used for
   publishable ticket work.
7. The repository name and slug MUST contain lowercase ASCII letters, digits
   and single hyphen-separated words. A ticket identifier MUST match
   `ticket-NNN` with at least three digits.
8. A runtime MUST validate the complete layout record before performing a Git
   or filesystem effect and SHOULD retain the validated record with its effect
   receipt.
9. Cleanup MUST be lease-aware and MUST verify ticket, branch, pull request,
   process and dirty-worktree state. This standard does not itself authorize
   cleanup.

## Responsibility boundaries

- `wellmanifest/worktrees` owns physical placement, deterministic names and the
  lease path contract.
- `wellmanifest/git-lifecycle` owns branch, ref and history transitions.
- `wellmanifest/ticket-lifecycle` owns ticket intent and workflow state.
- An adopting runtime such as Subactor owns Git and filesystem effects,
  locking, observation and receipts.

## Adoption

Projects adopt this pack as `ADOPT wellmanifest/worktrees`. A runtime service
does not `HOME wellmanifest`; it consumes the standard and remains owned by its
runtime domain.
