---
sprint: v0.0.1
part: part04
phase: 3
task: "3.4"
status: completed
date: 2026-11-17
evidence: ./
locale: zh-CN
---
# 任务 3.4 报告：指标仪表盘页（诚实性原则）

## 交付范围

- `src/pages/metrics/`（新建四件）：`metrics-data.ts`（契约消费通道：`satisfies Widen<Metrics>` 锁结构 + 溯源链接走 link-resolver 单点 + sprintSpan/fmtNum 呈现助手）、`MetricsDashboard.tsx`（六区组合页：总览五指标 / 质量四指标 / Sprint 节奏 / 证据密度 / LOC 规模 / 诚实性区）、`MetricCard.tsx`（指标卡，带 `data-metric` 探针）、`BarList.tsx`（纯 CSS 比例条）、`HonestyBadge.tsx`（CiBadge + BlockedBadge）
- `src/pages/MetricsPage.tsx`：占位 SectionPage 退役，挂正式仪表盘
- `src/i18n/`：新增 metrics 命名空间（zh/en 键对键一致），resources/use-locale/locale-context/index 四处注册（命名 `MetricsCopy`，与 schema `Metrics` 接口区分避免 import 遮蔽）
- 截图 2 张归档 `screenshots/`（metrics-zh-cn.png / metrics-en-us.png，同名覆盖 3.1 占位页截图——占位退役的预期演进）

## 关键决策

1. **图表选型：零依赖纯 CSS 比例条**（BarList）——数据形态是简单计数（节奏天数/证据密度/LOC 行数），坐标轴、交互、图表库均为多余重量；引入 recharts 等会新增 ~100 kB 依赖，违背「轻量优先」与 D4 build-time 静态零依赖精神。条宽严格按 value/max 线性比例，**零值零宽**（part04 当日开工 0 天渲染为空轨道——视觉同样诚实）。
2. **溯源链接走 link-resolver 单点**：metrics 源字段是仓相对路径（`Sprints/v0.0.1/…`），经 `resolveRelativeLink('/src/data/index/', …)` 统一解析为站内 `?url` 资产；解析不到降级源仓镜像并显式标注，源路径原文永不静默丢弃（已知坑 2 延续）。
3. **诚实性组件化**（D6/已知坑 4）：`CiBadge` 对 `not_run` 渲染词条「未实跑 · 规划中」（brick 警示档，绝不冒充 passing 绿色观感）；`BlockedBadge` 挂账警示档；挂账卡带出处链接 + 复验计划；移交往返从 sprint 索引 `moved_links` 渲染双向站内跳转。
4. **契约零私解析**：页面只消费 `Widen<Metrics>` 窄化形态，零 yaml/front-matter 耦合（V3.2.1 纯度判据口径延续）；移交往返消费 sprint 契约与 metrics `moved_count` 守恒（生成器 fail-loud 保证）。

## 步骤验证记录

| 步骤 | 判据 | 实测（2026-11-17） | 结果 |
|---|---|---|---|
| V3.4.1 三绿 | typecheck/lint/build 全 exit 0 | typecheck ✅（首轮 `LocaleContextValue` 漏 metrics 字段报 TS2339，补齐后过——satisfies 互锁即证）/ lint ✅ 零警告 / build ✅（3.03s，主 chunk 690.22 kB 与 3.3 基线同源，拆分归 V3.6.1） | PASS |
| V3.4.2 指标数字与源一致 | 页面四数字 vs Test-Report 头部逐项比对 | 源报告头部：VP **34/34 全过**、单测 **57/57 全绿**、E2E **55/55 断言**、**DRIFT: 0**；页面 `data-metric` 探针机械提取：vp=34/34、unit_tests=57/57、e2e_assertions=55/55、contract_drift=0——**逐项一致**（管线两端一致复验成立）；源报告 + 挂账出处链接 GET 200 ×3；en 态同四指标一致；两态 console 0 红错 | PASS |
| V3.4.3 诚实性判据 | grep 命中 ≥ 1；挂账/移交可见；CI 徽标如实；无虚构指标 | `grep -rn "规划中\|未实跑\|planned" src/pages/metrics/ \| wc -l` → **6**；CI 徽标「未实跑 · 规划中」visible=true（en「Not run · planned」）；挂账 2 项（part03-v6.3.4-android-carrier / part02-p3.6-apple-signing）brick 徽标 visible=true；移交 2 组 4 链接站内可达（part03:5.5 跳转实测达任务页）；数字全部消费 METRICS 契约，无虚构 | PASS |

## 走查环境

- dev server：vite :6203 strictPort（沿用 3.1–3.3 登记端口）；playwright 驱动（console error 计数 0）
- 收口：浏览器与 dev server 已停；`grep '\[DEBUG\]' src/pages/metrics/` = 0（src/data 树内 2 处命中为 part02 历史证据正文，属数据资产原文非代码注入）；build 复跑 ✓；sync 源仓 porcelain 0（本任务文档/截图归档除外）

## 遗留与移交

- 无挂账、无移交。主 chunk 690.22 kB 的路由级拆分归 V3.6.1 判据（3.3 已立先例记录）。
- portal 仓代码变更未提交（按 Phase 约定，提交时机由用户决定）。
