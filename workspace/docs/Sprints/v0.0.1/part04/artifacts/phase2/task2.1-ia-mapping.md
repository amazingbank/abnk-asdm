---
sprint: v0.0.1
part: part04
phase: 2
status: completed
date: 2026-11-16
evidence: ../
locale: zh-CN
---
# 任务 2.1 —— portal IA 设计文档（板块 → 数据源映射表）

- 日期：2026-11-16；执行人：AI（abnk-debugger 会话）
- 定位：Phase 3 页面任务开工前的对照单一事实源（防板块范围漂移）；路径约定——`workspace/` 前缀 = abnk-asdm 仓 `.asdm/workspace/`，「portal 仓」前缀 = abnk-devportal 仓内路径。

## 八大板块映射表（主表：板块 × 数据源路径 × 渲染模式 × 责任 Phase）

| # | 板块 | 数据源路径 | 渲染模式 | 责任 Phase |
|---|---|---|---|---|
| 1 | 方法论 | `workspace/docs/portal-content/methodology/{zh-CN,en-US}/`（四篇：index/context-engineering/harness-engineering/self-iteration——**任务 2.2/2.3 产出**）；素材源：asdm-training 仓 `docs/workshops/`（README 总纲 + `tracks/` + `sessions/20261030-ISS-Public/`，引用不改写、注明来源） | 内容渲染（portal-content） | Phase 2（内容：任务 2.2 zh 四篇 + 任务 2.3 en 总览）+ Phase 3（页面） |
| 2 | 规划与决策 | `workspace/docs/planning/abnk-design/adr/zh-CN/`（001–010 全集 + README，原文）；`workspace/docs/Sprints/v0.0.1/part02..04/zh-CN/v0.0.1-Part0N-Plan.md` 各「决策记录」节（D 表摘要卡——**part01 Plan 无决策表，如实登记为不适用**） | 混合（原文渲染（ADR/Plan 决策节）+ 时间轴编排（数据渲染）） | Phase 3（任务 3.3 决策时间线页） |
| 3 | 迭代时间线 | `workspace/index/sprint-v0.0.1.yaml`（Sprint→Part→Phase→Task 四层主轴）；深链目标：`workspace/docs/Sprints/v0.0.1/part*/zh-CN/` Phase 文档 | 混合（数据渲染（index 四层下钻主轴）+ 深链原文渲染（Phase md）） | Phase 3（任务 3.2 四层下钻页；路由骨架 3.1） |
| 4 | 任务证据链 | `workspace/docs/Sprints/v0.0.1/part01..04/`（`zh-CN/` Phase 文档 md + `artifacts/` 证据桶 yaml/png/txt/json——EvidenceIndex 按 Phase 分桶） | 原文渲染（Sprints md + 内联素材卡三态视觉层次） | Phase 3（任务 3.6 证据浏览页） |
| 5 | E2E 旅程 | `workspace/docs/Sprints/v0.0.1/part02/artifacts/phaseP3/`（`p3-01..05.yaml` + `p3-chk.yaml` 五步+核对快照；`screenshots/` + `taskP3.6-screens/` 截图；`taskP3.1-mobile-e2e.md`/`taskP3.2-bo-e2e.md` + `taskP3.{3,4,5}-*-evidence.txt` 证据）；`part01/artifacts/e2e-first-run.json`（首次运行记录） | 原文渲染（快照 + 截图 + 证据三素材编排） | Phase 3（任务 3.5 E2E 旅程故事线页） |
| 6 | 指标仪表盘 | `workspace/index/metrics-v0.0.1.json`（含 blocked_items 挂账——D6 诚实性：未完成项按「规划中」如实展示）；`workspace/index/loc-snapshot-v0.0.1.md`（LOC 快照） | 数据渲染（index/metrics） | Phase 3（任务 3.4 指标仪表盘页） |
| 7 | 治理与开放 | `workspace/docs/portal-content/governance/{zh-CN,en-US}/index.md`（导读——**任务 2.4 产出**）；`workspace/docs/planning/abnk-design/adr/zh-CN/010-repository-openness.md`（五仓两边界原文，压轴治理样本） | 混合（内容渲染（导读）+ 原文渲染（ADR-010）） | Phase 2（内容：任务 2.4 双语导读）+ Phase 3（页面） |
| 8 | 复现指南 | portal 仓 `scripts/sync-data.sh`（D4「提取入库、构建纯复制」——复制链即复现链）；`workspace/../scripts/gen-sprint-index.py`（asdm 仓 `.asdm/scripts/` 生成器入口）；`workspace/docs/Sprints/v0.0.1/part04/artifacts/phase4/` 发布命令链手册（**任务 4.4 产出**） | 混合（原文渲染（脚本/手册）+ 内容渲染（操作叙事）） | Phase 4（任务 4.4 发布手册与数据更新链固化——**表内声明：Phase 4**） |

