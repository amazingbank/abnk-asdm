# ASDM Toolset - ABNK Harness Toolset

toolset-id: abnk-harness-toolset
toolset-name: ABNK Harness Toolset
version: 0.1.0
updated-date: 2026-10-24
toolset-description: Automated toolset for Amazing Bank (ABNK). Stage-1 stack: PostgreSQL 18.3 docker（:5432，fineract_tenants + fineract_default）+ Fineract ServerApplication（Gradle devRun，:8443 SSL，JDWP :5005）。Provides the debugger action; grows into the full Amazing Bank IT stack orchestrator via config.json.

## Overview

ABNK Harness Toolset is an **automated toolset** built for the Amazing Bank IT system. It is deliberately designed as a **config-driven orchestrator**, not a Fineract-specific script: every system that joins the Amazing Bank stack gets a `processes[]` entry in `config.json`, and the debugger drives them all without document changes.

Stage 1 (current) is a 2-process stack:

- **PostgreSQL docker container**: `abnk-pg`（PostgreSQL 18.3，宿主 `:5432`）——承载 `fineract_tenants`（租户存储库）与 `fineract_default`（默认业务租户库）
- **Fineract backend**: `org.apache.fineract.ServerApplication`（Spring Boot + 内嵌 Tomcat）on `:8443`（强制 HTTPS 自签证书，JDWP `:5005`）

It provides four core capabilities that work together to form a self-directed debugging loop:

1. **Process Management** — Start/stop/restart stack processes with nohup, capture PIDs, and route stdout/stderr to log files for analysis.
2. **Log Reading** — Read and filter logs across managed processes to identify errors, anomalies, and event flows.
3. **Log Augmentation** — Temporarily inject debug logging into source code（`log.error("[DEBUG] ...")`）at strategic locations, then remove after root cause is found.
4. **Self-Directed Fix Scheduling** — Autonomously form hypotheses, implement fixes, rebuild/restart processes, re-test, and verify — looping until the issue is resolved.

## Key Design Principles

1. **Config-Driven** — `config.json` captures the process architecture, ports, auth, and API endpoints. Eliminates re-exploring the app each session.
2. **Java-Aware** — Knows Java's constraints that generic debuggers miss: **no HMR**（改代码必重启）、**Gradle forks the JVM**（杀 PID 杀不掉应用，按端口杀）、**JDK toolchain 是硬门槛**。
3. **Reproducible Environment** — Always start processes with nohup + pid file + log file, never rely on existing foreground processes.
4. **Evidence-Driven** — Every hypothesis must be validated by log evidence before proceeding to fix.
5. **Self-Directed Loop** — Hypothesize → Diagnose → Fix → Rebuild+Restart → Verify → Repeat until resolved.
6. **Extensible by Config, Not by Copy** — New systems are added to `config.json`, not to the action documents.

## When to Use

Use ABNK Harness Toolset when:

- A Fineract/Amazing Bank feature is not working as expected and you need to debug across API + database
- You need reproducible process management（deterministic start/stop, log capture）
- You need to trace data flow across layers（REST → Service → Domain → SQL）by injecting temporary debug logs
- You want the AI to autonomously debug, fix, and verify without manual intervention
- The issue spans the API ↔ database boundary（Hikari / Liquibase）

## Toolset Structure

```
.asdm/toolsets/abnk-harness-toolset/
  - manifest.json                         # Toolset metadata
  - config.json                           # ABNK project environment config (processes, ports, APIs)
  - README.md                             # This file
  - INSTALL.md                            # Installation guide
  - actions/
    - abnk-debugger.md                    # Main debugging action (self-directed loop)
  - specs/
    - process-management-spec.md           # nohup/pid/log + container management + config.json discovery
    - log-reading-spec.md                  # Log filtering, Java stack trace reading
    - log-augmentation-spec.md             # Temporary debug log injection/removal (Java/SLF4J)
    - fix-scheduling-spec.md               # Self-directed fix loop methodology
```

## Usage

```shell
# Install the toolset (follow INSTALL.md)
# Then invoke:
/abnk-debugger <describe the issue>
```

## config.json

The `config.json` file captures the Amazing Bank environment configuration:

- **`project`**: Name（`abnk`）, logsDir, pidFile
- **`environments.local`**: Local dev environment
  - **`processes[]`**: Stage 1 = 2 processes — `postgres`（docker container `:5432`）、`fineract`（dir `fineract`，`:8443`，debugPort `:5005`）
  - **`auth`**: Basic Auth（`mifos:password`）+ 租户头 `Fineract-Platform-TenantId: default`
  - **`apiEndpoints`**: Key API URLs（health / clients / loans / savings / offices / apiDocs）+ psql shortcuts
  - **`database`**: 连接信息 + 两个库的职责 + createCommand + migrationVerify
- **`browser`**: `tool: curl` — 阶段一纯 API，**不需要 preview_url / playwright-cli**
- **`dependencies`**: JDK 25（硬门槛）/ Gradle 9.7.1 wrapper / Docker / git
- **`extensions`**: 记录未来接入的系统清单（前端 / Keycloak / Kafka / 自有业务服务）

> **扩展约定**: 每接入一个新系统 → 在 `processes[]` 追加一条（含 startCommand / port / healthCheck / logFile / killCommand），并在 `extensions.planned` 中移除对应项。action 文档无需改动。

This file is **project-specific** — it describes the Amazing Bank architecture. The toolset reads it if present and falls back to manual exploration if absent.
