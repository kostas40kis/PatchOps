# Self-hosted PatchOps helper note

When PatchOps prints a `Report Path` line in stdout, treat that as the source of truth.

Do not guess the report filename pattern if the exact path was already emitted.