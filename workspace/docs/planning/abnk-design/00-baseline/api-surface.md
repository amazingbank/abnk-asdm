# API 面与实测坑

> **性质**：实测事实记录。数据来自 2026-10-24/25 对运行中实例（603 路径 OpenAPI spec + curl 实测）。
> **用途**：Phase 1 验证方案（`06-evolution/phase-1-validation.md`）的事实依据；渠道层设计的输入。

---

## 1. 总量

**603 个路径 / 968 个操作**（`GET /fineract-provider/fineract.json`，1.5 MB）。

⚠️ **取 spec 用静态端点**：`/fineract-provider/fineract.json`（resolve 任务生成）。springdoc 动态端点 `/api-docs` **实测 500，不可用**。

## 2. 业务链路端点分布

| 业务域 | 端点数 | 关键路径 |
|---|---|---|
| 客户 | 34 | `POST /v1/clients`、`POST /v1/clients/{id}?command=activate` / `close` |
| 存款 | 31 | `POST /v1/savingsproducts`、`POST /v1/savingsaccounts`、交易 `POST .../transactions?command=deposit\|withdrawal` |
| 贷款 | 99 | `POST /v1/loanproducts`、`POST /v1/loans`、`approve` / `disburse` |
| 交易/还款 | 63 | `POST /v1/loans/{id}/transactions?command=repayment` |
| 批处理作业 | 12 | 见下节 |
| 会计/总账 | 18 | `glaccounts` / `journalentries` / `accountingrules` / `financialactivityaccounts` |
| 业务日期 | 2 | `GET/POST /v1/businessdate` |
| 批量请求 | 1 | `POST /v1/batches` |
| 内部 API | 21 | `/v1/internal/*`（审计、COB 辅助、工作日贷款） |

**结论（Phase 1 依据）：开户→存款→贷款→还款→COB→关户全链路 100% 可 API 完成，无需写后端代码。**

## 3. 日终 COB —— 三套作业名（最大的坑）

| 用途 | 名称 | 出处 |
|---|---|---|
| **inline 触发（唯一可用）** | `LOAN_COB` / `WC_LOAN_COB` | E2E 测试 `InlineCOBStepDef.java:60` |
| 调度作业 shortName | `LA_ECOB` / `WC_COB` | `GET /v1/jobs` |
| 内部 businessJob 名 | `LOAN_CLOSE_OF_BUSINESS` / `WORKING_CAPITAL_LOAN_CLOSE_OF_BUSINESS` | `GET /v1/jobs/names` |

实测：

```bash
POST /api/v1/jobs/LOAN_COB/inline
Content-Type: application/json
{"loanIds": []}          # 可指定贷款范围
→ HTTP 200
```

用 `LA_ECOB` 或 `LOAN_CLOSE_OF_BUSINESS` 调 inline → 500 `Inline Job is not found by job name`。**OpenAPI 文档没写这个映射**——不看 E2E 测试代码猜不到。

## 4. 业务日期 —— 两个前置条件

```bash
# ① 先启用（默认 403 "Business date functionality is not enabled"）
PUT /api/v1/configurations/44
{"enabled": true}          # c_configuration 表 enable-business-date

# ② 设置（locale 必传，漏了报 400）
POST /api/v1/businessdate
{"type": "BUSINESS_DATE|COB_DATE", "date": "2026-10-24", "locale": "en", "dateFormat": "yyyy-MM-dd"}
```

- 设 `BUSINESS_DATE` 会联动推进 `COB_DATE`（`enable-automatic-cob-date-adjustment` 默认 true）。
- 当前环境已设置：BUSINESS_DATE=2026-10-24，COB_DATE=2026-10-23。

## 5. 调度作业（41 个，`GET /v1/jobs`）

关键作业与默认状态：

| 作业 | shortName | 默认 |
|---|---|---|
| Loan COB | LA_ECOB | **False** |
| Working Capital Loan COB | WC_COB | False |
| Increase COB Date by 1 day | BDT_COB1 | False |
| Increase Business Date by 1 day | BDT_INC1 | False |
| Recalculate Interest For Loans | — | True |
| Add Accrual Transactions | ACC_AATR | True |
| Update Loan Arrears Ageing | LA_ARAG | True |
| Loan Delinquency Classification | — | True |
| Post Interest For Savings | — | True |
| Execute All Dirty Jobs | — | True |

**含义：日终链路默认不跑，Phase 1 验证必须手工触发（inline）或激活作业。**

**调度作业可 API 触发（Phase 1 实测，2026-10-25）**：

```bash
POST /api/v1/jobs/{jobId}?command=executeJob    # operationId: executeJob
→ HTTP 202（异步执行，约 20s 内完成）
```

已实测成功触发 4 个作业：Post Interest For Savings（id=6，**利息入账可见**）、Add Accrual Transactions（11）、Update Loan Arrears Ageing（2）、Loan Delinquency Classification（35）。**这回答了"不等待 cron 如何验证计息/日终"——冒烟与集成测试的核心手段。**

## 6. 会计模块 —— API 齐备但数据全空（L1 核心工作量的实证）

```
GET /v1/glaccounts                → []
GET /v1/accountingrules           → []
GET /v1/financialactivityaccounts → []
```

复式记账的**端点、规则引擎、映射机制都存在**，但开箱一份数据都没有。启用完整会计 = 按《企业会计准则》重建科目表（详见 `05-domains/accounting.md`）。

## 7. 其他实测事实

- `GET /api-docs` → 500（springdoc 动态端点损坏；用静态 `/fineract.json`）
- `GET /v1/jobs` 在构建产物损坏时 500（症状与处置见 `environment.md` §7）
- `/v1/internal/*` 共 21 个端点：审计查询（client/loan/transaction audit）、COB 快进、贷款锁、配置覆写——**面向运维/诊断，生产网关层不应暴露**
- E2E 测试的 COB 写法（`InlineCOBStepDef.java:60`）是作业名映射的唯一可靠出处

---

*核对方法：路径分布来自 OpenAPI spec 解析（603 路径逐条分类）；三套命名、businessdate 前置、会计空数据均经 curl 实测（含对照组验证）。*
