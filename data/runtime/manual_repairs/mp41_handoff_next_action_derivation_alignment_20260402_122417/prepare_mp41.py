from __future__ import annotations

import json
import re
import sys
import textwrap
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def print_kv(key: str, value: object) -> None:
    print(f"{key}={value}")


def replace_function_block(text: str, func_name: str, new_block: str) -> str:
    pattern = re.compile(
        rf"^def {re.escape(func_name)}\([^\n]*\):\n(?:    .*\n|\n)*?(?=^def |\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        raise SystemExit(f"Could not find function block for {func_name}.")
    return text[:match.start()] + new_block + ("\n" if not new_block.endswith("\n") else "") + text[match.end():]


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / 'content'
    inner_report_root = working_root / 'inner_reports'
    content_root.mkdir(parents=True, exist_ok=True)
    inner_report_root.mkdir(parents=True, exist_ok=True)

    handoff_path = repo_root / 'patchops' / 'handoff.py'
    if not handoff_path.exists():
        raise SystemExit('patchops/handoff.py not found.')

    handoff_text = handoff_path.read_text(encoding='utf-8')
    current_test_path = repo_root / 'tests' / 'test_handoff_next_action_alignment_current.py'

    helper_import_present = 'from patchops.rerun_decisions import VERIFY_ONLY, WRAPPER_ONLY_REPAIR' in handoff_text
    helper_present = '_recommended_next_mode_from_report_path(' in handoff_text
    current_test_exists = current_test_path.exists()
    required_fragments = [
        'Recommended Next Mode :',
        '_recommended_next_mode_from_report_path(',
        'VERIFY_ONLY',
        'WRAPPER_ONLY_REPAIR',
        'content_repair',
    ]
    required_fragments_present = all(fragment in handoff_text for fragment in required_fragments)

    if helper_import_present and helper_present and current_test_exists and required_fragments_present:
        decision = 'stop_mp41_already_present'
        decision_reason = 'handoff next-action already aligns with report recommendation notes.'
        manifest_path = ''
    else:
        decision = 'author_mp41'
        decision_reason = 'Align handoff next-action derivation with the new report recommendation note and helper-owned rerun guidance.'
        manifest_path = str((working_root / 'patch_manifest.json').resolve())

        updated = handoff_text
        import_line = 'from patchops.rerun_decisions import VERIFY_ONLY, WRAPPER_ONLY_REPAIR\n'
        if import_line not in updated:
            import_block_match = re.search(r'^(from .*\n|import .*\n)+', updated, re.MULTILINE)
            if import_block_match is None:
                raise SystemExit('Could not find import block in patchops/handoff.py.')
            updated = updated[:import_block_match.end()] + import_line + updated[import_block_match.end():]

        constants_anchor = 'MANUAL_REVIEW_MODE = "manual_review"\n'
        if 'CONTENT_REPAIR_MODE = "content_repair"' not in updated:
            if constants_anchor not in updated:
                raise SystemExit('Could not find handoff mode constants anchor.')
            updated = updated.replace(constants_anchor, constants_anchor + 'CONTENT_REPAIR_MODE = "content_repair"\n', 1)

        helper_block = textwrap.dedent('''
        _RECOMMENDED_NEXT_MODE_RE = re.compile(r"^Recommended Next Mode\\s*:\\s*(?P<mode>[a-zA-Z0-9_]+)\\s*$", re.MULTILINE)


        def _recommended_next_mode_from_report_text(report_text: str) -> str | None:
            match = _RECOMMENDED_NEXT_MODE_RE.search(report_text)
            if match is None:
                return None
            mode = match.group("mode").strip()
            return mode or None


        def _recommended_next_mode_from_report_path(report_path: Path) -> str | None:
            try:
                report_text = report_path.read_text(encoding="utf-8")
            except OSError:
                return None
            return _recommended_next_mode_from_report_text(report_text)


        def _recommendation_from_report_mode(mode: str) -> dict[str, Any] | None:
            if mode == VERIFY_ONLY:
                return {
                    "recommended_mode": VERIFY_ONLY,
                    "next_action": "Use verify-only rerun to re-check and re-evidence the already-present target files.",
                    "rationale": "The canonical report already recommends verify-only, so the narrowest trustworthy next step is to preserve content and rerun verification.",
                    "escalation_required": False,
                    "next_recommended_patch": None,
                    "known_blockers": [],
                }
            if mode == WRAPPER_ONLY_REPAIR:
                return {
                    "recommended_mode": WRAPPER_ONLY_REPAIR,
                    "next_action": "Use wrapper-only repair to recover evidence or launcher/report mechanics without widening back into a full apply.",
                    "rationale": "The canonical report already recommends a wrapper-only path, so the next step should stay on the wrapper/evidence side.",
                    "escalation_required": False,
                    "next_recommended_patch": None,
                    "known_blockers": [],
                }
            if mode == CONTENT_REPAIR_MODE:
                return {
                    "recommended_mode": CONTENT_REPAIR_MODE,
                    "next_action": "Keep the repair narrow. Repair the failed target content before choosing a rerun mode.",
                    "rationale": "The canonical report already recommends content repair, so the next step should stay focused on the failed target surface.",
                    "escalation_required": False,
                    "next_recommended_patch": None,
                    "known_blockers": [],
                }
            return None
        ''').strip() + '\n\n'

        if '_recommended_next_mode_from_report_path(' not in updated:
            anchor = 'def build_next_action_recommendation_from_report_state(state: ExportedReportState) -> dict[str, Any]:\n'
            if anchor not in updated:
                raise SystemExit('Could not find build_next_action_recommendation_from_report_state anchor.')
            updated = updated.replace(anchor, helper_block + anchor, 1)

        new_function = textwrap.dedent('''
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

            report_mode = _recommended_next_mode_from_report_path(state.report_path)
            if report_mode is not None:
                recommendation = _recommendation_from_report_mode(report_mode)
                if recommendation is not None:
                    return recommendation

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
        ''').strip() + '\n'
        updated = replace_function_block(updated, 'build_next_action_recommendation_from_report_state', new_function)

        out_handoff = content_root / 'patchops' / 'handoff.py'
        ensure_parent(out_handoff)
        out_handoff.write_text(updated, encoding='utf-8')

        current_test = textwrap.dedent('''
        from pathlib import Path

        from patchops.handoff import ExportedReportState, build_next_action_recommendation_from_report_state
        from patchops.rerun_decisions import VERIFY_ONLY, WRAPPER_ONLY_REPAIR


        def _state(tmp_path: Path, report_text: str, *, failure_class: str = 'target_project_failure', status: str = 'fail') -> ExportedReportState:
            report_path = tmp_path / 'latest_report.txt'
            report_path.write_text(report_text, encoding='utf-8')
            return ExportedReportState(
                wrapper_project_root=tmp_path / 'wrapper',
                target_project_root=tmp_path / 'target',
                latest_run_mode='apply',
                manifest_patch_name='mp40_report_recommendation_note',
                current_status=status,
                failure_class=failure_class,
                report_path=report_path,
            )


        def test_handoff_prefers_verify_only_recommendation_from_report(tmp_path: Path):
            state = _state(tmp_path, 'Recommended Next Mode : verify_only\n', failure_class='target_project_failure')
            recommendation = build_next_action_recommendation_from_report_state(state)
            assert recommendation['recommended_mode'] == VERIFY_ONLY
            assert 'verify-only' in recommendation['next_action'].lower()


        def test_handoff_prefers_wrapper_only_repair_recommendation_from_report(tmp_path: Path):
            state = _state(tmp_path, 'Recommended Next Mode : wrapper_only_repair\n', failure_class='wrapper_failure')
            recommendation = build_next_action_recommendation_from_report_state(state)
            assert recommendation['recommended_mode'] == WRAPPER_ONLY_REPAIR
            assert 'wrapper-only' in recommendation['next_action'].lower()


        def test_handoff_prefers_content_repair_recommendation_from_report(tmp_path: Path):
            state = _state(tmp_path, 'Recommended Next Mode : content_repair\n', failure_class='target_project_failure')
            recommendation = build_next_action_recommendation_from_report_state(state)
            assert recommendation['recommended_mode'] == 'content_repair'
            assert 'repair' in recommendation['next_action'].lower()


        def test_handoff_falls_back_to_existing_target_failure_logic_when_note_missing(tmp_path: Path):
            state = _state(tmp_path, 'no recommendation here\n', failure_class='target_project_failure')
            recommendation = build_next_action_recommendation_from_report_state(state)
            assert recommendation['recommended_mode'] == 'repair_patch'


        def test_pass_status_still_continues_to_next_patch(tmp_path: Path):
            state = _state(tmp_path, 'Recommended Next Mode : verify_only\n', failure_class='none', status='pass')
            recommendation = build_next_action_recommendation_from_report_state(state)
            assert recommendation['recommended_mode'] == 'new_patch'
        ''').strip() + '\n'

        out_test = content_root / 'tests' / 'test_handoff_next_action_alignment_current.py'
        ensure_parent(out_test)
        out_test.write_text(current_test, encoding='utf-8')

        manifest = {
            'manifest_version': '1',
            'patch_name': 'mp41_handoff_next_action_derivation_alignment',
            'active_profile': 'generic_python',
            'target_project_root': str(repo_root),
            'files_to_write': [
                {
                    'path': 'patchops/handoff.py',
                    'content_path': str(out_handoff.resolve()),
                    'encoding': 'utf-8',
                },
                {
                    'path': 'tests/test_handoff_next_action_alignment_current.py',
                    'content_path': str(out_test.resolve()),
                    'encoding': 'utf-8',
                },
            ],
            'validation_commands': [
                {
                    'name': 'mp41 handoff next-action alignment tests',
                    'program': 'py',
                    'args': [
                        '-3', '-m', 'pytest', '-q',
                        'tests/test_handoff_next_action_alignment_current.py',
                        'tests/test_report_recommendation_note_current.py',
                        'tests/test_rerun_decision_matrix_current.py',
                        'tests/test_wrapper_retry_decision_helper_current.py',
                        'tests/test_verify_only_decision_helper_current.py',
                        'tests/test_handoff.py',
                    ],
                    'working_directory': '.',
                    'use_profile_runtime': False,
                    'allowed_exit_codes': [0],
                }
            ],
            'report_preferences': {
                'report_dir': str(inner_report_root.resolve()),
                'report_name_prefix': 'mp41',
                'write_to_desktop': False,
            },
            'tags': ['maintenance', 'pythonization', 'phase_f', 'mp41', 'self_hosted'],
            'notes': 'MP41 handoff next-action derivation alignment after confirmed MP40 completion.',
        }
        (working_root / 'patch_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    print_kv('decision', decision)
    print_kv('decision_reason', decision_reason)
    print_kv('helper_import_present', helper_import_present)
    print_kv('helper_present', helper_present)
    print_kv('current_test_exists', current_test_exists)
    print_kv('required_fragments_present', required_fragments_present)
    print_kv('manifest_path', manifest_path)
    print_kv('inner_report_root', str(inner_report_root.resolve()))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())