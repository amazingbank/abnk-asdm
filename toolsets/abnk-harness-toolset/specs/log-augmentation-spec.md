# Log Augmentation Spec

> Inject temporary debug logs at strategic points to trace data flow, then remove after root cause is found

## Overview

When existing logs are insufficient to identify the root cause, inject temporary debug logs at strategic points in the code to trace data flow. These logs are **temporary** — they must be removed after the root cause is confirmed.

**Java 特殊性**: Java 无 HMR，每次注入后必须重启进程（1–3 min 增量构建），因此注入要**一次到位**——同一次重启内把所有候选点都注入，不要反复重启。

## When to Augment

Augment logs when:

- Existing logs don't show the data flow clearly enough
- You need to confirm whether a specific code path is reached
- You need to inspect the value of a variable at a specific point
- You need to verify the timing or order of operations
- The hypothesis is "code path X is not reached" and you need to confirm

## When NOT to Augment

Do NOT augment logs when:

- The exception stack trace already points to the causing line（直接修）
- The issue is in configuration/environment（改配置，别改代码）
- The issue is in an external dependency（无法注入其代码）
- **已经有断点调试会话在跑**——优先用断点观察变量，比注入日志快得多（Java 无 HMR，重启成本高）

## Injection Strategy

### Step 1: Identify injection points

```
Hypothesis: "REST 层收到请求但服务层未处理"
→ Inject at: (1) ApiResource 入口（确认收到），(2) ServiceImpl 入口（确认进入）

Hypothesis: "服务 X 被调用时参数错误"
→ Inject at: (1) 调用方出口（log 实参），(2) 服务入口（log 形参）

Hypothesis: "Liquibase changelog 未生效"
→ 不注入代码——直接查 databasechangelog 账本表（数据侧更快）
```

### Step 2: Inject debug logs (Java / SLF4J)

**优先用断点；需要长周期/并发场景观察时才注入日志。**

```java
// 类上已有 @Slf4j（Lombok，Fineract 大量使用）时直接：
log.error("[DEBUG] ClientsApiResource: received request {}", apiRequestBodyAsJson);

// 无 @Slf4j 时临时加静态 logger（记得连同删除）：
private static final Logger log = LoggerFactory.getLogger(XxxServiceImpl.class);
log.error("[DEBUG] XxxServiceImpl: input={}, result={}", input, result);
```

> **用 `log.error` 而非 `log.debug`** —— Fineract 默认日志级别下 `debug` 不输出，用 error 可省掉改 `logback-spring.xml` 的麻烦，且保证一定落盘。

### Step 3: Mark injected logs

Always use a distinctive prefix (`[DEBUG]`) so injected logs are easy to find and remove:

```java
// Good — easy to find and remove
log.error("[DEBUG] LoanServiceImpl: disburse amount={}", amount);

// Bad — hard to distinguish from existing logs
log.error("disburse amount={}", amount);
```

### Step 4: Restart affected process（Java 无 HMR，必做）

```bash
lsof -ti:8443 -sTCP:LISTEN | xargs kill
cd fineract
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  nohup ./gradlew devRun > ../logs/fineract.log 2>&1 &
echo $! >> ../logs/debug-process.pid
cd ..
for i in $(seq 1 600); do grep -q "APACHE FINERACT IS READY" logs/fineract.log && break; sleep 1; done
```

### Step 5: Reproduce and read

```bash
# 复现（curl 触发）
curl -sk https://localhost:8443/fineract-provider/api/v1/clients \
  -H 'Fineract-Platform-TenantId: default' \
  -H 'Authorization: Basic bWlmb3M6cGFzc3dvcmQ='

# 读注入日志
grep '\[DEBUG\]' logs/fineract.log
```

### Step 6: Confirm or deny hypothesis

- **If debug log appears** → Code path is reached, check the logged values for anomalies
- **If debug log does NOT appear** → Code path is not reached, the issue is upstream

### Step 7: Remove ALL injected logs

**This is critical.** After root cause is found, remove all `[DEBUG]` logs:

```bash
grep -rn '\[DEBUG\]' fineract/fineract-provider/src fineract/fineract-core/src fineract/fineract-loan/src
# 逐个删除（连同临时加的 Logger 字段声明）后验证：
grep -rn '\[DEBUG\]' fineract/fineract-provider/src fineract/fineract-core/src fineract/fineract-loan/src | wc -l  # should be 0
```

## Common Injection Patterns (Java)

### Trace method entry/exit
```java
public CommandWrapperResult disburse(Long loanId, JsonCommand command) {
    log.error("[DEBUG] disburse: enter loanId={}, cmd={}", loanId, command.json());
    CommandWrapperResult result = doDisburse(loanId, command);
    log.error("[DEBUG] disburse: exit result={}", result);
    return result;
}
```

### Trace data transformation
```java
log.error("[DEBUG] before transform: {}", data);
var transformed = transform(data);
log.error("[DEBUG] after transform: {}", transformed);
```

### Trace conditional branches
```java
if (condition) {
    log.error("[DEBUG] branch A taken, condition={}", condition);
    // ...
} else {
    log.error("[DEBUG] branch B taken, condition={}", condition);
}
```

### Trace collection/batch processing
```java
log.error("[DEBUG] batch size={}, first={}", items.size(), items.isEmpty() ? null : items.get(0));
```

## Safety Rules

1. **Never commit debug logs** — Always remove before committing
2. **Never log sensitive data** — 不记密码、API key、token、客户 PII（银行系统红线）
3. **Limit injection scope** — 一次刷完所有候选点，避免反复重启（Java 重启成本高）
4. **Use `[DEBUG]` prefix** — 便于统一查找与删除
5. **Verify removal** — 跑 `grep -rn '\[DEBUG\]'` 确认清零
6. **优先断点** — 有 JDWP 会话时优先用断点观察变量，别先改代码
