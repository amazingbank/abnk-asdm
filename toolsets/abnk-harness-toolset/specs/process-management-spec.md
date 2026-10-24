# Process Management Spec

> Start/stop/restart application processes with nohup, PID tracking, and log file routing

## Overview

Reproducible debugging requires deterministic process management. This spec defines how to start, monitor, and clean up application processes using nohup, ensuring all stdout/stderr is captured to log files for analysis.

**本 spec 按 `config.json → environments.local.processes` 数组驱动**——Amazing Bank 后续接入的新系统追加到该数组即可，无需修改本文档。

## Config-Driven Process Discovery

**Always check for `config.json` first** — it eliminates re-exploring the app architecture each session:

```bash
cat .asdm/toolsets/abnk-harness-toolset/config.json
```

If `config.json` exists, extract:
- `processes[]` — 当前 2 条：
  - `postgres`（docker 容器 `abnk-pg`，宿主 `:5432`）
  - `fineract`（dir `fineract`，`:8443`，`debugPort` `:5005`，`killCommand` 按端口）
- `project.logsDir` — log directory（`logs/`）
- `project.pidFile` — `logs/debug-process.pid`
- `auth` — Basic Auth `mifos:password` + 租户头 `Fineract-Platform-TenantId: default`
- `apiEndpoints` — 健康检查与复现 URL
- `database` — 连接信息、createCommand、migrationVerify

> **ABNK note**: 阶段一为 2 进程栈——容器型进程（postgres，docker 管理）与 fork-JVM 型进程（fineract，Gradle devRun）。**当前无前端进程**，不需要 `preview_url` / `playwright-cli`（`browser.tool = curl`）。

**If `config.json` does NOT exist**, fall back to manual exploration:

1. **Read project config**: `build.gradle`, `settings.gradle`, `gradle.properties`, `application.properties`, `docker-compose*.yml`
2. **Identify processes**: 数据库容器 + 后端服务 +（未来）前端/消息中间件
3. **Identify start commands**: e.g. `./gradlew devRun`, `docker run ...`
4. **Identify ports**: e.g. postgres 5432、fineract 8443、JDWP 5005
5. **Identify dependencies**: 数据库必须先于应用启动

> **Recommendation**: After first manual exploration, create `config.json` to accelerate future sessions.

## Directory Structure

```
<workspace-root>/
  logs/
    <process-name>.log         # One log file per process
    debug-process.pid           # PID file (one PID per line)
```

## Start Processes

### Step 1: Create log directory
```bash
mkdir -p logs
```

### Step 2: Kill existing processes on target ports
```bash
lsof -ti:8443 -sTCP:LISTEN 2>/dev/null | xargs kill 2>/dev/null
lsof -ti:5005 -sTCP:LISTEN 2>/dev/null | xargs kill 2>/dev/null
# 按 config.json 中每条 process 的 port 执行
```

### Step 3: Start the container process (postgres)
```bash
docker start abnk-pg 2>/dev/null || \
  docker run -d --name abnk-pg -p 5432:5432 \
    -e POSTGRES_USER=root -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=root \
    -v abnk-pg-data:/var/lib/postgresql/data postgres:18.3
# 容器由 docker 管理，不写 PID 文件
```

### Step 4: Create databases (first time only)
```bash
cd fineract
./gradlew createPGDB -PdbName=fineract_tenants
./gradlew createPGDB -PdbName=fineract_default
cd ..
```

### Step 5: Start the JVM process (fineract) with nohup
```bash
cd fineract
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  nohup ./gradlew devRun > ../logs/fineract.log 2>&1 &
echo $! >> ../logs/debug-process.pid
cd ..
```

```bash
# 需要断点调试时（JDWP :5005）
cd fineract
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  nohup ./gradlew devRun --debug-jvm > ../logs/fineract.log 2>&1 &
echo $! >> ../logs/debug-process.pid
cd ..
```

