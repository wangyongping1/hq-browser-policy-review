# Xiaohongshu hq-browser Publisher Flow

## Preflight

Run:

```bash
.agents/skills/xhs-hq-browser-publisher/scripts/xhs-preflight.sh
```

Confirm:

- `hermes` and `relay` are running.
- `hq-browser` exists inside Hermes.
- The CDP config is relay-backed, normally `ws://chrome-use:8787/cdp?token=<redacted>`.
- Media exists under `/opt/data/workspace/image`, `/opt/data/workspace/video`, or `/opt/data/workspace/videos`.

## Open Publish Page

```bash
hq-browser open https://creator.xiaohongshu.com/publish/publish
hq-browser get url
hq-browser --json snapshot
```

If URL contains `/login`, stop and ask the user to log in on host Chrome.

## Image-Text Note

1. Choose one or more images.
2. Open the publish page.
3. If there is a note type switch, choose image/text or upload images mode.
4. Upload with JS DataTransfer injection:

   ```bash
   .agents/skills/xhs-hq-browser-publisher/scripts/xhs-js-upload-file.sh /opt/data/workspace/image/test1.png
   ```

5. Wait for thumbnails/upload completion:

   ```bash
   hq-browser wait 2000
   hq-browser --json snapshot
   ```

6. Fill title and content using visible placeholders or refs.
7. Add tags/topics in the content body or tag controls as requested.
8. Stop before final publish unless confirmed.

## Video Note

1. Choose one video from `/opt/data/workspace/video` or `/opt/data/workspace/videos`.
2. Open the publish page.
3. Choose video upload mode if needed.
4. Upload with JS DataTransfer injection:

   ```bash
   .agents/skills/xhs-hq-browser-publisher/scripts/xhs-js-upload-file.sh /opt/data/workspace/videos/example.mp4
   ```

5. Video upload and processing can take longer. Poll snapshots and wait:

   ```bash
   hq-browser wait 5000
   hq-browser --json snapshot
   ```

6. Fill title, content, cover options, and required metadata if present.
7. Stop before final publish unless confirmed.

## Login Handling

Current observed unauthenticated Creator Center behavior:

- Opening `https://creator.xiaohongshu.com/publish/publish` redirects to
  `https://creator.xiaohongshu.com/login?...`.
- Snapshot shows phone number, verification code, login button, terms checkbox.

Do not automate SMS verification or CAPTCHA. Ask the user to log in manually.

## Risk-Control Handling

Observed during real testing:

- The account could open `https://creator.xiaohongshu.com/publish/publish`.
- Switching from video upload to image-text upload worked through `hq-browser click @e6`.
- Uploading `/opt/data/workspace/image/test1.png` returned `Done`, then the page became unstable and later CDP calls timed out with errors such as `DOM.enable` or `Runtime.evaluate`.
- The user identified this state as Xiaohongshu risk control.

Important follow-up from older working skills:

- Do not use the generic `agent-browser upload` / `hq-browser upload` path as the first choice on Xiaohongshu.
- Older successful image/video skills used `base64 -> Blob -> File -> DataTransfer -> input.files -> change event`.
- The bundled `scripts/xhs-js-upload-file.sh` implements that safer path while still using `hq-browser`.

When this happens:

1. Stop automation immediately.
2. Do not keep retrying upload or publish actions.
3. Report that the page likely entered Xiaohongshu risk control.
4. Ask the user to resolve any visible challenge manually in host Chrome.
5. Continue only after a fresh `hq-browser --json snapshot` succeeds and the user confirms the page is stable.

Do not attempt to bypass risk-control, CAPTCHA, SMS verification, or account
safety checks.

## Verification

Before final publish, collect:

```bash
hq-browser get url
hq-browser --json snapshot
```

Report selected media, title, body, tags, and current publish-page status.

After confirmed publish, verify the success state with `snapshot`. If a toast or
redirect is visible, report it.
