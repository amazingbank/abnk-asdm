# 官网渠道多语言与字体方案（channels/website）

> 状态：✅ 已实施（2026-10-27）· 细化 ADR-008 中"官网零业务 API"的官网范围
> 参照来源：`asdm-website-ws/asdm-ai-2026`（已实测其 i18n 与字体实现，下文"出处"均指该仓库代码）
> 可视化评审：`abnk-system/channels/website/design/font-comparison.html`（浏览器直接打开）

## 1. 决策总览

| # | 决策 | 内容 |
|---|---|---|
| D1 | 自研 i18n，不引库 | 与 asdm-ai-2026 一致（出处：其 package.json 无 i18next/react-intl），无运行时依赖 |
| D2 | URL 前缀为语言唯一事实源 | `/zh-cn/`、`/en-us/`；无前缀 URL 重定向到浏览器检测语言（出处：asdm locale-url.ts / locale-provider.tsx） |
| D3 | 语言包静态打包（偏离 asdm） | asdm 按命名空间懒加载 + localStorage 缓存；本站为单页锚点站，两语言包 gzip 后约 6KB，静态 import 打进主包，从机制上消除 asdm cache.ts 注释中记录的两次"缓存版本未 bump → 白屏"事故类别 |
| D4 | 切换不重挂载（偏离 asdm） | asdm 用 `BrowserRouter key={locale}` 强制路由树 remount；本站无路由，pushState 换前缀后就地重渲染，保留滚动位置与 Reveal 动画状态 |
| D5 | 中英双语，浏览器语言检测 | `navigator.languages` 任一 tag 匹配 `/^zh\b/i` → zh-cn，否则 en-us（出处：asdm resolveBrowserLocale） |
| D6 | 字体与 asdm-ai-2026 一致 | 自托管 `@fontsource-variable`：Oxanium（拉丁）+ Noto Sans SC（中文）+ JetBrains Mono（等宽），逐字符回退，无 Google CDN |
| D7 | 大标题保留衬线（方案 A，已定案） | `font-serif` = Noto Serif SC（自托管）。2026-10-27 经 font-comparison.html 三方案可视化评审后选定 A：sans/mono 与 asdm-ai-2026 完全一致，衬线大标题作为 ABNK 品牌保留项（暖调银行质感核心） |

## 2. 多语言实现

### 2.1 目录结构

```
channels/website/src/i18n/
├── index.ts              # 统一出口（LocaleProvider 组件单独导出，规避 react-refresh 规则）
├── resources.ts          # Locale 类型 + RESOURCES 注册表 + 编译期结构校验（satisfies）
├── locale-url.ts         # URL 前缀解析/交换（与 asdm 同名文件一致）
├── locale.ts             # 浏览器语言检测 + <html lang> 映射
├── locale-context.ts     # React Context 定义
├── locale-provider.tsx   # Provider：html lang / title / meta description 同步、popstate 重同步、切换
├── use-locale.ts         # useLocale / useCommon / useHome 三个 Hook
├── interpolate.ts        # {param} 插值（如 "阶段 {no}"）
└── locales/
    ├── zh-cn/{common,home}.json   # 中文 = 文案原始来源，类型由此推导
    └── en-us/{common,home}.json   # 英文，结构必须与中文包一致（tsc 编译期校验）
```

命名空间划分与 asdm 一致：`common`（导航/页脚/SEO meta/语言切换文案）+ `home`（全部 section 文案）。本站单页，无需再按页面拆分。

### 2.2 关键机制（均与 asdm-ai-2026 对齐）

- **事实源**：URL 前缀。`main.tsx` 挂载前校验前缀，无前缀/非法前缀 → `location.replace('/' + 检测语言 + '/')`（reset 语义，丢弃 query/hash，出处：asdm LocaleResetRedirect "decision #15"）。
- **规范形态**：`/zh-cn` → `/zh-cn/` 尾斜杠 replaceState 规范化（出处：asdm App.tsx 同款逻辑）。
- **切换**：`pushState` 交换前缀（保留 query + hash，锚点与滚动位置不动），组件就地重渲染；写入 `localStorage["abnk-locale"]`（**只写不读**的兼容记录，出处：asdm 同设计——浏览器偏好持续生效，URL 永远优先）。
- **前进/后退**：`popstate` 从 URL 重同步 locale（出处：asdm locale-provider）。
- **SEO**：`<html lang>` / `<title>` / `meta description` 由 Provider effect 按语言更新；`index.html` 保留中文静态值作为 JS 加载前兜底（主要受众为中国市场）。
- **类型安全**：`resources.ts` 以 `typeof import('zh-cn/*.json')` + `Widen<T>` 推导结构，英文包 `satisfies` 校验——两语言键结构不一致直接编译失败（出处：asdm resources.ts 同款手法）。

### 2.3 文案抽取约定

