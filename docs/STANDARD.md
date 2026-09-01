# Wellmanifest Worktrees Standard

Version: 0.3.0

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
    |-- .branches/
    |   `-- <repo>/
    |       `-- ticket-NNN--<slug>/
    |-- .leases/
    |   `-- <repo>/
    |       `-- ticket-NNN--<slug>.json
```

The corresponding branch is `ticket/NNN-<slug>`.

Example:

```text
/home/tom/github/wellmanifest/new-project
/home/tom/github/wellmanifest/.worktrees/.branches/new-project/ticket-127--worktrees-standard
/home/tom/github/wellmanifest/.worktrees/.leases/new-project/ticket-127--worktrees-standard.json
ticket/127-worktrees-standard
```

The same segments apply on Windows with the native separator.

## Normative rules

1. The worktree root MUST be `<workspace>/.worktrees` and MUST be a sibling of
   the primary repository checkout.
2. Writable branch worktrees MUST live under the reserved `.branches`
   directory. Every repository MUST have exactly one namespace directory named
   `<repo>` below `.worktrees/.branches`; a delivery worktree inside it MUST be
   named `<ticket-id>--<slug>`.
3. A lease MUST use the same repository namespace and delivery stem under
   `.worktrees/.leases/<repo>` with the `.json` suffix.
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
10. Before any filesystem or Git effect, a runtime MUST reject an existing
    symbolic link in the canonical path from `<workspace>` through the
    delivery worktree or lease. It MUST NOT resolve such a link and continue.

## Workspace classes

Only a `delivery` workspace is a writable ticket worktree governed by the
canonical layout above. Other checkout classes must remain visibly distinct:

| Class | Writable | Canonical location | Meaning |
| --- | --- | --- | --- |
| `delivery` | yes, one lease holder | `<workspace>/.worktrees/.branches/<repo>/<ticket>--<slug>` | implementation for one publishable ticket |
| `validation-snapshot` | no | runtime-owned ephemeral storage | exact-head, read-only validation input |
| `deployment-snapshot` | no | runtime-owned deployment storage | immutable release/deployment input |
| `runtime-data` | not a Git worktree | runtime-owned state directory | queues, logs, caches and service state |

A runtime MUST NOT classify a deployment checkout, validator snapshot, cache or
service directory as a delivery worktree merely to exempt it from cleanup. A
delivery worktree MUST NOT contain another clone or another `.worktrees` root.

## Compatibility and migration

Version 3 reserves `.worktrees/.branches` for delivery worktrees. This avoids
collisions with legacy workspace indexes that placed repository symlinks at
`.worktrees/<repo>`. A runtime MUST NOT traverse or replace those symlinks.

Version 2 replaced the version 1 flat directory
`<repo>--<ticket>--<slug>` with the repository-nested form. Runtimes MUST use
version 3 for every new delivery allocation. They MUST classify registered
version 1 and version 2 paths as legacy and MUST NOT silently rename, remove or
reuse them.

Migration is an explicit runtime operation after observing dirty state, running
processes, IDE/tool bindings, lease state, open pull requests and commit
reachability. When safe and separately authorized, use `git worktree move` for
the exact registered path, update the exact lease binding, then verify `git
worktree list --porcelain`. Unknown or active work remains in place until its
delivery becomes terminal.

The nested layout adds one directory level and a repository rename changes the
namespace. These costs are preferable to an unstructured flat root: per-repo
inventory is direct, ticket numbers may repeat safely across repositories, and
tools can watch or authorize one repository subtree without name parsing.

## Lease and single-writer requirements

1. The runtime MUST acquire the exact lease before the first writable effect.
2. The lease identity MUST bind repository identity, ticket, branch and
   canonical path; a branch-name pattern or directory glob is not a lease.
3. At most one non-expired lease may authorize writes for a delivery unit.
4. Heartbeat, fencing token and compare-and-swap semantics are supplied by the
   adopted authority/change-lease contract; this pack only supplies the lease
   path.
5. A publication freeze makes the worktree read-only until the exact-head
   decision is terminal.
6. A released or expired lease does not itself prove that deletion is safe.

## Terminal audit and cleanup handoff

Cleanup is a separately authorized runtime effect. Before requesting it, the
runtime MUST record observations for dirty state, running processes, open pull
requests, remote reachability, integration into the default branch and unique
commits. Unknown or unique data is preserved. The runtime removes an exact
linked worktree through Git, prunes metadata, and only then may remove a
released disposable branch under `wellmanifest/git-lifecycle`.

## Responsibility boundaries

- `wellmanifest/worktrees` owns physical placement, deterministic names and the
  lease path contract.
- `wellmanifest/git-lifecycle` owns branch, ref and history transitions.
- `wellmanifest/merge` owns the evidence-based disposition of divergent work;
  it does not perform the effect.
- `wellmanifest/ticket-lifecycle` owns ticket intent and workflow state.
- An adopting runtime such as Subactor owns Git and filesystem effects,
  locking, observation and receipts.

## Adoption

Projects adopt this pack as `ADOPT wellmanifest/worktrees`. A runtime service
does not `HOME wellmanifest`; it consumes the standard and remains owned by its
runtime domain.
