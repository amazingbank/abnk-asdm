# ABNK Website — Release Notes

**版本**：`0.1.3`（镜像 tag，= abnk-website 仓 package.json version）
**日期**：2026-11-10
**状态**：⚠️ 容器侧部署完成，公网验证暴露**既有缺陷**（apex/www 无限重定向环——非本版引入，0.1.2 起即存在）→ 转 **0.1.4 热修**（见 `../0.1.4/release-note.md`）
**分支**：`main`

## 基线信息

| 仓库 | 上版本基线 | 本次基线（HEAD） | 新提交数 |
|------|-----------|-----------------|---------|
| `abnk-website`（主仓，发版对象——D9 独立私有仓） | `d2521b3`（0.1.2） | `45ae899` | 4 commits（`cb1794f` + `8cb849b` + `2392b75` + `45ae899`） |
| `abnk-system`（从仓，编排引用） | — | `609af17`（本地） | **未变**（本次发布不涉及 compose/env/编排变更——website 镜像经 ghcr FQN 引用，`ABNK_WEBSITE_IMAGE` 之外的九变量不动） |

## 变更内容

### 1. UI 修复：头部「了解 ASDM」链接高度统一（`cb1794f`）

- `src/components/Nav.tsx` — 「了解 ASDM」链接高度统一 `h-10`（40px），与语言切换按钮/菜单按钮基线一致（视觉评审反馈项）
- **生产可见变更**（本版唯一页面内容变化）

### 2. 工程规范：ABNK 6200-6299 端口规范 + 调试端口迁移（`8cb849b`）

- `vite.config.ts` — dev server 端口 `5173 → 6201`（纳入 ABNK 62xx 端口规范；**仅 dev 生效，生产构建无影响**）
- 仓内端口规范文档建立（docs 域）

### 3. 构建：builder 阶段钉 `$BUILDPLATFORM`（`2392b75`）

- `Dockerfile` — builder stage 显式 `--platform=$BUILDPLATFORM`（多架构构建口径统一，gateway/bo/website 三 Dockerfile 同式）
- 服务器 x86_64 原生构建行为不变（本提交在服务端为无操作变更）

### 4. 版本 bump（`45ae899`）

- `package.json` `0.1.2 → 0.1.3`（Iron Rule 4：patch 递增，不与在产 tag `ghcr.io/amazingbank/abnk-website:0.1.2` 复用）

**影响文件**：4 files changed, 18 insertions(+), 3 deletions(-)

## 部署命令（Phase B 在服务器执行）

```bash
# Step 5: pull + HEAD 核对（必须等于 45ae899）
<PROD_SSH> "cd ~/source/abnk-website && git checkout main && git pull origin main && git log --oneline -1"

# Step 6: 构建 + 推送（ghcr 私有包——服务器已 docker login ghcr.io）
<PROD_SSH> "cd ~/source/abnk-website && docker build -t ghcr.io/amazingbank/abnk-website:0.1.3 . 2>&1 | tail -10 \
  && docker push ghcr.io/amazingbank/abnk-website:0.1.3"

# Step 7: .env tag 更新 + 单服务滚动 up（⚠️ 禁止全栈 down/up——单服务 recreate，其余六容器零感知）
<PROD_SSH> "sed -i.bak 's|^ABNK_WEBSITE_IMAGE=.*|ABNK_WEBSITE_IMAGE=ghcr.io/amazingbank/abnk-website:0.1.3|' ~/deploy/.env \
  && grep '^ABNK_WEBSITE_IMAGE' ~/deploy/.env && rm ~/deploy/.env.bak"
<PROD_SSH> "cd ~/source/abnk-system && docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-website"

# Step 8: 验证（website 健康 + 三子域 + 全栈不受影响）
<PROD_SSH> "docker compose --env-file ~/deploy/.env -f ~/source/abnk-system/deploy/prod/compose-abnk-prod.yaml ps"
<PROD_SSH> "docker inspect abnk-website --format '{{.Config.Image}}' && docker logs abnk-website --tail=20"
curl -s -o /dev/null -w '%{http_code}\n' https://amazingbank.ai/          # 200
curl -s -o /dev/null -w '%{http_code}\n' https://www.amazingbank.ai/     # 200
curl -s -o /dev/null -w '%{http_code}\n' http://amazingbank.ai/          # 301
curl -s https://api.amazingbank.ai/actuator/health                        # {"status":"UP"}
curl -s -o /dev/null -w '%{http_code}\n' https://app.amazingbank.ai/     # 200
curl -s -o /dev/null -w '%{http_code}\n' https://bo.amazingbank.ai/      # 200
```

