"""Planner, validator and read-only inventory for wellmanifest.worktrees/v5."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Iterable
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Any

SCHEMA = "wellmanifest.worktrees/v5"
MINIMUM_GIT_VERSION = "2.51.0"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TICKET_RE = re.compile(r"^ticket-([0-9]{3,})$")
STEM_RE = re.compile(r"^(ticket-[0-9]{3,})--([a-z0-9]+(?:-[a-z0-9]+)*)$")
BRANCH_RE = re.compile(r"^(?:refs/heads/)?ticket/([0-9]{3,})-([a-z0-9]+(?:-[a-z0-9]+)*)$")


def _native_style() -> str:
    return "windows" if getattr(os, "name", "posix") == "nt" else "posix"


def _clean_git_env() -> dict[str, str]:
    return {k: v for k, v in getattr(os, "environ", {}).items() if not k.startswith("GIT_")}


def _path_type(style: str):
    if style == "posix":
        return PurePosixPath
    if style == "windows":
        return PureWindowsPath
    raise ValueError("pathStyle must be 'posix' or 'windows'")


def _validate_segment(label: str, value: str) -> None:
    if not isinstance(value, str) or not NAME_RE.fullmatch(value):
        raise ValueError(f"{label} must contain lowercase ASCII words separated by hyphens")


def _validate_repository(repository: str) -> None:
    if not isinstance(repository, str) or not repository.strip() or "\0" in repository:
        raise ValueError("repository must be a non-empty string")


def _validate_repository_name(repository_name: str) -> None:
    if (
        not isinstance(repository_name, str)
        or not repository_name
        or repository_name in {".", ".."}
        or any(ch in repository_name for ch in ("/", "\\", "\0"))
    ):
        raise ValueError("repositoryName must be an observed repository basename")


def strict_json_loads(text: str) -> Any:
    def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, val in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = val
        return result

    return json.loads(text, object_pairs_hook=_reject_duplicates)


def plan(
    *, repository: str, repository_name: str, ticket: str,
    slug: str, primary_checkout: str, path_style: str = "posix",
) -> dict[str, str]:
    """Return the canonical v5 layout record for one delivery unit."""
    _validate_repository(repository)
    _validate_repository_name(repository_name)
    _validate_segment("slug", slug)
    if not isinstance(ticket, str) or not (ticket_match := TICKET_RE.fullmatch(ticket)):
        raise ValueError("ticket must match ticket-NNN with at least three digits")
    if not isinstance(primary_checkout, str):
        raise TypeError("primaryCheckout must be a string")
    primary = _path_type(path_style)(primary_checkout)
    if not primary.is_absolute():
        raise ValueError("primaryCheckout must be absolute")
    stem = f"{ticket}--{slug}"
    worktrees_root, lease_root = primary / ".worktrees", primary / ".subactor" / "leases"
    return {
        "schema": SCHEMA, "kind": "layout-record", "repository": repository,
        "repositoryName": repository_name, "ticket": ticket, "slug": slug,
        "branch": f"ticket/{ticket_match.group(1)}-{slug}", "pathStyle": path_style,
        "primaryCheckout": str(primary), "worktreesRoot": str(worktrees_root),
        "worktreePath": str(worktrees_root / stem), "leaseRoot": str(lease_root),
        "leasePath": str(lease_root / f"{stem}.json"),
        "linkMode": "relative", "minimumGitVersion": MINIMUM_GIT_VERSION,
    }


def validate_layout(record: Any) -> list[str]:
    """Return stable layout errors; an empty list means exact conformance."""
    if not isinstance(record, dict):
        return ["invalid_record"]
    required = ("repository", "repositoryName", "ticket", "slug", "primaryCheckout", "pathStyle")
    if missing := [name for name in required if not isinstance(record.get(name), str)]:
        return [f"missing_or_invalid:{name}" for name in missing]
    try:
        expected = plan(
            repository=record["repository"], repository_name=record["repositoryName"],
            ticket=record["ticket"], slug=record["slug"],
            primary_checkout=record["primaryCheckout"], path_style=record["pathStyle"],
        )
    except (TypeError, ValueError) as exc:
        return [f"invalid_input:{exc}"]
    errors = [f"noncanonical:{k}" for k, v in expected.items() if record.get(k) != v]
    errors.extend(f"unexpected:{key}" for key in sorted(set(record) - set(expected)))
    return errors


def validate(record: Any) -> list[str]:
    """Validate either public v5 record kind."""
    if not isinstance(record, dict):
        return ["invalid_record"]
    if record.get("kind") == "layout-record":
        return validate_layout(record)
    if record.get("kind") == "inventory-record":
        return validate_inventory(record)
    return ["invalid_kind"]


def validate_filesystem(record: Any) -> list[str]:
    """Reject symlinks in existing repository-local canonical components."""
    if errors := validate_layout(record):
        return errors
    if record["pathStyle"] != _native_style():
        return ["filesystem_check_unsupported:pathStyle"]
    primary = Path(record["primaryCheckout"])
    checked: set[Path] = set()
    for field in ("primaryCheckout", "worktreesRoot", "worktreePath", "leaseRoot", "leasePath"):
        try:
            relative = Path(record[field]).relative_to(primary)
        except ValueError:
            return [f"filesystem_noncanonical:{field}"]
        current = primary
        candidates = [(current, ".")]
        for part in relative.parts:
            current = current / part
            candidates.append((current, str(current.relative_to(primary))))
        for candidate, relative_name in candidates:
            if candidate not in checked:
                checked.add(candidate)
                if candidate.is_symlink():
                    errors.append(f"symlink_component:{field}:{relative_name}")
    return errors


def _git_output(args: list[str], *, cwd: str | Path | None = None) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, env=_clean_git_env()
    ).stdout


def parse_worktree_porcelain(raw: bytes) -> list[dict[str, Any]]:
    """Parse `git worktree list --porcelain -z` without touching the filesystem."""
    records: list[dict[str, Any]] = []
    for raw_record in raw.split(b"\0\0"):
        if not raw_record:
            continue
        record: dict[str, Any] = {
            "path": None, "head": None, "branch": None,
            "bare": False, "detached": False, "locked": False, "prunable": False,
        }
        for raw_field in raw_record.split(b"\0"):
            if not raw_field:
                continue
            key, _, value = raw_field.decode("utf-8", "surrogateescape").partition(" ")
            if key in {"worktree", "HEAD", "branch"}:
                record[{"worktree": "path", "HEAD": "head", "branch": "branch"}[key]] = value
            elif key in {"bare", "detached", "locked", "prunable"}:
                record[key] = True
        if isinstance(record["path"], str):
            records.append(record)
    return records


def registered_worktrees(start_path: str) -> list[dict[str, Any]]:
    """Observe Git's registered worktrees; this function performs no repair."""
    records = parse_worktree_porcelain(
        _git_output(["-C", start_path, "worktree", "list", "--porcelain", "-z"], cwd=None)
    )
    if not records:
        raise ValueError("Git returned no registered worktrees")
    return records


