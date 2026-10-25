# Phase 1 实施方案：原生能力端到端验证

> **目标**：不写任何后端代码，用纯 API 把 Fineract 原生业务链路完整跑通一遍，形成 ABNK 的第一条可回归验证基线。
> **依据**：全部端点已实测核实（`00-baseline/api-surface.md`）；业务载体 = ADR-006 第一波产品线（储蓄+消费贷）。

---

## 1. 出口判据（全部满足即 Phase 1 完成）

| # | 判据 | 验证方式 | 状态（2026-10-25） |
|---|---|---|---|
| 1 | 全链路 12 步脚本一次跑通，零 5xx | 脚本退出码 0 | ✅ **通过**（报告 `abnk-system/artifacts/phase1/report-1025094135.json`） |
| 2 | 每步业务断言通过（余额/状态/分录） | 脚本内置断言 | ✅ **通过**（含余额=8000、状态机、13 期计划、负向关户断言） |
| 3 | COB 触发后产生可观测变化（应计/逾期分类） | API 查询对比 | ✅ **部分**——储蓄利息入账可见（0.33）；贷款未逾期无 summary 变化（预期内）；逾期分类未验证（需逾期数据） |
| 4 | 脚本入库为可重复执行的回归资产 | 存放于 `abnk-system/scripts/phase1/`，CI 可跑 | ✅ **入库**（monorepo，见 ADR：所有交付物进 abnk-system） |
| 5 | 200 个官方 E2E feature 的运行方式已验证 | E2E runner 实跑一次 | ⬜ **未做**（Phase 1 收尾项） |

## 2. 前置状态（2026-10-25 更新）

- Phase 0 环境可用（`00-baseline/environment.md`）
- 业务日期已启用（`c_configuration` id=44 enabled）；运行中已推进至 BUSINESS_DATE=2026-10-25 / COB_DATE=2026-10-24
- 租户时区已改 `Asia/Shanghai`（tenants 表直改，即时生效）
- 会计链路**暂不验证**（GL 全空，见 §6）

## 3. 验证脚本设计（12 步）

统一封装：curl 超时 / 租户头 / Basic 认证 / 断言（期望 HTTP 码 + JSON 路径取值）。

**第一段：基础数据（机构与人员）**

| 步 | 操作 | 端点 | 关键断言 |
|---|---|---|---|
| 1 | 建办公室 | `POST /v1/offices`（parentId=1 Head Office） | 返回 resourceId；`GET /v1/offices` 列表 +1 |
| 2 | 建职员 | `POST /v1/staff`（挂到新办公室） | resourceId |

**第二段：客户与储蓄（ADR-006 储蓄线）**

| 步 | 操作 | 端点 | 关键断言 |
|---|---|---|---|
| 3 | 建客户 | `POST /v1/clients`（officeId=新办公室，提交日期=业务日期） | resourceId |
| 4 | 激活客户 | `POST /v1/clients/{id}?command=activate` | status: active |
| 5 | 建储蓄产品 | `POST /v1/savingsproducts`（利率/币种 CNY 测试） | resourceId |
| 6 | 开储蓄账户 + 审批 + 激活 | `POST /v1/savingsaccounts` → `?command=approve` → `?command=activate` | status: active |
| 7 | 存款→取款 | `POST .../transactions?command=deposit` → `?command=withdrawal` | 余额 = 存-取（查询账户详情断言） |

**第三段：贷款（ADR-006 消费贷线）**

| 步 | 操作 | 端点 | 关键断言 |
|---|---|---|---|
| 8 | 建贷款产品 + 贷款申请 + 审批 + 发放 | `POST /v1/loanproducts` → `POST /v1/loans` → `?command=approve` → `?command=disburse` | status: active；还款计划存在 |
| 9 | 部分还款 | `POST /v1/loans/{id}/transactions?command=repayment` | 交易入账，余额下降 |

**第四段：日终与收尾**

| 步 | 操作 | 端点 | 关键断言 |
|---|---|---|---|
| 10 | 推进业务日期 | `POST /v1/businessdate`（type=BUSINESS_DATE，日期+1，联动 COB_DATE） | GET 回读变化 |
| 11 | 触发日终 | `POST /v1/jobs/LOAN_COB/inline`，body `{"loanIds":[贷款ID]}` | HTTP 200；**只认 `LOAN_COB`**（三套命名见基线文档） |
| 12 | 查日终效果 + 关户 | 查贷款详情（delinquency/应计变化）→ `POST /v1/clients/{id}?command=close` | 关户校验（有余额的账户应阻止关户——负向断言） |

## 4. 已知坑（写脚本时直接规避）

| 坑 | 规避 |
|---|---|
| COB 作业名 | inline 只认 `LOAN_COB` / `WC_LOAN_COB` |
| businessdate 需 locale | body 固定带 `"locale":"en","dateFormat":"yyyy-MM-dd"` |
| 业务日期未启用报 403 | 前置 `PUT /v1/configurations/44 {"enabled":true}`（幂等，脚本开头执行） |
| 日期前后关系 | 客户/账户的提交日期不得晚于业务日期；COB 后业务日期须≥COB 日期 |
| 自签证书 | curl `-k` |
| 租户头缺失 4xx | 封装层统一注入 |
| 贷款产品配置复杂 | progressive-loan 的产品参数多——先用 `GET /v1/loanproducts/template` 拿模板再改 |

## 5. 官方 E2E 复用（判据 5）

- 200 个 feature 在 `fineract-e2e-tests-runner`；COB 的官方写法参照 `fineract-e2e-tests-core/.../InlineCOBStepDef.java:60`
- 首次只验证"能跑起来 + 出报告"，**不追求全绿**（部分 feature 依赖邮件/SMS 等外部桩）
- 通过后把它定位为 ABNK 的上游回归门禁；我们的 12 步脚本定位为业务冒烟（更快、更贴近 ABNK 链路）

## 6. 范围外（显式排除）

- **会计分录验证**：GL/规则/映射全空（实测），复式记账验证推迟到 L1 科目表落地后（`05-domains/accounting.md`）
- 多租户：按 ADR-004 阶段一以 default 租户运行
- 前端：纯 API 验证（ADR-005 Phase 1 不建前端）
- 任何定制代码：本阶段零后端开发

## 7. 交付物

1. `abnk-smoke.sh`（或 Python）12 步验证脚本 + 断言输出
2. 脚本产出的数据快照（首次基线，供回归对比）
3. E2E runner 运行记录（含报告位置与通过率）
4. 本文档勾选出口判据并归档
