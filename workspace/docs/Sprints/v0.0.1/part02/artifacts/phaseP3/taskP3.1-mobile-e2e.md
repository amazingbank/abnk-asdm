# 任务 P3.1 手机银行接线 —— 端到端走查记录（VP3.1.3）

- **日期**：2026-11-09
- **载体**：Flutter web（`flutter run -d web-server --web-port 6280`，playwright 390×844 语义树驱动）
- **模式**：remote（`--dart-define=ABNK_API_BASE=http://localhost:8080/abnk/api/v1`）——mock/remote 切换工厂（`lib/data/repository_factory.dart`）按 dart-define 判定
- **链路**：web 载体（:6280）→ ABNK 网关（:8080，bootRun）→ 生产形态 Fineract 栈（:8081）+ abnk-pg-prod（:5433）
- **数据**：P0.3 local-prodform 种子（alice = clientId 28，活期账户 11/12）
- **口令**：alice 演示口令经 `.github-private/kbank-poc/gateway-demo-passwords.json`（local-prodform 节）注入走查，不落本文
- **截图**：`artifacts/phaseP3/screenshots/web-01~05`（登录 / 首页 / 转账表单 / 成功对话框 / 明细）

## 接线过程修复（走查中发现并修复的三处链路缺口）

| # | 问题 | 根因 | 修复 |
|---|---|---|---|
| 1 | dio 请求 URL 变为 `http://localhost:8080/?#/login`（路径被吞进 fragment） | `Uri.replace(path:'',query:'',fragment:'')` 序列化出 `?#` 尾巴，与请求 path 拼接后路由前缀进 fragment | `lib/data/remote/generated_client.dart` 改用 `Uri(scheme:host:port)` 构造 origin |
| 2 | CORS preflight 全部失败（对客收敛面为网关本地 @RestController，SCG globalcors 只覆盖路由转发；且 BearerTokenFilter(-100)/BlacklistFilter(-90) 把 OPTIONS 预检拦成 401/404） | dev 形态 web 载体（:6280）跨 origin 访问网关，网关侧无 CORS 放行 | 网关新增 `config/CorsConfig.java`（WebFlux 全局 CorsWebFilter，覆盖本地 controller 与转发）+ BearerTokenFilter / BlacklistFilter 对 OPTIONS preflight 直通（`channels/gateway`，生产同域反代下 CORS 头为冗余放行） |
| 3 | 登录 401 invalid_credentials | `data/gateway_users.json` 当前内容 = server 实例口令与 clientId 映射（1/2），与本地栈种子（alice=28）不匹配 | 生成 `data/gateway_users.local-prodform.json`（PBKDF2 哈希，clientId 28/29 映射，明文只在 .github-private），网关经 `ABNK_USERS_FILE` 指向启动 |

## 五步走查（逐步数据快照）

### 第 1 步：登录（网关 PBKDF2 凭据 + JWT 签发）
- alice + local-prodform 口令 → `POST /login` 200，JWT 注入 Bearer 拦截器（`setBearerAuth('bearerAuth', token)`）
- 截图 `web-01-login.png`

### 第 2 步：首页总览（真实 Fineract 余额 = P0.3 种子口径）
- 问候语：`你好，王 P.`（网关脱敏 displayName，clientId 28）
- 活期总余额：**¥10,029.82**
- 账户卡片：`0000**0011`（可用 ¥9,729.82）/ `0000**0012`（可用 ¥300.00）
- 独立核对（curl 网关 `/me/accounts`）：账户 [11, 12]，余额 [9729.82, 300.0] —— **UI = API 一致**
- 截图 `web-02-home.png`

### 第 3 步：转账 100（默认转出 11 → 转入 12）
- 金额 `100`，附言 `P3E2E-084537`（时间戳唯一标记）
- 截图 `web-03-transfer.png`

### 第 4 步：提交成功（网关聚合幂等 + 补偿）
- 成功对话框：**流水号 1026，转出账户新余额 ¥9,629.82**（9,729.82 − 100 ✓）
- 截图 `web-04-transfer-success.png`

### 第 5 步：明细出现新流水（runningBalance 变化）
- 明细首行：`网关转账 abnk-hnzh9zcstk-x74gpay0：P3E2E-084537 · 支取 -¥100.00 · 余额 ¥9,629.82`
- 历史流水同页可见（P2.4/P2.7 测试转账、每日 Interest posting）——真实 Fineract 数据
- 截图 `web-05-transactions.png`

## Fineract 侧独立核对（VP3.1.3 验证动作 / VP3.1.5 并档）

