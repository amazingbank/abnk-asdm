# 任务 2.1 界面走查记录（V2.1.4 / V2.1.5）

> 日期：2026-11-12 · dev server：http://localhost:6203（mock 模式，复用运行中实例）· 语言事实源：localStorage 键 `abnk-locale`

## V2.1.4 登录失败提示两语言态（`auth.invalidCredentials`）

| 步骤 | 操作 | 断言输出 |
|---|---|---|
| zh 态 | `localStorage.setItem('abnk-locale','zh-cn')` → 刷新 → 用户名 `admin` + 口令 `wrongpass` → 提交 | `.ant-message` innerText = `用户名或口令错误`（与 `zh-cn/errors.json` `auth.invalidCredentials` 词条一致） |
| en 态 | `localStorage.setItem('abnk-locale','en-us')` → 刷新 → 同操作 | `.ant-message` innerText = `Invalid username or password`（与 `en-us/errors.json` 语义重写词条一致，非逐字直译） |

截图：`task2.1-login-error-zh.png`、`task2.1-login-error-en.png`（toast 均在画面顶部可见）。

## V2.1.5 客户不存在两语言态（`client.notFound` + `{clientId}` 插值）

| 步骤 | 操作 | 断言输出 |
|---|---|---|
| 登录 | admin/password 正常登录（过 RequireAuth 守卫） | 成功进入 /clients |
| zh 态 | 直接访问 `/clients/999`（mock store 客户 ID = 28/29/30，999 必不命中） | toast = `客户不存在：clientId=999`（含 clientId=999 插值值）；页面渲染 Empty 兜底块 |
| en 态 | 切 en-us 后同操作 | toast = `Client not found (ID: 999)`（含插值值） |

截图：`task2.1-client-notfound-zh.png`、`task2.1-client-notfound-en.png`。

## 结论

- ApiError 错误码 → `apiErrorMessage` → errors 词条 → `interpolate(params)` 链路在两种语言下均正确。
- 英文词条为语义重写形态（D2 口径），非逐字直译。
