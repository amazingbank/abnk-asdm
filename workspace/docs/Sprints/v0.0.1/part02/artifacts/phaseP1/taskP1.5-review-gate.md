# 任务 P1.5 契约冻结与原型评审 —— 评审关口归档（VP1.5.3 材料）

> **时点**：2026-11-07 · Sprint v0.0.1 Part02 Phase P1 · Phase 出口铁门
> **契约**：`channels/shared/api-contract/openapi.yaml`（OpenAPI 3.1.0，18 paths / 19 operations）
> **评审记录**：`channels/shared/api-contract/REVIEW.md`（数据来源矩阵 / 脱敏 / 幂等补偿 / 生成器判定）
> **VP1.5.1 / VP1.5.2**：已通过（实测记录见 Phase P1 文档勾选行）

---

## 1. 三端同屏截图（VP1.5.3 评审材料一）

**同屏拼接图**：`artifacts/phaseP1/screenshots/p1.5-three-terminal.png`（2200×720，官网 + 手机银行 + Backoffice，暖色设计 tokens 三端同源——P1.2 `design-tokens.json` DIFF: 0 口径）

| 端 | 截图 | 来源与口径 |
|---|---|---|
| 官网（设计语言基线） | `artifacts/phaseP1/screenshots/site-01-home.png`（1440×900） | P1.5 现取：`channels/website/dist` 静态服务（SPA fallback，:6291 临时）+ playwright-cli；首页 hero（A Bank. And a Blueprint.） |
| 手机银行（Flutter mock 原型） | `artifacts/phaseP1/screenshots/web-02-home.png`（390×844） | P1.3 VP1.3.4 web 载体走查存量截图：首页账户总览（客户 A / Alice Green，¥10,000 活期 + ¥5,000） |
| Backoffice（React mock 原型） | `artifacts/phaseP1/screenshots/bo-02-client-list.png`（1440×900） | P1.4 VP1.4.4 走查存量截图：客户列表三客户 + 证照状态列（红/绿标） |

> 官网截图过程归档：首跑 404 根因 = SPA i18n 路由（`/` → `/en-us/`）无静态 fallback，换带 fallback 的简易服务后正常渲染（nginx.conf 同口径）。

## 2. 契约端点清单（VP1.5.3 评审材料二，19 operations）

### 2.1 对客通道（手机银行消费，11）

| # | 端点 | 语义 | 消费 repository 方法 |
|---|---|---|---|
| 1 | `POST /login` | 客户登录（简化登录 JWT，D2） | mobile `AuthRepository.login` |
| 2 | `GET /abnk/api/v1/me` | 当前客户资料（脱敏） | （P2.3 MeController；`UserProfile` 模型） |
| 3 | `GET /abnk/api/v1/me/identity` | 证照信息（只读三态） | mobile `IdentityRepository.getIdentity` |
| 4 | `GET /abnk/api/v1/me/accounts` | 账户总览（活期+定期） | mobile `AccountRepository.getAccounts` |
| 5 | `GET /abnk/api/v1/accounts/{id}/transactions` | 交易明细（runningBalance） | mobile `AccountRepository.getTransactions` |
| 6 | `POST /abnk/api/v1/accounts/{id}/transfer` | 转账聚合（幂等+补偿） | mobile `AccountRepository.transfer` |
| 7 | `POST /abnk/api/v1/savings` | 定期开户 | mobile `AccountRepository.openFixedDeposit` |
| 8 | `GET /abnk/api/v1/loan-products` | 消费贷产品清单 | mobile `LoanRepository.getLoanProducts` |
| 9 | `GET /abnk/api/v1/fixed-deposit-products` | 定期产品清单 | mobile `LoanRepository.getFixedDepositProducts` |
| 10 | `POST /abnk/api/v1/loans` | 贷款申请 | mobile `LoanRepository.applyLoan` |
| 11 | `GET /abnk/api/v1/loans/{id}` | 贷款详情（收敛） | （P2.3 LoanController；计划显式列出） |

### 2.2 内部通道（Backoffice 消费，8）

