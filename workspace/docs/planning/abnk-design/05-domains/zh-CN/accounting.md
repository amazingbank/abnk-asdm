# 会计域（★ L1 核心工作量）

> **性质**：设计文档，三段式（原生能力 / 中国差距 / 定制方案）。
> **事实锚点**：18 个会计 API 全部实测存在、数据全空（`00-baseline/api-surface.md` §6）。

---

## 1. 原生能力（实测）

| 能力 | 端点/机制 | 状态 |
|---|---|---|
| 科目管理 | `GET/POST/PUT/DELETE /v1/glaccounts` | API ✅ 数据空 |
| 复式分录 | `journalentries`（含 query/post） | API ✅ |
| 会计规则 | `accountingrules`（事件→借贷科目路由） | API ✅ |
| 业务活动映射 | `financialactivityaccounts`（业务语义→科目） | API ✅ |
| 科目启停（现金流/详细） | glaccounts 参数 | API ✅ |
| 期间结转 | 会计期末闭账（closure 端点族） | API 存在 |
| 辅助作业 | Update Trial Balance / Update Accounting Running Balances / Journal Entry Aggregation / Retained Earning Job（41 作业清单实测） | 部分默认 inactive |
| 产品级映射 | 产品定义里逐事件指定科目（存款/贷款产品） | 机制存在（Phase 1 验证） |

**关键事实：启用复式记账 = 纯数据工程（建 COA + 映射 + 规则），几乎不需要写代码。**

## 2. 中国差距

| 差距 | 说明 | 影响 |
|---|---|---|
| **COA 体系** | Fineract 自带通用模板不适配《企业会计准则》金融企业科目（1001/2001/…、贷款五级分类科目、减值科目） | **最大工作量**；每科目需 GL 端点创建或批量导入（`glaccounts` 有 uploadtemplate/downloadtemplate——批量通道） |
| 计提分录 | 利息计提/摊销的中国分录习惯（计提科目 vs 收入科目） | 映射 `financialactivityaccounts` + 作业（Add Accrual 系列）组合 |
| 减值/拨备 | 贷款损失准备（五级分类 → 拨备率） | Fineract 有 Loan Loss Provisioning 作业（实测在 41 作业中）——**口径映射待分析** |
| 会计期间 | 中国会计年度/季度结息日历 | closure + holiday 组合 |
| 报送映射 | 1104 报表口径要求科目可映射监管统计项 | COA 设计时**预留报送映射列**（`regulatory-reporting.md` 硬依赖） |

## 3. 定制方案（L1 落地路径）

```
第 1 步  COA 数据工程（纯数据，零代码）
         按《企业会计准则》设计科目全集 → glaccounts 批量导入
         （含报送映射列的旁注表——custom/abnk/report 的辅助表，不改核心）

第 2 步  业务活动映射
         financialactivityaccounts 全量映射（存款/贷款各业务事件）

第 3 步  产品级科目绑定
         第一波产品（储蓄+消费贷，ADR-006）逐事件绑定科目

第 4 步  计提与期末作业启用
         Add Accrual 系列 + Trial Balance/Running Balance 作业激活

第 5 步  验证
         12 步链路重跑（phase-1-validation 扩展版）→ 每步查 journalentries
         断言分录正确（借/贷科目+金额）
```

**代码落点极少**：仅报送映射旁注表（`custom/abnk/report`，走 custom-changelog）。**COA 的维护是数据治理问题**——版本化（导出/导入模板）+ 变更评审，不进代码。

## 4. 风险与待验证

| 项 | 状态 |
|---|---|
| 科目层级深度是否满足中国习惯 | 待 Phase 1 用真实 COA 验证 |
| 跨产品共用科目的规则冲突 | accountingrules 的优先级机制待验证 |
| 减值口径（五级分类 → 拨备）与 Fineract 拨备作业的映射 | Phase 2 业务分析 |
| 多租户 COA 差异（ADR-004） | 每租户独立初始化（分库天然支持），模板参数化 |

## 5. 工作量判断（供排期）

- COA 设计（业务侧主导）：**主要瓶颈**，需要会计专业输入
- 落地（批量导入+映射+作业启用）：工程量小（API 通道齐备）
- 验证：扩展 12 步脚本的分录断言，中等
