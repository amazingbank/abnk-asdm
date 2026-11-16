---
sprint: v0.0.1
part: part04
phase: 1
status: completed
date: 2026-11-16
evidence: ../
locale: zh-CN
---
# 任务 1.1 —— index/metrics 生成器首跑报告

- 日期：2026-11-16；执行人：AI（abnk-debugger 会话）
- 生成器：`$ASDM/scripts/gen-sprint-index.py`（python3 + `yaml.safe_load`，count-loc.sh 惯例骨架；双语注释自守——Part04 Phase 1 执行规则 7）
- 前置补缺记录：PyYAML 缺失 → `pip3 install pyyaml --user --break-system-packages`（PEP 668 externally-managed 阻断 `--user` 直装——homebrew python 特性，豁免标志仅装用户站点，版本 6.0.3）

## 一、生成物规模

| 产出物 | 规模 | 说明 |
|---|---|---|
| `workspace/index/sprint-v0.0.1.yaml` | parts=4 / docs=24 / tasks=74 | Sprint→Part→Phase→Task 层级（doc/status/date/evidence/locale/phase/doc-note/moved_to）；移交条目 `moved_to: part04:1.1` 在索引（part03 Phase5 文档） |
| `workspace/index/metrics-v0.0.1.json` | 10 顶层指标组 | test_report（四数字+源路径）/loc（快照解析）/sprint_rhythm/moved_count/blocked_items/adr_count/evidence_density/ci |
| `workspace/index/loc-snapshot-v0.0.1.md` | LOC 快照 | `count-loc.sh` 输出落盘（8516 文件 / 1,450,314 行，2026-11-16）；生成器默认只读快照（37s 量级重跑不进默认路径），`--refresh-loc` 显式更新 |

关键指标值（机械提取，无硬编码）：
- test_report：VP 34/34、单测 57/57、断言 55/55、DRIFT 0（源：`part02/Phase2Results/zh-CN/…Test-Report.md`，metrics 内 `source` 字段记路径）
- sprint_rhythm：part01 10-24→11-16（23 天）/ part02 11-07→11-16（9 天）/ part03 11-12→11-16（4 天）/ part04 11-16（0 天，进行中）
- moved_count=2（part01 任务 2.1 → Part02 P0.5；part03 任务 5.5 → part04 1.1——Plan 表 🔁 机械计数）
- blocked_items=2（人工维护常量，D6 诚实性——Android 载体走查 V6.3.4、Apple 签名段 VP3.6.3，各带出处与复验计划）
- adr_count=10、evidence_density：part01=3 / part02=208 / part03=169 / part04=0
- ci：`not_run`（"CI workflow 尚未建设（规划级）——如实标注未实跑（D6 诚实性）"）

## 二、三重校验输出（V1.1.2–V1.1.6）

1. **生成即校验**：首跑一次通过——front-matter 全量可解析、Plan 表 ↔ front-matter 双源零漂移（Phase 行 status 逐条比对）、Plan 聚合 status ↔ Plan front-matter 零漂移、Test-Report 四数字可提取。
2. **`--verify` 全量重比对**：`verify OK: parts=4 docs=24 tasks=74 — index/front-matter 双向一致，metrics/源报告一致`（exit 0）。
3. **覆盖完备**：`find $SPRINTS/part0[1-4]/zh-CN -name 'v0.0.1-Part0*.md' | wc -l` = 24 = index docs 条目数（零遗漏）。
4. **指标 vs 源报告**：四项逐项一致（34/34、57/57、55/55、DRIFT: 0 ↔ Test-Report 头部结论原文命中一致）。

## 三、幂等复跑记录（V1.1.5）

- 两遍完整生成 → 产出物 MD5 完全一致：`sprint-v0.0.1.yaml` = 4375d3d87ab7c5c87832a88744725db1、`metrics-v0.0.1.json` = e31e3555211b43d9dde33ea6c83d3298（BYTE-IDENTICAL）。
- 注记（2026-11-16 审核补）：上列哈希是 V1.1.5 时点记录——其后执行期源文档回写（执行结果填写、Plan 表 1.1 行状态）触发的 V1.1.8 重跑合法更新了字节，最终入库产物（暂存态实测 `sprint-v0.0.1.yaml` = b1fd3dda624a30c03c714d87ad81dcb1、`metrics-v0.0.1.json` = b6b7b5de94ca5736cbe64d771677cffe）与上列哈希不同属预期演进，非幂等失效；幂等判据以「同源两次重跑零字节差」为准。
- 已跟踪态（staged）复验：重跑后 porcelain 三条均 `A `（无 `M` 后缀）——重跑零工作区变更。

## 四、fail-loud 演示（V1.1.7）

- 破坏态（part03 Phase7 文档 status → `bogus-value-not-in-vocab`）：`--verify` exit 1，错误精确到
  `…v0.0.1-Part03-Phase7-Runtime-Data-Locale.md: status: 非法状态值: 'bogus-value-not-in-vocab'（词表: ['completed', 'draft', 'in_progress', 'moved', 'pending', 'planned-backlog']）`
  ——status 词表校验先于漂移比对拦截，无静默跳过路径。
- 还原态：exit 0；`git status` 零残留。

## 五、执行期就地修复清单（应用/文档零放宽）

| # | 发现 | 处置 |
|---|---|---|
| 1 | `--help` 首版误用 `__doc__`（用法头是 `#` 注释非 docstring）输出 None | 改为回显脚本头部注释块（单一事实源） |
| 2 | 头部注释第 7 行行首空格笔误致 usage 回显截断 | 修正行首空格 |
| 3 | PyYAML PEP 668 阻断 | `--user --break-system-packages` 用户站点安装（本报告头部已记录） |

## 六、入库状态（V1.1.8）

- `git add workspace/index` → 暂存 3 条（sprint yaml + metrics json + loc snapshot md），≥ 2 达标；入库纪律与 portal 侧 gitignore 相反（已知坑 2 两套纪律各自就位，portal 侧 V1.2.5 验证）。
- 提交时机由用户决定；提交分组：生成器脚本 + 产出物同车。

## 七、三合一门首战 Part04（收口后门禁复跑拦截与处置，2026-11-16）

任务 1.1 勾选后按 Part04 总体口径「三合一门管辖」复跑，门禁拦到两处并即修（判据未放宽）：

| # | 违规 | 根因 | 处置 |
|---|---|---|---|
| 1 | 生成器脚本注释双语 19 处 | 头部注释「中文段→英文段」逐段交替且以中文收尾 + `用法 / Usage` 单行混排——块级判定要求最后 CJK 行后有英文收尾（与 check-bilingual.sh 自身首战同款问题） | 头部重写为规范两段式（全部中文段在上、全部英文语义重写段在下） |
| 2 | front-matter UNROUTED ×1（`index/loc-snapshot-v0.0.1.md`） | Part04 引入新资产类型 `workspace/index/`（生成器机器产物），门禁创作树路由面未覆盖 | check-bilingual.sh `--frontmatter` 排除面扩展 `index/`（生成物目录，与 artifacts/modelB 同类——正当口径演进非放宽）+ action 文档判据同步（两处排除口径描述） |

修复后终验三门全绿：生成器脚本 0 违规 / frontmatter 全量 0 违规（index/ 排除生效）/ Part03 触碰面回归 0 违规；生成器功能复验（`--verify` OK、`--help` 两段式回显正常）。
