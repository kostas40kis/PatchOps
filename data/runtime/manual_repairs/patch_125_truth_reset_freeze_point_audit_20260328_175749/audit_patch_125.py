from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Patch 125 truth-reset audit helper")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--pytest-exit-code", required=True, type=int)
    return parser.parse_args()


PATCH_RE = re.compile(r"patch_(\d+)([a-z]?)_", re.IGNORECASE)
DOC_PATCH_RE = re.compile(r"Patch\s+(\d+)([A-Za-z]?)", re.IGNORECASE)


def patch_key(value: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)([A-Za-z]?)", value.strip())
    if not m:
        return (-1, -1)
    number = int(m.group(1))
    suffix = m.group(2).lower()
    suffix_rank = 0 if suffix == "" else (ord(suffix) - 96)
    return (number, suffix_rank)


def normalize_patch(value: str | None) -> str | None:
    if not value:
        return None
    m = re.search(r"(\d+)([A-Za-z]?)", value)
    if not m:
        return None
    number = int(m.group(1))
    suffix = m.group(2)
    return f"Patch {number}{suffix}"


def extract_doc_patch_tokens(text: str) -> list[str]:
    return [f"{int(m.group(1))}{m.group(2)}" for m in DOC_PATCH_RE.finditer(text)]


def max_patch_token(tokens: list[str]) -> str | None:
    if not tokens:
        return None
    best = max(tokens, key=patch_key)
    n, s = re.fullmatch(r"(\d+)([A-Za-z]?)", best).groups()
    return f"Patch {int(n)}{s}"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def find_first_key(obj: Any, target: str) -> Any:
    if isinstance(obj, dict):
        if target in obj:
            return obj[target]
        for value in obj.values():
            found = find_first_key(value, target)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_first_key(item, target)
            if found is not None:
                return found
    return None


def find_runtime_patches(root: Path) -> list[str]:
    found: list[str] = []
    for rel in (Path("data/runtime/manual_repairs"), Path("data/runtime/patch_backups")):
        base = root / rel
        if not base.exists():
            continue
        for child in base.iterdir():
            m = PATCH_RE.match(child.name)
            if m:
                found.append(f"{int(m.group(1))}{m.group(2)}")
    return found


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()

    project_status_path = root / "docs" / "project_status.md"
    patch_ledger_path = root / "docs" / "patch_ledger.md"
    handoff_json_path = root / "handoff" / "current_handoff.json"
    handoff_index_path = root / "handoff" / "latest_report_index.json"
    handoff_prompt_path = root / "handoff" / "next_prompt.txt"

    project_status_text = read_text(project_status_path)
    patch_ledger_text = read_text(patch_ledger_path)

    handoff_json = read_json(handoff_json_path)
    handoff_index = read_json(handoff_index_path)

    runtime_patch_tokens = find_runtime_patches(root)
    highest_runtime_patch = max_patch_token(runtime_patch_tokens)

    highest_project_status_patch = max_patch_token(extract_doc_patch_tokens(project_status_text))
    highest_patch_ledger_patch = max_patch_token(extract_doc_patch_tokens(patch_ledger_text))

    handoff_latest_attempted = normalize_patch(
        find_first_key(handoff_json, "latest_attempted_patch")
        or find_first_key(handoff_index, "latest_attempted_patch")
    )
    handoff_latest_passed = normalize_patch(
        find_first_key(handoff_json, "latest_passed_patch")
        or find_first_key(handoff_index, "latest_passed_patch")
    )
    handoff_current_status = find_first_key(handoff_json, "current_status") or find_first_key(handoff_index, "current_status")
    handoff_failure_class = find_first_key(handoff_json, "failure_class") or find_first_key(handoff_index, "failure_class")
    handoff_next_action = find_first_key(handoff_json, "next_action") or find_first_key(handoff_index, "next_action")

    candidate_report_path = (
        find_first_key(handoff_index, "latest_report_source_path")
        or find_first_key(handoff_index, "report_path")
        or find_first_key(handoff_index, "latest_report_copy_path")
        or find_first_key(handoff_json, "report_path")
        or None
    )

    notes: list[str] = []

    if args.pytest_exit_code == 0:
        if str(handoff_current_status).lower() == "fail":
            provisional = "inconsistent_docs_only"
            notes.append("pytest is green but handoff still says fail; handoff/docs may be stale.")
        else:
            provisional = "green_maintenance_head"
            notes.append("pytest is green and no live failure status was detected in handoff.")
    else:
        provisional = "narrow_repair_needed"
        notes.append("pytest failed, so the repo is not ready for final freeze yet.")

    if highest_runtime_patch:
        notes.append(f"highest patch observed from runtime folders: {highest_runtime_patch}")
    if highest_patch_ledger_patch:
        notes.append(f"highest patch token seen in docs/patch_ledger.md: {highest_patch_ledger_patch}")
    if highest_project_status_patch:
        notes.append(f"highest patch token seen in docs/project_status.md: {highest_project_status_patch}")

    if highest_runtime_patch and handoff_latest_attempted:
        runtime_key = patch_key(highest_runtime_patch.replace("Patch ", ""))
        handoff_key = patch_key(handoff_latest_attempted.replace("Patch ", ""))
        if runtime_key > handoff_key:
            notes.append("runtime patch inventory is ahead of current handoff latest-attempted patch; status surfaces may need refresh.")

    payload = {
        "project_root": str(root),
        "pytest_exit_code": args.pytest_exit_code,
        "provisional_classification": provisional,
        "highest_runtime_patch_observed": highest_runtime_patch,
        "highest_patch_in_project_status": highest_project_status_patch,
        "highest_patch_in_patch_ledger": highest_patch_ledger_patch,
        "handoff_current_status": handoff_current_status,
        "handoff_failure_class": handoff_failure_class,
        "handoff_latest_attempted_patch": handoff_latest_attempted,
        "handoff_latest_passed_patch": handoff_latest_passed,
        "handoff_next_action": handoff_next_action,
        "handoff_json_exists": handoff_json_path.exists(),
        "handoff_index_exists": handoff_index_path.exists(),
        "handoff_prompt_exists": handoff_prompt_path.exists(),
        "candidate_report_path": candidate_report_path,
        "notes": notes,
    }

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
