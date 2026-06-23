# Browser Server Deployment Bundle

整理日期：2026-06-23

这个目录是给开发同事在新服务器上部署浏览器相关能力的最终交付包。部署时从这里开始：

```text
NEW_SERVER_DEPLOYMENT_GUIDE.md
```

??????????? GitHub?????????? `git clone` ? `git pull` ???????????? `NEW_SERVER_DEPLOYMENT_GUIDE.md`???????

## 目录说明

```text
NEW_SERVER_DEPLOYMENT_GUIDE.md
server-deploy-resources/
server-deploy-resources.tar.gz
manifest.json
legacy-review-notes/
```

- `NEW_SERVER_DEPLOYMENT_GUIDE.md`：新服务器逐步部署说明，按这个文件操作。
- `server-deploy-resources/`：从当前可用服务器导出的实际部署资源。
- `server-deploy-resources.tar.gz`：同一套资源的压缩包，方便传到服务器。
- `manifest.json`：机器可读清单。
- `legacy-review-notes/`：上周 review 过程中的历史说明和 git 状态，仅供追溯，不作为部署入口。

## 部署资源内容

`server-deploy-resources/` 里包含：

```text
opt-data/.local/bin/hq-browser
opt-data/.config/hq-browser/cdp-url.example
opt-data/skills/browser-control-policy
opt-data/skills/xiaohongshu/xhs-hq-browser-publisher
opt-data/skills/xiaohongshu/xhs-hq-browser-video-publisher
hermes/plugins/camofox-extra
hermes/config/hermes-config-required-snippets.yaml
```

这些资源对应的目标位置：

```text
hermes-agent:/opt/data/.local/bin/hq-browser
hermes-agent:/opt/data/.config/hq-browser/cdp-url
hermes-agent:/opt/data/skills/browser-control-policy
hermes-agent:/opt/data/skills/xiaohongshu/xhs-hq-browser-publisher
hermes-agent:/opt/data/skills/xiaohongshu/xhs-hq-browser-video-publisher
/home/ubuntu/.hermes/plugins/camofox-extra
/home/ubuntu/.hermes/config.yaml
```

如果要部署到 `coder`、`pm`、`cao` 等 profile，需要按部署指南把对应资源复制到各自的 `hermes-agent-*` 容器。

## 不再使用的旧包

旧的直接安装包已经删除，不再作为部署入口：

```text
hq-browser-server-direct-install.tar.gz
hq-browser-server-direct-install.zip
hq-browser-server-direct-install-fixed.zip
hq-agent-skills-browser-policy.tar.gz
camofox-extra-deploy-package
camofox-extra-deploy-package.zip
```

新服务器部署统一使用：

```text
server-deploy-resources/
server-deploy-resources.tar.gz
NEW_SERVER_DEPLOYMENT_GUIDE.md
```

## CamoFox Extra Tools

`server-deploy-resources/hermes/plugins/camofox-extra` 包含 10 个工具：

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

`camofox_screenshot` 用于保存当前 CamoFox tab 的原始截图并返回 `screenshot_path`。如果任务是分析画面内容，仍应优先使用 `browser_vision`。

## 敏感信息

真实 relay token 没有写入本交付包。配置里的敏感值已替换为占位符：

```text
REPLACE_WITH_TARGET_ENV_TOKEN
REPLACE_WITH_TARGET_CHROME_CLIENT_TOKEN
REPLACE_WITH_TARGET_CHROME_BRIDGE_TOKEN
REPLACE_WITH_TARGET_FILESYSTEM_CLIENT_TOKEN
REPLACE_WITH_TARGET_FILESYSTEM_BRIDGE_TOKEN
```

部署到新服务器时，需要由目标环境提供自己的 token。

## 验证入口

部署完成后，按 `NEW_SERVER_DEPLOYMENT_GUIDE.md` 的验证步骤检查：

```text
hq-browser smoke test
camofox_health
camofox_links
camofox_screenshot
```
