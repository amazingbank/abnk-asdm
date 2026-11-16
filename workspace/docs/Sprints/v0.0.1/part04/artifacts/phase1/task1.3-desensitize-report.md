---
sprint: v0.0.1
part: part04
phase: 1
status: completed
date: 2026-11-16
evidence: ../
locale: zh-CN
---
# 任务 1.3 —— 脱敏终审报告（ADR-010 衍生约束门）

- 日期：2026-11-16；执行人：AI（abnk-debugger 会话）
- 终审对象：`$PORTAL/src/data/` 拟发布数据集（sync 复制产物 29 MB + index/metrics 生成物）——将随 public 仓（abnk-devportal）与 ghcr 公共镜像公开
- 通道：机械（`check-bilingual.sh --credentials` 全量）+ 人工（分层抽样通读）；通过是 Phase 2/3 消费该数据集的前置门（发版铁门口径）
- 前置复验（终审前）：abnk-asdm porcelain = 0；`$PORTAL/src/data/` 数据集在位（index/planning/sprints + 契约样例）

## 一、机械通道全量（V1.3.1）

- 命令：`bash $ABNK/scripts/check-bilingual.sh --credentials $PORTAL/src/data; echo exit=$?`
- 结果：**exit 0——「违规总数: 0，✅ 全部通过」**（口令/token 字面量、PAT/JWT、私钥块、密钥形态文件、公网 IP、`.github-private` 内容泄漏六类零违规）
- 抽检信息（不阻塞，供人工复核，逐条裁决见 §二/§四）：
  - 版本号上下文 IP 豁免 3 处（`37.2.13.0`）
  - `.github-private` 路径引用 83 处合法形态（内容泄漏由字面量模式拦截，零命中）

## 二、IP 轻规则抽查（V1.3.2，ADR-010 衍生约束 5）

命令：`grep -rnoE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' $PORTAL/src/data | grep -vE ':(10|127|0)\.|:192\.168\.|:172\.(1[6-9]|2[0-9]|3[01])\.'` → 残余命中 3 条，逐条人工裁决：

| # | 命中（文件:行） | 上下文 | 裁决 | 处置 |
|---|---|---|---|---|
| 1 | `part02/artifacts/phaseP1/taskP1.1-toolchain.txt:12` | `Emulator version 37.2.13.0 (build_id 16740729)`（flutter doctor 原始输出） | 语义化版本号误报（Android Emulator 版本，非 IP 地址） | 豁免（与 Part03 V5.1.1/V6.2.8 既有裁决口径一致） |
| 2 | `part03/artifacts/phase5/task5.1-credential-scan.txt:21` | 表格自引记录 #1 的裁决本身（公网 IP 扫描结果行） | 语义化版本号误报（裁决记录自引） | 豁免 |
| 3 | `part03/zh-CN/v0.0.1-Part03-Phase6-Comments-Convention.md:179` | 叙事文本复述既有豁免口径 | 语义化版本号误报（叙事自引） | 豁免 |

**公网 IP 实际命中 0**（3 条命中全部为版本号类误报，标注后不计）。

## 三、人工抽样复核（V1.3.3）

分层抽样 6 文件（机械模式覆盖外的风险面导向：部署拓扑/运行时/多租户语境优先），人工通读复核（关注：拓扑细节中的操作性凭据、`.github-private` 内容泄漏）：

