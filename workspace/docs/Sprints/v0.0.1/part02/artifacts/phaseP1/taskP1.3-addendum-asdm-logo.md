# Task P1.3 增补 — ASDM logo 接入（应用图标 + 登录页）

日期：2026-11-07　|　性质：P1.3 收口后的用户指令增补（超出原 P1.3 计划范围）
工程：abnk-system/channels/mobile-banking

## 需求

1. 模拟器桌面看不到 app 图标（排查 + 修复）
2. 应用图标使用 ASDM logo
3. 登录页出现 ASDM logo

## 排查结论：为什么"看不到图标"

- `flutter drive`/`flutter run` 装到模拟器的 app 一直**有**图标，但 P1.3 建工程沿用
  `flutter create` 模板——**Flutter 默认占位图标（Flutter 鸟）**，从未定制，不识别很正常。
- iOS 侧叠加一个摆放问题：新装 app 被排在**第 2 页第 7 槽**（IconState.plist），
  第 1 页被 Apple 默认应用占满——不翻页根本看不到。已改 IconState.plist 把
  `ai.amazingbank.abnkMobile` 挪到第 1 页。

## 实现

**图标资产**（源头：`channels/website/public/images/logo/asdm-icon-transparent.svg`——
ASDM 螺旋标志矢量图，靛紫色系 10 层旋转圆角矩形）：

- headless Chromium 按 1024×1024 栅格化 SVG（无缩放损失）：
  - `assets/brand/app-icon-1024.png`——奶油底 #FAF7F2 + 螺旋居中 640/1024（iOS 全档 + Android legacy）
  - `assets/brand/app-icon-adaptive-fg.png`——透明底前景 520/1024（Android 自适应安全区口径）
  - `assets/brand/asdm-logo.png`——透明底整 logo（登录页展示资产）
- `flutter_launcher_icons ^0.14.4`（`flutter_launcher_icons.yaml`）生成：
  iOS AppIcon 全 24 档（`remove_alpha_ios: true`）+ Android mipmap legacy/自适应
  （自适应底色 #FAF7F2）
- 登录页：`login_page.dart` 品牌标题上方加 `Image.asset('assets/brand/asdm-logo.png')`
  （88×88，Key `login-logo`）；pubspec assets 段登记

**过程修复**：首版图标 HTML 的背景选择器写错（`#bg` vs `id="icon"`），底色漏成纯白；
以严格像素校验（纯白=0、奶油>92 万）发现并重生成。

## 验证（像素级，playwright + canvas 扫描；本机无多模态目验）

| 载体 | 图标（桌面） | 登录页 logo |
|---|---|---|
| Android（abnk_api36） | dock 位 126×126 奶油簇 + 簇内 3785 靛紫像素 ✓ | 顶部中央 9198 靛紫像素 ✓ |
| iOS（iPhone 16 Pro，第 1 页） | 180×180 奶油簇 + 簇内 3647 靛紫像素 ✓ | 顶部中央 5164 蓝紫像素 ✓ |
| web（:6280） | 不适用 | 顶部中央 720 蓝紫像素 ✓ |

- 产物档校验：1024 源图 cream=925393 / white=0 / indigo=115508；iOS 180px 渲染档
  cream=27755 / white=0（flutter_launcher_icons 重采样不引入白底）
- `flutter analyze`：No issues found!；`flutter test`：13 用例全绿（登录 smoke 增加 logo 断言）
- `flutter build apk --debug` + `flutter run`（iOS）安装链路复验通过

## 归档截图（artifacts/phaseP1/screenshots/）

**2026-11-07 18:17–18:35 整套重抓**（logo 接入后统一版本，覆盖旧图）：

- `web-01` ~ `web-07`（含 03b/04b/05b/05c 共 11 张）——playwright 七页走查，console 0 errors；
  明细页含本次会话新流水（本人账户转账 -¥2,500 余额 ¥7,500 / 定期开户 -¥5,000）
- `ios-01` ~ `ios-04`、`android-01` ~ `android-04`——flutter drive 四页走查（All tests passed）
- `ios-00-home-icon.png` / `android-00-home-icon.png`——桌面图标在位
- 重抓后像素抽验：登录页 logo 三平台在位（iOS 5164 / Android 3987 / web 640 蓝紫像素）；
  桌面图标簇在位（iOS 180×180 奶油簇+3647 靛紫；Android dock 78×90 簇+3227 靛紫）

## 遗留与备注

- iOS bundle ID 为 `ai.amazingbank.abnkMobile`（flutter create 对 snake_case 项目名做驼峰化），
  Android 包名 `ai.amazingbank.abnk_mobile`——两平台不同，脚本操作时勿混用
- `flutter build ios --no-codesign` 产物未签名，`simctl launch` 会 code=4 拒启；iOS 调试装跑
  一律走 `flutter run`/`flutter drive`
- **`flutter drive` 结束会卸载双平台 app**（实测：iOS listapps 无 abnkMobile；Android
  `pm list packages` 0 条），Android 侧同时从 launcher 消失——需要桌面图标展示时，drive 之后
  必须 `adb install -r`（Android）/ `flutter run` 一次（iOS）重装，iOS 还需按需补写
  IconState.plist（"排查结论"节方法）
- **桌面图标验证正确姿势**（18:28 版 android-00-home-icon.png 曾因 drive 卸载而无效，
  且像素盲扫把 dock 位 Settings 图标误判为 ASDM 图标——已修正重拍）：
  Android 用 `adb shell uiautomator dump` 拿图标节点 bounds 再做框内色判据；
  iOS 用 IconState.plist + 既有格位。纯色簇盲扫不可信
- **应用显示名修正**（2026-11-07 18:45）：Android `android:label` `abnk_mobile` → `ABNK`；
  iOS `CFBundleDisplayName` `Abnk Mobile` → `ABNK`（launcher 标签同步生效，
  uiautomator 复验 desc="Predicted app: ABNK"）
- 图标源 HTML 与扫描脚本为一次性工具，置于 /tmp 未入库；如需复刻，本文件步骤可复现
