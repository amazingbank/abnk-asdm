---
sprint: v0.0.1
part: part04
phase: 3
task: "3.5"
status: completed
date: 2026-11-17
evidence: ./
locale: zh-CN
---
# 任务 3.5 报告：E2E 旅程故事线页

## 交付范围

- `src/pages/journey/`（新建三件）：`journey-steps.ts`（故事结构数据模块：五步 + 核对步 + 三载体复验 + 问题记录 + 快照/截图 URL 单点）、`JourneyView.tsx`（页面组合：概要行 → 六步序列 → 三载体复验 → 诚实性区）、`ShotCard.tsx`（截图卡：懒加载 + 原图链接 + data-shot 探针）
- `src/pages/JourneyPage.tsx`：占位 SectionPage 退役，挂正式故事线
- `scripts/sync-data.sh`：**journey 素材直供通道**——phaseP3 整目录（155 文件）复制至 `public/evidence/part02/phaseP3/`，资产清单 `manifest.json`（确定性内容、无时间戳幂等）落 evidence 根不混入守恒计数；--check 模式同步覆盖
- `.gitignore`：`public/evidence` 纳入生成产物不入库纪律（与 src/data/ 同口径）
- `src/i18n/`：journey 命名空间（zh/en 键对键一致），resources/use-locale/locale-context/index 四处注册
- 截图 3 张归档 `screenshots/`（journey-zh-cn.png / journey-zh-cn-honesty.png / journey-en-us.png，同名覆盖 3.1 占位页截图——占位退役的预期演进）

## 关键决策

1. **素材双通道**（已知坑 1 形态落定）：快照 yaml / 证据 md 走构建期 `?url` 资产（link-resolver evidenceUrlMap 单点取用）；截图 PNG 走 public/evidence 静态直供（二进制不 import 进 JS，14 张懒加载不阻塞首屏）。
2. **整目录守恒复制**：源侧实测 155 文件（p3 yaml 7 + screenshots 19 + 报告件 8 + gap 报告 4 + baseline 1 + **taskP3.6-screens 101**）超出计划枚举——整目录复制使守恒判据严格成立（155 = 155），taskP3.6-screens 属 phaseP3 桶内素材一并直供。
3. **故事内容文字化，页面零原始解析**：六步关键节点从快照 yaml / 证据报告 md 文字化（原样口径：金额、流水号、余额、附言逐字来自素材）；素材 URL 全部经 journey-steps 单点，页面不触碰文件系统语义。
4. **诚实性三落点**（V3.5.2 判据）：①p3-login.yaml 原文 verbatim 渲染（a11y 未开启状态整棵语义树仅一行「Enable accessibility」——不删除不补拍）；②步骤 1 节点原样含「指纹登录与安全键盘为视觉占位（POC 范围外）」；③4 条问题记录（a11y 快照 / 视觉占位 / 接线修复三缺口 / 环境坑位 3 条）+ 加载失败降级展示文件名（不悄悄吞掉缺失素材）。

## 步骤验证记录

| 步骤 | 判据 | 实测（2026-11-17） | 结果 |
|---|---|---|---|
| V3.5.1 三绿 + 素材就位 | 三绿全 exit 0；产物计数 = 源侧计数 | typecheck ✅ / lint ✅（首轮 1 个未用变量即修）/ build ✅（3.11s）；**守恒 155 = 155**；清单 manifest.json 155 条；dist/evidence 直供 155 文件；sync 前后源仓 porcelain 一致 | PASS |
| V3.5.2 故事线走查 | 五步 + 核对步全通；证据链接全可达；问题记录原样 | 6 步结构探针全对（第 6 步 `kind=check`）；**21/21 链接 GET 200**（主证据 1 + 快照 6 + 截图 14）；截图 **14/14 加载**（懒加载滚动触发）；p3-login 原文 verbatim（`- button "Enable accessibility" [ref=e4]`）；4 条问题记录齐；三载体 iOS 4 + Android 5 截图 + 计数链 75→79；两态 console 0 红错；截图 3 张归档 | PASS |

## 走查环境

- dev server：vite :6203 strictPort（沿用登记端口）；playwright 驱动；收口时浏览器与 dev server 已停、build 复跑 ✓、`[DEBUG]` 残留 0
- 源仓只读性：sync 前后 porcelain 逐字节一致（本会话的文档/截图归档写入均在 sync 前发生，不构成 sync 污染）

## 遗留与移交

- 无挂账、无移交。
- portal 仓代码与脚本变更未提交（按 Phase 约定，提交时机由用户决定）。
- 下一任务 3.6（证据浏览页）将复用本任务确立的 public/evidence 直供通道与 manifest 形态（全量截图复制 + 资产清单 JSON 扩展）。
