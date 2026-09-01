#!/usr/bin/env python3

import unittest

from conformance import plan, validate


class WorktreeConformanceTest(unittest.TestCase):
    def test_posix_layout(self):
        record = plan(
            repository="https://github.com/wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            workspace_root="/home/tom/github/wellmanifest",
        )
        self.assertEqual(record["branch"], "ticket/127-worktrees-standard")
        self.assertEqual(
            record["worktreePath"],
            "/home/tom/github/wellmanifest/.worktrees/new-project/ticket-127--worktrees-standard",
        )
        self.assertEqual(validate(record), [])

    def test_windows_layout(self):
        record = plan(
            repository="https://github.com/wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            workspace_root="C:\\github\\wellmanifest",
            path_style="windows",
        )
        self.assertEqual(
            record["leasePath"],
            "C:\\github\\wellmanifest\\.worktrees\\.leases\\new-project\\ticket-127--worktrees-standard.json",
        )
        self.assertEqual(validate(record), [])

    def test_rejects_repository_local_root(self):
        record = plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            workspace_root="/workspace/wellmanifest",
        )
        record["worktreesRoot"] = "/workspace/wellmanifest/new-project/.worktrees"
        self.assertIn("noncanonical:worktreesRoot", validate(record))

    def test_rejects_ticket_branch_drift(self):
        record = plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            workspace_root="/workspace/wellmanifest",
        )
        record["branch"] = "ticket/128-worktrees-standard"
        self.assertIn("noncanonical:branch", validate(record))

    def test_rejects_parallel_organization_root(self):
        record = plan(
            repository="subactor/subllm",
            repository_name="subllm",
            ticket="ticket-012",
            slug="release-1-4-1",
            workspace_root="/home/tom/github/subactor",
        )
        record["worktreePath"] = "/home/tom/github/subactor-worktrees/subllm-ticket12-release-1-4-1"
        self.assertIn("noncanonical:worktreePath", validate(record))

    def test_repository_namespaces_prevent_cross_repo_collision(self):
        left = plan(
            repository="subactor/platform",
            repository_name="platform",
            ticket="ticket-123",
            slug="precise-change",
            workspace_root="/workspace/subactor",
        )
        right = plan(
            repository="subactor/core",
            repository_name="core",
            ticket="ticket-123",
            slug="precise-change",
            workspace_root="/workspace/subactor",
        )
        self.assertNotEqual(left["worktreePath"], right["worktreePath"])
        self.assertEqual(left["repositoryWorktreesRoot"], "/workspace/subactor/.worktrees/platform")

    def test_rejects_legacy_flat_layout(self):
        record = plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            workspace_root="/workspace/wellmanifest",
        )
        record["worktreePath"] = "/workspace/wellmanifest/.worktrees/new-project--ticket-127--worktrees-standard"
        self.assertIn("noncanonical:worktreePath", validate(record))


if __name__ == "__main__":
    unittest.main()