| # | 层 | 样本文件 | 复核发现 | 结论 |
|---|---|---|---|---|
| 1 | index | `index/sprint-v0.0.1.yaml` | 纯结构化元数据（doc/status/date/locale/evidence 相对路径/task 标题与 note）；无凭据、无 IP、无 token、无 `.github-private` 引用 | 通过 |
| 2 | metrics | `index/metrics-v0.0.1.json` | LOC/测试指标/blocked_items（source 为相对路径）/ci `not_run` 如实标注；无凭据、无 IP | 通过 |
| 3 | Sprint 文档（部署拓扑高风险） | `sprints/v0.0.1/part02/zh-CN/v0.0.1-Part02-PhaseP3-Integration-Deploy.md` | 生产凭据全部为占位符（`$PROD_HOST`/`$PROD_SSH`/`$PROD_COMPOSE`）；口令/JWT secret/PAT 均只提 `.github-private` 路径无值；容器内网 IP `172.18.0.6` 与回环 `127.0.0.1:3322` 属 RFC1918/loopback 排除面；历史 IP 泄漏已在 VP3.5.1 敏感审计清除为占位符（文档在案）；token 仅出现长度描述（187 字符）无值 | 通过 |
| 4 | Sprint 文档（运行时语境） | `sprints/v0.0.1/part03/zh-CN/v0.0.1-Part03-Phase7-Runtime-Data-Locale.md` | mock 数据集运行时切换叙事；无凭据、无 IP、无 `.github-private` 引用 | 通过 |
| 5 | 测试报告 | `sprints/v0.0.1/part02/Phase2Results/zh-CN/v0.0.1-Part02-PhaseP2-Test-Report.md` | 敏感口径节在案：演示口令 6 个真实值全证据 grep 0 命中、报告 token 字段一律 `<redacted>`；`mobileNo 135******01`、`documentKey ID-A********347` 均脱敏形态；口令仅 `.github-private` 路径引用无值；端口叙述（:8080/:8081/:5433）非 IP | 通过 |
| 6 | 证据索引 | `sprints/v0.0.1/part04/artifacts/phase1/task1.1-generator-report.md` | 生成器首跑报告；MD5 哈希为产物完整性记录（非凭据）；pip 安装记录无凭据 | 通过 |

抽样 6/6 通过，无空单元格。

## 四、豁免口径声明

| 豁免项 | 数据集分布 | 豁免依据 |
|---|---|---|
| `mifos:password`（含 base64 形态 `bWlmb3M6cGFzc3dvcmQ=`） | 10 + 2 处（part01/part02/part04 文档叙事 + planning 文档 + 既有扫描证据自引） | Fineract **上游公开默认凭据**（Apache Fineract 官方 demo 默认值，非本组织真实凭据，仅限本地调试语境）——ADR-010 与 Part03 任务 5.1/V6.2.8 既有豁免口径一致 |
| `<redacted>` 标记 | 15 个文件（part02 gateway/gap 报告 JSON + 证据 txt + 文档） | token 脱敏标记本身——报告生成侧已脱敏（P2.7 口径），标记为豁免形态非泄漏 |
| 版本号上下文 IP 豁免 | 3 处（§二表） | 语义化版本号（Android Emulator `37.2.13.0`），非 IP 地址 |
| `.github-private` 路径引用 | 83 处 | 全部为路径根引用形态（敏感件存储位置叙事，内容不入公开数据集）——门禁口径：路径引用合法、内容泄漏违规（后者零命中） |
| 本机绝对路径（`/Users/leixu/...`，占位符解析值） | Part 文档占位符声明节（既有书写惯例） | 环境叙事非操作性凭据（不可用于访问任何系统）；机械门（V6.2.8 全树 / 本次 V1.3.1）均不计违规；ADR-010 保密边界针对凭据/密钥/内网可达拓扑，本机开发路径不在边界内 |

## 五、终审结论（Phase 2/3 前置门声明）

- 机械通道 exit 0（违规 0）+ IP 轻规则公网命中 0 + 人工抽样 6/6 通过 + 豁免口径全部在案声明——**脱敏终审通过**。
- **本数据集（`$PORTAL/src/data/` sync 产物 + `workspace/index/` 生成物）可作为 Phase 2/3 消费对象**——Phase 2（内容层）/Phase 3（站点层）据此开工，无需重复脱敏（新增素材在 Phase 4 发布前按 abnk-prod-deploy Step 0 敏感审计门复跑，铁律不豁免）。
- 数据时点注记：`workspace/index/` 生成物为 2026-11-16 任务 1.1 时点快照（任务 1.2/1.3 状态行彼时为 pending 属数据时点演进，非敏感问题）；Phase 2/3 消费前重跑生成器即刷新至当前态。
