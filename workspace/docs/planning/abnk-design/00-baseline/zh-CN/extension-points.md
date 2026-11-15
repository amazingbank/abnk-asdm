# 官方扩展点体系（custom 模块机制）

> **性质**：实测事实记录。来自官方文档 + `custom/acme` 参考实现的源码解析（2026-10-24/25）。
> **用途**：ADR-002（定制策略）与 `02-architecture/customization-strategy.md` 的事实基础。

---

## 1. 机制：动态模块扫描

```groovy
12:14:fineract/settings.gradle
// NOTE: dynamically load custom modules with pattern "custom -> company -> category -> module"
file("${rootDir}/custom").eachDir { companyDir -> ...
    include ":custom:${companyDir.name}:${categoryDir.name}:${moduleDir.name}"
```

约定路径 `custom/<company>/<category>/<module>/`——目录即模块，放入即被 Gradle 识别，**无需改 settings.gradle**。

## 2. 官方参考实现：`custom/acme`（5 个模块，3 个类别）

```
custom/acme/
├── event/
│   ├── externalevent/   # 自定义外部事件源（含 custom-changelog）
│   └── starter/         # Spring Boot 自动装配
├── loan/
│   ├── cob/             # 自定义 COB 业务步骤（含 custom-changelog）
│   ├── job/             # 自定义批处理作业（含 custom-changelog + 测试）
│   ├── processor/       # 自定义还款计划交易处理器
│   └── starter/
└── note/
    ├── service/         # 替换内置 Note 服务（读/写平台服务）
    └── starter/
```

**装配模式（可直接复制）**：

- 每个 category 一个 `starter` 模块，通过 Spring Boot 标准机制织入：

```
21:21:fineract/custom/acme/note/starter/src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
com.acme.fineract.portfolio.note.starter.AcmeNoteAutoConfiguration
```

- `starter` 的 `dependencies.gradle` 声明对同 category 实现模块的依赖 + `spring-boot-starter`
- 命名约定：group `com.acme.fineract`、artifact `acme-fineract-note-starter`（ABNK 对应 `com.abnk.fineract` / `abnk-fineract-*`）

## 3. 自定义数据库迁移（与核心 changelog 物理隔离）

约定（官方 `database-migration.adoc`）：

1. 在自己模块的 `src/main/resources` 建 `db/custom-changelog/` 目录
2. 放 `0001_<company>_<module>.xml`
3. 可建 `parts/` 子目录放分片

**这是关键解耦机制**：定制表结构走独立 changelog 流，Liquibase 账本互不干扰，上游升级不冲突。（对比：直接改核心表 = 与 473 个官方 changelog 撞车。）

## 4. 官方文档索引（10 篇，`fineract-doc/src/docs/en/chapters/custom/`）

| 文档 | 扩展点 |
|---|---|
| `intro.adoc` | 总述：兼容未来 clean room 模块方案 |
| `index.adoc` | 模块体系总览（**含 PoC 声明**） |
| `service.adoc` / `service-note.adoc` | **替换内置服务** |
| `loan-transaction-processor.adoc` | **自定义贷款交易处理器**（内置 7 种） |
| `business-step.adoc` | **自定义 COB 业务步骤** |
| `custom-batch-job.adoc` | **自定义批处理作业** |
| `database-migration.adoc` | **自定义数据库迁移** |
| `deployment.adoc` | 部署：JAR 丢 `libs/` 或 `custom:docker:jibDockerBuild` |

另有 `outlook.adoc`（官方对模块化的方向声明）。

## 5. ⚠️ 成熟度：官方声明为 PoC

`index.adoc` 原文：

> **NOTE: Currently, modules are a proof of concept feature in Fineract.**

`outlook.adoc`：*If this proof of concept is accepted we could prepare more of Fineract's internal services to be replaceable... It's an important goal to separate customized code from Fineract's internals.*

**解读**：方向是官方认定的长期目标（分离定制与内核），但当前成熟度是实验级。风险与缓解：

| 风险 | 缓解（详见 ADR-002） |
|---|---|
| API 不稳定，升级要改 | 季度 rebase 纪律 + 定制面窄（只做四类外围事） |
| 质量门禁对 acme 豁免 | 根构建脚本**仅对 `:custom:acme:` 禁用了 Checkstyle 和 SpotBugs**（`build.gradle:603,827`，条件 `project.path.startsWith(':custom:acme:')`）——**`custom/abnk` 不在豁免内**，且所有 custom 模块都被加入 `fineractJavaProjects`（`build.gradle:379`），官方门禁全量生效（利好）。自建 CI 的重点 = 一键编排（编译/单测/质量/冒烟/E2E 串行流水线），而非补位被豁免的检查（2026-10-25 源码核验修正） |
| 部署路径与 devRun 不一致 | 见下节 |

## 6. devRun 下的接入方式（与官方部署路径的差异）

官方部署路径（`deployment.adoc`）面向 Spring Boot JAR：JAR 丢进 `libs/` 目录（1.5.0+ 动态加载），或构建 `fineract-custom` Docker 镜像。

**devRun（我们的调试方式）不走这条路**：`fineract-provider/dependencies.gradle` 中没有任何 custom 占位。实测确认接入方式 = 在该文件追加一行：

```groovy
implementation(project(':custom:abnk:<category>:starter'))
```

这是一处 fork 本地改动，边界清晰、上游合并冲突风险极低。

## 7. 对 ABNK 的直接推论

1. `custom/abnk/` 的类别规划应对齐 acme 的演示类别：`product` / `localization` / `integration` / `report`（见 `02-architecture/customization-strategy.md`）
2. 每个 category 配一个 `starter`——这是 acme 反复演示的结构
3. 定制表一律走 `custom-changelog`，**永不**修改核心表
4. 替换内置服务（`service.adoc` 路线）慎用——它是 PoC 中最激进的能力，优先用"新增"而非"替换"

---

*核对方法：目录结构来自文件系统枚举；扫描逻辑、AutoConfiguration、质量门禁关闭、PoC 声明均来自源码/文档原文（行号已在文中标注）。*
