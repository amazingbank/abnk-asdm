# ASDM Action: ABNK Super Debug

## Metadata

```json
{
  "guid": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
  "name": "abnk-debugger",
  "displayName": "ABNK Debugger",
  "description": "Automated debugging for the Amazing Bank (ABNK) IT stack. 阶段一 = PostgreSQL 18.3 docker（:5432，fineract_tenants + fineract_default）+ Fineract ServerApplication（Gradle devRun，:8443 强制 HTTPS 自签证书，JDWP :5005），强制 JDK 25 toolchain。鉴权 = Basic Auth（mifos:password）+ 多租户头 Fineract-Platform-TenantId: default；DB 迁移 = Liquibase 随启动自动执行。设计为 Amazing Bank 整个 IT 系统（后续前端/OAuth2/消息中间件/自有业务服务）的通用调试入口——新系统接入只需在 config.json 的 processes 追加一条，本文档不随之改动。",
  "toolset": {
    "guid": "b7a2c9d1-4e3f-4a58-9c6b-1d2e3f4a5b6c",
    "id": "abnk-harness-toolset",
    "name": "ABNK Harness Toolset",
    "version": "0.1.0"
  },
  "scenario": "自动化调试"
}
```

## Overview

This action performs **self-directed automated debugging** of the Amazing Bank IT stack. 当前阶段一栈为双进程：

- **postgres**（必起）：`abnk-pg` 容器，PostgreSQL 18.3，宿主 `:5432`。账号 `root` / `postgres`——**刻意与 Fineract 代码默认值三方对齐**（application.properties 的 hikari 默认值、gradle `createPGDB` 任务的 `pgUser/pgPassword`），从而零环境变量覆盖即可跑通。承载 `fineract_tenants`（租户存储库）+ `fineract_default`（默认业务租户库）。
- **fineract**（核心）：`org.apache.fineract.ServerApplication`（fineract-provider 模块，Spring Boot + 内嵌 Tomcat），`:8443` 默认强制 HTTPS（自签 `keystore.jks`，密码 `openmf`），JDWP 调试口 `:5005`。启动即自动执行 Liquibase 迁移建表。

Key differences from a typical web-app debugger:

- **JDK 25 是硬门槛**——`build.gradle:418` 的 Gradle toolchain 会拒绝 17/21，缺 JDK 25 则**任何构建都起不来**（Step 0 必须完成）
- **Java 栈无 HMR**——改代码必须重启进程（Gradle 无热替换），每次验证周期 = 重启 + 等待就绪（首次 15–30 min，后续增量）
- **Gradle 会 fork JVM**——`nohup ./gradlew devRun` 的 PID 是 Gradle 客户端，**杀它不杀应用**；停机一律按端口 kill
- **无前端进程**——阶段一 Fineract 是纯 API 服务，验证走 `curl`，不需要 `preview_url` / `playwright-cli`
- **强制 HTTPS 自签**——所有 curl 必须 `-k`
- **多租户头必需**——`Fineract-Platform-TenantId: default` 缺失即 4xx
- **Liquibase 首次启动建表**——中断启动会破坏 changelog 账本；首次启动必须等 `APACHE FINERACT IS READY`，绝不中途 Ctrl-C
- **config.json 驱动扩展**——Amazing Bank 后续接入的系统登记到 `config.json → environments.local.processes`，本 action 自动按数组驱动，无需改本文档

## Purpose

- Set up reproducible debugging environment（docker postgres + nohup + pid files + log files）
- Read and filter logs across the stack（postgres + fineract）to identify errors and anomalies
- Inject temporary debug logs to trace data flow across layers
- Autonomously form hypotheses, implement fixes, rebuild, restart, and verify
- Minimize manual intervention — the AI drives the debugging loop

## Input

- Description of the issue（what's not working, what's expected）
- (Optional) Relevant file paths or class names

## Output

- Root cause identification with log evidence
- Fix implementation（committed）
- Verification result

---

## Debugging Procedure

### Step 0: 环境前置（一次性——阻塞项，必须先完成）

首次在这台机器上调试前，逐项检查。**任一缺失则后续全部步骤无法进行**：

