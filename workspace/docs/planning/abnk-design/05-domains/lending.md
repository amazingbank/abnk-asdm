# 贷款域（第一波消费贷 + 第二波经营贷，ADR-006）

> **性质**：设计文档，三段式。事实锚点：贷款端点族 99 个、progressive-loan/working-capital 模块、7 种交易处理器、COB 已实测可触发（`00-baseline/`）。

---

## 1. 原生能力（实测）

| 能力 | 证据 |
|---|---|
| 贷款产品 + 申请 + 审批 + 发放 | `loanproducts` / `loans` command 族（approve/disburse） |
| **渐进式贷款引擎** | `fineract-progressive-loan` + **独立可嵌入还款计划生成器模块**（schedule 策略可换） |
| 交易处理器 | 7 种内置（官方 `loan-transaction-processor.adoc`），可自定义扩展（acme 已示范 repayment schedule processor） |
| 还款/提前还款 | `transactions?command=repayment` + 提前还款参数族 |
| 日终 | **Loan COB（inline 已实测 200）** + Business Step 扩展点（acme cob 范式） |
| 应计 | Add Accrual Transactions 系列（3 个作业，2 个默认 active） |
| 逾期 | Update Loan Arrears Ageing + **Loan Delinquency Classification**（均默认 active） |
| 减值 | Generate Loan Loss Provisioning 作业 |
| 高级还款分配 | advanced-payment-allocation-rules（内部端点族实测存在） |
| 贷款锁/审计 | place-lock / audit 内部端点（排障用） |
| 经营贷（第二波） | `fineract-working-capital-loan` + delinquency 周期生成内部端点 |

## 2. 中国差距

| 差距 | 目标行为 | 初判落点 |
|---|---|---|
| **对年对月对日**（还款日） | 分期到期日按月对日，非 +30 天滚动 | schedule 生成器行为实测 → 偏差则用可嵌入生成器扩展点 |
| 还款计划形态 | 等额本息/等额本金（消费贷） | 生成器策略配置（Phase 1 验证原生支持度） |
| **LPR 定价** | 基准 LPR + 加点，重定价日调整 | 利率周期机制 + custom 定价服务（LPR 数据源是外围） |
| 提前还款违约金 | 按剩余本金比例/固定 | 费用（charges）机制映射 |
| 逾期罚息口径 | 罚息利率、复利口径 | 利率周期 + arrears 配置映射 |
| 五级分类 | 逾期天数 → 正常/关注/次级/可疑/损失 | **Delinquency Classification 作业的规则映射**（分类映射是数据工程） |
| 结息/账单日 | 消费贷按账单周期 | progressive 配置验证 |
| 经营贷循环额度 | 随借随还、额度恢复 | working-capital-loan 原生目标场景（第二波专项验证） |

## 3. 定制方案

```
Phase 1（原生基线）
  建消费贷产品（等额本息形态）→ 发放 → 还款 → 触发 LOAN_COB →
  查 arrears/delinquency/accrual 的实际行为 → 产出行为基线报告

Phase 2（差距落地，判定顺序：产品配置 > 生成器扩展点 > custom 模块）
  1. 对年对月对日：实测生成器行为，偏差 → 用 embeddable-schedule-generator 扩展点
  2. 五级分类：Delinquency 分类的规则映射（数据工程）
  3. LPR 定价：外围定价服务（事件驱动）+ 利率周期调整
  4. 违约金/罚息：charges + 利率周期配置

Phase 3+（第二波）
  working-capital-loan 专项验证（循环额度、delinquency 周期、随借随还）
  → 差距分析单独一轮
```

**代码落点预估**：schedule 生成器扩展（如需）+ LPR 外围服务；五级分类与罚息多为配置/数据。

## 4. 风险与待验证

| 项 | 风险 | 验证时点 |
|---|---|---|
| progressive-loan 复杂度（多 schedule 策略） | 配置面大，误配行为静默偏差 | Phase 1 用 template 端点起步 |
| COB 行为边界 | 分区并行下的顺序性假设 | Phase 1 单笔贷款观察 |
| Delinquency 分类规则与五级分类的口径差 | 映射不完整 | Phase 2 业务分析（需要信贷专家输入） |
| working-capital 模块成熟度 | 较新，行为面待探 | Phase 3 开项前专项 PoC |
