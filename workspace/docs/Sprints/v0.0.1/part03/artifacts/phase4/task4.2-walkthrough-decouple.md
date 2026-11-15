# 任务 4.2 · V4.2.6 走查记录 —— 数据语言与 UI 语言解耦（en 数据 + zh UI）

- 日期：2026-11-12
- 载体：`flutter run -d web-server --web-port=6280 --dart-define=ABNK_DATA_LOCALE=en-us --dart-define=ABNK_ENABLE_SEMANTICS=true`（日志就绪判据：:6280 LISTEN + HTTP 200）
- UI 语言机制：预置 `localStorage['flutter.abnk.locale'] = '"zh"'` 后刷新（存储合法值优先，`resolveInitialLocale` D1 口径）→ 刷新后登录页即刻呈中文（「手机银行」「登 录」），而数据集为 en-us——解耦成立的第一断言
- 自动化：agent-browser（语义树快照 + 截图），对齐 Phase 3 走查惯例

## 走查矩阵（zh UI 框架 / en 数据）

| 页面 | UI 框架（zh，arb 词条） | 数据（en-us 数据集） | 判定 |
|---|---|---|---|
| 登录 | 手机银行 / 用户名 / 密码 / 登 录 | alice/password 登录成功（凭据不随数据集变） | ✅ |
| 首页 | ABNK 手机银行 / 欢迎回来 / 你好，Alice Green / 活期总余额 / 活期账户 / 转账·定期·贷款·明细 | 账户名 `ABNK Current Savings（0000**0011/0012）` | ✅ 截图 `task4.2-en-home.png` |
| 明细 | 交易明细 / 选择账户 / 存入 / 支取 / 余额 | 存量 note `Initial deposit`；账户名 `ABNK Current Savings` | ✅ 截图 `task4.2-en-transactions.png` |
| 转账 | 本人转账 / 转出账户 / 转入账户 / 转账金额（CNY）/ 附言（选填）/ 提交转账 | 账户名 en | ✅ |
| 转账成功对话框 | 流水号 100 / 转出账户新余额：¥9,990.00 / 知道了 | — | ✅ |
| **转账兜底 note**（无附言 ¥10 转账 11→12） | 支取 / 余额（框架中文） | 新流水 note = **`Self transfer`**（`transferNoteFor('en-us')`）2026-11-12 · 支取 -¥10.00 · 余额 ¥9,990.00 | ✅ 硬断言 |
| 定期 | 定期存款 / 转出活期账户 / 存入金额（CNY）/ 开立定期账户 / 年利率 / 期限·个月 / 起存 | 产品名 **`ABNK Fixed Deposit`** + 描述 `Lump-sum term deposit with interest paid out at maturity on the same calendar day`（D2 语义重写） | ✅ |
| 定期开户成功对话框 | 新定期账户：0000**0200 / 到期日：2027-11-12（对年对月对日）/ 知道了 | — | ✅ |
| **定期开户兜底 note**（¥1,000 开立，账户 11） | 支取 / 余额（框架中文） | 新流水 note = **`Fixed deposit opening`**（`fixedDepositOpenNoteFor('en-us')`）2026-11-12 · 支取 -¥1,000.00 · 余额 ¥8,990.00 | ✅ 硬断言 |
| 贷款 | 消费贷款 / 申请贷款 / 年利率 / 期限 / 还款方式 / 等额本息 / 额度 | 产品名 **`ABNK Consumer Loan`** + 描述 `Amortizing personal loan with equal monthly installments, due on the same day each month` | ✅ |
| 我的 | 我的 / 客户资料 / 证件信息（只读）/ 语言·中文·English / 退出登录 | 证件号码/签发日期/有效期自 en-us identity.json 渲染（3301\*\*\*\*\*\*\*\*\*\*001X / 2015-01-01 / 2020-01-01）；状态 chip「已过期」zh 词条 | ✅（见下方说明） |

## console 判据

- `agent-browser errors` → 空（无页面错误）
- `agent-browser console` → 0 条 error/exception；仅 Flutter 框架语义树 warning（`Semantic node ... scopesRoute/namesRoute`，semantics define 场景的框架级噪音，非红错）

## 已知显示边界（既有行为，非本任务缺陷）

- **证照类型名（`National ID`）不在屏渲染**：`_InfoCard` 第 0 行 trailing 被 `_IdentityStatusChip`（已过期）占位、值槽位不渲染（`profile_page.dart:324-325`）——Phase 3 起的既有显示设计（Phase 3 zh 走查归档 `task3.4-walkthrough-zh.md` 同口径：证件类型行只记枚举 chip，「身份证」同样不显示）。
- **en 数据归属证明（间接链）**：`fixtureDirFor(dataLocale)` 为全部 5 个 fixture 的唯一路径决策（同一编译期常量），accounts/transactions/loan_products 三套在屏数据均实证 en-us 目录；identity.json 与 me.json 经同一函数加载，en 归属成立（`documentTypeName: "National ID"` 在 en 文件在场已由 V4.1.2 结构比对确认）。

## 截图归档

- `task4.2-en-home.png`（首页：zh 框架 + ABNK Current Savings）
- `task4.2-en-transactions.png`（明细：Initial deposit + Self transfer）
- `task4.2-en-profile.png`（我的：zh 框架 + en 证照字段 + 已过期 chip）

## 结论

V4.2.6 全部断言通过：UI 框架/表头/按钮全程中文，账户产品名、交易 note（含两条兜底串 `Self transfer` / `Fixed deposit opening`）、贷款产品名与描述、证照字段为 en-us 数据集内容；登录凭据不随数据集变；console 0 红错。