```bash
# 1) JDK 25 —— 硬门槛（build.gradle:418 JavaLanguageVersion.of(25)）
java -version 2>&1 | head -1          # 必须是 25.x
sdk list java | grep -E "25\."         # 查看可安装版本
# 缺失则安装（勿设为 default，避免污染其他 17/21 项目）：
# sdk install java 25-zulu
# 安装后在 .vscode/settings.json 按项目指定 java.jdt.ls.java.home / java.configuration.runtimes

# 2) Docker（postgres 容器宿主）
docker --version                       # 本机 Docker Desktop 29.7.2 + Compose v5.4.0 已可用
docker info --format '{{.ServerVersion}}'

# 3) Gradle wrapper（仓库自带 9.7.1，勿用系统 gradle）
cat fineract/gradle/wrapper/gradle-wrapper.properties | grep distributionUrl
# 预期：gradle-9.7.1-bin.zip

# 4) 工作区与代码状态
cd fineract && git --no-pager status --short   # 应保持干净
git --no-pager branch --show-current          # develop
```

> **do NOT skip this step**: JDK 25 缺失时 Gradle 会尝试自动下载 toolchain，网速不佳会卡死或直接失败；此时表现是各种莫名其妙的构建错误，而非清晰的 "need JDK 25"。

### Step 1: Load Environment Config

**Always start by reading `config.json`** to avoid re-exploring the application architecture:

```bash
cat .asdm/toolsets/abnk-harness-toolset/config.json
```

Extract from `environments.local`:
- **Processes**: `processes[]` — 当前 2 条：`postgres`（docker 容器，`:5432`）、`fineract`（dir `fineract`，`:8443`，debugPort `:5005`）。**按数组顺序启动**（依赖顺序），未来新增系统时追加即可
- **Auth**: `auth.authRequired` is `true` — Basic Auth + 租户头：
  ```bash
  ABNK_TENANT="Fineract-Platform-TenantId: default"
  ABNK_AUTH="Authorization: Basic bWlmb3M6cGFzc3dvcmQ="
  ```
  所有业务 API 调用带 `-H "$ABNK_TENANT" -H "$ABNK_AUTH"`；`/actuator/health` 免鉴权
- **API endpoints**: `apiEndpoints` — 健康检查与复现用 URL
- **Database**: `database` — 连接信息、两个库的职责、createCommand、migrationVerify
- **Browser**: `browser.tool` is `curl` — **阶段一不需要 preview_url / playwright-cli**

### Step 2: Set Up Debugging Environment

Follow the spec in `.asdm/toolsets/abnk-harness-toolset/specs/process-management-spec.md`

1. **Create log directory**（workspace root）:
   ```bash
   mkdir -p logs
   ```

2. **Kill existing processes** on stack ports:
   ```bash
   # Fineract on :8443（用 -sTCP:LISTEN 避免误杀出站连接）
   lsof -ti:8443 -sTCP:LISTEN 2>/dev/null | xargs kill 2>/dev/null
   # JDWP 调试口 :5005
   lsof -ti:5005 -sTCP:LISTEN 2>/dev/null | xargs kill 2>/dev/null
   # postgres 容器：默认保留运行（数据卷跨会话持久），不要 down
   # 仅当需要全新数据时（破坏性，必须先问用户）：docker rm -f abnk-pg && docker volume rm abnk-pg-data
   ```

3. **Start the postgres container**（Fineract 的存储依赖，必须先起）:
   ```bash
   docker start abnk-pg 2>/dev/null || \
     docker run -d --name abnk-pg -p 5432:5432 \
       -e POSTGRES_USER=root -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=root \
       -v abnk-pg-data:/var/lib/postgresql/data postgres:18.3

   # 验证（pg_isready，不要只用 docker ps）
   until docker exec abnk-pg pg_isready -U root -q; do sleep 1; done
   # 期望：accepting connections
   ```

4. **Create the two databases**（仅首次需要——容器数据卷首次为空时；已存在则跳过，createPGDB 会报 "already exists"）:
   ```bash
   cd fineract
   ./gradlew createPGDB -PdbName=fineract_tenants
   ./gradlew createPGDB -PdbName=fineract_default

   # 验证
   docker exec abnk-pg psql -U root -lqt | cut -d'|' -f1 | grep -E "fineract_(tenants|default)"
   # 期望：两行（fineract_tenants、fineract_default）
   cd ..
   ```
   > 这两个 task 不支持 configuration-cache（构建脚本已显式标记 `notCompatibleWithConfigurationCache`），可能提示配置缓存被禁用——**属预期行为，不是错误**。

