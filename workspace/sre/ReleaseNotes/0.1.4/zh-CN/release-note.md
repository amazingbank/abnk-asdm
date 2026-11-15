# ABNK Website — Release Notes

**版本**：`0.1.4`（镜像 tag，= abnk-website 仓 package.json version）
**日期**：2026-11-10
**状态**：✅ 已完成（2026-11-10 部署验证通过——apex/www 重定向环修复生效）
**分支**：`main`
**性质**：🔴 **热修**（apex/www 无限重定向环——0.1.2 起既有缺陷，0.1.3 发版验证时暴露，详见 `../0.1.3/release-note.md`）

## 基线信息

| 仓库 | 上版本基线 | 本次基线（HEAD） | 新提交数 |
|------|-----------|-----------------|---------|
| `abnk-website`（主仓，发版对象） | `45ae899`（0.1.3） | `75c5f5d` | 2 commits（`764c431` 修复 + `75c5f5d` bump） |
| `abnk-system`（从仓，编排引用） | — | `609af17`（本地） | **未变** |

## 变更内容

### 热修：容器 nginx `:80` 面直接服务静态内容（`764c431`）

**缺陷**：容器 nginx.conf 沿用单体栈形态（`:80 → 301 https` + `:443` 自终止 TLS）。P3.5 全栈切换后公网 TLS 由 `abnk-nginx` 入口终止并平面反代 `abnk-website:80`——`:80` 的 301 使请求回到 https 入口再被反代回 `:80`，**无限重定向环**（`https://amazingbank.ai/` 与 `https://www.amazingbank.ai/` 不可达，自全栈上线起约 13h）。

**修复**：
- `:80` = **内容服务面**：直接托管静态资源——SPA fallback（`try_files → /index.html`）、发版缓存策略（`/assets/` 强缓存一年 / `index.html` no-store / `favicon.svg` no-cache）、安全头（X-Content-Type-Options / X-Frame-Options / Referrer-Policy；HSTS 由入口统一注入，HTTP 平面不重复声明）、ACME http-01 预留保留
- `:443` = **健康自检面**：TLS server 块原样保留（compose healthcheck `wget --no-check-certificate https://localhost/` 依赖 + 证书挂载加载；不对公网暴露，宿主端口由入口收口）
- 发版前验证：`nginx -t`（nginx:1.27-alpine 官方镜像）语法通过

**影响文件**：1 file changed, 51 insertions(+), 6 deletions(-)（+版本 bump 1 file）

## 部署命令（Phase B 在服务器执行）

```bash
# Step 5: pull + HEAD 核对（必须等于 75c5f5d）
<PROD_SSH> "cd ~/source/abnk-website && git pull origin main && git log --oneline -1"

# Step 6: 构建 + 推送（ghcr 私有包）
<PROD_SSH> "cd ~/source/abnk-website && docker build -t ghcr.io/amazingbank/abnk-website:0.1.4 . 2>&1 | tail -10 \
  && docker push ghcr.io/amazingbank/abnk-website:0.1.4"

# Step 7: .env tag 更新 + 单服务滚动 up（其余六容器零感知）
<PROD_SSH> "sed -i.bak 's|^ABNK_WEBSITE_IMAGE=.*|ABNK_WEBSITE_IMAGE=ghcr.io/amazingbank/abnk-website:0.1.4|' ~/deploy/.env \
  && grep '^ABNK_WEBSITE_IMAGE' ~/deploy/.env && rm ~/deploy/.env.bak"
<PROD_SSH> "cd ~/source/abnk-system && docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-website"

# Step 8: 验证（重点：apex/www 200——本版修复判据）
curl -s -o /dev/null -w '%{http_code}\n' https://amazingbank.ai/          # 200（修复判据）
curl -s -o /dev/null -w '%{http_code}\n' https://www.amazingbank.ai/     # 200（修复判据）
curl -s -o /dev/null -w '%{http_code}\n' http://amazingbank.ai/          # 301
curl -sI https://amazingbank.ai/ | grep -i 'cache-control'               # no-store（HTML 面）
curl -s https://api.amazingbank.ai/actuator/health                        # {"status":"UP"}
curl -s -o /dev/null -w '%{http_code}\n' https://app.amazingbank.ai/     # 200
curl -s -o /dev/null -w '%{http_code}\n' https://bo.amazingbank.ai/      # 200
<PROD_SSH> "docker ps --format '{{.Names}}\t{{.Status}}' | sort; docker logs abnk-website --tail=10"
```