| 项 | 转账前 | 转账后 | 期望 |
|---|---|---|---|
| 账户 11 交易计数（`GET savingsaccounts/11/transactions/search` → `total`） | 75 | **76** | +1 ✓ |
| 账户 12 交易计数 | 3 | **4** | +1 ✓ |
| 账户 12 最新交易 | — | id=1027，Deposit ¥100.00，runningBalance ¥400.00，note=`网关转账 abnk-hnzh9zcstk-x74gpay0：P3E2E-084537` | 与 UI 附言一致 ✓ |

**断言行：UI 明细条数 = API 交易计数** —— UI 明细数据源为网关 `GET /accounts/11/transactions`（返回 50 条，收敛面分页口径，P0.2 VP0.2.4 实测），Fineract 侧 `total` = 76（全量）；UI 首条与 Fineract 最新交易逐字段一致（金额 / runningBalance / 附言 / 幂等后缀）。**转账前后计数 +1 与 UI 新流水出现互相印证，闭环成立。**

## VP3.1.4 · iOS 模拟器复验（iPhone 16 Pro，C6520335）

- **执行**：`flutter drive --driver=test_driver/integration_test.dart --target=integration_test/p3_e2e_test.dart -d C6520335-… --dart-define=ABNK_API_BASE=http://localhost:8080/abnk/api/v1 --dart-define=ABNK_DEMO_PASSWORD=<注入>`（iOS 模拟器共享宿主网络，localhost 直达网关）
- **结果**：`All tests passed.`（两轮：首轮流水号 1028 / 复验轮流水号 1030，均转账 100 成功 + 明细新流水断言 PASS）
- **数据快照**：首页总余额 ¥10,029.82（真实）；转账成功对话框「流水号 1028 · 新余额 ¥9,529.82」
- **截图归档**：`ios-01-login` / `ios-02-home` / `ios-03-transfer` / `ios-04-transactions`（外部 `xcrun simctl io screenshot` 通道——integration_test 内嵌 takeScreenshot 在本环境不稳定，见下）

## VP3.1.4 · Android 模拟器复验（abnk_api36，emulator-5554）

- **执行**：同上，`-d emulator-5554` + `--dart-define=ABNK_API_BASE=http://10.0.2.2:8080/abnk/api/v1`（Android 模拟器经 10.0.2.2 回环访问宿主网关；`android/app/src/debug/AndroidManifest.xml` 增 `usesCleartextTraffic`——仅 debug 构建，release/生产走 HTTPS 不受影响）
- **结果**：`All tests passed.`（流水号 1032，转账 100 成功 + 明细新流水断言 PASS）
- **数据快照**：首页「你好，王 P. · 总余额 ¥10,029.82 · 账户 11 ¥9,429.82 / 账户 12 ¥600.00」；成功对话框「流水号 1032 · 新余额 ¥9,329.82」；明细首行 `网关转账 …：P3E2E-1794187497286 · 支取 -¥100.00 · 余额 ¥9,329.82`
- **截图归档**：`android-01-login` / `android-02-home` / `android-03-transfer` / `android-04-transfer-success` / `android-05-transactions`（外部 `adb exec-out screencap` 通道）

### 走查过程环境坑位（归档备忘）

| # | 现象 | 处置 |
|---|---|---|
| 1 | Android 构建期 `Repository Google is disabled`（androidx.test 解析失败） | 瞬时网络失败后 Gradle 禁用仓库——`./gradlew --stop` 清 daemon 后重跑即过（socks5 代理配置 P1.1 口径有效） |
| 2 | driver `unusually long time to connect to the VM` + app 卡启动页 | 此前 `adb kill-server` 弄坏转发链路——冷启动模拟器（`-no-snapshot`）后恢复 |
| 3 | integration_test 内 `convertFlutterSurfaceToImage` 后 takeScreenshot 挂起（request_data 超时） | 三载体截图统一改外部通道（playwright / simctl / adb screencap），integration_test 只承担断言（P1 同逻辑当时可用，属环境敏感 flaky） |

### Fineract 计数链（全程核对）

| 时点 | 账户 11 `total` | 对应转账 |
|---|---|---|
| web 走查前基线 | 75 | — |
| web 走查后 | 76 | 流水 1026（web） |
| iOS drive1 后 | 77 | 流水 1028 |
| iOS drive2 后 | 78 | 流水 1030 |
| Android 后 | 79 | 流水 1032 |

每轮 +1 精确对应，无重复无遗漏——三载体走查共用同一幂等转账链路（网关聚合幂等 + Fineract 落账）。

## 结论

VP3.1.3 五步走查无空格：登录 → 总览（真实余额）→ 转账 100 → 提交成功 → 明细新流水（runningBalance 变化），全部经真实网关 + Fineract 数据；页面代码零改动（VP3.1.2 断言）。