5. **Start Fineract with nohup**（默认非 debug 模式）:
   ```bash
   cd fineract
   JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
     nohup ./gradlew devRun > ../logs/fineract.log 2>&1 &
   echo $! >> ../logs/debug-process.pid
   cd ..
   ```
   **需要断点调试时**（VS Code attach :5005），改用 `--debug-jvm`:
   ```bash
   cd fineract
   JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
     nohup ./gradlew devRun --debug-jvm > ../logs/fineract.log 2>&1 &
   echo $! >> ../logs/debug-process.pid
   cd ..
   ```
   > ⚠️ 用 `devRun` 而非 `bootRun`：devRun 会禁用 checkstyle / spotless / spotbugs / javadoc / modernizer / testClasses（`fineract-provider/build.gradle:449`），把分钟级构建压到代码改动级别。
   > ⚠️ **首次启动 15–30 min**（7100+ Java 文件 + OpenAPI/Avro 代码生成 + Liquibase 建全部表）。**绝不中途 Ctrl-C**——会破坏 Liquibase changelog 账本，导致后续启动失败。

6. **Wait for Fineract to be ready**（轮询 readyPattern，不要只 sleep）:
   ```bash
   # 轮询就绪标志（首次最长等 30 min）
   for i in $(seq 1 1800); do
     grep -q "APACHE FINERACT IS READY" logs/fineract.log && break
     sleep 1
   done
   grep "APACHE FINERACT IS READY" logs/fineract.log

   # HTTP 健康检查（必须 -k：自签证书）
   curl -sk https://localhost:8443/fineract-provider/actuator/health
   # 期望：{"status":"UP","groups":["liveness","readiness"]}
   ```

7. **Verify database migration**（首次启动后确认表已建）:
   ```bash
   docker exec abnk-pg psql -U root -d fineract_default -tAc \
     "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"
   # 期望：> 300（Liquibase 建的业务表 + databasechangelog 账本表）
   docker exec abnk-pg psql -U root -d fineract_default -tAc \
     "SELECT id, filename FROM databasechangelog ORDER BY orderexecuted DESC LIMIT 3"
   ```

8. **External dependencies** — JDK 25（硬门槛）+ Docker（postgres）；无需 Redis / MQ（Fineract 的 remote job message handler 默认走 spring events，`FINERACT_REMOTE_JOB_MESSAGE_HANDLER_SPRING_EVENTS_ENABLED` 默认 true）。

### Step 3: Attach Debugger（仅当需要断点调试时）

阶段一 Fineart 是纯 API 服务，**不需要 preview_url**。需要断点时用 VS Code 远程 attach：

1. 确认启动时用了 `./gradlew devRun --debug-jvm`（Step 2 第 5 步）
2. 确认 JDWP 端口在监听：
   ```bash
   lsof -i:5005 -sTCP:LISTEN
   ```
3. VS Code 中打断点 → 打开 `.vscode/launch.json` 的 **Attach Fineract (:5005)** 配置 → F5
4. 断点候选位置（改你关心的路径）：
   - `fineract-provider/src/main/java/org/apache/fineract/ServerApplication.java` — 启动入口
   - `fineract-provider/src/main/java/.../api/**ApiResource.java` — REST 层入口
   - `fineract-*/src/main/java/.../service/**ServiceImpl.java` — 业务服务层
   - `fineract-provider/src/main/java/.../jobs/service/JobRegisterServiceImpl.java` — 批处理作业注册

> **改代码后**：Java 无 HMR——保存后用 Step 7 的重启命令重启进程，断点会自动重连（JDWP 支持 attach 后重连）。

### Step 4: Reproduce the Issue

