from __future__ import annotations

__all__: list[str] = []

try:
    from .launcher_builder import build_patchops_bundle_launcher, ensure_powershell_block_wrapped

    __all__.extend([
        "build_patchops_bundle_launcher",
        "ensure_powershell_block_wrapped",
    ])

    try:
        from .launcher_builder import render_single_launcher_script
    except Exception:  # pragma: no cover - compatibility alias only
        render_single_launcher_script = build_patchops_bundle_launcher

    __all__.append("render_single_launcher_script")
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .models import (
        STANDARD_EXTRACTED_BUNDLE_LAYOUT,
        BundleMeta,
        ExtractedBundleLayout,
        ResolvedBundleLayout,
        build_standard_extracted_bundle_layout,
        load_bundle_metadata,
        resolve_bundle_layout,
    )

    __all__.extend([
        "STANDARD_EXTRACTED_BUNDLE_LAYOUT",
        "BundleMeta",
        "ExtractedBundleLayout",
        "ResolvedBundleLayout",
        "build_standard_extracted_bundle_layout",
        "load_bundle_metadata",
        "resolve_bundle_layout",
    ])

    try:
        from .models import BundleSchemaModel
        __all__.append("BundleSchemaModel")
    except Exception:  # pragma: no cover - optional newer surface
        pass
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .validator import BundleValidationMessage, BundleValidationResult, validate_extracted_bundle_dir

    BundleValidationIssue = BundleValidationMessage
    validate_extracted_bundle = validate_extracted_bundle_dir

    __all__.extend([
        "BundleValidationMessage",
        "BundleValidationIssue",
        "BundleValidationResult",
        "validate_extracted_bundle",
        "validate_extracted_bundle_dir",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .zip_loader import (
        BUNDLE_RUN_ROOT_RELATIVE,
        EXTRACTED_BUNDLE_DIR_NAME,
        BundleZipExtractionResult,
        build_bundle_run_root,
        extract_bundle_zip,
        sanitize_bundle_name_from_zip,
    )

    __all__.extend([
        "BUNDLE_RUN_ROOT_RELATIVE",
        "EXTRACTED_BUNDLE_DIR_NAME",
        "BundleZipExtractionResult",
        "build_bundle_run_root",
        "extract_bundle_zip",
        "sanitize_bundle_name_from_zip",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .checker import BundleCheckResult, check_bundle_zip

    check_bundle_archive = check_bundle_zip

    __all__.extend([
        "BundleCheckResult",
        "check_bundle_archive",
        "check_bundle_zip",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .inspector import BundleInspectResult, inspect_bundle_zip

    inspect_bundle_archive = inspect_bundle_zip

    __all__.extend([
        "BundleInspectResult",
        "inspect_bundle_archive",
        "inspect_bundle_zip",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .planner import BundlePlanResult, plan_bundle_zip

    plan_bundle_archive = plan_bundle_zip

    __all__.extend([
        "BundlePlanResult",
        "plan_bundle_archive",
        "plan_bundle_zip",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .applier import BundleApplyResult, apply_bundle_zip

    apply_bundle_archive = apply_bundle_zip

    __all__.extend([
        "BundleApplyResult",
        "apply_bundle_archive",
        "apply_bundle_zip",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .verifier import BundleVerifyResult, verify_bundle_zip

    verify_bundle_archive = verify_bundle_zip

    __all__.extend([
        "BundleVerifyResult",
        "verify_bundle_archive",
        "verify_bundle_zip",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .launcher_invoker import (
        LEGACY_LAUNCHER_DIR,
        ROOT_SINGLE_LAUNCHER_NAME,
        BundleLauncherInvocationResult,
        BundleLauncherResolution,
        build_bundled_launcher_command,
        invoke_bundled_launcher,
        resolve_bundle_launcher,
        resolve_bundled_launcher,
    )

    __all__.extend([
        "LEGACY_LAUNCHER_DIR",
        "ROOT_SINGLE_LAUNCHER_NAME",
        "BundleLauncherInvocationResult",
        "BundleLauncherResolution",
        "build_bundled_launcher_command",
        "invoke_bundled_launcher",
        "resolve_bundle_launcher",
        "resolve_bundled_launcher",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass

try:
    from .report_chain import BundleReportChain, build_bundle_report_chain, bundle_report_chain_as_dict

    __all__.extend([
        "BundleReportChain",
        "build_bundle_report_chain",
        "bundle_report_chain_as_dict",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass


try:
    from .native_zip_milestone import (
        NativeZipMilestoneProof,
        native_zip_milestone_as_dict,
        prove_bundle_native_zip_milestone,
        prove_native_zip_milestone,
    )

    __all__.extend([
        "NativeZipMilestoneProof",
        "native_zip_milestone_as_dict",
        "prove_bundle_native_zip_milestone",
        "prove_native_zip_milestone",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass


try:
    from .launcher_formatter import (
        DEFAULT_LAUNCHER_ENCODING,
        DEFAULT_LAUNCHER_NEWLINE,
        SUPPORTED_LAUNCHER_MODES,
        BundleLauncherFormatResult,
        build_standard_bundle_launcher,
        ensure_safe_launcher_wrapper,
        format_bundle_launcher,
        is_launcher_safely_wrapped,
        normalize_bundle_launcher_text,
        normalize_launcher_newlines,
        render_standard_bundle_launcher,
        strip_leading_launcher_artifacts,
    )

    __all__.extend([
        "DEFAULT_LAUNCHER_ENCODING",
        "DEFAULT_LAUNCHER_NEWLINE",
        "SUPPORTED_LAUNCHER_MODES",
        "BundleLauncherFormatResult",
        "build_standard_bundle_launcher",
        "ensure_safe_launcher_wrapper",
        "format_bundle_launcher",
        "is_launcher_safely_wrapped",
        "normalize_bundle_launcher_text",
        "normalize_launcher_newlines",
        "render_standard_bundle_launcher",
        "strip_leading_launcher_artifacts",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass


__all__ = list(dict.fromkeys(__all__))

try:
    from .launcher_heuristics import (
        LauncherHeuristicFinding,
        LauncherHeuristicReport,
        audit_bundle_launcher_text,
        find_common_launcher_mistakes,
    )

    __all__.extend([
        "LauncherHeuristicFinding",
        "LauncherHeuristicReport",
        "audit_bundle_launcher_text",
        "find_common_launcher_mistakes",
    ])
except Exception:  # pragma: no cover - optional compatibility export guard
    pass


__all__ = list(dict.fromkeys(__all__))
