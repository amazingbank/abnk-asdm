# ABNK Website — Release Notes

**版本**：`0.1.2`（镜像 tag，= channels/website/package.json version）
**日期**：2026-10-27
**状态**：✅ 已完成（2026-10-27 部署验证通过）
**分支**：`main`

## 基线信息

| 仓库 | 上版本 | 上版本基线 | 本次基线（HEAD） | 新提交数 |
|------|--------|-----------|-----------------|---------|
| `abnk-system` | `0.1.1` | `0e2b616` | `e1751aa` | 3 commits（`f86e071` + `812ec19` + `e1751aa`） |

## 变更内容

### 多语言：中英双语 i18n（自研方案，参照 asdm-ai-2026）

**背景**：官网此前仅中文、文案硬编码于组件（bolt-new-prompt.md 明确"不用 i18n 框架"）。本次引入中英双语，架构参照 asdm-ai-2026 并适配单页锚点站。

**改动点**：
- `channels/website/src/i18n/` — 新增自研 i18n（11 个文件）：URL 前缀 `/zh-cn/`、`/en-us/` 为语言唯一事实源；`common`/`home` 两命名空间 JSON 语言包（中英各 2 份）；`tsc satisfies` 编译期校验两语言键结构一致；浏览器语言检测重定向无前缀 URL；`{param}` 插值；`popstate` 重同步；`localStorage["abnk-locale"]` 只写记录
- **与 asdm 的两处机制偏离**（设计文档记录）：语言包静态打包（免懒加载/缓存/白屏事故类别）；切换不 remount（保留滚动位置与动画状态）
- `channels/website/src/main.tsx` — 挂载前前缀校验 + 重定向 + `LocaleProvider` 接入
- `channels/website/index.html` — title/description 注明运行时按语言动态更新
- `channels/website/tsconfig.app.json` — `resolveJsonModule`
- 全部 8 个 section 组件 + Nav/Footer/Logo 文案改由语言包驱动；新增 `LanguageToggle` 语言切换按钮（头部，桌面/移动可见）
- SEO：`<html lang>`、`<title>`、`meta description` 随语言动态切换

### 字体：asdm-ai-2026 同源方案（自托管）

- `@fontsource-variable/oxanium` / `jetbrains-mono` / `noto-sans-sc` / `noto-serif-sc` 四包自托管，Vite 打包进 `/assets`（unicode-range 分片按需加载）
- `tailwind.config.js` — sans = Oxanium + Noto Sans SC、mono = JetBrains Mono + Noto Sans SC（与 asdm-ai-2026 完全一致）；serif = Noto Serif SC 保留衬线大标题（**方案 A，2026-10-27 经 `design/font-comparison.html` 三方案可视化评审定案**）
- `index.html` — 移除 Google Fonts CDN（preconnect + link）
- `src/index.css` — 移除 Inter 专属 `font-feature-settings`

### 发版缓存策略（nginx.conf，对齐 asdm-ai-2026 deploy/nginx）

- `/assets/` — 单头 `Cache-Control: public, max-age=31536000, immutable`（修复原 `expires` + `add_header` 双重头）
- `location = /index.html` — `no-store`（杜绝启发式缓存导致发版后旧 HTML 按旧哈希名拉已删 assets——旧内容/白屏）；根路径与 `/zh-cn/`、`/en-us/` 经内部重定向同样命中
- `/favicon.svg` — `no-cache`（保留 304 协商）
- 各 location 显式补齐 HSTS 等安全头（location 含 `add_header` 不继承 server 级）
- 校验：`nginx:1.27-alpine` 官方镜像 `nginx -t` 通过

### 文案与视觉微调

- 英文导航单词化：Identity / Global / ASDM / Open / Beliefs
- 英文页 `note` 装饰标签全英文（First Landing / Insight / Traceable / Trust 等主题关键词）
- Logo 去外框、整体放大（图形 20px→36px、ABNK 17px）
- 头部「了解 ASDM」链接高度统一 h-10（40px），与语言切换/菜单按钮一致（`e1751aa`，评审反馈修复）

### 评审与文档

- `channels/website/design/font-comparison.html` — 字体三方案可视化对比页（存档）
- `.asdm/workspace/docs/planning/abnk-design/02-architecture/website-i18n-fonts.md` — 设计文档（abnk-asdm 仓库 `1561fae`）

