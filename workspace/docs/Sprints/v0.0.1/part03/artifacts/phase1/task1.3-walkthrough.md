# Task 1.3 界面走查记录 —— 系统语言跟随（resolveBrowserLocale 接入决策链）

- 日期：2026-11-12
- 环境：dev server `http://localhost:6203`（Vite v7.3.7，HTTP 200）；浏览器自动化 = playwright-cli（Chromium）；页面 = `/login`
- 走查浏览器说明：playwright Chromium 默认上报 `navigator.languages = ["en-US","en"]`（非本机中文环境）。按 Phase 文档口径「判据是规则一致，不是固定值」，V1.3.3 以两种系统语言取值分段验证 D1 规则；中文段用 `page.addInitScript` 覆盖 `navigator.languages`/`navigator.language` 模拟中文系统（页面主世界生效，已实测确认覆盖成功）。

## 环境异常与处置记录（已知环境坑 4 命中）

首次执行 V1.3.3 第二段时发现：`navigator.languages` 已成功覆盖为 `["zh-CN","zh"]` 且存储为空，但 `lang` 仍为 `"en-US"`。取证发现 dev server 下发的 `locale-provider.tsx` 为任务 1.2 旧码（`readStoredLocale() ?? DEFAULT_LOCALE`），磁盘上的 1.3 改动未被 Vite 模块图感知（`curl http://localhost:6203/src/i18n/locale-provider.tsx` 比对确认）。
处置：按已知环境坑 4 预案**重启 dev server**（kill :6203 → 重起 → HTTP 200 → 确认下发新码 `readStoredLocale() ?? resolveBrowserLocale()`），并重开浏览器会话后**重跑全部走查步骤**。重启前基于旧码的结果全部作废不计入验收。

## V1.3.3 无存储时跟随系统（两段）

| 段 | 系统语言（navigator.languages） | 存储 | 操作 | `document.documentElement.lang` | 结论 |
|---|---|---|---|---|---|
| 1 | `["en-US","en"]`（浏览器默认） | 空（`localstorage-list` 确认无条目） | 直接开页 | `"en-US"` | ✅ D1 非 zh 规则：→ en-us |
| 2 | `["zh-CN","zh"]`（init script 模拟） | 空 | reload | `"zh-CN"`（title 同步为「ABNK Backoffice · 运营后台」） | ✅ D1 zh 规则：任一 zh 开头 → zh-cn |

> 本机为中文环境（macOS 中文系统）；走查载体 Chromium 上报 en-US，故以两段模拟覆盖 D1 全规则空间，判据（规则一致）满足。

## V1.3.4 存储优先级高于系统探测

| 步骤 | 系统语言 | 存储 | `document.documentElement.lang` | 结论 |
|---|---|---|---|---|
| `setItem('abnk-locale','en-us')` + reload | `["zh-CN","zh"]`（模拟） | `en-us` | `"en-US"` | ✅ 存储值覆盖系统中文 |
| `removeItem` + reload（恢复无存储态） | `["zh-CN","zh"]`（模拟） | 空 | `"zh-CN"` | ✅ 回落系统跟随，无存储态已还原 |

## Console 检查

走查全程 console 0 红错（仅 React DevTools INFO 提示）。

## 结论

V1.3.1–V1.3.4 全部通过：初始语言决策链「持久化偏好优先 → 系统语言跟随（zh 开头 → zh-cn，否则 en-us）」完整接线并两态实测；D6 口径下无 URL 侵入。

## 截图证据（`task1.3-screenshots/`，2026-11-12 补录，playwright-cli 1440×900）

| 文件 | 状态 |
|---|---|
| `login-en-no-storage-system-follow.png` | 无存储 + 英文系统（浏览器默认 `["en-US","en"]`）→ 英文登录页（D1 非 zh 规则，对应 V1.3.3 第一段） |
| `login-zh-system-follow.png` | 无存储 + 中文系统模拟（init script 覆盖 `navigator.languages=["zh-CN","zh"]`）→ 中文登录页（D1 zh 规则，对应 V1.3.3 第二段） |
| `login-en-storage-priority.png` | 中文系统模拟下存储 `en-us` → 英文登录页（存储覆盖系统，对应 V1.3.4） |