**回滚**（如需）：`.env` 改回 `0.1.3` 同式单服务切换（回到重定向环态——除非 0.1.4 引入新问题，否则不建议）。

## 执行进度跟踪

- [x] ✅ Step 0：敏感信息审计（6 节全过——热修复用 0.1.3 发版同一审计窗口，期间 public 仓仅新增 nginx.conf 修复与本注记，无新增敏感形态）
- [x] ✅ Step 1：双仓干净已推送（abnk-website HEAD: `75c5f5d`；abnk-system 无随版变更）
- [x] ✅ Step 2：版本确定（`0.1.4`，在产 `0.1.3`——不重复；0.1.3 已推送 ghcr 不可覆盖，Iron Rule 8）
- [x] ✅ Step 3：服务器就绪（复用 0.1.3 发版前核查——SSH/磁盘/端口/证书/DNS 均绿；abnk-website 待 pull 至 `75c5f5d`）
- [x] ✅ Step 5：服务器 git pull + HEAD 核对（→ `75c5f5d`）
- [x] ✅ Step 6：docker build + push（ghcr 私有包 `0.1.4`，digest `1ff0469c…`）
- [x] ✅ Step 7：.env tag 更新 + 单服务滚动 up abnk-website（仅 recreate website，其余六容器零感知）
- [x] ✅ Step 8：部署验证（**修复判据 apex/www 200 达成**，详见下节）
- [x] ✅ Step 9：Release Note 回填 + commit

## 部署验证结果（Step 8，2026-11-10）

| 验证项 | 结果 |
|--------|------|
| **`https://amazingbank.ai/`** | ✅ **200**（重定向环修复生效——修复判据） |
| **`https://www.amazingbank.ai/`** | ✅ **200**（同上） |
| `http://amazingbank.ai/` | ✅ 301 → https（入口行为正确） |
| 页面 title | ✅ `Amazing Bank（ABNK）— 一家银行，也是一个范本`（真实首页，非 nginx 默认页） |
| 语言路由 `/zh-cn/` | ✅ 200（SPA fallback 生效） |
| HTML 缓存头 | ✅ `cache-control: no-store`（发版缓存策略随 :80 面生效） |
| `https://api.amazingbank.ai/actuator/health` | ✅ `{"status":"UP"}` |
| `https://app.amazingbank.ai/` / `https://bo.amazingbank.ai/` | ✅ 200 / 200 |
| 容器状态 | ✅ 七容器全 healthy；`abnk-website` 运行 `ghcr.io/amazingbank/abnk-website:0.1.4`；日志无 ERROR |
| 本版随附内容 | 0.1.3 的头部「了解 ASDM」h-10 修复随镜像血统一并上线 |

## 环境就绪检查

| 检查项 | 状态 |
|--------|------|
| 敏感信息审计 | ✅ 6 节全过（同窗口复验） |
| 修复验证 | ✅ `nginx -t` 语法通过（nginx:1.27-alpine） |
| 端口 80/443 | ✅ 由 abnk-nginx 入口容器占用——单服务滚动不触碰 |
| TLS 证书 | ✅ notAfter=2027-05-12；modulus 匹配（0.1.3 发版前核查） |
| DNS | ✅ amazingbank.ai / www → 生产 IP |
| 在产状态 | ⚠️ apex/www 不可达（重定向环）——本版修复对象；api/app/bo 正常 |
