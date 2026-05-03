from __future__ import annotations

from pathlib import Path

COMMANDS_PATH = Path("patchops/llm_browser/commands.py")
SENTINEL_START = "# PATCHOPS L5.12 START"
COMMAND = "browser-start-supervised-launch-edge-readiness"

PATCH_BLOCK = r'''
# PATCHOPS L5.12 START
# Passive Microsoft Edge supervised-launch readiness contract command.
# This block only registers/routes readback and performs no Selenium import,
# browser startup, profile creation, click/download, paste/send, package-run,
# commit, or push side effect.
import sys as _patchops_l5_12_sys

_PATCHOPS_L5_12_COMMAND = "browser-start-supervised-launch-edge-readiness"

try:
    _PATCHOPS_L5_12_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L5_12_PREV_BUILD_PARSER = None

if _PATCHOPS_L5_12_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L5_12_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L5_12_COMMAND not in choices:
                        readback_parser = action.add_parser(
                            _PATCHOPS_L5_12_COMMAND,
                            help="Read back the passive Microsoft Edge supervised-launch readiness contract.",
                        )
                        readback_parser.add_argument("--repo-root", default=None)
                        readback_parser.add_argument("--json", action="store_true")
                        readback_parser.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_readiness(args) -> int:
    from . import live_adapter_edge_supervised_launch_readiness_contract
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_supervised_launch_readiness_contract.main(module_args)


try:
    _PATCHOPS_L5_12_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L5_12_PREV_COMMAND_NAMES = None

if _PATCHOPS_L5_12_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L5_12_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L5_12_COMMAND,) if name not in names)


_PATCHOPS_L5_12_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    raw = list(_patchops_l5_12_sys.argv[1:] if argv is None else argv)
    if raw and raw[0] == _PATCHOPS_L5_12_COMMAND:
        from . import live_adapter_edge_supervised_launch_readiness_contract
        return live_adapter_edge_supervised_launch_readiness_contract.main(raw[1:])
    return _PATCHOPS_L5_12_PREV_MAIN(argv)
# PATCHOPS L5.12 END
'''


def main() -> int:
    if not COMMANDS_PATH.exists():
        raise SystemExit(f"commands.py not found: {COMMANDS_PATH}")
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if SENTINEL_START in text:
        print("L5.12 Edge readiness command wrapper already present")
        return 0
    if COMMAND in text:
        print("L5.12 command text already present; sentinel missing, appending guarded wrapper anyway")
    if not text.endswith("\n"):
        text += "\n"
    COMMANDS_PATH.write_text(text + "\n" + PATCH_BLOCK.strip() + "\n", encoding="utf-8")
    print("L5.12 Edge readiness command wrapper appended to patchops/llm_browser/commands.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())