# ASDM Action: ABNK Production Deploy

## Metadata

```json
{
  "guid": "a8c3d4e5-f6a7-8901-2345-67890abcdef1",
  "name": "abnk-prod-deploy",
  "displayName": "ABNK Prod Deploy",
  "description": "- Audit sensitive info (Step 0 iron gate), check environment readiness, generate Release Note for review, then build Docker image (abnk-website——channels/website 官网前端) on the production server and deploy the abnk-prod compose stack (abnk-website nginx TLS 终止 :80/:443——https://amazingbank.ai)",
  "toolset": {
    "guid": "b7a2c9d1-4e3f-4a58-9c6b-1d2e3f4a5b6c",
    "id": "abnk-harness-toolset",
    "name": "ABNK Harness Toolset",
    "version": "0.1.1"
  },
  "scenario": "生产部署"
}
```

## Overview

This action deploys the Amazing Bank 官网渠道前端（`abnk-system/channels/website`——Vite React SPA）to the production server（`abnk-vm001`）via Docker compose stack `abnk-prod`（`deploy/prod/compose-abnk-prod.yaml`）——单容器 `abnk-website`（多阶段镜像：nginx 静态托管 + TLS 终止），用户入口 `https://amazingbank.ai`（80 → 301 → https）。

### 敏感信息安全模型（本 action 的首要铁律）

> **⚠️ Single Source of Truth for Production Info**: 所有生产环境信息（服务器 IP、SSH 用户、路径、证书位置、DNS、凭据）**只存放于 `.github-private/abnk-prod/config.json`**（`.github-private` = workspace 内唯一 private repo）。本文件与所有 public 仓库（`abnk-system` / `fineract` / `.asdm`）**禁止出现任何生产敏感信息**——命令示例中的字面量仅为可读性，执行时一律从 private config 解析。开发环境信息（本地调试凭据等）允许出现在 public 仓库。

**信息分级**：

| 级别 | 内容 | 存放位置 |
|------|------|---------|
| 🔴 生产敏感 | 服务器 IP / SSH / 生产凭据 / TLS 私钥 / 生产路径 | `.github-private/`（ssl 归档 `ssl/`，环境配置 `abnk-prod/config.json`） |
| 🟢 开发公开 | 本地调试凭据（postgres/postgres、mifos:password 等）、代码、compose 编排、Dockerfile | public 仓库（`abnk-system` / `.asdm`） |

**每次部署 Step 0 强制执行敏感信息审计**：`.github-private/abnk-prod/scripts/audit-sensitive-info.sh`（扫描 public 仓库的私钥块/生产 IP/凭据模式/密钥文件形态 + private repo 完整性核查）。审计失败 = 部署中止。

### Environment Info Lookup

执行任何步骤前，先读生产配置：

```bash
cat .github-private/abnk-prod/config.json | jq '.environments.production'
```

| 占位符 | private config 路径 |
|--------|--------------------|
| `$PROD_SSH` | `environments.production.server.sshCommand` |
| `$PROD_HOST` | `environments.production.server.host` |
| `$PROD_REPO_SERVER` | `environments.production.server.serverRepoPath.server` |
| `$PROD_REPO_LOCAL` | `environments.production.server.serverRepoPath.local` |
| `$PROD_BRANCH` | `environments.production.server.branches.abnkSystem` |
| `$PROD_COMPOSE_FILE` | `environments.production.server.dockerComposeFile`（相对仓库根） |
| `$PROD_DEPLOY_ROOT` | `environments.production.deploy.deployRoot` |
| `$PROD_ENV_FILE` | `environments.production.deploy.envFile` |
| `$SSL_DIR` | `environments.production.deploy.ssl.serverDir` |
| `$SSL_ARCHIVE` | `environments.production.deploy.ssl.localArchive`（本地归档——服务器证书丢失时 scp 恢复） |
| `$GIT_REPO` | `environments.production.server.githubRepoUrl` |

### Iron Rules

