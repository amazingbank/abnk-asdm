---
sprint: v0.0.1
part: part04
phase: 3
status: completed
date: 2026-11-16
evidence: ../
locale: zh-CN
---
# 任务 3.3 —— 决策时间线页（ADR + Part 决策表合并渲染）走查记录

- 日期：2026-11-16；执行人：AI（abnk-debugger 会话）
- 定位：10 个 ADR + 25 条 Part 拍板记录按日期合并成一条决策时间线——「项目如何被逐个决策塑造」的叙事页；ADR 原文可渲染查看（含 GFM 表格）；修订上下文可跳转。

## 执行时决策记录

| 决策点 | 结论 | 依据 |
|---|---|---|
| 渲染器选型（前置条件表遗留项，提前至 3.3 落定） | **react-markdown ^10 + remark-gfm ^4**（remark/rehype 同族） | V3.3.2 硬门要求「点击 ADR-010 → 原文渲染（五仓定位表可见）」——GFM 表格是五仓定位表的硬需求；3.6 在此基座（`src/lib/markdown/MdContent.tsx`）上扩展 front-matter 元信息页头与三态视觉钩子 |
| D 表数据契约（契约唯一铁律前置） | **生成器增量**：`parse_decisions` 从各 Part Plan「决策记录」节提取 D 行（表头拍板日期 + 行内联日期 + 标题 + 内容）；Part01 无表 → optional 字段省略（审核实测口径） | 渲染层零 md 解析散落；契约双侧同步（schema.ts `DecisionEntry`）；fail-loud 三重：有表头零 D 行、〔修订〕标注未捕获 Phase、行形态漂移 |
| 修订上下文跳转 | `revised_in_phase` = 〔…修订，Phase N〕标注的**机械提取**（正则），渲染为「修订上下文 → Phase N」链接到时间线 Phase 文档页 | 数据里已有结构化标注（Part03 D3→Phase 7、D4→Phase 5）；不做文本猜测，只机械提取契约字段 |
| ADR 元数据 | **生成器增量**：`collect_adrs` 从 planning 树 ADR 提取 front-matter（section/status/locale，词表 accepted/proposed/rejected/superseded）+ 正文标题与日期行 → 索引顶层 `adrs`（10 条） | ADR 状态词表与 Sprints 状态词表分立（schema.ts `AdrStatus`）；id 取文件名三位前缀 |
| ADR 原文加载形态 | `import.meta.glob ?raw` 懒加载 + 按文件路由分块 | 已知坑 1 懒加载形态首个落地（`010-repository-openness` 独立 chunk 4.88 kB）；3.6 将 md 懒加载形态推广到 Sprints 文档 |
| ADR 站内路由 | link-resolver 扩展 `route` 解析类：markdown 内指向 ADR 的相对链接 → `/decisions/adr/NNN` 站内路由（非裸文件）；源仓镜像映射从 sprints 单树扩展为四树通用 | 「六页面共用」的内链转换层定位；Part03 D9 卡内的 ADR-010 markdown 链接实测转为站内路由跳转 |

## 改动清单

