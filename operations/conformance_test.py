import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from conformance import (
    feature_probe,
    inventory,
    plan,
    resolve_primary_checkout,
    validate,
    validate_filesystem,
)


class WorktreeConformanceTest(unittest.TestCase):
    def test_posix_layout(self):
        record = plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            primary_checkout="/home/tom/github/wellmanifest/new-project",
        )
        self.assertEqual(record["branch"], "ticket/127-worktrees-standard")
        self.assertEqual(
            record["worktreePath"],
            "/home/tom/github/wellmanifest/new-project/worktrees/ticket-127--worktrees-standard",
        )
        self.assertEqual(
            record["leasePath"],
            "/home/tom/github/wellmanifest/new-project/.subactor/leases/"
            "ticket-127--worktrees-standard.json",
        )
        self.assertEqual(record["linkMode"], "relative")
        self.assertEqual(record["minimumGitVersion"], "2.51.0")
        self.assertEqual(validate(record), [])

    def test_windows_layout(self):
        record = plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            primary_checkout="C:\\github\\wellmanifest\\new-project",
            path_style="windows",
        )
        self.assertEqual(
            record["worktreePath"],
            "C:\\github\\wellmanifest\\new-project\\worktrees\\ticket-127--worktrees-standard",
        )
        self.assertEqual(
            record["leasePath"],
            "C:\\github\\wellmanifest\\new-project\\.subactor\\leases\\"
            "ticket-127--worktrees-standard.json",
        )
        self.assertEqual(validate(record), [])

    def test_rejects_old_central_layout_and_absolute_link_mode(self):
        record = plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            primary_checkout="/workspace/wellmanifest/new-project",
        )
        record["worktreePath"] = (
            "/workspace/wellmanifest/.worktrees/.branches/new-project/"
            "ticket-127--worktrees-standard"
        )
        record["linkMode"] = "absolute"
        self.assertIn("noncanonical:worktreePath", validate(record))
        self.assertIn("noncanonical:linkMode", validate(record))

    def test_rejects_relative_primary_checkout(self):
        with self.assertRaisesRegex(ValueError, "primaryCheckout must be absolute"):
            plan(
                repository="wellmanifest/new-project",
                repository_name="new-project",
                ticket="ticket-127",
                slug="worktrees-standard",
                primary_checkout="new-project",
            )

    @unittest.skipIf(os.name == "nt", "POSIX symlink fixture")
    def test_rejects_symlink_inside_repository_local_namespace(self):
        with tempfile.TemporaryDirectory() as temporary:
            primary = Path(temporary) / "new-project"
            primary.mkdir()
            redirected = primary / "redirected"
            redirected.mkdir()
            (primary / "worktrees").symlink_to(redirected)
            record = plan(
                repository="wellmanifest/new-project",
                repository_name="new-project",
                ticket="ticket-127",
                slug="worktrees-standard",
                primary_checkout=str(primary),
            )
            self.assertIn(
                "symlink_component:worktreesRoot:worktrees",
                validate_filesystem(record),
            )

    def test_inventory_classifies_legacy_temp_duplicate_and_unknown(self):
        primary = "/workspace/wellmanifest/new-project"
        registered = [
            {"path": primary, "head": "a" * 40, "branch": "refs/heads/main"},
            {
                "path": f"{primary}/worktrees/ticket-127--worktrees-standard",
                "head": "b" * 40,
                "branch": "refs/heads/ticket/127-worktrees-standard",
            },
            {
                "path": (
                    "/workspace/wellmanifest/.worktrees/.branches/new-project/"
                    "ticket-127--worktrees-standard"
                ),
                "head": "b" * 40,
                "branch": "refs/heads/ticket/127-worktrees-standard",
            },
            {
                "path": (
                    "/workspace/wellmanifest/.worktrees/new-project/"
                    "ticket-128--legacy-two"
                ),
                "head": "c" * 40,
                "branch": "refs/heads/ticket/128-legacy-two",
            },
            {
                "path": (
                    "/workspace/wellmanifest/.worktrees/"
                    "new-project--ticket-129--legacy-one"
                ),
                "head": "d" * 40,
                "branch": "refs/heads/ticket/129-legacy-one",
            },
            {
                "path": "/tmp/new-project-ticket-130",
                "head": "e" * 40,
                "branch": "refs/heads/ticket/130-temporary",
            },
            {
                "path": "/opt/unknown/new-project-copy",
                "head": "f" * 40,
                "branch": "refs/heads/experiment",
            },
        ]
        record = inventory(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            primary_checkout=primary,
            registered=registered,
        )
        self.assertEqual(
            [entry["classification"] for entry in record["entries"]],
            [
                "primary",
                "canonical-v4",
                "legacy-v3",
                "legacy-v2",
                "legacy-v1",
                "system-temp",
                "unknown",
            ],
        )
        self.assertEqual(
            record["summary"]["anomalies"], {"duplicate-delivery": 2}
        )
        self.assertIn("duplicate-delivery", record["entries"][1]["anomalies"])
        self.assertIn("duplicate-delivery", record["entries"][2]["anomalies"])
        self.assertTrue(record["readOnly"])
        self.assertEqual(validate(record), [])

    def test_feature_probe_reports_version_and_both_flags(self):
        result = feature_probe()
        self.assertIn("gitVersion", result)
        self.assertEqual(result["supported"], all((
            result["versionSupported"],
            result["worktreeAddRelativePaths"],
            result["worktreeRepairRelativePaths"],
        )))

    def test_feature_probe_rejects_git_older_than_minimum(self):
        def old_git(args, **_kwargs):
            if args[-1] == "--version":
                return subprocess.CompletedProcess(
                    args, 0, b"git version 2.50.2\n", b""
                )
            return subprocess.CompletedProcess(
                args, 129, b"", b"usage: --[no-]relative-paths\n"
            )

        result = feature_probe(runner=old_git)
        self.assertFalse(result["versionSupported"])
        self.assertTrue(result["worktreeAddRelativePaths"])
        self.assertTrue(result["worktreeRepairRelativePaths"])
        self.assertFalse(result["supported"])

    @unittest.skipIf(os.name == "nt", "POSIX relocation fixture")
    def test_repository_rename_requires_then_passes_exact_relative_repair(self):
        if not feature_probe()["supported"]:
            self.skipTest("Git 2.51 relative worktree support is unavailable")

        def git(*args, cwd=None, check=True):
            return subprocess.run(
                ["git", *args],
                cwd=cwd,
                check=check,
                capture_output=True,
                text=True,
            )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            primary = root / "project-before-rename"
            primary.mkdir()
            git("init", "-b", "main", cwd=primary)
            git("config", "user.name", "Worktrees Test", cwd=primary)
            git("config", "user.email", "worktrees@example.invalid", cwd=primary)
            (primary / "tracked.txt").write_text("fixture\n", encoding="utf-8")
            git("add", "tracked.txt", cwd=primary)
            git("commit", "-m", "fixture", cwd=primary)

            linked = primary / "worktrees" / "ticket-130--rename-repair"
            git(
                "-c",
                "worktree.useRelativePaths=false",
                "worktree",
                "add",
                "--no-relative-paths",
                "-b",
                "ticket/130-rename-repair",
                str(linked),
                "HEAD",
                cwd=primary,
            )
            self.assertEqual(resolve_primary_checkout(str(linked)), str(primary))

            relocated = root / "project-after-rename"
            primary.rename(relocated)
            relocated_linked = relocated / "worktrees" / linked.name
            before = git("-C", str(relocated_linked), "status", check=False)
            self.assertNotEqual(before.returncode, 0)

            git(
                "-C",
                str(relocated),
                "worktree",
                "repair",
                "--relative-paths",
                str(relocated_linked),
            )
            after = git("-C", str(relocated_linked), "status", "--porcelain")
            self.assertEqual(after.returncode, 0)
            self.assertEqual(resolve_primary_checkout(str(relocated_linked)), str(relocated))
            link_file = (relocated_linked / ".git").read_text(encoding="utf-8")
            self.assertNotIn(str(primary), link_file)
            self.assertTrue(link_file.startswith("gitdir: ../../.git/worktrees/"))


if __name__ == "__main__":
    unittest.main()
