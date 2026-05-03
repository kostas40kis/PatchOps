from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.md")
TEST_PATH = Path("tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py")

WRONG = "l5_broad_readback.build_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback(root)"
RIGHT = "l5_broad_readback.build_l5_broad_validation_cli_readback(root)"
SENTINEL = "# PATCHOPS L5.18 START"
COMMAND = "browser-start-supervised-launch-edge-l5-readiness"

COMMAND_BLOCK = r'''
# PATCHOPS L5.18 START
# Passive Microsoft Edge supervised-launch L5 aggregate readiness gate command.
# This block only registers/routes readback and performs no Selenium import,
# browser startup, profile creation, click/download, paste/send, package-run,
# commit, or push side effect.
import sys as _patchops_l5_18_sys

_PATCHOPS_L5_18_COMMAND = "browser-start-supervised-launch-edge-l5-readiness"

try:
    _PATCHOPS_L5_18_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L5_18_PREV_BUILD_PARSER = None

if _PATCHOPS_L5_18_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L5_18_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L5_18_COMMAND not in choices:
                        readback_parser = action.add_parser(
                            _PATCHOPS_L5_18_COMMAND,
                            help="Read back the passive Microsoft Edge supervised-launch L5 aggregate readiness gate.",
                        )
                        readback_parser.add_argument("--repo-root", default=None)
                        readback_parser.add_argument("--json", action="store_true")
                        readback_parser.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_l5_readiness(args) -> int:
    from . import live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.main(module_args)


try:
    _PATCHOPS_L5_18_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L5_18_PREV_COMMAND_NAMES = None

if _PATCHOPS_L5_18_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L5_18_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L5_18_COMMAND,) if name not in names)


_PATCHOPS_L5_18_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    raw = list(_patchops_l5_18_sys.argv[1:] if argv is None else argv)
    if raw and raw[0] == _PATCHOPS_L5_18_COMMAND:
        from . import live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate
        return live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.main(raw[1:])
    return _PATCHOPS_L5_18_PREV_MAIN(argv)
# PATCHOPS L5.18 END
'''


def repair_module() -> None:
    if not MODULE_PATH.exists():
        raise SystemExit(f"missing module: {MODULE_PATH}")
    text = MODULE_PATH.read_text(encoding="utf-8")
    if WRONG in text:
        text = text.replace(WRONG, RIGHT)
    elif RIGHT not in text:
        raise SystemExit("L5.18 aggregate module does not contain the expected wrong or repaired L5.11 builder call")
    text = text.replace("PATCH = \"L5.18\"", "PATCH = \"L5.18\"")
    MODULE_PATH.write_text(text, encoding="utf-8")


def ensure_command_wrapper() -> None:
    if not COMMANDS_PATH.exists():
        raise SystemExit(f"missing commands file: {COMMANDS_PATH}")
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if SENTINEL in text and COMMAND in text:
        return
    if not text.endswith("\n"):
        text += "\n"
    COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")


def annotate_doc() -> None:
    if not DOC_PATH.exists():
        return
    text = DOC_PATH.read_text(encoding="utf-8")
    marker = "## L5.18a repair note"
    if marker not in text:
        text = text.rstrip() + "\n\n" + marker + "\n\nL5.18a repairs the aggregate gate module readback by using the accepted L5.11 builder name `build_l5_broad_validation_cli_readback`. The behavior remains passive: no Selenium import, no browser start, no Edge process start, no profile directory creation, and no click/download/paste/send/package-run side effect.\n"
        DOC_PATH.write_text(text + "\n", encoding="utf-8")


def add_regression_assertion() -> None:
    if not TEST_PATH.exists():
        return
    text = TEST_PATH.read_text(encoding="utf-8")
    marker = "def test_l5_18a_uses_accepted_l5_11_builder_name() -> None:"
    if marker in text:
        return
    extra = '''


def test_l5_18a_uses_accepted_l5_11_builder_name() -> None:
    module_path = PROJECT_ROOT / "patchops" / "llm_browser" / "live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py"
    text = module_path.read_text(encoding="utf-8")
    assert "build_l5_broad_validation_cli_readback(root)" in text
    assert "build_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback(root)" not in text
'''
    TEST_PATH.write_text(text.rstrip() + extra + "\n", encoding="utf-8")


def main() -> int:
    repair_module()
    ensure_command_wrapper()
    annotate_doc()
    add_regression_assertion()
    print("L5.18a repaired aggregate readiness L5.11 builder call and verified command wrapper")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())