| 类别 | 仓 | 文件 | 说明 |
|---|---|---|---|
| 修改 | abnk-asdm | `.asdm/scripts/gen-sprint-index.py` | `parse_decisions`（D 表提取 + 修订标注提取 + fail-loud）+ `collect_adrs`（ADR front-matter/标题/日期提取 + 词表校验）+ 索引注入 `decisions`/`adrs` + 头部文档 |
| 修改 | abnk-asdm | `workspace/index/sprint-v0.0.1.{yaml,json}` | 再生成：25 条 D 决策 + 10 条 ADR 入索引 |
| 修改 | portal | `src/data/schema.ts` | `DecisionEntry` + `PartEntry.decisions?` + `AdrStatus` + `AdrEntry` + `SprintIndex.adrs`（契约双侧同步） |
| 新建 | portal | `src/lib/markdown/MdContent.tsx` | markdown 渲染管线基座（react-markdown + remark-gfm + tailwind 组件 map + 内链 link-resolver 转换 + 出界降级显式标注） |
| 修改 | portal | `src/lib/link-resolver.ts` | `route` 解析类 + `adrRoute`/`decisionsRoute` + ADR 路径正则 + 四树源仓镜像映射 |
| 新建 | portal | `src/pages/decisions/`（4 文件） | decisions-data（索引窄化导出 + ADR ?raw 懒加载 + 元信息剥离）/DecisionTimeline（35 卡合并时间线）/AdrView（原文页，懒加载 + 失败如实态）/DecisionsPage（Outlet 壳） |
| 新建 | portal | `src/i18n/locales/{zh-cn,en-us}/decisions.json` | 决策页词条（ADR 状态词表/摘要计数/卡标签/修订上下文/加载态）；en 语义重写 |
| 修改 | portal | `src/i18n/` 注册四文件 + `src/router.tsx` + `package.json` | decisions 命名空间注册；嵌套路由（index 时间线 + adr/:adrId 原文页）；旧占位 `src/pages/DecisionsPage.tsx` 删除；渲染器依赖 |

## V3.3.1 实测（三绿）

- typecheck ✅（首轮 3 处类型错误即修：glob 懒加载器签名 ×2、statusLabels 索引收窄）/ lint ✅ 零警告 / build ✅
- ADR 原文懒加载分块生效（`010-repository-openness` 独立 chunk 4.88 kB）；主 chunk 673 kB 警告系 react-markdown 体积——**如实记录**：路由级拆分归 V3.6.1 判据接管
- 生成器：D 卡 25（9+9+7）+ ADR 10 提取全过；`--verify` 三产物一致；首跑发现 Part03 D9 行（`D9（2026-11-15 用户拍板）` 内联日期带附加文字）正则不匹配 → 放宽捕获后 9/9 齐

## V3.3.2 实测（决策覆盖完备走查，dev :6203）

| 判据 | 实测 |
|---|---|
| ADR-001–010 全部入线 | ADR 卡 = **10/10** ✅ |
| D 卡 25 张齐 | **25/25**（part02 9 / part03 9 / part04 7；Part01 无表如实省略）✅ |
| ADR-010 原文渲染 | h1 = 「ADR-010：仓库开放与保密边界（能开尽开 + 两条例外）」；**五仓定位表完整可见**（6 行：asdm/system/devportal 三 public + `.github-private` private + website private；GFM 表格渲染正确）✅ |
| Part03 D4 修订上下文 | 跳转 **/timeline/part03/phase/5**（Phase5-Asdm-Workspace 文档）✅；加验 D3 → /phase/7 亦成立（两处修订链全覆盖） |
| en 态抽查 | ADR/D = 10/25 卡齐；D9 卡内 ADR-010 markdown 链接经 link-resolver 转为 `/en-us/decisions/adr/010` 站内路由跳转成功 ✅ |
| console | 0 红错 ✅ |
| 截图归档 | 5 张：decisions-timeline-{zh-cn,en-us} / decisions-adr010-{zh-cn,en-us} / decisions-D4-revision-context-part03-phase5-zh-cn |

## 诚实备注（不美化）

1. **ADR 正文内链密度**：ADR-010 正文中无指向其他 ADR 的站内链接（源文即无内链），「正文内 ADR 站内链接数 = 0」如实记录——站内路由转换能力经 D9 卡内链接实测验证，非未实现。
2. **D 卡正文为 zh 原词**：决策内容按 D3 fallback 显示 zh（UI 词条双语、内容 en 重写为 roadmap 增量）。
3. **react-markdown 主包体积**：+490 kB（min）进入主 chunk；路由级懒加载拆分（markdown 渲染器整体异步化）是 V3.6.1 已知项，本任务不提前实施。
4. **两仓变更未提交**：延续 Phase 3 口径——提交时机由用户决定（上一轮 3.1/3.2 已按用户指令提交推送，本轮 3.3 变更待指令）。
