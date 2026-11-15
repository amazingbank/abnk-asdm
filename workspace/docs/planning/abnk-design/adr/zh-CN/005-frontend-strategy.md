# ADR-005：前端自建三套

- 状态：Accepted
- 日期：2026-10-25
- 决策人：ABNK 项目负责人

## 背景

Fineract 是纯 API 后端，无自带生产级前端。仓库内有 `docker-compose-web-app.yml` / `community-app`（社区前端，Mifos 时代产物）可作过渡。ABNK 需要三类前端：柜面（内部）、网银/手机银行（客户）、管理后台。事实依据：`00-baseline/api-surface.md`（603 端点）、`fineract-codebase.md`（`fineract-client`/`fineract-client-feign` 自动生成 SDK）。

## 决策

**前端全部自建，按三套规划：**

1. **管理后台**（先行）：租户/产品/配置/作业管理，内部运维与后台人员使用
2. **柜面**（第二）：营业网点柜员操作，开户/存取/放款录入
3. **网银 + 手机银行**（第三）：客户自助渠道

过渡策略：Phase 1 验证期间**不建任何前端**（纯 API 脚本验证）；Phase 3 启动前可用社区 web-app 作临时对照参考，不作为交付物。

## 理由

1. 三套前端的用户/交互/安全诉求差异巨大，一套统一前端注定都做不好
2. 603 个 API + 自动生成的 `fineract-client` SDK（含 Feign 变体）→ 前端对接成本可控，**不手写 SDK**
3. 社区前端的交互是 Mifos 微金融语境，与银行业务形态不匹配，深度改造不如自建
4. 自建前端是 ABNK 渠道体验差异化的载体（ADR-001 中四件价值事之一）

## 后果

### 正面
- 渠道体验完全可控，是产品差异化的一部分
- 前端只依赖 API 契约（OpenAPI spec），与 Fineract 内核解耦

### 负面 / 风险与缓解
- 三套前端 = 三支团队的长期投入 → 分阶段交付（管理后台最小集起步），共享设计系统与组件库
- 直接暴露 Fineract API 给浏览器的安全风险 → 一律经 API 网关（`02-architecture/api-gateway.md`），网关做鉴权、限流、字段收敛
- PoC 风险传导（ADR-002）：Fineract API 变化 → 网关层屏蔽版本差异，前端不直连 Fineract

### 必须遵守的衍生约束
- 前端**永不直连** Fineract 8443，一律走网关
- 客户端 SDK 用 resolve 任务生成的 `fineract-client(-feign)`，不手写
- 前端项目登记到 config.json 的 `processes[]`（含端口与 preview 信息）
- 网银/手机银行面向公网，安全基线高于内部系统（`04-operations/security-compliance.md`）
