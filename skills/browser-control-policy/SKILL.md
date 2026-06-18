---
name: browser-control-policy
description: Route browser-control tasks to the correct browser surface and enforce safety boundaries. Use when an agent must decide between controlling the user's host Chrome through hq-browser over relay/bridge and using cloud or sandbox browser tools such as browser navigate/click/snapshot. Also use before host-browser workflows that depend on the user's local login state, Chrome 9222, Xiaohongshu/RED Creator Center, or hq-browser.
---

# Browser Control Policy

## Contract

Choose exactly one browser surface before acting.

Use `hq-browser` only for the user's host browser: the Chrome instance exposed through the relay/bridge chain, typically host Chrome remote debugging port 9222. Use this surface when the task depends on the user's local login state, local browser profile, local verification state, local files mounted into Hermes, or a site workflow that the user explicitly wants performed in their computer's browser.

Use the cloud or sandbox browser tools only for cloud browser work: public page inspection, screenshots, unauthenticated browsing, local dev-server visual checks, or any task where the user's host Chrome/login state is not required.

Do not mix surfaces in one workflow unless the user explicitly asks to compare them.

## Host Browser Rules

For user-computer browser control, use only `hq-browser`.

Start every host-browser workflow with:

```bash
hq-browser reset
hq-browser get url
hq-browser --json snapshot
```

If `hq-browser` is not on `PATH` inside Hermes, use:

```bash
/opt/data/.local/bin/hq-browser
```

Use current snapshot refs only. Re-read `hq-browser --json snapshot` after navigation, modal changes, upload changes, login changes, or any step that may replace DOM nodes.

Stop and report the current URL plus visible state if `hq-browser reset`, `open`, `get url`, or `snapshot` fails. Do not silently switch to another browser surface.

## Cloud Browser Rules

For cloud or sandbox browser work, use the available browser tools such as navigate, click, type, screenshot, and snapshot. Do not use `hq-browser` for these tasks.

Cloud browser work is appropriate when the task does not require the user's local login/session and does not need to alter the user's visible Chrome.

## Prohibited

When the task is host-browser work:

- Do not use the default browser tool, Browser plugin, Camofox, Lightpanda, Playwright, or raw `agent-browser`.
- Do not connect directly to `ws://lightpanda:9223`.
- Do not override `HUAQING_BROWSER_CDP_URL` unless the user explicitly gives a relay/bridge CDP URL for this task.
- Do not set custom lock roots such as `HUAQING_BROWSER_LOCK_ROOT=/tmp/hq-locks-hermes`; the wrapper already isolates locks by runtime user.
- Do not bypass login, CAPTCHA, phone verification, risk-control, account safety, or suspicious-environment checks.
- Do not continue in another browser after a host-browser verification or risk-control page appears.

When the task is cloud-browser work:

- Do not use `hq-browser`.
- Do not operate the user's host Chrome as a convenience fallback.

## Xiaohongshu Boundary

Xiaohongshu / RED publishing is host-browser work. Use `hq-browser` because publishing depends on the user's host Chrome session, risk environment, and manual verification state.

For image-text publishing, use `xhs-hq-browser-publisher`.

For video publishing, use `xhs-hq-browser-video-publisher`.

If Xiaohongshu requires login, CAPTCHA, phone verification, account safety checks, or risk-control handling, stop and ask the user to resolve it manually in host Chrome. Continue only after the user confirms the page is ready.
