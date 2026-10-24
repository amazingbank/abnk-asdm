# 环境基线（Phase 0）

> **性质**：实测事实记录，非设计文档。全部内容来自 2026-10-24 的实际搭建与验证。
> **用途**：后续所有架构/领域文档的环境前提；新人上手的第一篇必读。
> **配套**：机器可读版见 `toolsets/abnk-harness-toolset/config.json`（v0.1.1）。

---

## 1. 组件清单

| 组件 | 版本/形态 | 端口 | 角色 |
|---|---|---|---|
| JDK | 25.0.5+8-tem（Temurin） | — | 编译/运行（toolchain 硬要求，`build.gradle:418`） |
| PostgreSQL | 18.3 docker 容器 `abnk-pg` | 5432 | 全系统唯一数据库宿主 |
| Fineract | develop 分支，Gradle devRun | 8443 (HTTPS) | 核心账务引擎 |
| JDWP 调试口 | `--debug-jvm` 启动时 | 5005 | IDE 远程断点调试 |
| Gradle | 9.7.1 wrapper | — | 构建系统 |

验证状态（2026-10-24）：`abnk-pg` healthy；Fineract `/actuator/health` = `{"status":"UP"}`；业务 API HTTP 200。

## 2. JDK 25

- **为什么是 25**：`fineract/build.gradle:418` toolchain 硬性要求，17/21 无法编译。
- **安装坑**：`sdk install java 25-tem` 在本机因 Adoptium 下载地址 307→302 双重跳转**必失败**。改用 `curl -L` 直取 tarball + sdkman 本地安装（`sdk install java 25-tem /path/to/dir` 或 `sdkman` 离线安装）。
- **目录级隔离**：`fineract/.sdkmanrc` 声明 `java=25.0.5+8-tem`，Gradle 启动时自动启用对应 SDK，**不影响全局**。全局默认保持 21.0.11，其他 Java 项目（17/21）零影响。
- 运行期需 `JAVA_HOME` 指向 25（devRun 命令行显式传）。

## 3. PostgreSQL

- **容器编排**：`abnk-system/deploy/docker-compose.yml`，项目名显式声明 `name: abnk-system`。
- **账号 `root`/`postgres`**——刻意与 Fineract 代码默认值**三方对齐**：
  1. `application.properties` 的 hikari 默认（`FINERACT_HIKARI_USERNAME` 默认 root / `FINERACT_HIKARI_PASSWORD` 默认 postgres）
  2. `fineract-provider/build.gradle:206-207` 的 `createPGDB` 任务默认凭据
  3. 容器环境变量

  结果是**零环境变量覆盖**即可跑通。仓库自带的 `config/docker/compose/postgresql.yml` 用随机密码，本地调试不用它。
- **两库分库**：`fineract_tenants`（租户存储库，6 表）+ `fineract_default`（默认业务租户库，280 表）。
- **日志**：容器开启 `logging_collector`，服务端日志直写宿主 `logs/postgres.log`（与 `fineract.log` 并列），按天轮转 / 50MB 切分。
- **硬约束**：
  1. 数据卷必须挂 `/var/lib/postgresql`（父目录）。PG 18+ 数据落在版本化子目录 `/var/lib/postgresql/18/data`，挂成 `/var/lib/postgresql/data` 直接启动失败。
  2. compose 必须显式 `name: abnk-system`。否则项目名取目录名 `deploy`，与其他项目的 deploy 目录撞名，`down` / `--remove-orphans` 会误停他人容器。
  3. 卷名 `abnk-pg-data` 固定（`volumes.abnk-pg-data.name`），避免 compose 加项目前缀。

## 4. Fineract 运行时

- **启动**：`cd fineract && JAVA_HOME=$HOME/.sdkman/candidates/java/25.0.5+8-tem ./gradlew devRun`（nohup 后台时输出重定向到 `logs/fineract.log`）。
- **就绪判据**：日志出现 `APACHE FINERACT IS READY`。正常停机日志 `APACHE FINERACT IS SHUTTING DOWN GRACEFULLY`。
- **HTTPS**：8443 强制 TLS，自签证书（`keystore.jks`，密码 openmf），curl 必须 `-k`。
- **鉴权**：Basic `mifos:password` + 租户头 `Fineract-Platform-TenantId: default`（缺失租户头返回 4xx）。actuator 端点免鉴权。
- **进程拓扑**：devRun 会 fork 独立 JVM 跑 Spring Boot。nohup 记录的 PID 是 **Gradle 客户端**，杀它不杀应用——**停机一律按端口**：`lsof -ti:8443 -sTCP:LISTEN | xargs kill`。
- **devRun vs bootRun**：devRun 禁用 checkstyle/spotless/spotbugs/javadoc/modernizer/testClasses（`fineract-provider/build.gradle:449`），把构建压到代码改动级别。**代价是提交前必须另跑质量门禁**。
- **调试**：`devRun --debug-jvm` 在 5005 开 JDWP（suspend 默认 n），VS Code 用 attach 配置连接。

## 5. 数据库迁移

- Liquibase 随应用启动自动执行（`spring.liquibase.enabled` 默认 true）。
- 实测账本：`fineract_default` 库 **2068 EXECUTED / 0 FAILED**，280 张表。
- **纪律**：首次启动建表期间**绝不能 Ctrl-C**——会在 `databasechangelog` 留 FAILED 行，后续启动直接失败。

## 6. 实测耗时（M-series 12C/64G）

| 操作 | 耗时 |
|---|---|
| devRun 到 READY（依赖已缓存） | ~4.5 min（其中 Spring Boot 启动 82.6s） |
| 全量 clean 重建 + 启动 | 3.6 min |
| 停机（按端口 kill） | <1s |

## 7. 坑总账（详见 `04-operations/engineering-conventions.md`）

| 坑 | 症状 | 处置 |
|---|---|---|
| 构建产物损坏 | 运行中实例突然对未用过的端点 500 `ClassNotFoundException` | `--stop` + `clean` + 清 build-cache + 重建 |
| Liquibase 中断 | 下次启动报 changelog FAILED | 禁止中途 Ctrl-C |
| Gradle fork | 杀 PID 杀不掉应用 | 一律按端口 kill |
| JDK 25 安装 | sdk install 必失败 | curl -L 直取 + 本地安装 |
| PG 卷挂载 | 容器启动失败 | 挂父目录 `/var/lib/postgresql` |
| compose 撞名 | 误停他人容器 | 显式 `name: abnk-system` |

---

*事实核对方法：全部条目在 2026-10-24 会话中经实际执行验证；引用的行号来自当日的 develop 分支快照，上游演进后可能漂移。*
