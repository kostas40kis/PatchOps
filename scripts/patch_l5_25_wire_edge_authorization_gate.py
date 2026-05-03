from __future__ import annotations

from pathlib import Path

COMMANDS_PATH = Path("patchops/llm_browser/commands.py")
SENTINEL_START = "# PATCHOPS L5.25 START"
COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-gate"

PATCH_BLOCK = r'''
# PATCHOPS L5.25 START
# Passive Microsoft Edge supervised-launch explicit authorization argument gate.
# This block only registers/routes readback and performs no Selenium import,
# browser startup, profile creation, click/download, paste/send, package-run,
# commit, or push side effect.
import sys as _patchops_l5_25_sys

_PATCHOPS_L5_25_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-gate"

try:
    _PATCHOPS_L5_25_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L5_25_PREV_BUILD_PARSER = None

if _PATCHOPS_L5_25_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L5_25_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L5_25_COMMAND not in choices:
                        auth_parser = action.add_parser(
                            _PATCHOPS_L5_25_COMMAND,
                            help="Read back the passive Microsoft Edge supervised-launch explicit authorization argument gate.",
                        )
                        auth_parser.add_argument("--repo-root", default=None)
                        auth_parser.add_argument("--allow-live-start", action="store_true", dest="allow_live_start")
                        auth_parser.add_argument("--profile-dir", default=None)
                        auth_parser.add_argument("--json", action="store_true")
                        auth_parser.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_live_start_authorization_gate(args) -> int:
    from . import live_adapter_edge_supervised_launch_explicit_authorization_argument_gate
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "allow_live_start", False):
        module_args.append("--allow-live-start")
    profile_dir = getattr(args, "profile_dir", None)
    if profile_dir:
        module_args.extend(["--profile-dir", str(profile_dir)])
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_supervised_launch_explicit_authorization_argument_gate.main(module_args)


try:
    _PATCHOPS_L5_25_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L5_25_PREV_COMMAND_NAMES = None

if _PATCHOPS_L5_25_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L5_25_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L5_25_COMMAND,) if name not in names)


_PATCHOPS_L5_25_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    raw = list(_patchops_l5_25_sys.argv[1:] if argv is None else argv)
    if raw and raw[0] == _PATCHOPS_L5_25_COMMAND:
        from . import live_adapter_edge_supervised_launch_explicit_authorization_argument_gate
        return live_adapter_edge_supervised_launch_explicit_authorization_argument_gate.main(raw[1:])
    return _PATCHOPS_L5_25_PREV_MAIN(argv)
# PATCHOPS L5.25 END
'''


def main() -> int:
    if not COMMANDS_PATH.exists():
        raise SystemExit(f"commands.py not found: {COMMANDS_PATH}")
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if SENTINEL_START in text:
        print("L5.25 Edge explicit authorization argument gate command wrapper already present")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    COMMANDS_PATH.write_text(text + "\n" + PATCH_BLOCK.strip() + "\n", encoding="utf-8")
    print("L5.25 Edge explicit authorization argument gate command wrapper appended to patchops/llm_browser/commands.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())