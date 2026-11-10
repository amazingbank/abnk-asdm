# ABNK Fullstack — Release Notes

**版本**：`fullstack-0.1.0`（全栈首次发布——七容器拓扑；网关版本 `0.1.0` 为主版本口径）
**日期**：2026-11-10
**状态**：✅ 已完成（2026-11-10 部署验证通过——用户「确认发版」后 Phase B 执行完毕）
**分支**：`main`（abnk-system）；fineract 仓 WAR 基线 `7b896ad6`

## 基线信息

| 仓库 | 上版本 | 上版本基线 | 本次基线（HEAD） | 新提交数 |
|------|--------|-----------|-----------------|---------|
| `abnk-system` | website `0.1.2` | `e1751aa`（2026-10-27） | `fb3b944` | 27 commits（P0.1–P3.4 + D8/P3.5 前置） |
| `fineract`（WAR） | 平台栈 `ad988473` | — | `7b896ad6`（P0.5 custom 骨架） | WAR 重建 + sha256 双向校验（`de6d8a68…`） |

## 发布镜像（服务端构建 + ghcr 推送，D8 口径）

| 服务 | 镜像（FQN tag） | digest（前 12 位） | 构建时长 |
|------|----------------|--------------------|---------|
| 入口 | `nginx:1.27-alpine`（钉版本基础镜像） | — | 拉取 |
| 数据库 | `postgres:18.3`（钉版本基础镜像） | — | 已在服务器 |
| Fineract | `ghcr.io/amazingbank/abnk-fineract:7b896ad6` | `21749b6d5410` | 35s |
| 官网 | `ghcr.io/amazingbank/abnk-website:0.1.2` | `269d1c5c0f17` | 服务端已构建，tag FQN |
| 网关 | `ghcr.io/amazingbank/abnk-gateway:0.1.0` | `b114d38618ad` | 1m52s |
| Backoffice | `ghcr.io/amazingbank/abnk-bo:0.1.0` | `5d36f3779a96` | 42s |
| 手机银行 web | `ghcr.io/amazingbank/abnk-mweb:1.0.0` | `a483680189ca` | ~4 min |

## 变更内容（上版本 website 0.1.2 → 本次全栈）

### 拓扑：单容器官网栈 → 七容器全栈（单 VM）

- **`abnk-nginx` 单入口**（唯一绑定宿主 80/443）：TLS 终止（通配证书 `*.amazingbank.ai`）+ 按 Host 分流——`api.` → 网关、`app.` → 手机银行 web、`bo.` → Backoffice、apex/`www` → 官网
- **网关 `abnk-gateway`**（SCG，容器化）：简化登录 JWT / 对客收敛面 `/abnk/api/v1/*` / bo 转发 `/bo/api/*` / 转账聚合幂等+补偿 / 通道隔离（P2.1–P2.7）
- **双前端接线**（P3.1/P3.2）：手机银行与 Backoffice 从 mock 切换到 openapi 生成 client（真实网关 + Fineract 数据）
- **Fineract 生产形态**：WAR + Tomcat 容器（沿用 P0.4 平台栈口径，卷 `abnk-pg-platform-data` 数据不动、种子连续）；D7 公网直暴 8080 随本栈收编退役（NSG 8080 规则后续可收紧）
- **缺口验证资产**（P3.3）：`baseline_gap_test.py`——POC 开场演示「证件过期客户转账依然成功」的自动化证据
- 525 files changed, 65842 insertions(+)

### 本地演练已通过（VP3.4.1–VP3.4.5，2026-11-10）

七容器全 healthy；种子施加 3 客户；双剧本（缺口 23 断言 / 网关 55 断言）退出码 0。

## 部署命令（Phase B 在服务器执行）

```bash
# 0) 更新部署根 .env 为全栈形态（含五镜像 FQN + ABNK_JWT_SECRET 生产值 +
#    保留 ABNK_FINERACT_IMAGE_TAG 供平台栈 down；DB 凭据沿用现网）
# （由部署流程经 heredoc 写入 ~/deploy/.env，值源 .github-private 凭据档案）

# 1) 退役平台栈（容器 abnk-fineract/abnk-pg-platform 与全栈同名——必须先退役；
#    卷挂载为部署根路径，数据卷 abnk-pg-platform-data 不动）
cd ~/source/abnk-system
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-platform.yaml down

# 2) 官网栈切换（既有官网服务短暂中断窗口——秒级）
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml down
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d

# 3) 验证
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml ps  # 七容器 healthy
curl -s https://api.amazingbank.ai/actuator/health        # "status":"UP"
curl -s -o /dev/null -w '%{http_code}' https://api.amazingbank.ai/abnk/api/v1/loan-products  # 401（无 token）
curl -s -o /dev/null -w '%{http_code}' https://app.amazingbank.ai/   # 200
curl -s -o /dev/null -w '%{http_code}' https://bo.amazingbank.ai/    # 200
curl -s -o /dev/null -w '%{http_code}' http://amazingbank.ai/        # 301
```

## 回滚预案

镜像切换式回滚（无 DB schema 变更，数据卷/部署根挂载不动）：

```bash
# 全栈回滚 = ①② 反序重 up 平台栈（+ 官网栈还原为单容器形态）：
cd ~/source/abnk-system
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml down
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-platform.yaml up -d
# 官网回滚到独立 80/443 形态需 checkout 历史版本 compose（abnk-website:0.1.2 镜像不变）
```

