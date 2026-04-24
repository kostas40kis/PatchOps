from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_readme_mentions_pythonization_maintenance_surfaces_current() -> None:
    text = _read("README.md")
    assert "## Pythonization stream maintenance note" in text
    assert "suspicious-run rule detection" in text
    assert "optional artifact emission behind an explicit opt-in flag" in text
    assert "short canonical report mention" in text
    assert "maintenance-grade wrapper-health aids" in text


def test_project_status_records_live_stream_frontier_without_overclaiming_redesign() -> None:
    text = _read("docs/project_status.md")
    assert "## Pythonization stream maintenance status" in text
    assert "green through MP48 in the current live patch sequence" in text
    assert "MP49 example and template alignment stop" in text
    assert "MP50 one real self-hosted PatchOps-on-PatchOps proof patch" in text
    assert "MP51 final status refresh for the stream" in text
    assert "does not redesign manifests, profiles, reports, handoff, or the PowerShell/Python boundary" in text


def test_final_reference_frames_suspicious_run_support_as_conservative_wrapper_health_aid() -> None:
    text = _read("docs/patchops_final_reference.md")
    assert "## Pythonization maintenance addendum" in text
    assert "small Python-owned suspicious-run support layer" in text
    assert "artifact emission is opt-in in the first release" in text
    assert "wrapper-health support only" in text
    assert "not target-project business logic and it is not a product redesign" in text
