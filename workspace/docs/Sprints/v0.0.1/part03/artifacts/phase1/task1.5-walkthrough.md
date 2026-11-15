# Task 1.5 界面走查记录 —— antd ConfigProvider locale 与 dayjs locale 随语言联动

- 日期：2026-11-12
- 环境：dev server `http://localhost:6203`（Vite v7.3.7，HTTP 200，本次改动 dev server 已正常感知无需重启）；浏览器自动化 = playwright-cli（Chromium）；mock 会话（admin/password，`/clients`）
- 快照证据：`task1.5-snapshots/`（v153-zh-initial / v153-zh-empty / v153-en-empty）
- 走查路径：客户列表搜索框输入不存在关键词「不存在的客户XYZ」+ Enter（`Input.Search` 为 onSearch 触发，非即时过滤）→ Table 空态（antd Empty 内建文案）→ 点击语言切换器就地断言

## V1.5.3 antd 内建文案随语言切换

| 断言项 | 中文态 | 英文态（点击切换器后） |
|---|---|---|
| `document.documentElement.lang` | `"zh-CN"` | `"en-US"` |
| Table 空态文案（antd Empty 内建） | `暂无数据` ✅（antd zh_CN） | `No data` ✅（antd en_US） |
| 切换方式 | — | 切换器点击后就地翻转（无刷新，搜索过滤状态保留） |

## V1.5.2 静态核验摘要（同轮实测）

- `main.tsx`：代码级 `zh_CN`/`zhCN` 清零（仅注释中说明性提及；`locale={zhCN}` 直传形态消失，antd locale 移至 `AppProviders.tsx` 的 `ANTD_LOCALES` 映射表达式）
- `AppProviders.tsx:6-7`：`import 'dayjs/locale/zh-cn'` 与 `import 'dayjs/locale/en'` 两个 import 均存在
- `IdentifierEditForm.tsx`：dayjs 用法（`dayjs(date)`/`format('YYYY-MM-DD')`/`DatePicker`）均无显式 locale 传参，自动跟随全局 `dayjs.locale`，本任务无需改动

## Console 检查

走查全程 console 0 红错（仅 React DevTools INFO 提示）。

## 结论

V1.5.1–V1.5.3 全部通过：antd 内建文案（Table 空态 Empty）随语言两态正确切换（暂无数据 ↔ No data），ConfigProvider locale 经 `AppProviders` 映射驱动，dayjs 全局 locale 同步接线。

## 截图证据（`task1.5-screenshots/`，2026-11-12 补录，playwright-cli 1440×900）

| 文件 | 状态 |
|---|---|
| `empty-state-zh.png` | 中文态搜索不存在关键词 → Table 空态「暂无数据」（antd zh_CN 内建文案） |
| `empty-state-en.png` | 英文态同操作 → 空态「No data」（antd en_US 内建文案；截图中英文表头/标题/口径注脚一并可见） |
