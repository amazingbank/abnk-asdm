# ASDM Action: ABNK Sprint Doc Review

## Metadata

```json
{
  "guid": "d4e5f6a7-b8c9-4012-8def-567890abcdef",
  "name": "abnk-doc-review",
  "displayName": "ABNK Sprint Doc Review",
  "description": "- Five-dimension review (feasibility/completeness/reasonableness/consistency/accuracy) of Sprint/Phase design docs under .asdm/workspace/docs/Sprints/, with code-evidence verification against the Fineract codebase and per-step acceptance auditing (执行和验收步骤·步步有验收); also audits the 前置条件 section (environment summary table · judgeable 判据 · 前置条件门槛/分层放行), the per-task trio (改动详情/交付物/执行和验收步骤), task-ID/step-ID scheme, and sequential task gating (任务门禁)",
  "toolset": {
    "guid": "b7a2c9d1-4e3f-4a58-9c6b-1d2e3f4a5b6c",
    "id": "abnk-harness-toolset",
    "name": "ABNK Harness Toolset",
    "version": "0.1.1"
  },
  "scenario": "设计文档审核"
}
```

## Overview

This action performs **evidence-driven five-dimension review** of a Sprint/Phase design document (`.asdm/workspace/docs/Sprints/**/v*-*-PhaseN-*.md`). Every claim in the doc is verified against the actual Fineract code and the real runtime environment (postgres 容器 + fineract 进程); every 执行和验收步骤 item is audited for executability. Problems found are fixed in place, cross-referenced sections are synchronized, and a structured report is produced. The review loops ("再次检查") until no new findings — each round shifts focus to the previous round's blind spots.

**ABNK project context** (verify at review time, never assume):
- 双进程栈：**postgres**（docker 容器 `abnk-pg`，PostgreSQL 18.3，宿主 `:5432`，承载 `fineract_tenants` + `fineract_default` 两库）/ **fineract**（`org.apache.fineract.ServerApplication`，Spring Boot + 内嵌 Tomcat，`:8443` 强制 HTTPS 自签证书，JDWP `:5005`，Gradle `devRun` 启动）
- **JDK 25 是硬门槛**（`fineract/build.gradle:418` toolchain）；构建一律用仓库自带 wrapper `./gradlew`（禁用系统 gradle）
- **Java 栈无 HMR**——任何代码改动必须按端口 kill（`lsof -ti:8443 -sTCP:LISTEN | xargs kill`）+ 重启 `devRun` + 等日志 `APACHE FINERACT IS READY`；Gradle 会 fork JVM，**杀 Gradle 客户端 PID 不杀应用**
- DB 迁移 = **Liquibase 随启动自动执行**（非 Flyway 人工直连）——changelog 位于 `fineract/fineract-provider/src/main/resources/db/changelog/`，`db.changelog-master.xml` 为总账本
- 验证通道：**curl**（业务 API 必须 `-k` + Basic Auth 头 + 租户头 `Fineract-Platform-TenantId: default`；actuator 免鉴权）+ **psql**（`docker exec abnk-pg psql -U root -d fineract_default`）；阶段一无前端 UI——不适用 playwright/preview_url 类验收
- 测试运行器：**Gradle test 任务**（如 `./gradlew :fineract-provider:test`）与 `fineract-e2e-tests`（Cucumber E2E）——不是 jest/vitest，验收命令不得写错运行器
- 已知坑（实测发生，前置条件与步骤审核须携带）：① 首次完整编译 15–30 min；② 中途 Ctrl-C 启动会破坏 Liquibase changelog 账本；③ VS Code Gradle 扩展后台构建可产出截断 jar 且 build cache 反复还原损坏产物（处置：`./gradlew --stop && clean && rm -rf ~/.gradle/caches/build-cache-1`）；④ compose 项目名固定 `abnk-system`（撞名会误停他项目容器）；⑤ `docker volume rm` 等破坏性命令须用户确认

**Sprint 文档目录约定**（与 aLink 的 `.asdm/workspace/Sprints/` 结构保持一致，abnk 收敛在 `docs/` 层级下）：

