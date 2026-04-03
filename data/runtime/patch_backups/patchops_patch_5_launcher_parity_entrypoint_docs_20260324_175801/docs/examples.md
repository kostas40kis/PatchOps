# Examples

See the `examples/` folder for Stage 1 manifests:

- `generic_python_patch.json`
- `generic_backup_patch.json`
- `generic_verify_patch.json`
- `trader_code_patch.json`
- `trader_doc_patch.json`
- `trader_verify_patch.json`

## Safe proving order

Use examples in this order:

1. `generic_python_patch.json`
   - run `inspect`
   - run `plan`
   - safe first apply run against a throwaway local project

2. `generic_backup_patch.json`
   - run `inspect`
   - run `plan`
   - proves backup behavior by overwriting an existing file after the first generic apply run

3. `generic_verify_patch.json`
   - run `inspect`
   - run `plan --mode verify`
   - proves verification-only flow without rewriting files

4. `trader_code_patch.json`
   - first trader-shaped example after the wrapper itself is already proven

5. `trader_doc_patch.json`
   - documentation-oriented trader example

6. `trader_verify_patch.json`
   - trader verify-only example

These examples are intentionally simple. They demonstrate manifest shape, profile selection, pre-apply resolution, report structure, and how validation commands attach to a run.