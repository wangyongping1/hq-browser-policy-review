# Xiaohongshu Video Flow With hq-browser

## Why This Skill Uses JS Upload

Older working Xiaohongshu upload flows avoided generic `agent-browser upload`
because it could crash or destabilize the target. This skill uses JavaScript
DataTransfer injection instead:

```text
base64 -> Blob -> File -> DataTransfer -> input.files -> input/change events
```

This keeps the workflow inside `hq-browser` while avoiding the generic upload
path.

## Flow

1. Run preflight:

   ```bash
   .agents/skills/xhs-hq-browser-video-publisher/scripts/xhs-video-preflight.sh
   ```

2. Open Creator Center:

   ```bash
   hq-browser open https://creator.xiaohongshu.com/publish/publish
   hq-browser --json snapshot
   ```

3. If logged out or challenged, stop and ask the user to handle it manually.

4. Choose video upload mode. Use the current snapshot ref for `上传视频`, often `@e4`.

5. Upload:

   ```bash
   .agents/skills/xhs-hq-browser-video-publisher/scripts/xhs-js-upload-video.sh /opt/data/workspace/videos/test1.mp4
   ```

6. Wait and poll:

   ```bash
   hq-browser wait 5000
   hq-browser --json snapshot
   ```

7. When title/body fields appear, fill them with current refs.

8. Stop before final publish unless the user explicitly confirms.

## Real Test Notes

The video flow was verified with `hq-browser` and JS DataTransfer:

- Preflight found `/opt/data/workspace/videos/test1.mp4`.
- `xhs-js-upload-video.sh /opt/data/workspace/videos/test1.mp4` returned `success:true`.
- The page entered video edit mode and showed `test1.mp4`, video preview, title/body fields, and a publish button.
- Tested title field ref was `@e47` before filling; after snapshot refresh it became `@e48`.
- Tested body field ref was `@e33`.
- Tested publish button ref was `@e29`.
- Filled test title `test-video-title-do-not-publish`.
- Filled test body `hq-browser video upload test draft only do not publish testtag`.
- Final publish was not clicked.

The image flow was also verified to work with `hq-browser` and JS DataTransfer:

- `@e6` switched to image-text upload.
- JS upload returned `success:true`.
- The page entered edit mode and showed title/body fields and publish button.

For video, use the same JS upload strategy and allow longer processing time.
