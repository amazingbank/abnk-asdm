# 存款域（第一波产品线，ADR-006）

> **性质**：设计文档，三段式。事实锚点：savings 端点族 31 个（实测）；`fineract-savings` 模块。

---

## 1. 原生能力（实测端点族推断 + 作业清单）

| 能力 | 证据 |
|---|---|
| 产品定义（利率/期限/费用/锁定） | `savingsproducts` 端点族 + template |
| 账户生命周期 | 创建→approve→activate→（存取）→close（command 模式） |
| 存/取交易 | `transactions?command=deposit|withdrawal`（含 external-id 变体） |
| 计息 | Post Interest For Savings 作业（默认 active）+ Add Accrual For Savings（默认 inactive） |
| 利率周期 | 产品级利率区间机制（待 Phase 1 验证行为） |
| GSIM（集团储蓄） | `savingsaccounts/gsim` 端点族 |
| 费用/扣款 | charges 端点族 + Pay Due Savings Charges 作业 |
| 休眠 | Update Savings Dormant Accounts 作业 |
| 到期 | Update Deposit Accounts Maturity details 作业 |

## 2. 中国差距

| 差距 | 目标行为 | 初判落点 |
|---|---|---|
| **积数计息**（活期） | 按日累计余额积数 × 日利率，**不是按计提周期平均** | 产品配置先试；不足则 custom 模块扩展计提（`custom/abnk/product/savings`） |
| **按季结息**（活期） | 3/6/9/12 月固定结息日入账 | Post Interest 作业的调度 + 结息日历（Holiday/Calendar）组合 |
| **对年对月对日**（定存到期） | 2026-03-31 存 1 年 → 2027-03-31 到期（非 +365 天） | 到期计算行为待 Phase 1 实测；偏差则 custom |
| 提前支取计息 | 按活期利率 + 已存天数分段 | 产品配置（提前支取规则）+ 验证 |
| 存款保险 | 50 万限额标识与统计 | custom 辅助字段（datatable 或 report 模块） |
| 利息税 | 代扣代缴（如适用） | 交易后处理 custom 步骤 |

## 3. 定制方案

**判定顺序（对齐 `localization.md` 原则：配置 > 产品定义 > custom）**

1. Phase 1 用 API 建储蓄产品跑通存取与计息作业——**先获得原生行为基线**（含到期日、结息金额的实际计算方式）
2. 对照上表逐项 diff：可配置解决 → 固化进产品模板（`custom/abnk/product/savings` 模板化）
3. 配置不够的（积数计息最可能）→ custom 模块：计提逻辑挂在作业/business step 扩展点（acme 的 cob/job 范式）
4. 结息日历 → Holiday/Calendar 数据 + 作业调度配置

## 4. 验证设计（Phase 1/2 边界）

Phase 1 只验证**原生行为**（产品建立、存取、计息作业触发、到期日计算方式）——产出行为基线报告，作为差距判定的输入。**不做任何计息定制。**

## 5. 待验证清单

- [ ] 定存到期日计算：对年对月对日还是 +365 天？（决定 custom 与否）
- [ ] 活期计息基数：周期平均还是逐日？
- [ ] 计提频率可配置到日？
- [ ] 提前支取的利率切换行为
- [ ] 利息税处理位（交易层 or 后处理）
