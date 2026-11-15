# ADR-001：不重写 Fineract，核心账务直接复用

- 状态：Accepted
- 日期：2026-10-25
- 决策人：ABNK 项目负责人

## 背景

ABNK 需要一套完整的核心银行系统（客户/存款/贷款/会计/批处理）。自建 vs 基于开源，是第一个架构级决策。事实依据见 `00-baseline/fineract-codebase.md`：7100 个 Java 文件、473 个 Liquibase changelog、200 个 E2E feature、成熟的多租户与命令架构、progressive-loan 贷款引擎十余年演进。

## 决策

**Apache Fineract（fork `amazingbank/fineract`，develop 分支）作为 ABNK 的核心账务引擎，不自研、不重写、不大改内核。**

## 理由

1. 核心账务（复式记账、计提、日终、逾期分类、多租户隔离）是高复杂度、低差异化的基础设施——全球数字银行已反复验证 Fineract 这条路
2. 473 个 changelog 背后的领域经验（利息计算边界、冲账、账务期间）自研团队 3-5 年内补不齐
3. ABNK 的差异化价值在**本地化、渠道体验、外围集成、数据智能**四件事（见 ADR-006），不在核心账务
4. 200 个 E2E feature 是免费的回归基线

## 后果

### 正面
- 团队精力集中在真正产生差异的层
- 上游社区持续免费获得功能演进与安全修复

### 负面 / 风险与缓解
- 受制于上游路线（如某功能上游不做）→ 走 ADR-002 的 custom 模块路径，不动内核
- 升级依赖 fork 维护纪律 → 季度级 rebase（`02-architecture/release-strategy.md`）

### 必须遵守的衍生约束
- **任何改动不得触碰 Fineract 核心模块的源码与 changelog**（唯一例外见 ADR-002 的 provider 依赖行）
- 升级风险评估时，把"上游是否接受我们的需求"当作第一选项
