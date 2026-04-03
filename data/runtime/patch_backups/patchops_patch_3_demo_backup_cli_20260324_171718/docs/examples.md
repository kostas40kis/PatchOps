# Examples

See the `examples/` folder for Stage 1 manifests:

- `trader_code_patch.json`
- `trader_doc_patch.json`
- `trader_verify_patch.json`
- `generic_python_patch.json`
- `generic_verify_patch.json`

## Safe proving order

Use examples in this order:

1. `generic_python_patch.json`
   - safe first apply run against a throwaway local project
2. `generic_verify_patch.json`
   - proves verification-only flow without rewriting files
3. `trader_code_patch.json`
   - first trader-shaped example after the wrapper itself is already proven
4. `trader_doc_patch.json`
   - documentation-oriented trader example
5. `trader_verify_patch.json`
   - trader verify-only example

These examples are intentionally simple. They demonstrate manifest shape, profile selection, report structure, and how validation commands attach to a run.