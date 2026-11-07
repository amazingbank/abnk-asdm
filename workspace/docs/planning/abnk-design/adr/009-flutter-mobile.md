# ADR-009：手机银行移动端采用 Flutter（取代 ADR-008 的"原生薄壳 + H5"移动方案）

- 状态：Accepted（2026-11-07 转正——决策已由 Part02 主计划 D4 落定：Flutter web + iOS + Android 三目标；执行载体为 Sprint v0.0.1 Part02 Phase P1，工具链经任务 P1.1 实测就位）
- 日期：2026-11-03
- 决策人：ABNK 项目负责人
- Supersedes：ADR-008 第 3 点（移动端混合 App 方案）

## 背景

ADR-008 将移动端定为「原生薄壳（Kotlin/Swift/ArkTS）只做安全与设备能力，业务页面全部 H5（React）」。该决策的核心理由是：全仓语言收口到 Java + TS + Python，业务代码 100% TS，移动端只留长期稳定的小体量壳。

项目负责人现明确要求：手机银行（个人客户对客渠道）采用 **Flutter** 构建原生跨平台应用，并作为 KBank POC 的渠道侧交付物之一。因此需要就移动端技术栈重新拍板，仅推翻 ADR-008 的「移动端」一条，其余（SCG 网关、React 管理后台/柜面、契约先行）不变。

## 决策

**手机银行移动端采用 Flutter（Dart）构建，取代 ADR-008 的「原生薄壳 + H5」混合方案。**

| 维度 | ADR-008 原方案 | 本 ADR 新方案 |
|---|---|---|
| 移动端框架 | 原生薄壳 + H5（React） | Flutter（Dart），业务逻辑在客户端内 |
| 业务代码语言 | TS（H5） | Dart |
| 壳职责 | 只做安全/设备能力 | 不再区分壳与业务——Flutter 一体化承载 |
| iOS/Android | 双壳 | Flutter 单代码库双平台 |
| 鸿蒙 | ArkTS 壳（Phase 4 末 PoC） | Flutter 鸿蒙适配（OpenHarmony Flutter 分支）远期评估 |

## 理由

1. **原生体验与金融 UI 一体化**：银行 App 需要安全键盘、生物识别、手势/动画、推送等原生能力，Flutter 单框架统一承载 UI 与设备能力，不再维护「壳 + H5」两套心智。
2. **单代码库交付 iOS/Android**：POC 阶段人员有限，Flutter 一套 Dart 代码同时交付双平台，验收与演示成本最低。
3. **AI 适配性可接受**：Dart/Flutter 是主流框架中 LLM 语料较厚的移动栈（弱于 React 但显著强于 Kotlin/Swift 双写与 ArkTS），配合「契约先行 + OpenAPI 生成 Dart client」可把 AI 编码风险压在薄 client 层。
4. 备选否决：保留 ADR-008 混合方案会与负责人「采用 Flutter」的明确要求冲突；React Native 相较 Flutter 在金融 App 的原生键盘/渲染一致性上无优势。

## 后果

### 正面
- 手机银行一套代码双端交付，POC 演示与后续迭代成本最低
- 业务逻辑内聚在客户端，UI 体验完全可控（承接 ADR-005「渠道体验差异化」）
- 渠道层「契约先行」模式完整复用：网关 OpenAPI 生成 Dart client，前端永不手写 API 类型

### 负面 / 风险与缓解
- **语言栈新增 Dart**（原「Java + TS + Python」三语言收口被打破）→ Dart 仅限手机银行一个渠道，其余前端仍 TS；设计系统 tokens 需另出一份 Flutter `ThemeData` 映射（官网 `tailwind.config.js` 暖色 tokens 为唯一事实源，双份映射纳入共享验收）
- **AI 语料弱于 React/TS** → 用「契约先行 + 代码生成」把 Dart 手写面压到 UI 层；移动端接入 `config.json` 的 `processes[]` 与验收脚本，纳入 abnk-debugger 托管
- **鸿蒙路径变化** → 原 ArkTS 壳方案废弃，鸿蒙适配改走 OpenHarmony Flutter 分支（Phase 4 末专项 PoC，不阻断当前）
- **安全键盘/生物识别的原生实现** → Flutter 生态有成熟方案（`local_auth`、自绘安全键盘），在 ADR-007 信创约束下 Phase 3 评审选型

### 必须遵守的衍生约束
- 手机银行**永不直连** Fineract 8443，一律经网关（承接 ADR-005/008）
- 手机银行 API 类型从网关 OpenAPI 生成 Dart client（`channels/mobile-banking/` 内 `openapi-generated/`），不手写
- 公网安全基线：OAuth2/OIDC（Keycloak）、限流、字段脱敏（承接 `api-gateway.md` / `security-compliance.md`）
- 设计系统：颜色/字体沿用 `channels/website/` 暖色 tokens 与字体栈（Oxanium + Noto Sans SC + Noto Serif SC），Flutter 侧出对应 `ThemeData` 映射
- 端口登记：手机银行属客户端 App，无 dev-server 端口；其模拟/调试端口如需（如 `flutter run -d web-server` 的调试口）按 `docs/port-allocation.md` 62xx 段登记后再写配置
