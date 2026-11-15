# 任务 7.2 · V7.2.3 走查记录 —— mobile 数据集运行时随 UI 切换

- 日期：2026-11-12；载体：`flutter run -d web-server --web-port=6280 --dart-define=ABNK_DATA_LOCALE=en-us --dart-define=ABNK_ENABLE_SEMANTICS=true`（初始 en 数据）；UI 初始语言：预置 `localStorage['flutter.abnk.locale']='"zh"'`；自动化：agent-browser
- 改造机制：`FixtureBundle.activate`（目录运行时切换 + 清缓存）+ `Resettable` 接口（`MockAccountRepository.reset` 清账本/流水/账户）+ `AppState.dataEpoch`（`AbnkApp` home 子树 ValueKey remount → 页面 future 重拉）

## 断言矩阵

| # | 操作 | 预期 | 实测 | 判定 |
|---|---|---|---|---|
| 1 | zh UI 登录 → 首页 | zh UI + **en 初始数据**（解耦初始态，初始语言 = define 注入） | 框架中文（你好，Alice Green / 活期总余额）；数据 `ABNK Current Savings` | ✅ |
| 2 | 我的页语言区块 → English | en UI + en 数据（幂等） | UI 全英文（Welcome back / Home·Activity·Loans·Profile），数据仍 Current Savings；epoch remount 生效（页面回 Home） | ✅ |
| 3 | 语言区块 → 中文 | zh UI + **数据切换为中文数据集** | UI 中文（你好，Alice Green）；数据变 `ABNK 活期储蓄（0000**0011/0012）` | ✅ |
| 4 | 转账 ¥10（zh 态，流水号 100，余额 ¥9,990）→ 切 English | **内存态重置 + 数据集回 en**：余额回 ¥10,000、转账流水消失 | 首页余额 `Available ¥10,000.00`（9,990 重置）；明细仅 `Initial deposit`（无 Self transfer 流水）；数据 `ABNK Current Savings` | ✅ |
| 5 | console / errors | 0 红错 | errors 空、error 计数 0 | ✅ |

## 走查实施口径（工具层，非应用缺陷）

- agent-browser 对 Flutter ListTile 的语义 ref 点击在本页面不可靠（默认 720 高视口下语言区块在视口外，DOM `scrollintoview` 对 Flutter 自绘滚动无效）——判据改用 `get box` 取语义节点坐标 + `mouse move/down/up` 坐标点击，视口扩至 1280×1000 后语言区块全程在场、点击稳定命中。此为走查工具口径记录，应用侧点击链路在 widget 测试（`app_locale_test` ③ / `data_epoch_reset_test` ④）中已直接验证。

## 归档

- 截图：`task7.2-switched-en-reset.png`（切换 en 后余额/流水重置态）
- 载体收尾：走查后停载体，实测 `port-listen=0`；浏览器会话已关
