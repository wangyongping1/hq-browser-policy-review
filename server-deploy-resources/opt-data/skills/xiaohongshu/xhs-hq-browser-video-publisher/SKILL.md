---
name: xhs-hq-browser-video-publisher
description: Prepare or publish Xiaohongshu / RED / 小红书 video notes through hq-browser controlling the host Chrome browser via relay/bridge. Use when the user wants a video post workflow with videos stored inside Hermes at /opt/data/workspace/videos or /opt/data/workspace/video, including opening Creator Center, selecting video upload, injecting MP4/MOV/WebM files, waiting for processing, filling title/body/tags, previewing, diagnosing upload issues, or stopping before final publish. Always use hq-browser and the bundled JavaScript DataTransfer upload script; do not use Camofox, Lightpanda, the default browser tool, or generic hq-browser upload for normal video publishing.
---

# XHS hq-browser Video Publisher

## Browser Surface

Follow `browser-control-policy` before acting. This is a host-browser-only workflow: use `hq-browser` through the user's relay/bridge-connected Chrome, not cloud browser tools.

## Rules

Use only `hq-browser` to control host Chrome. If `hq-browser` is not on PATH inside Hermes, use `/opt/data/.local/bin/hq-browser`.

Start with `hq-browser reset` before opening or inspecting Xiaohongshu, then use `hq-browser get url` and `hq-browser --json snapshot` to confirm the current page.

Do not use `hq-browser upload` for Xiaohongshu video upload. Use `scripts/xhs-js-upload-video.sh`, which injects the file through `File`, `DataTransfer`, and `change` events.

Do not bypass login, CAPTCHA, phone verification, account safety checks, or risk-control prompts. If these appear, stop and ask the user to handle them manually in host Chrome.

Do not click the final publish button unless the user explicitly asks to publish. For tests and drafts, stop after upload and field filling.

## Quick Workflow

1. Preflight:

   ```bash
   .agents/skills/xhs-hq-browser-video-publisher/scripts/xhs-video-preflight.sh
   ```

2. Open Creator Center:

   ```bash
   hq-browser open https://creator.xiaohongshu.com/publish/publish
   hq-browser get url
   hq-browser --json snapshot
   ```

3. If login page appears, stop and ask the user to log in through host Chrome.

4. Select video upload mode. On the current Creator Center page, the snapshot usually shows `上传视频` as `@e4`, but refs are session-local. Always click the current ref from snapshot.

   ```bash
   hq-browser click @e4
   hq-browser wait 1500
   hq-browser --json snapshot
   ```

5. Upload video:

   ```bash
   .agents/skills/xhs-hq-browser-video-publisher/scripts/xhs-js-upload-video.sh /opt/data/workspace/videos/test1.mp4
   ```

6. Wait for processing. Poll until title/body fields and the publish button appear:

   ```bash
   hq-browser wait 5000
   hq-browser --json snapshot
   ```

7. Fill title/body using current refs from snapshot. Typical refs vary, but title is the textbox with placeholder similar to `填写标题会有更多赞哦`.

8. Report selected video, title, body, current URL, and publish readiness. Stop before publish unless confirmed.

## Video Selection

List videos:

```bash
.agents/skills/xhs-hq-browser-video-publisher/scripts/list-xhs-videos.sh
```

If the user does not specify a file, choose the newest supported file from:

- `/opt/data/workspace/videos`
- `/opt/data/workspace/video`

Supported extensions: `.mp4`, `.mov`, `.m4v`, `.webm`.

## Fill Pattern

After upload and processing:

```bash
hq-browser --json snapshot
hq-browser fill @<title-ref> "video title"
hq-browser fill @<body-ref> "video body #tag"
hq-browser --json snapshot
```

Use refs from the current snapshot only. Do not reuse old refs after navigation, upload, reset, or tab changes.

## Recovery

- If CDP calls time out after upload, wait once and retry `snapshot`. If it still fails, stop and report possible risk control or page instability.
- If the page is stuck on upload mode after JS upload, inspect the returned JSON from `xhs-js-upload-video.sh`; verify `success:true`, file size, MIME type, and input `accept`.
- If the host browser does not visibly change, run `hq-browser reset` once and reopen the Creator Center.
- If the uploaded video is large, wait longer; video processing can take minutes.

## References

Read `references/video-flow.md` for detailed notes and troubleshooting.
