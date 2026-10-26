# ABNK Website — Release Notes

**版本**：`0.1.1`
**日期**：2026-10-26
**状态**：✅ 已完成（2026-10-26）
**分支**：`main`

## 基线信息

| 仓库 | 上版本 | 上版本基线 | 本次基线（HEAD） | 新提交数 |
|------|--------|-----------|-----------------|---------|
| `abnk-system` | `0.1.0` | `a4a7ce1` | `0e2b616` | 1 commit |

## 变更内容

### 品牌形象：ASDM 官方 logo 与 favicon 接入

**背景**：站点此前使用 lucide `Landmark` 通用图标 + Vite 默认 favicon（`vite.svg`）作为占位，需接入 ASDM 官方品牌形象。

**改动点**：
- `channels/website/public/images/logo/` — 新增 ASDM logo 三配色变体（`asdm-icon-transparent.svg` / `asdm-icon-black.svg` / `asdm-icon-white.svg`，存放方式对齐 asdm-ai-2026 站点）
- `channels/website/public/favicon.svg` — ASDM favicon（替换 vite.svg 占位）
- `channels/website/index.html` — favicon 引用 `/vite.svg` → `/favicon.svg`
- `channels/website/src/components/Nav.tsx` — Logo 组件图形替换：lucide Landmark → ASDM 旋转矩形叠层图形（`AsdmMark` 内联 SVG，继承 amber 主题色；Nav 与 Closing 两处自动生效）
- `channels/website/package.json` — `0.1.0` → `0.1.1`（镜像 tag）

**影响文件**：7 files changed, 26 insertions(+), 4 deletions(-)

## 部署命令（Phase B 在服务器执行）

```bash
cd ~/source/abnk-system && git pull origin main
docker build -f channels/website/Dockerfile -t abnk-website:0.1.1 channels/website
ABNK_WEBSITE_IMAGE=abnk-website:0.1.1 docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml down
ABNK_WEBSITE_IMAGE=abnk-website:0.1.1 docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d
```

## 执行进度跟踪

- [x] ✅ Step 0：敏感信息审计（5 节全过）
- [x] ✅ Step 1：仓库干净已推送（HEAD: `0e2b616`）
- [x] ✅ Step 2：版本确定（`0.1.1`，patch 自动递增；本地 build + typecheck 通过）
- [x] ✅ Step 3：服务器就绪（SSH ✅ / Docker 29.9.2 / 磁盘 120G / 80·443 由 abnk-website 监听 / 证书 notAfter 2027-05-12 / 当前生产 200）
- [x] ✅ Step 5：服务器 git pull + HEAD 核对（== `0e2b616`）
- [x] ✅ Step 6：docker build（abnk-website:0.1.1）
- [x] ✅ Step 7：compose 切换（down → up，容器 Up (healthy)）
- [x] ✅ Step 8：部署验证（HTTPS 200 / www 200 / HTTP 301 / favicon.svg 200 且为 ASDM 图形 / logo 三变体 200 / html icon 引用已切换）
- [x] ✅ Step 9：Release Note 回填 + commit

## 回滚

`ABNK_WEBSITE_IMAGE=abnk-website:0.1.0` compose up --force-recreate（镜像仍在服务器本地缓存）。
