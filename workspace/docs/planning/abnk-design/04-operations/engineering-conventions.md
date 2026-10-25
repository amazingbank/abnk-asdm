# 工程规范与踩坑总账

> **性质**：全部来自实际踩坑（2026-10-24/25），每条都有现场证据。新人上手必读第一篇。
> **定位**：`00-baseline/environment.md` §7 的完整展开 + 团队工程纪律。

---

## 1. 坑总账（按严重度排序）

### 1.1 构建产物损坏：devRun 长驻 + IDE Gradle 扩展（最重）

- **现象**：运行中的 Fineract 突然对**未用过的端点**报 500 `ClassNotFoundException`（实测案例：`IdTypeResolver`——源码明明 `implements Serializable`）。重启应用不愈。
- **根因**：VS Code Gradle 扩展（`vscjava.vscode-gradle`）常驻 `GradleServer` 进程，其后台构建被中断时写出**截断的 fineract-core jar**（`zip END header not found`）。且 `org.gradle.caching=true` 使损坏产物进构建缓存，之后每次构建都被还原，删 `build/` 无效。
- **诱因链**：损坏 jar 被运行中的应用按需加载 → 新触达的类加载失败 → Jersey 500。已加载过的类不受影响，所以问题总是"突然"出现。
- **处置**（完整重建，实测 3.6 min）：

```bash
cd fineract
./gradlew --stop                                # 停守护进程清内存态
./gradlew clean
rm -rf ~/.gradle/caches/build-cache-1           # 清被污染的缓存（安全）
# 按 environment.md §4 正常 devRun
```

- **预防**：devRun 长驻期间不让 IDE 的 Gradle 扩展在后台跑构建（关 auto-refresh / 长会话前停 devRun）。
- **诊断技巧**：`NoClassDefFoundError` 但源码/编译产物都存在 → 先怀疑构建损坏，别去改代码。

### 1.2 Liquibase 中断（破坏性，不可自愈）

- **现象**：首次启动建表期间 Ctrl-C → `databasechangelog` 留 FAILED 行 → 后续启动直接失败。
- **纪律**：首次启动（建表期间）**绝不中断**；看到 `APACHE FINERACT IS READY` 前保持耐心（实测 ~4.5 min）。

### 1.3 进程拓扑：Gradle fork（日常高频）

- nohup 记录的 PID 是 **Gradle 客户端**，杀它不杀应用。
- **一律按端口**：`lsof -ti:8443 -sTCP:LISTEN | xargs kill`
- 正常停机日志：`APACHE FINERACT IS SHUTTING DOWN GRACEFULLY`；Gradle 报 `Build cancelled while executing task` 属正常退出，不是崩溃。

### 1.4 JDK 25 安装

- `sdk install java 25-tem` 在本机因 Adoptium 307→302 双重跳转**必失败**。
- 解法：`curl -L` 直取 tarball + sdkman 本地安装；目录级隔离靠 `fineract/.sdkmanrc`，全局默认 21.0.11 不动，其他 Java 项目零影响。

### 1.5 PostgreSQL 18 卷挂载

- 数据卷必须挂 **`/var/lib/postgresql`（父目录）**。PG 18+ 数据在版本化子目录 `…/18/data`，挂成 `/var/lib/postgresql/data` 直接启动失败。
- 容器日志直写宿主 `logs/postgres.log`（logging_collector，按天/50MB 轮转）。

### 1.6 compose 项目撞名（伤害他人）

- 必须显式 `name: abnk-system`。否则项目名取目录名 `deploy`，与其他项目的 deploy 目录撞名，`docker compose down` / `--remove-orphans` 会**误停别人的容器**。

### 1.7 Java 无 HMR

- 改代码必重启（kill 8443 + devRun）。调试器 session 会断开，断点需重挂。
- 日志增强/插桩类改动**一次注入完所有候选点**再重启，别反复。

### 1.8 Docker 虚拟磁盘写满 → PG 崩溃循环（2026-10-25 实际发生）

- **现象**：容器 `running (unhealthy)`，`pg_isready` 拒绝连接；`logs/postgres.log` 反复出现 `PANIC: could not write to file "pg_logical/replorigin_checkpoint.tmp": No space left on device` + `all server processes terminated; reinitializing`（恢复→checkpoint→PANIC 死循环）。
- **根因**：Docker Desktop 虚拟盘满（本机当时：镜像 16.9GB + 卷 37.8GB + 构建缓存）。PG 的 WAL 回放本身完好，只是 checkpoint 写不出去。
- **处置**（数据完整恢复）：`docker builder prune -f` + `docker image prune -f` 释放 ~1GB 即够 → `docker compose restart abnk-pg` → 280 表与 Liquibase 账本完好。
- **预防**：`docker system df` 看 RECLAIMABLE 列纳入日常巡检；卷清理需确认归属后进行（未使用卷里含 aos-bench/deploy_mysql_data 等**他人项目数据**，不可盲 prune）。

## 2. 提交纪律

| 时机 | 动作 |
|---|---|
| devRun 期间 | 它禁用了 checkstyle/spotless/spotbugs/javadoc/modernizer/testClasses（`fineract-provider/build.gradle:449`） |
| **提交前** | `./gradlew spotlessApply checkstyleMain` 必跑；改动核心相邻区另跑 spotbugsMain |
| custom 模块 | 官方对 `:custom:*` 关闭了 Checkstyle/SpotBugs（`build.gradle:603,827`）→ **自建 CI 门禁补位**（见下） |

## 3. CI 门禁（自建，因官方对 custom 关闭质量检查）

最低集（Phase 2 建立）：编译 → spotless → checkstyle（自配规则集）→ 单测 → 12 步冒烟脚本（`06-evolution/phase-1-validation.md`）→ E2E 子集。

## 4. 日常操作速查

| 操作 | 命令 |
|---|---|
| 起库 | `cd abnk-system/deploy && docker compose up -d abnk-pg` |
| 停库 | `docker compose stop abnk-pg` |
| 起应用 | `cd fineract && JAVA_HOME=~/.sdkman/candidates/java/25.0.5+8-tem ./gradlew devRun` |
| 停应用 | `lsof -ti:8443 -sTCP:LISTEN \| xargs kill` |
| 健康检查 | `curl -k https://localhost:8443/fineract-provider/actuator/health` |
| 业务 API | 加租户头 + Basic（用法见 config.json `auth` 节） |
| OpenAPI | `curl -k https://localhost:8443/fineract-provider/fineract.json`（**不是** /api-docs） |
| psql | `docker exec -it abnk-pg psql -U root -d fineract_default` |
| 触发日终 | `POST /api/v1/jobs/LOAN_COB/inline`（三套命名坑见 `00-baseline/api-surface.md` §3） |

## 5. 排障决策树

```
端点 500？
├─ ClassNotFound 且源码存在 → 构建损坏（§1.1 处置）
├─ 首次触达才 500 → 同上（按需加载特性）
├─ 403 business.date → PUT /v1/configurations/44 启用
├─ 400 locale → 请求体补 locale
├─ Inline Job not found → 作业名用错（要用 LOAN_COB）
└─ 其他 → 查 logs/fineract.log（搜 ERROR + Caused by）
```

---

*新坑入账规则：现象 + 根因 + 处置 + 预防四要素齐备才可写入；来源标注日期。*
