# ChatGPT Uploader U2.7 Attachment Verification, No Send

U2.6A proved the full live pre-send upload path:

```text
normal Edge launch requested
canonical picker trigger
exact report path typed
Enter pressed once in the Windows picker
picker closed
no ChatGPT send
```

U2.7 adds the next proof layer: after the upload attempt, verify that the expected report filename is visible as an attachment in the Edge UI Automation tree.

## Flow

```text
run U2.6A recovery/upload stage
if upload stage passes:
  focus configured Edge target
  inspect UIA accessible names for the expected report filename only
  pass if the exact filename appears
stop before ChatGPT Send
```

## Safety boundary

U2.7 must not:

```text
send/submit ChatGPT
read or log conversation text
use Selenium/WebDriver
use browser DOM automation
use Tab
use second Enter
use plus/menu/Ctrl+U fallback
perform random clicks
```

The verifier records only filename-match evidence, not the full page text.

## Next step

After U2.7 passes live, U2.8 can either strengthen attachment readiness checks or add an explicit gated final-send patch. Send must remain disabled until a dedicated send patch clearly changes that boundary.
