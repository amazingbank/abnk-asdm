# ASDM Action: ABNK Check Bilingual (三合一防回潮门)

## Metadata

```json
{
  "guid": "f7a8b9c0-1d2e-4f3a-9b4c-5d6e7f8a9b0c",
  "name": "abnk-check-bilingual",
  "displayName": "ABNK Check Bilingual",
  "description": "Three-in-one regression gate for the Amazing Bank (ABNK) repos: ① bilingual comment check on channel sources（触碰/增量源码，中文在上、英文语义重写在下——同行 `中文 | English` 或相邻行两形态均合法，行内 noqa-bilingual 豁免）；② front-matter structural check on workspace markdown（创作 md，排除 artifacts/ 与 modelB/ 与 index/——首行 `---`、YAML 可解析、三 profile 必填字段，与 Phase 5 注入脚本共用校验口径）；③ credential scan on public evidence（ADR-010 衍生约束 2/5——口令/token/密钥字面量、GitHub PAT/JWT 字面量、私钥块、密钥形态文件、公网 IP 字面量抽检口径；`.github-private` 路径引用合法、内容泄漏违规）。Violations > 0 → exit 1.",
  "toolset": {
    "guid": "b7a2c9d1-4e3f-4a58-9c6b-1d2e3f4a5b6c",
    "id": "abnk-harness-toolset",
    "name": "ABNK Harness Toolset",
    "version": "0.1.2"
  },
  "scenario": "防回潮门禁"
}
```

## Overview

规范只存在于文档规则里会随增量开发回潮（Part03 Phase 6 方案要点）。本 action 把三项「文档约定」升级为「可执行门禁」，脚本本体为 `abnk-system/scripts/check-bilingual.sh`（bash + `set -euo pipefail`，macOS bash 3.2 兼容，风格对齐 `count-loc.sh`）：

- **① 注释双语（默认模式）**：对 `channels/{backoffice,mobile-banking}` 的触碰/增量源码跑注释双语门禁——存量未触碰文件不追溯（Plan 总体口径），存量渐进策略随 CI 首版由用户拍板。
- **② front-matter（`--frontmatter <workspace路径>`）**：对 `.asdm/workspace` 创作 md 跑结构化元数据门禁——Phase 5 注入资产的防漂移检查。
- **③ 凭据扫描（`--credentials <evidence路径>`）**：对公开证据（Part 桶 evidence）跑 ADR-010 公开资产纪律常驻门。

## Input

- 默认模式：一个或多个 `<目录|文件>`（目录遍历时排除构建产物与 `node_modules`，仅扫源码扩展名；显式文件不做扩展名过滤——清单语义，调用方负责范围）
- `--frontmatter`：workspace 目录路径（如 `.asdm/workspace`）
- `--credentials`：evidence 目录/文件路径（如 `.asdm/workspace/docs/Sprints/v0.0.1`）

## Output

- markdown 违规表（`文件:行号:内容`）+ 各模式违规数 + 违规总数 + 抽检信息（凭据模式）
- 退出码：`0` = 通过；`1` = 存在违规；`2` = 用法/目标错误

## 判据口径

### 模式一：注释双语（Judgment: bilingual comments）

- **注释形态识别**：`//`、`///`、`/*`、`/**`、`*`、`*/`、`#` 起始的行（行首空白容忍）。
- **块级配对判定**（与任务 6.1 审计矩阵口径一致）：连续注释行为一个块，遇非注释行断块；块内含 CJK 注释行时，须存在英文注释行（无 CJK 且含字母）位于最后一个 CJK 行**之后**。
- **两形态均合法**：形态 A = 同行 `中文 | English`（`|` + 空白 + 英文单词）；形态 B = 中文注释行在上、英文语义重写行紧随（语义重写而非逐字直译——决策 D2）。
- **行内豁免**：注释行含 `noqa-bilingual` 即豁免（罕见场景：引用原文名言/专名）。

### 模式二：front-matter（Judgment: front-matter structure）

- **创作树口径**：排除 `artifacts/`（证据语言无关、不注入 front-matter）、`modelB/`（外部资料）与 `index/`（生成器机器产物——Part04 引入，非创作 md）——与 Phase 5 注入脚本 `add-frontmatter.py` 口径一致 + Part04 数据管线产物目录演进。
- **三 profile 路由与必填字段**（共用校验口径）：
  - `sprint-doc`（`docs/Sprints/v*/part*/*`）：`sprint` / `part` / `status` / `date` / `locale`
  - `planning-doc`（`docs/README.md` 与 `docs/planning/abnk-design/*`）：`section` / `status` / `locale`
  - `release-note`（`sre/ReleaseNotes/*`）：`version` / `date` / `locale`
- **结构判据**：首行 `---`、50 行内闭合 `---`、元数据行可按 `key: value` 解析、必填字段非空；路径不可路由 = `UNROUTED` 违规。

### 模式三：凭据扫描（Judgment: credentials, ADR-010 衍生约束 2/5）

- **违规模式**：私钥块（`BEGIN ... PRIVATE KEY`）；口令/密钥赋值字面量（`password/secret/... : "..."` 形态，占位符 `<...>`、开发默认值 `mifos:password` 家族、`${...}` 环境变量引用、既有裁决家族豁免）；token 赋值字面量；GitHub PAT（`ghp_`/`github_pat_` 等形态）；JWT 字面量（`eyJ...` 三段式）；密钥形态文件（`*.key`/`*.p12`/`*.pfx`）。
- **IP 字面量抽检口径**：排除 RFC1918/回环/链路本地段后的公网 IP 字面量计违规；版本号上下文（`version`/`build_id`/`版本`/`Emulator`）豁免为信息项输出。
- **`.github-private` 边界**：路径引用合法（说明性提及），内容泄漏由字面量模式拦截；mentions 计数以信息项输出。

## Procedure

```bash
# 触碰面清单门禁（Phase 6 任务 6.1 落盘的清单为传参范围）
cd abnk-system && bash scripts/check-bilingual.sh \
  $(cat "$ASDM/workspace/docs/Sprints/v0.0.1/part03/artifacts/phase6/task6.1-filelist.txt")

# front-matter 全 workspace 门禁
bash abnk-system/scripts/check-bilingual.sh --frontmatter .asdm/workspace

# 凭据门禁（Part 桶 evidence）
bash abnk-system/scripts/check-bilingual.sh \
  --credentials .asdm/workspace/docs/Sprints/v0.0.1
```

## Notes

- **CI 接入**：`abnk-system/ci/README.md` 规划表已登记（触发：每次提交；范围：channels 两端触碰/增量源码）——workflow YAML 随 CI 首版落地（显式出界）。
- **不读取不修改**：`secrets.local.json` 等敏感件（工具集纪律）；凭据模式扫描的是公开证据面的泄漏，不接触私有仓内容本体。
- **md 内容双语不在此门**：front-matter 模式检查的是结构（非内容双语）；en-US 内容政策见 Phase 5 / Part04。
