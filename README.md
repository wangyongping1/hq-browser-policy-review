# hq-browser policy review bundle

Created: 2026-06-18T08:59:04.986Z

## Contents

- packages/: install/archive artifacts I created or used for server installation.
- skills/browser-control-policy/: new browser routing and safety policy skill.
- skills/xhs-hq-browser-publisher/: Xiaohongshu image-text publishing skill with host-browser policy hook.
- skills/xhs-hq-browser-video-publisher/: Xiaohongshu video publishing skill with host-browser policy hook.
- manifest.json: machine-readable inventory.
- git-status.txt and git-diff-stat.txt: local repository state at bundle creation time.

## Server install locations

- /opt/data/skills/browser-control-policy
- /opt/data/skills/xiaohongshu/xhs-hq-browser-publisher
- /opt/data/skills/xiaohongshu/xhs-hq-browser-video-publisher

## Validation already performed

- Local skill validator passed for all three skills.
- Server hq-browser smoke test passed with URL: https://example.com/?skill-policy-smoke=1

## Notes

The policy skill separates host-browser work from cloud-browser work. Host-browser tasks must use hq-browser and must not fall back to default browser tools, Camofox, Lightpanda, raw agent-browser, or ws://lightpanda:9223. Xiaohongshu publishing remains in the two dedicated XHS skills and is marked host-browser-only.

## hq-browser Wrapper 说明

`hq-browser` 是一个放在 Hermes 容器里的轻量命令包装器，用来让服务器 agent 控制你本机的 Chrome，而不是误连到 Lightpanda、Camofox 或默认云端浏览器。

当前默认链路是：

```text
Hermes agent 容器
  -> /opt/data/.local/bin/hq-browser
  -> agent-browser --engine chrome --cdp <relay URL>
  -> chrome-use-relay 容器
  -> 你本机 bridge
  -> 你本机 Chrome remote debugging 9222
```

### 服务器安装位置

默认 profile 已安装到：

```text
hermes-agent:/opt/data/.local/bin/hq-browser
hermes-agent:/opt/data/.config/hq-browser/cdp-url
```

我之前也安装到了这些 Hermes 容器：

```text
hermes-agent
hermes-agent-coder
hermes-agent-pm
hermes-agent-cao
```

但目前只有默认链路 `hermes-agent -> chrome-use-relay` 有 bridge session，其他 profile 的 relay 当时是健康但 `sessions: 0`。

### 配置来源

`hq-browser` 读取 CDP URL 的顺序是：

1. `HUAQING_BROWSER_CDP_URL` 环境变量。
2. `/opt/data/.config/hq-browser/cdp-url`。
3. fallback 到 `ws://lightpanda:9223`。

正常使用时不应该让它走 fallback。安装脚本会把 relay URL 写入：

```text
/opt/data/.config/hq-browser/cdp-url
```

文件权限是 `600`，里面包含 relay token。

### 常用命令

每次 host-browser 工作流先执行：

```bash
hq-browser reset
hq-browser get url
hq-browser --json snapshot
```

如果 `hq-browser` 不在 PATH，使用完整路径：

```bash
/opt/data/.local/bin/hq-browser reset
/opt/data/.local/bin/hq-browser get url
/opt/data/.local/bin/hq-browser --json snapshot
```

打开页面：

```bash
hq-browser open 'https://example.com/?check=1'
hq-browser get url
hq-browser --json snapshot
```

### reset 的意义

`hq-browser reset` 做两件事：

1. 清理 `hq-browser` 的锁目录。
2. 执行 `agent-browser close --all`，清掉旧 default session。

这个步骤很重要，因为旧 session 可能让 agent 嘴上使用 `hq-browser`，底层却复用之前 Lightpanda 或其他 CDP 会话。

### 锁机制

`hq-browser` 会按 CDP URL 建锁，避免多个 agent-browser 客户端同时抢同一个 relay/bridge 单客户端会话。

默认锁目录类似：

```text
/tmp/hq-browser-locks-<uid>
```

不要再手动设置旧提示里的：

```bash
HUAQING_BROWSER_LOCK_ROOT=/tmp/hq-locks-hermes
```

新 wrapper 已经按运行用户隔离锁目录。

### 禁止事项

在用户电脑浏览器任务里，agent 必须只用 `hq-browser`。禁止：

- 直接调用 `agent-browser`。
- 使用 `ws://lightpanda:9223`。
- 使用默认 browser tool、Camofox、Lightpanda 或 Playwright 替代。
- 为了绕过错误切换到其他浏览器。
- 绕过登录、验证码、手机号验证、风控或安全检查。

### 当前验证结果

默认 profile 烟测通过：

```bash
/opt/data/.local/bin/hq-browser reset
/opt/data/.local/bin/hq-browser open https://example.com/?skill-policy-smoke=1
/opt/data/.local/bin/hq-browser get url
/opt/data/.local/bin/hq-browser --json snapshot
```

返回 URL：

```text
https://example.com/?skill-policy-smoke=1
```

snapshot 里能看到 `Example Domain`，说明默认链路已经实际到达你本机 Chrome 9222。

### 排障口径

检查 relay 是否有 bridge session：

```bash
docker exec hermes-agent sh -lc 'curl -fsS http://chrome-use-relay:8787/healthz || wget -qO- http://chrome-use-relay:8787/healthz'
```

期望默认 profile 返回类似：

```json
{"ok":true,"sessions":1}
```

如果是 `sessions: 0`，说明 relay 在，但没有 bridge 连上。

如果 `hq-browser get url` 返回 `409 Conflict`，通常表示 relay/bridge 会话不可用或被占用；不要切到 Lightpanda，先检查 bridge 和 relay session。

### 安装包说明

`packages/hq-browser-server-direct-install.zip` 是原始 zip 包。它可以用 `bash install-hq-browser-server.sh ...` 跑，但有三个不理想点：服务器没有 `unzip`、zip 不保留可执行权限、installer 文件头曾有 BOM 噪音。

`packages/hq-browser-server-direct-install.tar.gz` 是我整理出的推荐包：去掉 BOM，保留可执行权限，服务器可直接用 `tar -xzf` 解压。

`packages/hq-browser-server-direct-install-fixed.zip` 是修正版 zip，保留元数据给人工对照，但服务器部署更推荐 tar.gz。

`packages/hq-agent-skills-browser-policy.tar.gz` 是这次同步到服务器的三个 skill 打包件，不是 hq-browser wrapper 本体。
