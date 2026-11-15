# Task P1.3 web 载体走查记录（ABNK 手机银行 mock 原型）

- 日期：2026-11-07
- 载体：`flutter run -d web-server --web-port 6280`（Chrome 内核浏览器，视口 390×844）
- 驱动：playwright-cli + Flutter web 语义树（a11y）；截图目录 `artifacts/phaseP1/screenshots/`
- 数据：mock（fixtures/*.json，P0.3 种子快照口径）；登录口令 alice / password（原型专用明文）

## 走查路径（七页面主路径，每步截屏）

| # | 页面 | 操作 | 观察结果 | 截图 |
|---|------|------|----------|------|
| 1 | 登录 | 打开首页 | **ASDM logo**（螺旋标志，2026-11-07 增补）+ 品牌 serif 大标题 + eyebrow + 铜色主按钮 + 指纹/安全键盘视觉占位（范围外标注） | `web-01-login.png` |
| 2 | 首页 | alice 登录 | 问候语「你好，Alice Green」；活期总余额 ¥10,000.00；账户卡片 0000**0011/0012；快捷操作四入口 | `web-02-home.png` |
| 3 | 转账 | 首页 → 转账；11→12，¥2,500，附言「还房贷」，提交 | 成功对话框：流水号 100 + 转出账户新余额 ¥7,500.00 | `web-03-transfer.png` / `web-03b-transfer-success.png` |
| 4 | 定期 | 返回首页 → 定期；选产品（3.0% / 12 个月 / 起存 ¥1,000），存 ¥5,000，开户 | 成功对话框：新定期账户 + 到期日（对年对月对日）；转出账户余额同步为 ¥7,500.00 | `web-04-fixed-deposit.png` / `web-04b-fd-success.png` |
| 5 | 贷款 | 底部页签「贷款」；产品卡（12.0% / 最长 12 个月 / 等额本息）；申请 ¥20,000 | 底部弹层表单 → 提交 → snackbar「申请已提交（贷款编号 900），等待审批」 | `web-05-loans.png` / `web-05b-loan-apply.png` / `web-05c-loan-submitted.png` |
| 6 | 明细 | 底部页签「明细」（转账后） | 新流水「还房贷 -¥2,500.00 余额 ¥7,500.00」+ 种子流水「初始存入 +¥10,000.00」，runningBalance 列可见 | `web-06-transactions.png` |
| 7 | 我的 | 底部页签「我的」 | 客户资料（alice / 28）+ 证照信息只读（身份证 / 2020-01-01 / 状态 chip「已过期」——中性展示，无过期横幅/拦截分支）+ 退出登录 | `web-07-profile.png` |

核心闭环（对齐旅程 Step 8）：**交易成功 → 明细出现新流水**，三载体（web / iOS / Android）一致验证通过。

## console 观察记录

- 未捕获异常（红错）：**0**
  - 过程修复 1 例：390px 窄视口下账户下拉 InputDecorator 溢出 29px（RenderFlex overflow）→
    `DropdownButtonFormField` 加 `isExpanded: true` 后消除
- warning：3 条（Flutter 框架语义路由标签提示 "route is currently ignored / always ignored"，
  框架层提示、非应用异常，不阻塞验收——归档说明）

## 范围备注（显式不做，POC 演示增量承接）

- 证照过期横幅与 403 交易拦截（旅程 Step 3/9 增量；错误框架已预留 ForbiddenException 语义分支）
- 指纹登录 / 安全键盘（视觉占位）
- 定期到期 / 贷款还款流（原型范围外）
