from __future__ import annotations

from pathlib import Path

COMMANDS_PATH = Path("patchops/llm_browser/commands.py")
SENTINEL_START = "# PATCHOPS L5.11 START"

PATCH_BLOCK = r'''
# PATCHOPS L5.11 START
# Passive browser-start supervised launch handoff L5 broad-validation CLI/readback surface.
# This wrapper forwards only to the accepted passive L5.11 readback module.
# It must not start a browser, import Selenium, create profile directories,
# click/download, paste/send, run downloaded packages, commit, or push.
import sys as _patchops_l5_11_sys

_PATCHOPS_L5_11_COMMAND = "browser-start-supervised-launch-handoff-l5-broad-validation"

try:
    _PATCHOPS_L5_11_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L5_11_PREV_BUILD_PARSER = None

if _PATCHOPS_L5_11_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L5_11_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L5_11_COMMAND not in choices:
                        readiness_parser = action.add_parser(
                            _PATCHOPS_L5_11_COMMAND,
                            help="Read back passive L5 broad validation without starting a browser.",
                        )
                        readiness_parser.add_argument("--repo-root", default=None)
                        readiness_parser.add_argument("--json", action="store_true")
                        readiness_parser.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_handoff_l5_broad_validation(args) -> int:
    from . import live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback.main(module_args)


try:
    _PATCHOPS_L5_11_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L5_11_PREV_COMMAND_NAMES = None

if _PATCHOPS_L5_11_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L5_11_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L5_11_COMMAND,) if name not in names)


_PATCHOPS_L5_11_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l5_11_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L5_11_COMMAND:
        from . import live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback
        return live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback.main(arg_list[1:])
    return _PATCHOPS_L5_11_PREV_MAIN(argv)
# PATCHOPS L5.11 END
'''


def main() -> int:
    if not COMMANDS_PATH.exists():
        raise SystemExit(f"commands.py not found: {COMMANDS_PATH}")
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if SENTINEL_START in text:
        print("L5.11 command wrapper already present")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    COMMANDS_PATH.write_text(text + "\n" + PATCH_BLOCK.strip() + "\n", encoding="utf-8")
    print("L5.11 command wrapper appended to patchops/llm_browser/commands.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())