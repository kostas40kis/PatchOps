from pathlib import Path


def test_emitted_and_recovery_docs_refresh_keep_current_supported_surfaces() -> None:
    emitter_doc = Path("docs/operator_script_emitter.md").read_text(encoding="utf-8")
    recovery_doc = Path("docs/bootstrap_repair.md").read_text(encoding="utf-8")

    emitter_required = [
        "emit-operator-script",
        "run-package-zip",
        "maintenance-gate",
        "Windows PowerShell 5.1",
        "ArgumentList",
        "Arguments",
        "copy/paste-safe",
        "compatibility shim",
        "Keep PowerShell thin.",
        "Keep reusable mechanics in Python.",
    ]
    for phrase in emitter_required:
        assert phrase in emitter_doc

    recovery_required = [
        "bootstrap-repair",
        "patchops.bootstrap_repair",
        "patchops.cli bootstrap-repair",
        "not a second apply engine",
        "normal PatchOps CLI import chain is too broken",
        "Return to the normal `check` / `inspect` / `plan` / `apply` / `verify`",
    ]
    for phrase in recovery_required:
        assert phrase in recovery_doc