## 入口路由建议（板块 → 路由）

| 板块 | 路由 | 说明 |
|---|---|---|
| 首页导览（附注，非八板块主体） | `/` | 消费 `workspace/docs/portal-content/overview/{zh-CN,en-US}/`（index.md 首页导览 + timeline.md 时间线骨架说明——任务 2.3 产出）；布局由任务 3.1 承载 |
| 方法论 | `/methodology` | 板块 1 |
| 规划与决策 | `/decisions` | 板块 2（ADR 10 卡 + D 表摘要卡统一时间轴） |
| 迭代时间线 | `/timeline` | 板块 3（灵魂页面：四层下钻） |
| 任务证据链 | `/evidence` | 板块 4（DocView + EvidenceIndex） |
| E2E 旅程 | `/journey` | 板块 5（五步 + 核对故事线） |
| 指标仪表盘 | `/metrics` | 板块 6（诚实性原则） |
| 治理与开放 | `/governance` | 板块 7 |
| 复现指南 | `/reproduce` | 板块 8 |

## 依赖声明（三类数据域 × 消费板块）

1. **消费 index/metrics（数据渲染域）**：迭代时间线（sprint yaml 四层）、指标仪表盘（metrics json + loc 快照）、规划与决策（时间轴编排消费 ADR 元数据）——复制依赖 portal 仓 `scripts/sync-data.sh` 既有映射 `workspace/index → src/data/index/`。
2. **消费 portal-content（内容渲染域）**：方法论、治理与开放、首页导览（overview）——**首次扩面**：portal-content 分区当前不在 sync 复制范围，扩展由任务 2.3 对 `sync-data.sh` 的增量承载（Phase 1 契约未覆盖该分区）。
3. **消费 planning/Sprints 原文（原文渲染域）**：规划与决策（ADR 全集）、任务证据链（Sprints md + artifacts）、E2E 旅程（phaseP3 三素材）、复现指南（跨仓脚本 + Phase 4 手册）——复制依赖既有映射 `Sprints → src/data/sprints/`、`planning/abnk-design → src/data/planning/abnk-design/`。
4. **跨仓只读纪律（全板块共用）**：portal 构建零提取逻辑、对 abnk-asdm 纯只读（sync 前后 porcelain 比对）；en 深链内容 fallback 由 index 层 locale 路由承载（任务 2.3 机制）。

## 既有性判定口径（V2.1.1 执行前声明）

- **既有数据源**（Phase 1 数据集 + planning + Sprints + 两仓脚本）：逐一 `test -e`，必须全过（下方核验记录）。
- **Phase 2/4 产出落点**（portal-content 三分区、phase4 手册）：以「产出任务」标注——既有性由对应任务的验收步骤承载（V2.2.1 / V2.3.1 / V2.4.1 / 任务 4.4），Phase 3 消费时点必然既有；**不计入失联数据源**。

## V2.1.1 核验记录（映射表产出与完备性）

