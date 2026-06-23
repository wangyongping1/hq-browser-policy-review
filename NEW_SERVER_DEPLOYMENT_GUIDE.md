# 新服务器部署指南

这份文档给开发同事使用，用来在一台新服务器上部署当前这套浏览器相关能力。

部署时不要使用旧安装包。当前唯一推荐入口是：

```text
server-deploy-resources/
server-deploy-resources.tar.gz
```

旧安装包已经从 bundle 中删除，例如：

```text
hq-browser-server-direct-install.tar.gz
hq-browser-server-direct-install.zip
hq-browser-server-direct-install-fixed.zip
hq-agent-skills-browser-policy.tar.gz
camofox-extra-deploy-package.zip
```

这些名字只在文档中作为“不要再找、不要再用”的历史说明出现。真正部署资源来自当前可用服务器 `192.168.1.100` 的实际导出。

## 0. 部署内容

这次部署分成两条能力线。

第一条是 host-browser 能力，用来让 agent 通过 `hq-browser` 控制用户本机 Chrome：

```text
hq-browser wrapper
browser-control-policy skill
xhs-hq-browser-publisher skill
xhs-hq-browser-video-publisher skill
```

第二条是 CamoFox 补充工具能力：

```text
camofox-extra Hermes plugin
```

其中 `camofox-extra` 当前包含 10 个工具：

```text
camofox_health
camofox_tabs
camofox_links
camofox_images
camofox_downloads
camofox_stats
camofox_screenshot
camofox_viewport
camofox_macro_search
camofox_extract
```

## 1. 从 GitHub 仓库拉取部署目录

在新服务器上先 clone 或 pull 你的 GitHub 仓库。示例：

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd <YOUR_REPO_DIR>/hq-browser-policy-review-20260618T085904Z
```

如果仓库已经存在：

```bash
cd <YOUR_REPO_DIR>
git pull
cd hq-browser-policy-review-20260618T085904Z
```

进入目录后，确认能看到：

```bash
ls -la
```

至少应包含：

```text
NEW_SERVER_DEPLOYMENT_GUIDE.md
server-deploy-resources/
server-deploy-resources.tar.gz
manifest.json
```

后续命令默认在 `hq-browser-policy-review-20260618T085904Z` 目录下执行。

如果你只拿到了压缩包，可以这样解压：

```bash
mkdir -p /tmp/hq-browser-deploy
tar -xzf server-deploy-resources.tar.gz -C /tmp/hq-browser-deploy
cd /tmp/hq-browser-deploy/server-deploy-resources
```

如果直接使用仓库里的文件夹：

```bash
cd server-deploy-resources
```

下面第 2 至第 5 步默认当前目录是 `server-deploy-resources`。

## 2. 安装 hq-browser 到 Hermes Agent 容器

默认 profile 的容器名是：

```text
hermes-agent
```

执行：

```bash
docker exec hermes-agent sh -lc 'mkdir -p /opt/data/.local/bin /opt/data/.config/hq-browser'
docker cp opt-data/.local/bin/hq-browser hermes-agent:/opt/data/.local/bin/hq-browser
docker exec hermes-agent sh -lc 'chmod 755 /opt/data/.local/bin/hq-browser'
```

然后在容器里创建 CDP URL 配置文件：

```bash
docker exec hermes-agent sh -lc 'cat > /opt/data/.config/hq-browser/cdp-url <<EOF
ws://chrome-use-relay:8787/cdp?token=REPLACE_WITH_TARGET_CHROME_CLIENT_TOKEN
EOF
chmod 600 /opt/data/.config/hq-browser/cdp-url'
```

把 `REPLACE_WITH_TARGET_CHROME_CLIENT_TOKEN` 替换为新服务器 / 当前 profile 对应的 `relay.chrome.client_token`。

如果新服务器还要测试 `coder`、`pm`、`cao` 等 profile，需要分别对这些容器重复安装，并使用对应 profile 的 relay 地址和 token：

```text
hermes-agent-coder -> ws://chrome-use-relay-coder:8787/cdp?token=...
hermes-agent-pm    -> ws://chrome-use-relay-pm:8787/cdp?token=...
hermes-agent-cao   -> ws://chrome-use-relay-cao:8787/cdp?token=...
```

只配置实际要测试的 profile。

## 3. 安装三个 Skill 到 Hermes Agent 容器

默认 profile：

```bash
docker exec hermes-agent sh -lc 'mkdir -p /opt/data/skills/xiaohongshu'

