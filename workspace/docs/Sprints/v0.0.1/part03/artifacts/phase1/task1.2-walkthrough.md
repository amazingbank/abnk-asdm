# Task 1.2 界面走查记录 —— LocaleProvider + localStorage 事实源 + `<html lang>`/title 同步

- 日期：2026-11-12
- 环境：dev server `http://localhost:6203`（Vite v7.3.7，`ready in 368 ms`，HTTP 200）；浏览器自动化 = playwright-cli（Chromium）；页面 = `/login`
- 走查取态口径：直接改 `localStorage` 的步骤均 `location.reload()` 后断言（初始语言决策在挂载时发生）

## V1.2.2 存储驱动语言 + title/lang 副作用（英文态）

| 操作 | 结果 |
|---|---|
| `localStorage.setItem('abnk-locale','en-us')` + reload | — |
| `document.documentElement.lang` | `"en-US"` ✅（期望 `"en-US"`） |
| `document.title` | `"ABNK Backoffice · Operations Console"` ✅（与 `en-us/common.json` 的 `meta.title` 完全一致） |

## V1.2.3 中文态对称走查

| 操作 | 结果 |
|---|---|
| `localStorage.setItem('abnk-locale','zh-cn')` + reload | — |
| `document.documentElement.lang` | `"zh-CN"` ✅（期望 `"zh-CN"`） |
| `document.title` | `"ABNK Backoffice · 运营后台"` ✅（与 `zh-cn/common.json` 的 `meta.title` 完全一致） |

## V1.2.4 非法/缺失存储值兜底

| 操作 | 结果 |
|---|---|
| `localStorage.setItem('abnk-locale','fr')` + reload | — |
| `document.documentElement.lang` | `"en-US"` ✅ |
| 存储值（reload 后） | `fr`（原样保留在存储中，但未成为渲染语言） |

> 判据「非法值不成为渲染语言」满足：`fr` 未生效。
>
> **规则口径修订（2026-11-12 用户拍板）**：存储值非中文非英文（如 `fr`）一律**无条件回退英文**（`DEFAULT_LOCALE = en-us`），不进入系统探测——兜底结果不随系统语言摇摆。初版实现为「非法值视同缺失走系统探测」，任务 1.3 接线后曾在中文系统模拟下得到 zh-CN；按上述口径已修正 `locale-provider.tsx` 的 `initialLocale()`（合法存储值 → 用之；非法存储值 → 英文；无存储值 → 系统跟随），并于 2026-11-12 在中文系统模拟（`navigator.languages=["zh-CN","zh"]`）下复测：`fr` → `"en-US"` ✅，同时回归验证 `zh-cn` → `"zh-CN"`、`en-us` → `"en-US"`、无存储 → `"zh-CN"`（系统跟随不受影响）。截图 `login-invalid-fr-fallback.png` 已按新规则重拍（英文登录页）。

## Console 检查

走查全程 console 0 红错（仅 React DevTools INFO 提示，共 4 次页面加载各一条）。

## 结论

V1.2.2 / V1.2.3 / V1.2.4 全部通过：localStorage 事实源驱动初始语言，`<html lang>`（BCP 47 大写）与 `document.title`（取 `common.meta.title`）随语言正确同步，非法存储值被拦截。

## 截图证据（`task1.2-screenshots/`，2026-11-12 补录，playwright-cli 1440×900）

| 文件 | 状态 |
|---|---|
| `login-stored-en-us.png` | 存储 `en-us` + reload → 英文登录页（对应 V1.2.2；页面标题 "ABNK Backoffice · Operations Console" 见截图页面渲染） |
| `login-stored-zh-cn.png` | 存储 `zh-cn` + reload → 中文登录页（对应 V1.2.3） |
| `login-invalid-fr-fallback.png` | 存储 `fr` + reload → **英文登录页**（对应 V1.2.4；按 2026-11-12 用户拍板口径，非法值无条件回退英文，中文系统模拟下复测确认） |
