# ChatGPT Uploader U2.0E Win32 Edge Focus Fallback

U2.0E adds a Win32 top-level window fallback for the focus-only Edge preflight.

U2.0D proved the code path and target config, but the live focus still blocked. The next safest step is not upload and not navigation. It is a better local window discovery/focus primitive.

## Added behavior

- Keep UIA window discovery first.
- If UIA cannot find/focus a safe candidate, enumerate visible top-level windows through Win32.
- Identify `msedge.exe` windows by process image name.
- For root target `https://chatgpt.com/`, allow exactly one visible Edge window as a focus candidate.
- If multiple Edge windows are found, block as ambiguous.
- Write UIA and Win32 details into evidence for diagnosis.

## Safety boundary

No upload, no file picker, no attachment selection, no send/submit, no Selenium/WebDriver, no browser DOM automation, no random clicking, no conversation text logging, no automatic URL launch.
