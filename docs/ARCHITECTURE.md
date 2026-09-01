# Architecture

`wellmanifest/worktrees` is a data-only `domain_pack`. Version 4 separates pure
queries from runtime effects:

```text
current checkout
    -> registered-worktree query
    -> primary checkout resolver
    -> feature probe
    -> v4 layout planner + validator
    -> adopting runtime lease/Git/filesystem transaction
    -> external effect receipt

registered-worktree query
    -> read-only v1/v2/v3/v4/temp/unknown classifier
    -> duplicate anomaly projection
    -> lifecycle decision outside this pack
```

The pack has no daemon, credential access, network access or authority to alter
a repository. `operations/conformance.py` executes only bounded Git queries for
the primary resolver, feature probe and inventory. Planning and validation are
pure string/data operations. It never invokes `worktree add`, `move`, `repair`,
`remove`, `prune`, `clean` or branch mutation.

## Boundary records

`models/worktrees.schema.json` defines two closed
`wellmanifest.worktrees/v4` record kinds:

- `layout-record` is the exact proposed allocation, including repository and
  ticket identity, primary checkout, delivery path, lease path,
  `linkMode=relative` and the minimum Git version.
- `inventory-record` is a reproducible read-only projection of Git's registered
  worktrees, path classifications and duplicate-delivery anomalies.

Consumers persist the validated layout beside the creation/use/cleanup receipt.
Inventory is evidence, not authority; it cannot widen ticket intent, grant a
lease or select a destructive target.

## Repository-local topology

The primary repository is the stable allocation anchor:

```text
<primary>/
|-- .git/                         primary Git administration
|   `-- worktrees/<admin>/        linked-worktree administration
|-- .subactor/leases/<stem>.json runtime state, root-ignored
`-- worktrees/<stem>/             linked checkout, root-ignored
    `-- .git                      relative administrative pointer
```

Because both sides of Git's administrative link move with `<primary>`, a v4
checkout remains addressable after a whole-directory rename. Relative Git
links are therefore an invariant of the boundary record. The feature probe
requires Git 2.51.0 plus the actual `add` and `repair` options rather than
assuming a vendor version exposes the feature.

Starting allocation inside a linked worktree does not change the anchor. The
resolver reads Git's NUL-delimited worktree registry and returns its primary
record, preventing recursive `worktrees` nesting.

## Observation and migration boundary

The classifier recognizes only registered paths. It preserves the underlying
layout class when marking a duplicate, so an operator can distinguish a v3
duplicate from an unknown duplicate without rescanning prose. `/tmp` is an
explicit POSIX class because system temporary storage is not durable delivery
state.

Migration remains a runtime effect. The pack documents the exact
`git worktree repair --relative-paths <path>` recovery shape and tests it only
inside a disposable scratch repository. Live paths are never repaired or moved
by conformance or inventory. Dirty/unknown data, process and IDE bindings,
leases, PR state and commit reachability must be observed before a separately
authorized lifecycle controller selects any effect.

## Deliberate non-ownership

The pack does not duplicate Git lifecycle, merge or ticket policy. Vendored
bytes in `wellmanifest/new-project` are immutable digest-bound adoption
projections, not a second source of truth. Runtime session and recovery data
belongs to the adopter's ignored `.subactor` state and external receipt store,
not to this repository contract.
