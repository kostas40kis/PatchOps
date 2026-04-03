from __future__ import annotations

import shutil
import textwrap
from pathlib import Path
import re

ROOT = Path(r"C:\\dev\\patchops")
WORKING_ROOT = Path(r"C:\\dev\\patchops\\data\\runtime\\manual_repairs\\mp41_handoff_next_action_derivation_alignment_direct_repair_20260402_125448")
BACKUP_ROOT = Path(r"C:\\dev\\patchops\\data\\runtime\\manual_repairs\\mp41_handoff_next_action_derivation_alignment_direct_repair_20260402_125448\\backups")

HANDOFF_PATH = ROOT / "patchops" / "handoff.py"
TEST_PATH = ROOT / "tests" / "test_handoff_next_action_alignment_current.py"


def backup_file(path: Path) -> None:
    if not path.exists():
        return
    destination = BACKUP_ROOT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, destination)


def replace_top_level_function(source: str, function_name: str, new_block: str) -> str:
    pattern = re.compile(
        rf"(?ms)^def {re.escape(function_name)}\(.*?(?=^def |^class |^@dataclass|\Z)"
    )
    if not pattern.search(source):
        raise RuntimeError(f"Could not locate function block for {function_name}")
    return pattern.sub(new_block.rstrip() + "\n\n", source, count=1)


def insert_after_top_level_function(source: str, function_name: str, insertion: str) -> str:
    pattern = re.compile(
        rf"(?ms)^def {re.escape(function_name)}\(.*?(?=^def |^class |^@dataclass|\Z)"
    )
    match = pattern.search(source)
    if not match:
        raise RuntimeError(f"Could not locate insertion anchor for {function_name}")
    insertion_text = "\n\n" + insertion.strip() + "\n\n"
    return source[: match.end()] + insertion_text + source[match.end() :]


source = HANDOFF_PATH.read_text(encoding="utf-8")
original_source = source

class_pattern = re.compile(
    r"(?ms)^@dataclass\(frozen=True\)\nclass ExportedReportState:\n.*?(?=^def _line\b)"
)
new_class_block = textwrap.dedent(
    """
    @dataclass(frozen=True)
    class ExportedReportState:
        wrapper_project_root: Path
        target_project_root: Path
        latest_run_mode: str
        manifest_patch_name: str
        current_status: str
        failure_class: str
        report_recommended_mode: str | None
        report_path: Path
    """
).strip()
if not class_pattern.search(source):
    raise RuntimeError("Could not locate ExportedReportState block")
source = class_pattern.sub(new_class_block + "\n\n", source, count=1)

