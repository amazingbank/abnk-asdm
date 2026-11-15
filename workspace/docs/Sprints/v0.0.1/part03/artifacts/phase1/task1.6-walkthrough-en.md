# Task 1.6 界面走查记录（英文态）—— pages/components 全量词条替换 + 插值断言

- 日期：2026-11-12
- 环境：dev server `http://localhost:6203`（Vite v7.3.7）；浏览器自动化 = playwright-cli（Chromium）；mock 登录 admin/password
- 取态：`localStorage.abnk-locale=en-us` + `location.reload()` 后断言；走查路径与中文态对称（loan-ops 就地 reload 核对 → detail → clients → logout → login）
- 快照证据：`task1.6-snapshots/`（v164-en-*，共 6 份；连同中文态 10 份共 16 份归档）
- 数据值说明：数据内容（如姓名「王POC-…」、证照类型「身份证」）为 mock 数据集内容，双语数据集属 Phase 2 任务 2.2（决策 D3：运行时切换语言不切数据集）——本断言只覆盖 UI 词条层。displayName 于 2026-11-12 按用户拍板改为语言中性英文 `ABNK Operations Admin`（operators.json 单值）

## 1) loan-ops（reload 就地核对）

- 标题 `Loan Operations`、只读 Alert 英文文案 ✅
- 表头 8 列：Loan ID / Client / Product / Principal / Interest Rate / Term (months) / Status / Actions ✅
- 逾期标签 `Overdue for 40 days (ABNK_POC_OD)`——**语义重写形态**（英语句式 "Overdue for N days"，非逐字直译）✅
- 禁用按钮 `Approve` / `Disburse` + 数据口径注脚英文（Data source: P0.3 seed snapshot …）✅

## 2) client detail

- `Back` 按钮、标题 `Client Details · 王POC-A1107104347`（{name} 插值）✅
- Client Profile 卡：Client ID / External ID / Name / Mobile Number / Email / Branch / Status ✅
- Identity Documents (editable) 卡：Document Type / Document Number / Issue Date / Expiry Date / Record Status / Expiry Status (derived) = `Expired` ✅
- Accounts 卡：`Current Accounts`（Account Number / Product / Balance / Status）、`Fixed Deposits` 空态 `No fixed deposits`、Loan 卡空态 ✅

## 3) clients（total 插值断言）

- 标题 `Clients`、搜索 placeholder `Search by name, external ID, or mobile number`、表头 7 列英文、操作列 `Details` ✅
- **分页 total 插值：`Total 3 clients`**——英语句式形态，非逐字直译 ✅
- 数据口径注脚英文（money 插值 ¥10,000.00）✅

## 4) login（登出后走查）

- 标题 `Backoffice Operations Console`、label `Username` / `Password`、按钮 `Sign in`、mock 提示英文 ✅
- 空表单校验：`Please enter your username` / `Please enter your password` ✅
- 欢迎语 toast：`Welcome, ABNK Operations Admin`（{name} 插值）✅
- 用户菜单 `Sign out` ✅

## Console 检查

走查全程 console 0 红错（两个会话日志 grep error 均为 0）。

## 结论

V1.6.4 通过：英文态全页面文案与 `en-us` 词条一致且为语义重写形态（Overdue for N days / Total N clients 等英语句式），插值模板（{name}/{total}/{money}/{days}/{classification}）两态全部正确。V1.6.5：typecheck exit=0（satisfies 保证结构对齐）+ 两语言 JSON 文件集一一对应（clients/common/errors/loanOps/login）。

## 截图证据（`task1.6-screenshots/`，2026-11-12 补录，playwright-cli 1440×900）

| 文件 | 状态 |
|---|---|
| `login-en.png` | 登录页英文态素净版（Backoffice Operations Console / Username / Password / Sign in） |
| `login-en-validation.png` | 空表单提交 → "Please enter your username" / "Please enter your password" |
| `welcome-toast-en.png` | 登录成功 → toast "Welcome, ABNK Operations Admin"（{name} 插值） |
| `clients-list-en.png` | 客户列表全项（英文表头/Details/"Total 3 clients"/英文口径注脚） |
| `client-detail-en.png` | 客户详情全项（Client Profile 等 label/Identity Documents/Current Accounts/Fixed Deposits） |
| `loanops-en.png` | 贷款运营全项（英文 Alert/表头/"Overdue for 40 days (ABNK_POC_OD)"/Approve/Disburse） |
