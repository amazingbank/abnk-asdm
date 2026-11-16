---
sprint: v0.0.1
part: part04
phase: 3
status: completed
date: 2026-11-16
evidence: ../
locale: zh-CN
---
# 任务 3.1 —— 路由与布局骨架 + 正式双语 UI 词条（走查记录）

- 日期：2026-11-16；执行人：AI（abnk-debugger 会话）
- 定位：八板块九页面路由 + Nav/Footer/PageShell 布局基底 + 正式双语词条（nav 命名空间独立成包）——后续五任务（3.2–3.6）的统一挂载点与视觉基底。
- 前置条件核验（执行前真实跑）：Phase 门禁（awk 区段 ⏳=0）✅；契约基线三绿 ✅；数据只读性（sync 后源仓 porcelain 0/0）✅。

## 选型决策记录（执行时核验，非凭记忆）

| 决策点 | 结论 | 依据 |
|---|---|---|
| 路由库 | **react-router-dom `^6.30.6`**（^6.28.0 约束族内解析） | 同构参照核验：abnk-website 为单页锚点导航（无路由库，不适用多页站点）；abnk-system backoffice（第二次同构实例，Part03 Phase 1）实际使用 `react-router-dom ^6.28.0` + BrowserRouter + v7 future flags——portal 是多页站点，跟随 backoffice 实际形态 |
| 语言切换通道 | LocaleProvider 移入 BrowserRouter 内部，切换走 router navigate 单通道 | 原实现「裸 pushState + popstate 监听」与 RR 的内部 location 状态分叉（pushState 不通知 RR），合流为单通道后 URL 与渲染语言永不背离 |
| 未知路径 | 板块内未匹配路径 → 保持语言前缀重置回该语言首页（reset 语义） | 与 main.tsx 对无前缀 URL 的处理一致；未知路径不冒充 404 内容页 |
| 路由 ↔ 词条互证 | `SECTION_ROUTES as const satisfies …` + `SECTION_PAGES satisfies Record<SectionId, …>` 双向编译期互锁 | 路由缺词条 / 板块缺页面挂载均直接编译失败（V3.2.1 契约唯一铁律的前置形态） |

## 改动清单

| 类别 | 文件 | 说明 |
|---|---|---|
| 新建 | `src/router.tsx` | 路由表（SECTION_ROUTES 9 板块）+ 页面挂载表 + PortalLayout（语言门 + Nav/Outlet/Footer）+ ScrollToTop + UnknownPath |
| 新建 | `src/components/layout/Nav.tsx` | 品牌→首页、九板块 NavLink 激活态、语言切换、移动端折叠菜单（路由切换即收起） |
| 新建 | `src/components/layout/Footer.tsx` | tagline + 双仓入口（abnk-asdm / abnk-devportal GitHub）+ 版权年份（interpolate） |
| 新建 | `src/components/layout/PageShell.tsx` | 页面级视觉基底（eyebrow/H1/描述页头 + 内容容器），六任务页面共用 |
| 新建 | `src/pages/HomeView.tsx` | 首页导览（hero + 九板块卡片目录，全部消费 nav/home 词条） |
| 新建 | `src/pages/SectionPage.tsx` + 九板块页薄封装 | 板块占位页：PageShell + 「建设中」卡片（{task} 注入交付任务号，D6 诚实性如实标注） |
| 新建 | `src/i18n/locales/{zh-cn,en-us}/nav.json` | 正式导航与板块页面词条（mainAria/homeLabel/menu + 9 板块 × label/eyebrow/title/description/deliverTask）；en 语义重写 |
| 修改 | `src/i18n/locales/{zh-cn,en-us}/common.json` | nav 词条独立成包后移除 nav 键；新增 shell（skipToContent/languageAria）与 section（planned 系 + backHome）词条 |
| 修改 | `src/i18n/locales/{zh-cn,en-us}/home.json` | 骨架文案 → 正式首页文案（hero + directory）；phaseNote 递归更新到 Phase 3 |
| 修改 | `src/i18n/resources.ts` / `locale-context.ts` / `use-locale.ts` / `index.ts` | nav 命名空间注册（Widen/satisfies 互证扩到三包）；新增 `useNav` |
| 修改 | `src/i18n/locale-provider.tsx` | 路由感知重构（useLocation/useNavigate 单通道） |
| 修改 | `src/App.tsx` / `src/main.tsx` | App 挂 PortalRouter；main.tsx 保留挂载前 URL 前缀拦截，LocaleProvider 移入 Router 内部 |
| 修改 | `package.json` / `package-lock.json` | react-router-dom 依赖 |
| 删除 | `src/components/Nav.tsx` / `src/components/Footer.tsx` | Phase 1 旧骨架组件，迁移至 `src/components/layout/`（任务 3.1 新位置） |

