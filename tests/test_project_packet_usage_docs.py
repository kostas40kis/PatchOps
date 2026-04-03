from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_examples_mentions_project_packets_and_examples_boundary() -> None:
    text = read_text("docs/examples.md").lower()
    for token in [
        "project packet",
        "docs/projects/",
        "examples remain the baseline",
        "check",
        "inspect",
        "plan",
    ]:
        assert token in text


def test_operator_quickstart_mentions_both_start_paths() -> None:
    text = read_text("docs/operator_quickstart.md").lower()
    for token in [
        "handoff/current_handoff.md",
        "docs/project_packet_contract.md",
        "docs/project_packet_workflow.md",
        "docs/projects/",
        "project-packet-aware usage",
    ]:
        assert token in text


def test_project_status_mentions_rollout_and_future_generator_work() -> None:
    text = read_text("docs/project_status.md").lower()
    for token in [
        "project packet rollout status",
        "docs/projects/",
        "trader.md",
        "generation and refresh support",
        "future work",
    ]:
        assert token in text