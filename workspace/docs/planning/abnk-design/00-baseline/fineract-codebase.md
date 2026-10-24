# Fineract 代码库测绘

> **性质**：实测事实记录。数据来自 2026-10-24 对 `amazingbank/fineract`（develop 分支）的静态探查。
> **用途**：评估定制工作量、判断"改核心 vs 扩展"的依据（ADR-001/002 的事实基础）。

---

## 1. 规模

| 指标 | 数值 |
|---|---|
| Java 文件 | **7100** |
| Gradle 模块 | 35（`settings.gradle` 36 个 include，含 custom 动态扫描） |
| Liquibase changelog | 473 个 XML |
| Avro schema | 99 个 `.avsc` |
| E2E feature 文件 | 200 个 Cucumber `.feature` |

**定性结论**：十余年积累的成熟核心银行系统。重写不可行，也不必要。

## 2. 模块清单（settings.gradle 实测）

| 分组 | 模块 |
|---|---|
| **核心** | `fineract-core`（1053 个类）、`fineract-security`、`fineract-validation` |
| **命令架构** | `fineract-command` + 四种实现：`-jdbc` / `-audit` / `-async` / `-disruptor`（+ `-test`） |
| **账务** | `fineract-accounting`、`fineract-charge`、`fineract-tax`、`fineract-rates` |
| **贷款** | `fineract-loan`、`fineract-loan-origination`、`fineract-progressive-loan`、`fineract-progressive-loan-embeddable-schedule-generator`、`fineract-working-capital-loan` |
| **存款/投资** | `fineract-savings`、`fineract-investor`（资产证券化） |
| **日终** | `fineract-cob`（分区并行的 close-of-business） |
| **渠道与文档** | `fineract-branch`、`fineract-document`、`fineract-report` |
| **交付物** | `fineract-provider`（Spring Boot 主应用）、`fineract-war`、`fineract-doc` |
| **客户端 SDK** | `fineract-client`、`fineract-client-feign`（均由 resolve 任务从 OpenAPI spec 自动生成） |
| **事件** | `fineract-avro-schemas` |
| **测试** | `integration-tests`、`fineract-e2e-tests-core`、`fineract-e2e-tests-runner`、`twofactor-tests`、`oauth2-tests` |
| **定制扩展点** | `custom/`（动态扫描，见 `extension-points.md`） |

## 3. 关键子系统（定制决策相关）

### 命令架构（CQRS 风格）
所有写操作走 Command 通道，有四种可切换的实现（jdbc/audit/async/disruptor）——`application.properties` 中有对应 retry 配置（如 `resilience4j.retry.instances.executeCommand`）。**含义：写路径是异步可重试的，排障时要看 command 审计表，不能只看业务表。**

### 贷款引擎（最复杂、最不可重写的部分）
- `progressive-loan`：渐进式贷款，含**独立的可嵌入还款计划生成器模块**（多种 schedule 策略）
- `working-capital-loan`：经营贷
- 7 种内置贷款交易处理器（官方文档 `loan-transaction-processor.adoc`）

### COB（日终批处理）
`fineract-cob` 分区并行执行；配套业务步骤（Business Step）机制可扩展（见 `extension-points.md`）。作业通过 Quartz 调度，41 个已注册作业（实测 `/v1/jobs`）。

### 多租户
`fineract_tenants`（租户存储库）+ 每租户独立业务库（物理分库）。租户路由按请求头 `Fineract-Platform-TenantId`。天然支持多法人 / BaaS（ADR-004 已决策启用）。

### 外部事件
`fineract-avro-schemas`（99 个 schema）+ external events 框架，可切 Spring Events（默认）/ Kafka / ActiveMQ。Kafka topic `external-events`（`application.properties:183`）。

## 4. 测试资产

- **200 个 E2E feature**（Cucumber）——已覆盖完整业务链路，含 COB 触发写法（`InlineCOBStepDef.java:60`）。**这是 ABNK 免费的回归基线**，Phase 1 直接复用。
- `integration-tests` 模块含 `InlineLoanCOBTest` 等集成测试。

## 5. 可观测性栈（仓库自带，勿另造）

`config/docker/compose/observability.yml`：

| 组件 | 版本 |
|---|---|
| Loki | 2.9.2 |
| Prometheus | v2.47.2 |
| Grafana OSS | 10.2.0 |
| Tempo | 2.2.4 |

另有现成编排：`docker-compose-development.yml`、`docker-compose-postgresql-kafka.yml`、`docker-compose-custom.yml` 等 18 个 compose 文件在仓库根目录。

---

*核对方法：模块清单来自 settings.gradle 逐行读取；规模统计来自文件系统计数；子系统结论来自模块命名 + 官方文档 + application.properties。*
