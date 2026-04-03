from __future__ import annotations
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
checks = {
    root / 'README.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'llm_usage.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'operator_quickstart.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'project_status.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'patch_ledger.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'summary_integrity_repair_stream.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
}
for path, needle in checks.items():
    text = path.read_text(encoding='utf-8')
    if needle not in text:
        raise SystemExit(f'missing marker in {path}')
print('patch_134f validation passed')
