# Repair 17: operator-observed type-path attempt

Patch `pseudo_self_report_upload_no_send_repair_17_operator_observed_type_path` changes the workflow per operator instruction.

## Operator instruction

Do not use code to validate whether UI steps happened. The operator will report what happened.

## Previous stuck point

The Windows file picker opens, but nothing is written into it. Repair 16 also showed the script failed while trying to write into candidate controls.

## New behavior

This patch does not inspect the picker, does not validate attachment, and does not decide whether upload happened.

It attempts only this sequence:

```text
use existing Chrome / current foreground flow
press /
press Enter
wait briefly for the Windows file picker that the operator sees
type the full Desktop path literally
press Enter
stop
```

## Full path attempted

```text
C:\Users\vicky\Desktop\pseudo_self_report_upload_no_send_repair_17_operator_observed_type_path_self_report.txt
```

## Evidence meaning

A PASS for this patch means only:

```text
the attempt sequence ran
```

It does **not** mean the file attached. The operator is the source of truth.

## Evidence contract

```text
operator_observed_mode:true
automated_ui_step_validation_used:false
automated_attachment_verification_used:false
slash_key_attempted:true
upload_command_enter_attempted:true
full_path_type_attempted:true
picker_enter_attempted:true
operator_must_confirm_visible_result:true
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

No new Chrome tab, no mouse clicks, no Tab trigger, no clipboard/Ctrl+V, no native dialog introspection, no UI-step validation, no Selenium/WebDriver, no DOM automation, no raw conversation logging, no Send.