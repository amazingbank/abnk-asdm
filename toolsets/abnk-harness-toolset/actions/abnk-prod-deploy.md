# ASDM Action: ABNK Production Deploy

## Metadata

```json
{
  "guid": "a8c3d4e5-f6a7-8901-2345-67890abcdef1",
  "name": "abnk-prod-deploy",
  "displayName": "ABNK Prod Deploy",
  "description": "- Audit sensitive info (Step 0 iron gate), check environment readiness, generate Release Note for review, then build Docker image (abnk-website——独立私有仓 abnk-website 官网前端，2026-11-10 迁出 abnk-system) on the production server and deploy the abnk-prod compose stack (abnk-website 静态托管；TLS 终止在 abnk-nginx 入口——https://amazingbank.ai)",
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

This action deploys the Amazing Bank 官网渠道前端（**独立私有仓 `abnk-website`**——Vite React SPA；2026-11-10 自 `abnk-system/channels/website` subtree split 迁出，承载 amazingbank.ai 入口/对外展示/方法论链接/社区管理，**不随 ABNK 开源**；ghcr 包同为 private——D8 修订「四公共 + 一私有」）to the production server（`abnk-vm001`）via Docker compose stack `abnk-prod`（`abnk-system/deploy/prod/compose-abnk-prod.yaml`）——容器 `abnk-website`（静态托管；TLS 由 `abnk-nginx` 入口终止），用户入口 `https://amazingbank.ai`（80 → 301 → https）。

### 敏感信息安全模型（本 action 的首要铁律）

> **⚠️ Single Source of Truth for Production Info**: 所有生产环境信息（服务器 IP、SSH 用户、路径、证书位置、DNS、凭据）**只存放于 `.github-private/abnk-prod/config.json`**（`.github-private` = workspace 内唯一 private repo）。本文件与所有 public 仓库（`abnk-system` / `fineract` / `.asdm`）**禁止出现任何生产敏感信息**——命令示例中的字面量仅为可读性，执行时一律从 private config 解析。开发环境信息（本地调试凭据等）允许出现在 public 仓库。

**信息分级**：

| 级别 | 内容 | 存放位置 |
|------|------|---------|
| 🔴 生产敏感 | 服务器 IP / SSH / 生产凭据 / TLS 私钥 / 生产路径 / **制品库推送 PAT**（D8） | `.github-private/`（ssl 归档 `ssl/`，环境配置 `abnk-prod/config.json`，PAT 归档 `abnk-prod/`） |
| 🔴 私有代码 | `abnk-website` 仓（官网独立私有仓——D9：对外展示/方法论链接/社区管理，不随 ABNK 开源）；ghcr 包 `abnk-website`（private，D8 修订「四公共 + 一私有」） | `amazingbank/abnk-website`（private repo）+ ghcr private package |
| 🟢 开发公开 | 本地调试凭据（postgres/postgres、mifos:password 等）、代码、compose 编排、Dockerfile、**制品镜像本体**（四服务公开包——gateway/fineract/mweb/bo） | public 仓库（`abnk-system` / `.asdm`）与 ghcr.io/amazingbank |

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
| `$PROD_REPO_SERVER` | `environments.production.server.serverRepoPath.server`（abnk-system 仓——compose/env 所在） |
| `$PROD_REPO_LOCAL` | `environments.production.server.serverRepoPath.local` |
| `$PROD_BRANCH` | `environments.production.server.branches.abnkSystem` |
| `$WEBSITE_REPO_SERVER` | `environments.production.server.websiteRepo.server`（**abnk-website 独立私有仓——本 action 的发版对象**，D9） |
| `$WEBSITE_REPO_LOCAL` | `environments.production.server.websiteRepo.local` |
| `$WEBSITE_GIT_REPO` | `environments.production.server.websiteRepo.githubRepoUrl` |
| `$PROD_COMPOSE_FILE` | `environments.production.server.dockerComposeFile`（相对 abnk-system 仓库根） |
| `$PROD_DEPLOY_ROOT` | `environments.production.deploy.deployRoot` |
| `$PROD_ENV_FILE` | `environments.production.deploy.envFile` |
| `$SSL_DIR` | `environments.production.deploy.ssl.serverDir` |
| `$SSL_ARCHIVE` | `environments.production.deploy.ssl.localArchive`（本地归档——服务器证书丢失时 scp 恢复） |
| `$GIT_REPO` | `environments.production.server.githubRepoUrl`（abnk-system） |

### Iron Rules