1. **敏感信息铁律** — 生产环境信息只在 `.github-private`（见安全模型节）。Step 0 审计是每次部署的强制门禁；审计失败 = 中止。发现泄漏的处置：从 public 仓库清除 → 移入 `.github-private` → commit → 必要时轮换凭据/证书。
2. **所有代码改动在本地，所有制品在服务端构建** — 本地 Mac 只做 edit/commit/push；服务器 `git pull` + `docker build` + compose 切换。禁止本地构建镜像推送（Mac ARM64 vs 服务器 x86_64）。
3. **up/down 必须带 `--env-file`** — compose 宿主挂载全经 `${ABNK_DEPLOY_ROOT:?}`（缺失即硬失败，不静默回落）；一切运行时写入物归部署根 `~/deploy`，代码域随仓库。
4. **镜像 tag = website package.json version** — `channels/website/package.json` 的 `version` 字段（`0.y.z`）。仅 patch 位随发版自动递增；minor/major 须用户明确指定。禁止复用已存在的版本号。
5. **用户确认是铁门** — Phase A 生成 Release Note 后必须停止，等用户明确回复"确认发版"才能进入 Phase B。
6. **TLS 证书生命周期** — 证书与私钥归部署根数据域 `$SSL_DIR`（compose 只读挂载 `/etc/nginx/ssl`）；私钥源件归档 `$SSL_ARCHIVE`（强管控），服务器丢失 = 自归档 scp 恢复。续期 = 覆盖两 PEM + `docker compose restart abnk-website`（无需 rebuild/重发版）。部署前置：证书存在 + 有效期 > 30 天 + 与私钥 modulus 匹配。
7. **服务器 clone 用专用 deploy key** — 服务器 `~/.ssh/id_rsa_github`（已配置 `~/.ssh/config`，`ssh.github.com:443`），只读用途即 GitHub 常规 SSH key；服务器上禁止任何文件编辑（纯 git pull + build + compose）。

### Two-Phase Flow

```
┌────────────────────────────────────────────────────┐
│  Phase A: Pre-Deploy (Review Checkpoint)           │
│                                                    │
│  0. 敏感信息审计（强制门禁——失败即中止）           │
│  1. 仓库推送与工作区干净核查                        │
│  2. 版本确定（website package.json → 镜像 tag）     │
│  3. 服务器就绪检查（SSH/Docker/磁盘/端口/证书）     │
│  4. 生成 Release Note → 审查                       │
│                                                    │
│  ⏸ IRON GATE: 等待用户回复"确认发版"               │
├────────────────────────────────────────────────────┤
│  Phase B: Deploy (制品全部在服务端构建)             │
│  5. 服务器 git pull + HEAD 一致性核对               │
│  6. docker build（abnk-website:<version>）          │
│  7. compose down → up（--env-file，注入镜像 tag）   │
│  8. 部署验证（容器健康 + HTTPS 200 + 301 跳转）     │
│  9. 更新 Release Note 实际结果 + commit            │
└────────────────────────────────────────────────────┘
```

---

## Phase A: Pre-Deploy (Review Checkpoint)

### Step 0: 敏感信息审计（强制门禁）

```bash
bash .github-private/abnk-prod/scripts/audit-sensitive-info.sh
# Expected: exit 0（5 节全 ✅）
```

审计失败处置：按脚本输出的泄漏项定位 → 从 public 仓库清除（git rm / 修改文件）→ 该信息如属生产必需则移入 `.github-private` → 重新审计通过后才能继续。**已 push 到远端的泄漏 = 立即告知用户评估凭据/证书轮换**（git 历史清除需用户裁决）。

### Step 1: 仓库推送与干净核查

```bash
cd <PROD_REPO_LOCAL>
git status --short                    # 应为空
git log --oneline origin/<PROD_BRANCH>..HEAD   # 应为空（全部已推送）
```

### Step 2: 确定版本

```bash
cd <PROD_REPO_LOCAL>/channels/website
grep '"version"' package.json         # 当前版本，如 0.1.0

# 服务器已部署版本（首次部署跳过）
<PROD_SSH> "docker inspect abnk-website --format '{{.Config.Image}}'" 2>/dev/null

# 递增规则（Iron Rule 4）：patch +1（如 0.1.0 → 0.1.1）；minor/major 须用户明确指定
# 禁止复用：目标 tag 不得等于运行中镜像 tag
```

版本 bump = 本地编辑 `package.json` version + commit + push（Phase A 内完成）。