回滚判据：全栈 up 后 30 min 内七容器未全 healthy，或 api/app/bo 公网验证连续失败。

## 执行进度跟踪

- [x] ✅ Step 0：敏感信息审计（6 节全过——首跑拦截 1 项生产 IP 泄漏，已清除 + commit `91f9191`，复跑全绿）
- [x] ✅ Step 1：仓库干净已推送（abnk-system HEAD: `fb3b944`；`origin/main..HEAD` = 0）
- [x] ✅ Step 2：版本确定（gateway `0.1.0` / website `0.1.2` / mweb `1.0.0` / bo `0.1.0` / fineract `7b896ad6`）
- [x] ✅ Step 3：服务器就绪（SSH/Docker 29.9.2/磁盘 117G/内存 5.3G/证书 2027-05-12/DNS 六条 A 记录/`git pull` HEAD 一致 + WAR sha256 校验通过）
- [x] ✅ Step 6（前置）：五镜像服务端构建 + ghcr 推送全成功（VP3.5.4）
- [x] ✅ Phase B：部署根 .env 扩容为全栈形态（10 变量，JWT 生产值经 stdin 注入）
- [x] ✅ Phase B：① 退役平台栈（down，用户铁门确认；卷 `abnk-pg-platform-data` 保留）
- [x] ✅ Phase B：② 官网栈切换 down → up（中断秒级）
- [x] ✅ Phase B：七容器 healthy（3 min 内全绿）+ 三子域公网验证五值全中（UP/401/200/200/301）
- [x] ✅ Phase B：公网缺口剧本回归（退出码 0，断言 23/23）
- [x] ✅ Phase B：Release Note 回填 + commit（VP3.5.9）

## 环境就绪检查

| 检查项 | 状态 |
|--------|------|
| 敏感信息审计 | ✅ 6 节全过（2026-11-10 复跑） |
| SSH / Docker | ✅ Docker 29.9.2 / Compose v5.6.1 |
| 磁盘 / 内存 | ✅ 117G 可用 / 5.3G 可用（≥ 20G/4G 口径） |
| 端口 80/443 | ✅ 由现运行官网栈占用——compose 切换即接管 |
| 部署根 + .env | ✅ 已扩容为全栈形态（10 变量：五镜像 FQN + JWT + DB 凭据 + 平台栈 legacy）；initdb/ssl/WAR 在位 |
| TLS 证书 | ✅ notAfter=2027-05-12（>30 天）；SAN *.amazingbank.ai |
| DNS（api/app/bo + apex/www/@） | ✅ 六条 A 记录 → `$PROD_HOST`（2026-11-10 dig 实测全中） |
| 服务器仓库 | ✅ main @ `fb3b944`（与本地推送一致） |
| ghcr 登录 | ✅ `auths: ['ghcr.io']`（PAT 经 stdin 注入） |
| JWT 生产密钥 | ✅ 源件 `.github-private/abnk-prod/jwt-secret.txt`（600） |

## 挂账与风险声明

| 项 | 说明 | 影响 |
|----|------|------|
| ghcr 包可见性 public + 关联源仓库 | REST API 对 org 包不支持 PATCH visibility（实测 GET 200 / PATCH 404）——需 org admin 在 `github.com/orgs/amazingbank/packages` 各包设置页手动设置（五包：abnk-fineract/gateway/website/bo/mweb） | 不阻塞部署（服务器本地镜像齐备，`pull_policy missing` 命中本地）；仅影响匿名 pull/外部回滚通道 |
| 官网中断窗口 | ② compose 定义变更（website 端口收编）必然触发 recreate | 秒级中断；回滚预案已备 |
| NSG 8080 规则 | D7 直暴形态随本栈切换退役 | 公网入口统一收口 abnk-nginx 80/443；8080 规则可后续收紧（Azure Portal 操作，非本次范围） |
| 网关用户表实例态 | `gateway_users.json` 已恢复 server 实例（`fb3b944`，口令与服务器在产种子一致）；镜像 bake 后不可变 | alice/bob/admin 演示口令 = 服务器种子态（`.github-private` 归档） |

## 部署验证结果（Phase B，2026-11-10）

| 验证项 | 结果 |
|--------|------|
| 容器状态 | ✅ 七容器全部 healthy（`abnk-nginx`/`abnk-website`/`abnk-gateway`/`abnk-fineract`/`abnk-pg-platform`/`abnk-bo`/`abnk-mweb`，up 后 3 min 全绿；Fineract 既有数据卷延续，Liquibase 账本核对非首迁） |
| `abnk-fineract` 实例计数 | ✅ `1`（平台栈零残留；compose 项目仅 `abnk-prod running(7)`） |
| `https://api.amazingbank.ai/actuator/health` | ✅ `{"status":"UP"}` |
| api 无 token 业务路径 | ✅ `401`（网关存活 + 鉴权生效双证据） |
| `https://app.amazingbank.ai/` | ✅ `200` |
| `https://bo.amazingbank.ai/` | ✅ `200` |
| `http://amazingbank.ai/` | ✅ `301` → https |
| 公网缺口剧本（VP3.5.8） | ✅ 退出码 0，段 4/4、断言 23/23——EXPIRED 客户 alice 经公网转账 HTTP 200（缺口在生产域名成立），Fineract 独立核对 −10/+10 对称 |
| 证据归档 | ✅ `abnk-system/artifacts/phaseP3/taskP3.5-prod-evidence.txt` + `gap-report-20261110-093911.json` |
