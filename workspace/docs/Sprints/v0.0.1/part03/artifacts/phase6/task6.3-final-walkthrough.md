# 任务 6.3 —— Part 03 收口全流程走查汇总（两端 × 两语言态 × 全页面）

- 日期：2026-11-16；执行人：AI（abnk-debugger 惯例自动走查）
- 判据口径：全部复用既有 Phase 步骤（已知坑 8——不做新断言口径）；探查类证据 = 快照 + 本记录
- 环境与工具：
  - backoffice：dev server `http://localhost:6203`（Vite v7.3.7，HTTP 200，strictPort）；自动化 = playwright-cli（Chromium）；mock 会话 admin/password；快照归档 `task6.3-bo-snapshots/`（22 件 yaml）
  - mobile-banking：见「V6.3.3」节（:6280 web 载体 + agent-browser 语义树）

## V6.3.1 —— 两端用户可见中文清零终检（口径复用 V1.6.2/V2.1.2/V3.4.2/V4.2.2）

实测命令（Phase 6 文档印刷口径）：

- ① backoffice：`grep -rnE "[一-龥]" $BO/src --include='*.ts' --include='*.tsx' | grep -vE ":\s*(//|/\*|\*)" | grep -vE "i18n/locales/zh-cn|mockData/zh-cn" | wc -l` → **7**
- ② mobile：`grep -rnE "[一-龥]" $MB/lib --include='*.dart' | grep -vE ":\s*(//|///|/\*|\*)" | grep -v "l10n" | wc -l` → **0** ✅

② 零命中。① 的 7 行经逐条裁决全部为合法类（已知坑 2「合法中文必须精确排除」原则的精确化）：

| # | 位置 | 内容 | 裁决 |
|---|---|---|---|
| 1–4 | `BoLayout.tsx:101-104` | `{/* 数据纪元 remount … */}` JSX 块注释（中文段 101-104 + 英文语义重写段 105-110） | **双语注释，合法**——行首排除式（`:\s*(//|/\*|\*)`）不识别 JSX `{/*` 形态，注释本体经 6.1 矩阵审计配对缺口 0（check-bilingual 块级判定同口径）；非用户可见（编译期剥离） |
| 5 | `fineractRaw.ts:153` | `businessDateCache = null; // 失败不缓存（如 token 过期）——下次调用重试`（行尾注释） | **注释，合法**——V2.1.2 原判据执行结果已明文豁免此行（「行尾注释…不以引号开头故不匹配」）；Part02 存量未触碰文件（Plan 总体口径不追溯） |
| 6 | `resources.ts:36` | `{ code: 'zh-cn', label: '中文' }` | **语言自称 label，合法**——切换器设计本意（「每个候选项以其自身语言标注」，D6 体系；与 zh-cn 词条文件同类合法中文）；en 态下同样显示「中文」是 i18n 惯例 |
| 7 | `AuthContext.ts:20` | `throw new Error('useAuth 必须在 AuthProvider 内使用')` | **开发态守卫，非用户可见**——React hook 误用防线，运行时正常路径不可达 UI；Part02 存量未触碰文件，在 V1.6.2（pages/components）与 V2.1.2（api 层）原判据范围之外 |

原判据范围复跑（判据本身，无漂移）：

- V1.6.2 原口径（`$BO/src/pages $BO/src/components`，非注释中文字符串）：命中的 4 行 = 上表 #1–4（同一 JSX 注释块）——**非注释中文字符串实际为 0** ✅
- V2.1.2 原口径（`$BO/src/api` 引号中文字面量，排除 generated/）：**0** ✅
- mobile（V3.4.2/V4.2.2 口径）：**0** ✅

结论：两端用户可见中文文案清零成立；7 行均为注释/语言自称/开发态守卫的合法类，无一条为运行时用户可见文案。

## V6.3.2 —— backoffice 全流程双语走查（复验 V1.4.2/V1.5.3/V1.6.3/V1.6.4/V2.1.4/V2.1.5 + Phase 7 行为态）

