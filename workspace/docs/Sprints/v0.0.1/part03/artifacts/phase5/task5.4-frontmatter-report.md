# 任务 5.4 · front-matter 注入报告

执行日：2026-11-16；注入脚本：`.asdm/scripts/add-frontmatter.py`（入库，含 `--check` 校验模式，供 Phase 6 三合一防回潮门复用）。

## 覆盖率与 profile 路由（V5.4.1 / V5.4.2）

| profile | 文件数 | 字段 | 路由来源 |
|---|---|---|---|
| sprint-doc | 25 | sprint/part/phase/status/date/evidence/locale/doc-note/moved_to | Plan 进度概要 Phase 级行反填（19 Phase 文档）+ 聚合（4 Plan 文档）+ 文档头抽取（KBank-POC-Journey 设计稿 🟡→draft）+ 占位 |
| planning-doc | 42 | section/status/locale | 分区名路由；status 默认 stable、ADR 从正文「状态：」抽取（accepted/proposed） |
| release-note | 8 | version/date/locale | 版本目录名 + 正文「**日期**」抽取 |
| **合计** | **75** | — | 覆盖率 100%（V5.4.1 判据 0 缺口）；schema 必填 0 违规（V5.4.2，`--check` issues=0） |

**不注入对象**（口径与判据一致）：Part 桶内 artifacts 证据 md（28 件 + Sprint 级 artifacts/README.md）与 modelB——证据与外部资料永不分层、不注入。

## status/date 词表映射（V5.4.3 交叉验证）

词表：✅→completed / ⏳→pending / 🚧→in_progress / 🔁→moved / 🟢·排期·远期→planned-backlog /
**🟡→draft**（本轮实测新增形态：KBank-POC-Journey 设计稿头部状态）。

date 口径：完成态取 Plan 括注日期（多日期取最后一个 = 最终完成日，如 part02 P3 取 2026-11-11）；
无日期态（⏳/🚧/🟢/🟡）取注入执行日 2026-11-16（状态快照日）。

交叉验证结果：19 个 Phase 文档（part01 3 + part02 4 + part03 7 + part04 5）× Plan「进度概要」
Phase 级行比对——**drift = 0**（front-matter 与正文状态双源一致；任务行不参与比对——文档级元数据
无任务级载体，2026-11-15 二轮审核口径）。part03 Phase 5/6 的 pending 态与 Phase 7 的插入性质
（doc-note: 插入性质（D3 修订触发））均正确入注。

## 幂等（V5.4.4）

完整执行两遍：第二遍 `injected=0 already=75`，git status 变更数 before=86 / after=86——
**重跑零变更**（已注入跳过逻辑有效），PASS。

## part03 特殊项

- Phase 5 文档：`doc-note: 范围扩展（资产归仓 + front-matter 同车）` + `moved_to: part04:1.1`（移交声明）
- Phase 7 文档：`doc-note: 插入性质（D3 修订触发）`
- Phase2Results 嵌套文档（Test-Report）：`evidence: ../../artifacts/`（相对深度随目录结构）

## 提交纪律声明（commit A / commit B 分离，blame 位移取舍）

- **commit A（迁移提交）**：纯 rename（git mv 暂存的 R100 rename）+ 拷贝新增（artifacts 分桶）+ 引用
  清扫与删源——零 front-matter 内容；
- **commit B（注入提交）**：front-matter 注入（本任务 75 文件头部插入）+ 注入脚本/检查脚本入库。
  注入可独立 revert 不牵动迁移。
- **blame 位移取舍**：注入使 blame 整体位移一次（每文件头部 +N 行）——分离提交保证 `git log --follow`
  语义清晰（rename 在 A、内容在 B， blame 位移只发生一次且可独立 revert）；front-matter 头部为机器
  生成元数据，后续 blame 关注正文行时 `-L` 范围查询不受影响。
- 提交分组与时机由用户决定（本报告仅固化约定）。

## 状态工作流（自本 Phase 起）

任务勾选同时改 front-matter 的 status 字段（正文 emoji 保留为渲染形态）——Phase 5 全部任务完成后：
Phase 5 文档 front-matter `status: pending → completed`、`date: 2026-11-16`，Plan 进度概要
Phase 5 行同步 ✅。

## 判据输出汇总

| 判据 | 输出 | 期望 | 结果 |
|---|---|---|---|
| V5.4.1 覆盖率 | 0 缺口 | 0 | ✅ |
| V5.4.2 schema | issues=0 | 0 | ✅ |
| V5.4.3 交叉验证 | drift=0（19 文档） | 0 | ✅ |
| V5.4.4 幂等 | 86→86 零变更 | 0 变更 | ✅ |
| V5.4.5 提交纪律声明 | 本报告（commit A/B/rename/注入 命中 ≥4） | ≥4 | ✅ |
