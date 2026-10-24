# Fix Scheduling Spec

> Self-directed fix loop: hypothesize → diagnose → fix → rebuild → restart → verify, autonomously

## Overview

The AI drives the debugging loop autonomously. It forms hypotheses based on log evidence, implements fixes, rebuilds/restarts processes, re-tests, and verifies — looping until the issue is resolved or it needs to ask the user.

## The Loop

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  1. HYPOTHESIS                                       │
│     - Based on log evidence                          │
│     - "I think the issue is X because log shows Y"   │
│                                                      │
│  2. DIAGNOSE                                         │
│     - Read existing logs                             │
│     - Attach debugger (:5005) or augment logs        │
│     - Reproduce and confirm/deny hypothesis          │
│                                                      │
│  3. FIX                                               │
│     - Edit Java source                                │
│     - Remove all [DEBUG] logs                        │
│                                                      │
│  4. REBUILD + RESTART                                │
│     - ./gradlew :fineract-provider:classes           │
│     - kill :8443（按端口），再 devRun                  │
│     - Wait for "APACHE FINERACT IS READY"            │
│     —— Java 无 HMR，这一步不可省（1–3 min）            │
│                                                      │
│  5. VERIFY                                           │
│     - Reproduce the issue again                      │
│     - Check logs for expected behavior               │
│     - Check API output (curl -k) / DB (psql)         │
│                                                      │
│  6. RESOLVED?                                        │
│     - YES → Cleanup (remove debug logs, commit)      │
│     - NO  → Back to Step 1 with new hypothesis       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Hypothesis Formation

### Evidence-driven

Every hypothesis must be backed by log evidence:

```
GOOD: "logs/fineract.log 显示 Liquibase 在 0000_upgrade_to_xxx.xml 报 FAILED，
       且 databasechangelog 有 exectype=FAILED 行。
       Hypothesis: 该 changelog 与已有数据冲突，需修 changeset 或清账本。"

BAD:  "Maybe the database connection is broken."
      (No evidence — pure speculation)
```

### Common hypothesis patterns

| Symptom | Hypothesis Pattern |
|---------|-------------------|
| 无任何相关日志 | 请求未进入——查路由、鉴权 401、租户头缺失 |
| Exception with stack trace | 读栈顶**业务包**（非框架包）定位行，修它 |
| `Caused by:` 链 | 看**最内层** Caused by——外层只是包装 |
| Expected log missing | 代码路径未执行——注入 `[DEBUG]` 或打断点确认 |
| API 返回错但日志正常 | DTO/实体字段映射问题 |
| 间歇性失败 | 并发/时序问题——加时间戳 `[DEBUG]` |
| 仅首次启动失败 | Liquibase 迁移问题——查 `databasechangelog` |
| 改了代码没生效 | Java 无 HMR——确认已 kill :8443 并重启 |
| 端口仍被占 | Gradle fork 陷阱——按端口 kill，不是按 PID |

### Multiple hypotheses

If the evidence supports multiple hypotheses, test them in order of:
1. **Most likely**（based on evidence and common patterns）
2. **Easiest to verify**（requires least injection/restart）
3. **Least destructive to test**（doesn't require data modification）

## Iteration Logging

For each iteration of the loop, record:

```
--- Iteration 1 ---
Hypothesis: 租户头缺失导致 4xx
Evidence: logs/fineract.log 无请求日志；直接 curl 不带租户头返回 403
Action: 复现脚本补 -H 'Fineract-Platform-TenantId: default'
Result: API 返回 200 + {"totalFilteredRecords":0,"pageItems":[]}。Issue resolved.

--- Iteration 2 ---
Hypothesis: LoanSchedule 计算入参错误
Evidence: 断点停在 XXXServiceImpl:142，amount=null
Action: 在调用方补默认值
Result: 重启后 API 返回正确排期。Issue resolved.
```

## Termination Conditions

### Stop and ask the user when:

1. **3 failed fix attempts**: Three consecutive iterations didn't resolve the issue
2. **Missing information**: Can't determine how to start a process, what ports are used, etc.
3. **Destructive operation needed**: 删除 postgres 数据卷、drop 数据库、覆盖业务数据、force push
4. **External dependency issue**: 根因在 JDK/Gradle/Docker 环境或 Fineract 上游缺陷
5. **Ambiguous requirements**: Not sure what the "expected" behavior should be
6. **首次构建超过 30 min 未就绪**: 可能是 toolchain 下载/网络问题，需人工判断

### Stop and declare success when:

1. **Issue is reproduced as fixed**: The same reproduction steps now produce the expected behavior
2. **Logs confirm correct flow**: All expected log entries are present, no errors
3. **API/DB output is correct**: The output matches expectations

## Fix Implementation Guidelines

### Minimal changes

- Fix **only** the root cause — don't refactor or clean up unrelated code
- Keep the fix as small as possible for easy review
- Don't introduce new patterns or abstractions unless necessary
- **Fineract 是上游开源项目**——修上游缺陷时优先考虑：能否在 `custom/` 自定义模块里解决（Fineract 的 `settings.gradle` 会动态加载 `custom/<company>/<category>/<module>`）？能则不改核心代码，降低后续升级冲突

### Rebuild strategy

Use `config.json` → `processes[].rebuildCommand` if available. Otherwise:

| Language/Platform | Rebuild Command | Restart Needed? |
|-------------------|----------------|-----------------|
| Java (Spring Boot, Gradle) | `./gradlew :fineract-provider:classes` | **Yes** — kill :8443 + 重新 devRun（无 HMR） |
| Java (full verification) | `./gradlew build` | Yes（含质量门禁，慢，仅提交前用） |
| PostgreSQL (container) | N/A（容器管理） | `docker restart abnk-pg`（极少需要） |

> **devRun 会跳过质量门禁**——提交代码前另行 `./gradlew spotlessApply checkstyleMain`，否则 CI 会挂。

### After fix

1. Remove ALL `[DEBUG]` logs injected during diagnosis
2. Verify removal: `grep -rn '\[DEBUG\]' fineract/fineract-provider/src | wc -l` → 0
3. Rebuild: `./gradlew :fineract-provider:classes`
4. Restart: `lsof -ti:8443 -sTCP:LISTEN | xargs kill` → 重新 devRun → 等 READY
5. Reproduce the issue to verify fix
   - **API**: `curl -sk https://localhost:8443/fineract-provider/actuator/health` + 业务端点
   - **Logs**: `tail -50 logs/fineract.log`
   - **DB**: `docker exec abnk-pg psql -U root -d fineract_default -c "..."`
6. If fixed: commit with descriptive message
7. If not fixed: return to hypothesis step

## Commit Message Format

```
fix(abnk): <description of root cause and fix>

- <what was wrong>
- <what was changed>
- <how it was verified>
```

> Fineract 上游仓库沿用其社区规范（如 `FINERACT-XXXX: <summary>`）。在 `fineract/` 目录内提交时按其规范；在 `.asdm/` 内提交时用 `fix(abnk):` 前缀。