### Step 3: 服务器就绪检查

```bash
# 1. SSH 连通 + Docker
<PROD_SSH> "echo 'SSH OK' && docker --version && docker compose version"

# 2. 磁盘与内存
<PROD_SSH> "df -h / && free -h"

# 3. 端口占用（80/443 应空闲或被 abnk-website 占用）
<PROD_SSH> "ss -tlnp | grep -E ':80|:443' || echo 'ports free'"

# 4. 部署根 + env 文件
<PROD_SSH> "ls ~/deploy/.env && cat ~/deploy/.env | grep ABNK_DEPLOY_ROOT"

# 5. TLS 证书（存在 + 有效期 + modulus 匹配——Iron Rule 6）
<PROD_SSH> "openssl x509 -in $SSL_DIR/fullchain.pem -noout -enddate -ext subjectAltName \
  && openssl x509 -in $SSL_DIR/fullchain.pem -noout -modulus | openssl md5 \
  && openssl rsa -in $SSL_DIR/privkey.pem -noout -modulus | openssl md5"
# Expected: SAN 含 *.amazingbank.ai + amazingbank.ai；notAfter > 30 天；两个 modulus MD5 一致

# 6. DNS 解析（域名 → 生产 IP）
dig +short amazingbank.ai A && dig +short www.amazingbank.ai A
# Expected: 均指向 <PROD_HOST>；未生效时验证降级 --resolve 并在 Release Note 挂账

# 7. 仓库在位（首次部署：clone <GIT_REPO>）
<PROD_SSH> "cd <PROD_REPO_SERVER> && git log --oneline -1 && git branch --show-current"
```

### Step 4: 生成 Release Note 并请求确认（IRON GATE）

生成 `.asdm/workspace/sre/ReleaseNotes/<version>/release-note.md`（模板见下），向用户完整输出并明确询问：

> - 回复 **"确认发版"** 开始 Phase B
> - 回复 **"修改"** + 意见，更新后重新提交 review
> - 回复 **"取消"** 中止

**在此停止。不得以任何理由跳过确认门。**

#### Release Note 模板

```markdown
# ABNK Website — Release Notes

**版本**：`<version>`（镜像 tag，= channels/website/package.json version）
**日期**：<YYYY-MM-DD>
**状态**：🟡 预部署（Phase A 完成，等待用户确认）
**分支**：`<PROD_BRANCH>`

## 基线信息

| 仓库 | 本次基线（HEAD） | 新提交数 |
|------|-----------------|---------|
| `abnk-system` | `<commit>` | N commits |

## 变更内容
<!-- git log 上版本基线..HEAD，含 files changed -->

## 部署命令（Phase B 在服务器执行）
<!-- docker build + compose down/up 完整命令（镜像 tag 注入）-->

## 执行进度跟踪
- [ ] ✅ Step 0：敏感信息审计（5 节全过）
- [ ] ✅ Step 1：仓库干净已推送（HEAD: `<commit>`）
- [ ] ✅ Step 2：版本确定（`<version>`）
- [ ] ✅ Step 3：服务器就绪（SSH/Docker/磁盘/端口/证书/DNS）
- [ ] ⬜ Step 5：服务器 git pull + HEAD 核对
- [ ] ⬜ Step 6：docker build
- [ ] ⬜ Step 7：compose 切换
- [ ] ⬜ Step 8：部署验证（HTTPS 200 + 301）
- [ ] ⬜ Step 9：Release Note 回填 + commit

## 环境就绪检查
| 检查项 | 状态 |
|--------|------|
| 敏感信息审计 | ✅ |
| TLS 证书（有效期/modulus） | ✅ <notAfter> |
| DNS（amazingbank.ai / www） | ✅ |
| 端口 80/443 | <状态> |
```

---

## Phase B: Deploy (Execute)

### Step 5: 服务器 Pull + HEAD 一致性核对

```bash
<PROD_SSH> "cd <PROD_REPO_SERVER> && git checkout <PROD_BRANCH> && git pull origin <PROD_BRANCH> \
  && git log --oneline -1"
# 必须等于 Phase A Step 1 推送的 commit——漂移即中止
```

