# ADR-002：全部定制走 `custom/abnk/` 模块

- 状态：Accepted
- 日期：2026-10-25
- 决策人：ABNK 项目负责人

## 背景

不重写核心（ADR-001）之后，中国本地化、数据扩展、外围集成的代码放哪里？备选：(a) 直接改核心模块；(b) 用 Fineract 官方 custom 模块机制。事实依据见 `00-baseline/extension-points.md`：`settings.gradle:87-94` 动态扫描、`custom/acme` 参考实现、独立 `custom-changelog` 迁移、官方 10 篇文档——以及**官方自己声明该机制为 PoC**（`index.adoc`）。

## 决策

**ABNK 的全部定制代码放入 `custom/abnk/<category>/<module>/`，按官方模块机制组织，不修改 Fineract 核心模块。**

类别规划：`product` / `localization` / `integration` / `report`（每个类别配一个 `starter` 模块做 Spring Boot 自动装配，复制 acme 模式）。

## 理由

1. **可合并性**：直接改核心 = 与 473 个官方 changelog 和数千个源文件冲突，两三个版本后 fork 就废了；custom 路径物理隔离，rebase 成本近零
2. 有官方参考实现（acme 五模块）和文档（10 篇），不是在无人区发明
3. `custom-changelog` 独立迁移机制专门解决了"定制表结构与上游不冲突"
4. 与上游官方的模块化方向一致（`outlook.adoc` 明示）——未来升级为正式机制时我们免费受益

## 后果

### 正面
- fork 与上游 `develop` 保持季度级可合并
- 定制代码边界清晰，可独立测试（acme 模块演示了 Cucumber 测试组织）
- 上游替换内核服务时，我们的扩展按接口重新装配即可

### 负面 / 风险与缓解
- **官方声明 PoC**（最大风险）：
  - 定制面收窄——只做本地化/集成/报表，**不做核心账务逻辑定制**；核心行为差异尽量用配置和产品定义解决
  - 季度 rebae 时把 custom 模块 API 变更列入检查清单
  - 慎用"替换内置服务"（`service.adoc` 路线）这种最激进的能力，优先新增而非替换
- **官方对 `:custom:*` 关闭了 Checkstyle 与 SpotBugs**（`build.gradle:603,827`）→ ABNK 自建 CI 质量门禁（`04-operations/engineering-conventions.md`）
- devRun 加载 custom 需要 fork 本地改动（`fineract-provider/dependencies.gradle` 追加一行 `implementation(project(':custom:abnk:...:starter'))`）——**这是对 ADR-001"不碰内核"的唯一例外**，单行、边界清晰、合并冲突风险极低

### 必须遵守的衍生约束
- 定制表一律走 `db/custom-changelog/`，**永不**修改核心表或核心 changelog
- 每个 category 必须有 `starter` + `AutoConfiguration.imports`（照抄 acme 结构）
- 命名空间：`com.abnk.fineract` / `abnk-fineract-*`
- 自定义模块同样受租户隔离约束（ADR-004）
