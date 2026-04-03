"""Pure rerun-decision helpers for maintenance-grade next-mode guidance."""

VERIFY_ONLY = 'verify_only'
WRAPPER_ONLY_REPAIR = 'wrapper_only_repair'


def should_recommend_verify_only(*, failure_class: str | None, target_content_already_present: bool, writes_applied_by_wrapper: bool) -> bool:
    """Return True when the next truthful move is verify-only.

    The helper stays intentionally narrow. It only answers whether a run already
    matches the verify-only pattern based on already-known classification and evidence.
    """
    if failure_class != 'target_project_failure':
        return False
    if not target_content_already_present:
        return False
    if writes_applied_by_wrapper:
        return False
    return True

def should_recommend_wrapper_only_repair(*, failure_class: str | None, target_content_already_present: bool, writes_applied_by_wrapper: bool) -> bool:
    """Return True when wrapper-only repair is the narrow truthful next mode."""
    if failure_class != 'wrapper_failure':
        return False
    if not target_content_already_present:
        return False
    if writes_applied_by_wrapper:
        return False
    return True
