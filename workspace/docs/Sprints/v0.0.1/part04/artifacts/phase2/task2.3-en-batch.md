---
sprint: v0.0.1
part: part04
phase: 2
status: completed
date: 2026-11-16
evidence: ../
locale: zh-CN
---
# 任务 2.3 —— en-US 第一批清单与抽查记录

- 日期：2026-11-16；执行人：AI（abnk-debugger 会话）
- 定位：en-US 树从「生长规则约定」变为第一批实体内容（D2 口径：语义重写非翻译），生成器 locale 路由 + 双侧契约同步落地。

## en-US 第一批清单（5 新建 + 3 修改）

| 类别 | 文件 | 说明 |
|---|---|---|
| 新建 | `portal-content/overview/zh-CN/index.md` | 首页导览 zh（en 的对称 doc id 原始内容） |
| 新建 | `portal-content/overview/zh-CN/timeline.md` | 时间线骨架说明 zh（四层下钻导读） |
| 新建 | `portal-content/overview/en-US/index.md` | 首页导览 en（语义重写） |
| 新建 | `portal-content/overview/en-US/timeline.md` | 时间线骨架说明 en（语义重写） |
| 新建 | `portal-content/methodology/en-US/index.md` | 方法论总览 en（语义重写） |
| 修改 | `.asdm/scripts/gen-sprint-index.py` | locale 路由增量：portal-content 遍历 + 双 locale 注册 + fallback 标记（PORTAL_STATUS/PORTAL_LOCALES 词表 fail-loud） |
| 修改 | `abnk-devportal/scripts/sync-data.sh` | 复制范围扩 `workspace/docs/portal-content → src/data/portal-content/`（首次扩面，3→4 映射） |
| 修改 | `abnk-devportal/src/data/schema.ts` | `Locale` 枚举 + `PortalStatus`/`PortalContentEntry`（含 `fallback?` 字段）+ `SprintIndex.portal_content` 必填字段 |

双语 doc id（3 个）：`overview/index`、`overview/timeline`、`methodology/index`；单语 zh doc id（6 个）：methodology 的 context-engineering / harness-engineering / self-iteration + overview 侧无（全部带 fallback 标记）。

## V2.3.2 抽查记录：en 语义重写质量（三篇 × 3 段人工判读）

判读口径（D2）：句式按英语习惯重组（非逐词对应）、术语用金融/软件行业惯用语、无「翻译腔」开头与结构。

| # | 篇目 | zh 原段（要点） | en 重写段（要点） | 判读 |
|---|---|---|---|---|
| 1 | methodology/en-US/index | 大模型本质是超快的文字接龙工具，没有「理解」，只有统计相关性 | an LLM is, at bottom, a blisteringly fast **text-completion engine** — no "understanding," just statistical correlations learned from a massive corpus | ✅ 「文字接龙」→ text-completion engine（LLM 行业术语，FIM/text completion 惯用），非直译 |
| 2 | methodology/en-US/index | 将系统开发从「为人类设计」转向「为 AI 设计」 | **stop designing systems for humans and start designing them for AI** | ✅ 名词化陈述重组为英语祈使句对仗，母语惯用 |
| 3 | methodology/en-US/index | 递归叙事是设计原则，不是副产品 | the recursive narrative is a design principle, **not a by-product** | ✅ by-product 为地道搭配；整句独立成理，无逐词痕迹 |
| 4 | overview/en-US/index | 银行核心系统项目把软件工程过程完整摊开的窗口 | a **core-banking** project with its entire software engineering process **laid open** | ✅ core-banking 为金融科技行业标准术语；laid open 保留原句修辞力度 |
| 5 | overview/en-US/index | 透明包括透明地展示未完成 | Transparency includes **transparently showing what's unfinished** | ✅ 原句的递归修辞在英语中同样成立，句式自然 |
| 6 | overview/en-US/index | git history 即数据可信度审计记录 | the git history **doubles as** the audit trail for data trustworthiness | ✅ doubles as 英语惯用；audit trail 为工程审计标准术语 |
| 7 | overview/en-US/timeline | 产出状态由验证结果驱动，不由自述驱动 | Status is driven by verification results, **never by self-report** | ✅ never by self-report 简洁有力，软件流程惯用表述 |
| 8 | overview/en-US/timeline | 两处数字天然一致（幂等可复算） | the numbers **agree by construction** (idempotently recomputable) | ✅ by construction 为数学/工程惯用语，准确传达「机制保证」 |
| 9 | overview/en-US/timeline | portal 展示自己的交付过程，递归叙事是设计原则 | The portal **exhibits its own delivery process** — the recursive narrative is a design principle | ✅ exhibits 自反用法自然；em-dash 节奏为英语写作惯例 |

