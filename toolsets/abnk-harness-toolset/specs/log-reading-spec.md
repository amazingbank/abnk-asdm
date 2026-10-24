# Log Reading Spec

> Read, filter, and analyze logs across all managed processes to identify errors and trace data flow

## Overview

Log reading is the primary diagnostic tool in the debugging loop. This spec defines patterns for filtering logs to find errors, trace requests, and identify anomalies — **adapted for Java/Spring Boot stacks**.

## Basic Log Reading

### Read all logs
```bash
cat logs/fineract.log
tail -200 logs/fineract.log
tail -f logs/fineract.log
docker logs abnk-pg --tail 100
```

### Filter for errors (Java)
```bash
# 错误与异常
grep -iE 'error|fail|exception|caused by|SEVERE' logs/fineract.log

# 完整 Java 堆栈（Java 栈很长，-A30 起）
grep -A30 -E 'Exception|Caused by:' logs/fineract.log | head -100

# 警告
grep -i 'WARN' logs/fineract.log

# 首次出现（定位最早错误源头，避免被后续连锁异常淹没）
grep -n -iE 'error|exception' logs/fineract.log | head -5
```

### Filter for specific patterns
```bash
# 租户/请求级追踪
grep -iE 'tenant|request|correlation' logs/fineract.log

# SQL 层（Hikari 已开 logSlowQueries + dumpQueriesOnException）
grep -iE 'hikari|slow query|prepared' logs/fineract.log | head -20

# Liquibase 迁移（首次启动失败必查）
grep -iE 'liquibase|changelog|migration' logs/fineract.log | head -20

# 批处理作业
grep -iE 'job|scheduler|COB' logs/fineract.log | head -20

# 超时/性能
grep -iE 'timeout|slow|elapsed|duration' logs/fineract.log
```

## Cross-Process Log Tracing

```bash
# 用唯一标识（租户 ID / 请求 ID / 客户 ID）跨进程搜
IDENTIFIER="<unique-id>"
grep -rn "$IDENTIFIER" logs/

# 请求入口 → 出口
grep -iE 'incoming|received' logs/fineract.log | head -10
grep -iE 'response|completed' logs/fineract.log | tail -10

# 数据库侧佐证
docker exec abnk-pg psql -U root -d fineract_default -c "SELECT ..."
```

## Identify Missing Logs

Sometimes the most important clue is what's **missing** from the logs:

```bash
# 预期有日志但没有 → 代码路径未走到
grep -iE '<expected-log-pattern>' logs/fineract.log
# 无输出 = 代码路径未执行 → 这是强根因信号，用 [DEBUG] 注入确认
```

## Log Analysis Patterns

```bash
# 错误 + 上下文
grep -B5 -A20 'Exception' logs/fineract.log

# 频次分析
grep -c -iE 'error|exception' logs/fineract.log

# 时间线重建
grep -iE 'request|job|event|error' logs/fineract.log | sort
```

## No Browser Console (阶段一)

阶段一 Fineract 是纯 API 服务，**无前端进程**：

- 不需要 `preview_url` / `playwright-cli`（`config.json → browser.tool = curl`）
- API 契约查 `https://localhost:8443/fineract-provider/api-docs`（可在 IDE 内置浏览器打开，需信任自签证书）
- 验证一律走 curl：
  ```bash
  curl -sk https://localhost:8443/fineract-provider/actuator/health
  ```

> 未来 Amazing Bank 接入前端后，在 `config.json` 登记前端进程并将 `browser.tool` 改为 `preview_url`，届时再启用本节的前端日志能力。

## Decision Framework

After reading logs, classify the finding:

| Finding | Next Step |
|---------|-----------|
| **Exception with stack trace** | 读栈顶业务包（非框架包）的定位行，修它 |
| **`Caused by:` 链** | 看**最内层** Caused by——那才是真根因，外层是包装 |
| **WARN found** | 判断是根因还是副作用（如 Hikari 慢查询警告常指向 SQL 问题） |
| **Expected log missing** | 代码路径未走到——注入 `[DEBUG]` 确认 |
| **Log 正常但 API/DB 结果错** | 层间数据转换问题——查 DTO/实体字段映射 |
| **No relevant logs at all** | 请求未进入——查路由、鉴权（401）、租户头 |
| **仅在首次启动出现** | Liquibase 迁移问题——查 `databasechangelog` 账本 |