- 主表 8 行 × 4 列，空单元格 0（`grep -cE '\|\s*\|'` 主表区段命中 0）。
- 既有数据源 `test -e` 逐条结果（真实执行，2026-11-16）：

| 数据源路径（相对 `.asdm/workspace/`，另注者除外） | test -e |
|---|---|
| `index/sprint-v0.0.1.yaml` | ✅ |
| `index/metrics-v0.0.1.json` | ✅ |
| `index/loc-snapshot-v0.0.1.md` | ✅ |
| `docs/planning/abnk-design/adr/zh-CN/`（001–010 + README） | ✅ |
| `docs/Sprints/v0.0.1/part02/zh-CN/v0.0.1-Part02-Plan.md` | ✅ |
| `docs/Sprints/v0.0.1/part03/zh-CN/v0.0.1-Part03-Plan.md` | ✅ |
| `docs/Sprints/v0.0.1/part04/zh-CN/v0.0.1-Part04-Plan.md` | ✅ |
| `docs/Sprints/v0.0.1/part01..04/`（zh-CN Phase 文档 + artifacts） | ✅ |
| `docs/Sprints/v0.0.1/part02/artifacts/phaseP3/`（p3-01..05/chk.yaml、screenshots/、taskP3.6-screens/、e2e/evidence md+txt） | ✅ |
| `docs/Sprints/v0.0.1/part01/artifacts/e2e-first-run.json` | ✅ |
| 素材源：asdm-training `docs/workshops/README.md`（+ `tracks/`、`sessions/20261030-ISS-Public/`） | ✅ |
| portal 仓 `scripts/sync-data.sh` | ✅ |
| asdm 仓 `.asdm/scripts/gen-sprint-index.py` | ✅ |

- 失联数据源 0（既有数据源 13 行展开 23 条路径 test -e 全过——真实执行两轮：workspace 相对路径 18 条 + 绝对路径复跑 5 条（asdm-training 素材源 ×3、portal 仓 sync 脚本、asdm 仓生成器）；产出落点 3 项按「既有性判定口径」登记）。
- 渲染模式枚举核验：主表 8 行渲染模式 ∈ {数据渲染（index/metrics）、内容渲染（portal-content）、原文渲染（planning/Sprints md）、混合}，越界 0（数据渲染 1、内容渲染 1、原文渲染 2、混合 4）。

## V2.1.2 核验记录（责任 Phase 声明一致性）

与 Part04 Plan「进度概要」任务归属逐板块比对（2026-11-16 真实比对）：

| 板块 | 映射表责任声明 | Plan 进度概要对应行 | 一致性 |
|---|---|---|---|
| 方法论 | Phase 2（任务 2.2/2.3）+ Phase 3 | 任务 2.2 方法论板块内容改写（P2）、任务 2.3 en-US 第一批（P2） | ✅ |
| 规划与决策 | Phase 3（任务 3.3） | 任务 3.3 决策时间线页（P3） | ✅ |
| 迭代时间线 | Phase 3（任务 3.2） | 任务 3.2 迭代时间线四层下钻页（P3） | ✅ |
| 任务证据链 | Phase 3（任务 3.6） | 任务 3.6 证据浏览页（P3） | ✅ |
| E2E 旅程 | Phase 3（任务 3.5） | 任务 3.5 E2E 旅程故事线页（P3） | ✅ |
| 指标仪表盘 | Phase 3（任务 3.4） | 任务 3.4 指标仪表盘页（P3） | ✅ |
| 治理与开放 | Phase 2（任务 2.4）+ Phase 3 | 任务 2.4 治理与开放板块内容（P2） | ✅ |
| 复现指南 | Phase 4（任务 4.4，表内声明） | 任务 4.4 发布手册与数据更新链固化（P4）——V2.1.2 判据「Phase 3 或 4 以表内声明为准」 | ✅ |

- 冲突 0；方法论/治理 → 本 Phase，时间线/证据/E2E/指标 → Phase 3，复现指南 → Phase 4（表内声明），全部与 Plan 任务归属一致。
