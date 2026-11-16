---
section: governance
status: published
locale: zh-CN
date: 2026-11-16
---
# 治理与开放——十次拍板如何塑造了现在的形态

> 本篇不重写 ADR 内容——ADR 原文全量链接在文末。这里讲的是故事线：从 2026-10-25 到 2026-11-15 的十次架构决策，如何一步一步把这个项目塑造成你现在看到的样子；以及压轴的开放策略（ADR-010）：为什么一个银行系统项目敢把过程全部摊开。

## 第一幕：站在巨人肩上（2026-10-25，内核四连拍）

项目第一天连续拍板四条，定了「底座怎么搭」：

1. **[ADR-001：不重写 Fineract](../../../planning/abnk-design/adr/zh-CN/001-no-rewrite.md)**——核心账务直接复用 Apache Fineract（7100 个 Java 文件、473 个 Liquibase changelog、200 个 E2E 用例的成熟引擎），不自研不重写。差异化价值放在本地化、渠道体验、外围集成、数据智能四件事上；
2. **[ADR-002：全部定制走 `custom/abnk/` 模块](../../../planning/abnk-design/adr/zh-CN/002-custom-modules.md)**——不重写不等于不能定制：所有定制代码物理隔离在 custom 模块路径，fork 与上游保持季度级可合并。「不碰内核」只有一条单行例外，边界清晰到可以在 ADR 里写死；
3. **[ADR-003：PostgreSQL 单一数据库宿主](../../../planning/abnk-design/adr/zh-CN/003-postgresql-baseline.md)**——跟随上游标准化，账号与代码默认值三方对齐，本地调试零环境变量覆盖；
4. **[ADR-004：采用 Fineract 多租户架构](../../../planning/abnk-design/adr/zh-CN/004-multi-tenancy.md)**——架构是现成的、物理分库天然满足金融数据隔离合规；但分阶段落地，业务数据为零时不强行铺开。

这四条的共同逻辑：**高复杂度、低差异化的基础设施用成熟开源，自建精力全部投向差异化**。

## 第二幕：渠道与产品边界（同日补刀两条）

5. **[ADR-005：前端自建三套](../../../planning/abnk-design/adr/zh-CN/005-frontend-strategy.md)**——管理后台、柜面、网银/手机银行按用户诉求分三套建，社区前端不采用；铁律「前端永不直连核心，一律经网关」；
6. **[ADR-006：产品线三波推进](../../../planning/abnk-design/adr/zh-CN/006-product-lines.md)**——储蓄 + 消费贷先行（对应 Fineract 最成熟的两个模块），经营贷第二波，供应链金融留位。产品线决定本地化深水区（会计科目、计息规则）的攻坚顺序。

## 第三幕：技术架构定栈（2026-10-26，评审三连拍）

7. **[ADR-007：信创兼容策略](../../../planning/abnk-design/adr/zh-CN/007-xinchuang-compatibility.md)**——主线开源、信创走兼容层、单一代码线：协议标准优先（OIDC/S3/Redis 协议/K8s），兼容性左移进 CI，国密商密收口网关。拒绝「信创分支」这种双代码线方案；
8. **[ADR-008：渠道层技术架构](../../../planning/abnk-design/adr/zh-CN/008-channel-tech-stack.md)**——Spring Cloud Gateway 网关 + React/TS 前端 + 契约先行（API 类型一律从 OpenAPI 生成，永不手写）；
9. **[ADR-009：移动端改用 Flutter](../../../planning/abnk-design/adr/zh-CN/009-flutter-mobile.md)**——十次决策里**唯一一次公开推翻前决策**（Supersedes ADR-008 第 3 点）：手机银行从「原生薄壳 + H5」改为 Flutter 单代码库双端交付。决策机制的价值不在于永不改判，而在于改判有痕迹、有理由、有边界（只推翻移动端一条，网关与契约先行不变）。

## 压轴：为什么敢全部摊开（2026-10-25 之外的第四个日期，2026-11-15）

10. **[ADR-010：仓库开放与保密边界](../../../planning/abnk-design/adr/zh-CN/010-repository-openness.md)**——**能开尽开为默认；不可开放仅两条边界，各由专仓承载**：

| 仓 | 开放性 | 域 |
|---|---|---|
| abnk-asdm | public | 过程资产（规划/Sprint/ADR/证据/工具集——本站数据源） |
| abnk-system | public | 系统交付物（基础设施编排/渠道/部署） |
| abnk-devportal | public | 内容展示（本站） |
| `.github-private` | private | **密钥边界**：会攻破生产环境的操作性凭据 |
| abnk-website | private | **社区运营边界**：用户 PII 与团队运营过程 |

核心理念：**透明是内容本体，不是需要辩护的风险**——部署拓扑、端口分配、决策过程、未完成状态都是 ASDM 能力展示的一部分；生产安全靠密钥隔离 + 网关鉴权 + NSG 规则，**不靠拓扑模糊**（security through obscurity 不是本项目策略）。配套三道闸门：新资产入仓分流判据、凭据扫描常驻工具门、仓定位变更必须走 ADR（不允许隐性变更）。

你正在浏览的这个 Dev Portal，就是 ADR-010 的直接推论——「五仓两边界」里 public 内容展示域的落地，且带一条自我约束：**portal 是纯渲染器**，只做内容渲染、不长运营功能（用户注册/互动/统计属社区运营域，归 abnk-website 边界）。

## 治理机制的三个样本点

- **决策有账本**：每条 ADR 带状态、日期、决策人、背景、理由、后果（含负面风险）与「必须遵守的衍生约束」——拍板不是拍脑袋，是可追溯的工程记录；
- **改判有痕迹**：ADR-009 Supersedes ADR-008 的单点条目，展示决策体系如何优雅地处理「计划赶不上变化」；
- **治理自身是活样本**：ADR-010 的「五仓两边界」治理框架，正是本站治理板块存在的依据——治理文档描述规则，项目结构执行规则，两者互为印证。

---

> **素材来源**：本篇为 portal 原创导读（叙事线编排），**不改写 ADR 原文**——ADR-001–010 全集原文见 `workspace/docs/planning/abnk-design/adr/zh-CN/`（各 ADR 链接已内嵌正文；事实与措辞以原文为准）。