```
.asdm/workspace/docs/Sprints/
  v0.0.1/                                  # Sprint 版本目录（每轮 Sprint 一个）
    part01/                                # Part 目录（一个大方向/交付批次一个 part）
      v0.0.1-Part01-Plan.md                # 主计划（进度概要 + 任务分解索引）
      v0.0.1-Part01-<总体设计主题>.md       # 总体设计文档（可选，如 Dev-Center 类）
      v0.0.1-Part01-PhaseN-<Slug>.md       # Phase 详细计划（本 action 的主要审核对象）
      v0.0.1-Part01-Hotfix.md              # 线上修复记录（可选，被引用时纳入一致性核对）
```

命名硬规则：文档名一律带 `<版本>-Part<NN>-` 前缀；Phase 文档名含 Phase 号（`PhaseN` 或 `PhaseN.M[.K]`，深度可变）；目录内不混放非本 Part 文档。

**文件名仅限 ASCII**：文档文件名只允许字母/数字/连字符（`-`）/下划线（`_`）/点，**不得出现中文字符**（含全角字符）。Slug 用英文短语（如 `Phase2-Custom-L1.md`、`Phase0-Results.md`），中文内容只出现在文档正文与标题内。发现中文文件名 = P2 finding，就地重命名并同步所有引用（含同 Part 文档、Plan.md、跨文档链接）。

## Purpose

- Verify doc claims against code facts (Java class/method existence, call-site counts, REST endpoint paths, Liquibase changelog, DB table/column names) — never from memory
- Verify acceptance commands against the real environment (ports, processes, HTTPS/auth headers, log capabilities, test runners, DB observation channels)
- Audit task decomposition: purpose / 改动详情 / 交付物 / 执行和验收步骤 / execution rules completeness
- Ensure every design point has an executable verification step, and every test case maps to a step — **a step without a verification action may not be checked off (步步有验收)**
- Audit the 前置条件 section: environment summary table · itemized preconditions with judgeable 判据 · 现状 backed by actual inspection · 分层放行
- Fix findings in place with full-document consistency sweep

## Input

- Path to the Sprint/Phase document to review (e.g., `.asdm/workspace/docs/Sprints/v0.0.1/part01/v0.0.1-Part01-Phase1-XXX.md`)
- (Optional) "再次检查" — re-run with focus on previous round's blind spots

## Output

- Structured review report: findings table (severity / dimension / problem / evidence / fix), passed items, conclusion
- The doc updated in place (uncommitted; user decides when to commit)

---

## Review Procedure

### Step 1: Scope the Review

1. Read the target doc fully (do NOT review from memory of past reads — re-read)
2. Identify linked docs that must stay consistent:
   - 同 Part 的 `*Plan.md`（task list, titles, deliverables, status, work estimates）
   - 同 Part 的总体设计文档（`<版本>-Part<NN>-<主题>.md`，若 Phase 引用其架构决策）
   - Adjacent Phase docs referenced by the target (prior phases it builds on)
   - `*Hotfix.md` if referenced
   - `.asdm/workspace/docs/planning/` 下的规划文档（若被引用，纳入跨文档核对）
3. Note the doc's structure: background/decisions/design/task-breakdown/tests/risks/estimates.
   For task-breakdown specifically, note the ID scheme（task IDs derive from the Phase number;
   step IDs are `V<任务号>.<步骤序号>`——see rubric "Task ID & Heading Rules"）, the per-task
   trio（`#### 改动详情` / `#### 交付物` / `#### 执行和验收步骤`——缺任一为 P2）, and whether a
   **前置条件** section exists and follows "Prerequisites Section Rules" in the rubric
   （environment summary table on top · itemized preconditions with judgeable 判据 · 分层放行——applies
   to new/in-progress Phase docs; closed historical docs are NOT retro-fitted）.

### Step 2: Five-Dimension Checks

Run each dimension with the specific actions below. **Every claim must be verified with a tool call** (`grep` / `read_file` / `lsp` / `execute_command`), never assumed.

#### 2.1 Accuracy (准确性)

