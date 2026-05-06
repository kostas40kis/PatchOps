# ChatGPT Uploader U2.0A Config Smoke Preseed Repair

U2.0A repairs the U2.0 apply-time failure where the config-only smoke could run before `data/config/chatgpt_copilot_target.json` existed.

## Fix

- Pre-seed `data/config/chatgpt_copilot_target.json` as a PatchOps-written file.
- Make `scripts/run_uploader_edge_preflight.py` catch missing/invalid target config errors.
- Ensure config-load failures still write JSON/TXT evidence and return `FAIL_OR_BLOCKED` with exit code `2`.
- Preserve the no-upload/no-send safety boundary.

## Safety

This repair still does not open the upload picker, select a file, attach a file, send a message, use Selenium/WebDriver, use browser DOM automation, or click random page coordinates.
