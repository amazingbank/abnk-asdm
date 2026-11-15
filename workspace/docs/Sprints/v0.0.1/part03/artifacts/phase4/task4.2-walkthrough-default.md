# 任务 4.2 · V4.2.7 走查记录 —— 默认态回归（无 dart-define）

- 日期：2026-11-12
- 载体：`flutter run -d web-server --web-port=6280 --dart-define=ABNK_ENABLE_SEMANTICS=true`（**无** `ABNK_DATA_LOCALE` define → `dataLocale` 缺省 zh-cn；就绪判据 HTTP 200）
- UI 语言：localStorage `flutter.abnk.locale = "zh"`（沿走查会话预置）→ zh UI
- 前置收尾：停 V4.2.6 en 载体（`lsof -ti:6280 -sTCP:LISTEN | xargs kill` → 端口清空实测 0）
- 自动化：agent-browser（语义树快照 + 截图）

## 走查矩阵（zh UI + zh 数据，与 Phase 3 走查一致性回归）

| 页面 | UI 框架 | 数据（zh-cn 数据集） | 判定 |
|---|---|---|---|
| 登录 | 手机银行 / 登 录 | alice/password 成功 | ✅ |
| 首页 | 欢迎回来 / 活期总余额 / 转账·定期·贷款·明细 | `ABNK 活期储蓄（0000**0011/0012）`——中文回归无漂移 | ✅ 截图 `task4.2-zh-home.png` |
| 明细 | 交易明细 / 存入 / 支取 / 余额 | 存量 note `初始存入`（zh） | ✅ 截图 `task4.2-zh-transactions.png` |
| **转账兜底 note**（无附言 ¥10 转账 11→12，流水号 100） | 支取 / 余额 | 新流水 note = **「本人账户转账」**（`transferNoteFor('zh-cn')`）2026-11-12 · 支取 -¥10.00 · 余额 ¥9,990.00 | ✅ 硬断言（与 V4.2.6 `Self transfer` 对称） |
| 定期 | 定期存款 / 开立定期账户 / 年利率 / 起存 | 产品名 `ABNK 定期存款` + 描述 `整存整取，对年对月对日到期` | ✅ |
| 定期开户成功对话框 | 新定期账户：0000**0200 / 到期日：2027-11-12（对年对月对日） | — | ✅ |
| **定期开户兜底 note**（¥1,000 开立，账户 11） | 支取 / 余额 | 新流水 note = **「定期开户」**（`fixedDepositOpenNoteFor('zh-cn')`）2026-11-12 · 支取 -¥1,000.00 · 余额 ¥8,990.00 | ✅ 硬断言（与 V4.2.6 `Fixed deposit opening` 对称） |
| 贷款 | 消费贷款 / 申请贷款 / 等额本息 | `ABNK 消费贷` + `等额本息个人消费贷款，按月对日还款` | ✅ |
| 我的 | 客户资料 / 证件信息（只读）/ 语言 / 退出登录 | 证照字段 zh 数据（同 V4.2.6 边界：类型名不在屏渲染，Phase 3 既有设计） | ✅ 截图 `task4.2-zh-profile.png` |

## console 判据

- `agent-browser errors` → 空；`console` error/exception 计数 = 0（仅框架语义树 warning，同 V4.2.6）

## 收尾

- 归档后停载体：`lsof -ti:6280 -sTCP:LISTEN | xargs kill` → 实测 `port-listen=0`（端口清空 ✅）
- 浏览器会话关闭（`agent-browser close`）

## 截图归档

- `task4.2-zh-home.png`（首页：ABNK 活期储蓄）
- `task4.2-zh-transactions.png`（明细：本人账户转账 + 定期开户 + 初始存入）
- `task4.2-zh-profile.png`（我的）

## 结论

V4.2.7 全部断言通过：默认态（无 define）数据回归中文、无回归漂移；两条兜底 note 均为中文常量形态（「本人账户转账」/「定期开户」），与 V4.2.6 的 en 态构成 data_locale 两映射函数的双向运行时实证。
