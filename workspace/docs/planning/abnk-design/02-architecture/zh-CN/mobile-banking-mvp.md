# 渠道层 MVP 设计：手机银行（Flutter）+ 对客 API + Backoffice

> **性质**：设计文档（Phase 3 渠道层开项前细化）。技术栈已定：SCG 网关 + React 管理后台 + **Flutter 手机银行**（ADR-008 / 待拍板 ADR-009）。
> **范围**：第一波产品线（储蓄 + 消费贷，ADR-006）+ KBank POC 的合规演示主线（证照过期拦截）。
> **事实锚点**：`00-baseline/api-surface.md`（603 端点/存款 31/贷款 99/客户 34）、`05-domains/savings.md`、`05-domains/lending.md`、`01-product/personas.md`。

---

## 1. 范围与假设

**一句话目标**：让「个人客户」在手机上完成第一波产品的核心业务操作，同时把 KBank POC 的合规主线（证照过期拦截）做成端到端可演示；配套一个管理后台（Backoffice）让「运营管理员 + 风控专员」能配置与监控这套业务。

**明确纳入 MVP 的业务**：储蓄（活期 + 整存整取定期）、个人消费贷（等额本息）、本人账户资金往来。

**明确不做（MVP 边界）**：

| 不做 | 原因 |
|---|---|
| 第三方转账 / 支付 / 代发 | 依赖网联/银联（L4 外围，Phase 4，`payments.md`） |
| 企业网银 | ADR-005 第三套，远期 |
| 经营贷（循环额度） | 第二波（ADR-006，Phase 3+） |
| 财富 / 供应链金融 | 远期，不进详细设计 |
| 生产级安全加固 / 高可用 | POC 范围外（`kbank-poc-demo-scenario.md` §7） |

---

## 2. 移动端 App（Flutter）最小功能设计

### 2.1 架构形态

```
Flutter App（个人客户）
   │  OAuth2/OIDC（Keycloak，授权码 + PKCE）
   ▼
SCG 网关（租户注入 / 脱敏 / 限流 / 证照拦截预检）
   │  Fineract-Platform-TenantId 注入
   ▼
Apache Fineract（L0 核心，603 端点）
```

- 客户端 **永不直连 8443**（ADR-005 铁律）。
- Dart client 从网关 OpenAPI 生成（`channels/mobile-banking/openapi-generated/`），不手写 API 类型。
- 网关按 OIDC subject 解析出当前客户（client），客户端不携带、也不可见 Fineract 内部 resourceId。

### 2.2 功能清单（按优先级分档）

> P0 = MVP/POC 必做；P1 = 紧随其后；P2 = 明确延后。

| # | 模块 | 功能 | 档位 | 底层 Fineract / 说明 |
|---|---|---|---|---|
| M1 | 身份认证 | OIDC 登录（授权码+PKCE）、Token 刷新、登出 | P0 | 网关 + Keycloak |
| M2 | 身份认证 | 生物识别解锁（指纹/面容） | P0 | `local_auth`；解锁本地令牌，非远端鉴权 |
| M3 | 身份认证 | 自绘安全键盘（金额/密码输入） | P0 | Flutter 自绘组件，防录屏/防系统输入法 |
| M4 | 账户 | 账户总览（活期/定期余额与可用余额） | P0 | `GET /v1/clients/{id}/accounts` + savingsaccounts 明细 |
| M5 | 账户 | 单账户详情（利率/期限/到期日/结息方式） | P0 | `GET /v1/savingsaccounts/{id}` |
| M6 | 账户 | 交易明细（存取/利息入账，含 runningBalance） | P0 | `GET /v1/savingsaccounts/{id}/transactions/search`（本 HEAD 无朴素列表 GET——实测口径见 Part02 P0.2 VP0.2.4） |
| M7 | 储蓄 | 本人账户间转账（活期→活期） | P0 | `deposit` + `withdrawal` 组合（或网关聚合） |
| M8 | 储蓄 | 定期开户（3M/6M/1Y/2Y/3Y，对年对月对日到期） | P0 | `POST /v1/savingsaccounts`（定存产品） |
| M9 | 储蓄 | 提前支取（定期→活期） | P0 | `withdrawal`（提前支取规则由产品配置） |
| M10 | 贷款 | 消费贷产品展示（利率/期限/额度） | P0 | `GET /v1/loanproducts`（对客收敛字段） |
| M11 | 贷款 | 贷款申请（金额/期限/还款日，等额本息） | P0 | `POST /v1/loans` |
| M12 | 贷款 | 申请进度 / 审批状态 | P0 | `GET /v1/loans/{id}`（status 对象） |
| M13 | 贷款 | 还款计划（对月对日，逐期本息） | P0 | `GET /v1/loans/{id}?associations=all`（repaymentSchedule） |
| M14 | 贷款 | 还款 / 提前还款 | P0 | `POST /v1/loans/{id}/transactions?command=repayment` |
| M15 | 合规（POC 主线） | 证照状态展示（有效/临期/过期） | P0 | `custom/abnk/identity` + 网关 `/me/identity` |
| M16 | 合规（POC 主线） | 证照过期交易拦截（客户端预检 + 服务端强制） | P0 | 见 §5；客户端只做提示，服务端是权威 |
| M17 | 合规 | 证照更新申请（Re-KYC 提交） | P1 | 客户提交 → 柜面/后台复核（Phase 3+） |
| M18 | 通用 | 中英多语言、暖色设计系统 | P0 | 沿用官网 tokens（Oxanium + Noto Sans SC） |
| M19 | 通知 | 交易/结息/还款提醒推送 | P1 | 依赖通知服务（L4，Phase 4，`event-bus`） |
| M20 | 通用 | 深色模式 / 无障碍 | P2 | 设计系统层 |

