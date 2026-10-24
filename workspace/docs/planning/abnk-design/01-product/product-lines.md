# 产品线规划（依 ADR-006 展开）

> **性质**：设计文档。决策已定（ADR-006，2026-10-25），本文展开产品明细与范围影响。

---

## 1. 三波次总表

| 波次 | 产品线 | 阶段 | Fineract 依赖模块（已核实存在） |
|---|---|---|---|
| 第一波 | 储蓄 + 消费贷 | Phase 1–2 | `fineract-savings`、`fineract-loan` + `fineract-progressive-loan` |
| 第二波 | 经营贷 | Phase 3+ | `fineract-working-capital-loan`（含 delinquency 周期） |
| 远期 | 供应链金融 / 财富管理 | 未排期 | 待评估 `fineract-investor` |

## 2. 第一波产品明细（Phase 1–2 范围）

### 储蓄
| 产品 | 关键配置 | 本地化要点 |
|---|---|---|
| 活期 | 利率周期、计提频率 | 积数计息、按季结息（`05-domains/savings.md`） |
| 整存整取（3M/6M/1Y/2Y/3Y） | 期限、到期处理 | 对年对月对日到期、提前支取计息规则 |

### 消费贷
| 产品 | 关键配置 | 本地化要点 |
|---|---|---|
| 个人消费贷（等额本息） | schedule 生成器、还款日 | 等额本息计划、LPR 定价（`05-domains/lending.md`） |
| 信用卡类循环额度（可选） | 循环额度 | 验证 progressive-loan 支持度后定 |

## 3. 第二波产品明细（Phase 3+）

| 产品 | 依赖 | 风险点 |
|---|---|---|
| 个人经营贷 | working-capital-loan | 循环额度行为、delinquency 分期生成较新，需专项验证 |
| 小微企业经营贷 | 同上 + 担保机制 | 担保品管理需评估 Fineract collateral 能力 |

## 4. 范围影响（本文档存在的意义）

产品线**直接裁剪**以下工作的深度：

| 工作项 | 第一波范围 | 第二波增量 |
|---|---|---|
| 会计科目表（`05-domains/accounting.md`） | 储蓄+消费贷科目全集 | 经营贷专属科目（贴现/担保类） |
| 计息规则 | 活期积数、定存对年对月对日、贷款按期 | 循环额度按日计提 |
| 监管报送 | 个人存贷款口径 | 小微企业贷款专项报送（1104 部分） |
| 产品模板（`custom/abnk/product/`） | 第一波两套 | 经营贷一套 |

## 5. 验证载体

Phase 1 的 12 步链路（`06-evolution/phase-1-validation.md`）= 第一波产品的端到端最小集。**产品模板在 Phase 2 才固化进 `custom/abnk/product/`**，Phase 1 用 API 直接创建（验证原生行为）。
