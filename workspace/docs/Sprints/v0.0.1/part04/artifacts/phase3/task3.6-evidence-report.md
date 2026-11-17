---
sprint: v0.0.1
part: part04
phase: 3
task: "3.6"
status: completed
date: 2026-11-17
evidence: ./
locale: zh-CN
---
# 任务 3.6 报告：证据浏览页（markdown 渲染 + 内链路由 + 三态视觉层次）

## 交付范围

- `src/lib/markdown/`：`meta.ts`（front-matter 剥离公共化——3.3 起沉淀于 decisions-data，六页面共用后上提）；`MdContent.tsx` 升级**三态视觉钩子**（GFM task list `- [x]` sage 实勾 / `- [ ]` copper 空框 / 执行输出行 sage 背景块——双年代形态：Part04 行首「实测（…）」+ Part02 内联「✅ 实测 2026-…」）
- `src/pages/evidence/`（新建三件）：`evidence-data.ts`（?raw 懒加载通道 + 索引查询 + 素材内容 loader）、`DocView.tsx`（通用文档页：front-matter 元信息页头 + 三态正文 + 证据内联素材区 + 同 Part 文档快捷链）、`EvidenceIndex.tsx`（四 Part 分桶索引：文档清单 + Phase 折叠证据浏览 + 计数探针）、`MaterialCard.tsx`（内联素材卡三分支：截图 img / JSON pretty / 文本 pre，点击展开、失败态如实展示）
- **三板块正式页落地**（nav 词条 deliverTask 3.6 的显式责任——六任务收口要求九板块全真实内容）：`src/pages/methodology/`（索引 + 篇章子路由，portal_content 契约 locale 路由 + fallback 标记）、`src/pages/planning/`（README 导览 + 七分区索引 + 单篇子路由，glob keys 构建期静态清单）、`src/pages/governance/`（双语导读 + ADR-010 压轴卡）；三个板块页挂载点退役占位
- `src/lib/link-resolver.ts` 大升级：**内链路由四类全通**（sprints md → DocView 路由 / methodology md → 方法论路由 / planning 设计文档 → 规划路由 / ADR → 决策路由）+ **双坐标解析**（sourcePathOf/dataPathOf 单点换算——已知坑 2 的两坐标系：portal-content 树剥 workspace/docs 前缀致层级差 1 + 源仓 Sprints 大写）+ png 直供 URL 换算 + evidence glob 扩 log/py + 点文件 `.*` 补配
- `scripts/sync-data.sh`：证据直供通道**四桶泛化**（part01–04 全 artifacts 复制 public/evidence/<part>/，V3.5.1 的 phaseP3 155 守恒可复现）+ manifest.json 全量四桶形态（确定性、无时间戳幂等）
- `src/i18n/`：evidence/methodology/planning/governance 四命名空间（zh/en 键对键一致）+ 四处注册；路由嵌套（evidence/methodology/planning 子路由）
- 截图 5 张归档 `screenshots/`（evidence-doc-part02-phaseP2 / evidence-doc-part04-phase4 / evidence-adr010 / evidence-inline-materials / evidence-index）

## 关键决策

1. **双坐标解析**（V3.6.3 实测发现的核心坑）：方法论文档按源仓坐标写相对链接（`../../../Sprints/…` 大写 S、4 层回退含 workspace/docs 层）——数据树坐标首轮未命中时按源仓坐标重解析再映回数据树，两坑（层级差 1 + S/s 大小写）由 sourcePathOf/dataPathOf 单点吸收，不散落页面。
2. **三态钩子限呈现**（已知坑 3）：渲染管线只加样式钩子（勾选框颜色/输出块背景），状态判定仍归 front-matter——渲染呈现状态、不判定状态。
3. **分桶计数 = 构建期 glob keys**：evidenceUrlMap（文本+点文件补配）+ evidenceImageKeys（png keys-only）与源侧 find 全量同口径，两处实测缺口（dotfile / sync 时点）当日发现当日修复。
4. **三个板块页最小组合**：复用渲染管线（MdContent + meta）+ 契约（portal_content/planning glob keys），每页仅组合不新造渲染逻辑——渲染管线与路由转换集中的原则落地。

## 步骤验证记录

| 步骤 | 判据 | 实测（2026-11-17） | 结果 |
|---|---|---|---|
| V3.6.1 三绿 + 懒加载 | 全 exit 0；产物数与最大 chunk 记录；≤ 1 MB 量级 | typecheck ✅ / lint ✅ / build ✅（3.65s）；assets 产物 786；最大 chunk 788 kB（主包 < 1 MB ✓）+ 240/236 kB gap-report 懒 chunk；dist/evidence 直供 427 文件 | PASS |
| V3.6.2 文档三态 | 已完成态勾选/输出区分；非完成态空框；ADR 原文 + front-matter 头 | P2：34 实勾 + **10 输出块**（首轮 0——排查发现 Part02 内联「✅ 实测」形态，钩子扩展双年代后 10 ✓）+ 徽标「已完成」+ 素材卡 10；P4：12 空框 + 0 输出 + 0 素材（与 pending 自洽）+「待执行」；ADR-010：原文表 + 页头「2026-11-15 · 已接受」；console 0 红错；截图 3 张 | PASS |
| V3.6.3 内链路由 | 前三类转路由全通；出界降级标注可见 | ①Plan→Phase1–5 全转 DocView（点击跳转 ✓）；②跨树链接首轮未转→双坐标修复后 Part01–04 全转（点击 Part03 Phase5 跳转 ✓；sprints 文档间跨 part 互链实测 0 处如实登记）；③ADR-010 链接两文档均转 `/decisions/adr/010`；④index yaml/json → GitHub 镜像 + `data-out-of-scope` 可见（四树外 md 链接实测 0 处如实登记） | PASS |
| V3.6.4 内联 + 分桶 | 内联卡展开；计数逐桶一致；console 0 红错 | P3 文档页 155 素材卡：json pretty ✓ / png img 390px ✓ / yaml pre ✓；**四桶 3/207/169/52 = find 3/207/169/52 逐桶一致**（缺口 2 处当日修：dotfile `.audit-pairing.py` glob 漏配 + 归档截图 sync 时点对齐；part02 的 208 含 .DS_Store 非证据件）；en 态同构；console 0 红错；截图 2 张 | PASS |

## 走查环境

- dev server：vite :6203 strictPort（沿用登记端口）；playwright 驱动；收口浏览器与 dev server 已停；三绿终跑 ✓（build exit=0，主 chunk 796 kB——dist 清空的 shim 报错用 `rm -rf dist` 前置规避，非代码问题）
- 源仓只读性：sync 前后 porcelain 一致（本会话归档写入均在 sync 前/后点如实对齐）

## 遗留与移交

- 无挂账、无移交。主 chunk 796 kB 的路由级拆分评估归后续（react-markdown 体积惯性，3.3 起持续记录；懒 chunk 已按文件拆分）。
- portal 仓代码变更未提交（按 Phase 约定，提交时机由用户决定）。
- **六任务收口**：九板块（首页/时间线/决策/旅程/指标/证据/方法论/规划/治理）全真实内容、占位卡全部退役——站点层就绪，Phase 4（容器构建/部署）的部署对象成立。
