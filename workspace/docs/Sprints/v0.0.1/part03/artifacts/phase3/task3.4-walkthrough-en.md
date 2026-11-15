# Part03 · Phase 3 · 任务 3.4 —— 全页面双语走查记录（en 态）+ 异常路径两语言态（V3.4.5/V3.4.6）

- **日期**：2026-11-12
- **载体**：web（`flutter run -d web-server --web-port=6280 --dart-define=ABNK_ENABLE_SEMANTICS=true`，mock 模式；与 zh 走查同一进程）
- **走查工具**：agent-browser + 语义树快照 + 语义节点合成激活
- **en 态设定**：profile 页语言区块点 English（真实切换链路：`AppState.setLocale` → `notifyListeners` → MaterialApp 整树重建 + localStorage 持久化）

## V3.4.5 —— en 态七页走查（全部语义重写形态，非逐字直译）

| 页 | 实测结果（en 词条命中） | 证据 |
|---|---|---|
| login | Mobile Banking / Username / Password / Sign In / Fingerprint sign-in and the secure keyboard are visual placeholders (outside the POC scope) | 截图 `task3.4-en-login.png` |
| home | ABNK Mobile Banking / Welcome back / **Hi, Alice Green**（`homeGreeting` 语义重写）/ Total savings balance / Transfer · Term deposit · Loans · **Activity**（`navTransactions` US banking idiom）/ 账户卡片半角括号 `{name} ({accountNo})` / Available ¥10,000.00 | 截图 `task3.4-en-home.png` |
| transactions | Transactions / Select account / **Deposit**（枚举映射：存入↔Deposit）· Balance ¥10,000.00 | 截图 `task3.4-en-transactions.png` |
| transfer | **Transfer between my accounts**（`transferTitle` 语义重写）/ From account · To account / Amount (CNY) / Note (optional) / Transfer；校验词条 **Enter a valid amount**；Material 内建：Back（返回箭头 tooltip）/ 40 characters remaining | 截图 `task3.4-en-transfer.png` |
| fixed_deposit | Term deposits / Interest rate · Term · Minimum / 12 months / **Funding savings account**（`fdSourceAccountLabel` 语义重写）/ Amount (CNY) / Open term deposit | 截图 `task3.4-en-fixed-deposit.png` |
| loans | **Personal loans**（`loansTitle` 语义重写——消费贷款 US banking idiom）/ Interest rate · Term · Up to 12 months / Repayment · **Equal monthly installments**（枚举映射：等额本息↔Equal monthly installments，D2 示例词条）· Amounts from ¥1,000.00 to ¥500,000.00 / Apply now | 截图 `task3.4-en-loans.png` |
| profile | Profile / AMAZING BANK **Retail Customer**（`profileBadge` 语义重写）/ Customer profile / Username · Customer ID 28 / Identity documents (read-only) / Document type · Document number · Date issued · Valid until / **Expired**（枚举映射：已过期↔Expired）· Language 区块（中文/English 原生形态不翻译 ✓）/ Sign out / ABNK Mobile Banking prototype (mock data) | 截图 `task3.4-en-profile.png`（语言切换瞬间整树重建：我的→Profile 即时生效） |

### 三处枚举映射两态抽查汇总（专项判据）

| 枚举 | zh 态 | en 态（语义重写） |
|---|---|---|
| 交易类型（transactions，`transactionTypeLabel`） | 存入（2027-01-17 · 存入） | Deposit（2027-01-17 · Deposit） |
| 证照状态（profile，`identityStatusLabel`） | 已过期 | Expired |
| 还款方式（loans，`repaymentMethodLabel`） | 等额本息 | Equal monthly installments |

### console 检查

- en 态走查全程 `agent-browser console` grep `\[error\]|Uncaught` 计数 **0**。

### 数据边界观察（D3）

- en 态下产品名（ABNK 活期储蓄/ABNK 定期存款/ABNK 消费贷）、产品描述、note（初始存入）仍为中文——fixtures 数据不随 UI 语言切换，Phase 4 双语数据集（`--dart-define ABNK_DATA_LOCALE`）处理，与 backoffice V2.2.4 同口径。

## V3.4.6 —— 异常路径两语言态（码化链路端到端）

| 态 | 操作 | 实测 SnackBar 提示 | 对应词条 |
|---|---|---|---|
| en | alice + 错误口令 wrongpass 登录 | **Incorrect username or password** | `errAuth` en（语义重写：非「用户名或密码错误」直译） | 
| zh | 同操作 | **用户名或密码错误** | `errAuth` zh |

- 链路：MockAuthRepository `throw const AuthException()`（code=`err.auth`）→ `AppExceptionPresenter.present(e, l10n)` 按 `l10n.errAuth` 查词条 → SnackBar——api 层零中文、UI 层按语言解析的码化链路端到端验证通过。
- 截图：`task3.4-en-login-error.png`、`task3.4-zh-login-error.png`（zh 态经 localStorage 偏好 reload 切回后对称执行）。

## 结论

en 态七页全部文案为语义重写形态 en 词条（无逐字直译痕迹、无中英夹杂——数据文案除外属 D3 边界）；三处枚举映射两态抽查全部通过；异常路径码化链路两语言态对称成立；console 0 红错——V3.4.5 / V3.4.6 通过。
