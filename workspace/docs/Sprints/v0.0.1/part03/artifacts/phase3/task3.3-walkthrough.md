# Part03 · Phase 3 · 任务 3.3 —— profile 页语言切换区块 web 载体走查记录

- **日期**：2026-11-12
- **载体**：web（`flutter run -d web-server --web-port=6280 --dart-define=ABNK_ENABLE_SEMANTICS=true`，mock 模式）
- **走查工具**：agent-browser（自动化 Chromium）+ 语义树快照/合成语义点击
- **登录口径**：alice / password（P1.3 mock 口径）

## 环境与方式说明

- 6280 端口走查前实测空闲（清理了一处残留监听后启动）；flutter run 日志归档于本目录 `flutter-run.log`。
- 走查以 `-d web-server` + 自动化浏览器替代手工 Chrome：判据本质（web 载体实测）不变。
- 交互方式说明：语言区块位于 profile 页视口下方，Playwright 坐标点击会落到底部导航（曾误触「贷款」页签）；故语言选项交互采用对 `flt-semantics[role=button]` 语义节点直接派发合成 `click` 事件（等价于无障碍激活），页签切换用稳定选择器 `[role=tab][aria-label="我的"]`。两种方式均为真实浏览器事件链路。

## 判据逐项记录

| # | 判据 | 实测结果 | 证据 |
|---|---|---|---|
| 1 | 初始语言跟随系统（D1 顺带验证） | 走查浏览器系统语言 en-US、localStorage 为空 → 启动即 en：语言区块标题 `Language`，`document.title = "ABNK Mobile Banking"`（onGenerateTitle en 词条） | 快照 StaticText "Language"；eval `JSON.stringify(Object.keys(localStorage))` = `[]` |
| 2 | 点「中文」→ 区块标题即时切换 | `Language` → **`语言`**；页签仍停留「我的」；页面其余文案仍中文（任务 3.4 预期边界） | 快照 StaticText "语言"、tab "我的" [selected]；截图 `task3.3-zh-switched.png` |
| 3 | 点「English」→ 标题切回 en 词条 + 持久化写入 | `语言` → **`Language`**；localStorage 写入 `flutter.abnk.locale = "en"`（shared_preferences web 键前缀） | 快照 + eval localStorage；截图 `task3.3-en-switched.png` |
| 4 | 热重启（R）后仍英文 | `Performing hot restart... 401ms / Restarted application in 401ms`；重启后登录页 `document.title = "ABNK Mobile Banking"`；重新登录进「我的」→ 标题仍 **`Language`**（持久化 en 经启动期 resolveInitialLocale 读回） | flutter-run.log 热重启两行 + 快照 StaticText "Language" |
| 5 | 切回中文对称成立 | `Language` → **`语言`**；localStorage 更新为 `flutter.abnk.locale = "zh"`；页签仍「我的」 | 快照 + eval localStorage；截图 `task3.3-zh-restored.png` |
| 6 | 页签保持（坑 6 正交断言） | 全程语言切换（含 en↔zh 双向）后页签均为「我的」[selected]，IndexedStack 索引不丢 | 各步快照 tab "我的" [selected] |
| 7 | console 无红色错误 | 纯切换交互期（清空控制台后 en→zh→en 双向切换）**0 条 [error]/Uncaught**；唯一一次 `Trying to render a disposed EngineFlutterView` 出现在热重启帧竞态（Flutter web 引擎级瞬态，非业务错误，重启后功能正常） | `agent-browser console` grep 计数 0 |

## 截图清单（本目录）

| 文件 | 内容 |
|---|---|
| `task3.3-zh-before.png` | zh 态基线（首次会话，含语言区块） |
| `task3.3-zh-switched.png` | 点「中文」后：标题 `语言` |
| `task3.3-en-switched.png` | 点「English」后：标题 `Language` |
| `task3.3-zh-restored.png` | 热重启验证后切回中文：标题 `语言` |

## 结论

任务 3.3 全部判据通过：语言区块渲染、即时切换（locale → MaterialApp 整树重建链路）、shared_preferences 持久化（重启读回）、双向对称切换、页签正交保持、控制台纯交互期零错误。