if "def _normalize_report_recommended_mode(" not in source:
    helper_block = textwrap.dedent(
        """
        def _normalize_report_recommended_mode(value: str | None) -> str | None:
            if value is None:
                return None

            normalized = "_".join(str(value).strip().lower().replace("-", "_").split())
            if not normalized:
                return None

            mapping = {
                VERIFY_ONLY_MODE: VERIFY_ONLY_MODE,
                "wrapper_only_repair": WRAPPER_ONLY_RETRY_MODE,
                WRAPPER_ONLY_RETRY_MODE: WRAPPER_ONLY_RETRY_MODE,
                "content_repair": REPAIR_PATCH_MODE,
                REPAIR_PATCH_MODE: REPAIR_PATCH_MODE,
                NEW_PATCH_MODE: NEW_PATCH_MODE,
                MANUAL_REVIEW_MODE: MANUAL_REVIEW_MODE,
            }
            return mapping.get(normalized)


        def _report_recommended_mode_from_text(text: str) -> str | None:
            patterns = (
                r"(?im)^\\s*Recommended next mode\\s*:\\s*(.+?)\\s*$",
                r"(?im)^\\s*Next Recommended Mode\\s*:\\s*(.+?)\\s*$",
            )
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return _normalize_report_recommended_mode(match.group(1).strip())
            return None


        def _recommendation_from_report_hint(state: ExportedReportState) -> dict[str, Any] | None:
            hint = state.report_recommended_mode
            if hint is None:
                return None

            if hint == VERIFY_ONLY_MODE:
                return {
                    "recommended_mode": VERIFY_ONLY_MODE,
                    "next_action": "Use verify-only rerun to re-check and re-evidence the already-present target files.",
                    "rationale": "The exported report already recommends verify-only, so handoff should preserve that narrower evidence-first path.",
                    "escalation_required": False,
                    "next_recommended_patch": None,
                    "known_blockers": [],
                }

            if hint == WRAPPER_ONLY_RETRY_MODE:
                return {
                    "recommended_mode": WRAPPER_ONLY_RETRY_MODE,
                    "next_action": "Use wrapper-only repair or wrapper-only retry to recover the handoff and evidence surface without widening back into a full apply.",
                    "rationale": "The exported report already recommends a wrapper-only repair path, so handoff should preserve that narrower wrapper-side guidance.",
                    "escalation_required": False,
                    "next_recommended_patch": None,
                    "known_blockers": [],
                }

            if hint == REPAIR_PATCH_MODE:
                return {
                    "recommended_mode": REPAIR_PATCH_MODE,
                    "next_action": "Keep the repair narrow. The exported report already recommends content repair for the failed surface.",
                    "rationale": "The exported report already recommends content repair, so handoff should preserve that narrower target-side guidance.",
                    "escalation_required": False,
                    "next_recommended_patch": None,
                    "known_blockers": [],
                }

            if hint == NEW_PATCH_MODE:
                return {
                    "recommended_mode": NEW_PATCH_MODE,
                    "next_action": f"Continue with {_next_patch_label_from_name(state.manifest_patch_name)}.",
                    "rationale": "The exported report already recommends continuing to the next planned patch.",
                    "escalation_required": False,
                    "next_recommended_patch": _next_patch_label_from_name(state.manifest_patch_name),
                    "known_blockers": [],
                }

            return None
        """
    ).strip()
    source = insert_after_top_level_function(source, "_mode_from_report_text", helper_block)

new_build_state = textwrap.dedent(
    """
    def _build_exported_report_state(
        report_path: str | Path | None,
        *,
        wrapper_project_root: str | Path | None = None,
    ) -> ExportedReportState:
        resolved_wrapper_root = (
            Path(wrapper_project_root).resolve()
            if wrapper_project_root is not None
            else Path(__file__).resolve().parents[1]
        )
        handoff_root = resolved_wrapper_root / HANDOFF_DIRNAME

        if report_path is None:
            fallback_report = handoff_root / LATEST_REPORT_COPY_FILENAME
            if not fallback_report.exists():
                raise FileNotFoundError(
                    "No report path was supplied and handoff/latest_report_copy.txt does not exist yet."
                )
            resolved_report_path = fallback_report.resolve()
        else:
            resolved_report_path = Path(report_path).resolve()

        if not resolved_report_path.exists():
            raise FileNotFoundError(f"Latest report path does not exist: {resolved_report_path}")

        text = resolved_report_path.read_text(encoding="utf-8")
        manifest_patch_name = _report_field(text, "Patch Name") or "unknown_patch"
        target_project_root_value = _report_field(text, "Target Project Root")
        target_project_root = (
            Path(target_project_root_value).resolve()
            if target_project_root_value and target_project_root_value != "(none)"
            else resolved_wrapper_root
        )
        result_label = (_report_field(text, "Result") or "FAIL").upper()
        current_status = "pass" if result_label == PASS_LABEL else "fail"
        failure_class = _report_field(text, "Category") or "none"

        return ExportedReportState(
            wrapper_project_root=resolved_wrapper_root,
            target_project_root=target_project_root,
            latest_run_mode=_mode_from_report_text(text),
            manifest_patch_name=manifest_patch_name,
            current_status=current_status,
            failure_class=failure_class,
            report_recommended_mode=_report_recommended_mode_from_text(text),
            report_path=resolved_report_path,
        )
    """
).strip()
source = replace_top_level_function(source, "_build_exported_report_state", new_build_state)

