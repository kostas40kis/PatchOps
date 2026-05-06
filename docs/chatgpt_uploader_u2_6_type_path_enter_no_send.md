# ChatGPT Uploader U2.6 Type Path + Enter, No Send

U2.5 proved the canonical picker opens, but the UIA filename-field writer returned:

```text
FAIL_PATH_WRITE_NOT_VERIFIED
```

The operator confirmed the simpler real workflow:

```text
when Windows File Explorer opens, type or paste the file path and press Enter
```

U2.6 implements that workflow.

## U2.6 flow

```text
run canonical picker trigger with close_picker_on_detect=false
type the exact PatchOps apply report path
press Enter once inside the Windows picker
wait for the picker to close
stop before ChatGPT Send
```

## Safety boundary

U2.6 may:

```text
type the exact report path
press Enter once in the Windows picker
attempt the file upload/attachment selection
```

U2.6 must not:

```text
send/submit the ChatGPT message
use Tab
use second Enter
use plus/menu/Ctrl+U fallback
use Selenium/WebDriver
use browser DOM automation
perform random clicks
log conversation text
```

Attachment verification is intentionally left for a later patch. U2.6 only proves that the picker accepts the path and closes after Enter.
