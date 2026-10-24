# Amazing Bank 设计文档（abnk-design）

> 本目录是 Amazing Bank IT 系统的设计文档区。结构于 2026-10-25 评审通过（含 `00-baseline/` 事实层与 `adr/` 决策层的扩展）。
> **铁律：事实与设计分离**——`00-baseline/` 只放实测核实的内容（带出处）；设计文档引用事实、不重复事实；已核实 / 推断 / 猜测永不混排。

## 阅读顺序

```
新人/评审：00-baseline/ 四篇 → adr/ 六篇 → 06-evolution/roadmap.md
施工：06-evolution/phase-1-validation.md（当前活跃文档）
领域设计：05-domains/（差距分析三段式：原生能力/中国差距/定制方案）
```

## 目录结构与状态看板

> ✅ 已填充 · 🚧 部分填充 · ○ 骨架（目标阶段到达时填充）

```
abnk-design/
├── README.md                        # 本文件
│
├── 00-baseline/                     # 事实基线（实测，非设计）
│   ├── environment.md               #   ✅ Phase 0 环境全貌
│   ├── fineract-codebase.md         #   ✅ 代码库测绘（35 模块/7100 文件）
│   ├── api-surface.md               #   ✅ 603 端点分布 + COB三套命名 + 实测坑
│   └── extension-points.md          #   ✅ custom 模块机制 + PoC 风险
│
├── 01-product/
│   ├── positioning.md               #   ○ 定位与价值主张
│   ├── personas.md                  #   ○ 用户角色
│   └── product-lines.md             #   🚧 依 ADR-006 展开（决策已定，待成文）
│
├── 02-architecture/
│   ├── overview.md                  #   ○ L1–L5 分层总览
│   ├── customization-strategy.md    #   ○ custom/abnk 宪法（Phase 2 前必填）
│   ├── api-gateway.md               #   ○ 渠道网关（Phase 3）
│   ├── event-bus.md                 #   ○ 事件总线（Phase 4）
│   └── release-strategy.md          #   ○ 上游同步策略（Phase 2）
│
├── 03-data-model/
│   ├── domain-concepts.md           #   ○ Fineract 核心概念
│   ├── datatables-vs-custom-tables.md # ○ 字段扩展决策树
│   └── localization.md              #   ○ 时区/币种/证照/计息
│
├── 04-operations/
│   ├── engineering-conventions.md   #   ✅ 踩坑总账 + 工程纪律 + 排障树
│   ├── observability.md             #   ○ 复用官方观测栈（Phase 2）
│   └── security-compliance.md       #   ○ 安全与合规（Phase 4）
│
├── 05-domains/                      # 差距分析三段式：原生/差距/方案
│   ├── accounting.md                #   ○ ★ L1 核心：中国 COA 重建
│   ├── savings.md                   #   ○ 存款域
│   ├── lending.md                   #   ○ 贷款域（含经营贷差异节）
│   ├── payments.md                  #   ○ 支付域（Phase 4）
│   └── regulatory-reporting.md      #   ○ EAST/1104（Phase 4）
│
├── 06-evolution/
│   ├── roadmap.md                   #   ○ Phase 0–5 路线图
│   ├── phase-1-validation.md        #   ✅ ★ 当前活跃：12 步端到端施工图
│   └── aos-integration.md           #   ○ AOS 集成（Phase 2 建议）
│
└── adr/                             # 架构决策记录
    ├── README.md                    #   ✅ 索引 + 模板
    ├── 001-no-rewrite.md            #   ✅ 不重写 Fineract
    ├── 002-custom-modules.md        #   ✅ 定制走 custom/abnk（PoC 风险显式接受）
    ├── 003-postgresql-baseline.md   #   ✅ PG 单宿主 + 三方对齐
    ├── 004-multi-tenancy.md         #   ✅ 采用多租户，分阶段
    ├── 005-frontend-strategy.md     #   ✅ 前端自建三套
    └── 006-product-lines.md         #   ✅ 储蓄+消费贷先行
```

## 已生效的决策（摘要）

| ADR | 决策 | 对下游的硬约束 |
|---|---|---|
| 001 | 不重写 Fineract | 永不改核心模块源码与 changelog |
| 002 | 定制全走 `custom/abnk/` | 定制表只走 custom-changelog；自建质量门禁 |
| 003 | PG 单一宿主 | 新服务默认连 abnk-pg，登记 config.json |
| 004 | 多租户要做（分阶段） | 代码不得硬编码单租户假设 |
| 005 | 前端自建三套 | 前端永不直连 8443，一律走网关 |
| 006 | 储蓄+消费贷先行 | 05-domains 优先级按波次排 |

## 当前阶段

**Phase 1（原生能力验证）已解锁**——施工图见 `06-evolution/phase-1-validation.md`，全部前置就绪（环境健康、业务日期已设、COB 触发方式已实测）。

## 维护规则

- 新坑/新事实先入 `00-baseline/`（带出处与日期），再被设计文档引用
- 决策变更走 ADR（不修改已 Accepted 的文档，用新 ADR supersede）
- 每完成一个 Phase，勾选 phase 文档的出口判据并在本文档更新状态看板
- 修改请提交至 `amazingbank-asdm` 仓库
