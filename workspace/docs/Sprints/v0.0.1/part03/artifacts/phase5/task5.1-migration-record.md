# 任务 5.1 · artifacts 跨仓迁移记录

## 来源与基线

| 项 | 值 |
|---|---|
| 来源仓 | abnk-system（`/Users/leixu/source/asdm/amazingbank-ws/abnk-system`） |
| 来源 HEAD | `bd3cf62`（fix(gateway,bo): 错误响应补 CORS 回显 + LoanOpsPage 静默失败修复，2026-11-13） |
| 迁移执行日 | 2026-11-16 |
| 落点仓 | `.asdm` HEAD `3213125`（D9 修订批已提交，两仓工作区干净——已知坑 10 已解除） |
| 执行方式 | `cp -R` 纯增量复制 + 来源 hash 记录（**跨仓不保历史，有意取舍**——见「取舍声明」） |

## 分桶映射与守恒计数

| 源（abnk-system/artifacts/ + 工作区根） | 目标（$SPRINTS = `.asdm/workspace/docs/Sprints/v0.0.1/`） | 源实测 | 落点实测 |
|---|---|---|---|
| `phase1/` | `part01/artifacts/` | 3 | 3 |
| `phaseP0/` | `part02/artifacts/phaseP0/` | 6 | — |
| `phaseP1/` | `part02/artifacts/phaseP1/` | 37 | — |
| `phaseP2/` | `part02/artifacts/phaseP2/` | 10 | — |
| `phaseP3/` | `part02/artifacts/phaseP3/` | 148 | — |
| 工作区根 `p3-*.yaml` | `part02/artifacts/phaseP3/` | 7 | — |
| part02 小计 | | 201+7=208 | 208 |
| `part03/`（phase1–4/7 + poc-journey + seed-en） | `part03/artifacts/`（phase5 为本任务新证目录，不计入守恒） | 124 | 124 |
| 根 `README.md` | `../artifacts/README.md`（Sprint 级兜底，按新路径更新引用） | 1 | 1 |
| **总计** | | **329 + 7 = 336** | **336** |

守恒判据执行：`find` 逐桶计数（part03 桶计数显式排除 phase5 本任务新增证据目录）——
`part01=3`、`part02=208`、`part03=124`、`test -f $SPRINTS/artifacts/README.md` 通过。

## 凭据扫描门结果（V5.1.1）

详见同目录 `task5.1-credential-scan.txt`：主扫描 100 处命中逐条裁决全部为叙事/label/错误消息/
配置键名/mock 原型口令/占位符/路径引用形态（JWT 字面量 0、公网 IP 0、`.github-private` 内容
引用 0），**违规 0，无需脱敏**，336 文件全量放行。

## p3-*.yaml 散件处置（V5.1.3）

7 件快照拷贝入 `part02/artifacts/phaseP3/`；源文件（非 git 管理）保留至任务 5.3 清扫时删除
（已知坑 3——避免双份各自演化，删除前以源为审校对象）。

## 取舍声明（跨仓不保历史——已知坑 4）

`git mv` 不适用跨仓迁移；本迁移采用**复制 + 来源 commit hash 记录**。理由：证据文件是执行
快照非演进代码，blame 需求近乎为零，subtree/filter-repo 的工序成本远超历史价值。与 workspace
侧逐目录 `git mv`（R100 保 blame 链，任务 5.2）是**两种不同口径**，勿混用。

## 回滚预案

纯增量拷贝——删除目标侧（`$SPRINTS/part01/artifacts`、`$SPRINTS/part02/artifacts`、
`$SPRINTS/part03/artifacts` 拷贝内容、`$SPRINTS/artifacts/README.md`）即完成回退；
源侧 abnk-system 零改动（V5.1.5 判据）。
