# ChatGPT Uploader U2.4D Tab/Enter Trigger Path

U2.4D implements the operator-observed picker-opening path:

```text
focus Edge
optional calculated neutral click inside the focused Edge document area
Tab
Enter
if no picker is detected, Enter once more
stop immediately if a picker is detected
close the picker
```

## Why this patch exists

U2.4C did not reach live testing because a text evidence spacing regression failed an older test. U2.4D repairs that spacing while adding a new explicit trigger backend.

## Safety rules

U2.4D may open and close the picker when explicitly called with:

```text
--allow-open-picker
--allow-tab-enter-sequence
--allow-neutral-click
```

It must not:

```text
write a report path
select a file
press Open/Enter inside the picker
confirm attachment
claim upload success
send/submit
use Selenium/WebDriver
use browser DOM automation
perform random clicks
log conversation text
```

The neutral click is calculated from the focused Edge window rectangle and deliberately avoids title bar, side rails, and the bottom composer row. It is recorded as `neutral_click_attempted`, while `random_page_click_performed` remains false.

## Acceptance target

Preferred live target:

```text
5/5 attempts pass
picker opens and closes every time
no file path written
no file selected
no Open pressed
no send
```