- 组件内只留**结构与图形数据**（lucide 图标映射、SVG 坐标、CountUp 数值），字符串一律入语言包。
- 大标题的多行/强调色（`<br className="hidden sm:block">`、`text-amber` span）属于结构，留在组件 JSX；语言包只存逐行文本（`title.line1 / title.line2`）。
- 双语装饰性小标签（`note` 字段）：**中文页注英文**（"中国本土"/China，延续原站设计）；**英文页一律英文**（China/First Landing、Discover/Insight、Process/Traceable、Steadfast/Trust——与正文主题呼应的等宽关键词，2026-10-27 用户评审否决了英文页注中文的互文方案）。语言切换按钮的悬停提示按目标语言书写（英文页显示"切换到中文"，与 asdm-ai-2026 一致）。
- 英文导航用单词入口（Identity / Global / ASDM / Open / Beliefs），中文保持双字/三字词组（2026-10-27 决策）。
- 品牌级、两语言完全相同的行（如页脚 "Built on ASDM · Open by Default"）保留在代码中，不入语言包。

## 3. 字体方案

### 3.1 与 asdm-ai-2026 一致的部分（已生效）

```css
--font-sans : "Oxanium Variable", "Noto Sans SC Variable", ui-sans-serif, system-ui, sans-serif;
--font-mono : "JetBrains Mono Variable", "Noto Sans SC Variable", ui-monospace, monospace;
```

- 交付：npm 包 `@fontsource-variable/{oxanium,jetbrains-mono,noto-sans-sc}`，`main.tsx` 顶部 import，Vite 打包进 `/assets`（构建产物带内容哈希，nginx `expires 30d` 长缓存），**零外部 CDN 依赖**（替换原 Google Fonts link）。
- 中英混排：Oxanium 缺 CJK 字形时浏览器逐字符回退 Noto Sans SC，无需任何 JS（出处：asdm index.css 注释）。
- 中文按 unicode-range 分片（约 100 个 woff2），浏览器只加载页面用到的分片。
- 已移除 Inter 专属的 `font-feature-settings: 'ss01', 'cv11'`（asdm body 无此设置）。

### 3.2 font-serif 决策：方案 A（已定案 2026-10-27）

| 方案 | serif 栈 | 结论 |
|---|---|---|
| **A（定案）** | `"Noto Serif SC Variable", Georgia, serif` | 保留银行衬线大标题质感；sans/mono 与 asdm 完全一致，衬线为 ABNK 品牌保留项 |
| B（未采用） | 无衬线，= sans 栈 | 与 asdm 100% 一致，但中文大标题失去衬线质感；备选，切换成本：tailwind.config 删 serif 行 + 全站 `font-serif` → `font-sans`（约 9 处）+ 删 noto-serif-sc 引入 |

可视化对比页（保留存档）：`design/font-comparison.html`（浏览器直接打开）。

## 4. 部署要点

- **语言前缀路径零额外规则**：既有 `try_files $uri $uri/ /index.html` 已天然支持 `/zh-cn/`、`/en-us/` 前缀路径回退（已用 `vite preview` + curl 实测 200）。
- **发版缓存策略**（2026-10-27 对齐 asdm-ai-2026 deploy/nginx，杜绝"发版后老访客看不到新内容"）：
  - `/assets/`（Vite 内容哈希产物）：单头 `Cache-Control: public, max-age=31536000, immutable`——原 `expires 30d` + `add_header` 并存会产生双重 Cache-Control，已统一；
  - `location = /index.html`：`no-store` 彻底禁止存储。`no-cache` 仍允许磁盘缓存 + 启发式新鲜度，旧 HTML 会存活数小时并按旧哈希名拉已删除的 assets（旧内容/白屏）；no-store 保证发版后任何刷新方式都回源拿新 HTML。根路径（index 指令）与 `/zh-cn/`、`/en-us/`（try_files 回退）经内部重定向同样命中 no-store；
  - `/favicon.svg` 等根级元文件：`no-cache`（保留 304 协商校验）；
  - location 内含 `add_header` 时不再继承 server 级安全头——各 location 显式补齐 HSTS 等四个安全头（原配置在 `/assets/` 上已存在此遗漏，一并修复）。
- 字体文件进 `/assets/`，享受 immutable 强缓存。

## 5. 验证记录（2026-10-27）

- `tsc --noEmit` 通过（含两语言包结构 satisfies 校验）；`eslint` 0 error（仅 Reveal.tsx 1 条改造前既有 warning）；`vite build` 通过。
- 浏览器实测（Chromium，preview 4173）：`/` → `/en-us/`（英文浏览器）；点语言按钮 → URL `/zh-cn/`、全站中文、`html.lang=zh-CN`、title/description 同步切换、`localStorage.abnk-locale=zh-cn`；h1 字体 `Noto Serif SC Variable`、body `Oxanium Variable`、eyebrow `JetBrains Mono Variable` 均按预期生效。
- 2026-10-27 增量：`nginx.conf` 发版缓存策略改版后经 `nginx:1.27-alpine` 官方镜像 `nginx -t` 语法校验通过（自签证书挂载）；英文导航单词化后 `tsc` 通过。

## 6. 后续演进

- **新增第三语言**：`resources.ts` 增加 Locale + JSON 目录 + LOCALES 项；`locale-url.ts` 前缀集合与 `locale.ts` 检测规则同步扩展。
- **SSR/预渲染**：当前 `/zh-cn/` 与 `/en-us/` 共用同一份中文兜底 index.html，爬虫依赖 JS 执行后内容；若 SEO 要求提高，后续可引入 vite-prerender 按前缀出双份静态 HTML（不改变现有架构）。
