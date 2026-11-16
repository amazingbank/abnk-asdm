---
sprint: v0.0.1
part: part04
phase: 3
status: completed
date: 2026-11-16
evidence: ../
locale: zh-CN
---
# 任务 3.2 —— 迭代时间线四层下钻页（灵魂页面）走查记录

- 日期：2026-11-16；执行人：AI（abnk-debugger 会话）
- 定位：portal 核心叙事「证据链可被点击验证」的实现层——Sprint → Part → Phase → Task 四层下钻，每层链到证据指针与文档原文；移交往返链与挂账标记如实显示（D6）。

## 执行时决策记录

| 决策点 | 结论 | 依据 |
|---|---|---|
| 索引 TS 消费形态（已知坑 7） | **决策①：生成器补产 `sprint-v0.0.1.json`** | D4「提取入库、构建纯复制」的自然延伸——portal 保持零运行时解析；契约双侧同步（生成器 + schema.ts）；`sample.check.ts` 升级为锁真实产物（一次性 yaml 转换样例 `sprint.sample.json` 废弃删除，gitignore 区内无入库影响） |
| 移交往返链数据载体 | **生成器新增 `moved_links` 结构化字段**（人工维护常量 MOVED_LINKS，与 BLOCKED_ITEMS 同口径） | 索引中任务级移交仅有状态标记与 note 文本（「🔁 已移交 Part04」），往返跳转需要结构化两端点；fail-loud 校验三重：端点存在、from 侧 moved 状态、moved 任务与链守恒（moved=2 = links=2） |
| 证据/文档资产通道 | 构建期 `import.meta.glob ?url` 直供（133 文本证据件 + 24 文档复制进 dist/assets） | 已知坑 1 的文本资产形态——二进制截图不 import（走 3.5/3.6 的 public/evidence 清单通道）；md 懒加载拆分随任务 3.6 接管 |
| 五形态徽标覆盖六值词表 | done←completed、doing←in_progress/draft、pending←pending、moved←moved、suspended←planned-backlog（词表外保守档） | 标签文案始终取状态词表原词（draft/planned-backlog 各有如实标签），档位只决定视觉——「渲染呈现状态、不判定状态」 |
| 任务↔Phase 归属 | 任务 id 前缀（`P2.4`→P2、`5.5`→5） | 索引任务为 Part 级扁平结构，前缀归属是零新契约的推导；全部 74 任务归属核对见 V3.2.3 |

## 改动清单

| 类别 | 仓 | 文件 | 说明 |
|---|---|---|---|
| 修改 | abnk-asdm | `.asdm/scripts/gen-sprint-index.py` | JSON 补产 + `moved_links` 输出 + 守恒校验 + `--verify` 三产物齐核 + 头部文档 |
| 修改 | abnk-asdm | `workspace/index/sprint-v0.0.1.yaml` | 再生成：新增 `moved_links`；part04 任务 3.1 状态随源 Plan 表勾选刷新为 completed |
| 新建 | abnk-asdm | `workspace/index/sprint-v0.0.1.json` | 索引 JSON 形态（任务 3.2 起 TS 构建消费） |
| 修改 | portal | `src/data/schema.ts` | `MovedLink` 接口 + `SprintIndex.moved_links` 必填（契约双侧同步） |
| 修改 | portal | `src/data/sample.check.ts` | 互证锁升级：消费真实 JSON 产物（原一次性样例删除） |
| 新建 | portal | `src/lib/link-resolver.ts` | 内链路由转换层单点：四层路由拼装 / 任务引用解析 / 文档与证据 ?url 资产映射 / 相对链接解析（3.6 渲染管线消费，树外降级源仓 GitHub 镜像） |
| 新建 | portal | `src/pages/timeline/`（8 文件） | timeline-data（索引加载+派生）/StatusBadge（五形态）/TimelineBreadcrumb/SprintView/PartView/PhaseView/TaskView/TimelinePage（Outlet 壳） |
| 新建 | portal | `src/i18n/locales/{zh-cn,en-us}/timeline.json` | 四层下钻词条（状态词表/层级标题/移交往返/诚实空态）；en 语义重写 |
| 修改 | portal | `src/i18n/` 注册四文件 + `src/router.tsx` | timeline 命名空间注册；四层嵌套路由（旧 `src/pages/TimelinePage.tsx` 占位删除） |