会话路径：初始英文态（playwright Chromium 默认 `navigator.languages=["en-US"]`，同 V1.3 惯例）全路径 → 切换器切中文 → 中文态全路径。判据逐项：

### 英文态（en-us）

| 判据 | 实测 | 结果 |
|---|---|---|
| V1.4.2（切换器/`<html lang>`/存储） | 初始 `document.documentElement.lang="en-US"`（存储 null——系统跟随未持久化，V1.3 口径设计态）；侧栏 Clients / Loan Operations；头部 Backoffice Operations Console | ✅ |
| V2.1.4（错误口令提示） | admin/wrongpass → `Invalid username or password`（语义重写形态，非逐字直译） | ✅ |
| V1.6.4（clients 页 + 插值） | 登录 → /clients：表头 Client ID/Name/External ID/Mobile Number/Identifier Status/Identifier Expiry Date/Actions；数据 = en 数据集（Alex/Ben/Chloe POC-A/B/C + Expired/Valid）；分页 **`Total 3 clients`**（插值语义重写）；footer 数据口径叙事英文（Wang/Li/Zhao——D2 语义重写） | ✅ |
| V1.5.3（antd 空态 en） | 搜索 `zzz-no-match` 回车 → antd Empty **`No data`**（en_US 内建） | ✅ |
| V1.6.4（client detail） | /clients/28：heading `Client Details · Alex POC-A1107104347`；Descriptions 全 label 英文（Client ID/External ID/Name/Mobile Number/Email/Branch/Status/Document Type/Document Number/Issue Date/Expiry Date/Record Status/Expiry Status (derived)）；账户产品 `ABNK Current Savings` | ✅ |
| V1.6.3/1.6.4（loan-ops） | /loan-ops：heading Loan Operations；表头 Loan ID/Client/Product/Principal/Interest Rate/Term (months)/Status/Actions；操作列 `Approve`/`Disburse`（disabled——POC 基线预埋）；金额 ¥50,000.00（formatMoney locale 参数化，Intl 分组随 en-US） | ✅ |
| V2.1.5（客户不存在 + 插值） | /clients/999 → message **`Client not found: clientId=999`**（999 插值）+ Empty 兜底 `Client not found (ID: 999)`（t.detail.notFound） | ✅ |

### 切换器行为（V1.4.2 中文态）

点击「切换到中文」（当前语言反向标注，目标语言自称——`resources.ts` LOCALES 设计）：

- `document.documentElement.lang` → **`zh-CN`**；`localStorage['abnk-locale']` → **`zh-cn`**；URL 不变（就地重渲染，title 同步 `ABNK Backoffice · 运营后台`）✅
- 999 错误提示就地变中文：`客户不存在：clientId=999` + 「返回客户列表」✅

### Phase 7 行为态复验（数据集运行时跟随）

- 整页重载（goto /clients）后：zh UI + **en 数据**（Alex POC-A…）——初始解耦态 = D3 修订设计（数据初始语言 = 注入缺省 en-us，与 UI 初始语言独立）✅
- SPA 会话内切换器 en → zh（无整页重载）：数据即刻变中文（**王POC-A / 李POC-B**）——reseedDataSet + dataEpoch remount 生效 ✅（快照 `v632-spa-en.yaml` / `v632-spa-zh.yaml` 对照）

### 中文态（zh-cn）