def resolve_primary_checkout(start_path: str) -> str:
    """Resolve the primary checkout even when called from a linked worktree."""
    primary = registered_worktrees(start_path)[0]
    if primary["bare"]:
        raise ValueError("bare repositories do not have a primary checkout")
    return str(primary["path"])


def _delivery_identity(stem: str | None, branch: str | None) -> tuple[str | None, str | None]:
    if stem and (stem_match := STEM_RE.fullmatch(stem)):
        return stem_match.group(1), stem_match.group(2)
    if branch and (branch_match := BRANCH_RE.fullmatch(branch)):
        return f"ticket-{branch_match.group(1)}", branch_match.group(2)
    return None, None


def _direct_child_stem(path: PurePath, root: PurePath) -> str | None:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return None
    return relative.name if len(relative.parts) == 1 else None


def _legacy_v1_stem(value: str, repository_name: str):
    return value.startswith(f"{repository_name}--") and STEM_RE.fullmatch(
        value[len(repository_name) + 2 :]
    )


def _classify_location(candidate, primary, workspace, repository_name, path_style):
    if candidate == primary:
        return "primary", None, None
    roots = (
        ("canonical-v5", "v5", primary / ".worktrees"),
        ("legacy-v4", "v4", primary / "worktrees"),
        ("legacy-v3", "v3", workspace / ".worktrees" / ".branches" / repository_name),
        ("legacy-v2", "v2", workspace / ".worktrees" / repository_name),
    )
    for classification, version, root in roots:
        if (value := _direct_child_stem(candidate, root)) and STEM_RE.fullmatch(value):
            return classification, version, value
    if (value := _direct_child_stem(candidate, workspace / ".worktrees")) and _legacy_v1_stem(
        value, repository_name
    ):
        return "legacy-v1", "v1", value[len(repository_name) + 2 :]
    if path_style == "posix" and (
        candidate == PurePosixPath("/tmp") or PurePosixPath("/tmp") in candidate.parents
    ):
        return "system-temp", None, None
    return "unknown", None, None


def classify_path(
    *, path: str, primary_checkout: str, repository_name: str,
    branch: str | None = None, path_style: str = "posix",
) -> dict[str, Any]:
    """Classify one registered path without changing or resolving it."""
    if branch is not None and not isinstance(branch, str):
        raise TypeError("branch must be a string or None")
    path_type = _path_type(path_style)
    candidate, primary = path_type(path), path_type(primary_checkout)
    classification, layout_version, stem = _classify_location(
        candidate, primary, primary.parent, repository_name, path_style
    )
    ticket, slug = _delivery_identity(stem, branch)
    return {
        "path": str(candidate), "branch": branch.removeprefix("refs/heads/") if branch else None,
        "classification": classification, "layoutVersion": layout_version,
        "ticket": ticket, "slug": slug, "anomalies": [],
    }