### 2.3 关键页面/流程（MVP 主路径）

```
登录（OIDC + 生物识别 + 安全键盘）
  → 首页（账户总览 + 证照状态横幅）
      ├─ 储蓄账户 → 交易明细 / 账户间转账 / 定期开户 / 提前支取
      ├─ 消费贷 → 产品列表 → 申请 → 进度 → 还款计划 → 还款
      └─ 我的 → 客户资料（脱敏）/ 证照有效期 / Re-KYC 申请
```

**证照过期拦截的用户侧表现**（KBank POC 演示点）：
- 首页常驻横幅：`证件已过期，请更新`（来自 `/me/identity`）。
- 任何涉及「新交易」的入口（转账/定期开户/贷款申请）在客户端预检即置灰并提示原因；**真正拦截在服务端**——网关或 custom 模块对过期客户的新交易返回 403/422，保证「漏改一处」也不放行。

---

## 3. 后台 API（网关对客收敛面）

> 网关职责承接 `02-architecture/api-gateway.md`：路由 / 鉴权 / 租户注入 / 字段收敛脱敏 / 限流 / 审计 / 简单聚合。**含审批流的业务编排放外围服务，不进网关。**

### 3.1 对客 API 清单（手机银行可达子集）

> 对外路径 `/abnk/api/v1/...`；底层 Fineract 路径 `/fineract-provider/api/v1/...`（客户端不可见）。

| 移动功能 | 网关对外 API | 底层 Fineract | 收敛/脱敏要点 |
|---|---|---|---|
| 当前客户 | `GET /me` | `GET /v1/clients/{id}` | 姓名/证件号按 `personas.md` 脱敏 |
| 证照状态 | `GET /me/identity` | custom identity + client datatable | 只返回状态与有效期，不返回证件原件 |
| 账户总览 | `GET /me/accounts` | `GET /v1/clients/{id}/accounts`（+ savingsaccounts 聚合） | 只返回本人账户；脱敏账号尾号 |
| 账户详情 | `GET /accounts/{id}` | `GET /v1/savingsaccounts/{id}` | 收敛字段 |
| 交易明细 | `GET /accounts/{id}/transactions` | `GET /v1/savingsaccounts/{id}/transactions/search` | runningBalance 保留 |
| 账户间转账 | `POST /accounts/{id}/transfer` | `deposit` + `withdrawal`（网关聚合，幂等） | 服务端校验同客户 |
| 定期开户 | `POST /savings` | `POST /v1/savingsaccounts`（定存产品） | 产品由网关按渠道白名单收敛 |
| 提前支取 | `POST /accounts/{id}/withdraw` | `POST .../transactions?command=withdrawal` | 走提前支取规则 |
| 贷款产品 | `GET /loan-products` | `GET /v1/loanproducts` | 收敛对客字段（隐藏内部配置） |
| 贷款申请 | `POST /loans` | `POST /v1/loans` | 客户端不可选内部参数 |
| 贷款详情/进度 | `GET /loans/{id}` | `GET /v1/loans/{id}` | 状态对象规范化 |
| 还款计划 | `GET /loans/{id}/schedule` | `GET /v1/loans/{id}?associations=all` | 只取 repaymentSchedule |
| 还款 | `POST /loans/{id}/repayment` | `POST /v1/loans/{id}/transactions?command=repayment` | 金额字段 `transactionAmount` |

