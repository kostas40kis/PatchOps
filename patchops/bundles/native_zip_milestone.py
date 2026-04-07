from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Mapping

from .checker import check_bundle_zip
from .launcher_invoker import invoke_bundled_launcher
from .report_chain import BundleReportChain, build_bundle_report_chain, bundle_report_chain_as_dict


@dataclass(frozen=True)
class NativeZipMilestoneProof:
    check: Any
    launcher_invocation: Any
    report_chain: BundleReportChain
    mode: str
    wrapper_project_root: Path
    operator_one_liner: str

    @property
    def patch_name(self) -> str | None:
        return self.report_chain.patch_name

    @property
    def bundle_zip_path(self) -> str | None:
        return self.report_chain.bundle_zip_path

    @property
    def extracted_bundle_root(self) -> str | None:
        return self.report_chain.extracted_bundle_root

    @property
    def launcher_path(self) -> str | None:
        return self.report_chain.launcher_path

    @property
    def exit_code(self) -> int:
        return int(getattr(self.launcher_invocation, 'exit_code', 1))

    @property
    def result_label(self) -> str:
        return 'PASS' if self.exit_code == 0 else 'FAIL'

    @property
    def operator_can_skip_manual_unzip(self) -> bool:
        return True

    @property
    def proof_summary(self) -> str:
        return (
            'PatchOps can start from the raw zip, extract it, locate the bundled launcher, '
            'and invoke it without manual extraction by the operator.'
        )


def _build_operator_one_liner(bundle_zip_path: str | Path, wrapper_project_root: str | Path, mode: str) -> str:
    command_name = 'apply-bundle' if str(mode).strip().lower() != 'verify' else 'verify-bundle'
    return (
        'py -c "import json; from patchops.bundles.cli_commands import run_bundle_command; '
        f"print(json.dumps(run_bundle_command('{command_name}', r'{bundle_zip_path}', r'{wrapper_project_root}'), indent=2))" + '"'
    )


def prove_native_zip_milestone(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    mode: str = 'apply',
    timestamp_token: str | None = None,
    powershell_program: str = 'powershell',
    launcher_invoke_func: Callable[..., Any] | None = None,
    launcher_env: Mapping[str, str] | None = None,
) -> NativeZipMilestoneProof:
    check_result = check_bundle_zip(
        bundle_zip_path,
        wrapper_project_root,
        timestamp_token=timestamp_token,
    )
    invoke_func = launcher_invoke_func or invoke_bundled_launcher
    launcher_invocation = invoke_func(
        check_result.extraction.bundle_root,
        wrapper_project_root,
        mode=mode,
        powershell_program=powershell_program,
        env=launcher_env,
    )

    metadata = getattr(check_result, 'metadata', None)
    proof_view = SimpleNamespace(
        metadata=metadata,
        extraction=check_result.extraction,
        launcher_invocation=launcher_invocation,
        target_project_root=getattr(metadata, 'target_project_root', None),
        report_path=getattr(launcher_invocation, 'report_path', None),
        inner_report_path=getattr(launcher_invocation, 'inner_report_path', None),
    )
    chain = build_bundle_report_chain(proof_view)
    return NativeZipMilestoneProof(
        check=check_result,
        launcher_invocation=launcher_invocation,
        report_chain=chain,
        mode=str(mode).strip().lower(),
        wrapper_project_root=Path(wrapper_project_root),
        operator_one_liner=_build_operator_one_liner(bundle_zip_path, wrapper_project_root, mode),
    )


prove_bundle_native_zip_milestone = prove_native_zip_milestone


def native_zip_milestone_as_dict(result: NativeZipMilestoneProof) -> dict[str, Any]:
    payload = bundle_report_chain_as_dict(result.report_chain)
    payload.update(
        {
            'mode': result.mode,
            'wrapper_project_root': str(result.wrapper_project_root),
            'launcher_exit_code': result.exit_code,
            'launcher_stdout': getattr(result.launcher_invocation, 'stdout', ''),
            'launcher_stderr': getattr(result.launcher_invocation, 'stderr', ''),
            'result_label': result.result_label,
            'operator_can_skip_manual_unzip': result.operator_can_skip_manual_unzip,
            'operator_one_liner': result.operator_one_liner,
            'proof_summary': result.proof_summary,
        }
    )
    return payload
