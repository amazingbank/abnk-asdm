# Amazing Bank 设计文档（abnk-design）

> 本目录是 Amazing Bank IT 系统的设计文档区。结构于 2026-10-25 评审通过并**全部成文**（34 篇）。
> **铁律：事实与设计分离**——`00-baseline/` 只放实测核实的内容（带出处）；设计文档引用事实、不重复事实；已核实 / 推断 / 猜测永不混排。

## 阅读顺序

```
新人/评审：00-baseline/ 四篇 → adr/ 六篇 → 06-evolution/roadmap.md
施工：06-evolution/phase-1-validation.md（当前活跃文档）
定制开发：02-architecture/customization-strategy.md（宪法）→ 03-data-model/ → 05-domains/
排障：04-operations/engineering-conventions.md（排障决策树）
```

## 目录结构与状态看板

> ✅ 已成文 · 🚧 活跃维护 · 复审标记：★ = 该板块核心文档

```
abnk-design/
├── README.md                          # 本文件
│
├── 00-baseline/                       # 事实基线（实测，非设计）
│   ├── environment.md                 #   ✅ Phase 0 环境全貌
│   ├── fineract-codebase.md           #   ✅ 代码库测绘（35 模块/7100 文件）
│   ├── api-surface.md                 #   ✅ 603 端点分布 + COB三套命名 + 实测坑
│   └── extension-points.md            #   ✅ custom 模块机制 + PoC 风险
│
├── 01-product/
│   ├── positioning.md                 #   ✅ 定位与价值四支柱
│   ├── personas.md                    #   ✅ 7 类角色 → 架构约束映射
│   └── product-lines.md               #   ✅ 三波次明细 + L1 范围裁剪
│
├── 02-architecture/
│   ├── overview.md                    #   ✅ L0–L5 分层 + 依赖方向硬规则
│   ├── customization-strategy.md      #   ✅ ★ custom/abnk 宪法（目录/模板/6红线/门禁）
│   ├── api-gateway.md                 #   ✅ 渠道网关（含 /v1/internal 黑名单）
│   ├── event-bus.md                   #   ✅ Kafka 事件总线（含与 job-topic 的区分）
│   └── release-strategy.md            #   ✅ 季度 rebase 流程 + 检查单 + 冲突预案
│
├── 03-data-model/
│   ├── domain-concepts.md             #   ✅ 概念地图 + 行为语义 + 词汇表
│   ├── datatables-vs-custom-tables.md #   ✅ 字段扩展决策树 + 预判场景
│   └── localization.md                #   ✅ 时区/币种/证照 + 三落点矩阵
│
├── 04-operations/
│   ├── engineering-conventions.md     #   ✅ ★ 踩坑总账 7 类 + 排障决策树
│   ├── observability.md               #   ✅ 复用官方栈 + 分阶段接入
│   └── security-compliance.md         #   ✅ 鉴权演进 + 合规义务地图
│
├── 05-domains/                        # 三段式：原生能力/中国差距/定制方案
│   ├── accounting.md                  #   ✅ ★ L1 核心：COA 五步落地路径
│   ├── savings.md                     #   ✅ 积数计息/按季结息/对年对月对日
│   ├── lending.md                     #   ✅ LPR/五级分类 + 经营贷（第二波）节
│   ├── payments.md                    #   ✅ 骨架：网联/银联/人行集成面
│   └── regulatory-reporting.md        #   ✅ 骨架：EAST/1104 依赖链
│
├── 06-evolution/
│   ├── roadmap.md                     #   ✅ Phase 0–5 + 出口判据 + 风险燃尽表
│   ├── phase-1-validation.md          #   ✅ ★ 判据 5/5 全达成（12 步全通 + E2E 已验证）
│   └── aos-integration.md             #   ✅ 双本体愿景 + Phase 2 建基线理由
│
└── adr/                               # 架构决策记录（全部 Accepted）
    ├── README.md                      #   ✅ 索引 + 模板
    ├── 001-no-rewrite.md              #   ✅ 不重写 Fineract
    ├── 002-custom-modules.md          #   ✅ 定制走 custom/abnk（PoC 显式接受）
    ├── 003-postgresql-baseline.md     #   ✅ PG 单宿主 + 三方对齐
    ├── 004-multi-tenancy.md           #   ✅ 多租户分阶段
    ├── 005-frontend-strategy.md       #   ✅ 前端自建三套
    └── 006-product-lines.md           #   ✅ 储蓄+消费贷先行
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

**Phase 1（原生能力验证）完成（2026-10-25）**——12 步端到端一次跑通（报告 `abnk-system/artifacts/phase1/`）；官方 E2E 运行方式已验证（1 scenario/10 steps 全 passed + allure 报告，判据 5/5 全达成）。**待验证项已回填**，两个原判被推翻：积数计息与对年对月对日均**原生支持**，无需 custom。下一步：Phase 2（custom/abnk 骨架 + 自建 CI 门禁 + COA 会计科目表——后者是关键路径，需要会计专业输入）。

## 维护规则

- 新坑/新事实先入 `00-baseline/`（带出处与日期），再被设计文档引用
- 决策变更走 ADR（不修改已 Accepted 的文档，用新 ADR supersede）
- 每完成一个 Phase，勾选 phase 文档的出口判据并在本文档更新状态看板
- 修改请提交至 `amazingbank-asdm` 仓库