1. **敏感信息铁律** — 生产环境信息只在 `.github-private`（见安全模型节）。Step 0 审计是每次部署的强制门禁；审计失败 = 中止。发现泄漏的处置：从 public 仓库清除 → 移入 `.github-private` → commit → 必要时轮换凭据/证书。
2. **所有代码改动在本地，所有制品在服务端构建并推送 ghcr** — 本地 Mac 只做 edit/commit/push（**本地构建的镜像不推送不发布——仅调试用**）；服务器 `git pull` + `docker build`（x86_64 原生）+ `docker push ghcr.io/amazingbank/*` + compose 切换。禁止本地构建镜像推送（Mac ARM64 vs 服务器 x86_64）。
3. **up/down 必须带 `--env-file`** — compose 宿主挂载全经 `${ABNK_DEPLOY_ROOT:?}`（缺失即硬失败，不静默回落）；一切运行时写入物归部署根 `~/deploy`，代码域随仓库。
4. **镜像 tag = website package.json version** — `abnk-website` 仓（独立私有仓）`package.json` 的 `version` 字段（`0.y.z`）。仅 patch 位随发版自动递增；minor/major 须用户明确指定。禁止复用已存在的版本号。
5. **用户确认是铁门** — Phase A 生成 Release Note 后必须停止，等用户明确回复"确认发版"才能进入 Phase B。
6. **TLS 证书生命周期** — 证书与私钥归部署根数据域 `$SSL_DIR`（compose 只读挂载 `/etc/nginx/ssl`）；私钥源件归档 `$SSL_ARCHIVE`（强管控），服务器丢失 = 自归档 scp 恢复。续期 = 覆盖两 PEM + `docker compose restart abnk-nginx`（**P3.4 拓扑适配：TLS 终止在 `abnk-nginx` 入口，续期 restart 目标已从 abnk-website 迁至 abnk-nginx**；无需 rebuild/重发版）。部署前置：证书存在 + 有效期 > 30 天 + 与私钥 modulus 匹配。
7. **服务器 clone 用专用 deploy key（一仓一把）** — abnk-system：`~/.ssh/id_rsa_github`（已配置 `~/.ssh/config`，`ssh.github.com:443`）；abnk-website（D9 独立仓）：`~/.ssh/id_ed25519_abnk_website`（read-only deploy key，仓库级 `core.sshCommand` 已配置——clone 后无需再指定）。服务器上禁止任何文件编辑（纯 git pull + build + compose）。
8. **制品库 = GitHub Packages**（D8，2026-11-10；**D9 修订**）— ABNK 定位开源可演示银行系统（展示 ASDM 全 SDLC AI 能力），镜像发布 `ghcr.io/amazingbank/abnk-*`：gateway/fineract/mweb/bo **四包公共**（匿名 pull 免登录、存储/流量免费不设配额），**abnk-website 私有包**（D9：源仓私有，镜像同口径——外部匿名 pull 不适用于 website）。推送 PAT（`write:packages`）只存 `.github-private` 与服务器 docker config（服务器已登录 ghcr，私有包 pull 正常）；**禁止覆盖已推送 tag**（ghcr 允许覆盖同 tag——不可变性靠纪律）；推送凭据泄漏扫描入 Step 0 审计门（第 5 节）。

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
│  5. 服务器 git pull（abnk-website 仓）+ HEAD 核对   │
│  6. docker build + push（abnk-website:<version>）  │
│  7. .env 更新镜像 tag + 单服务滚动 up abnk-website │
│  8. 部署验证（website 健康 + 全栈六容器不受影响）   │
│  9. 更新 Release Note 实际结果 + commit            │
└────────────────────────────────────────────────────┘
```

---

## Phase A: Pre-Deploy (Review Checkpoint)

### Step 0: 敏感信息审计（强制门禁）

```bash
bash .github-private/abnk-prod/scripts/audit-sensitive-info.sh
# Expected: exit 0（6 节全 ✅——第 5 节为 GitHub PAT/Token 扫描，D8 引入）
```

审计失败处置：按脚本输出的泄漏项定位 → 从 public 仓库清除（git rm / 修改文件）→ 该信息如属生产必需则移入 `.github-private` → 重新审计通过后才能继续。**已 push 到远端的泄漏 = 立即告知用户评估凭据/证书轮换**（git 历史清除需用户裁决）。

### Step 1: 仓库推送与干净核查（双仓——D9 后）

```bash
# 主仓：abnk-website（发版对象）
cd <WEBSITE_REPO_LOCAL>
git status --short                            # 应为空
git log --oneline origin/main..HEAD          # 应为空（全部已推送）

# 从仓：abnk-system（仅当 compose/env 样例等编排引用有变化时随版核查）
cd <PROD_REPO_LOCAL>
git status --short                            # 应为空
git log --oneline origin/<PROD_BRANCH>..HEAD  # 应为空
```

### Step 2: 确定版本

```bash
cd ~/source/asdm/amazingbank-ws/abnk-website   # 独立私有仓（websiteRepo 解析自 private config）
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

# 3. 端口占用（80/443 应由 abnk-nginx 入口容器占用——P3.4 起唯一宿主端口绑定者）
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