### 3.2 网关鉴权与当前客户解析

- 外部渠道 OAuth2/OIDC（Keycloak），授权码 + PKCE；网关持有 Token 校验与租户注入职责。
- **OIDC subject → Fineract client 的映射**：网关维护映射（custom 表或 external-id 反查），不向客户端暴露内部 client id；多租户按登录上下文注入 `Fineract-Platform-TenantId`。

### 3.3 生产黑名单（对客不可达，承接 api-gateway.md §3）

- `/v1/internal/*`（21 端点）、`/v1/jobs/*`、`/v1/configurations/*`、`/fineract.json` —— 仅管理后台经内部通道可达。

---

## 4. Backoffice（管理后台）最小功能设计

> 承接 ADR-005「管理后台先行」；React + Ant Design Pro（ADR-008）。用户：运营管理员、风控专员（`personas.md`）。

### 4.1 功能清单（按优先级分档）

| # | 模块 | 功能 | 档位 | 底层 Fineract |
|---|---|---|---|---|
| B1 | 机构 | 租户 / Office 树 / Staff 管理 | P0 | `offices` / `staff` / 租户管理 |
| B2 | 客户 | 客户查询、资料维护、证照状态查看 | P0 | `clients` + custom identity |
| B3 | 客户 | 证照过期客户清单 + 拦截规则配置（POC） | P0 | custom identity + 配置 |
| B4 | 产品 | 储蓄产品定义（活期积数/按季结息、定存期限） | P0 | `savingsproducts` |
| B5 | 产品 | 贷款产品定义（等额本息、还款日、利率） | P0 | `loanproducts` |
| B6 | 贷款 | 贷款审批 + 放款 | P0 | `loans?command=approve/disburse` |
| B7 | 账户 | 账户查询、冻结/解冻、休眠 | P1 | `savingsaccounts` command 族 |
| B8 | 作业 | 日终 COB 触发、作业状态（内部通道） | P0 | `jobs`（含 `LOAN_COB/inline`） |
| B9 | 配置 | 业务日期（business date）、系统配置 | P0 | `businessdate` / `configurations` |
| B10 | 会计 | 科目表/分录/会计规则（L1 重建后可见） | P1 | `glaccounts` / `journalentries` / `accountingrules` |
| B11 | 风控 | 逾期/五级分类监控、黑名单 | P1 | `loans`（delinquency）+ 风控配置 |
| B12 | 报送 | EAST / 1104 报表（Phase 4 起） | P2 | `reports` + 报送框架（`regulatory-reporting.md`） |

### 4.2 渠道映射（承接 api-gateway.md §5）

| 前端 | 网关入口 | 鉴权 | 可达面 |
|---|---|---|---|
| 管理后台 | 内部域名 | 内部 SSO | 全量（含 jobs/configurations/会计） |
| 手机银行 | 公网域名 | OAuth2/OIDC | 收敛后的对客子集（§3） |

> **关键差异**：作业管理（B8）、业务日期（B9）、会计（B10）只在内部通道可达；对客通道对这些路径一律 404/403。

---

## 5. 证照过期拦截（KBank POC 主线）——Fineract 落点

> 这是 KBank POC 的演示故事（`kbank-poc-demo-scenario.md` §3）。设计要点：**触及核心客户域，但改动面受 ADR-001/002 约束**——不重写核心，定制走 `custom/abnk/`。

### 5.1 数据落点

- 客户证件（类型/号码/有效期）落到客户扩展数据：优先 Fineract client **datatable**（ADR-002 之外零侵入）；如需强校验/索引，再上 `custom/abnk/identity` 的 custom-changelog 表（**永不改核心表**）。
- 有效期字段 + 状态（VALID / EXPIRING_SOON / EXPIRED）由 custom 模块计算，写入 datatable 或 custom 表。

### 5.2 拦截点（服务端权威）

| 拦截点 | 落点 | 说明 |
|---|---|---|
| 储蓄存取（M7/M8/M9） | custom 校验 + 网关预检 | 新交易入口 |
| 贷款申请/放款/还款（M11/M14） | custom 校验 + 网关预检 | 新交易入口 |
| 账户间转账（M7） | 同上 | 资金移动 |
| 查询类（明细/详情） | 不拦截 | 只读不阻断，但首页横幅提示 |

