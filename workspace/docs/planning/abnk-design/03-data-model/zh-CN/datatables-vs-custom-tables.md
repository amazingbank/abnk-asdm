# 字段扩展决策树（datatable vs custom 表）

> **性质**：设计规范。机制事实：datatables 为 Fineract 原生机制；custom 表走 ADR-002 独立迁移。

---

## 1. 决策树

```
需要一个新字段/新数据？
├─ 弱语义（展示/分类/外部引用，无强约束、无跨实体 JOIN）？
│   └─ 是 → Fineract Datatable（原生，零代码，API 即可建）
│
├─ 强语义（唯一约束/外键/参与业务规则计算）？
│   └─ 是 → custom 模块 + db/custom-changelog 独立表
│
├─ 需要改核心表已有列（m_client 加 NOT NULL 列）？
│   └─ 红线 R2 → 禁止。改为 custom 表 + external id 关联，或 datatable
│
└─ 需要新领域实体（如"证件审核记录"整套）？
    └─ custom 模块（含服务层 + 表 + changelog + 测试）
```

## 2. 两种机制对比

| 维度 | Datatable | custom 表 |
|---|---|---|
| 建立方式 | API 调用（零代码） | 模块 + changelog |
| 约束强度 | 弱（挂到实体，字段级校验有限） | 完整 SQL 约束/外键/索引 |
| 业务逻辑 | 无（纯数据） | 服务层任意实现 |
| 与核心联动 | 只读展示为主（部分视图可关联） | 可参与 command/business step |
| 升级风险 | 零（原生机制） | 低（独立 changelog） |
| 适用 | 证件辅助信息、渠道来源标记、备注 | 证照唯一性、担保品、审批流实例 |

## 3. 规范

1. **datatable 命名**：`abnk_<entity>_<purpose>`（避免与上游/其他 fork 混用）
2. **custom 表命名**：`abnk_<domain>_<entity>`，主键规范与核心一致（BIGINT），关联核心一律走 **external id 或 resourceId**，不建对核心表的外键（核心表结构上游可变，外键会锁死升级）
3. 迁移纪律：custom 表变更只追加 changelog 文件，**不修改已发布的历史 changelog**
4. 每个 datatable 建立时同步登记到本文档附表（Phase 2 起维护）

## 4. 已知场景的预判（Phase 1–2 陆续遇到）

| 场景 | 决策 |
|---|---|
| 客户证件号码唯一性（身份证） | **custom 表**（唯一索引必须）→ `custom/abnk/localization/identity` |
| 客户经理归属标记 | datatable 即可 |
| 存款产品渠道销售标记 | datatable（挂产品） |
| 贷款审批流实例 | custom 表 + 服务层（Phase 3，网关层编排的落库） |
| 监管报送到岸数据 | custom 表（`report` 类别） |