双语注释铁律：以上触碰的全部 ts/tsx 文件注释均为「中文在上、英文语义重写在下」。

## V3.1.1 实测（三绿，2026-11-16）

- `npm run typecheck` → exit 0（首跑暴露 1 处 JSX 方括号成员表达式语法错误 `SECTION_PAGES[id]`，改为局部常量后通过——修复即重跑，非跳过）
- `npm run lint` → exit 0
- `npm run build` → exit 0，产物：`dist/index.html 0.94 kB` + `CSS 12.36 kB` + `JS 182.55 kB`（✓ built in 2.27s）

## V3.1.2 实测（双语导航走查，dev :6203 strictPort，playwright 驱动）

- 切换器实测：`/zh-cn/` 首页点击「切换语言」→ URL `http://localhost:6203/en-us/`、`<title>` 与 h1 全切换为 en——通过
- 逐板块路由可达：10 路由（home + 9 板块）× 2 语言 = **20 路全可达**，每页 navLinks=10、h1 逐页断言通过（zh：方法论/规划原文/决策时间线/迭代时间线/任务证据链/E2E 旅程/指标仪表盘/治理与开放/复现指南；en：Methodology/Planning Documents/Decision Timeline/Iteration Timeline/Task Evidence Chain/E2E Journey/Metrics Dashboard/Governance & Openness/Reproduction Guide）
- console 红错：**0**（consoleErrors=0，含 pageerror）
- 截图归档：`$ART/screenshots/` 20 张，`{页面}-{语言态}.png` 命名（10 页 × 2 态）
- `grep -rn "TODO\|placeholder" src/i18n/locales | wc -l` → **0**（无占位残留）

## V3.1.3 实测（词条编译期校验）

- `npm run typecheck` exit 0——`Widen`/`satisfies` 互证（en 包结构绑定 zh 包，缺 key 即编译失败）
- zh/en key 集合机械 diff（python 展平嵌套 JSON，点号路径）：

| 命名空间 | zh keys | en keys | en 侧缺失 | zh 侧缺失 |
|---|---|---|---|---|
| common | 24 | 24 | 0 | 0 |
| home | 9 | 9 | 0 | 0 |
| nav | 60 | 60 | 0 | 0 |

- 合计缺失 0——PASS。

## 收口冒烟（执行规则 6）

- `npm run preview`（:6204 strictPort）：`/zh-cn/` → 200；深链 `/zh-cn/timeline` → 200（SPA fallback 生效，nginx try_files 由 Phase 4 容器化承接）；`<title>` 正确；`dist/` 产物存在。
- 走查后清理：dev/preview 进程已按端口 kill，浏览器会话已关闭。

## 诚实备注（不美化）

1. **字体包未引入**：`@fontsource-variable` 字体包（Oxanium/Noto Sans SC 等设计 tokens 字面）仍延后（main.tsx 注释保留原口径）——当前渲染回落系统字体栈，视觉与 website 终态有差距；后续任务需要时再引入（非本任务改动清单项）。
2. **首页导览长文未接**：`portal-content/overview/` 的 index/timeline md 渲染依赖渲染器（任务 3.6），当前首页 hero + 卡片目录为任务 3.1 范围的布局态。
3. **板块页为占位实现**：九板块页只呈现「规划中」卡片与交付任务号（D6），无数据渲染——这按任务定位（路由与布局骨架）即为完成态，不是欠账。
4. **代码未提交**：portal 仓变更未提交（Phase 3 风险与备注口径——六任务代码变更提交时机由用户决定）。
