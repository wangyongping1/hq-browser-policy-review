---
name: xhs-hq-browser-publisher
description: Publish or prepare Xiaohongshu / RED / 小红书 image-text notes and video notes through hq-browser controlling the host Chrome browser via relay/bridge. Use when the user wants Codex or an agent to operate Xiaohongshu Creator Center with host-browser login state, upload media from Hermes container paths such as /opt/data/workspace/image, /opt/data/workspace/video, or /opt/data/workspace/videos, fill title/body/tags, inspect publish pages, or diagnose Xiaohongshu publishing through hq-browser. Always use hq-browser, not Camofox, not the default browser tool, and not raw agent-browser unless diagnosing hq-browser itself.
---

# XHS hq-browser Publisher

## Browser Surface

Follow `browser-control-policy` before acting. This is a host-browser-only workflow: use `hq-browser` through the user's relay/bridge-connected Chrome, not cloud browser tools.

## Contract

Use only `hq-browser` to control the host Chrome browser. Do not use the default browser tool, Camofox, Lightpanda, or raw `agent-browser` for normal publishing.

Prefer `hq-browser` when it is on PATH. If not found inside Hermes, use `/opt/data/.local/bin/hq-browser`.

Start with `hq-browser reset` before opening or inspecting Xiaohongshu, then use `hq-browser get url` and `hq-browser --json snapshot` to confirm the current page.

Never bypass login, CAPTCHA, phone verification, or account checks. If Xiaohongshu shows a login or verification page, stop and ask the user to complete it in host Chrome, then continue with `hq-browser`.

Never bypass risk-control, anti-bot, account safety, or abnormal-environment checks. If the page shows verification, risk-control prompts, upload blocking, repeated timeouts after upload, or suspicious-environment messages, stop and report the state. Ask the user to resolve it manually in host Chrome or change the browser/network/account environment.

Do not click the final publish/submit button unless the user has explicitly asked to publish the prepared post. If the user asks to draft, prepare, test, preview, or fill, stop before final publish.

## Quick Flow

1. Preflight:

   ```bash
   .agents/skills/xhs-hq-browser-publisher/scripts/xhs-preflight.sh
   ```

2. Open Creator Center:

   ```bash
   hq-browser open https://creator.xiaohongshu.com/publish/publish
   hq-browser get url
   hq-browser --json snapshot
   ```

3. If redirected to login, ask the user to log in through the host Chrome window. Continue only after `hq-browser get url` no longer shows `/login`.

4. Choose note type:

   - Image-text note: upload one or more images from `/opt/data/workspace/image`.
   - Video note: upload one video from `/opt/data/workspace/video` or `/opt/data/workspace/videos`.

5. Upload media with JavaScript DataTransfer injection. Prefer the bundled script:

   ```bash
   .agents/skills/xhs-hq-browser-publisher/scripts/xhs-js-upload-file.sh /opt/data/workspace/image/test1.png
   ```

   Avoid `hq-browser upload` on Xiaohongshu unless the JS method is impossible; prior Xiaohongshu skills observed that the upload command can crash or destabilize the target.

   Fallback only if needed:

   ```bash
   hq-browser upload 'input[type=file]' /opt/data/workspace/image/test1.png
   ```

   If direct selector upload fails, use `snapshot` to find the upload control, click it, then retry the file input selector.

6. Fill title, body/caption, tags/topics, and any required fields using visible labels, placeholders, or refs from `snapshot`.

7. Verify:

   ```bash
   hq-browser --json snapshot
   hq-browser get url
   ```

8. Publish only when explicitly confirmed.

## Media Selection

List available media before uploading:

```bash
.agents/skills/xhs-hq-browser-publisher/scripts/list-xhs-media.sh
```

If the user does not specify a file:

- For image-text posts, choose the newest supported image from `/opt/data/workspace/image`.
- For video posts, choose the newest supported video from `/opt/data/workspace/video`; if absent, try `/opt/data/workspace/videos`.
- Tell the user which file was selected before upload.

Supported extensions:

- Images: `.jpg`, `.jpeg`, `.png`, `.webp`
- Video: `.mp4`, `.mov`, `.m4v`, `.webm`

## Command Patterns

Snapshot and inspect:

```bash
hq-browser get url
hq-browser --json snapshot
```

Click a snapshot ref:

```bash
hq-browser click @e12
```

Fill by placeholder, label, or selector:

```bash
hq-browser fill 'input[placeholder*="标题"]' '标题文本'
hq-browser fill 'textarea' '正文文本 #话题'
```

Upload:

```bash
.agents/skills/xhs-hq-browser-publisher/scripts/xhs-js-upload-file.sh /opt/data/workspace/image/test1.png
```

Keyboard fallback:

```bash
hq-browser click @e12
hq-browser keyboard type '正文文本'
hq-browser press Enter
```

## Publishing Safety

Before final publish, report:

- Current URL.
- Selected media file path.
- Title.
- Body/caption.
- Tags/topics.
- Whether the visible page appears ready to publish.

If the user has not explicitly confirmed publishing, stop with: "Draft is ready; waiting for publish confirmation."

When publishing is confirmed, click the visible publish button by text/ref, then verify success page/toast with `snapshot`.

## Troubleshooting

- If `hq-browser` is not found, run `/opt/data/.local/bin/hq-browser ...` or reinstall from `apps/chrome/scripts/install-hq-browser.sh`.
- If the host Chrome does not visibly change, run `hq-browser reset` once, reopen the Creator Center, and verify `http://127.0.0.1:9222/json/list` on the bridge host.
- If upload fails, confirm the file path exists inside Hermes, not only on the host.
- If `hq-browser upload` causes page instability, switch to `scripts/xhs-js-upload-file.sh`; this is the preferred Xiaohongshu upload path.
- If the page is logged out, do not continue automation until the user logs in manually.
- If Xiaohongshu triggers risk control, upload blocking, verification, or repeated CDP timeouts after upload, stop. Do not retry aggressively. Ask the user to manually clear the challenge in host Chrome, then continue only after the page is stable.
- If Xiaohongshu changes labels or layout, use `snapshot` refs and the reference flow in `references/publisher-flow.md`.

## References

Read `references/publisher-flow.md` when a publish task needs detailed step-by-step handling or troubleshooting.
