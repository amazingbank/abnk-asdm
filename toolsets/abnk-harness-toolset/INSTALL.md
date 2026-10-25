# ABNK Harness Toolset Installation

**Toolset ID:** `abnk-harness-toolset`

## Overview

This document provides instructions for installing and setting up the ABNK Harness Toolset for the Amazing Bank (ABNK) IT system. It provides two actions:

1. **abnk-debugger** — Automated debugging with process management, log analysis, and self-directed fix scheduling（阶段一：PostgreSQL `:5432` + Fineract `:8443`）
2. **abnk-doc-review** — Evidence-driven five-dimension review (feasibility/completeness/reasonableness/consistency/accuracy) of Sprint/Phase design docs under `.asdm/workspace/docs/Sprints/`（结构与 aLink `Sprints/` 一致：`<版本>/partNN/<版本>-PartNN-*.md`），with code-evidence verification against the Fineract codebase and executable acceptance-step auditing（步步有验收）

## AI Guided Installation

To install this toolset using AI Guided Installation, copy and paste the following prompt into your AI Coding tool's chat window:

```shell
Follow instructions in .asdm/toolsets/abnk-harness-toolset/INSTALL.md
```

## Installation Steps

### 1. Detect the current `Agentic Engine` provider

Detect the current AI coding assistant provider (e.g., Claude Code, GitHub Copilot, Tencent CodeBuddy). Using the following guidelines to detect the provider:

- If `.claude` directory exists, use `Claude Code`
- If `.github` directory exists, use `GitHub Copilot`
- If `.codebuddy` directory exists, use `Tencent CodeBuddy`
- If no such folder is found in the current workspace, give user a prompt to select a provider manually

> **ABNK 工作区现状**：工作区根（`amazingbank-ws`）目前没有 `.claude` / `.github` / `.codebuddy`，需在步骤 2 创建 `.codebuddy/commands/`（默认 Tencent CodeBuddy——本机已装 VS Code + Java Extension Pack）。

### 2. Create shortcut commands for ABNK Harness Toolset (toolset ID: `abnk-harness-toolset`) in provider's entry point

Create shortcut commands in the appropriate location based on the detected provider. Each command file contains **only frontmatter + a thin `Follow` reference** to the action instruction file — **do NOT copy the full action content**. This keeps commands thin and ensures the single source of truth stays in `.asdm/toolsets/abnk-harness-toolset/actions/`.

#### For Claude Code (`.claude/commands/`):

```bash
mkdir -p .claude/commands/

cat > .claude/commands/abnk-debugger.md << 'EOF'
---
description: "Automated debugging for the Amazing Bank IT stack (PostgreSQL :5432 + Fineract :8443) with process management, log analysis, and self-directed fix scheduling"
argument-hint: "[describe the issue to debug]"
---

Follow the instructions in .asdm/toolsets/abnk-harness-toolset/actions/abnk-debugger.md to debug: $ARGUMENTS
EOF

# ABNK Doc Review command
cat > .claude/commands/abnk-doc-review.md << 'EOF'
---
description: "Five-dimension review of a Sprint/Phase design doc under .asdm/workspace/docs/Sprints/ with code-evidence verification"
argument-hint: "[path to the doc, e.g. .asdm/workspace/docs/Sprints/v0.0.1/part01/...Phase1-*.md]"
---

Follow the instructions in .asdm/toolsets/abnk-harness-toolset/actions/abnk-doc-review.md to review: $ARGUMENTS
EOF
```

#### For GitHub Copilot (`.github/prompts/`):

```bash
mkdir -p .github/prompts/

cat > .github/prompts/abnk-debugger.prompt.md << 'EOF'
---
agent: 'agent'
description: 'Automated debugging for the Amazing Bank IT stack with process management, log analysis, and self-directed fix scheduling'
argument-hint: 'Describe the issue to debug'
---

Follow the instructions in .asdm/toolsets/abnk-harness-toolset/actions/abnk-debugger.md to debug: $ARGUMENTS
EOF

# ABNK Doc Review prompt
cat > .github/prompts/abnk-doc-review.prompt.md << 'EOF'
---
agent: 'agent'
description: 'Five-dimension review of a Sprint/Phase design doc under .asdm/workspace/docs/Sprints/ with code-evidence verification'
argument-hint: 'Path to the doc, e.g. .asdm/workspace/docs/Sprints/v0.0.1/part01/...Phase1-*.md'
---

Follow the instructions in .asdm/toolsets/abnk-harness-toolset/actions/abnk-doc-review.md to review: $ARGUMENTS
EOF
```

