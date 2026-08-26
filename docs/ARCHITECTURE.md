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
`wellmanifest.worktrees/v1` representation beside the receipt for worktree
creation, use or cleanup.