| 判据 | 实测 | 结果 |
|---|---|---|
| V1.6.3（clients 页 + 分页） | 表头 客户号/姓名/外部编号/手机号/证照状态/证照到期日/操作；证照状态枚举 `已过期`/`有效`；操作列 `详情`；分页 **`共 3 名客户`**；footer `数据口径：P0.3 种子快照（王/李/赵 POC-A/B/C…）——金额格式示例 ¥10,000.00` | ✅ |
| V1.5.3（antd 空态 zh） | 搜索 `无此人zzz` 回车 → **`暂无数据`**（zh_CN 内建） | ✅ |
| V1.6.3（client detail） | heading `客户详情 · 王POC-A1107104347`；label 全中文（客户号/外部编号/姓名/手机号/邮箱/所属机构/状态/证照类型=身份证/证件号/签发日/到期日/记录状态/到期状态（推导）=已过期）；账户产品 `ABNK 活期储蓄`（zh 数据集） | ✅ |
| V1.6.3（loan-ops） | heading 贷款运营；表头 贷款号/客户/产品/本金/利率/期限(月)/状态/操作；操作列 **`审 批`/`放 款`**（disabled 预埋）；脚注「POC 基线只读——审批/放款为预埋操作位」 | ✅ |
| V2.1.5（客户不存在 zh） | /clients/999 → `客户不存在：clientId=999`（插值）+ Empty 兜底同词条 | ✅ |
| V2.1.4（错误口令 zh） | 退出登录（用户菜单「退出登录」）→ admin/wrongpass → **`用户名或口令错误`** | ✅ |
| V1.6.3/1.6.4（login 页） | 中文态 login 页：Backoffice 运营后台 / 用户名 / 口令 / 登 录 / mock 演示口令注记全中文 | ✅ |

### console 终检

- `playwright-cli console`：**Total messages: 3（Errors: 0, Warnings: 0）**——两语言态全路径 0 红错 ✅

结论：backoffice 全流程双语走查全部判据两态成立，V6.3.2 通过。

## V6.3.3 —— mobile web 载体全流程双语走查（复验 V3.3.3/V3.4.4/V3.4.5/V3.4.6/V4.2.6 + Phase 7 行为态）

- 载体：`flutter run -d web-server --web-port=6280 --dart-define=ABNK_DATA_LOCALE=en-us --dart-define=ABNK_ENABLE_SEMANTICS=true`（就绪判据 HTTP 200）；UI 初始语言：预置 `localStorage['flutter.abnk.locale']='"zh"'` 后刷新；自动化 = agent-browser（语义树快照 + `flt-semantics[role=button]` 合成 click——语言区块/退出按钮 ref 点击不可靠，沿 task3.3/task7.2 已知坑口径）
- 截屏归档：`carrier-walkthrough/web-{zh|en}-{login|home|profile}.png`（4 张，MD5 校验唯一）

| 判据 | 实测 | 结果 |
|---|---|---|
| V4.2.6（数据集解耦第一断言） | 预置 zh 后刷新：登录页「手机银行/用户名/密码/登 录」；登录后首页 zh UI（欢迎回来/你好，Alice Green/活期总余额/转账定期贷款明细）+ **en 数据**（`ABNK Current Savings（0000**0011）`）——`--dart-define=ABNK_DATA_LOCALE=en-us` 注入生效，初始解耦成立 | ✅ |
| V3.4.4（zh 七页 + 插值 + 枚举） | login/home/transactions/transfer/fixed_deposit/loans/profile 七页全文案 zh 词条命中——插值：`你好，Alice Green`、`活期总余额 ¥10,000.00`、`余额 ¥10,000.00`、`流水号 100 转出账户新余额：¥9,990.00`、`期限 最长 12 个月`、`额度 ¥1,000.00 ~ ¥500,000.00`；三处枚举映射 zh 命中：`存入`、`等额本息`、`已过期`；Material 内建中文化 `还可输入 40 个字符` | ✅ |
| V3.3.3（切换链路） | Profile 语言区块点 English：整树即时重建为 en（`Welcome back`/`Hi, Alice Green`/`Total savings balance`/`Transfer/Term deposit/Loans/Activity`），存储写入 `localStorage['flutter.abnk.locale']='"en"'`（持久化）；重载后仍中文/英文随存储（boot 读路径双向实测）；**架构注记**：Phase 7 dataEpoch KeyedSubtree remount 使切换后回 Home 页签——Phase 3「停留我的页签」断言被 remount 架构取代（非缺陷，如实记录） | ✅ |
| V3.4.5（en 七页 + 枚举语义重写） | en 态七页走查——`Personal loans`/`Amounts from ¥1,000.00 to ¥500,000.00` 系语义重写；枚举映射 en：`Deposit`、`Expired`、**`Equal monthly installments`**（D2 示例词条）；语言名 `中文`/`English` 原生形态不翻译 ✓；`Retail Customer` | ✅ |
| V3.4.6（异常码化链路两态） | en 态错误口令 → SnackBar **`Incorrect username or password`**；zh 态错误口令 → SnackBar **`用户名或密码错误`**——AuthException → AppExceptionPresenter 按语言查词条端到端 | ✅ |
| Phase 7 行为态（V7.2.3 复验） | zh UI + en 数据态转账 ¥10（余额 ¥9,990）→ 切 en：**余额回 ¥10,000 + Activity 仅 Initial deposit（转账流水消失）**——双重重置证明；再切 zh：数据即刻变 **`ABNK 活期储蓄`**（运行时目录切换跟随） | ✅ |
| console 终检 | `agent-browser console` → `[error]|Uncaught` 计数 **0** | ✅ |

