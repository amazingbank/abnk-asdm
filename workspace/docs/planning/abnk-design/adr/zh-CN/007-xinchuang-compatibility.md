# ADR-007：信创兼容策略（主线开源 + 兼容层）

- 状态：Accepted
- 日期：2026-10-26
- 决策人：ABNK 项目负责人

## 背景

ABNK 首批业务落地中国市场（`01-product/positioning.md`），银行监管环境对国产化（信创）有现实要求：芯片（鲲鹏/飞腾/海光）、OS（麒麟/openEuler）、数据库（达梦/人大金仓/GaussDB）、国密商密（SM2/SM3/SM4，人行监管趋势）。2026-10-26 技术架构规划评审需回答：开源技术主线如何兼容信创，而不产生第二条代码线。相关既有决策：ADR-003（PG 单宿主）、ADR-005（前端经网关）。

## 决策

**主线开源、信创走兼容层，单一代码线。四原则：**

1. **主线开源，不 fork 信创分支**——信创是部署目标，不是代码分支
2. **协议标准优先**（OIDC / S3 / Redis 协议 / Kafka 协议 / K8s 上游 API）——替换成本 = 改配置，不是改代码
3. **兼容性左移进 CI**——multi-arch 构建（amd64/arm64）+ 国产库兼容 job + 国产 OS 基础镜像，问题在提交时暴露而非验收时
4. **商密改造收口网关**——SM2 双证书 TLS（Tongsuo/铜锁）与 SM3/SM4 应用签名（BouncyCastle）集中在渠道网关（`channels/gateway/`），Fineract 与前端零侵入

## 理由

1. PG 单宿主（ADR-003）恰好是数据库信创最优路径：KingbaseES / openGauss(GaussDB) 均为 PG 血统，迁移面最小——**补充约束而非推翻决策**
2. JVM 系中间件（Kafka/网关/外围服务）对国产 OS/CPU 无障碍，仅需 JDK 发行版适配（毕昇 JDK / Dragonwell，代码零改动）
3. 双代码线与 AI 时代研发范例的目标相悖；兼容层模式才具备可复制性

## 后果

### 正面
- 信创验收路径清晰，认证目标矩阵可机读、可进 CI
- IAM/缓存/对象存储等组件均为协议级平替，替换不产生代码侵入

### 负面 / 风险与缓解
- 国产库兼容需持续投入 → CI 兼容 job（openGauss/KingbaseES 容器）Phase 4 起常态运行
- 国密 TLS 依赖国内开源库成熟度 → Phase 3 安全评审先行 PoC

### 必须遵守的衍生约束
- Liquibase changelog 避免散用 PG 专有扩展；必须用时集中封装并标注（保证 KingbaseES/openGauss 可迁移）——对 ADR-003 的补充约束
- IAM 只用 OIDC 标准协议，不绑 Keycloak 私有特性（国产 IdP 可配置级替换）
- 缓存统一用 Valkey（Redis 协议开源分支），禁止使用 Redis 私有 API；避免 Redis 商业许可争议
- 部署产物必须 multi-arch（amd64/arm64）；Helm 保持上游标准，不绑厂商 CRD
- 生产部署保留 JAR 直启路径（VM 场景），与容器路径并存（对齐 `02-architecture/customization-strategy.md` §4 双路径）
- **认证目标矩阵**：DB = KingbaseES / openGauss；OS = 麒麟 V10 / openEuler；芯片 = 鲲鹏(ARM) / 海光(x86)；JDK = 毕昇 / Dragonwell
