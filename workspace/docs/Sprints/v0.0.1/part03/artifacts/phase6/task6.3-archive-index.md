# 任务 6.3 —— Part 03 归档索引清单（收口核验）

- 日期：2026-11-16；核验口径：全部归档子目录非空（存量 7 + 本 Part 执行新增 2，共 9 个子目录）；文件数实测 `find <dir> -type f | wc -l`
- 根目录：`.asdm/workspace/docs/Sprints/v0.0.1/part03/artifacts/`（D9 资产仓归一后的唯一事实源——abnk-system 侧不再承载过程证据）

## 子目录清单（9/9 非空 ✅）

| 子目录 | 文件数 | 性质 |
|---|---:|---|
| `phase1/` | 57 | 存量——Phase 1 走查/快照/审计（task1.x-walkthrough + snapshots 等） |
| `phase2/` | 10 | 存量——Phase 2 走查与数据集证据 |
| `phase3/` | 29 | 存量——Phase 3 l10n 七页走查（zh/en 记录 + 截图） |
| `phase4/` | 9 | 存量——Phase 4 fixtures 数据集走查（default/decouple 两轮） |
| `phase7/` | 4 | 存量——Phase 7 运行时数据集切换走查 |
| `poc-journey/` | 13 | 存量——KBank POC journey 走查报告与证据 |
| `seed-en/` | 2 | 存量——种子数据英文态证据 |
| `phase5/` | 7 | 本 Part 执行新增——Phase 5 资产归仓（迁移记录 + front-matter 报告 + 扫描报告） |
| `phase6/` | 38 | 本 Part 执行新增——Phase 6 收口（6.1 审计矩阵/清单、6.2 三合一门产出物、6.3 走查汇总 + 截屏） |

## phase6 目录内索引（本 Part 新增）

- 任务 6.1：`task6.1-bilingual-audit.md`、`task6.1-filelist.txt`、`.audit-pairing.py`（判定工具留档）
- 任务 6.2：`task6.1-filelist.txt` 为 V6.2.3 硬门传参（与 6.1 落盘同步）
- 任务 6.3：`task6.3-final-walkthrough.md`（V6.3.1 终检裁决 + V6.3.2/6.3.3/6.3.4 走查记录）、`task6.3-archive-index.md`（本文件）、`task6.3-bo-snapshots/`（22 件 playwright 快照）、`carrier-walkthrough/`（11 件截屏：web × 4 + ios 最终通过 run × 5 + ios 失败 run 过程件 × 2——`ios-04-home-zh-switched.png`/`ios-04-profile-zh-switched.png` 为 run 1/2 失败现场（断言页错位与 setLocale 重复选择短路），最终判据以 run 4 五张为准，保留作调试旅程证据）

## 收口结论

- Part 03 全部任务（Phase 1–7）状态 ✅，Plan `⏳` 计数 = 0（V6.3.5 判据实测通过）
- 挂账项：Android 载体走查（V6.3.4 段）——复验计划见 `task6.3-final-walkthrough.md`，不阻塞收口
