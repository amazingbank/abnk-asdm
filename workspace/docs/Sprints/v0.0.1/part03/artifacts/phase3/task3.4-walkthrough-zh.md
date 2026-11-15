# Part03 · Phase 3 · 任务 3.4 —— 全页面双语走查记录（zh 态）

- **日期**：2026-11-12
- **载体**：web（`flutter run -d web-server --web-port=6280 --dart-define=ABNK_ENABLE_SEMANTICS=true`，mock 模式；日志归档本目录 `task3.4-flutter-run.log`）
- **走查工具**：agent-browser（自动化 Chromium）+ 语义树快照 + 语义节点激活（对齐任务 3.3 惯例）
- **登录口径**：alice / password（P1.3 mock 口径）
- **zh 态设定**：`localStorage['flutter.abnk.locale'] = "\"zh\""`（shared_preferences web 键）后刷新——启动期 `resolveInitialLocale` 读回 zh

## 判据逐项记录

| 页 | 判据（文案与 app_zh.arb 一致） | 实测结果 | 证据 |
|---|---|---|---|
| login | 手机银行 / 用户名 / 密码 / 登 录 / 指纹占位说明 | 全命中（`loginTagline`/`fieldUsername`/`fieldPassword`/`loginSubmit`/`loginPlaceholderNote`） | 快照 StaticText ×5；密码框 `fill` 不达 Flutter 控制器时校验词条「请输入密码」（`fieldPasswordRequired`）即时可见 |
| home | ABNK 手机银行 / 欢迎回来 / 你好，Alice Green / 活期总余额 / 转账·定期·贷款·明细 / 账户卡片插值 | 全命中（`appName`/`homeWelcome`/`homeGreeting{name}` 插值「你好，Alice Green」/`homeTotalSavingsBalance`/`homeAction*`+`nav*`/`accountTitle{name,accountNo}`「ABNK 活期储蓄（0000**0011）」+`homeAvailableBalance{amount}`「可用余额 ¥10,000.00」） | 截图 `task3.4-zh-home.png` |
| transactions | 交易明细 / 选择账户 / 存入（枚举）/ 余额插值 | 全命中（`txTitle`/`txSelectAccount`/`txTypeDeposit` 经 `transactionTypeLabel` 映射「2027-01-17 · 存入」/`txBalanceLabel{amount}`「余额 ¥10,000.00」） | 截图 `task3.4-zh-transactions.png` |
| transfer | 本人转账 / 转出账户 / 转入账户 / 转账金额（CNY）/ 附言（选填）/ 提交转账 + 金额校验 | 全命中；输入 0 提交 → 「请输入有效金额」（`formAmountInvalid`）；Material 内建计数器「还可输入 40 个字符」随 delegates 呈中文 | 截图 `task3.4-zh-transfer.png`、`task3.4-zh-transfer-validation.png` |
| fixed_deposit | 定期存款 / 转出活期账户 / 存入金额（CNY）/ 开立定期账户 / 年利率·期限·起存 / 12 个月 | 全命中（`fdTitle`/`fdSourceAccountLabel`/`fdAmountLabel`/`fdSubmit`/`metricInterestRate`/`metricTerm`/`metricMinDeposit`/`monthsOption{months}`）；输入 100 提交 → 「低于起存金额 ¥1,000.00」（`fdBelowMinDeposit{amount}` 插值） | 截图 `task3.4-zh-fixed-deposit.png`、`task3.4-zh-fd-validation.png` |
| loans | 消费贷款 / 年利率 / 最长 12 个月 / 还款方式 / 等额本息（枚举）/ 额度区间 / 申请贷款 + 申请表单 | 全命中（`loansTitle`/`metricInterestRate`/`termUpTo{months}`/`metricRepaymentMethod`/`repaymentEqualInstallments` 经 `repaymentMethodLabel` 映射/`loanAmountRange{min,max}`「额度 ¥1,000.00 ~ ¥500,000.00」/`loanApply`）；表单：申请 ABNK 消费贷（`loanApplyTitle{name}`）/ 申请金额（CNY）/ 期限（月）+12 个月 / 用途（选填）/ 提交申请 | 截图 `task3.4-zh-loans.png`、`task3.4-zh-loan-apply.png` |
| profile | 我的 / AMAZING BANK 个人客户 / 客户资料 / 用户名 / 客户编号 / 证件信息（只读）/ 证件类型·号码·签发·有效期 / 已过期（枚举）/ 语言·中文·English / 退出登录 / 原型说明 | 全命中（`navProfile`/`profileBadge`/`profileCustomerInfo`/`fieldUsername`/`profileCustomerId`/`profileIdentitySection`/`profileDoc*`×4/`identityStatusExpired` 经 `identityStatusLabel` 映射/P3.3 既有区块/`profileLogout`/`profilePrototypeNote`） | 截图 `task3.4-zh-profile.png` |

## console 检查

- 走查全程 `agent-browser console` grep `\[error\]|Uncaught` 计数 **0**；`agent-browser errors` 无页面错误。

## 说明

- 产品名（ABNK 活期储蓄/ABNK 消费贷）、产品描述、流水 note（初始存入）、证件号码/日期等为 fixtures **数据**（D3 数据边界，Phase 4 双语数据集处理），非 UI 词条，不随语言切换——zh 态恰为中文，与词条口径不冲突。
- 密码框 `fill` 值经 DOM 直接注入不达 Flutter 控制器（obscure 控件特性），改 `type` 逐键输入后正常——走查操作口径备注。
- 页签切换/返回/遮罩关闭：普通 click 与语义节点合成 click 均为真实浏览器事件链路（3.3 惯例）。

## 结论

zh 态七页全部文案与 `app_zh.arb` 词条逐项一致（含全部插值模板与三处枚举映射），console 0 红错——V3.4.4 通过。