| Check | How |
|-------|-----|
| Call-site counts ("X 处调用") | `grep -rn` the symbol in the stated files（`fineract/` Java 源码）; count and compare |
| Class/method existence and signature | `read_file` or `lsp hover` at the stated location（Java：类名/包路径/方法签名） |
| DB schema claims（表/列/约束） | ① `grep` Liquibase changelog（`fineract/fineract-provider/src/main/resources/db/changelog/`）；② 实测 `docker exec abnk-pg psql -U root -d fineract_default -c '\d <表名>'`（运行态与环境一致时） |
| REST endpoint 声明 | 对照静态 OpenAPI spec：`curl -k https://localhost:8443/fineract-provider/fineract.json`（**用这个**；springdoc 动态 `/api-docs` 实测 500，勿用）或 `grep` 对应 Controller |
| Port / path / env values | `execute_command`: read `config.json`、`fineract/fineract-provider/src/main/resources/application.properties`、`abnk-system/deploy/docker-compose.yml`、`abnk-system/deploy/.env` |
| "Currently absent" claims (e.g., "该表无此列") | `grep` changelog / psql `\d` 查证；0 matches = claim holds |
| Ambiguous words ("同上", "1 次批量") | Resolve against actual code structure |
| 验证命令栈声明 | Java 构建/测试一律 `./gradlew`（禁用系统 gradle）；API 验证用 `curl -k` + 双头（Basic Auth + 租户头）；DB 观察用 `docker exec ... psql`——用错为 P3 |

#### 2.2 Feasibility (可行性)

- Do the target APIs/Service/Repository/Controller actually exist as the doc assumes？（对照 OpenAPI spec 与源码）
- Does the plan fit the real runtime?（**Java 无 HMR**——文档若暗示"改完即生效"为可行性失败；重启周期 = 按端口 kill + `devRun` + 等 `APACHE FINERACT IS READY`；首次完整编译 15–30 min）
- **Liquibase 适配**：新增 changelog 文件必须被 `db.changelog-master.xml`（或其 include 链）引用——`grep` 核实 include 关系；文档不得安排"运行时手工 DDL 绕过 changelog"（重启即漂移）
- 鉴权与多租户前提：业务 API 步骤是否声明 Basic Auth + `Fineract-Platform-TenantId: default` 双头；actuator（`/actuator/health`）免鉴权可直接用；HTTPS 自签——curl 必须 `-k`
- API 载荷格式：日期等字段是否声明 `locale` + `dateFormat`（Fineract API 实测漏 locale 报 400）；时间戳/版本参数须有序列化格式说明
- 权限/配置开关类前置（如 business date 默认 403 需先开 c_configuration）是否在步骤中安排
- psql 手工改数/造数的步骤：是否声明所属库（`fineract_default` 业务库 vs `fineract_tenants` 租户库）与恢复方案

#### 2.3 Completeness (完整性)

- Task decomposition covers the full scope of the decisions section
- Every task has the **trio, in order**（缺任一为 P2 finding）：
  1. `#### 改动详情` — new/modified file list（`**新建文件**` / `**修改文件**`）；**步骤所依赖的验证脚本与测试文件必须在此声明**（步骤引用了改动详情未声明的脚本 = P2）
  2. `#### 交付物` — deliverables list（file paths preferred）
  3. `#### 执行和验收步骤` — step list（标题即信号：执行与验收不可分离——never just "执行步骤"）
- Every step in that list is immediately followed by executable verification lines (验证动作/验证命令 + 期望输出) — a bare step line with no verification is a finding
- Every design point added late has a matching verification step
- Every test case (TC-XX-NN) maps to at least one verification step
- **前置条件 section present and complete**（new/in-progress docs; closed docs not
  retro-fitted——see rubric "Prerequisites Section Rules"）: environment summary table at the
  top · grouped precondition items each with a judgeable 判据（命令 → 期望）· 现状 backed by
  actual runtime inspection（docker ps/lsof/psql/ls——executed at review time）, never assumed ·
  前置条件门槛（分层放行——which task/step classes need which precondition groups）
- Edge branches (error paths, empty states, 4xx/5xx 分支) are either covered or explicitly declared out of scope

#### 2.4 Reasonableness (合理性)