**回滚**（如需）：`.env` 的 `ABNK_WEBSITE_IMAGE` 改回 `ghcr.io/amazingbank/abnk-website:0.1.2` → 同式单服务 `up -d abnk-website`（镜像切换，无状态迁移）。

## 执行进度跟踪

- [x] ✅ Step 0：敏感信息审计（6 节全过，2026-11-10 实测 exit 0）
- [x] ✅ Step 1：双仓干净已推送（abnk-website HEAD: `45ae899`；abnk-system `609af17` 无随版变更）
- [x] ✅ Step 2：版本确定（`0.1.3`，服务器现运行 `0.1.2`——不与在产 tag 重复）
- [x] ✅ Step 3：服务器就绪（SSH/Docker 29.9.2/磁盘 100G 可用/内存 4.7Gi 可用/端口 80·443 归 abnk-nginx/证书 modulus 匹配/DNS 生效/双仓在位）
- [x] ✅ Step 5：服务器 git pull + HEAD 核对（abnk-website → `45ae899`，fast-forward）
- [x] ✅ Step 6：docker build + push（ghcr 私有包 `0.1.3`，digest `a78336b4…`）
- [x] ✅ Step 7：.env tag 更新 + 单服务滚动 up abnk-website（仅 recreate website，其余六容器零感知）
- [x] ⚠️ Step 8：部署验证——**部分通过，发现既有缺陷**（详见下节）
- [x] ✅ Step 9：Release Note 回填 + 转 0.1.4 热修

## 部署验证结果（Step 8，2026-11-10）

| 验证项 | 结果 |
|--------|------|
| 容器状态 | ✅ `abnk-website` Up (healthy)，运行镜像 `ghcr.io/amazingbank/abnk-website:0.1.3`；其余六容器 healthy 零感知 |
| `https://api.amazingbank.ai/actuator/health` | ✅ `{"status":"UP"}` |
| `https://app.amazingbank.ai/` / `https://bo.amazingbank.ai/` | ✅ 200 / 200 |
| `http://amazingbank.ai/` | ✅ 301 → https（入口行为正确） |
| **`https://amazingbank.ai/` / `https://www.amazingbank.ai/`** | ❌ **301 + `location: https://amazingbank.ai/`（无限重定向环）** |
| 容器日志 | ✅ 无 ERROR |

**根因（既有，非本版引入）**：abnk-website 容器 nginx.conf 为单体栈形态（`:80 → 301 https` + `:443` 自终止 TLS）；P3.5 全栈切换后公网 TLS 由 abnk-nginx 入口终止并平面反代 `abnk-website:80`——`:80` 的 301 使请求回到 https 入口再被反代回 `:80`，无限循环。**0.1.2（全栈上线起约 13h）即受影响**；fullstack-0.1.0 验证清单漏验 apex HTTPS 200（`http→301` 恰好掩盖）。回滚 0.1.2 无意义（同缺陷）→ 热修随 **0.1.4** 发布（`:80` 改为直接服务静态内容，`:443` 保留供 healthcheck）。

## 环境就绪检查

| 检查项 | 状态 |
|--------|------|
| 敏感信息审计 | ✅ 6 节全过（exit 0） |
| SSH / Docker | ✅ Docker 29.9.2 / Compose 5.6.1 |
| 磁盘 / 内存 | ✅ 100G 可用 / 4.7Gi 可用 |
| 端口 80/443 | ✅ 由 abnk-nginx 入口容器占用（docker-proxy）——单服务滚动不触碰 |
| 部署根 + .env | ✅ `~/deploy/.env`（10 变量，本版仅动 `ABNK_WEBSITE_IMAGE` 一行） |
| TLS 证书（有效期/modulus） | ✅ notAfter=2027-05-12（>30 天）；SAN *.amazingbank.ai + amazingbank.ai；modulus MD5 一致 |
| DNS（amazingbank.ai / www） | ✅ 均指向生产 IP |
| 服务器双仓 | ✅ abnk-website `2392b75`（待 pull 至 `45ae899`）；abnk-system `19bb0f6`（本次无随版变更，不强求同步） |