#### For Tencent CodeBuddy (`.codebuddy/commands/`):

```bash
mkdir -p .codebuddy/commands/

cat > .codebuddy/commands/abnk-debugger.md << 'EOF'
Follow the instructions in .asdm/toolsets/abnk-harness-toolset/actions/abnk-debugger.md to debug: $ARGUMENTS
EOF

# ABNK Doc Review command（同样为 thin reference）
cat > .codebuddy/commands/abnk-doc-review.md << 'EOF'
Follow the instructions in .asdm/toolsets/abnk-harness-toolset/actions/abnk-doc-review.md to review: $ARGUMENTS
EOF
```

> **Why thin references?** The action instruction files (`.asdm/toolsets/abnk-harness-toolset/actions/*.md`) are the single source of truth. Copying their full content into each provider's command file creates duplication — when an action is updated, all copies must be manually synced. Thin `Follow` references ensure the provider command stays in sync automatically.

### 3. Install JDK 25 (hard requirement —阻塞项)

Fineract 的 `build.gradle:418` 用 Gradle toolchain 强制 **JDK 25**；本机仅装 17.0.9-zulu / 21.0.11-ms 时任何构建都起不来。

**本机实际安装记录（2026-10-24）**：`25.0.5+8-tem`（Temurin），位于 `~/.sdkman/candidates/java/25.0.5+8-tem`。

> ⚠️ **已知坑：`sdk install java <ver>` 在本机必定失败**。
> 症状：`Repackaging... → no matches found: /Users/leixu/.sdkman/tmp/out/*/Contents/Home → Stop! The archive was corrupt`。
> 根因：sdkman 的下载器处理不了 Adoptium 的 **307 → 302 双重跳转**（`api.adoptium.net` → `github.com/...` → `release-assets.githubusercontent.com`），拿到空文件。
> 放宽 `~/.sdkman/etc/config` 里的 `sdkman_curl_max_time` **无效**——不是超时问题。
> 解法：curl 直取 + sdkman 本地安装（下方步骤）。

```bash
# 1) 下载 Temurin 25（macOS arm64）——走双重跳转必须用 -L
curl -L --max-time 600 -o /tmp/jdk25-tem.tar.gz \
  "https://api.adoptium.net/v3/binary/latest/25/ga/mac/aarch64/jdk/hotspot/normal/eclipse"
# 校验：约 130MB，file 应为 gzip compressed data

# 2) 解压
cd /tmp && tar -xzf jdk25-tem.tar.gz      # → /tmp/jdk-25.0.5+8/Contents/Home

# 3) 本机安装（对 "set as default?" 必须答 n）
export SDKMAN_DIR="$HOME/.sdkman"; source "$HOME/.sdkman/bin/sdkman-init.sh"
printf 'n\n' | sdk install java 25.0.5+8-tem /tmp/jdk-25.0.5+8/Contents/Home

# 4) ⚠️ 必须移到永久位置——上一步只是软链到 /tmp，而 /tmp 会被系统清理
rm -f ~/.sdkman/candidates/java/25.0.5+8-tem
mv /tmp/jdk-25.0.5+8/Contents/Home ~/.sdkman/candidates/java/25.0.5+8-tem

# 5) 验证
~/.sdkman/candidates/java/25.0.5+8-tem/bin/java -version   # 25.0.5
java -version                                                # 仍应是 21.0.11——证明全局未被污染
```

> **不要设为 default**（`sdk default java ...`）以免污染本机的 17/21 项目。改为在 VS Code 按项目指定（见步骤 4）或在命令前 `JAVA_HOME=...`。

### 4. Configure VS Code for the Fineract Gradle project (可选——仅 IDE 内调试需要)

本机已装 VS Code + `redhat.java` + `vscode-java-debug` + `vscode-gradle`，可直接调试 Java。

在**工作区根**创建 `.vscode/settings.json`（以实际 JDK 25 路径为准）：

