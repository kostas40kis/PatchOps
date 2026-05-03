from __future__ import annotations

from pathlib import Path

DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_real_probe_preflight_aggregate_gate.md")
PHRASE = "real filesystem probe requires a separate explicit preflight flag"
ANCHOR = "- real-probe preflight contract enforced."


def main() -> int:
    if not DOC_PATH.exists():
        raise FileNotFoundError(f"Expected L11.5 doc is missing: {DOC_PATH}")

    text = DOC_PATH.read_text(encoding="utf-8")
    if PHRASE in text:
        print("L11.5 doc phrase already present")
        return 0

    line = f"- {PHRASE}."
    if ANCHOR in text:
        text = text.replace(ANCHOR, ANCHOR + "\n" + line, 1)
    else:
        marker = "- six real-probe preflight fixtures remain stable."
        if marker in text:
            text = text.replace(marker, line + "\n" + marker, 1)
        else:
            text = text.rstrip() + "\n" + line + "\n"

    DOC_PATH.write_text(text, encoding="utf-8")
    print("L11.5 doc phrase repaired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())