- Threshold/boundary choices are coherent (e.g., 分页 limit vs 实际数据量；轮询间隔 vs Liquibase 启动时长) — rationale must not self-contradict
- 方案分层合理（REST → Service → Domain → Persistence 各层职责不越界；临时 hack 须标注退出计划）
- Verification burden proportional to change size; temporary environment changes（JDWP attach、`--debug-jvm`、docker 容器重建、psql 手工造数、`general_log` 类开关）are reverted or documented after use
- 任务粒度与工时预估相称（一个任务塞两个不相关交付 = P3 拆分建议）；Java 改动的任务须把重启验证周期计入工时

#### 2.5 Consistency (一致性)

- Same fact stated identically everywhere in the doc (counts, paths, table names, endpoint paths, prefix conventions) — `grep` the doc for each critical token after any fix
- **步骤 ID 嵌入任务号**：`V<任务号>.<步骤序号>`——步骤 ID 未嵌入其所属任务当前 ID 为一致性失败（renumber 后旧步骤 ID 残留同样）
- Cross-doc: Plan.md task titles/deliverables/status match the Phase doc verbatim（modulo ID prefix）; 跨文档任务号同步（renumber 后 `grep` Plan.md / 相邻 Phase 文档旧 ID 清零）
- Acceptance grep patterns are not coupled to implementation style（Java import 顺序、lambda vs 匿名类、常量折叠 `60 * 1000` vs `60000`）— or if coupled, the doc says so

### Step 3: Acceptance-Step Executability Audit (执行和验收步骤)

For each step under every task's 执行和验收步骤 list, verify ALL of:

