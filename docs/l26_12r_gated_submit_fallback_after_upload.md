# L26.12R Gated Submit Fallback After Upload

L26.12Q proved that the upload precondition passed, but failed because Edge UIA did not expose a named ChatGPT Send/Submit button.

L26.12R keeps the accepted L26.12P upload primitive and adds a gated submit fallback:

1. upload the pre-send report snapshot using the picker-confirmed flow;
2. require `--allow-chatgpt-submit`;
3. send Escape once to close any leftover slash menu;
4. try a UIA Send/Submit button if exposed;
5. if no UIA button is exposed, click the lower-right composer/send area by Edge-window-relative coordinates;
6. record the submit method;
7. keep no DOM/WebDriver/Selenium and no prompt/conversation/file-content logging.

This patch intentionally accepts a coordinate fallback because the real Edge UIA tree did not expose a usable named Send control in L26.12Q.
