# Task 1.7 界面走查记录 —— utils/format.ts 金额/数字格式 locale 参数化

- 日期：2026-11-12
- 环境：dev server `http://localhost:6203`（Vite v7.3.7，改动已被 dev server 感知）；浏览器自动化 = playwright-cli（Chromium）；mock 会话（admin/password）
- 快照证据：`task1.7-snapshots/`（v173-en-loanops / v173-zh-loanops）
- 实现口径：`formatMoney` 的 locale 来源 = i18n 模块级语言快照 `getCurrentLocale()`（`locale.ts` 可变快照，由 `LocaleProvider` 每次渲染同步写入，纯函数无 hook 读取），映射 `'zh-cn' → 'zh-CN'` / `'en-us' → 'en-US'`（`INTL_LOCALES`）——全部既有调用点零改动

## V1.7.3 金额格式两态回归（贷款运营页本金列）

| 断言项 | 英文态（en-US） | 中文态（点击切换器就地翻转，无刷新） |
|---|---|---|
| `document.documentElement.lang` | `"en-US"` | `"zh-CN"` |
| 本金列金额 | `¥50,000.00` ✅ | `¥50,000.00` ✅ |
| 格式判据 | 千分位 + 两位小数 + ¥ 货币前缀 ✅ | 同左 ✅ |

- 佐证：zh-CN 与 en-US 的 Intl 数字分组对 CNY 两位小数形态一致（均为 `50,000.00`），判据为「格式随 locale 生效且无回归」——机制已 locale 化（`INTL_LOCALES[getCurrentLocale()]`），两态渲染均正确
- 附带证据（任务 1.6 走查中已录）：客户列表 dataNote 的 `{money}` 插值两态均为 `¥10,000.00`；客户详情活期余额/贷款本金列（formatMoney 调用点）两态渲染正常

## V1.7.2 静态核验摘要（同轮实测）

- `grep -n "zh-CN" src/utils/format.ts` → 仅第 7 行 `INTL_LOCALES` 映射表达式内出现一次，无独立写死字面量 ✅

## Console 检查

走查全程 console 0 红错（仅 React DevTools INFO 提示）。

## 结论

V1.7.1–V1.7.3 全部通过：`formatMoney` locale 参数化落地（调用点零改动），金额两态正确渲染且随语言就地联动。

## 截图证据（`task1.7-screenshots/`，2026-11-12 补录，playwright-cli 1440×900）

| 文件 | 状态 |
|---|---|
| `loanops-money-zh.png` | 中文态贷款运营页：本金列 `¥50,000.00`（千分位 + 两位小数 + ¥ 前缀） |
| `loanops-money-en.png` | 英文态同页面同列 `¥50,000.00`（格式无回归；`getCurrentLocale()` 驱动） |
