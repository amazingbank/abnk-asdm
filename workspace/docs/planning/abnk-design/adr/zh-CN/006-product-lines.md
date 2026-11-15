# ADR-006：产品线——储蓄+消费贷先行，经营贷后续

- 状态：Accepted
- 日期：2026-10-25
- 决策人：ABNK 项目负责人

## 背景

产品线决定 L1 本地化的深度与范围（会计科目表、计息规则、报送口径都随之变化），是必须先于详细设计拍板的决策。备选范围：储蓄 / 消费贷 / 经营贷 / 供应链金融。事实依据：`00-baseline/fineract-codebase.md`（savings/loan/progressive-loan/working-capital-loan 模块齐备）、`api-surface.md`（存款 31 端点、贷款 99 端点、COB 已实测可触发）。

## 决策

**产品线按三波推进：**

| 波次 | 产品线 | 阶段 | 依赖的 Fineract 能力（均已核实存在） |
|---|---|---|---|
| 第一波 | **储蓄 + 消费贷** | Phase 1–2 | savings 模块、loan + progressive-loan |
| 第二波 | **经营贷** | Phase 3+ | working-capital-loan 模块（含 delinquency 周期生成） |
| 远期 | 供应链金融 / 财富管理 | 未排期 | 需评估 investor 模块 + 外围建设 |

第一波 = Phase 1 端到端验证的业务载体（开户→存款→贷款→还款→COB→关户）。

## 理由

1. 储蓄+消费贷构成零售基本盘，覆盖客户全生命周期，且**对应 Fineract 最成熟的两个模块**（savings 与 progressive-loan）——风险最低、原生能力验证最充分
2. 经营贷（working-capital-loan）模块较新、行为更复杂（循环额度、delinquency 分期），放第二波可避免 Phase 1 同时验证两条复杂贷款线
3. 计息/逾期/科目表等本地化深水区在储蓄与消费贷上完成一次，经营贷复用大部分成果

## 后果

### 正面
- L1 本地化范围收敛：科目表与计息规则先按储蓄+消费贷设计，经营贷做增量
- Phase 1 验证链路与第一波产品线完全对齐，一次验证两用

### 负面 / 风险与缓解
- 经营贷客户早期无法服务 → 明示为路线图排期问题，非架构限制
- 后续加产品线时 COA/报送口径要增量扩展 → 科目表设计预留扩展位（`05-domains/accounting.md`）

### 必须遵守的衍生约束
- `05-domains/` 的差距分析按本 ADR 的波次排序优先级：savings/lending 先行，经营贷差异在 lending.md 单列一节
- 产品定义（product 模板）按波次进 `custom/abnk/product/`
- 供应链/财富管理**不进当前任何设计文档的详细设计**，只在 roadmap 留位