docker cp opt-data/skills/browser-control-policy \
  hermes-agent:/opt/data/skills/browser-control-policy

docker cp opt-data/skills/xiaohongshu/xhs-hq-browser-publisher \
  hermes-agent:/opt/data/skills/xiaohongshu/xhs-hq-browser-publisher

docker cp opt-data/skills/xiaohongshu/xhs-hq-browser-video-publisher \
  hermes-agent:/opt/data/skills/xiaohongshu/xhs-hq-browser-video-publisher

docker exec hermes-agent sh -lc 'chmod +x /opt/data/skills/xiaohongshu/xhs-hq-browser-publisher/scripts/*.sh /opt/data/skills/xiaohongshu/xhs-hq-browser-video-publisher/scripts/*.sh || true'
```

如果其他 profile 也要使用这些 skill，需要对对应 `hermes-agent-*` 容器重复复制。

## 4. 安装 camofox-extra 插件到宿主机

`camofox-extra` 是 Hermes 插件，放在宿主机的 Hermes 目录，不是 `/opt/data` 容器目录。

执行：

```bash
mkdir -p /home/ubuntu/.hermes/plugins
rm -rf /home/ubuntu/.hermes/plugins/camofox-extra
cp -a hermes/plugins/camofox-extra /home/ubuntu/.hermes/plugins/camofox-extra
```

安装后应存在：

```text
/home/ubuntu/.hermes/plugins/camofox-extra/plugin.yaml
/home/ubuntu/.hermes/plugins/camofox-extra/__init__.py
/home/ubuntu/.hermes/plugins/camofox-extra/schemas.py
/home/ubuntu/.hermes/plugins/camofox-extra/tools.py
```

## 5. 合并 Hermes 配置

编辑宿主机配置：

```text
/home/ubuntu/.hermes/config.yaml
```

参考文件：

```text
server-deploy-resources/hermes/config/hermes-config-required-snippets.yaml
```

注意：不要直接用参考文件覆盖完整 `config.yaml`，而是把需要的段落合并进去。

必须启用插件：

```yaml
plugins:
  enabled:
    - camofox-extra
```

如果新服务器默认浏览器能力要走 CamoFox，确认有类似配置：

```yaml
browser:
  cloud_provider: camofox
  use_gateway: false
  camofox:
    managed_persistence: true
    user_id: test
    session_key: test
    adopt_existing_tab: false
    rewrite_loopback_urls: true
    loopback_host_alias: host.docker.internal
```

relay 配置需要使用新服务器自己的 token：

```yaml
relay:
  chrome:
    bridge_relay_url: ws://TARGET_SERVER_IP:8787/relay
    bridge_token: REPLACE_WITH_TARGET_CHROME_BRIDGE_TOKEN
    client_relay_url: ws://chrome-use:8787/cdp
    client_token: REPLACE_WITH_TARGET_CHROME_CLIENT_TOKEN
  filesystem:
    bridge_relay_url: ws://TARGET_SERVER_IP:8788/relay
    bridge_token: REPLACE_WITH_TARGET_FILESYSTEM_BRIDGE_TOKEN
    client_mcp_url: http://filesystem-use:8788/mcp
    client_token: REPLACE_WITH_TARGET_FILESYSTEM_CLIENT_TOKEN
