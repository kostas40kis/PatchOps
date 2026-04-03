class PatchOpsError(Exception):
    """Base exception for PatchOps."""


class ManifestError(PatchOpsError):
    """Raised when a manifest is invalid."""


class ProfileResolutionError(PatchOpsError):
    """Raised when a profile cannot be resolved."""


class WrapperExecutionError(PatchOpsError):
    """Raised when wrapper mechanics fail during a run."""
