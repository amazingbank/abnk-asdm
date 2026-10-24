# 可观测性

> **性质**：设计框架（Phase 2 落地）。**原则：复用官方栈，不另造**（`00-baseline/fineract-codebase.md` §5）。

---

## 1. 现成资产（版本实测核实）

| 组件 | 版本 | 用途 |
|---|---|---|
| Loki | 2.9.2 | 日志聚合（`logs/fineract.log`、`logs/postgres.log` 已统一落宿主） |
| Prometheus | v2.47.2 | 指标（Fineract actuator/micrometer） |
| Grafana OSS | 10.2.0 | 看板 |
| Tempo | 2.2.4 | 分布式追踪（网关接入后跨层串联） |

入口编排：`config/docker/compose/observability.yml`（仓库自带）。

## 2. 接入规划

| 阶段 | 动作 |
|---|---|
| Phase 1（当前） | 免观测——`logs/` 三件套 + `/actuator/health` 已够调试 |
| Phase 2 | 起 observability compose（登记 `config.json`）；Loki 收应用日志；Prom 抓 8443 actuator；Grafana 建基础看板（命令时延、连接池、JVM） |
| Phase 3 | 网关接入 Tempo 追踪；前端错误上报 |
| Phase 4 | 事件流监控（Kafka lag）、外围服务全量接入 |

## 3. 必建看板（Phase 2 验收）

1. **命令通道健康**：command 处理时延/重试率（`domain-concepts.md` 的排障语义）
2. **Liquibase/作业**：COB 运行时长、成败（41 作业清单在 `/v1/jobs`）
3. **连接池**：hikari 指标
4. **租户维度**：按 `Fineract-Platform-TenantId` 拆分的关键指标（ADR-004）

## 4. 日志规范

- 应用日志集中在 `logs/`（现有布局）；容器化后统一输出到 Loki
- custom 模块日志用 `com.abnk.fineract.*` logger 命名空间——与核心日志可区分、可分级
- 禁止在 custom 模块打印租户敏感全量数据（证照号等——脱敏）
