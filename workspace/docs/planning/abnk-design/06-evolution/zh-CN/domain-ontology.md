# 银行领域本体（数据智能层·建法）

> **性质**：设计框架（Phase 2 建概念骨架，Phase 5 深化）。本文是 `aos-integration.md` §2"双本体愿景"中**银行领域本体**的落地建法；代码本体见彼文。
> **事实依据**：`03-data-model/domain-concepts.md`（概念地图/行为语义）、`02-architecture/event-bus.md`（99 个 Avro schema）、ADR-004（租户模型）、`05-domains/regulatory-reporting.md`（EAST/1104 依赖链）。

---

## 1. 核心思路：三方对齐，不是从零发明

ABNK 领域本体的概念来源**全部现成**，缺的只是结构化与对齐：

```
        Fineract 数据模型（默认库 280 表 + API + 99 个 Avro 事件 schema）
                     │  "系统里真实存在什么"
                     ▼
        银行领域本体（概念层 + 实例层）
                     ▲
                     │  "监管要什么口径"
        中国监管概念体系（EAST / 1104、会计准则、五级分类）
```

一个概念只有同时挂上**系统实现**与**监管口径**两条锚线，本体才具备 `aos-integration.md` 承诺的"智能应用、跨域查询、监管映射"价值。

## 2. 概念骨架 v0（从 domain-concepts.md 起步）

`03-data-model/domain-concepts.md` 的概念总图与词汇表即本体蓝图 v0，按下列初始类清单结构化（按依赖顺序，全部有基线出处）：

| 层 | 概念 | 事实出处 |
|---|---|---|
| 当事人 | `Tenant` / `Office` / `Staff` / `Client` | domain-concepts.md §1/§3（ADR-004 租户模型） |
| 产品（模板） | `SavingsProduct` / `LoanProduct` / `Charge` | domain-concepts.md §2（Product ≠ Account 模板语义） |
| 账户（实例） | `SavingsAccount` / `LoanAccount` / `Datatable` | domain-concepts.md §1 |
| 行为 | `Transaction` / `Command`（审计事实源）/ Avro 事件个体 | domain-concepts.md §2、event-bus.md §1 |
| 账务 | `GLAccount` / `JournalEntry` / `AccountingRule` | `05-domains/accounting.md` |
| 时序 | `BusinessDate` / `COB` / `BusinessStep` / `Delinquency` | domain-concepts.md §2 |
| 风险 | `Risk` 相关概念 | **Phase 5 才引入**（征信/反洗钱输入在 L4 侧） |

概念词汇不自造，两个参照系：

- **FIBO**（EDM Council 金融业本体）：产品/协议/账户的类层次抽象
- **BIAN**（银行业务架构标准）：服务域边界划分（与 `05-domains/` 五域天然对位）
- 每个概念挂 **EAST/1104 字段映射**（如 `Client` → EAST 客户信息表口径）——"监管映射"用途的落点

## 3. 实例层：从事件流填充，不从数据库抄

架构硬规则（`02-architecture/overview.md` §2：L5 **只读事件流与数仓副本**）决定了实例化路径：

- **Phase 3–4**：Kafka `external-events` 的 Avro 事件 → 按 99 个 schema 的类型系统实例化本体个体（客户开户 → `Client` 个体 + `owns` 关系）
- 为什么不是快照同步：风险图谱/异常检测（Phase 5 用途）需要的是**带时序与事件 ID 的行为流**，事件流天然携带；库表快照丢行为语义

## 4. 与代码本体的对齐点

领域本体的每个概念标注"Fineract 里由哪个实体/端点/事件实现"（如 `JournalEntry` ↔ `JournalEntryEntity` + `/v1/journalentries`）。此映射即 `aos-integration.md` §2 说的两本体对齐处，反向即 AOS 图谱的"概念 → 代码位置"查询。**两本体共用 AOS 图模型，不引入第二套存储。**

## 5. 硬约束（已有决策推导，不可违反）

| 约束 | 出处 |
|---|---|
| 实例层只来自事件流/数仓副本，永不直连业务库 | overview.md §2（L5 规则） |
| 本体实例带租户标识，图谱查询默认租户作用域（禁止跨租户全局表） | ADR-004、domain-concepts.md §3 |
| `Transaction` 语义权威来源是 `CommandSource` 命令审计，非业务表 | domain-concepts.md §2 |
| 概念层与代码本体同放 AOS，不建独立本体库 | aos-integration.md §1 |
| Phase 5 前不深化风险概念 | aos-integration.md §5 |

## 6. 分阶段节奏（对齐 roadmap）

| Phase | 做什么 | 深度 |
|---|---|---|
| **2** | 概念骨架 v0 导入 AOS + 对齐验证（挑 3–5 个概念验证"概念 ↔ 代码"映射，与代码本体基线同一批做） | 骨架 |
| **3–4** | 事件流实例化（先 `Client`/`Account`/`Transaction` 三类）+ EAST/1104 字段映射初版 | 半动态 |
| **5** | `Risk` 概念引入（接入 L4 征信/反洗钱事件）+ 智能问答/异常检测应用 | 深化 |

## 7. 风险与待决策

| 项 | 说明 |
|---|---|
| AOS 侧 banking blueprint 成熟度 | 对齐概念命名前先评估（`aos-integration.md` §5 同项） |
| FIBO/BIAN 借用深度 | 全量对齐成本高；只借类层次与命名，不引入其推理栈 |
| EAST/1104 映射工作量 | 依赖 `05-domains/regulatory-reporting.md` 骨架先充实 |
| 银行业务专家参与 | Phase 5 深化前不必（与 aos-integration.md §5 一致） |

## 8. 第一步行动（Phase 2）

- [ ] 将 `domain-concepts.md` §1 概念总图 + §4 词汇表结构化为 AOS 概念骨架（含 FIBO 命名对照）
- [ ] 选 3–5 个概念（建议 `Client` / `LoanAccount` / `JournalEntry` / `Command`）完成"概念 ↔ 代码 ↔ 端点"三向映射验证
- [ ] 与 AOS 侧 banking blueprint 概念命名对齐（`aos-integration.md` §6 同项）
