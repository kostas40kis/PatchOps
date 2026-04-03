# Manifest Schema

Stage 1 uses a JSON manifest with `manifest_version: "1"`.

## Required fields

- `manifest_version`
- `patch_name`
- `active_profile`

## Main optional fields

- `target_project_root`
- `backup_files`
- `files_to_write`
- `validation_commands`
- `smoke_commands`
- `audit_commands`
- `cleanup_commands`
- `archive_commands`
- `report_preferences`
- `failure_policy`
- `tags`
- `notes`

## `files_to_write` item

```json
{
  "path": "relative/path/from/target/root.txt",
  "content": "inline content",
  "encoding": "utf-8"
}
```

or

```json
{
  "path": "relative/path/from/target/root.txt",
  "content_path": "relative/path/from/manifest/file.txt",
  "encoding": "utf-8"
}
```

## Command item

```json
{
  "name": "pytest",
  "use_profile_runtime": true,
  "args": ["-m", "pytest", "tests/test_sample.py"],
  "working_directory": ".",
  "allowed_exit_codes": [0]
}
```

If `use_profile_runtime` is false or omitted, provide `program` explicitly.

## CLI schema reference

`patchops schema` prints a JSON summary of the manifest contract. This is useful when you want a fast, machine-readable reminder of required fields, optional fields, command-group meaning, and starter notes before generating or editing a manifest.

### Report preference examples

Use `report_name_prefix` when you want the canonical report filename to begin with a stable label such as a patch slug. Use `report_dir` when you want the report written to a deterministic directory instead of the default location. Keep `write_to_desktop` true when you still want a Desktop evidence copy.
