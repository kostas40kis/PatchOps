# ChatGPT Uploader U2.4G Slash Enter Trigger

U2.4G keeps the quiet single safe-click trigger contract but changes the key sequence:

```text
focus Edge
one calculated safe click
send `/`
send Enter once
detect picker
close picker if detected
```

## Removed from this trigger

```text
Tab
second Enter
plus-button search
menu-item search
Ctrl+U
repeated production attempts
```

## Safety boundary

U2.4G must not:

```text
write a report path
select a file
press Open/Enter inside the picker after detection
confirm attachment
claim upload success
send/submit
use Selenium/WebDriver
use browser DOM automation
perform random clicks
log conversation text
```

This patch is a trigger-only test. U2.5 can later combine the best picker trigger with exact report-path writing.
