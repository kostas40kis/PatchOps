# L26.12E Upload-Safe Report Copy Strict Menu Repair

L26.12D made real progress: the current-URL guard worked, the target page was ready, composer focus passed, report discovery passed, the plus button was found/clicked, and an upload-menu candidate was found/clicked. The selected candidate was wrong, however: it was a OneDrive upload/sync status control. No file picker opened.

The operator also observed a Windows error that the selected report file was in use by another program. The likely cause is uploading directly from a Desktop/OneDrive-synced report file while the file is open or being synced.

L26.12E repairs both layers:

- keep the current-URL guard and skip refresh/navigation when the target chat is already loaded;
- create an upload-safe copy of the selected report under the runtime output directory, outside Desktop/OneDrive;
- close and reopen the upload-safe copy to prove PatchOps is not holding the file handle;
- verify the source/copy hash and size match;
- reject OneDrive/sync/status/tray/notification controls as upload-menu candidates;
- click only stricter ChatGPT upload labels such as Upload files, Upload from computer, Add photos and files, Browse, or Attach files;
- stage the upload-safe copy;
- keep ChatGPT send forbidden.

Forbidden:

- pressing Enter in the ChatGPT composer;
- submitting a ChatGPT prompt;
- activating the send button;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full URLs, file paths, prompt text, file contents, or conversation text.