def _mark_duplicate_deliveries(entries: list[dict[str, Any]]) -> None:
    non_primary = [e for e in entries if e["classification"] != "primary"]
    id_counts = Counter((e["ticket"], e["slug"]) for e in non_primary if e["ticket"] and e["slug"])
    branch_counts = Counter(e["branch"] for e in non_primary if e["branch"])
    for entry in non_primary:
        if (entry["ticket"] and id_counts[(entry["ticket"], entry["slug"])] > 1) or (
            entry["branch"] and branch_counts[entry["branch"]] > 1
        ):
            entry["anomalies"].append("duplicate-delivery")


def inventory(
    *, repository: str, repository_name: str, primary_checkout: str,
    registered: Iterable[dict[str, Any]], path_style: str = "posix",
) -> dict[str, Any]:
    """Build a deterministic, observation-only inventory record."""
    _validate_repository(repository)
    _validate_repository_name(repository_name)
    if not isinstance(primary_checkout, str):
        raise TypeError("primaryCheckout must be a string")
    primary = _path_type(path_style)(primary_checkout)
    if not primary.is_absolute():
        raise ValueError("primaryCheckout must be absolute")

    exists_fn = getattr(getattr(os, "path", None), "exists", None)
    check_host_fs = path_style == _native_style() and callable(exists_fn)
    entries = []
    for observed in registered:
        if not isinstance(observed, dict):
            raise TypeError("every registered worktree must be a mapping")
        path = observed.get("path")
        if not isinstance(path, str) or not path:
            raise TypeError("every registered worktree requires a non-empty path")
        head = observed.get("head")
        if head is not None and not isinstance(head, str):
            raise TypeError("head must be a string or None")
        entry = classify_path(
            path=path, primary_checkout=primary_checkout, repository_name=repository_name,
            branch=observed.get("branch"), path_style=path_style,
        )
        anomalies = list(entry["anomalies"])
        missing_on_disk = bool(observed.get("prunable") and check_host_fs and not exists_fn(path))
        if (observed.get("stale") or missing_on_disk) and "stale-registration" not in anomalies:
            anomalies.append("stale-registration")
        if observed.get("merged") and "merged-leftover" not in anomalies:
            anomalies.append("merged-leftover")
        entry["anomalies"] = anomalies
        entry.update({
            "head": head, "bare": bool(observed.get("bare", False)),
            "detached": bool(observed.get("detached", False)),
            "locked": bool(observed.get("locked", False)),
            "prunable": bool(observed.get("prunable", False)),
        })
        entries.append(entry)

    _mark_duplicate_deliveries(entries)
    cls_counts = Counter(entry["classification"] for entry in entries)
    anom_counts = Counter(anomaly for entry in entries for anomaly in entry["anomalies"])
    return {
        "schema": SCHEMA, "kind": "inventory-record", "repository": repository,
        "repositoryName": repository_name, "pathStyle": path_style,
        "primaryCheckout": str(primary), "readOnly": True, "entries": entries,
        "summary": {
            "total": len(entries), "classifications": dict(sorted(cls_counts.items())),
            "anomalies": dict(sorted(anom_counts.items())),
        },
    }


