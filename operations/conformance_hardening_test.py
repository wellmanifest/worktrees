"""Hardening and regression tests for wellmanifest.worktrees/v5 conformance."""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import conformance
from conformance import inventory, plan, validate, validate_filesystem


class WorktreeHardeningTest(unittest.TestCase):
    def test_operations_python_modules_stay_below_500_lines(self) -> None:
        ops_dir = Path(__file__).resolve().parent
        for py_path in sorted(ops_dir.glob("*.py")):
            count = len(py_path.read_text(encoding="utf-8").splitlines())
            self.assertLess(count, 500, f"{py_path.name} has {count} lines")

    def test_planner_and_inventory_reject_empty_or_non_string_repository_and_checkout(self) -> None:
        for bad_repo in ("", "   ", "org\0repo", None, 123):
            with self.subTest(bad_repo=bad_repo), self.assertRaises(ValueError):
                inventory(
                    repository=bad_repo,
                    repository_name="repo",
                    primary_checkout="/workspace/repo",
                    registered=[],
                )
            with self.subTest(planner_repo=bad_repo), self.assertRaises(ValueError):
                plan(
                    repository=bad_repo,
                    repository_name="repo",
                    ticket="ticket-011",
                    slug="valid-slug",
                    primary_checkout="/workspace/repo",
                )
        for bad_primary in (None, 123):
            with self.assertRaises(TypeError):
                plan(
                    repository="org/repo",
                    repository_name="repo",
                    ticket="ticket-011",
                    slug="valid-slug",
                    primary_checkout=bad_primary,
                )
            with self.assertRaises(TypeError):
                inventory(
                    repository="org/repo",
                    repository_name="repo",
                    primary_checkout=bad_primary,
                    registered=[],
                )

    def test_inventory_cli_isolates_inherited_git_selectors(self) -> None:
        script = Path(__file__).with_name("conformance.py").resolve()
        repository = str(script.parent.parent)
        with tempfile.TemporaryDirectory() as temporary:
            env = dict(
                os.environ,
                GIT_DIR=str(Path(temporary) / "missing"),
                GIT_WORK_TREE=temporary,
                GIT_COMMON_DIR=temporary,
            )
            inv_res = subprocess.run(
                [
                    "python3",
                    str(script),
                    "inventory",
                    "--repository",
                    "wellmanifest/worktrees",
                    "--repository-name",
                    "worktrees",
                    "--from-worktree",
                    repository,
                ],
                cwd=temporary,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(inv_res.returncode, 0, inv_res.stderr)
            self.assertEqual(validate(json.loads(inv_res.stdout)), [])

    def test_malformed_records_duplicate_keys_and_symlinks_fail_closed(self) -> None:
        for non_dict in ([], "text", 42, None):
            self.assertEqual(validate(non_dict), ["invalid_record"])
            self.assertEqual(validate_filesystem(non_dict), ["invalid_record"])

        valid_inv = inventory(
            repository="org/repo",
            repository_name="repo",
            primary_checkout="/workspace/repo",
            registered=[{"path": "/workspace/repo", "branch": "main"}],
        )
        self.assertEqual(validate(dict(valid_inv, entries=[123])), ["invalid_entry"])
        bad_anom = dict(valid_inv, entries=[dict(valid_inv["entries"][0], anomalies=123)])
        self.assertEqual(validate(bad_anom), ["invalid_entry:anomalies"])
        bad_flag = dict(valid_inv, entries=[dict(valid_inv["entries"][0], bare="yes")])
        self.assertEqual(validate(bad_flag), ["invalid_entry:bare"])
        bad_head = dict(valid_inv, entries=[dict(valid_inv["entries"][0], head={})])
        self.assertTrue(validate(bad_head)[0].startswith("invalid_input:"))

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            valid_file = tmp_dir / "record.json"
            valid_file.write_text(json.dumps(valid_inv), encoding="utf-8")
            dup_file = tmp_dir / "dup.json"
            dup_file.write_text(
                '{"kind":"layout-record","kind":"layout-record"}', encoding="utf-8"
            )
            dup_buf = io.StringIO()
            with contextlib.redirect_stdout(dup_buf):
                self.assertEqual(conformance.main(["validate", str(dup_file)]), 1)
            self.assertIn("duplicate JSON key", dup_buf.getvalue())
            if os.name != "nt":
                link_file = tmp_dir / "link.json"
                link_file.symlink_to(valid_file)
                link_buf = io.StringIO()
                with contextlib.redirect_stdout(link_buf):
                    self.assertEqual(conformance.main(["validate", str(link_file)]), 1)
                self.assertIn("symlinked record is forbidden", link_buf.getvalue())
