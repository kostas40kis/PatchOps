from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, '-m', 'patchops.cli', *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    runtime_dir = PROJECT_ROOT / 'data' / 'runtime' / 'check_launcher_bootstrap'
    runtime_dir.mkdir(parents=True, exist_ok=True)

    safe_launcher = runtime_dir / 'safe_launcher.ps1'
    safe_launcher.write_text(
        '& {\n'
        '    py -m patchops.cli apply .\\manifest.json\n'
        '}\n',
        encoding='utf-8',
    )

    risky_launcher = runtime_dir / 'risky_launcher.ps1'
    risky_launcher.write_text(
        'Get-Content state.json | ConvertFrom-Json\n'
        'Copy-Item .\\manifest.json .\\backup_manifest.json\n'
        'py -c "print(\'hi\')"\n',
        encoding='utf-8',
    )

    safe_completed = _run_cli('check-launcher', str(safe_launcher))
    if safe_completed.returncode != 0:
        raise AssertionError(
            'check-launcher returned nonzero for safe launcher:\n'
            + safe_completed.stdout
            + '\nSTDERR:\n'
            + safe_completed.stderr
        )
    safe_payload = json.loads(safe_completed.stdout)
    if not bool(safe_payload.get('ok')):
        raise AssertionError('safe launcher payload was not ok:\n' + json.dumps(safe_payload, indent=2, sort_keys=True))
    if int(safe_payload.get('issue_count', -1)) != 0:
        raise AssertionError('safe launcher issue_count was not zero:\n' + json.dumps(safe_payload, indent=2, sort_keys=True))

    risky_completed = _run_cli('check-launcher', str(risky_launcher))
    if risky_completed.returncode != 1:
        raise AssertionError(
            'check-launcher did not return 1 for risky launcher:\n'
            + risky_completed.stdout
            + '\nSTDERR:\n'
            + risky_completed.stderr
        )
    risky_payload = json.loads(risky_completed.stdout)
    if bool(risky_payload.get('ok')):
        raise AssertionError('risky launcher payload unexpectedly ok:\n' + json.dumps(risky_payload, indent=2, sort_keys=True))
    joined = '\n'.join(str(x) for x in risky_payload.get('issues', []))
    lowered = joined.lower()
    if not any(term in lowered for term in ['json', 'convertfrom-json', 'copy', 'inline python', 'py -c']):
        raise AssertionError('risky launcher issues did not mention expected patterns:\n' + json.dumps(risky_payload, indent=2, sort_keys=True))

    print('check-launcher bootstrap validation PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