def validate_inventory(record: Any) -> list[str]:
    """Validate a generated inventory by deterministically rebuilding it."""
    if not isinstance(record, dict):
        return ["invalid_record"]
    required = ("repository", "repositoryName", "primaryCheckout", "pathStyle", "entries")
    if missing := [name for name in required if name not in record]:
        return [f"missing:{name}" for name in missing]
    if bad_str := [n for n in required[:-1] if not isinstance(record.get(n), str)]:
        return [f"missing_or_invalid:{name}" for name in bad_str]
    if not isinstance(record["entries"], list):
        return ["missing_or_invalid:entries"]
    observed = []
    for entry in record["entries"]:
        if not isinstance(entry, dict):
            return ["invalid_entry"]
        anomalies = entry.get("anomalies", [])
        if not isinstance(anomalies, list) or not all(isinstance(a, str) for a in anomalies):
            return ["invalid_entry:anomalies"]
        for flag in ("bare", "detached", "locked", "prunable"):
            if flag in entry and not isinstance(entry[flag], bool):
                return [f"invalid_entry:{flag}"]
        observed.append({
            "path": entry.get("path"), "head": entry.get("head"), "branch": entry.get("branch"),
            "bare": entry.get("bare", False), "detached": entry.get("detached", False),
            "locked": entry.get("locked", False), "prunable": entry.get("prunable", False),
            "stale": "stale-registration" in anomalies, "merged": "merged-leftover" in anomalies,
        })
    try:
        expected = inventory(
            repository=record["repository"], repository_name=record["repositoryName"],
            primary_checkout=record["primaryCheckout"], registered=observed,
            path_style=record["pathStyle"],
        )
    except (TypeError, ValueError) as exc:
        return [f"invalid_input:{exc}"]
    errors = [f"noncanonical:{k}" for k, v in expected.items() if record.get(k) != v]
    errors.extend(f"unexpected:{key}" for key in sorted(set(record) - set(expected)))
    return errors


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = re.search(r"([0-9]+)\.([0-9]+)\.([0-9]+)", value)
    if not match:
        raise ValueError(f"cannot parse Git version: {value}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def feature_probe(
    git: str = "git",
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
    *, from_worktree: str = ".",
) -> dict[str, Any]:
    """Probe Git in the chosen repository, without mutating caller state."""
    env = _clean_git_env()
    context = runner(
        [git, "-C", from_worktree, "rev-parse", "--git-dir"],
        check=False, capture_output=True, env=env,
    )
    context_ok = context.returncode == 0
    version_result = runner([git, "--version"], check=False, capture_output=True, env=env)
    version_text = (version_result.stdout + version_result.stderr).decode("utf-8", "replace").strip()
    try:
        version_ok = (
            version_result.returncode == 0
            and _version_tuple(version_text) >= _version_tuple(MINIMUM_GIT_VERSION)
        )
    except ValueError:
        version_ok = False
    options: dict[str, bool] = {"add": False, "repair": False}
    for command in ("add", "repair"):
        if context_ok:
            res = runner(
                [git, "-C", from_worktree, "worktree", command, "-h"],
                check=False, capture_output=True, env=env,
            )
            help_text = (res.stdout + res.stderr).decode("utf-8", "replace")
            options[command] = res.returncode in (0, 129) and "relative-paths" in help_text
    return {
        "minimumGitVersion": MINIMUM_GIT_VERSION, "repositoryContextValid": context_ok,
        "probeError": None if context_ok else "repository_context_unavailable",
        "gitVersion": version_text, "versionSupported": version_ok,
        "worktreeAddRelativePaths": options["add"],
        "worktreeRepairRelativePaths": options["repair"],
        "supported": version_ok and all(options.values()),
    }


def _read_json(path: str) -> Any:
    if path == "-":
        return strict_json_loads(sys.stdin.read())
    target = Path(path)
    if target.is_symlink():
        raise ValueError("symlinked record is forbidden")
    return strict_json_loads(target.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    planner = subparsers.add_parser("plan")
    for flag in ("--repository", "--repository-name", "--ticket", "--slug"):
        planner.add_argument(flag, required=True)
    location = planner.add_mutually_exclusive_group(required=True)
    location.add_argument("--primary-checkout")
    location.add_argument("--from-worktree")
    planner.add_argument("--path-style", choices=("posix", "windows"), default="posix")

    validator = subparsers.add_parser("validate")
    validator.add_argument("record", help="JSON file or - for stdin")
    validator.add_argument("--check-filesystem", action="store_true")

    observer = subparsers.add_parser("inventory")
    observer.add_argument("--repository", required=True)
    observer.add_argument("--repository-name", required=True)
    observer.add_argument("--from-worktree", default=".")

    probe = subparsers.add_parser("feature-probe")
    probe.add_argument("--git", default="git")
    probe.add_argument("--from-worktree", default=".")

    args = parser.parse_args(argv)
    if args.command == "plan":
        if args.from_worktree and args.path_style != _native_style():
            parser.error("--from-worktree requires the native path style")
        primary = args.primary_checkout or resolve_primary_checkout(args.from_worktree)
        print(json.dumps(plan(
            repository=args.repository, repository_name=args.repository_name,
            ticket=args.ticket, slug=args.slug, primary_checkout=primary,
            path_style=args.path_style,
        ), indent=2))
        return 0
    if args.command == "validate":
        try:
            record = _read_json(args.record)
        except (OSError, ValueError) as exc:
            print(json.dumps({"ok": False, "errors": [f"invalid_json:{exc}"]}, indent=2))
            return 1
        errors = validate_filesystem(record) if args.check_filesystem else validate(record)
        print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
        return 0 if not errors else 1
    if args.command == "inventory":
        print(json.dumps(inventory(
            repository=args.repository, repository_name=args.repository_name,
            primary_checkout=resolve_primary_checkout(args.from_worktree),
            registered=registered_worktrees(args.from_worktree), path_style=_native_style(),
        ), indent=2))
        return 0
    result = feature_probe(args.git, from_worktree=args.from_worktree)
    print(json.dumps(result, indent=2))
    return 0 if result["supported"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
