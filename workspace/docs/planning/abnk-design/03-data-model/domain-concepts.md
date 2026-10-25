# Fineract 核心领域概念

> **性质**：概念地图（基于 API 面与模块结构整理；Phase 1 实跑后补充实测细节）。供 L2/L3 设计者建立词汇表。

---

## 1. 概念总图

```
Tenant（租户，物理分库，ADR-004）
└─ Office（机构树：Head Office → 分支）
   ├─ Staff（职员，挂机构）
   └─ Client（客户）
        ├─ Savings Account ── Savings Product
        ├─ Loan Account ──── Loan Product（含 progressive 配置）
        ├─ Charges（费用）
        └── Datatable（自定义扩展字段）

交易与命令：
Transaction（账户交易）── 由 Command 通道驱动
Command（命令，CQRS 写侧）→ CommandSource（审计）→ 四种执行实现（jdbc/async/disruptor/audit）

会计：
GL Account（科目）← Accounting Rule（规则）← Financial Activity Account（业务活动映射）
Journal Entry（分录，复式记账）

日终：
Business Date / COB Date ── COB 作业（Loan COB / WC Loan COB）── Business Step（可扩展）
```

## 2. 关键概念的行为语义（定制设计必须理解的）

| 概念 | 语义要点 | 对 ABNK 的含义 |
|---|---|---|
| **Command 通道** | 写操作异步可重试（resilience4j retry 配置实测存在）；`CommandSource` 是审计事实源 | 排障看命令审计表，不能只看业务表；对账以 CommandSource 为准 |
| **Office 树** | 数据隔离单位（`personas.md` 柜员网点边界） | 机构层级 = 网点权限边界，初始化即规划 |
| **Product vs Account** | 产品是模板（规则/利率），账户是实例——**本地化差异优先落产品配置** | L1 计息差异先试产品配置，不够再 custom |
| **External ID** | 全资源支持外部业务标识（实测有 `external-id` 端点族） | ABNK 渠道层用自有编号映射，不暴露内部 resourceId |
| **Business Date ≠ 系统日期** | 业务日期独立推进（已实测启用与设置流程） | 日终测试/回溯的基石；网关必须禁止客户端操纵 |
| **COB** | 日终按贷款分区并行；Business Step 可插入定制步骤 | 中国日终的定制步骤走 `custom/abnk`（acme 已示范） |
| **Delinquency** | 贷款逾期分级有独立作业（Loan Delinquency Classification，默认 active） | 逾期口径本地化 = 该分类规则的映射 |

## 3. 租户模型（ADR-004 事实基础）

- `fineract_tenants`（6 表）：租户清单 + 各自连接串——**路由按请求头**
- 每租户独立业务库：`fineract_default` 为默认（280 表）
- 含义：Liquibase 迁移、COB 作业、定制表全部按租户逐一执行
- 扩展约束（ADR-004）：定制不得跨租户查询；不建跨租户全局表

## 4. 词汇表（ABNK ↔ Fineract 映射）

| ABNK 业务词 | Fineract 概念 |
|---|---|
| 网点 | Office |
| 客户号 | Client (internal id) / external id |
| 账户 | Savings/Loan Account |
| 产品 | Product（Savings/Loan） |
| 分录 | Journal Entry |
| 日终 | COB（Close of Business） |
| 命令/流水 | Command / Transaction |

## 5. Phase 1 实测回填（2026-10-25）

**命令动词（command query 参数）实测全集**：`activate`（客户/储蓄账户）、`approve`（储蓄/贷款）、`disburse`（贷款）、`repayment`（贷款交易）、`deposit` / `withdrawal`（储蓄交易）、`close`（客户，有未清账户被拒）、`executeJob`（作业触发，202）、`inline`（LOAN_COB）。

**交易类型实测（transactionType.value）**：储蓄——Deposit / Withdrawal / **Interest posting**（利息入账，带 runningBalance）；贷款——Disbursement / **Accrual**（应计）/ Repayment。

**状态对象形态**：`{id: 300, code: "<type>.active", value: "Active", ...布尔族}`——判定一律用 `value` 或 `code`，勿用裸字符串比对（大小写实测为 `Active`）。

**字段级发现（写集成代码必读）**：
- 客户 `mobileNo` 全库唯一（幂等脚本必须变号码）；`legalFormId`：1=Person / 2=Entity
- 储蓄/贷款产品 `shortName` ≤ 4 字符
- 储蓄交易强制 `paymentTypeId`（`GET /v1/paymenttypes` 取，内置 Money Transfer id=1）
- 贷款还款字段是 `transactionAmount`（不是 `amount`）
- 产品创建要 `locale`（"en"）但**不要** `dateFormat`（400 unsupported）；带日期的 command 端点两者都要
- 贷款产品必填：`numberOfRepayments / repaymentEvery / daysInMonthType / daysInYearType`（30/360）
- progressive 架构：`GET /loans/{id}` 默认**不含** repaymentSchedule，须 `?associations=all`
- 枚举入参一律是**整型 id**（模板 `*Options` 提供 id↔code 映射），唯一例外 `transactionProcessingStrategyCode` 用字符串