```json
{
  "java.jdt.ls.java.home": "/Users/leixu/.sdkman/candidates/java/25.0.5+8-tem",
  "java.configuration.runtimes": [
    { "name": "JavaSE-25", "path": "/Users/leixu/.sdkman/candidates/java/25.0.5+8-tem", "default": true }
  ],
  "java.import.gradle.java.home": "/Users/leixu/.sdkman/candidates/java/25.0.5+8-tem",
  "java.import.gradle.wrapper.enabled": true,
  "java.compile.nullAnalysis.mode": "disabled",
  "files.exclude": {
    "**/build": true,
    "**/bin": true
  },
  "files.watcherExclude": {
    "**/build/**": true,
    "**/.gradle/**": true
  }
}
```

并创建 `.vscode/launch.json`（远程 attach 到 `--debug-jvm` 的 JDWP 口）：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "java",
      "name": "Attach Fineract (:5005)",
      "request": "attach",
      "hostName": "localhost",
      "port": 5005
    }
  ]
}
```

> **Lombok**: Fineract 大量使用 Lombok（`build.gradle:752-753`）。`redhat.java` 默认启用 annotation processing；验证方式——打开一个 `@Getter` 类，若不报 "method not found" 即正常。

### 5. Create or Verify `config.json` (ABNK Project Environment Config)

Check if `config.json` exists in the toolset directory:

```bash
cat .asdm/toolsets/abnk-harness-toolset/config.json
```

If it exists, it contains Amazing Bank's process architecture, ports, auth config, and API endpoints — eliminating the need to re-explore the app each debugging session.

If it does NOT exist, the first debugging session will explore the app manually. After exploration, create `config.json` to accelerate future sessions. See existing `config.json` for schema reference.

### 6. Verify the Stack Can Start

Before first debugging session, verify the stack:

```bash
# 1) 起 postgres 容器
docker start abnk-pg 2>/dev/null || \
  docker run -d --name abnk-pg -p 5432:5432 \
    -e POSTGRES_USER=root -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=root \
    -v abnk-pg-data:/var/lib/postgresql/data postgres:18.3
until docker exec abnk-pg pg_isready -U root -q; do sleep 1; done

# 2) 建两个库（首次）
cd fineract
./gradlew createPGDB -PdbName=fineract_tenants
./gradlew createPGDB -PdbName=fineract_default

# 3) 起 Fineract（首次 15–30 min，别中断）
mkdir -p ../logs
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  nohup ./gradlew devRun > ../logs/fineract.log 2>&1 &
cd ..
for i in $(seq 1 1800); do grep -q "APACHE FINERACT IS READY" logs/fineract.log && break; sleep 1; done

# 4) 验证
curl -sk https://localhost:8443/fineract-provider/actuator/health
# 期望：{"status":"UP","groups":["liveness","readiness"]}

curl -sk https://localhost:8443/fineract-provider/api/v1/clients \
  -H 'Fineract-Platform-TenantId: default' \
  -H 'Authorization: Basic bWlmb3M6cGFzc3dvcmQ='
# 期望：{"totalFilteredRecords":0,"pageItems":[]}
```

## Verification

After installation, verify that:

1. Shortcut commands for `abnk-debugger` and `abnk-doc-review` are created in the provider directory（`.codebuddy/commands/` 等）—— contains only frontmatter + thin `Follow` reference
2. The ABNK Harness Toolset files are located in `.asdm/toolsets/abnk-harness-toolset`
3. `java -version` 为 **25.x**
4. `config.json` exists in `.asdm/toolsets/abnk-harness-toolset/` with ABNK project config
5. The workspace has a `logs/` directory（will be created automatically during debugging）
6. The stack can start：`abnk-pg` 容器就绪 + `curl -sk https://localhost:8443/fineract-provider/actuator/health` 返回 UP

## Available Commands

Once installed, you can use the following commands:

1. **`/abnk-debugger <issue description>`** — Start automated debugging session for the Amazing Bank IT stack
2. **`/abnk-doc-review <doc path>`** — Five-dimension review of a Sprint/Phase design doc under `.asdm/workspace/docs/Sprints/`（repeat with "再次检查" to iterate on previous rounds' blind spots until clean）

## Extending the Toolset

Amazing Bank 接入新系统时：

1. 在 `config.json → environments.local.processes` 追加一条（name / description / dir / startCommand / port / healthCheck / logFile / killCommand / language）
2. 在 `config.json → apiEndpoints` 补该系统的端点
3. 从 `extensions.planned` 移除该条目
4. **action / spec 文档无需改动**