# 7. 仓库在位（双仓——首次部署：clone <GIT_REPO> 与 <WEBSITE_GIT_REPO>；
#    abnk-website 仓用专用 deploy key，clone 时 GIT_SSH_COMMAND 指定，clone 后
#    仓库级 core.sshCommand 已持久化，后续 git pull 直用）
<PROD_SSH> "cd <WEBSITE_REPO_SERVER> && git log --oneline -1 && git branch --show-current \
  && cd <PROD_REPO_SERVER> && git log --oneline -1 && git branch --show-current"
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

**版本**：`<version>`（镜像 tag，= abnk-website 仓 package.json version）
**日期**：<YYYY-MM-DD>
**状态**：🟡 预部署（Phase A 完成，等待用户确认）
**分支**：`<PROD_BRANCH>`

## 基线信息

| 仓库 | 本次基线（HEAD） | 新提交数 |
|------|-----------------|---------|
| `abnk-website`（主仓，发版对象） | `<commit>` | N commits |
| `abnk-system`（从仓，编排引用——无变更则标「未变」） | `<commit>` | 0/N commits |

## 变更内容
<!-- abnk-website 仓 git log 上版本基线..HEAD，含 files changed -->

## 部署命令（Phase B 在服务器执行）
<!-- .env tag 更新 + 单服务滚动 up（见 Step 6/7 命令） -->

## 执行进度跟踪
- [ ] ✅ Step 0：敏感信息审计（6 节全过）
- [ ] ✅ Step 1：双仓干净已推送（abnk-website HEAD: `<commit>`）
- [ ] ✅ Step 2：版本确定（`<version>`）
- [ ] ✅ Step 3：服务器就绪（SSH/Docker/磁盘/端口/证书/DNS/双仓在位）
- [ ] ⬜ Step 5：服务器 git pull + HEAD 核对（abnk-website）
- [ ] ⬜ Step 6：docker build + push（ghcr 私有包）
- [ ] ⬜ Step 7：.env tag 更新 + 单服务滚动 up abnk-website
- [ ] ⬜ Step 8：部署验证（website 健康 + 三子域 + 全栈不受影响）
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

### Step 5: 服务器 Pull + HEAD 一致性核对（主仓 abnk-website；abnk-system 有随版变更时同式核对）

```bash
<PROD_SSH> "cd <WEBSITE_REPO_SERVER> && git checkout main && git pull origin main \
  && git log --oneline -1"
# 必须等于 Phase A Step 1 推送的 commit——漂移即中止
```

### Step 6: Docker Build + Push（服务端，D8 口径）

```bash
<PROD_SSH> "cd ~/source/abnk-website && docker build \
  -t ghcr.io/amazingbank/abnk-website:<version> . 2>&1 | tail -10 \
  && docker push ghcr.io/amazingbank/abnk-website:<version>"
```

多阶段自含构建（npm ci + vite build 在 builder 内完成），服务器无需预装 Node。
**D8/D9**：tag 用 ghcr FQN 并在构建后 push（Iron Rule 8）——`abnk-website` 为**私有包**
（服务器已 docker login ghcr.io，push/pull 正常；外部匿名 pull 不适用）。
全栈其余四镜像（gateway/fineract/mweb/bo，公共包）的发布走全栈发布流程（P3.5 范式），
不在本 action 范围。

### Step 7: Compose 切换（**单服务滚动**——P3.4 全栈时代口径）

> ⚠️ **禁止全栈 down/up**：`compose-abnk-prod.yaml` 已是七容器全栈（nginx 入口/gateway/
> fineract/pg/bo/mweb/website）——website 发版若 `down` 会中断 api/app/bo 全部线上服务。
> 正确姿势：更新部署根 `.env` 的 `ABNK_WEBSITE_IMAGE` → 只对 `abnk-website` 单服务
> `up -d`（镜像 tag 变化自动触发 recreate，其余六容器零感知）。

```bash
# 1) 更新部署根 .env 的镜像 tag（sed 原位替换——其余 9 个变量不动）
<PROD_SSH> "sed -i.bak 's|^ABNK_WEBSITE_IMAGE=.*|ABNK_WEBSITE_IMAGE=ghcr.io/amazingbank/abnk-website:<version>|' ~/deploy/.env \
  && grep '^ABNK_WEBSITE_IMAGE' ~/deploy/.env && rm ~/deploy/.env.bak"

# 2) 单服务滚动 up（--env-file 铁律 3；compose 检测 tag 变化仅 recreate abnk-website）
<PROD_SSH> "cd <PROD_REPO_SERVER> && \
  docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-website"
# 依赖：证书在位（Step 3 已查）——缺失即 abnk-nginx/website 起不来
# compose pull_policy 缺省 missing：本地已有同 FQN 镜像（Step 6 刚构建）不重复拉取
```

