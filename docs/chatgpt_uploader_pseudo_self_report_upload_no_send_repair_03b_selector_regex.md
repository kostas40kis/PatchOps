# Repair 03b: regex selector replacement

This repair replaces the current Chrome attachment selector using a regex block replacement instead of an exact template match.

It broadens semantic attachment names and adds a bounded lower-left composer UIA fallback for blank Chrome accessibility names.

Expected live smoke label:

```text
PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND
```

No-enter/no-send contract remains:

```text
enter_key_pressed:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

The fallback still clicks an actual visible and enabled UIA element. It does not use DOM automation, Selenium/WebDriver, random clicks, bypass behavior, raw conversation logging, Enter fallback, or Send.