**实现策略（对齐 `customization-strategy.md`）**：
1. 拦截逻辑挂在 custom 模块的 **Business Step / 交易校验扩展点**（acme 的 cob/job 范式），在交易 Command 写入前校验证件有效期。
2. 网关层做**预检**（Java 过滤器，查 custom 表/datatable），对过期客户的新交易直接快速失败，减轻核心压力并保证「前端漏拦截也不放行」。
3. 客户端只做**体验层提示**（置灰 + 横幅），不作为安全边界。

### 5.3 影响分析演示价值

这条拦截横跨储蓄、贷款、账务、客户四个域，是 POC「阶段 2 影响分析 A/B 对比」的理想载体：改动涉及 client datatable、custom 模块、网关过滤器、多个 transaction 端点，AI 需给出精确影响面清单，可审计。

---

## 6. Fineract 能力映射与缺口汇总

| 需求 | Fineract 原生 | 缺口/定制 | 落点 |
|---|---|---|---|
| 活期积数计息 + 按季结息 | ✅ 实测原生（`interestCalculationType=dailybalance` + `interestPostingPeriodType=Quarterly`） | 无 | 产品配置（`custom/abnk/product/savings` 模板化） |
| 定存对年对月对日到期 | ⚠️ 待测（Phase 2 初专项用例） | 偏差则 custom | `savings.md` §5 |
| 等额本息 + 对月对日还款 | ✅ 实测原生（12 期逐月对日） | 无 | `loanproducts` 配置 |
| LPR 定价（浮息） | ⚠️ 未测 | 外围定价服务（L4，Phase 4） | `lending.md` §3 |
| 五级分类 | ⚠️ Delinquency 分类规则映射 | 数据工程（Phase 2） | `lending.md` §3 |
| 证照过期拦截 | ❌ 无此概念 | **custom/abnk/identity**（Phase 2 第一个模块） | 本设计 §5 |
| 提前还款违约金 | ⚠️ charges 机制映射 | 产品配置 | `lending.md` §2 |
| 账户间转账 | 原生有 deposit/withdrawal，无「本人账户间转账」单端点 | 网关聚合（§3.1） | L3 网关 |

---

## 7. KBank POC 对齐

| POC 阶段 | 本设计的对应交付 |
|---|---|
| 阶段 0 私有化底座 | 环境不变（Fineract 8443 + PG 5432 + 网关 + Keycloak） |
| 阶段 2 影响分析 | 证照拦截跨域改动 = 影响分析 A/B 对比的演示载体 |
| 阶段 4 编码执行 | Flutter App + 网关收敛 + custom/abnk/identity = AI 编码执行产物 |
| 阶段 5 测试门禁 | 手机银行 UI E2E + 12 步冒烟 + 200 官方 E2E 回归 |
| 阶段 6 部署运营 | 手机端演示走真实 Fineract 数据，非 mock |
| 阶段 7 知识回流 | 本设计文档 + ADR-009 即知识资产 |

**演示种子数据**：含「过期证照客户」与「逾期贷款客户」（`kbank-poc-demo-scenario.md` §6），用于现场演示拦截与风控视图。

---

## 8. 里程碑（对齐 roadmap）

| 阶段 | 交付 |
|---|---|
| Phase 2（当前） | `custom/abnk/identity` 证照校验（第一个定制模块）；定存到期行为实测 |
| Phase 3 | SCG 网关 MVP（路由+鉴权+租户注入）+ 管理后台（B1–B9）+ Flutter 手机银行 P0（M1–M16） |
| Phase 3 末 | 柜面接入；证照拦截端到端闭环（客户端提示 → 网关预检 → custom 强制） |
| Phase 4 | 通知推送（M19）、LPR 定价、Re-KYC 流程（M17）、报送框架 |

---

## 9. 待业务输入项（Phase 3 开项前必须）

- [ ] 手机银行各页面脱敏口径（姓名/账号/证件号的展示规则）
- [ ] 定期提前支取计息规则确认（活期利率 + 已存天数分段）
- [ ] 消费贷额度/期限/利率档位（产品参数表）
- [ ] 证照过期拦截的宽限期（EXPIRING_SOON 阈值：如到期前 30 天提醒）
- [ ] Backoffice 角色权限矩阵（映射 Fineract permission 编码，`personas.md` 待细化项）
