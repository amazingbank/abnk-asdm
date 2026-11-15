# 任务 5.3 · 三面引用大清扫执行证据

执行日：2026-11-16；执行前基线：A 面 9 处文件级 + B 面 72 处（判据一 14 + 判据二 58）+ C 面 11 处输出路径（实测 8 处文本 + 2 处 .pyc 编译缓存 + 1 处 docs/README 复核为 0）。

## A 面（workspace 旧路径 → 含 zh-CN 段新路径）

| 位置 | 旧 | 新 |
|---|---|---|
| toolsets INSTALL.md:55/82 | `part01/...Phase1-*.md` | `part01/zh-CN/...Phase1-*.md` |
| toolsets abnk-doc-review.md:23 | `Sprints/**/v*-*-PhaseN-*.md` | `Sprints/**/zh-CN/v*-*-PhaseN-*.md` |
| toolsets abnk-doc-review.md:61 | `part01/v0.0.1-Part01-Phase1-XXX.md` | `part01/zh-CN/...` |
| toolsets abnk-prod-deploy.md:174 | `<version>/release-note.md` | `<version>/zh-CN/release-note.md` |
| part02 PhaseP3:247/273 | `<version>/`、`fullstack-0.1.0/` | 插入 `zh-CN/` 段 |
| part02 PhaseP1:121 | `adr/009-flutter-mobile.md` | `adr/zh-CN/009-flutter-mobile.md` |
| ReleaseNotes 0.1.2:54 | `02-architecture/website-i18n-fonts.md` | `02-architecture/zh-CN/...` |

- 跨目录相对链接（ADR-010）：7 处（part04 5 文档 + part03 Phase5:4 + **Part03-Plan D9 行:57——方案 7 处基线的完整构成**）
  `](../../../planning/abnk-design/adr/010-repository-openness.md)` → `](../../../../planning/abnk-design/adr/zh-CN/010-repository-openness.md)`
- 跨 Part 承接方引用 4 处：part01→part02（2）与 part03→part04（2），`../partN/` → `../../partN/zh-CN/`
- `.asdm/README.md`：目录树 workspace 段同步叶子层结构（Sprints/modelB/zh-CN 布局）+ ADR-010 链接插 zh-CN

## B 面（artifacts 跨仓引用 72 处 → Part 内相对路径）

- part02 树 5 文档：`` `artifacts/phaseP `` → `` `../artifacts/phaseP `` + PhaseP0:311 完整形态 → `../artifacts/...`
- part02/Phase2Results：→ `../../artifacts/...`（嵌套目录 +1 深度）
- part01 树：`abnk-system/artifacts/phase1/` → `../artifacts/`（无 phase1 子层直达）+ 断链修复 1 处（见下）
- part03 树 6 文档：`abnk-system/artifacts/part03/` → `../artifacts/`；Phase6:71 backtick → `../artifacts/`
- planning/06-evolution：2 处 → `../../../../../docs/Sprints/v0.0.1/part01/artifacts/`
- sre/fullstack-0.1.0：1 处 → `../../../../../docs/Sprints/v0.0.1/part02/artifacts/phaseP3/`
- part02 PhaseP0:157 漏网 1 处（判据二复跑捕获）：`` `artifacts/phase1/report-<ts>.json` `` → `` `../../part01/artifacts/report-<ts>.json` ``（跨 Part）

## C 面（abnk-system 源切换）

- `git rm -r artifacts`：326 tracked 删除 + 物理清理 gitignore 排除残留（.DS_Store 2、flutter-run.log 2、__pycache__ 3 目录）
- 工作区根 `p3-*.yaml` 7 件源文件删除（已知坑 3 收口）
- `README.md`：artifacts 表格行删除→指向 `.asdm` 新位置 + 入库纪律段两段式改写
- `scripts/prodform/probe_poc.py`、`tests/{smoke,poc,gateway}/*.py`、`tests/README.md`：docstring 注释 + 代码输出路径（`REPORT_DIR`/`ART`/`art_dir`）改本地 `output/`（各自脚本目录）+ 收口归档路径声明
- `.gitignore`：追加 `scripts/**/output/`、`tests/**/output/` 排除（保留 artifacts 旧规则防再生成）

## 断链修复（迁移前即断链，按实际证据位置改写）

1. part01 Phase2-Custom-L1:147：`abnk-system/artifacts/phase2/task2.1-wiring-evidence.txt`（从未存在）
   → `../../part02/artifacts/phaseP0/taskP0.5-wiring-evidence.txt`（实际证据位置，122 行移交记录印证）
2. planning/00-baseline fineract-codebase.md:22/103：`count-loc.sh` 同目录链接（5.2 未迁移非 md 脚本导致断链）
   → `../count-loc.sh`（V5.3.4 全验捕获并修复——叶子层迁移真实断链的唯一实例）

## 判据口径修正声明（执行中发现并修正，非静默）

1. **V5.3.1**：原判据 grep 源含 `$ASDM/workspace` 整树——任务 5.1 已将证据拷入 `partXX/artifacts/`，证据 md 内路径快照不改写（V5.3.2 豁免 ① 同族口径），执行口径补 `--exclude-dir=artifacts`；`-v` 排除模式三示例（partXX/abnk-design/ReleaseNotes 的 zh-CN）未覆盖分区子目录（`adr/zh-CN`、`02-architecture/zh-CN`）与 glob（`Sprints/**/zh-CN`）合法新形态，执行口径扩展为 `/zh-CN/` 全形态豁免。终版判据 0。
2. **V5.3.5**：判据模式 `^[+-][^+-]` 对列表形态变更行（diff 输出 `-- Path...`）漏检，且删除行（旧路径）天然不含 zh-CN——按判据意图「无内容性改动混入」执行口径：**+ 行不含 zh-CN 计数 = 0** + 5 对 -/+ 配对均为纯 `zh-CN` 段插入（人工核对 8+2 行 diff）。toolsets 内容零改动（D4「内容不动」延续）。
3. **V5.3.4**：105 处检查 = 85 OK + 2 GLOB-OK（INSTALL glob 契约有效）+ 4 PLACEHOLDER（`<version>/<ts>` 模板）+ 8 PLAN-TEXT（part01 phase2 历史移交任务的未来归档位计划文本，非现存证据）+ 6 DESIGN-TEXT（Phase5 判据省略号示例 + doc-review 模板 `./link`）+ **真实失联 0**（count-loc.sh 2 处断链已修复）。检查脚本入库：`.asdm/scripts/ref-check-v534.py`。

## 判据输出汇总

| 判据 | 输出 | 期望 | 结果 |
|---|---|---|---|
| V5.3.1 A 面（终版口径） | 0 | 0 | ✅ |
| V5.3.2 B 面判据一 | 0 | 0 | ✅ |
| V5.3.2 B 面判据二 | 0 | 0 | ✅ |
| V5.3.3 删除计数 | 326 | ≥326 | ✅ |
| V5.3.3 源目录消亡 | OK | OK | ✅ |
| V5.3.3 p3 源文件 | 0 | 0 | ✅ |
| V5.3.3 scripts/tests 残留 | 0 | 0 | ✅ |
| V5.3.4 失联引用 | 0（真实断链口径） | 0 | ✅ |
| V5.3.5 toolsets 纯路径 | +行 0 例外、5 对纯插入 | 0 | ✅ |
| V5.3.6 出界甄别 | 12 文件全部自身/第三方指向 | 零跨仓 | ✅ |
