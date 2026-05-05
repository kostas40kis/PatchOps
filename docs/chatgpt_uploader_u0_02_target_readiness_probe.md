# U0.2 ChatGPT uploader target readiness probe

U0.2 adds the first target-readiness probe for the PatchOps Co-Pilot uploader stream.

The probe is deliberately conservative:

- it inspects the configured target URL string;
- it verifies that the target is a ChatGPT conversation URL;
- it writes JSON and text evidence artifacts when an output directory is provided;
- it optionally allows a local pywinauto normal-Edge window diagnostic only behind an explicit gate;
- it performs no network request;
- it performs no browser DOM automation;
- it performs no upload;
- it performs no ChatGPT submit/send;
- it does not import Selenium.

The runnable smoke surface is:

```powershell
py -m patchops.chatgpt_uploader.target_readiness `
  --target-url "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f9e01d-f588-838f-b2c8-3e3f0f0153cf" `
  --output-dir "data/runtime/u0_02_chatgpt_uploader_target_readiness_probe" `
  --json
```

Safety expectations for this patch:

```text
webdriver_used:false
selenium_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
file_upload_attempted:false
chatgpt_submit_performed:false
conversation_text_logged:false
random_page_click_performed:false
```

This patch does not attempt report upload, file attach, pasteback, send, or downloader behavior. Those remain later Uploader/Downloader phases.