1. **Trigger the action** that causes the issue:
   ```bash
   # 健康检查（免鉴权——必须先 -k）
   curl -sk https://localhost:8443/fineract-provider/actuator/health

   # 业务 API——必须带租户头 + Basic Auth
   curl -sk https://localhost:8443/fineract-provider/api/v1/clients \
     -H 'Fineract-Platform-TenantId: default' \
     -H 'Authorization: Basic bWlmb3M6cGFzc3dvcmQ='
   # 空库期望：{"totalFilteredRecords":0,"pageItems":[]}

   # 常见业务端点
   curl -sk https://localhost:8443/fineract-provider/api/v1/loans -H "$ABNK_TENANT" -H "$ABNK_AUTH"
   curl -sk https://localhost:8443/fineract-provider/api/v1/savings -H "$ABNK_TENANT" -H "$ABNK_AUTH"
   curl -sk https://localhost:8443/fineract-provider/api/v1/offices -H "$ABNK_TENANT" -H "$ABNK_AUTH"

   # POST 示例（创建客户，注意 Fineract 用 locale/dateFormat 必填参数）
   curl -sk -X POST https://localhost:8443/fineract-provider/api/v1/clients \
     -H 'Fineract-Platform-TenantId: default' \
     -H 'Authorization: Basic bWlmb3M6cGFzc3dvcmQ=' \
     -H 'Content-Type: application/json' \
     -d '{"officeId":1,"firstname":"Test","lastname":"User","dateFormat":"yyyy-MM-dd","locale":"en","active":true,"activationDate":"2026-01-01"}'
   ```
   > **API 契约以 https://localhost:8443/fineract-provider/api-docs 为准**——Fineract 的 API 参数组合繁杂，不确定时先查 api-docs，别猜。

   - **Database inspection**（存储层调试）:
     ```bash
     # 业务库
     docker exec -it abnk-pg psql -U root -d fineract_default
     # 单条查询
     docker exec abnk-pg psql -U root -d fineract_default -c "SELECT COUNT(*) FROM m_client"
     # 租户库（看租户清单与连接串）
     docker exec abnk-pg psql -U root -d fineract_tenants -c "SELECT id, identifier, schema_name FROM tenant"
     # Liquibase 账本
     docker exec abnk-pg psql -U root -d fineract_default -c "SELECT orderexecuted, id, exectype FROM databasechangelog ORDER BY orderexecuted DESC LIMIT 10"
     ```

   - **Batch job / Scheduler**（Fineract 的 COB 作业等）:
     ```bash
     curl -sk https://localhost:8443/fineract-provider/api/v1/jobs -H "$ABNK_TENANT" -H "$ABNK_AUTH"
     ```

2. **Wait** for the expected behavior to occur (or fail to occur)

3. **Capture initial logs**:
   ```bash
   tail -200 logs/fineract.log
   ```

### Step 5: Form Hypothesis from Logs

Follow `.asdm/toolsets/abnk-harness-toolset/specs/log-reading-spec.md`

1. **Read all logs** and look for:
   ```bash
   # 错误与异常（Java 栈——搜 Exception 与 Caused by）
   grep -iE 'error|fail|exception|caused by|WARN|SEVERE' logs/fineract.log

   # 堆栈跟踪（-A 30 拿完整 Java 栈）
   grep -A30 -E 'Exception|Caused by:' logs/fineract.log | head -80

   # 首次出现位置（定位最早的错误源头）
   grep -n -iE 'error|exception' logs/fineract.log | head -5
   ```

2. **Trace the data flow** across the stack:
   ```bash
   # 请求是否进入
   grep -iE 'incoming|request|received' logs/fineract.log | head -10

   # SQL 层（Hikari 慢查询/异常，application.properties 已开 logSlowQueries/dumpQueriesOnException）
   grep -iE 'hikari|slow query|sql' logs/fineract.log | head -20

   # Liquibase 迁移（首次启动失败必查）
   grep -iE 'liquibase|changelog|migration' logs/fineract.log | head -20

   # postgres 容器
   docker logs abnk-pg --tail 50 2>&1 | grep -iE 'error|fatal'
   ```

3. **Form a hypothesis**: Based on log evidence, what is the most likely root cause?

### Step 6: Augment Logs if Needed

Follow `.asdm/toolsets/abnk-harness-toolset/specs/log-augmentation-spec.md`

If existing logs are insufficient to confirm the hypothesis:

1. **Identify strategic injection points** in Fineract code:
   - `fineract-provider/src/main/java/.../api/**ApiResource.java` — REST 层（请求进入点）
   - `fineract-*/src/main/java/.../service/**ServiceImpl.java` — 业务服务层
   - `fineract-core/src/main/java/.../domain/actioncommand/` — 命令模型
   - `fineract-provider/src/main/java/.../jobs/service/JobRegisterServiceImpl.java` — 作业调度
   - `fineract-provider/src/main/resources/db/changelog/tenant/parts/` — Liquibase changelog（数据/DDL 问题）

2. **Inject temporary debug logs**（Java 用 SLF4J，勿用 System.out）:
   ```java
   // 类内已有 @Slf4j（Lombok）时用：
   log.error("[DEBUG] ApiResource: received request {}", requestBody);
   // 无 @Slf4j 时临时加静态 logger：
   private static final Logger log = LoggerFactory.getLogger(XxxService.class);
   log.error("[DEBUG] XxxService: input={}", input);
   ```
   > 用 `log.error` 而非 `log.debug`——Fineract 默认日志级别下 debug 不输出，省去改 logback 配置的麻烦。

