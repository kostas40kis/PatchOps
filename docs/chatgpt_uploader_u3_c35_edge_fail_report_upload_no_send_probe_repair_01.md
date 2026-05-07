# U3 C35 Edge fail report upload no-send probe repair 01

Patch `u3_c35_edge_fail_report_upload_no_send_probe_repair_01` repairs the C35 evidence schema.

## Failure repaired

The focused C35 test expected `file_upload_attempted` as a top-level evidence field:

```text
payload["file_upload_attempted"] is True
```

The C35 result model only carried `file_upload_attempted` inside the nested `safety` object, so the JSON evidence raised `KeyError: 'file_upload_attempted'`.

## Repair

This repair adds:

```python
file_upload_attempted: bool
```

to `EdgeFailReportUploadNoSendResult` and assigns:

```python
file_upload_attempted=safety.file_upload_attempted
```

when building the result.

## Safety boundary

This is a schema-only repair. It does not add browser action, send action, upload send, DOM automation, Selenium/WebDriver, CAPTCHA/Cloudflare bypass, raw conversation logging, random clicking, or unbounded loops.