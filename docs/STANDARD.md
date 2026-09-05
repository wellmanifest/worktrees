# Wellmanifest Worktrees Standard

Version: 0.4.1

## Purpose

This domain pack defines where an automation runtime may place a linked Git
worktree for a ticket branch, where it records the corresponding lease, and how
it observes old or anomalous registrations before any migration decision.

The standard is query-only. Its planner, validator, feature probe, primary
checkout resolver and inventory do not create directories, change Git config,
move or repair worktrees, delete data, acquire credentials or publish branches.

## Canonical v4 layout

Given the primary checkout `<primaryCheckout>`, ticket `ticket-NNN` and
normalized slug `<slug>`, the only canonical delivery path is:

```text
<primaryCheckout>/
|-- .git/
|-- .subactor/
|   `-- leases/
|       `-- ticket-NNN--<slug>.json
`-- worktrees/
    `-- ticket-NNN--<slug>/
```

The corresponding branch is `ticket/NNN-<slug>`. The path and lease stem are
identical. The same segments apply on Windows with native separators.

Example:

```text
/home/tom/github/subactor/platform
/home/tom/github/subactor/platform/worktrees/ticket-281--twin-account-runtime
/home/tom/github/subactor/platform/.subactor/leases/ticket-281--twin-account-runtime.json
ticket/281-twin-account-runtime
```

Adopters MUST root-ignore `/worktrees/` and `/.subactor/`; raw sessions,
snapshots and lease state are runtime data, not repository artifacts.

## Normative allocation rules

1. A runtime MUST resolve the primary checkout from Git's registered worktree
   list. When allocation begins in a ticket worktree, it MUST NOT treat that
   linked checkout as the primary or append another `worktrees` directory to
   it.
2. A delivery worktree MUST be exactly
   `<primaryCheckout>/worktrees/<ticket>--<slug>`. Repository-external central
   roots, `.worktrees`, `/tmp`, duplicate clones and nested
   `worktrees/.../worktrees` are noncanonical for new allocations.
3. A lease MUST be exactly
   `<primaryCheckout>/.subactor/leases/<ticket>--<slug>.json` and bind the same
   repository identity, ticket, branch and canonical path.
4. The layout record MUST declare `schema=wellmanifest.worktrees/v4`,
   `kind=layout-record`, `linkMode=relative` and
   `minimumGitVersion=2.51.0`.
5. Before its first Git or filesystem effect, a runtime MUST validate the
   complete layout record, reject an existing symlink in any canonical
   component, acquire the exact lease and persist the validated record with
   its effect receipt.
6. One delivery unit maps to one ticket, branch, worktree and lease. A branch
   pattern, path glob or non-expired lease for another path grants no write
   authority.
7. The repository name and slug contain lowercase ASCII letters, digits and
   single hyphen-separated words. A ticket matches `ticket-NNN` with at least
   three digits.
8. The primary checkout and ticket worktrees MUST remain siblings in Git's
   worktree registry even though their filesystem paths are nested. A runtime
   MUST NOT recursively treat the nested worktree as primary-repository
   content.

## Relative Git linkage and feature gate

Version 4 requires Git 2.51.0 or newer and both of these supported options:

```text
git worktree add --relative-paths ...
git worktree repair --relative-paths ...
```

Checking only a version string is insufficient. The runtime MUST feature-probe
the `add` and `repair` help surfaces before allocation. It MAY set repository
configuration `worktree.useRelativePaths=true`, but every creation transaction
SHOULD still pass `--relative-paths` explicitly so its receipt is self-evident.

Relative linkage is part of conformance, not an optimization. Both the linked
worktree's `.git` pointer and the primary repository's worktree administration
record must remain valid when the complete primary checkout directory,
including its nested `worktrees` subtree, is renamed or relocated.

## Primary checkout resolution

The query may start in the primary checkout or any registered linked worktree.
It reads `git worktree list --porcelain -z` and selects Git's primary record.
It fails for a bare repository or an empty/inconsistent registry. It does not
infer the primary from the current directory name, follow an arbitrary symlink,
scan parent directories for lookalike clones or create missing registrations.

