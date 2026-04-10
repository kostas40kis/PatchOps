from pathlib import Path


def test_top_level_docs_reflect_post_publish_state_and_current_surfaces() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    project_status = Path("docs/project_status.md").read_text(encoding="utf-8")
    llm_usage = Path("docs/llm_usage.md").read_text(encoding="utf-8")

    assert "Patch 26" in readme
    assert "main" in readme
    assert "maintenance-gate" in readme
    assert "emit-operator-script" in readme
    assert "bootstrap-repair" in readme
    assert "Push-PatchOpsToGitHub.ps1" in readme
    assert "canonical Desktop txt report" in readme
    assert "post_publish_snapshot.md" in readme

    assert "Patch 26" in project_status
    assert "published-state snapshot" in project_status
    assert "GitHub publish helper" in project_status
    assert "maintenance mode" in project_status
    assert "main" in project_status

    assert "post_publish_snapshot.md" in llm_usage
    assert "bootstrap_repair.md" in llm_usage
    assert "github_publish_helper.md" in llm_usage
    assert "Prefer narrow repair over broad rewrite." in llm_usage
    assert "Push-PatchOpsToGitHub.ps1" in llm_usage
