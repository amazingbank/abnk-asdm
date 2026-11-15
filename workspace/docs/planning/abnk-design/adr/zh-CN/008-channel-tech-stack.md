# ADR-008：渠道层技术架构（网关 SCG + 前端 React + 移动混合）

- 状态：Accepted
- 日期：2026-10-26
- 决策人：ABNK 项目负责人

## 背景

ADR-005 确定前端自建三套但未定技术栈；`02-architecture/api-gateway.md` §4 将网关选型（Spring Cloud Gateway / APISIX / Kong）留待 Phase 3 评审。2026-10-26 技术架构规划评审**提前定案**：技术栈影响 custom 模块、CI、契约生成的全局约定，越早定案约束能越早固化。官网 Landing Page 已由 bolt.new 以 React + TypeScript + Vite + Tailwind 生成并验收（原 `abnk-web001`，现入库 `abnk-system/channels/website/`）。

## 决策

**渠道层（L3）统一技术栈：**

1. **网关**：Spring Cloud Gateway + Spring Security OAuth2/OIDC（Keycloak，Phase 3 引入）；国密商密收口本层（ADR-007）
2. **前端框架**：React + TypeScript + Vite + Ant Design（管理后台用 Ant Design Pro）
3. **移动端**：混合 App——原生薄壳（Kotlin / Swift / ArkTS-鸿蒙）只做安全与设备能力（安全键盘、生物识别、推送、行方 SDK），业务页面全部 H5（React），经网关调用；小程序（Taro）为远期可选
4. **官网**：`channels/website/`（品牌站，不经网关、零业务 API、静态部署）
5. **契约先行**：网关维护收敛后的 OpenAPI，`channels/shared/` 由此生成 TS client，前端永不手写 API 类型

## 理由

1. **银行惯例**：Ant 系是国内金融后台事实标准；混合 App 是国内手机银行主流形态；2026 年鸿蒙原生 App 已是既成事实，ArkTS 为 TS 超集、与全仓 TS 语言族同源
2. **AI 适配性**：React+TS 是 LLM 语料最厚的前端栈（bolt.new 等生成工具默认产出 React）；Spring 是 Java 侧语料最厚的生态；业务代码 100% TS，移动端仅保留小体量、长期稳定的壳代码
3. **同栈复用**：SCG 与 Fineract/custom 同 JVM 栈——租户注入/字段脱敏即 Java 过滤器（AI 可直接编写），观测（Micrometer→Tempo）原生集成
4. 备选否决：APISIX/Kong 的租户注入需 Lua/插件开发（AI 适配性降一档，运维分离）；Vue 3 + Ant Design Vue 可行但 AI 语料弱于 React——若未来合作厂商强约束 Vue 再以新 ADR 重议

## 后果

### 正面
- 全仓语言收口：Java（后端）+ TypeScript（前端/移动/ArkTS 同族）+ Python（脚本）
- 加渠道 = 加壳/加目录，业务与契约零改动——"契约先行 + 薄客户端"模式的范例价值

### 负面 / 风险与缓解
- SCG 为 JVM 网关，资源占用高于 Nginx 系 → 容器化限配 + Phase 3 末压测基线
- 鸿蒙壳（ArkTS）生态新 → Phase 4 末专项 PoC，壳代码量刻意压到最小

### 必须遵守的衍生约束
- 前端**永不直连** Fineract 8443，一律经网关（承接 ADR-005）
- 前端 API 类型一律从网关 OpenAPI 生成（`channels/shared/`），不手写
- 移动端壳不承载业务逻辑；原生能力经桥接层暴露给 H5
- 官网（`channels/website/`）不得调用任何业务 API，数据只允许本地 JSON
- 网关生产黑名单：`/v1/internal/*` 全部端点（`02-architecture/api-gateway.md` §3）
- 渠道前端项目登记到 config.json 的 `processes[]`（承接 ADR-005）
