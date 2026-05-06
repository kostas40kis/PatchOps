# ChatGPT Uploader U2.5 Canonical Open + Write Path, No Open

U2.5 is the first upload-stage composition patch.

It combines two accepted pieces:

1. U2.4I canonical picker trigger:

```text
focus Edge
one calculated safe click
send `/`
send Enter once
detect picker
```

2. U2.3 exact report path writer:

```text
resolve exact report path
write it into the already-open Windows file picker filename field
```

## U2.5 flow

```text
run canonical picker trigger with close_picker_on_detect=false
write exact report path into filename field
close picker for cleanup
stop
```

## Safety boundary

U2.5 must not:

```text
press Open
press Enter inside the picker after path write
select/confirm attachment
claim upload success
send/submit
use Tab
use second Enter
use plus/menu/Ctrl+U fallback
use Selenium/WebDriver
use browser DOM automation
perform random clicks
log conversation text
```

## Next step

U2.6 can decide whether to press Open after the path is written and then verify that ChatGPT shows an attachment. U2.6 must still avoid send/submit unless a later patch explicitly allows it.
