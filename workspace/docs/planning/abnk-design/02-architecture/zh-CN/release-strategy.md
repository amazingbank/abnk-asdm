# 上游同步策略（fork 与 develop 的长期可合并性）

> **性质**：设计框架（Phase 2 建立 CI 后执行）。依据 ADR-001/002；机制事实见 `extension-points.md`。

---

## 1. 前提：隔离带来的结构性收益

| 改动类型 | 落点 | 与上游的冲突面 |
|---|---|---|
| 业务定制代码 | `custom/abnk/**` | **零**（上游无此目录内容） |
| 定制表结构 | `db/custom-changelog/**` | **零**（独立迁移流） |
| 模块接入 | `fineract-provider/dependencies.gradle`（每类别一行） | 极低（单行追加） |
| 配置 | 环境变量 / compose（abnk-system 仓库） | 零 |
| 文档 | `.asdm` 仓库 | 零 |

**唯一实质冲突面 = 上游自身演进**（正常 rebase 成本）。

## 2. 同步节奏

- **季度级 rebase**：`develop`（上游）→ fork
- 例外：安全修复（CVE）即时 cherry-pick
- rebase 窗口选业务低峰；全流程在 CI 干净后执行

## 3. rebase 检查清单（每次执行）

```
□ 上游 release notes 通读；标注对我们有影响的变更
□ custom 模块机制的变更 diff（extension-points.md 的五个机制面）：
    settings.gradle 扫描逻辑 / starter 装配 / custom-changelog 约定 /
    质量门禁豁免（build.gradle:603,827）/ 部署路径（libs/, jib）
□ fineract-provider/dependencies.gradle 的 custom 行无冲突
□ 数据库迁移演练：在废弃租户库上跑上游新 changelog + 我们的 custom-changelog
□ 官方 E2E 跑通（上游行为基线）
□ 12 步冒烟跑通（ABNK 行为基线）
□ 会计科目/计息等 L1 数据兼容性检查（changelog 是否动 COA 相关表）
```

## 4. 冲突处理预案

| 冲突类型 | 处理 |
|---|---|
| dependencies.gradle 单行冲突 | 手工合并（保留双方追加行） |
| 配置项语义变化（application.properties） | 对照 release notes 重映射；进 config.json 同步更新 |
| 上游改了我们定制的邻居代码 | custom 路径通常不受影响；受影响 = 扩展点 API 变了 → 按 ADR-002 的缓解流程评审 |
| Liquibase 上游重排/回滚 | 在演练库先验证；绝不手工改 databasechangelog |

## 5. 反馈上游（降低长期分叉）

- 能上游化的修复（非 ABNK 特有）一律提 PR 回上游——分叉越少，rebase 越轻
- 中国本地化中**通用**的部分（如时区默认值缺陷）优先上游；**合规特有**的部分留 custom
