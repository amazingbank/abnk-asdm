# ABNK Gateway 0.1.2/0.1.3 + BO 0.1.2 — Release Notes

**版本**：`gateway 0.1.2`（中途升 0.1.3）+ `bo 0.1.2`（镜像 tag，双 patch 递增）
**日期**：2026-11-13
**状态**：✅ 已完成（发版中追加 0.1.3——见「发版中修复」节；后续改进项转 gateway 0.1.4 / bo 0.1.3 预部署）
**分支**：`main`（abnk-system）

## 缺陷背景（发版动因）

线上 BO（`https://bo.amazingbank.ai`）客户列表显示 **"No data"**。根因链（已完整定位并本地复现）：

1. 浏览器跨域请求 `https://api.amazingbank.ai/bo/api/v1/clients` 前先发 **CORS 预检 OPTIONS**（不带 Bearer 头——W3C 规范如此）；
2. `BearerTokenFilter`(-100) 对 OPTIONS 直通（P3.1 设计），但 `BoRouteFilter`(-80) **漏了同款直通**——通道属性为空 → 403 `internal channel requires internal channel token`，早于 SCG CorsWebFilter 应答；
3. 预检 403 → 浏览器拦截真实 GET → 前端 `ClientListPage.load()` `try/finally` **无 catch** → 静默渲染空表 "No data"。

**该缺陷随 gateway 0.1.1 发布即存在**（`part03/seed-en/bo-online-english-clients.png` 截图实证当时已 No data）——当时验证只覆盖 API 层（curl 无预检），UI 层静默失败漏检。curl 直连（无预检）与带合法 token 的请求均正常，后端数据无损。

## 变更内容

| 项 | 文件 | 说明 |
|----|------|------|
| 根因修复 | `BoRouteFilter.java` | OPTIONS 预检直通（与 BearerTokenFilter 同口径），交 SCG CorsWebFilter 应答 |
| 回归测试 | `BoRouteFilterTest.java` | 新增 `corsPreflightPassesThroughWithoutChannel`；全套通过 ✅ |
| 防御修复 | `ClientListPage.tsx` | `load()` 补 catch + antd Alert 错误提示（失败不再静默空表） |
| 版本 bump | `gradle.properties` / `package.json` | gateway `0.1.1→0.1.2`、bo `0.1.1→0.1.2`（Iron Rule 4 不复用） |

**基线**：abnk-system `0968236`（已推送 origin/main；上版本基线 `62dcb89`，1 commit）
**验证**：gateway `BoRouteFilterTest` 全套通过；bo `npm run build`（tsc + vite）通过

## 部署命令（Phase B 在服务器执行）

1. 服务器 `git pull`（HEAD 核对 = `0968236`）
2. 服务端构建 + push：
   `docker build -f channels/gateway/Dockerfile -t ghcr.io/amazingbank/abnk-gateway:0.1.2 .`
   `docker build -f channels/backoffice/Dockerfile --build-arg ABNK_DATA_LOCALE=en-us -t ghcr.io/amazingbank/abnk-bo:0.1.2 .`
   （双镜像 push ghcr 公共包）
3. `~/deploy/.env` 更新 `ABNK_GATEWAY_IMAGE` / `ABNK_BO_IMAGE` 两行
4. 单服务滚动：`up -d abnk-gateway abnk-bo`（其余五容器零感知）
5. **`docker restart abnk-nginx`**（2026-11-12 铁律：upstream IP 缓存）
6. 验证：预检 OPTIONS 200、线上 BO 登录后客户列表显示 Wang/Li/Zhao 数据、全栈七容器 healthy

## 发版中修复：gateway 0.1.3（第二重根因——ACAO 双头）

0.1.2 上线后 UI 验证发现：预检已 200，但真实 GET 仍被浏览器拦截——curl 实测响应中
`Access-Control-Allow-Origin` **出现两次**（网关 SCG CorsWebFilter + Fineract 下游
Spring Security CORS 各加一套；浏览器 Fetch 规范该头仅允许单值，重复即整请求失败）。
修复（`15186cb`）：bo-channel 路由加
`DedupeResponseHeader=Access-Control-Allow-Origin Access-Control-Allow-Credentials Access-Control-Expose-Headers, RETAIN_FIRST`
（实测头序：网关先加、下游后拷入，RETAIN_FIRST 保网关权威一套）。
本地 mock 下游端到端验证（ACAO 恰一次/预检 200/透传正常）后构建部署 0.1.3。

## 实测验证结果（Step 8）

| 检查项 | 结果 |
|--------|------|
| 预检 `OPTIONS /bo/api/v1/clients` | 403 → **200** ✅ |
| GET ACAO 头计数 | 2 → **1** ✅ |
| 线上 BO 登录 → 客户列表 | **Wang/Li/Zhao POC-* 数据完整显示**（证照 Expired/Valid/Valid）✅ 截图 `verify-clients-online-0.1.3.png` |
| 线上 BO 贷款运营页 | Zhao POC-C 贷款 + 40 天逾期分档（ABNK_POC_OD）✅ |
| 全栈回归（api/app/bo/website） | 全 200 / health UP ✅ |
| 七容器 | 全部 healthy ✅ |
| 附带发现 | 错误响应（401/403/404）缺 CORS 头（短路在 CorsWebFilter 前）——会话过期被 SPA 误报 "Network unreachable"；已修复待发（见 gateway 0.1.4 / bo 0.1.3 预部署 note）。另：此前怀疑的"过期 token 返回 200"实为 OPTIONS 预检直通（W3C 规范预检不带凭据）——**网关过期校验无缺陷**（JwtService 过期分支单测在册，篡改 token 线上实测 401） |

## 执行进度跟踪
- [x] ✅ Step 0：敏感信息审计（6 节全过）
- [x] ✅ Step 1：仓库干净已推送（abnk-system HEAD: `0968236` → 发版中追加 `15186cb`）
- [x] ✅ Step 2：版本确定（gateway 0.1.2 → 发版中升 0.1.3 / bo 0.1.2）
- [x] ✅ Step 3：服务器就绪（SSH/Docker 29.9.2/磁盘 96G 可用/仓库在位）
- [x] ✅ Step 5：服务器 git pull + HEAD 核对（`0968236` / `15186cb` 均一致）
- [x] ✅ Step 6：docker build + push（gateway 0.1.2 `sha256:d92abcc6…` → 0.1.3 `sha256:042f7d6c…`；bo 0.1.2 `sha256:1b7aef38…`）
- [x] ✅ Step 7：.env 更新 + 单服务滚动 up + restart abnk-nginx（两次均执行）
- [x] ✅ Step 8：部署验证（见上方实测结果表）
- [x] ✅ Step 9：Release Note 回填 + commit

## 遗留（转后续发版）
- **gateway 0.1.4 / bo 0.1.3（已提交 `bd3cf62`，待用户确认发版）**：三过滤器错误响应补 CORS 回显（会话过期 UX）；LoanOpsPage 补 catch + Alert（同 ClientListPage 修法）
- nginx resolver 永久化（upstream IP 缓存根治）——挂账不变
