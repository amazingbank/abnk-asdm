# 任务 P3.2 Backoffice 接线 —— 端到端走查记录（VP3.2.3 / VP3.2.4）

- **日期**：2026-11-09
- **载体**：Vite dev server（`VITE_ABNK_API_BASE=/ npm run dev`，:6203，agent-browser 语义树驱动）
- **模式**：remote（`src/api/dataSource.ts` 按 `VITE_ABNK_API_BASE` 判定；同源相对路径经 vite dev proxy `/bo` → 网关）
- **链路**：backoffice dev server（:6203）→ vite proxy → ABNK 网关（:8080，bootRun，`ABNK_USERS_FILE=gateway_users.local-prodform.json`）→ 生产形态 Fineract 栈（:8081）+ abnk-pg-prod（:5433）
- **口令**：admin 演示口令经 `.github-private/kbank-poc/gateway-demo-passwords.json`（local-prodform 节）注入走查，不落本文
- **截图**：`artifacts/phaseP3/screenshots/bo-01~05`（登录后列表 / 客户详情 / 证照编辑后 / 恢复后 / 贷款运营）

## 接线实现要点（架构口径归档）

| # | 决策 | 依据 |
|---|---|---|
| 1 | 适配层做 raw→契约组装（列表证照状态列 N+1 并发补齐、详情聚合 4 端点、PUT 后回读映射） | P2.5 定案：`/bo/api/**` 为**全量转发面**（网关不聚合），P2.6 契约 diff 白名单排除转发族 6 路径（容差声明）——组装职责落在消费端适配层 |
| 2 | Fineract PUT identifiers 必填的 `locale`/`dateFormat` 由适配层注入（契约面不暴露、转发面不注入） | P0.2 VP0.2.1 / P2.5 VP2.5.3 实测口径；PUT 响应为 resourceId 变更回执，回读 `GET .../identifiers` 后映射返回 |
| 3 | 证照到期 / 逾期天数推导基准 = Fineract 业务日期（`GET /bo/api/v1/businessdate`，BUSINESS_DATE=2027-03-29，会话级缓存） | 与网关 `/me/identity` 服务端推导同源同算法（ISO 字典序比较 / 日期差） |
| 4 | 定期账户 `maturityDate`/`interestRate` 经 `GET /bo/api/v1/fixeddepositaccounts/{id}` 补齐 | `/clients/{id}/accounts` 投影无 maturityDate（P3.2 接线探查实测） |
| 5 | JWT sessionStorage 持久化（`abnk-bo-jwt`，登出清除） | 与 AuthProvider session 持久化（刷新不掉线）口径一致；页面层零改动 |
| 6 | 逾期分档（`delinquencyClassification`）不在 loans 列表投影中——对 inArrears 贷款并发补拉 `GET /loans/{id}` 详情 | 详情端点 `delinquencyRange.classification`（P0.3 客户 C 分档口径） |

## 改动清单（新建/修改，对 P3.1 基线 commit `94aa0a7`）

- **新建**：`src/api/remote/`（`generatedClient.ts` 生成 client 适配 + token/错误映射 + `rawGet` 转发端点访问；`fineractRaw.ts` raw 形态接口 + 日期归一化 + 业务日期缓存；`remoteAuth.ts` / `remoteClient.ts` / `remoteLoan.ts` 三 repository 实现）
- **新建**：`src/api/dataSource.ts`（mock/remote 切换点）、`src/vite-env.d.ts`（`VITE_ABNK_API_BASE` env 类型声明）
- **修改**：`src/api/index.ts`（装配点移交 dataSource，类型出口不变——页面 import 路径零变化）、`vite.config.ts`（dev proxy `/bo` → `http://localhost:8080`，`ABNK_GW_BASE` 可覆盖）
- **零改动断言（VP3.2.2）**：`src/pages/` + `src/api/repositories/` 对基线 `94aa0a7` diff = **0 行**

## VP3.2.1 编译门槛（双跑口径）