0. **Verification attached (步步有验收)**: the step is immediately followed by an executable verification action (验证动作/验证命令 + 期望输出). A step without one is a finding — fix by adding the verification, or by folding the step into a step that has one. Applies to probe/exploration tasks too: their verification = recorded command+output archived and the matrix/table cell filled (no blank cells). Pure implementation steps (write code) still need a verification action — `./gradlew :fineract-provider:classes` / `compileJava` for code, curl/psql assertions for behavior
1. **Command + expected output**: the step states what to run and what output means pass. No subjective-judgment items ("工作正常"), no design-property items masquerading as checks (超时阈值是设计属性，靠常量核验，不是靠等待)
2. **Environment alignment** (the #1 source of false results):
   - Ports: read from `config.json` / docker-compose / application.properties, not guessed（5432 postgres、8443 fineract、5005 JDWP——but verify, don't assume）
   - Process location: fineract 用 `lsof -tnP -iTCP:8443 -sTCP:LISTEN`（**禁止** pgrep gradle——Gradle 客户端 PID 不是应用）；postgres 用 `docker ps --filter name=abnk-pg`；"新代码生效" = 重启后 `logs/fineract.log` 出现 `APACHE FINERACT IS READY` 且时间戳晚于源文件 mtime——禁止凭"接口能访问"判定（旧进程也能访问）
   - API paths and query params: `grep` the actual Controller or 对照 `fineract.json` 静态 spec（注意：同名作业三套命名 LOAN_COB/LA_ECOB/LOAN_CLOSE_OF_BUSINESS 这类映射坑，spec 没写的以源码/E2E 代码为准）
   - Log capability: does the process actually emit the logs the step reads?（fineract 日志在 `logs/fineract.log`（nohup 重定向）；postgres 用 `docker logs abnk-pg`——别读错通道）
   - Test runner: 单测/集成 = `./gradlew ... :test` 系命令；E2E = `fineract-e2e-tests`（Cucumber）——命令与仓库实际运行器一致；`devRun` 禁用了 testClasses，跑测试须独立 gradle 任务
   - HTTPS/鉴权: curl 一律 `-k`；业务端点带双头；漏租户头 = 4xx
3. **Task-boundary timing**: the step must pass using ONLY the current task's deliverables — a step that requires a later task's changes will always fail now
4. **Step ordering**: 编译门槛 → 静态 → 进程 → 运行时/API → DB 观测. Steps depending on artifacts of earlier steps (e.g., curl 先于服务 READY 检查) come after them
5. **Verification-iron-rule compliance**: "new code is live" requires READY 日志时间戳 vs 源文件 mtime，或 curl 一个带新代码标记的端点——never "I restarted and it works"（旧进程/旧产物同样能响应）

### Step 4: Fix with Full-Sweep Synchronization

When fixing any finding:

1. Fix the primary location
2. `grep` the whole doc (and linked docs) for every token affected — paths, counts, cross-references ("已纳入任务 X.N 验收步骤 3")、task/step IDs — and synchronize
3. If a check cannot be made executable, move it out of 执行和验收步骤 into a design-attribute note
4. Re-verify the fix itself (e.g., after replacing an endpoint path, `grep -c` to confirm zero stale-path remnants)

### Step 5: Report

Output a structured report:

| Section | Content |
|---------|---------|
| Findings table | severity (P1 blocker / P2 must-fix / P3 should-fix / P4 polish) · dimension · problem · evidence (file:line or command output) · fix applied |
| Passed items | what was verified and held |
| Conclusion | five-dimension verdict + reminder that changes are uncommitted |

### Iteration Rule (再次检查)

On repeat invocations, do NOT just re-run the same checks. Each round picks the previous rounds' **blind spots**. Observed blind-spot progression (use as a checklist of candidate areas):

1. Code-fact verification (counts, signatures, schema, endpoint paths)
2. Acceptance-command environment alignment (ports, processes, HTTPS/auth headers, log channels, test runners)
3. Runtime-cycle realism (no-HMR 重启周期、首次编译时长、Liquibase 启动迁移耗时是否计入步骤) — the classic P1 that static review misses
4. Timing/ordering (task-boundary dependencies, step ordering, artifact reuse)
5. Internal sweep (bare steps without verification lines; design points added late vs verification steps; TC coverage mapping)
6. Self-consistency after fixes (labels, counts, cross-references in sync)
7. Format normalization (task ID scheme; step IDs embedding task ID; numbered section headings colliding with task IDs; assertion-only steps vs executable command steps; trio completeness per task; cross-doc stale task IDs after renumbering)
8. Prerequisites & environment (前置条件 section presence/structure——环境汇总表 completeness,
   判据 judgeability, 现状 inspection-backed vs assumed, 分层放行 coverage; test-isolation
   declarations——psql 手工改数的恢复方案、破坏性命令（volume rm / compose down / clean+删缓存）是否
   标注需用户确认、JDK 25 门槛声明; temporary env changes without paired restore commands)

Stop when a full pass yields no new findings.

---

## PhaseX Document Authoring Requirements (the review rubric)

A Phase doc is review-complete only if it satisfies ALL of:

### Task ID & Heading Rules（编号与章节标题）

- **Task IDs derive from the Phase number + sequential suffix**（任务号 = Phase 号.序号——ABNK
  Phase 编号深度可变（`1` / `2.1` / `2.1.3`），任务号随之（`1.1` / `2.1.1` / `2.1.3.1`）。
  两条硬规则：① 任务号必须以 Phase 号为前缀（独立序号为 P2，renumber 不只是加注）；② 同一
  文档内任务号不得与任务标题之外的正文章节号冲突。
- **Step IDs derive from task IDs**: `V<任务号>.<步骤序号>`（任务号 + 步骤序号）. A step ID that does
  not embed its task's current ID is a consistency failure; after renumbering, `grep` the doc for
  stale step IDs.
- **Section headings carry NO numeric prefixes**（`## 背景与动机` not `## 1. 背景与动机`）——numbered
  headings collide with task IDs and stale `§N` cross-references. In-doc references to other
  sections use **section names**（「调研验证证据」节）or links, never `§N`.
- **Cross-doc ID sync**: after any renumbering, `grep` the linked docs（同 Part 的 `*Plan.md` 进度概要、
  adjacent Phase docs、总体设计文档、planning 规划文档）for old task IDs and update in the same sweep.
  Task titles must be verbatim-identical（modulo ID prefix）between Plan and PhaseX doc.

### Plan Doc（主计划）Format Rules

- The Plan doc's task section is titled **「进度概要」**（not 任务分解）and uses a **single merged
  table** with columns `| Phase | 任务 | 状态 | 交付物 |`:
  - Phase-level row: `| **[Phase N](./link)** | **主题** | 状态文字 | 概述 |`（doc link in the
    Phase column, status with text, deliverable = phase-level summary）
  - Task rows: empty Phase column + `任务 N.M:` prefix + bare status symbol
- Per-Phase `###` sub-tables under「任务分解」are legacy format——flag and convert（收口历史 Plan 不强制追溯）.

### Task Decomposition Rules

- Each task has a **purpose statement** in the form: current problem → what this task does → achieved effect (~2 sentences, concise but specific)
- Each task has the **trio, in order**（缺任一为 P2 finding）：
  1. **`#### 改动详情`** — new/modified file list（`**新建文件**` / `**修改文件**`），file paths first;
     **verification scripts and test files the steps depend on MUST be declared here**（步骤引用
     未声明脚本 = P2——先写验收命令、再写实现，验收命令即脚本的契约）
  2. **`#### 交付物`** — deliverables list（file paths preferred; capability description only when no
     file evidence exists yet——never invent paths）
  3. **`#### 执行和验收步骤`** — the task's step list（标题即信号：执行与验收不可分离——never just
     "执行步骤" or "验证步骤"）; every step is an executable command + expected output (see
     Acceptance Step Format below), never "acceptance criteria" as prose（**历史已执行文档不追溯**：
     标题要求适用于进行中/新建 Phase 文档；对已收口文档的「验证步骤」标题不要求追溯改写）
- Global **execution rules** at the top of the decomposition section stating:
  1. Steps are mandatory — run and record actual output; no skipping; compilation-pass or code-eyeballing never counts as pass
  2. **Sequential order with task gating** — tasks execute in ID order; **the next task may not
     start until the current task's steps all pass AND are checked off**; any step failing means
     stop; after fixing, re-run from that step.（Parallel-execution allowances inside a Phase are
     NOT permitted in the rules text; if work is parallelized in practice, the doc still records
     sequential gating.）
  3. **步步有验收** — every step is immediately followed by an executable verification action
     (验证动作/验证命令 + 期望输出); a step without an executable verification action may NOT be
     checked off; actual-vs-expected is the only pass criterion; probe/exploration steps 的验收 =
     实测记录归档 + 表格填写（no blank cells）
  4. **Placeholders declared once**（`$FINERACT` / `$TENANT` / `$AUTH` / `$PSQL` …）with concrete
     resolution in the rules block（including test-isolation conventions——psql 手工改数须声明所属库
     与恢复方案；破坏性命令须标注执行前问用户；JDK 25 依赖须声明判定方式）
  5. **状态标注** — 任务状态在执行前为"⏳ 待执行"，全部步骤通过后改为"✅ 已完成"
  6. **编译重启铁律** — 任何 Java 代码改动后必须 `./gradlew :fineract-provider:classes`
     （禁用系统 gradle，一律仓库 wrapper）+ 按端口 kill（`lsof -ti:8443 -sTCP:LISTEN | xargs kill`）
     + `nohup ./gradlew devRun` 重启 + 等日志 `APACHE FINERACT IS READY` 再验证；重启后以 READY
     时间戳晚于源文件 mtime 确认新进程新代码，再执行验证命令；涉及 schema 改动时重启即触发
     Liquibase 迁移，验收须含 changelog 账本核对（`databasechangelog` 表新行）

### Prerequisites Section Rules（前置条件——新建/进行中 Phase 文档强制）

Every new/in-progress Phase doc MUST contain a top-level **`## 前置条件`** section (before
背景/任务分解), proving "can this Phase even run" before any step executes. Missing the
section entirely is a **P2 finding** for docs whose steps consume running services, databases,
or build toolchains; closed historical docs are NOT retro-fitted. Required structure:

1. **环境汇总表 at the top** — one indexed overview table answering "本轮执行将使用什么
   环境/数据" at a glance. Columns: `维度 | 本轮使用 | 状态 | 作用`. Must cover at least:
   代码基线（fineract 分支/HEAD、abnk-system 状态）、JDK 25 toolchain、postgres 容器与端口
   （abnk-pg :5432）、fineract 进程与端口（:8443/JDWP :5005/启动形态 devRun）、数据库与 Liquibase
   状态（两库 + changelog 账本水位）、凭据（Basic Auth/租户头）、测试基线.
   The summary table is an **index** (what), pointing to the itemized tables for how——narrative
   duplication between summary and detail rows is a P3 finding（single source of truth per fact:
   汇总表=what，明细表=判据，正文节=口径定义）.
2. **Itemized precondition groups**（P0 环境（JDK 25/Docker/gradle wrapper）/ 进程与端口 /
   数据基线（Liquibase 水位/测试数据）/ 鉴权凭据——grouping by when/what, naming free）——each row
   is a precondition with a **judgeable 判据**（命令 → 期望输出）and a **现状** column. 现状 MUST
   come from actual inspection（`docker ps` / `lsof` / `ps` / `psql` / `ls`——executed at review
   time）, never assumption; items not yet created are marked ⬜ with the creating step referenced
   （创建动作内嵌验收步骤，不设独立准备任务——unless truly standalone）.
3. **前置条件门槛**（分层放行）——which task/step classes require which precondition groups
   （e.g., 纯代码/编译步骤只需代码基线 + JDK 25；API/运行时步骤需 postgres + fineract 全就位；
   涉及租户库 `fineract_tenants` 的步骤须单独标注）; precondition items themselves do not get
   independent acceptance steps (their 判据 run inside the steps they gate); a failed precondition
   assumption mid-execution = stop that step, fix prerequisite, re-run（不推翻任务边界）.
4. **已知环境坑必须在相关行携带**（verify still true at review time）：
   - JDK 25 缺失时 Gradle 会尝试自动下载 toolchain（网速差时表现为莫名其妙的构建错误而非清晰的
     版本报错）——前置条件必须实测 `java -version`
   - Liquibase 迁移随启动执行——**绝不中途 Ctrl-C**（破坏 changelog 账本导致下次启动失败）；
     首次完整编译 15–30 min，涉及首次启动的步骤须声明等待判据（日志 `APACHE FINERACT IS READY`）
   - 构建产物损坏坑（VS Code Gradle 扩展后台构建截断 jar + build cache 还原）——症状是运行中
     实例突然 500 `ClassNotFoundException`；处置命令 `./gradlew --stop && ./gradlew clean &&
     rm -rf ~/.gradle/caches/build-cache-1` 须可出现在相关步骤
   - Gradle fork JVM——停机一律按端口 kill；`nohup ./gradlew devRun` 记录的 PID 是客户端
   - compose 项目名 `abnk-system` 固定——`docker compose down` 会按项目名清容器，误在他项目
     deploy/ 目录执行会误停 aos 等容器；数据卷删除（`rebuildCommand`）是破坏性操作，执行前必须问用户
   - 临时环境改变（`--debug-jvm` JDWP、psql 手工造数、配置开关如 business date）配对恢复命令
     （同 Verification Iron Rule）

### Database & Naming Rules（ABNK 适配版）

- abnk 为 **Liquibase 双库演进**（`fineract_tenants` 租户存储库 + `fineract_default` 默认业务租户库，
  changelog 位于 `fineract/fineract-provider/src/main/resources/db/changelog/`，master 文件
  `db.changelog-master.xml` include 链）——不适用 per-Phase 建库或 Flyway $VNEXT 规则，但以下硬规则适用：
  - **changelog include 完整性**：新增 changelog 文件必须被 master（或其 include 链）引用——
    `grep -rn '<include' db/changelog/` 核实；孤立 changelog = 改动永不生效（P2）
  - **引用历史表/列的声明**（"沿用 m_client 的 X 列"）须与实际 changelog 或 psql `\d` 实测对得上
    （`grep` 核实）；表命名遵循 Fineract 既有约定（`m_` 前缀、蛇形命名）；修改既有表结构须新增
    changeset 而非改历史 changeset（Liquibase 账本不可回写）
  - **数据与 schema 分离**：Liquibase 只管 schema 与种子数据；验收步骤中手工 DML（造数/改数）须
    声明所属库、影响范围与恢复方案；`databasechangelog` 表是迁移账本，验收 schema 变更时核对新行
    （`docker exec abnk-pg psql -U root -d fineract_default -tAc "SELECT id FROM databasechangelog ORDER BY executed_at DESC LIMIT 1"`）

### Acceptance Step Format

```
- [ ] **V<任务号>.<步骤序号>**（层级·检查点）：动作描述
  - 验证动作：<可执行命令，或探查类步骤的"实测记录归档 + 表格填写"动作>
  - 期望输出：<可判定的通过判据>
```

- **Every step line MUST be immediately followed by verification lines**（验证动作/验证命令 +
  期望输出——naming may vary, but both must be executable and judgeable）; a bare step line with
  no verification is a review finding
- **Step ID embeds its task ID**（`V2.1.3.1` = 任务 2.1.3 步骤 1）——renumber 后旧 ID 残留为 P3
- Implementation-only steps (write code) still need a verification action —
  `./gradlew :fineract-provider:classes`（编译门槛）/ `./gradlew :fineract-provider:test`（单测）
  / curl + psql assertions（行为）
- Probe/exploration steps: the expected-output side is a recorded command+output（实测记录归档）; any matrix/table cell they feed must be filled — no blank cells
- 层级 ∈ {编译门槛, 静态, 进程, 运行时, API, DB}（未来接入前端后追加「界面」层）and steps are
  ordered by that layering
- **Every step is an executable action, not a descriptive assertion**（P2 if violated）——a step
  must state a runnable command（`./gradlew <task>` / `grep -c '<pattern>' <file>` / `curl -k ...` /
  psql SQL）plus the concrete expected output（exact counts, `UP`/`READY` 日志行、comparison
  operators with thresholds）. Assertion-only prose（"结果与全量一致" without the command that
  produces the comparison）must be rewritten into command form; if the verifying script does not
  exist yet, declare it in 改动详情 and write the step against it（先写验收命令、再写实现——验收命令即
  脚本的契约）.
- Commands reference placeholders declared once (`$FINERACT` = `https://localhost:8443/fineract-provider`、
  `$TENANT` = `Fineract-Platform-TenantId: default`、`$AUTH` = `Authorization: Basic bWlmb3M6cGFzc3dvcmQ=`、
  `$PSQL` = `docker exec abnk-pg psql -U root -d fineract_default`) with their concrete resolution
  （port 与路径出处：config.json / application.properties / docker-compose.yml）
- grep patterns match semantics, not style（Java import 顺序、常量折叠、lambda 写法）
- curl steps assert full response shape（status + body markers，如 `"totalFilteredRecords":<N>`），
  not just HTTP 200；业务端点必须 `-k` + 双头；DB 观测步骤指名精确表名与 psql 查询，并区分
  `fineract_default` 与 `fineract_tenants`
- 等待类步骤（首次编译/Liquibase 迁移）须给判据（日志 READY 行 + 超时上限），不是"耐心等待"

### Verification Iron Rule (落地为步骤，不是口号)

- Compile → restart → verify, with process-confirmation steps（READY 日志时间戳 vs 源文件 mtime；
  `lsof -ti:8443 -sTCP:LISTEN` 确认监听进程存在）
- Gradle daemon 状态与构建缓存的干扰纳入确认（产物损坏处置三连 `--stop` / `clean` / 删 build-cache，
  仅在出现对应症状时执行）
- Any temporary environment change（JDWP `--debug-jvm`、docker 容器重建、psql 手工改数、配置开关
  如 business date / c_configuration）has a paired revert/restore command in the same step
- 破坏性命令（`docker volume rm`、`docker compose down`、`./gradlew clean` + 删全局缓存）一律
  标注"执行前问用户"

## When to Stop and Ask

1. The doc references code/repos/branches not present in the workspace（fineract = develop 分支）
2. A fix would require changing code (not docs) — propose, don't implement during review
3. Two linked docs disagree on something only the user can arbitrate (e.g., scope boundaries)
4. A round finds ≥3 P2 findings — report first instead of silently rewriting large sections
5. 任何验收步骤的修复需要执行破坏性命令（数据卷删除/容器重建/全局缓存清理）——问用户，不代决
