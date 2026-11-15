# ADR-003：PostgreSQL 单一数据库宿主，root/postgres 三方对齐

- 状态：Accepted
- 日期：2026-10-25
- 决策人：ABNK 项目负责人

## 背景

Fineract 历史上支持 MariaDB/MySQL/PostgreSQL，FSIP-9 已将 PostgreSQL 定为标准（MariaDB/MySQL 路径废弃）。本地调试环境需要定凭据与编排。事实依据见 `00-baseline/environment.md` §3。

## 决策

**ABNK 全栈用 PostgreSQL 单一数据库宿主：容器 `abnk-pg`（postgres:18.3），账号 `root`/`postgres`，与 Fineract 代码默认值三方对齐（hikari 默认 / createPGDB 任务默认 / 容器环境变量），实现零环境变量覆盖。**

## 理由

1. 上游标准化到 PostgreSQL（FSIP-9）——跟随上游 = 升级无数据库层摩擦
2. 三方对齐后**本地调试不需要任何环境变量覆盖**，`devRun` 直接跑通，降低新人上手成本
3. 单一数据库宿主简化 ops：一个容器、一份备份策略、一套监控

## 后果

### 正面
- 调试环境零配置漂移（config.json 记录的就是全部事实）
- 与上游 CI 的数据库假设一致

### 负面 / 风险与缓解
- root 账号非最小权限 → 仅限**本地调试**；生产部署另行设计专用角色（`04-operations/security-compliance.md` 处理）
- 未来外围系统（数仓）可能引入其他存储 → 不在本 ADR 范围，届时另立 ADR

### 必须遵守的衍生约束
- 后续接入的所有服务默认连 `abnk-pg`（按数据库分库，不另起数据库容器），登记到 config.json
- compose 项目名固定 `abnk-system`，卷名固定 `abnk-pg-data`（防撞名，见环境基线 §3 硬约束）