This rule prevents an allocator invoked from
`<primaryCheckout>/worktrees/<ticket>--<slug>` from producing a nested
`.../<ticket>--<slug>/worktrees/...` allocation.

## Read-only inventory

Inventory consumes Git's registered worktree records and returns
`kind=inventory-record`, `readOnly=true`. Its repository name is an observed
basename, preserved exactly, including `.github`, mixed case, underscores and
spaces. Inventory rejects empty names, `.`/`..`, path separators and NUL. The
normalized repository-name and slug rules above apply to allocation only;
observing an existing checkout does not authorize creating one.

Path classification is deterministic:

| Classification | Recognized registered path |
| --- | --- |
| `primary` | exact primary checkout |
| `canonical-v4` | `<primary>/worktrees/<ticket>--<slug>` |
| `legacy-v3` | `<workspace>/.worktrees/.branches/<repo>/<ticket>--<slug>` |
| `legacy-v2` | `<workspace>/.worktrees/<repo>/<ticket>--<slug>` |
| `legacy-v1` | `<workspace>/.worktrees/<repo>--<ticket>--<slug>` |
| `system-temp` | any registered POSIX path below `/tmp` |
| `unknown` | every other registered location |

An entry also carries its observed HEAD, branch, detached/locked/prunable state
and any anomaly. `duplicate-delivery` is attached to every non-primary entry
when more than one registration has the same normalized ticket/slug or branch.
An anomaly does not erase the path's layout classification.

The inventory is deliberately limited to registered worktrees. Finding an
unregistered directory or independent clone requires a separate bounded
filesystem inventory owned by the adopting runtime. Neither absence from this
record nor a `prunable` flag authorizes cleanup.

## Compatibility and explicit migration

Versions 1 through 3 are legacy observation classes. Runtimes MUST use v4 only
for new allocations after adoption and MUST preserve every legacy, `/tmp`,
duplicate or unknown entry until a separately authorized lifecycle operation
has established dirty state, active processes and IDEs, lease state, pull
requests, HEAD reachability and unique commits.

There is no automatic move, repair, delete, prune or branch removal in this
pack. In particular, a runtime MUST NOT use broad `git clean` on a primary
checkout containing nested worktrees. Cleanup targets one verified registered
path through Git and remains owned by `wellmanifest/git-lifecycle` and the
adopting runtime.

For a v4-shaped worktree whose old absolute administration links became stale
after the complete primary directory was relocated, the separately authorized
repair is exact and path-bound:

```text
git -C <primary-after-relocation> worktree repair --relative-paths \
  <primary-after-relocation>/worktrees/<ticket>--<slug>
```

The runtime MUST demonstrate failure before repair, run the command for the
exact registered path, and then verify the linked checkout, primary registry,
relative pointers, lease binding and `git worktree list --porcelain -z`.
Repair does not make an unsafe worktree safe to delete or move.

## Workspace classes

Only a `delivery` workspace is writable under this layout:

| Class | Writable | Location and meaning |
| --- | --- | --- |
| `delivery` | one lease holder | `<primary>/worktrees/<ticket>--<slug>` |
| `validation-snapshot` | no | runtime-owned immutable exact-head input |
| `deployment-snapshot` | no | runtime-owned deployment input |
| `runtime-data` | not a worktree | `.subactor` leases, sessions, receipts and caches |

A runtime MUST NOT relabel a deployment checkout, validator snapshot, cache,
service directory or duplicate clone as `delivery` to exempt it from audit.

## Responsibility boundaries

- `wellmanifest/worktrees` owns placement, deterministic names, relative-link
  requirements, the lease path and observation classifications.
- `wellmanifest/git-lifecycle` owns branch, ref, history, repair and cleanup
  effects.
- `wellmanifest/merge` owns evidence-based disposition of divergent work.
- `wellmanifest/ticket-lifecycle` owns ticket intent and workflow state.
- An adopter such as Subactor owns Git/filesystem effects, locks, IDE/process
  observation, receipts and external recovery storage.

Projects use `ADOPT wellmanifest/worktrees`; a runtime service does not `HOME`
this domain pack.
