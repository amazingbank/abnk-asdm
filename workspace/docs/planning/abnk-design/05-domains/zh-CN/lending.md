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
| progressive-loan 复杂度（多 schedule 策略） | 配置面大，误配行为静默偏差 | ✅ Phase 1 已过（12 期等额本息一次配成） |
| COB 行为边界 | 分区并行下的顺序性假设 | ✅ Phase 1 单笔贷款观察通过 |
| Delinquency 分类规则与五级分类的口径差 | 映射不完整 | Phase 2 业务分析（需要信贷专家输入） |
| working-capital 模块成熟度 | 较新，行为面待探 | Phase 3 开项前专项 PoC |

## 5. Phase 1 实测回填（2026-10-25）

- [x] **对年对月对日 ✅ 原生支持**——12 期还款计划到期日 `2026-11-24 → 2027-10-24` **逐月对日**（放款日 10-24，末期恰在 12 个月后对日）。原判"偏差则用生成器扩展点"大概率不需要
- [x] **等额本息 ✅ 原生支持**——`amortizationType=Equal installments(1)`，每期 `totalDueForPeriod` 恒定 4395.79，利息递减（416.67→36.33）本金递增，标准年金形态；首期利息 416.67 = 50000×10%/12 精确吻合
- [x] **COB 触发 ✅**——`POST /v1/jobs/LOAN_COB/inline {"loanIds":[id]}` 200；未逾期贷款的 summary 无变化（预期内——日终对未逾期贷款无可见账务动作）
- [x] 贷款交易类型实测可见：Disbursement / **Accrual** / Repayment 三连
- ⚠️ **新观察（Phase 2 会计分析项）**：`Add Accrual Transactions` 作业对 accountingRule=NONE 的贷款也入账了 **2749.54 ≈ 全期利息总额**（4395.79×12 − 50000）的一次性 Accrual 交易——应计口径/时点与中国"按期计提"差异明显，启用会计后的分录行为必须专项分析
- [ ] LPR（浮息）：未测（需 `isLinkedToFloatingInterestRates` + 利率基准数据）
- [ ] 五级分类：未测（需制造逾期数据后触发 Loan Delinquency Classification）
- [ ] 还款计划查询方式（progressive 架构变化）：默认 `GET /loans/{id}` **不含** repaymentSchedule，须 `GET /loans/{id}?associations=all`