## V3.2.1 实测（三绿 + 纯度）

- typecheck ✅ / lint ✅（首跑 2 个未用变量 + 1 个 react-refresh 警告，即修后零警告）/ build ✅
- 纯度判据 `grep -rn "yaml\|front-matter" src/pages/timeline/ | wc -l` → **0**（页面零原始格式耦合）
- 生成器侧：`index OK: parts=4 docs=24 tasks=74 moved=2 moved_links=2` + `--verify` 三产物一致

## V3.2.2 实测（三路径走查，dev :6203）

- **路径①（证据指针可达）**：Sprint → part02 → phase/P2 → task/P2.4 → 证据指针 `taskP2.4-transfer-evidence.txt` HTTP **200**，文件身份断言通过
- **路径②（移交往返链）**：phase5 `moved_to=part04:1.1` 渲染 → 任务 5.5「已移交」徽标 + `data-moved-to` 链接 → 跳转 part04/task/1.1（`data-moved-from=part03:5.5` 承接来路显示）→ 回跳 5.5——**双向往返成立**
- **路径③（插入性质标记）**：phase 7「插入性质（D3 修订触发）」chip 可见
- **五形态徽标盘点**：已完成/进行中/待执行/已移交/路线占位 全部 VISIBLE（挂账说明随 note 原样呈现，如 P3.6「⏸ 挂账——Apple 账号条件门」）
- **console**：纯应用页面 0 红错；裸证据文档顶级导航时浏览器自动请求 `/favicon.ico` 404 为环境行为（站点声明 `favicon.svg` 正常工作——诚实记录，不隐藏）
- 截图 10 张归档 `$ART/screenshots/`（timeline 系列：sprint/part02/phaseP2/task-P2.4/证据文件/part03-phase5/task-5.5/part04-task-1.1/part03-phase7/task-P2.4-en-us）

## V3.2.3 实测（覆盖完备，机械比对）

playwright 脚本由真实索引 JSON 生成（非人工抄写期望值）：

| Part | phase 行（DOM/期望） | task 行（DOM/期望） | 判定 |
|---|---|---|---|
| part01 | 4/4 | 8/8 | COUNT-OK |
| part02 | 5/5 | 23/23 | COUNT-OK |
| part03 | 8/8 | 26/26 | COUNT-OK |
| part04 | 6/6 | 17/17 | COUNT-OK |

- 合计 phase 23、task 74——与索引 docs=24（含 1 篇无 phase 伴生文档）/tasks=74 零漂移，**全量 Phase/Task 零遗漏**
- 23 phase + 74 task 逐层钻取 h1 非空；页面全部证据链接逐个 GET 断言 HTTP 200；探针 287、失配 0、console 0

## 诚实备注（不美化）

1. **证据裸文档的中文编码观感**：`.txt` 证据件以 `text/plain` 无 charset 头直供，浏览器顶级导航打开时中文按传统编码显示（乱码观感）。指针可达性判据（HTTP 200 + 文件身份）已过；**正文渲染形态随任务 3.6 DocView/素材卡接管**（内联渲染携带正确编码），nginx 侧 charset 由任务 4.1 容器化承载。
2. **en-US 深链内容 zh 回退**：en 态时间线的 UI 词条（徽标/标题/标签）为 en，任务/文档标题等内容按 D3 fallback 显示 zh 原词——内容 en 语义重写是 roadmap 级增量，不是本任务欠账。
3. **eager 资产映射的包体**：当前证据/文档 ?url 映射 eager 进主包（JS 481 kB / gzip 149 kB），懒加载拆分（import.meta.glob 非全 eager + 路由级 chunk）由 V3.6.1 判据接管——本任务验收判据不含该门槛。
4. **part03 非常规证据桶**（`poc-journey/`、`seed-en//`）不在 phase 目录约定内，时间线 Phase 层不展示（避免虚构归属）；Part 级根证据通道已就位，全量分桶浏览随任务 3.6 EvidenceIndex。
5. **代码未提交**：两仓变更均未提交（Phase 3 口径——提交时机由用户决定）。
