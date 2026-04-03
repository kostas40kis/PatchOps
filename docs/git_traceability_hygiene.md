# Git and traceability hygiene

Git visibility is useful and strongly preferred, but it is not the same thing as PatchOps core correctness.

A missing `.git` directory or unavailable Git metadata should usually be interpreted as an environment / traceability warning unless there is evidence that a required workflow depends on Git.