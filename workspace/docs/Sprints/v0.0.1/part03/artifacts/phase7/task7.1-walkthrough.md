# 任务 7.1 · V7.1.3 走查记录 —— backoffice 数据集运行时随 UI 切换

- 日期：2026-11-12；载体：backoffice dev server（:6203，无 env → 初始 en-us 数据）；自动化：agent-browser
- 改造机制：`reseedDataSet`（locale-provider 用户切换入口调用）+ `dataEpoch`（BoLayout `<Outlet key>`，切换时页面子树 remount → 数据重拉）

## 断言矩阵

| # | 操作 | 预期 | 实测 | 判定 |
|---|---|---|---|---|
| 1 | 预置 `abnk-locale=zh-cn` 刷新登录 → 客户列表 | zh UI + **en 初始数据**（解耦初始态，D3 修订「默认英文」） | 表头「客户列表/客户号/姓名」中文；数据 `Alex POC-A1107104347` / `Ben POC-B…`（en 数据集） | ✅ |
| 2 | 切换器 → English | en UI + en 数据（幂等，数据不变） | UI 全英文（Clients / Loan Operations），数据仍 Alex/Ben POC | ✅ |
| 3 | 切换器 → 切换到中文 | zh UI + **数据切换为中文数据集** | UI 中文（客户列表）；数据变 `王POC-A1107104347`（zh 数据集，remount 重拉生效） | ✅ |
| 4 | 客户 28 详情 → 证照编辑（到期日 2099-12-31 + 说明标记）→ 保存 → 推导「有效」→ 切 en | 编辑内存态随 reseed **重置**：回详情推导回 `Expired` 初始态、说明回 en 数据集值 `National ID (expired)` | 推导 `Expired`（2099 编辑丢失=重置）；说明字段 = en 数据集原生值（同时证明数据已切 en） | ✅ |
| 5 | console / errors | 0 红错 | errors 空、error 计数 0 | ✅ |

## 判据体系变更记录（D3 修订取代）

- Phase 2 `V2.2.3`「bundle 单数据集 tree-shaking」废止——`V7.1.2` 实测 `npm run build` 后 zh/en 数据串**双集均在** bundle（`ABNK 活期储蓄` 与 `ABNK Current Savings` 各命中 1），运行时选择的必要条件成立。

## 归档

- 截图：`task7.1-switched-zh.png`（切换后 zh 数据态）+ `/tmp/v71-initial.png`（初始解耦态，本地临时件，正式归档以本目录为准）
- 附注：初始解耦态截图因轮次中浏览器会话已前进，正式归档以断言矩阵实测输出为准（每行断言均有 agent-browser 快照输出记录于执行日志）
