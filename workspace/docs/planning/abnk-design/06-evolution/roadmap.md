# 路线图（Phase 0–5）

> **性质**：设计文档。每阶段有明确入口/出口判据；当前状态实时同步到本文档与主 README 状态看板。

---

## 1. 总览

| 阶段 | 目标 | 状态 | 出口判据（全部满足才进入下一阶段） |
|---|---|---|---|
| **Phase 0** | 本地可调试基线 | ✅ **完成（2026-10-24）** | 环境健康 / API 200 / 280 表 / 0 FAILED 迁移 |
| **Phase 1** | 原生能力端到端验证 | 🚧 **当前（已解锁）** | 详见 `phase-1-validation.md` §1 五条判据 |
| **Phase 2** | 定制框架 + L1 本地化 | 排期 | 见下 §2 |
| **Phase 3** | 渠道层（网关+前端） | 排期 | 见下 §2 |
| **Phase 4** | 外围集成（事件+支付+报送） | 排期 | 见下 §2 |
| **Phase 5** | 数据智能（AOS+数仓+AI） | 远期 | 见下 §2 |

## 2. 各阶段展开

### Phase 1（当前）——原生能力验证
- 施工图：`phase-1-validation.md`（12 步）
- 交付：冒烟脚本（回归资产）+ E2E 运行方式验证 + 各域**行为基线报告**（savings/lending 的待验证清单回填）
- **零后端代码**

### Phase 2——定制框架 + L1
- `custom/abnk/` 骨架（`customization-strategy.md` §1）+ 第一个模块（identity 证照校验）
- 自建 CI 门禁（`engineering-conventions.md` §3）
- L1 三件：时区/币种固化、**COA 重建**（`accounting.md` 的 5 步路径）、计息差距落地（savings/lending 的 Phase 2 段）
- 季度 rebase 流程首跑（`release-strategy.md`）
- 出口：12 步链路带**分录断言**全绿；custom 模块 CI 通过；第一波产品模板化

### Phase 3——渠道层
- API 网关 MVP（路由+鉴权+租户注入）+ 管理后台 → 柜面（`api-gateway.md` 里程碑）
- OAuth2/Keycloak 接入（Basic 退役）
- 出口：柜员可全界面完成第一波产品业务操作

### Phase 4——外围集成
- 事件总线最小闭环（`event-bus.md` 落地步骤）→ 通知服务
- 支付适配（`payments.md`）+ 反洗钱
- EAST/1104 报送框架（`regulatory-reporting.md` 开项前置：COA 稳定一个报送周期）
- 出口：首笔经支付通道的完整交易端到端；首个报送口径映射完成

### Phase 5——数据智能
- AOS 代码本体导入（`aos-integration.md`）
- 数仓 + 报表 + AI 应用
- 出口：定制影响分析走图谱查询（代替逐文件扫描）

## 3. 跨阶段原则

1. **每阶段产出回归资产**（Phase 1 脚本 → Phase 2 分录断言 → Phase 3 UI E2E）——不许只交付功能不交付验证
2. 产品线波次（ADR-006）约束每阶段的业务范围：第二波（经营贷）在 Phase 3+ 引入，远期产品线不进详细设计
3. 多租户按 ADR-004 分阶段：Phase 2 建租户生命周期管理，Phase 3+ 视业务开放多法人

## 4. 风险燃尽表（随阶段更新）

| 风险 | 引入 | 缓解 | 状态 |
|---|---|---|---|
| custom PoC 破裂 | Phase 2 | ADR-002 措施 + rebase 检查单 | 监控中 |
| COA 设计依赖会计专业输入 | Phase 2 | 尽早引入业务侧；模板先行 | **未启动（关键路径）** |
| LPR/报送等监管口径不清 | Phase 2–4 | 业务侧输入清单已列（各域文档） | 未启动 |
| working-capital 成熟度 | Phase 3+ | 专项 PoC 前置 | 未启动 |