- 机翻腔黑名单扫描（`the following|as mentioned above|it can be seen that`）：**命中 0**（判据 ≤ 2）。
- 附加观察：en 篇对 zh-only 深链的引用方式采用「英文标题 + 中文链接 + per-need 生长声明」（如 harness-engineering 链接旁注 Chinese; English edition growing per-need）——与 fallback 机制（V2.3.3）语义一致。
- 诚实性声明：判读者为创作执行者本人（AI 会话），非独立第三方——结论如实记录，供后续人工复核抽样。

## V2.3.1 编译门槛记录（已勾选步骤的证据留存）

- `gen-sprint-index.py` 生成 exit 0：`parts=4 docs=24 tasks=74 moved=2 portal_docs=9 portal_en=3`——index 含 locale=en-US 条目 **3**（≥ 3：overview/index、overview/timeline、methodology/index）；
- `--verify` exit 0（index/front-matter 双向一致，metrics/源报告一致）；
- 首跑拦截记录（fail-loud 实证）：Phase 2 Plan 行「🔶 进行中（任务 2.1 ✅ …）」因混入 ✅ emoji 被状态词表按首命中映射为 completed，与 Phase2 文档 front-matter in_progress 双源漂移 → exit 1。处置：修源双改（Plan 行改「🚧 进行中（2026-11-16 开工，任务 2.1/2.2 已收口）」），未给生成器加容错——机制按设计工作；
- `sync-data.sh` exit 0（4 映射），源↔拷贝守恒：`portal-content` md **9 = 9**，只读性证明成立（porcelain 前后一致）；
- `npm run typecheck` exit 0（`sprint.sample.json` 已按任务 1.2 同口径再制备——yaml→json 一次性转换含 portal_content；`sample.check.ts` 扩 portalDocs/portalEn 互证事实）。

## V2.3.3 fallback 机制演示记录（数据管线 en 路由有效性）

- 单语 doc id 条目（`methodology/context-engineering.md`，仅 zh-CN）字段形态：
  ```yaml
  - section: methodology
    doc: context-engineering.md
    locale: zh-CN
    status: published
    date: '2026-11-16'
    fallback: zh-CN      # ← 单语条目含 fallback 标记（值 = 仅有 locale）
  ```
- 双语 doc id 条目（`methodology/index.md`）字段形态——双 locale 注册、无 fallback 字段：
  ```yaml
  - {section: methodology, doc: index.md, locale: zh-CN, status: published, date: '2026-11-16'}
  - {section: methodology, doc: index.md, locale: en-US, status: published, date: '2026-11-16'}
  ```
- 全量统计：portal_content 总条目 9 = 6 双语条目（3 doc id × 2 locale）+ 3 单语条目（context-engineering / harness-engineering / self-iteration，均带 fallback）；en-US 条目 3。Phase 3 渲染层按 `locale` 路由、按 `fallback` 回退，无需扫描目录。

## V2.3.4 幂等复验记录

- 验证方法（快照对照）：第一遍运行产出快照 → 完整重跑第二遍 → 两产物逐字节 `diff` —— **零差异，幂等成立**。
- 判据口径的如实说明：V2.3.4 字面命令 `git diff --stat -- workspace/index | wc -l` 当前输出 3（两文件 M，+63/-9）——这是**首次运行相对上次提交的合法内容变更**（portal_content 新增 + Phase2/任务 2.1–2.3 状态推进），非幂等失败；生成器/契约增量按已知坑 4 单独提交、提交时机由用户决定——提交后重跑该命令即得 0。
