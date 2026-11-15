# Task 1.4 界面走查记录 —— BoLayout 头部语言切换器 + 布局文案词条化

- 日期：2026-11-12
- 环境：dev server `http://localhost:6203`（Vite v7.3.7，HTTP 200）；浏览器自动化 = playwright-cli（Chromium）；mock 登录 admin/password（Part02 P1.4 五步走查同口径）
- 快照证据：`task1.4-snapshots/`（login-zh / layout-zh / layout-en / layout-zh-back / user-dropdown）
- 走查取态口径：切换器走查点击后就地断言（验证无刷新重渲染），不 reload；无刷新判据 = 点击前置 `window.__noReload = 'marker'`，点击后 marker 仍存活且 URL 不变
- 环境备注：落码后再次命中已知环境坑 4（dev server 下发过期 `BoLayout.tsx`，新文件正常），按预案重启 dev server 并复验新码下发后执行走查

## V1.4.2 切换器就位且就地重渲染（英文态）

初始态：`localStorage.abnk-locale=zh-cn` + reload → 登录（admin/password）→ `/clients` 主布局（中文态渲染正确：菜单「客户列表/贷款运营」、头部「Backoffice 运营后台」、用户按钮「ABNK Operations Admin」、切换器 aria-label="Switch to English" 指向目标语言名）。

> **displayName 口径（2026-11-12 用户拍板）**：mock 运营账号 displayName 由「ABNK 运营管理员」改为语言中性英文 `ABNK Operations Admin`（`operators.json` 单值，不随 UI 语言切换；双语数据集仍属 Phase 2 任务 2.2 / 决策 D3）。本目录 yaml 快照为改动前取证、PNG 截图均为改动后重拍，故两者用户态文案不同属预期。

点击切换器后断言：

| 断言项 | 结果 | 期望 |
|---|---|---|
| `document.documentElement.lang` | `"en-US"` | ✅ |
| `localStorage.abnk-locale` | `en-us` | ✅（切换即写存储） |
| URL | `/clients`（不变） | ✅（无路由跳变） |
| `window.__noReload` | `"marker"`（存活） | ✅（无页面刷新，就地重渲染） |
| 侧栏菜单 | `Clients` / `Loan Operations` | ✅（en 语义重写词条） |
| 头部标题 | `Backoffice Operations Console` | ✅（en 语义重写词条） |
| 切换器 label | `切换到中文` | ✅（随语言翻转，指向新目标） |

## V1.4.3 中文态对称走查 + 布局文案完整两态

再次点击切换器（label「切换到中文」）后断言：

| 断言项 | 结果 | 期望 |
|---|---|---|
| `document.documentElement.lang` | `"zh-CN"` | ✅ |
| `localStorage.abnk-locale` | `zh-cn` | ✅ |
| `window.__noReload` | `"marker"`（存活） | ✅（两向切换均无刷新） |
| 侧栏两项菜单 label | `客户列表` / `贷款运营` | ✅ 与 `zh-cn/common.json` 一致 |
| 头部标题 | `Backoffice 运营后台` | ✅ 与词条一致 |
| 用户态 | `ABNK Operations Admin`（session.displayName，2026-11-12 起为语言中性英文） | ✅；兜底值词条 `user.anonymous`（未登录）已在两语言 JSON 落位 |
| 用户 Dropdown | menuitem「退出登录」 | ✅ 与 `user.logout` 词条一致 |

## V1.4.4 布局文案硬编码清零（静态）

`grep -nE "[一-龥]" src/components/BoLayout.tsx | grep -vE "^\s*[0-9]+:\s*(//|/\*|\*)"` → **0 行**（非注释中文字符清零；`Amazing Bank` 为品牌名不本地化）。

## Console 检查

走查全程 console 0 红错（仅 React DevTools INFO 提示）。

## 结论

V1.4.1–V1.4.4 全部通过：语言切换器就位（aria-label/title 写目标语言名，website 同构口径），点击切换写存储 + 就地重渲染（无刷新/无路由跳变双向验证），布局文案（菜单/标题/用户态/退出登录）全部词条化且两态与 JSON 一致。

## 截图证据（`task1.4-screenshots/`，2026-11-12 补录，playwright-cli 1440×900）

| 文件 | 状态 |
|---|---|
| `layout-zh-dropdown-open.png` | 中文态主布局：侧栏「客户列表/贷款运营」、头部「Backoffice 运营后台」、语言切换器、用户 Dropdown 展开显示「退出登录」、表格「已过期/有效」标签、分页「共 3 名客户」、口径注脚 ¥10,000.00 |
| `layout-en-dropdown-open.png` | 英文态主布局（对应 V1.4.2 切换后）：侧栏 Clients / Loan Operations、头部 Backoffice Operations Console、Dropdown 展开 Sign out |
