# Sprints/artifacts — Sprint 级证据兜底目录

运行 `scripts/`/`tests/` 产生的可复现产物，按 Part 分桶归档（`partXX/artifacts/`）；
无法归属具体 Part 的散件归本目录（Sprint 级兜底）。

| 目录 | 内容 |
|---|---|
| `part01/artifacts/` | Part01 冒烟报告（`report-*.json`）、各步数据快照、COB 前后对比、行为基线证据 |
| `part02/artifacts/phaseP0..P3/` | Part02 各 Phase 执行证据、gateway/gap 报告 JSON、E2E 快照（含工作区根归位的 `p3-*.yaml`） |
| `part03/artifacts/phase1..7/` | Part03 各 Phase 走查记录、快照与双语验证证据（phase5 = 本迁移自身证据） |
| （兜底） | 无法归属 Part 的散件归本目录 |

## 纪律

- 只入库**小且可 diff** 的 JSON/Markdown；大文件与本地路径相关产物由根 `.gitignore` 排除
- 报告文件名带运行时间戳；首次运行产物即**基线**（回归对比对象）
- 这些快照是 `.asdm` 设计文档"待验证清单"回填的原始证据
- 证据资产**语言无关、永不分层**（不入 `zh-CN/` 叶子层，不注入 front-matter）
- 来源口径：跨仓复制自 abnk-system（来源 commit hash 见 `part03/artifacts/phase5/task5.1-migration-record.md`，2026-11-16 归仓）