| # | 端点 | 语义 | 消费 repository 方法 |
|---|---|---|---|
| 12 | `POST /bo/login` | 运营登录（internal channel） | bo `AuthRepository.login` |
| 13 | `GET /bo/api/v1/clients` | 客户列表（证照状态列） | bo `ClientRepository.listClients` |
| 14 | `GET /bo/api/v1/clients/{id}` | 客户详情（全量聚合） | bo `ClientRepository.getClientDetail` |
| 15 | `GET /bo/api/v1/clients/{id}/identifiers` | 证照清单 | （计划显式列出） |
| 16 | `GET /bo/api/v1/clients/{id}/identifiers/{identifierId}` | 单证照详情 | （计划显式列出；P0.2 回读实测） |
| 17 | `PUT /bo/api/v1/clients/{id}/identifiers/{identifierId}` | 证照更新（旅程 Step 7） | bo `ClientRepository.updateClientIdentifier` |
| 18 | `GET /bo/api/v1/loans` | 贷款运营列表（逾期分档） | bo `LoanRepository.listLoans` |
| 19 | `POST /bo/api/v1/loans/{id}` | 贷款 command 族转发（approve/disburse） | （POC 演示增量预埋；基线按钮 disabled） |

覆盖核对（VP1.5.2）：两端 16 方法全覆盖 + logout ×2 客户端本地声明；**GAP = 无**。

## 3. 走查记录索引（VP1.5.3 评审材料三）

| 资产 | 路径 | 状态 |
|---|---|---|
| P1.3 手机银行 web 载体走查（7 页面 + 9 截图） | `artifacts/phaseP1/taskP1.3-web-walkthrough.md` | ✅ |
| P1.3 证据归档（VP1.3.1–VP1.3.8 全文） | `artifacts/phaseP1/taskP1.3-evidence.txt` | ✅ |
| P1.3 iOS / Android 模拟器走查截图（各 4 张 + 图标 2 张） | `artifacts/phaseP1/screenshots/ios-*.png` / `android-*.png` | ✅ |
| P1.4 Backoffice 五步走查（4 节 + console 0 红） | `artifacts/phaseP1/taskP1.4-bo-walkthrough.md` | ✅ |
| P1.4 走查截图（6 张：login/列表/详情/证照编辑/贷款运营） | `artifacts/phaseP1/screenshots/bo-*.png` | ✅ |
| P1.2 设计 tokens 一致性证据（DIFF: 0） | `artifacts/phaseP1/taskP1.2-tokens-evidence.txt` | ✅ |
| P1.5 契约评审记录（来源矩阵/幂等补偿/生成器判定） | `channels/shared/api-contract/REVIEW.md` | ✅ |
| P1.5 三端同屏拼接图 | `artifacts/phaseP1/screenshots/p1.5-three-terminal.png` | ✅（本归档现取） |

## 4. 评审要点提示（供裁决参考）

1. **端点命名**：定期开户为 `POST /abnk/api/v1/savings`（P1.5 计划与 P2.3 SavingsController 原文口径）；`POST /savings` 语义在 REVIEW.md §2.1 声明（转发 `POST /fixeddepositaccounts`）。
2. **3.1 vs 3.0**：生成器试生成双通过，保持 OpenAPI 3.1.0；dart-dio beta 残留风险 + 语义无损降级口径见 REVIEW.md §4。
3. **幂等 / 补偿**：转账 `externalId` 幂等键 + 两步编排 + 冲正 502 口径见 REVIEW.md §2.1（P2.4 实现依据）。
4. **基线零拦截**：identity 纯读三态；无任何证照拦截行为（D1 口径）。

## 5. VP1.5.3 裁决记录（待填）

| 项 | 记录 |
|---|---|
| 提交评审时点 | 2026-11-07 |
| 用户裁决 | ✅ **「确认冻结」**（2026-11-07） |
| 冻结生效时点 | **2026-11-07**——`channels/shared/api-contract/openapi.yaml` 进入冻结态，P2/P3 以此为唯一契约事实源 |

---

*状态同步：本归档与 Phase P1 文档任务 P1.5 及 Plan.md 进度概要一致；执行规则遵循 toolset action `abnk-doc-review.md` rubric。*
