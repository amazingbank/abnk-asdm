# 事件总线（Kafka）

> **性质**：设计框架（Phase 4 启动时细化）。机制事实：`00-baseline/fineract-codebase.md` §3（外部事件）、`api-surface.md`。

---

## 1. 事实基线（已核实）

- Fineract 有 external events 框架 + `fineract-avro-schemas`（**99 个 schema**）
- Kafka 生产端配置存在：topic `external-events`（`application.properties:183`）、bootstrap `localhost:9092`、分区 10
- 默认消息处理器走 Spring Events（进程内），Kafka 是可切换项
- 仓库自带 `docker-compose-postgresql-kafka.yml` 编排
- 内部 API：`GET/DELETE /v1/internal/externalevents`（事件留存管理）、`Purge External Events` 作业（默认 inactive）

## 2. 目标拓扑（Phase 4）

```
Fineract ──(Avro 事件)──▶ Kafka: external-events ──▶ 各订阅方
                              │
                              ├─ 风控服务（实时规则）
                              ├─ 通知服务（短信/推送）
                              ├─ 数仓摄取（CDC 式入仓）
                              ├─ 监管报送（EAST/1104 数据源）
                              └─ AOS/智能层（行为流）
```

## 3. 设计原则

1. **核心只广播，不编排**：外围业务逻辑（审批流、多步流程）在订阅方完成，Fineract 保持事件源角色
2. **Avro 契约优先**：用上游 99 个 schema 起步；ABNK 自有事件放 `custom/abnk/integration/events`，schema 走同一注册表
3. **消费幂等**：所有订阅方按事件 ID 幂等——上游事件可能重放
4. **不反向写**：订阅方要改核心数据时回调 Fineract API，**永不直连业务库**（`overview.md` 依赖方向）

## 4. 与 remote-job-message-handler 的区分（易混）

| 机制 | 用途 | topic |
|---|---|---|
| **external events**（本方案主体） | 业务事件广播给外围 | `external-events` |
| remote job message handler | Fineract 集群内部作业分发（MSK/K8s 场景） | `job-topic` |

单机调试两者都不需要；Phase 4 只启用前者。

## 5. 落地步骤（Phase 4 骨架）

1. compose 加 Kafka（对齐仓库自带编排）→ 登记 `config.json` processes
2. 开启 Fineract Kafka 生产端（环境变量）→ E2E 验证事件落 topic
3. 第一个订阅方 = 通知服务（最小闭环）
4. 事件留存/清理策略（`Purge External Events` 作业激活 + 留存窗口）

## 6. 待决策（Phase 4 开项时）

- [ ] Schema Registry 选型与治理
- [ ] 事件留存时长（合规 vs 成本）
- [ ] 数仓摄取是走事件流还是库级 CDC（各订阅方诉求不同）
