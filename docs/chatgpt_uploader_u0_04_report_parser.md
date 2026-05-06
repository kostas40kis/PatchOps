# U0.4 ChatGPT uploader report parser

This patch adds the Co-Pilot uploader report parser.

## Scope

U0.4 reads a local PatchOps canonical txt report and extracts a compact machine-readable summary.

It may extract:

- result;
- exit code;
- failure category;
- failure layer;
- patch name;
- report path;
- first failing command when clearly present;
- primary Python-style error evidence when present;
- known safety flags when present.

## Boundaries

This patch does not:

- upload files;
- paste into ChatGPT;
- send a message;
- start Microsoft Edge;
- use Selenium or WebDriver;
- inspect browser DOM;
- bypass CAPTCHA or Cloudflare;
- build `PATCHOPS_LLM_PASTEBACK`.

`PATCHOPS_LLM_PASTEBACK` construction remains U0.5.

## Added files

```text
patchops/chatgpt_uploader/report_parser.py
tests/test_chatgpt_uploader_report_parser_current.py
scripts/run_u0_04_chatgpt_uploader_report_parser.py
docs/chatgpt_uploader_u0_04_report_parser.md
```

## Acceptance

```text
report_parsed:true
exit_code_extracted:true
result_extracted:true
failure_layer_classified:true
file_upload_attempted:false
chatgpt_submit_performed:false
selenium_used:false
webdriver_used:false
```
