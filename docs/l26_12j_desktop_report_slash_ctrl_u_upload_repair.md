# L26.12J Desktop Report Slash+Ctrl+U Upload Repair

L26.12I opened an OS-side window and selected a path, but it still failed to observe a staged upload. The operator corrections after that run are now part of the contract:

- do not use the `/` command menu and then also press the `+` button;
- type `/` in the composer, then press Ctrl+U directly;
- the program must change/navigate the picker directory instead of only detecting a window;
- the report path is decided by the script/PatchOps and is normally on Desktop;
- save that report first, then upload the report.

L26.12J changes the control flow accordingly:

1. Run the PatchOps patch normally first, without live browser validation inside `apply`.
2. Write the Desktop operator report path that the outer script controls.
3. Copy that report to a closed runtime upload-safe copy to avoid Desktop/OneDrive file-lock problems.
4. Attach to the already-open ChatGPT chat without navigation/refresh.
5. Clear the composer, type `/`, and press Ctrl+U directly.
6. Do not press the plus button after typing `/`.
7. Detect only strict OS picker windows, rejecting non-picker classes such as `rctrl_renwnd32`.
8. Change the picker directory with Ctrl+L, then enter the safe-copy file name.
9. Confirm with Enter inside the OS picker only.
10. Wait for the attachment to stage.

This patch still forbids final ChatGPT submit/send. It proves attachment staging first. A later patch may add explicit gated send after staging is proven.
