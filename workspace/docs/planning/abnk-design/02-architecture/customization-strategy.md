# 定制策略（custom/abnk 宪法）

> **性质**：设计文档 ★ 全部定制工作的执行规范。决策依据 ADR-002；机制事实见 `00-baseline/extension-points.md`。
> **地位**：Phase 2 第一件事 = 按本文搭建 `custom/abnk/` 骨架。

---

## 1. 目录规划（对齐 acme 范式）

```
custom/abnk/
├── product/                          # 产品定义
│   ├── savings/                      #   储蓄产品模板（第一波）
│   │   ├── build.gradle + dependencies.gradle
│   │   └── src/main/java/com/abnk/fineract/product/savings/...
│   ├── consumer-loan/                #   消费贷模板（第一波）
│   │   └── ...
│   └── starter/                      #   ← AutoConfiguration 装配
├── localization/                     # 本地化（证照校验/证照服务）
│   ├── identity/
│   └── starter/
├── integration/                      # 外部系统适配（事件订阅/推送）
│   ├── events/
│   └── starter/
└── report/                           # 监管报送辅助
    ├── regulatory/
    └── starter/
```

**规则**：

1. 每个类别一个 `starter`，通过 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 织入（照抄 `custom/acme/note/starter` 结构）
2. 模块 = `build.gradle` + `dependencies.gradle` + 源码，**无第三种文件**
3. 命名空间：group `com.abnk.fineract`，artifact `abnk-fineract-<category>-<module>`
4. 需要建表的模块放 `src/main/resources/db/custom-changelog/0001_abnk_<category>_<module>.xml`（独立迁移流）

## 2. 模块模板（新建模块即复制此骨架）

```
custom/abnk/<category>/<module>/
├── build.gradle            # description + group + archivesName + apply from: 'dependencies.gradle'
├── dependencies.gradle     # implementation(project(':custom:abnk:<category>:<别的实现模块>')) + 三方依赖
└── src/
    ├── main/java/com/abnk/fineract/<category>/<module>/...
    ├── main/resources/db/custom-changelog/0001_abnk_*.xml   # 仅需要建表时
    └── test/java/...       # Cucumber 测试（参照 acme 的 TestSuite 组织）
```

`starter` 模块额外含：

```
src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
    → com.abnk.fineract.<category>.starter.<Xxx>AutoConfiguration
```

## 3. 红线（违反 = 架构评审否决）

| # | 红线 | 理由 |
|---|---|---|
| R1 | 永不修改 Fineract 核心模块源码 | ADR-001 |
| R2 | 永不修改核心表 / 核心 changelog | 473 个官方 changelog 冲突面 |
| R3 | 定制表只走 `db/custom-changelog/` | 官方约定（`database-migration.adoc`） |
| R4 | 永不跨租户查询/缓存/JOIN | ADR-004 |
| R5 | 慎用"替换内置服务"（service.adoc 路线）——优先新增不替换 | PoC 中最激进的能力 |
| R6 | 单测+质量门禁自建（官方对 custom 关了 Checkstyle/SpotBugs，`build.gradle:603,827`） | 官方豁免 ≠ 我们豁免 |

## 4. devRun 接入（对 ADR-001 的唯一豁免）

`fineract-provider/dependencies.gradle` 追加（每类别一行）：

```groovy
implementation(project(':custom:abnk:product:starter'))
implementation(project(':custom:abnk:localization:starter'))
// ...
```

- fork 本地改动，单行、边界清晰、合并冲突风险极低
- 生产部署走官方路径：JAR 丢 `libs/` 或 `:custom:docker:jibDockerBuild`（`deployment.adoc`）——**两条路径都要在 CI 中验证**

## 5. 质量门禁（补位官方豁免）

| 门禁 | 触发 | 工具 |
|---|---|---|
| 格式 | 每次提交 | spotless（自配规则，不依赖官方对 custom 的关闭） |
| 静态检查 | 每次提交 | checkstyle 自配规则集 |
| 单测 | 每次提交 | 模块内 JUnit + Cucumber |
| 集成 | 每日 | 12 步冒烟（`phase-1-validation.md`）+ 官方 E2E 子集 |
| 租户隔离 | 每次涉及数据改动 | 双租户测试用例（ADR-004） |

## 6. PoC 风险的持续管理

- 季度 rebase 时：diff `custom/` 相关上游变更（`extension-points.md` 的机制面）→ 变更清单过架构评审
- 每个 custom 模块头部注释标注"依赖的 Fineract 扩展点 + 官方文档篇名"，rebase 时按图索骥
- 若上游正式化模块机制（outlook 兑现），做一次性迁移评估

## 7. 第一个落地模块的建议顺序

1. `localization/identity`（身份证 18 位校验）——小、独立、立刻有用（Phase 1 建客户即需）
2. `product/savings` 模板（Phase 2）
3. `integration/events`（Phase 2 末，对接事件总线前）