结论：mobile web 载体全流程双语走查全部判据成立，V6.3.3 通过。

## V6.3.4 —— mobile iOS/Android 载体 drive 走查（条件门）

- 设备条件门实测（2026-11-16）：`flutter devices` → **iPhone 16 Pro 模拟器可用**（iOS 18.3，`C6520335-…`）；**Android 无设备/模拟器** → Android 段挂账（见下）。
- iOS 走查工具：`flutter drive -d <sim> --driver=test_driver/integration_test.dart --target=integration_test/v634_tmp_test.dart --dart-define=ABNK_DATA_LOCALE=en-us`（临时 drive 脚本——走查后已删除，git 零残留；截图经 `ABNK_SHOT_DIR/ABNK_SHOT_PREFIX=ios` 落盘，沿 VP1.3.5 基建）。
- 关键路径（登录 → 首页 → 我的语言切换 → 复验切换生效，zh/en 两态 + 数据集跟随）：**All tests passed**，5 张截屏归档 `carrier-walkthrough/ios-0[1-5]-*.png`：
  - `01-login`（boot 态：上轮持久化 zh）→ `02-home-initial`（zh UI + en 数据——初始解耦）→ `03-profile`（语言卡：中文选中勾）→ `04-home-en-switched`（切 en 后首页：Welcome back + ABNK Current Savings）→ `05-home-zh-switched`（切 zh 后首页：欢迎回来 + **ABNK 活期储蓄**——数据集跟随实机渲染验证）
- **走查中拦到并修复的三处走查脚本问题（应用零改动，判据未放宽）**：
  1. run 1 断言落空：iOS 切换语言后停留「我的」页签（V3.3.3 原口径行为），断言写在首页——修正为先导航首页再断言；
  2. run 2 切换无效：上一轮已持久化 zh + `setLocale` 对重复选择短路（`app_scope.dart:104`）——修正序列为先切 en（真实切换）再切 zh；
  3. run 3 tap 落空：语言卡在 iOS 视口下方（English 行视口外）——P3.3 已知坑实测复现，`ensureVisible` 滚动后 tap 生效。
  - 架构注记：web DDC 构建下 epoch remount 后回 Home 页签，iOS 模拟器下保留当前页签——同一 remount 机制的载体渲染差异，非缺陷，如实记录。
- **Android 段挂账（对齐 P3.6 挂账惯例，不阻塞 Part 收口）**：本机无 Android 设备/模拟器（`flutter devices` 无 android 项；`flutter emulators` 可后补启动）。复验计划：Android 模拟器可用时以同一临时 drive 脚本口径（`ABNK_SHOT_PREFIX=android` + `convertFlutterSurfaceToImage`，walkthrough_test.dart 已含该转换分支）重跑五步关键路径即可；web 载体判据（V6.3.3）已覆盖逻辑层，iOS 与 Android 共享全部 Dart 代码，载体差异仅渲染引擎。

结论：iOS 载体 zh/en 两态关键路径走查全过（≥4 张关键路径截屏齐备）；Android 段挂账不阻塞，V6.3.4 通过。
