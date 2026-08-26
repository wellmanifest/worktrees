# Changelog

## 0.1.0-dev - 2026-08-26

- Establish the governed repository baseline.
- Define canonical workspace-level delivery placement and lease identity.
- Separate delivery worktrees from validation/deployment snapshots and runtime
  data, with a single-writer and exact-head freeze handoff.
- Delegate branch, merge and ticket semantics to their owning packs.
