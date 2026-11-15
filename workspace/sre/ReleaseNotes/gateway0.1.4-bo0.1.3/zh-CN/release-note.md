# ABNK Gateway 0.1.4 + BO 0.1.3 — Release Notes

**版本**：`gateway 0.1.4` + `bo 0.1.3`（镜像 tag，双 patch 递增）
**日期**：2026-11-13
**状态**：✅ 已完成
**分支**：`main`（abnk-system）

## 缺陷背景（发版动因）

前序发版（gateway 0.1.3 + bo 0.1.2，见 `../gateway0.1.2-bo0.1.2/`）的 UI 验证过程中发现两处遗留缺陷：

1. **错误响应缺 CORS 头（gateway）**：三个 WebFilter 的错误写入器（`BearerTokenFilter` 401、`BoRouteFilter` 403/404、`BlacklistFilter` 403/404）都短路在 SCG `CorsWebFilter`（order LOWEST）之前——错误响应不携带 `Access-Control-Allow-Origin`。浏览器跨域读取不到错误体 → SPA 把会话过期（JWT TTL 15 分钟）/鉴权失败一律误报成 **"Network unreachable"**。线上实测：带 Origin 的 401 响应无任何 Access-Control 头。
2. **LoanOpsPage 静默失败（bo）**：与本次已修的 `ClientListPage` 完全同型——`listLoans().then(...).finally(...)` 无 catch，请求失败静默渲染空表 "No data"。

另附结论澄清：此前怀疑的「过期 token 网关仍返回 200」**不成立**——该 200 实为 OPTIONS 预检直通（W3C 规范预检不携带凭据，网关设计如此）；`JwtService` 过期分支校验无缺陷（单测在册；篡改 token 线上实测 401）。

## 变更内容（基线 `bd3cf62`，1 commit，上基线 `15186cb`）

| 项 | 文件 | 说明 |
|----|------|------|
| 根因修复 | `BearerTokenFilter` / `BoRouteFilter` / `BlacklistFilter` | 错误写入器回显请求 Origin + `allow-credentials: true`（口径同 globalcors） |
| 回归测试 | `BoRouteFilterTest` | 新增 `unauthorizedResponseCarriesCorsHeaders`（全链路 401 + Origin → 断言 ACAO/ACAC 回显） |
| 防御修复 | `LoanOpsPage.tsx` | load 链补 catch + Alert 错误提示 |
| 版本 bump | `gradle.properties` / `package.json` | gateway `0.1.3→0.1.4`、bo `0.1.2→0.1.3` |

**验证**：gateway 全套 **59 单测通过**；bo `npm run build`（tsc + vite）通过。

## 部署命令（Phase B 在服务器执行）

1. 服务器 `git pull`（HEAD 核对 = `bd3cf62`）
2. 构建推送：gateway 0.1.4（仓库根上下文）+ bo 0.1.3（`--build-arg ABNK_DATA_LOCALE=en-us`）
3. `.env` 更新 `ABNK_GATEWAY_IMAGE` / `ABNK_BO_IMAGE`
4. 单服务滚动 `up -d abnk-gateway abnk-bo` + **`docker restart abnk-nginx`**（铁律）
5. 验证：401 带 Origin 响应含 ACAO；全栈回归；BO 两页正常

## 环境就绪检查
| 检查项 | 状态 |
|--------|------|
| 敏感信息审计（Step 0） | ✅ |
| 仓库干净已推送（HEAD `bd3cf62`） | ✅ |
| 服务器（SSH/Docker/磁盘 95G） | ✅ |
| 七容器 | ✅ 全部 healthy |

## 执行进度跟踪
- [x] ✅ Phase A 完成（审计/版本/就绪）
- [x] ✅ Phase B 完成（用户确认发版）

## 实测验证结果（Step 8）

| 检查项 | 结果 |
|--------|------|
| 401 + Origin（无效 token 打 bo 面） | **ACAO 回显 `https://bo.amazingbank.ai` + ACAC true** ✅（修复前：无任何 Access-Control 头） |
| 401 + Origin（无效 token 打对客面） | ACAO 回显 `https://app.amazingbank.ai` + ACAC true ✅ |
| 预检 OPTIONS（bo 面） | 200 + ACAO ✅（0.1.3 修复保持） |
| 线上 BO 走查（bo 0.1.3） | 登录 → 客户列表 Wang/Li/Zhao 数据 ✅；贷款页 Zhao POC-C 贷款 + 40 天逾期分档（ABNK_POC_OD）✅ 截图 `verify-loanops-0.1.4.png`；页面零 JS 错误 ✅ |
| 全栈回归（api/app/bo/website） | health UP / 全 200 ✅ |
| 七容器 | 全部 healthy ✅（gateway 0.1.4 `sha256:f7e3efe6…` / bo 0.1.3 `sha256:85e61b7d…`） |
| 滚动纪律 | `docker restart abnk-nginx` 已执行 ✅ |

**会话过期 UX 生效机理**（JWT TTL 15 分钟到期后）：401 现可被浏览器跨域读取 → axios `toApiError` 映射 `auth.sessionExpired` → 页面 Alert 显示 "Your session has expired — please sign in again"（不再误报 Network unreachable）。
