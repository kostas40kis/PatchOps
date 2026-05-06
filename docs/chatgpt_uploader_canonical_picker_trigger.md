# ChatGPT Uploader Canonical Picker Trigger

As of U2.4H, the accepted picker-open trigger is:

```text
focus Edge
one calculated safe click
send `/`
send Enter once
detect picker
close picker if this is a trigger-only proof
```

## Canonical entrypoint

Future uploader patches should use:

```text
scripts/run_uploader_open_picker_canonical.py --allow-open-picker
```

or import:

```text
patchops.chatgpt_uploader.canonical_picker_trigger.run_canonical_picker_trigger
```

## Contract

Production mode is always one attempt. Stress-test loops must not be hidden inside production upload flow.

Forbidden picker-open backends:

```text
Tab
second Enter
plus-button UIA search
menu-item UIA search
Ctrl+U
Selenium/WebDriver
browser DOM automation
random clicking
```

## Safety boundary

The canonical trigger opens the picker only. It must not:

```text
write a report path
select a file
press Open/Enter inside the picker after detection
confirm attachment
claim upload success
send/submit
log conversation text
```

U2.5 may combine this canonical trigger with the existing exact report resolver/path writer, but it must preserve the same no-send boundary until a later explicit send patch.