```

不要复用 `192.168.1.100` 上的 token，除非目标环境明确就是共享同一套 relay secrets。

## 6. 检查依赖服务是否存在

测试前确认新服务器有这些容器或服务：

```bash
docker ps --format '{{.Names}} {{.Status}}' | grep -E 'hermes-agent|chrome-use-relay|filesystem-use-relay|camofox-browser'
```

默认 profile 期望看到：

```text
hermes-agent
chrome-use-relay
filesystem-use-relay
camofox-browser
```

如果要测试其他 profile，还应看到对应容器，例如：

```text
hermes-agent-coder
chrome-use-relay-coder
filesystem-use-relay-coder
```

## 7. 重启容器

默认 profile：

```bash
docker restart hermes-agent
```

如果配置了其他 profile：

```bash
docker restart hermes-agent-coder
docker restart hermes-agent-pm
docker restart hermes-agent-cao
```

## 8. 验证 hq-browser

在默认 Hermes 容器里执行：

```bash
docker exec hermes-agent sh -lc '/opt/data/.local/bin/hq-browser reset'
docker exec hermes-agent sh -lc '/opt/data/.local/bin/hq-browser open https://example.com/?skill-policy-smoke=1'
docker exec hermes-agent sh -lc '/opt/data/.local/bin/hq-browser get url'
docker exec hermes-agent sh -lc '/opt/data/.local/bin/hq-browser --json snapshot'
```

期望：

```text
URL 包含 https://example.com/?skill-policy-smoke=1
snapshot 里能看到 Example Domain
```

如果返回 `409 Conflict`，不要切到 Lightpanda。先检查 `chrome-use-relay` 是否有 bridge session，以及本机 bridge 是否连上。

## 9. 验证 camofox-extra 插件

先检查文件：

```bash
test -f /home/ubuntu/.hermes/plugins/camofox-extra/plugin.yaml
test -f /home/ubuntu/.hermes/plugins/camofox-extra/tools.py
```

再做语法检查：

```bash
python3 - <<'PY'
import ast, pathlib
for p in [
    '/home/ubuntu/.hermes/plugins/camofox-extra/__init__.py',
    '/home/ubuntu/.hermes/plugins/camofox-extra/schemas.py',
    '/home/ubuntu/.hermes/plugins/camofox-extra/tools.py',
]:
    ast.parse(pathlib.Path(p).read_text(), filename=p)
    print('ok', p)
PY
```

然后在 agent 对话里测试：

```text
调用 camofox_health
```

再测试页面链接提取：

```text
打开云端浏览器访问 https://example.com，然后调用 camofox_links 提取链接。
```

测试截图 artifact：

```text
调用 camofox_screenshot，保存当前 CamoFox tab 的原始截图，并返回 screenshot_path。
```

## 10. 工具边界

host-browser 任务必须走 `hq-browser` 和 host-browser policy skill，不要把这类任务切到 CamoFox。

普通云端 / CamoFox 页面导航和交互，仍优先使用原生 browser 工具：

```text
browser_navigate
browser_snapshot
browser_click
browser_type
browser_scroll
browser_back
browser_press
browser_vision
```

`camofox-extra` 用于 CamoFox 诊断和页面元数据：

```text
camofox_health
camofox_tabs
camofox_links
camofox_images
camofox_downloads
camofox_stats
camofox_screenshot
camofox_viewport
camofox_macro_search
camofox_extract
```

`camofox_screenshot` 只保存原始截图文件。如果任务是让 agent 看图分析页面内容，优先使用 `browser_vision`。

## 11. 最终落点清单

宿主机：

```text
/home/ubuntu/.hermes/plugins/camofox-extra/
/home/ubuntu/.hermes/config.yaml
```

`hermes-agent` 容器内：

```text
/opt/data/.local/bin/hq-browser
/opt/data/.config/hq-browser/cdp-url
/opt/data/skills/browser-control-policy/
/opt/data/skills/xiaohongshu/xhs-hq-browser-publisher/
/opt/data/skills/xiaohongshu/xhs-hq-browser-video-publisher/
```

如果其他 profile 也需要这套能力，对应的 `hermes-agent-*` 容器也需要复制同样的 `/opt/data/.local/bin/hq-browser`、`/opt/data/.config/hq-browser/cdp-url` 和 `/opt/data/skills/...`。
