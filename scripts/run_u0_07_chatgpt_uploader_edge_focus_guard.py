from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_repo_root() -> None:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[1]
    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)


_bootstrap_repo_root()

from patchops.chatgpt_uploader.edge_focus_guard import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
