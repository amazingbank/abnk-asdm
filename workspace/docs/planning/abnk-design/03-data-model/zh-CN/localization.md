# 本地化数据规则

> **性质**：设计文档（L1 数据面）。事实锚点：默认时区 `Asia/Kolkata`（`application.properties:61`，实测）；领域差距详见 `05-domains/`。

---

## 1. 规则总表

| 项 | Fineract 默认（实测/文档） | ABNK 目标 | 落点 |
|---|---|---|---|
| 时区 | `Asia/Kolkata`（`fineract.tenant.timezone`，环境变量可覆盖） | `Asia/Shanghai` | 环境变量 `FINERACT_DEFAULT_TENANTDB_TIMEZONE`；**租户级配置**（ADR-004 多租户差异位） |
| 币种 | 产品级配置 | CNY（产品模板固化） | 产品定义 |
| 语言 | locale 参数（en 默认） | zh-CN 界面文案（前端层）；API locale=en 稳定 | 前端，不动核心 |
| 证照 | 通用字段，无中国校验 | 身份证 18 位校验位、统一社会信用代码 | `custom/abnk/localization/identity` |
| 会计日历 | 通用 | 公历年度 + 会计期间 | COA 设计（`accounting.md`） |

## 2. 计息相关数据规则（细节在 `05-domains/`）

| 规则 | 目标行为 | 所属文档 |
|---|---|---|
| 活期计息 | 积数计息（按日累计余额×利率/360） | `savings.md` |
| 活期结息 | 按季结息（3/6/9/12 月 20 或 21 日） | `savings.md` |
| 定存到期 | 对年对月对日 | `savings.md` |
| 贷款还款日 | 对日；节假日顺延规则 | `lending.md` |
| 贷款定价 | LPR 加点基准 | `lending.md` |
| 节假日 | 中国法定节假日表 | `Holiday`/`Calendar` 原生实体（Phase 1 验证） |

## 3. 实施位置矩阵（本地化三落点）

```
环境变量/配置  ← 时区、币种默认、locale
产品定义       ← 利率、期限、计提频率（L1 的主力落点，零代码）
custom 模块    ← 证照校验、强约束字段、计息引擎补差（仅当产品配置不够）
```

**原则：本地化优先级 = 配置 > 产品定义 > custom 代码。** 能用配置解决的绝不写代码（ADR-002 定制面收窄）。

## 4. 多租户的本地化差异（ADR-004 衍生）

- 时区是租户级（`fineract.tenant.timezone`）——多法人跨境场景天然支持
- 币种、科目表按租户独立初始化（每租户库独立）
- 证照校验按租户启用（`custom/abnk/localization` 的配置开关）

## 5. Phase 1 验证清单（2026-10-25 回填）

- [x] **时区 → `Asia/Shanghai` ✅**——实测路径：直接改 `fineract_tenants.tenants.timezone_id`（原 `Asia/Kolkata`），**无需重启即时生效**（业务日期与客户日期回读正常）。比"环境变量+重启"（只影响新建租户）更直接；ADR-004 多租户下按租户逐个设置
- [x] **CNY 产品创建 ✅**——储蓄/贷款产品 `currencyCode=CNY` 一次成功，金额精度 2 位正确（余额 8000.0 / 利息 0.33 / 每期 4395.79）
- [ ] Holiday/Calendar API 建立中国节假日表——未做（Phase 2 初，产品排期需要时）
- [ ] 证照字段存储与展示——未做（校验逻辑 Phase 2 `custom/abnk/localization/identity`）
