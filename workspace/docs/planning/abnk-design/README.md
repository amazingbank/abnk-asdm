# Amazing Bank 设计文档（abnk-design）

> 本目录是 Amazing Bank IT 系统的设计文档区，**规划内容由版本线与阶段推进逐步填充**。
> 目录结构参照 ASDM 规划设计文档的六大板块组织方式。

## 目录结构

```
abnk-design/
├── README.md                # 本文件（索引）
├── 01-product/              # 产品：定位 / 用户 / 场景 / 价值
├── 02-architecture/         # 架构：总览 / 集成 / 存储 / 可扩展性
├── 03-data-model/           # 数据模型：核心领域概念 / 账务模型 / 租户模型
├── 04-operations/           # 运行治理：可观测性 / 安全合规 / 质量
├── 05-domains/              # 领域：银行业务域扩展（存款/贷款/支付/风控等）
└── 06-evolution/            # 演进：路线图 / 发版计划
```

## 当前状态

| 板块 | 状态 |
|---|---|
| 01-product | 待填充 |
| 02-architecture | 待填充（阶段一事实已录入 `toolsets/abnk-harness-toolset/config.json`） |
| 03-data-model | 待填充（Fineract 现有模型可直接作为基线） |
| 04-operations | 待填充 |
| 05-domains | 待填充 |
| 06-evolution | 待填充 |

## 已知基线事实

阶段一技术基线（已核实，详见 `.asdm/toolsets/abnk-harness-toolset/config.json`）：

- 核心引擎 = Apache Fineract（fork `amazingbank/fineract`，`develop` 分支）
- JDK 25 / Gradle 9.7.1 / PostgreSQL 18.3 / Liquibase
- 多租户架构（`fineract_tenants` 租户存储库 + 各租户业务库物理隔离）
- 端口 8443 强制 HTTPS，Basic Auth（后续可切 OAuth2/2FA）
- 远程作业消息处理器默认走 Spring Events（可切 ActiveMQ / Kafka）
