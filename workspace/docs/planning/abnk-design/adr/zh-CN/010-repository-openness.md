---
section: adr
status: accepted
locale: zh-CN
---
# ADR-010：仓库开放与保密边界（能开尽开 + 两条例外）

- 状态：Accepted
- 日期：2026-11-15
- 决策人：ABNK 项目负责人

## 背景

ABNK 的项目性质是以 **Amazing Bank 真实银行系统开发过程为载体**，展示 ASDM 的方法论与平台能力——过程透明是叙事本体，不是需要辩护的风险。开放策略此前散在各处：D8（Part02）确立「公开性是设计目标」（ghcr 五服务公共镜像），D9 处理官网仓私有化，但「什么开放、什么不开放、边界由谁承载」缺项目级单一事实源，新仓/新资产入仓无判据可循。

当前实测开放状态（2026-11-15）：abnk-asdm（目录 `.asdm`）与 abnk-system 为 public；`.github-private/` 与 abnk-website 为 private。

## 决策

**能开尽开为默认；不可开放仅两条边界，各由专仓承载：**

1. **密钥边界**：会暴露生产环境、导致可被攻破的操作性凭据（PAT、口令明文、私钥、证书文件）——由 `.github-private/` 承载，仅在开发/测试/构建时可获取。
2. **社区运营边界**：ASDM 团队针对 Amazing Bank 开源范例项目的运营动作（用户管理——注册/认证；社区活动——报名/跟踪；用户行为统计）——由 abnk-website 承载（含社区用户 PII，且运营是团队工作过程而非项目内容）。

**五仓定位（含新增仓推论）：**

| 仓 | 开放性 | 域 | 说明 |
|---|---|---|---|
| abnk-asdm | public | 过程资产 | 规划/Sprint/ADR/过程证据/工具集 |
| abnk-system | public | 系统交付物 | 基础设施编排/渠道/部署 |
| **abnk-devportal** | **public** | 内容展示 | dev portal 站点（Sprint v0.0.1 Part04 交付；空仓已建 `git@github.com:amazingbank/abnk-devportal.git`，域名 dev.amazingbank.ai） |
| `.github-private` | private | 密钥边界 | 只在开发/测试/构建时获取 |
| abnk-website | private | 社区运营边界 | 品牌站 + 未来社区管理能力（D9 延续） |

## 理由

1. **透明是内容本体**：部署拓扑、端口分配、决策过程、未完成状态都是 ASDM 能力展示的一部分；生产安全靠密钥隔离 + 网关鉴权 + NSG 规则，**不靠拓扑模糊（security through obscurity 不是本项目策略）**。
2. **两条边界性质不同**：密钥边界是安全边界（公开即被攻破）；运营边界是数据保护 + 域边界（社区用户 PII 与 ASDM 团队运营过程均非「Amazing Bank 项目内容」）。
3. **devportal public 是策略直接推论**：它是 ABNK 项目的展示窗口（内容域），与运营域无关；ghcr 公共镜像口径（D8）与此一致。

## 后果

### 正面

- 开放策略有单一事实源；新仓/新资产入仓有判据可循；dev portal 的数据源仓（abnk-asdm）天然可公开。
- 「五仓两边界」本身是 ASDM 治理能力的活样本——dev portal 治理板块可直接展示 ADR-001–010 全集（本 ADR 压轴）。

### 负面 / 风险与缓解

- 公开拓扑给攻击者省了侦查步骤 → 缓解：防线在凭据隔离（`.github-private`）、网关鉴权、NSG 规则；evidence 中真实公网 IP 字面量以域名替代（衍生约束 5）。
- 误放敏感件进 public 仓 → 缓解：凭据扫描常驻工具门（衍生约束 2）——Part02 既有纪律（「演示口令对全部证据 grep 0 命中、token 一律 `<redacted>`」）从单 Phase 收口自律升级为工具链常驻门。

### 必须遵守的衍生约束

1. **新资产入仓分流判据**：是可攻破生产环境的凭据 → `.github-private`；是社区运营功能/数据 → abnk-website；否则 → 对应 public 仓（过程资产类 → abnk-asdm；系统交付类 → abnk-system；内容展示类 → abnk-devportal）。
2. **凭据扫描常驻门**：public 仓触碰 evidence/报告类文件必跑（Part03 Phase 6 落地，与 check-bilingual 同族工具）；已知模式：口令/token/密钥字面量、`.github-private` 内容泄漏（路径引用允许、内容禁止）。
3. **`.github-private` 路径引用**：public 仓中允许出现其路径（说明性），其内容永不出现。
4. **dev portal 纯渲染器约束**：portal 只做内容渲染，不长运营功能——用户互动/注册/统计属运营域，归 abnk-website 边界处理；技术形态（build-time 静态）与策略边界互锁。
5. **轻规则（IP 替代）**：evidence 中真实公网 IP 字面量以 `amazingbank.ai` 域名替代（域名本公开，零信息损失）；拓扑描述、部署流程、端口分配**不属**脱敏对象。
6. **仓定位变更走 ADR**：任何仓的开放性/域归属变更，新开 ADR 并标注 `Superseded by`，不在 Part 文档内隐性变更。
