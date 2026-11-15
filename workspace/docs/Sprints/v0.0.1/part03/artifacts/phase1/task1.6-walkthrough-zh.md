# Task 1.6 界面走查记录（中文态）—— pages/components 全量词条替换

- 日期：2026-11-12
- 环境：dev server `http://localhost:6203`（Vite v7.3.7，改动均已被 dev server 感知）；浏览器自动化 = playwright-cli（Chromium）；mock 登录 admin/password
- 取态：`localStorage.abnk-locale=zh-cn` + `location.reload()` 后断言
- 快照证据：`task1.6-snapshots/`（v163-zh-*，共 10 份）

## 1) login（校验提示触发一次）

| 文案点 | 实测 | 词条 |
|---|---|---|
| 标题 | `Backoffice 运营后台` | `login.title` ✅ |
| 表单 label | `用户名` / `口令` | `login.{username,password}.label` ✅ |
| placeholder | `运营账号` / `口令` | ✅ |
| 空表单提交校验 | `请输入用户名` / `请输入口令` | `login.{username,password}.required` ✅ |
| 登录按钮 | `登 录` | `login.submit` ✅ |
| 欢迎语 toast | `欢迎，ABNK Operations Admin` | `login.welcome`（{name} 插值）✅ |
| mock 提示 | `mock 演示口令：admin / password（原型专用明文，生产走 PBKDF2 凭据）` | `login.mockHint` ✅ |

## 2) clients（搜索、分页 total 文案）

- 标题 `客户列表`、搜索 placeholder `搜索姓名 / 外部编号 / 手机号`、表头 7 列（客户号/姓名/外部编号/手机号/证照状态/证照到期日/操作）、操作列 `详情`——全部与 `clients.list` 词条一致 ✅
- 分页 total：初始 `共 3 名客户`；搜索「王」过滤后 `共 1 名客户`（{total} 插值联动）✅
- 数据口径注脚含 `{money}` 插值：`……金额格式示例 ¥10,000.00` ✅
- 证照状态列：`已过期`（王）/`有效`（李）——`clients.status.*` ✅

## 3) client detail（Descriptions 各 label）

- `返回` 按钮、标题 `客户详情 · 王POC-A1107104347`（{name} 插值）✅
- 客户信息卡：客户号/外部编号/姓名/手机号/邮箱/所属机构/状态 ✅
- 证照信息（可编辑）卡：证照类型/证件号/签发日/记录状态/到期状态（推导）= `已过期` + 编辑提示句 ✅
- 编辑表单：到期日（必填 `请选择到期日` 词条落位）/证件号（可选）/说明（可选） ✅
- 账户信息卡：`活期`（表头 账号/产品/余额/状态）、`定期` 空态 `无定期账户` ✅
- 贷款信息卡空态 `无贷款记录` ✅

## 4) loan-ops（表头、操作列）

- 标题 `贷款运营`、只读 Alert 文案 ✅
- 表头 8 列（贷款号/客户/产品/本金/利率/期限(月)/状态/操作）✅
- 逾期标签 `逾期 40 天（ABNK_POC_OD）`（{days}/{classification} 插值）✅
- 操作列禁用按钮 `审 批` / `放 款` + 只读 Tooltip 词条落位 ✅
- 数据口径注脚 ✅

## Console 检查

走查全程 console 0 红错（仅 React DevTools INFO 提示）。

## 结论

V1.6.3 通过：中文态全页面（login → clients → detail → loan-ops）文案与 `zh-cn` 词条完全一致，插值模板（{name}/{total}/{money}/{days}/{classification}）全部正确渲染。

## 截图证据（`task1.6-screenshots/`，2026-11-12 补录，playwright-cli 1440×900）

| 文件 | 状态 |
|---|---|
| `login-zh.png` | 登录页中文态素净版（标题/表单/按钮/mock 提示） |
| `login-zh-validation.png` | 空表单提交 → 「请输入用户名」「请输入口令」校验提示 |
| `welcome-toast-zh.png` | 登录成功 → toast「欢迎，ABNK Operations Admin」（{name} 插值）+ 客户列表全景 |
| `clients-list-zh.png` | 客户列表全项（表头 7 列/「共 3 名客户」/口径注脚 ¥10,000.00） |
| `client-detail-zh.png` | 客户详情全项（信息卡 label/证照卡/账户卡/空态） |
| `loanops-zh.png` | 贷款运营全项（Alert/表头 8 列/「逾期 40 天（ABNK_POC_OD）」/禁用审批放款） |
