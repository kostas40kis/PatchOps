from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    llm_usage = root / "docs" / "llm_usage.md"

    text = llm_usage.read_text(encoding="utf-8")
    marker = "PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:START"
    if marker not in text:
        raise SystemExit(f"Patch 84 LLM usage block not found in {llm_usage}.")

    if "starter --profile" in text:
        message = "starter --profile already present in llm_usage.md"
    else:
        anchor = "generate the first manifest from the closest example or `starter`,"
        replacement = (
            "generate the first manifest from the closest example or `starter --profile ... --intent ...`,"
        )
        if anchor not in text:
            raise SystemExit(f"Expected anchor line not found in {llm_usage}.")
        text = text.replace(anchor, replacement, 1)
        message = "Inserted explicit starter --profile phrase into llm_usage.md"

    llm_usage.write_text(text, encoding="utf-8")
    print(json.dumps({"written_files": [str(llm_usage)], "message": message}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())