# ChatGPT Uploader U2.4E Single Safe-Click Tab/Enter Trigger

U2.4E replaces the noisy U2.4D trigger stack with one path only:

```text
focus Edge
one calculated safe neutral click
Tab once
Enter once
if no picker is detected, Enter once more
stop immediately once picker is detected
close picker
```

## Removed from live actuation

U2.4E does not use:

```text
plus-button UIA search
menu-item UIA search
Ctrl+U
repeated fallback clicking
coordinate guessing beyond one calculated safe click
```

The click is deterministic and derived from the focused Edge window rectangle. The default point is:

```text
x = left + 50% of width
y = top + 34% of height
```

This is meant to land in the main page area and avoid the title bar, sidebar, composer, and obvious controls.

## Safety boundary

U2.4E may open and close the picker when explicitly called with:

```text
--allow-open-picker
--allow-single-safe-click-tab-enter
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

The second Enter is skipped if the picker is detected after the first Enter, to avoid pressing Open inside the picker.
