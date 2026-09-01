# Architecture

`wellmanifest/worktrees` is a data-only `domain_pack`.

```text
ticket intent
    -> layout query
    -> validated layout record
    -> runtime Git/filesystem effect
    -> effect receipt
```

The pack has no daemon, credential access, network access or authority to
change a repository. Its only executable artifact is a pure conformance tool
that derives and validates strings. This keeps policy portable while allowing
Subactor, Semcod or another runtime to implement the effect and operational
controls.

The layout record is the boundary interface. Consumers should persist its
`wellmanifest.worktrees/v2` representation beside the receipt for worktree
creation, use or cleanup.

The shared root has two parallel repository namespaces: delivery paths under
`.worktrees/<repo>/` and non-worktree lease data under
`.worktrees/.leases/<repo>/`. Keeping `.leases` outside a Git worktree subtree
prevents discovery tools from treating runtime state as a checkout.

## Deliberate non-ownership

The pack does not duplicate Git policy, merge policy or ticket policy. It
references their stable pack identifiers and supplies only the path facts they
consume. Vendored bytes in `wellmanifest/new-project` are immutable,
digest-bound adoption projections, not a second source of truth.

`wellmanifest/git` is a navigation alias for `wellmanifest/git-lifecycle`.
Creating both as independent standards would make branch semantics ambiguous
and is therefore forbidden by the composition map in `wellmanifest/new-project`.