3. **Restart the affected process**（Java 无 HMR，必须重启）:
   ```bash
   lsof -ti:8443 -sTCP:LISTEN | xargs kill
   cd fineract
   JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
     nohup ./gradlew devRun > ../logs/fineract.log 2>&1 &
   echo $! >> ../logs/debug-process.pid
   cd ..
   # 等就绪
   for i in $(seq 1 600); do grep -q "APACHE FINERACT IS READY" logs/fineract.log && break; sleep 1; done
   ```
   > 增量重启远快于首次（Gradle 只重编译改动模块），但仍需 1–3 min。

4. **Reproduce the issue again**

5. **Read the augmented logs**:
   ```bash
   grep '\[DEBUG\]' logs/fineract.log
   ```

6. **If hypothesis denied**: Form new hypothesis, inject new logs, repeat

### Step 7: Implement Fix

Once root cause is confirmed:

1. **Fix the root cause** in the source code
2. **Remove all temporary debug logs** injected in Step 6:
   ```bash
   grep -rn '\[DEBUG\]' fineract/fineract-provider/src fineract/fineract-core/src fineract/fineract-loan/src
   # 逐个删除后验证：
   grep -rn '\[DEBUG\]' fineract/fineract-provider/src fineract/fineract-core/src fineract/fineract-loan/src | wc -l  # must be 0
   ```
3. **Rebuild check**（编译验证，不跑全量质量检查）:
   ```bash
   cd fineract && ./gradlew :fineract-provider:classes && cd ..
   ```
   > 提交前如需过质量门禁，另跑 `./gradlew spotlessApply checkstyleMain`（`devRun` 会跳过它们，不代表代码合规）。

4. **Restart affected processes**（Java 无 HMR）— 命令同 Step 6 第 3 条

### Step 8: Verify Fix

1. **Reproduce the issue again**（same steps as Step 4）
2. **Check logs**: Verify the expected behavior now occurs
   ```bash
   tail -50 logs/fineract.log
   grep -icE 'error|exception' logs/fineract.log
   ```
3. **Check API**（backend issue）:
   ```bash
   curl -sk https://localhost:8443/fineract-provider/actuator/health
   ```
4. **Check DB**（data issue）:
   ```bash
   docker exec abnk-pg psql -U root -d fineract_default -c "<验证 SQL>"
   ```
5. **If not fixed**: Return to Step 5 with new hypothesis

### Step 9: Cleanup

1. **Ensure all temporary debug logs are removed**:
   ```bash
   grep -rn '\[DEBUG\]' fineract/fineract-provider/src fineract/fineract-core/src fineract/fineract-loan/src | wc -l  # must be 0
   ```
2. **Commit the fix** with a descriptive message:
   ```
   fix(abnk): <description of root cause and fix>

   - <what was wrong>
   - <what was changed>
   - <how it was verified>
   ```
3. **Kill debug processes**（optional，or leave running for further testing）:
   ```bash
   lsof -ti:8443 -sTCP:LISTEN | xargs kill
   # postgres 容器默认保留（数据卷持久）：docker stop abnk-pg 可停但非必需
   ```

---

## Self-Directed Fix Scheduling

Follow `.asdm/toolsets/abnk-harness-toolset/specs/fix-scheduling-spec.md`

The AI should **autonomously** drive the debugging loop:

```
┌──────────────────────────────────────────────────┐
│  Hypothesis (from logs)                           │
│       ↓                                          │
│  Diagnose (augment logs if needed)                │
│       ↓                                          │
│  Fix (edit Java source)                           │
│       ↓                                          │
│  Rebuild (:fineract-provider:classes)             │
│  + Restart (kill :8443 + devRun —— 无 HMR)        │
│       ↓                                          │
│  Verify (reproduce + check logs/API/DB)           │
│       ↓                                          │
│  Fixed? ── No ──→ Back to Hypothesis              │
│       │                                          │
│      Yes                                          │
│       ↓                                          │
│  Cleanup (remove [DEBUG] logs, commit)            │
└──────────────────────────────────────────────────┘
```

