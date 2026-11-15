# 任务 5.2 · workspace 双语叶子层迁移实测证据

执行日：2026-11-16；执行方式：逐目录 `git mv`（`mkdir -p <目录>/zh-CN && git mv <目录>/*.md <目录>/zh-CN/`，已知坑 1 口径——不混入非 md 文件）。

## 基线（执行前实测）

| 项 | 值 |
|---|---|
| workspace tracked 总数 | 86（= 方案基线 79 + D9 批新增 part04 6 + ADR-010 1，均已随 `3213125` 提交） |
| tracked 创作 md（quotepath 关闭、排除 modelB） | 74（= 方案基线 67 + part04 6 + ADR-010 1） |
| sre png | 2（gateway0.1.2-bo0.1.2、gateway0.1.4-bo0.1.3 各 1） |

## 迁移面（逐目录实测）

| 树 | 目录 | md 数 |
|---|---|---|
| Sprints/v0.0.1 | part01 / part02 / part03 / part04 / part02/Phase2Results | 4+6+8+6+1 = 25 |
| planning/abnk-design | 根 README + 00-baseline/01-product/02-architecture/03-data-model/04-operations/05-domains/06-evolution/adr | 1+4+3+7+3+3+5+4+11 = 41 |
| sre/ReleaseNotes | 8 个版本目录各 1 release-note.md | 8 |
| **合计** | | **74** |

非 md 处置：`00-baseline/count-loc.sh` 不迁移（原地保留）；2 png → 各版本 `{版本}/artifacts/`。

## V5.2.1 判据输出

- `git status --porcelain | grep -c "^R"` = **76**（74 纯 R + 2 RM）——落在判据区间 69–76 上限：
  67（原 tracked 创作 md）+ 2（png）+ 6（part04，执行前已提交）+ 1（ADR-010，执行前已提交）；
  `git diff --cached -M --name-status` 中非 R100 计数 = 0——除 2 个 RM（Phase5/Plan 文档，
  RM = rename + 任务 5.1 勾选产生的 worktree modify，非历史链断裂）外全部 **R100 完美 rename**。
- `git -c core.quotepath=false status --porcelain | grep -c "^??"` = **5**，逐项列举：
  1. `Sprints/v0.0.1/artifacts/`（任务 5.1 新增，Sprint 级兜底 README）
  2. `Sprints/v0.0.1/part01/artifacts/`（任务 5.1 新增，3 文件）
  3. `Sprints/v0.0.1/part02/artifacts/`（任务 5.1 新增，208 文件）
  4. `Sprints/v0.0.1/part03/artifacts/`（任务 5.1 新增拷贝 124 + phase5 本 Phase 证据 2）
  5. `workspace/docs/README.md`（本任务新建，en-US 生长规则约定）
  ——part04 6 文档与 ADR-010 已提交为 tracked（计入 R 分母），不在 ?? 侧。

## V5.2.2–V5.2.4 判据输出

- V5.2.2：part03 下恰 `artifacts` + `zh-CN` 两目录；`part03/artifacts/zh-CN` 不存在；`modelB/zh-CN` 不存在；abnk-design 出界 md 计数 = 0。
- V5.2.3：三处抽验全部存在——`part03/zh-CN/v0.0.1-Part03-Plan.md`、`abnk-design/zh-CN/README.md`、`ReleaseNotes/0.1.4/zh-CN/release-note.md`。
- V5.2.4：`workspace/docs/README.md` 存在；`grep -c "doc id\|路径即"` = 2 ≥ 1。

## 回滚预案

反向 `git mv`（zh-CN/* → 原目录）+ 删除新建 README 即回退；rename 均已暂存（已知坑 9：暂存 ≠ 提交）。
