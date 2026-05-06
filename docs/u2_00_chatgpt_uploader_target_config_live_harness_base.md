# U2.0 ChatGPT uploader target config and live harness base

This patch starts the U2.x uploader hardening stream by turning the target URL and live evidence mechanics into reusable Python code.

## Added

- `patchops/chatgpt_uploader/config.py`
- `patchops/chatgpt_uploader/evidence.py`
- `scripts/set_chatgpt_copilot_target.py`
- `scripts/run_uploader_edge_preflight.py`
- `tests/test_chatgpt_uploader_u2_00_target_config_live_harness_current.py`

## Safety boundary

This patch does not upload a file and does not send a ChatGPT message.

Safety flags must stay false for:

- Selenium / WebDriver usage
- browser DOM automation
- Cloudflare or CAPTCHA bypass
- file upload attempt
- file dialog path writing
- attachment confirmation
- ChatGPT submit/send
- random page clicking
- conversation text logging

## Live proof

The live proof only reads the configured target, finds or launches normal Microsoft Edge, focuses the best Edge/ChatGPT candidate window, and writes JSON/TXT evidence.

Next patch: U2.1 exact report resolver.