### Step 6: Docker Build（服务端）

```bash
<PROD_SSH> "cd <PROD_REPO_SERVER> && docker build -f channels/website/Dockerfile \
  -t abnk-website:<version> channels/website 2>&1 | tail -10"
```

多阶段自含构建（npm ci + vite build 在 builder 内完成），服务器无需预装 Node。

### Step 7: Compose 切换

```bash
<PROD_SSH> "cd <PROD_REPO_SERVER> && \
  ABNK_WEBSITE_IMAGE=abnk-website:<version> \
    docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml down && \
  ABNK_WEBSITE_IMAGE=abnk-website:<version> \
    docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d"
# 依赖：证书在位（Step 3 已查）——缺失即 nginx 起不来
```

### Step 8: 部署验证

```bash
# 容器健康
<PROD_SSH> "docker compose --env-file ~/deploy/.env -f <PROD_REPO_SERVER>/deploy/prod/compose-abnk-prod.yaml ps"
# Expected: abnk-website Up (healthy)

# HTTPS 入口（本地执行——DNS 未生效时加 --resolve amazingbank.ai:443:<PROD_HOST>）
curl -s -o /dev/null -w "HTTPS: %{http_code}\n" https://amazingbank.ai/
# Expected: 200
curl -s -o /dev/null -w "HTTPS www: %{http_code}\n" https://www.amazingbank.ai/
# Expected: 200
curl -s -o /dev/null -w "HTTP redirect: %{http_code}\n" http://amazingbank.ai/
# Expected: 301
curl -sv https://amazingbank.ai/ 2>&1 | grep -E "subject:|expire date|SSL certificate verify"
# Expected: *.amazingbank.ai + verify ok
curl -s https://amazingbank.ai/ | grep -oE '<title>[^<]*</title>'
# Expected: 官网首页 title（非 nginx 默认页）

# 容器日志无 ERROR
<PROD_SSH> "docker logs abnk-website --tail=20"
```

### Step 9: 回填 Release Note + Commit

更新 Release Note：勾选 Phase B checkbox、状态改 `✅ 已完成`、补充验证结果，commit 到 `.asdm` 仓库。

## Rollback

```bash
# 回滚到上一版本（镜像仍在服务器本地缓存；首次部署无上一版可回）
<PROD_SSH> "cd <PROD_REPO_SERVER> && \
  ABNK_WEBSITE_IMAGE=abnk-website:<previous-version> \
    docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d --force-recreate"
```

无数据库/状态迁移——回滚即镜像切换，无需数据恢复。

## Troubleshooting

### 容器起不来 / healthcheck 失败
```bash
<PROD_SSH> "docker logs abnk-website --tail=30"
# 常见：证书 modulus 不匹配（Step 3 #5 应已拦截）/ PEM 含 CRLF（openssl 解析失败——源 zip 为 Windows 行尾，
# 上传前 tr -d '\r' 规范化）/ 证书链拼接缺换行（END 与 BEGIN 连行——cat 拼接时补空行）
```

### 公网 443 不通（服务器本地 curl 正常）
Azure NSG 未放行 80/443——Azure Portal → VM → Networking → Inbound rules 添加（服务器内不可见 NSG 状态）。

### 服务器证书丢失恢复
```bash
# 自本地强管控归档恢复（Iron Rule 6）
scp .github-private/ssl/amazingbank.ai.fullchain.pem .github-private/ssl/amazingbank.ai.privkey.pem \
  <PROD_SSH_USER>@<PROD_HOST>:$SSL_DIR/
<PROD_SSH> "chmod 600 $SSL_DIR/privkey.pem && docker compose --env-file ~/deploy/.env \
  -f <PROD_REPO_SERVER>/deploy/prod/compose-abnk-prod.yaml restart abnk-website"
```

## Notes

- Iron Rules 不可协商——尤其 Rule 1（敏感信息审计门禁）与 Rule 5（用户确认铁门）。
- 后续接入生产服务（如 Fineract 生产栈）时：compose 服务追加到 `deploy/prod/compose-abnk-prod.yaml`，生产凭据（DB 密码等）写入 `.github-private`，compose 经 env 引用部署根 `.env`——public 仓库只留占位符。