- 接线前基线 + 接线后复验两轮，`npm run typecheck && npm run lint && npm run build` 退出码均 0、零错误
- build 产物 `✓ built in 3.57s`（dist 备料，P3.4 Docker 化沿用）

## 端到端走查（五步剧本 + 双断言）

### 第 1 步：admin 登录（网关 PBKDF2 凭据 + internal JWT）
- `POST /bo/login`（经 vite proxy 同源转发）→ 200，JWT（channel=internal，TTL 900s）注入 Bearer
- 界面横幅显示「运营管理员」→ 跳转客户列表
- 截图 `bo-01-login.png`

### 第 2 步：客户列表（真实 Fineract 数据 ≥3 户）
- 表格 **29 户**（`totalFilteredRecords=29`），种子客户 28/29/30 可见
- 证照状态列（适配层 N+1 补齐 + 业务日期推导）：28 王 POC-A=**已过期** 2020-01-01 / 29 李 POC-B=有效 2099-12-31 / 30 赵 POC-C=有效 2099-12-31 / 无证照客户=「未登记」
- 截图 `bo-01-login.png`（登录后首屏即列表）

### 第 3 步：客户 A（28）详情
- 客户信息：外部编号 ABNK-POC-A-1107104347 / 状态 Active / Head Office
- 证照：Passport · ID-A-1107104347 · 签发 2015-01-01 · **到期 2020-01-01** · 记录状态 ACTIVE · 到期状态（推导）**已过期**
- 账户：活期 000000011（**¥9,329.82**）+ 000000012（**¥700.00**）——真实 Fineract 余额（含 P3.1 走查转账后状态）；无定期、无贷款
- 截图 `bo-02-client-detail.png`

### 第 4 步：证照编辑 `expiry_date` → 2099-12-31 → 保存 → 界面回显
- `PUT /bo/api/v1/clients/28/identifiers/8`（载荷 expiryDate=2099-12-31 + locale/dateFormat 适配层注入）→ 200
- 界面回显：到期日 **2099-12-31**，到期状态（推导）翻转为**有效**，message.success「证照已更新（到期日 2099-12-31）」
- 截图 `bo-03-identifier-updated.png`

**改断言（Fineract 侧独立回读，直连 :8081 + 租户头/Basic）**：
`GET /clients/28/identifiers` → identifierId=8, **expiryDate=2099-12-31** —— 与界面一致 ✓ **PASS**

### 第 5 步：配对恢复（种子态保持——P3.3 依赖过期种子）
- 界面改回 `2020-01-01` → 保存 → 回显：到期日 **2020-01-01**，推导状态回**已过期**
- 截图 `bo-04-identifier-restored.png`

**恢复断言（双通道交叉验证）**：
- Fineract 直连回读：identifierId=8, **expiryDate=2020-01-01** ✓ **PASS**
- 对客通道 alice `GET /abnk/api/v1/me/identity` → `{"status":"EXPIRED","expiryDate":"2020-01-01"}` —— 种子过期态经 bo 写 + 对客读双向确认恢复 ✓（沿用 P2.5.3 口径）

### 附加复验：贷款运营页（remote loan 数据层，交付物完整性）
- 6 笔真实贷款全量加载；客户 C 贷款 6：`Active · 逾期 40 天（ABNK_POC_OD）`——与 mock 快照口径**逐值一致**（业务日期 2027-03-29 − 逾期起算 2027-02-17 = 40 天，分档自详情端点补拉）
- 探查/冒烟贷款（无 delinquency bucket 产品）分档显示「—」、逾期天数推导正确（111/112 天）
- 截图 `bo-05-loan-ops.png`

## 结论

VP3.2.3 五步走查无空格：admin 登录 → 客户列表（29 户真实数据）→ 客户 A 详情（真实余额/证照）→ 证照编辑 2099-12-31 → 保存回显（推导状态翻转），**改 + 恢复双断言 PASS**（Fineract 回读 + 对客通道交叉验证）；页面代码零改动（VP3.2.2 断言 0 行）——运营视角端到端闭环成立（旅程 Step 1/7 基线前提达成）。
