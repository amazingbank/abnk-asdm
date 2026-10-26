# 架构决策记录（ADR）

> ADR 记录**已拍板**的架构决策及其后果。一旦写入即生效，推翻需新开一条并标注 `Superseded by`。
> 命名：`NNN-短名.md`，序号递增不复用。

## 索引

| # | 决策 | 状态 | 日期 |
|---|---|---|---|
| [001](001-no-rewrite.md) | 不重写 Fineract，核心账务直接复用 | ✅ Accepted | 2026-10-25 |
| [002](002-custom-modules.md) | 全部定制走 `custom/abnk/` 模块（显式接受 PoC 风险） | ✅ Accepted | 2026-10-25 |
| [003](003-postgresql-baseline.md) | PostgreSQL 单一数据库宿主，root/postgres 三方对齐 | ✅ Accepted | 2026-10-25 |
| [004](004-multi-tenancy.md) | 采用 Fineract 多租户架构（分阶段落地） | ✅ Accepted | 2026-10-25 |
| [005](005-frontend-strategy.md) | 前端自建三套（柜面/网银手机/管理后台） | ✅ Accepted | 2026-10-25 |
| [006](006-product-lines.md) | 产品线：储蓄+消费贷先行，经营贷后续 | ✅ Accepted | 2026-10-25 |
| [007](007-xinchuang-compatibility.md) | 信创兼容策略：主线开源 + 兼容层（四原则 + 认证矩阵） | ✅ Accepted | 2026-10-26 |
| [008](008-channel-tech-stack.md) | 渠道层技术栈：SCG 网关 + React 前端 + 移动混合 App | ✅ Accepted | 2026-10-26 |

## 模板

```markdown
# ADR-NNN：<决策标题>

- 状态：Proposed | Accepted | Superseded by ADR-XXX
- 日期：YYYY-MM-DD
- 决策人：<who>

## 背景
<为什么现在必须做这个决策；相关事实（引用 00-baseline 的出处）>

## 决策
<用一句话说清做了什么选择>

## 理由
<为什么是这个选项而不是备选；关键论据>

## 后果
### 正面
### 负面 / 风险与缓解
### 必须遵守的衍生约束
```

## 维护规则

- 新决策先 Proposed，拍板后改 Accepted 并填写日期
- 引用事实必须来自 `00-baseline/`（已核实），不得引用未验证的推断
- 每条决策的"衍生约束"是下游文档（02–05 板块）的硬前提