**Key principles**:
- **Don't ask the user for each step** — proceed autonomously through the loop
- **Only stop and ask** if: blocked by missing information, destructive operation needed, or 3 failed fix attempts
- **Record each iteration**: What was the hypothesis, what was checked, what was found, what was fixed
- **Limit iterations**: Maximum 5 hypothesis-fix-verify cycles before asking user for guidance

## When to Stop and Ask

Stop the autonomous loop and ask the user when:

1. **Missing information**: Can't determine how to start a process, what ports are used, etc.
2. **Destructive operation**: 删除 postgres 数据卷（`docker rm -f abnk-pg && docker volume rm abnk-pg-data`）、drop 数据库、覆盖已有业务数据、push to remote
3. **3 failed fix attempts**: Three consecutive fix attempts didn't resolve the issue
4. **Root cause is external**: The issue is caused by JDK/Gradle/Docker 环境问题，或 Fineract 上游缺陷（此时考虑 upstream issue 或本地 patch 策略）
5. **Ambiguous requirements**: Not sure what the "expected" behavior should be
6. **首次构建超过 30 min 仍未就绪**：可能是 toolchain 下载或网络问题，需人工介入判断

## ABNK/Fineract-Specific Debugging Tips

### JDK 25 Toolchain Missing
构建报 `No matching toolchains found` / 自动下载 toolchain 卡住：
1. `java -version` 确认实际版本（本机 17/21 都不行）
2. `sdk install java 25-zulu`
3. 在 `fineract` 目录的 `.vscode/settings.json` 指定 `java.jdt.ls.java.home`，或在命令行前置 `JAVA_HOME=...`

### Liquibase Migration Failure（首次启动失败）
`logs/fineract.log` 出现 Liquibase 异常：
1. 查账本：`docker exec abnk-pg psql -U root -d fineract_default -c "SELECT orderexecuted, id, exectype FROM databasechangelog ORDER BY orderexecuted DESC LIMIT 10"`
2. `exectype` 为 `FAILED` 说明该 changelog 失败——修根因后需清理该行再重启
3. **全新重来（破坏性，先问用户）**：`docker rm -f abnk-pg && docker volume rm abnk-pg-data` → 重建容器 → createPGDB → 重启 Fineract
4. **绝不在迁移过程中 Ctrl-C**——这是最常见的账本损坏原因

### Port Conflict on :8443 / :5005
1. `lsof -i:8443 -sTCP:LISTEN` / `lsof -i:5005 -sTCP:LISTEN`
2. 杀掉：`lsof -ti:<port> -sTCP:LISTEN | xargs kill`
3. 或用 `FINERACT_SERVER_PORT` 环境变量改端口

### SSL / Certificate Issues
- 所有 curl 必须 `-k`（自签 `keystore.jks`，密码 `openmf`）
- 本地想关 SSL：`FINERACT_SERVER_SSL_ENABLED=false`（仅本地调试）
- Postman 需在 Settings 关掉 SSL certificate verification

### 401 / 403 / 租户相关 4xx
1. 租户头缺失 → 加 `-H 'Fineract-Platform-TenantId: default'`
2. Basic Auth 错 → 默认 `mifos:password`，base64 = `bWlmb3M6cGFzc3dvcmQ=`
3. OAuth2 打开时 Basic 失效 → 检查 `fineract.security.oauth2.enabled`（默认 false）
4. `/actuator/health` 免鉴权——用它先区分是鉴权问题还是进程问题

### Gradle 构建慢 / 卡住
1. `gradle.properties` 已有 `org.gradle.jvmargs=-Xmx12g`——本机 64 GB RAM 足够，无需调整
2. 首次必慢（OpenAPI `resolve` + Avro 代码生成）——耐心等，勿中断
3. 想加速：确认用 `devRun` 而非 `bootRun`（前者跳过全部质量检查）
4. 缓存失效类诡异问题：`./gradlew --stop` 停掉守护进程后重试

### 杀进程杀不掉（Gradle fork JVM 陷阱）
`kill <gradle-pid>` 只杀 Gradle 客户端，Spring Boot 进程仍占 :8443：
1. 一律按端口杀：`lsof -ti:8443 -sTCP:LISTEN | xargs kill`
2. 确认：`lsof -i:8443 -sTCP:LISTEN`（应无输出）

### 唤醒 Modulith Report（架构违规排查）
```bash
cd fineract && ./gradlew :fineract-provider:test --tests '*Modulith*' -Dfineract.modulith.report=true
# 生成的架构图在 fineract-provider/build/reports/modulith/
```