new_recommendation_from_state = textwrap.dedent(
    """
    def build_next_action_recommendation_from_report_state(state: ExportedReportState) -> dict[str, Any]:
        if state.current_status == "pass":
            return {
                "recommended_mode": NEW_PATCH_MODE,
                "next_action": f"Continue with {_next_patch_label_from_name(state.manifest_patch_name)}.",
                "rationale": "The latest exported report passed, so the trustworthy next step is the next planned patch.",
                "escalation_required": False,
                "next_recommended_patch": _next_patch_label_from_name(state.manifest_patch_name),
                "known_blockers": [],
            }

        hint_recommendation = _recommendation_from_report_hint(state)
        if hint_recommendation is not None:
            return hint_recommendation

        if state.failure_class == TARGET_FAILURE:
            return {
                "recommended_mode": REPAIR_PATCH_MODE,
                "next_action": "Keep the repair narrow. Write a repair patch for the failed target surface.",
                "rationale": "The exported report shows a target-project failure, so the next step is a narrow target repair.",
                "escalation_required": False,
                "next_recommended_patch": None,
                "known_blockers": [],
            }

        if state.failure_class == WRAPPER_FAILURE:
            return {
                "recommended_mode": WRAPPER_ONLY_RETRY_MODE,
                "next_action": "Use wrapper-only retry or a narrow wrapper repair to recover the handoff and evidence surface.",
                "rationale": "The exported report shows a wrapper failure, so the next step should stay on the wrapper/evidence side.",
                "escalation_required": False,
                "next_recommended_patch": None,
                "known_blockers": [],
            }

        return {
            "recommended_mode": MANUAL_REVIEW_MODE,
            "next_action": "Stop and inspect the latest report before widening scope.",
            "rationale": "The exported report does not provide enough stable signal to choose a narrower path automatically.",
            "escalation_required": True,
            "next_recommended_patch": None,
            "known_blockers": [],
        }
    """
).strip()
source = replace_top_level_function(source, "build_next_action_recommendation_from_report_state", new_recommendation_from_state)

if source == original_source:
    raise RuntimeError("MP41 patcher made no changes to patchops/handoff.py")

backup_file(HANDOFF_PATH)
HANDOFF_PATH.write_text(source, encoding="utf-8")