### Step 8: 部署验证

```bash
# 容器健康（七容器——重点：abnk-website 新版本 healthy + 其余六容器不受滚动影响）
<PROD_SSH> "docker compose --env-file ~/deploy/.env -f <PROD_REPO_SERVER>/deploy/prod/compose-abnk-prod.yaml ps"
# Expected: 七 service Up (healthy)；abnk-website 运行镜像 = 本次 <version>
<PROD_SSH> "docker inspect abnk-website --format '{{.Config.Image}}'"

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

# 滚动影响面核查（单服务发版的回归判据——api/app/bo 不受影响）
curl -s https://api.amazingbank.ai/actuator/health        # Expected: {"status":"UP"}
curl -s -o /dev/null -w '%{http_code}\n' https://app.amazingbank.ai/   # Expected: 200
curl -s -o /dev/null -w '%{http_code}\n' https://bo.amazingbank.ai/    # Expected: 200

# 容器日志无 ERROR
<PROD_SSH> "docker logs abnk-website --tail=20"
```

### Step 9: 回填 Release Note + Commit

更新 Release Note：勾选 Phase B checkbox、状态改 `✅ 已完成`、补充验证结果，commit 到 `.asdm` 仓库。

## Rollback（单服务镜像切换——与 Step 7 同式）

> ⚠️ **滚动 up 后必须 `docker restart abnk-nginx`**（2026-11-12 bo 0.1.1 + mweb 1.0.1 发版实测新增纪律）：nginx worker 启动时解析并缓存 upstream 容器名 → IP 映射，被反代容器（bo/mweb/website/gateway）recreate 时 Docker 重新分配 IP，nginx 若不重启则按旧 IP 转发——bo/mweb 双 recreate 实测触发 `bo.*`/`app.*` 内容互换错位（容器产物/配置/DNS 三者均正确，仅 nginx 缓存陈旧）。修复与预防 = 每次滚动 up 后重启入口 nginx（秒级）。根治方案（`resolver 127.0.0.11` + 变量式 proxy_pass）挂账后续优化。
> ⚠️ **After any rolling up, `docker restart abnk-nginx` is mandatory** (new discipline from the bo 0.1.1 + mweb 1.0.1 release, 2026-11-12): nginx workers resolve and cache the upstream container-name → IP mapping at startup; when a proxied container (bo/mweb/website/gateway) is recreated Docker reassigns IPs, and an un-restarted nginx keeps forwarding to stale IPs — the bo/mweb double recreate swapped the content served by `bo.*`/`app.*` (container artifacts, nginx config and DNS were all correct; only the nginx cache was stale). Fix and prevention = restart the entry nginx after every rolling up (seconds). A permanent fix (resolver 127.0.0.11 + variable-form proxy_pass) is backloged.

```bash
# 回滚到上一版本（D8 后：历史 tag 随时可自 ghcr 拉取——服务器本地缓存或 registry 双通道；
# abnk-website 私有包经服务器已登录凭据拉取）
<PROD_SSH> "sed -i.bak 's|^ABNK_WEBSITE_IMAGE=.*|ABNK_WEBSITE_IMAGE=ghcr.io/amazingbank/abnk-website:<previous-version>|' ~/deploy/.env && rm ~/deploy/.env.bak \
  && cd <PROD_REPO_SERVER> && \
  docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-website"
```

无数据库/状态迁移——回滚即镜像切换（仅 recreate abnk-website），无需数据恢复。

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
# P3.4 拓扑：TLS 终止在 abnk-nginx 入口——restart 目标为 abnk-nginx
#（abnk-website 容器内 conf 亦加载同一挂载，稳妥可一并 restart）
<PROD_SSH> "chmod 600 $SSL_DIR/privkey.pem && docker compose --env-file ~/deploy/.env \
  -f <PROD_REPO_SERVER>/deploy/prod/compose-abnk-prod.yaml restart abnk-nginx abnk-website"
```

## Notes

- Iron Rules 不可协商——尤其 Rule 1（敏感信息审计门禁）与 Rule 5（用户确认铁门）。
- **本 action 范围（D9 后）**：`abnk-website` 单服务发版（私有仓 → 服务端构建 → ghcr 私有包 → 单服务滚动）。全栈发布/扩容（七容器 compose 整体切换、四公共镜像、网关/fineract 等）走全栈发布流程（P3.5 两阶段铁门范式，工具集内以 Sprint 文档承载）。
- 部署根 `.env` 为全栈唯一真实值 env（10 变量）；website 发版只动 `ABNK_WEBSITE_IMAGE` 一行，其余九个变量（四镜像 tag/JWT/DB 凭据/部署根）不得变更——变更即全栈发版范畴，需走全栈流程与铁门。
