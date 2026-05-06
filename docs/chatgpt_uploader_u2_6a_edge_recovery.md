# ChatGPT Uploader U2.6A Edge Recovery Then Type Path Enter, No Send

U2.6 applied successfully, but the live stage was blocked because Edge was shut down. U2.6A does not change the canonical uploader mechanics. It adds an explicit recovery layer for that environment state.

## Flow

```text
if --allow-launch-edge is provided:
  open the configured ChatGPT target URL in normal Microsoft Edge
  wait briefly for Edge/session restore/login readiness
then:
  run U2.6 canonical picker trigger
  type the exact PatchOps apply report path
  press Enter once inside the Windows picker
  do not press ChatGPT Send
```

## Safety boundary

U2.6A may launch normal Microsoft Edge only when explicitly gated:

```text
--allow-launch-edge
```

It must not:

```text
overwrite the target config
hardcode a ChatGPT URL
use Selenium/WebDriver
use browser DOM automation
use Tab
use second Enter
use plus/menu/Ctrl+U fallback
send/submit ChatGPT
log conversation text
```

If the configured target opens to login, CAPTCHA, Cloudflare, or any other operator-required state, the uploader must fail/block with evidence rather than attempting bypass.