**影响文件**：30 files changed, 1419 insertions(+), 222 deletions(-)（+版本 bump 1 file）

**发版前验证**：`tsc` 0 错误（含两语言包结构校验）；`eslint` 0 error（仅 Reveal.tsx 既有 1 warning）；`vite build` 通过；浏览器实测（dev + preview）中英切换、URL 前缀、html lang/title/meta、三种字体族生效、英文页全文无 CJK。

## 部署命令（Phase B 在服务器执行）

```bash
# Step 5: pull + HEAD 核对（必须等于 e1751aa）
cd ~/source/abnk-system && git pull origin main && git log --oneline -1

# Step 6: 构建
docker build -f channels/website/Dockerfile -t abnk-website:0.1.2 channels/website

# Step 7: compose 切换
ABNK_WEBSITE_IMAGE=abnk-website:0.1.2 docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml down
ABNK_WEBSITE_IMAGE=abnk-website:0.1.2 docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d

# Step 8: 验证
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml ps
curl -s -o /dev/null -w "%{http_code}" https://amazingbank.ai/          # 200
curl -s -o /dev/null -w "%{http_code}" https://www.amazingbank.ai/     # 200
curl -s -o /dev/null -w "%{http_code}" http://amazingbank.ai/          # 301
docker logs abnk-website --tail=20
```

回滚（如需）：`ABNK_WEBSITE_IMAGE=abnk-website:0.1.1 docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d --force-recreate`

## 执行进度跟踪

- [x] ✅ Step 0：敏感信息审计（5 节全过）
- [x] ✅ Step 1：仓库干净已推送（HEAD: `e1751aa`；abnk-asdm `1561fae`）
- [x] ✅ Step 2：版本确定（`0.1.2`，服务器现运行 `0.1.1`——不与运行中 tag 重复）
- [x] ✅ Step 3：服务器就绪（SSH/Docker/磁盘/端口/证书/DNS/仓库）
- [x] ✅ Step 5：服务器 git pull + HEAD 核对（`e1751aa` 与本地一致）
- [x] ✅ Step 6：docker build（abnk-website:0.1.2，96MB）
- [x] ✅ Step 7：compose 切换（down → up，--env-file）
- [x] ✅ Step 8：部署验证（详见下节验证结果）
- [x] ✅ Step 9：Release Note 回填 + commit

## 环境就绪检查

| 检查项 | 状态 |
|--------|------|
| 敏感信息审计 | ✅ 5 节全过 |
| SSH / Docker | ✅ Docker 29.9.2 / Compose v5.6.1 |
| 磁盘 / 内存 | ✅ 120G 可用 / 7.1Gi 可用 |
| 端口 80/443 | ✅ 由现运行 abnk-website(0.1.1) 占用——compose 切换即接管 |
| 部署根 + .env | ✅ `~/deploy/.env`（ABNK_DEPLOY_ROOT） |
| TLS 证书（有效期/modulus） | ✅ notAfter=2027-05-12（>30 天）；SAN *.amazingbank.ai + amazingbank.ai；modulus MD5 一致 |
| DNS（amazingbank.ai / www） | ✅ 均指向生产 IP |
| 服务器仓库 | ✅ main @ 0e2b616（待 pull 至 e1751aa） |

## 部署验证结果（Step 8，2026-10-27）

| 验证项 | 结果 |
|--------|------|
| 容器状态 | ✅ `abnk-website` Up (healthy)，运行镜像 `abnk-website:0.1.2` |
| `https://amazingbank.ai/` | ✅ 200 |
| `https://www.amazingbank.ai/` | ✅ 200 |
| `http://amazingbank.ai/` | ✅ 301 → https |
| 语言前缀 `/zh-cn/`、`/en-us/` | ✅ 均为 200（生产环境语言路由生效） |
| TLS 证书 | ✅ subject `CN=*.amazingbank.ai`，verify ok，expire 2027-05-12 |
| 页面 title | ✅ 官网首页 title（非 nginx 默认页） |
| HTML 缓存头（`/`、`/zh-cn/`） | ✅ `cache-control: no-store`（发版后任何刷新立即拿新 HTML） |
| assets 缓存头 | ✅ `cache-control: public, max-age=31536000, immutable` |
| 容器日志 | ✅ 无 ERROR（仅 healthcheck Wget 200 记录） |
