# worktrees

Canonical Wellmanifest standard for the physical placement and lease identity
of temporary Git worktrees.

- Normative rules: [`docs/STANDARD.md`](docs/STANDARD.md)
- Responsibility model: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Machine contract: [`models/worktrees.schema.json`](models/worktrees.schema.json)
- Pure planner and validator: [`operations/conformance.py`](operations/conformance.py)

This pack owns paths, names and lease identity only. Branch and remote state are
owned by `wellmanifest/git-lifecycle`; divergent-work disposition is owned by
`wellmanifest/merge`; ticket state is owned by `wellmanifest/ticket-lifecycle`.
The alias `wellmanifest/git` resolves to `wellmanifest/git-lifecycle` and MUST
NOT be implemented as another pack.