> **⚠️ Gradle fork 陷阱**: `nohup ./gradlew devRun` 的 PID 是 **Gradle 客户端**，Spring Boot 跑在它 fork 出的独立 JVM 里。杀 PID 杀不掉应用——**停机一律按端口 kill**。

### Step 6: Wait for each process to be ready
```bash
# postgres（轮询 pg_isready）
until docker exec abnk-pg pg_isready -U root -q; do sleep 1; done

# fineract（轮询 readyPattern——首次最长 30 min）
for i in $(seq 1 1800); do
  grep -q "APACHE FINERACT IS READY" logs/fineract.log && break
  sleep 1
done

# HTTP 健康检查（自签证书必须 -k）
curl -sk https://localhost:8443/fineract-provider/actuator/health
# 期望：{"status":"UP","groups":["liveness","readiness"]}
```

### Step 7: Verify migration (after first start)
```bash
docker exec abnk-pg psql -U root -d fineract_default -tAc \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"
# 期望：> 300
```

## Restart a Single Process

**Java 无 HMR**——改代码后必须重启：

```bash
# 1) 按端口杀（唯一可靠方式）
lsof -ti:8443 -sTCP:LISTEN | xargs kill

# 2) 重启
cd fineract
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  nohup ./gradlew devRun > ../logs/fineract.log 2>&1 &
echo $! >> ../logs/debug-process.pid
cd ..

# 3) 等就绪
for i in $(seq 1 600); do grep -q "APACHE FINERACT IS READY" logs/fineract.log && break; sleep 1; done
```

> 增量重启远快于首次（Gradle 只重编译改动模块），通常 1–3 min。

## Monitor Processes

```bash
# 端口占用
lsof -i:8443 -sTCP:LISTEN
lsof -i:5005 -sTCP:LISTEN

# 容器状态
docker ps --filter name=abnk-pg

# 跟踪日志
tail -f logs/fineract.log
docker logs abnk-pg --tail 50
```

## Cleanup

```bash
# 杀 JVM 进程（按端口——不要用 pid 文件，它记的是 Gradle 客户端）
lsof -ti:8443 -sTCP:LISTEN | xargs kill
lsof -ti:5005 -sTCP:LISTEN | xargs kill

# 停容器（保留数据卷）
docker stop abnk-pg

# 全量销毁（破坏性——必须先问用户）
# docker rm -f abnk-pg && docker volume rm abnk-pg-data

# 清理日志
rm -rf logs/*
```

## Notes

- 启动顺序按 `config.json` 的 `processes[]` 数组（依赖在前）
- Always create `logs/` before starting processes
- 容器型进程用 docker 管理，不进 PID 文件；JVM 型进程写 PID 文件（仅供记录，杀进程按端口）
- If a process fails to start, read its log file immediately
- Use `>>` (append) for PID file; use `>` (overwrite) for individual log files

## Common Pitfalls

### 杀进程杀不掉
`kill <gradle-pid>` 后端口仍被占 → Spring Boot 在 fork 出的 JVM 里：
1. `lsof -ti:8443 -sTCP:LISTEN | xargs kill`
2. 确认 `lsof -i:8443 -sTCP:LISTEN` 无输出

### Liquibase 账本损坏（首次启动被中断）
启动中 Ctrl-C 导致 `databasechangelog` 出现 `FAILED` 行，下次启动即失败：
1. 查账本：`docker exec abnk-pg psql -U root -d fineract_default -c "SELECT orderexecuted, id, exectype FROM databasechangelog ORDER BY orderexecuted DESC LIMIT 10"`
2. 修根因后清理 FAILED 行再重启
3. 全新重来（破坏性，先问用户）：销毁容器 + 数据卷 → 重建 → createPGDB → 启动

### JDK 25 缺失
构建报 `No matching toolchains found` → `sdk install java 25-zulu`，并在命令前 `JAVA_HOME=...` 或配 `.vscode/settings.json`。

### 首次启动过慢
15–30 min 属正常（7100+ Java 文件 + OpenAPI/Avro 代码生成 + Liquibase 建表）。**不要中断**。