new_test_text = textwrap.dedent(
    """
    import json
    from pathlib import Path

    from patchops.handoff import export_handoff_bundle


    def _read_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


    def _write_report(
        root: Path,
        *,
        patch_name: str = "mp41_handoff_alignment_demo",
        result_label: str = "FAIL",
        failure_category: str | None = "wrapper_failure",
        recommended_next_mode: str | None = None,
        first_line: str = "PATCHOPS APPLY",
    ) -> Path:
        report_path = root / "latest_report.txt"
        failure_block = "(none)"
        if failure_category is not None:
            failure_block = f"Category : {failure_category}\\nMessage  : simulated failure\\n"

        recommendation_block = ""
        if recommended_next_mode is not None:
            recommendation_block = (
                "RECOMMENDATION\\n"
                "--------------\\n"
                f"Recommended next mode : {recommended_next_mode}\\n\\n"
            )

        report_text = (
            f"{first_line}\\n"
            f"Patch Name           : {patch_name}\\n"
            "Manifest Path        : C:\\\\dev\\\\patchops\\\\data\\\\runtime\\\\self_hosted\\\\example.json\\n"
            "Workspace Root       : C:\\\\dev\\n"
            f"Wrapper Project Root : {root}\\n"
            f"Target Project Root  : {root}\\n"
            "Active Profile       : generic_python\\n"
            "Runtime Path         : (none)\\n"
            f"Backup Root          : {root}\\\\data\\\\runtime\\\\patch_backups\\\\example\\n"
            f"Report Path          : {report_path}\\n"
            "Manifest Version     : 1\\n"
            "\\n"
            "TARGET FILES\\n"
            "------------\\n"
            f"{root}\\\\patchops\\\\handoff.py\\n"
            "\\n"
            "BACKUP\\n"
            "------\\n"
            "(none)\\n"
            "\\n"
            "WRITING FILES\\n"
            "-------------\\n"
            f"WROTE : {root}\\\\patchops\\\\handoff.py\\n"
            "\\n"
            "VALIDATION COMMANDS\\n"
            "-------------------\\n"
            "NAME    : pytest\\n"
            "COMMAND : python -m pytest -q\\n"
            f"CWD     : {root}\\n"
            f"EXIT    : {0 if result_label == 'PASS' else 1}\\n"
            "\\n"
            "FULL OUTPUT\\n"
            "-----------\\n"
            "[pytest][stdout]\\n"
            "...\\n"
            "\\n"
            "[pytest][stderr]\\n"
            "\\n"
            "\\n"
            "FAILURE DETAILS\\n"
            "---------------\\n"
            f"{failure_block}"
            f"{recommendation_block}"
            "SUMMARY\\n"
            "-------\\n"
            f"ExitCode : {0 if result_label == 'PASS' else 1}\\n"
            f"Result   : {result_label}\\n"
        )
        report_path.write_text(report_text, encoding="utf-8")
        return report_path


    def test_report_note_verify_only_maps_handoff_to_verify_only(tmp_path: Path) -> None:
        report_path = _write_report(
            tmp_path,
            result_label="FAIL",
            failure_category="wrapper_failure",
            recommended_next_mode="verify_only",
            first_line="PATCHOPS VERIFY",
        )
        payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)
        current_handoff = _read_json(tmp_path / "handoff" / "current_handoff.json")

        assert payload["next_recommended_mode"] == "verify_only"
        assert current_handoff["resume"]["next_recommended_mode"] == "verify_only"
        assert "verify-only" in payload["next_action"].lower()


    def test_report_note_wrapper_only_repair_maps_handoff_to_wrapper_only_retry_guidance(tmp_path: Path) -> None:
        report_path = _write_report(
            tmp_path,
            result_label="FAIL",
            failure_category="wrapper_failure",
            recommended_next_mode="wrapper_only_repair",
        )
        payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)
        current_handoff = _read_json(tmp_path / "handoff" / "current_handoff.json")

        assert payload["next_recommended_mode"] == "wrapper_only_retry"
        assert current_handoff["resume"]["next_recommended_mode"] == "wrapper_only_retry"
        assert "wrapper-only" in payload["next_action"].lower()


    def test_report_note_content_repair_maps_handoff_to_repair_patch_guidance(tmp_path: Path) -> None:
        report_path = _write_report(
            tmp_path,
            result_label="FAIL",
            failure_category="wrapper_failure",
            recommended_next_mode="content_repair",
        )
        payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)
        current_handoff = _read_json(tmp_path / "handoff" / "current_handoff.json")

        assert payload["next_recommended_mode"] == "repair_patch"
        assert current_handoff["resume"]["next_recommended_mode"] == "repair_patch"
        assert "content repair" in payload["next_action"].lower() or "repair" in payload["next_action"].lower()


    def test_missing_report_note_falls_back_to_failure_class_logic(tmp_path: Path) -> None:
        report_path = _write_report(
            tmp_path,
            result_label="FAIL",
            failure_category="wrapper_failure",
            recommended_next_mode=None,
        )
        payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        assert payload["next_recommended_mode"] == "wrapper_only_retry"
        assert "wrapper-only" in payload["next_action"].lower()


    def test_pass_status_still_recommends_new_patch_even_if_report_note_exists(tmp_path: Path) -> None:
        report_path = _write_report(
            tmp_path,
            patch_name="mp41_demo_pass",
            result_label="PASS",
            failure_category=None,
            recommended_next_mode="content_repair",
        )
        payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

        assert payload["current_status"] == "pass"
        assert payload["next_recommended_mode"] == "new_patch"
        assert "continue with" in payload["next_action"].lower()
    """
).strip() + "\n"

backup_file(TEST_PATH)
TEST_PATH.parent.mkdir(parents=True, exist_ok=True)
TEST_PATH.write_text(new_test_text, encoding="utf-8")

summary = {
    "patched_files": [
        str(HANDOFF_PATH.relative_to(ROOT)),
        str(TEST_PATH.relative_to(ROOT)),
    ],
    "backup_root": str(BACKUP_ROOT),
}
(WORKING_ROOT / "prepare_summary.json").write_text(__import__("json").dumps(summary, indent=2), encoding="utf-8")
print((WORKING_ROOT / "prepare_summary.json").read_text(encoding="utf-8"))