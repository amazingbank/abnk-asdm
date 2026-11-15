# KBank POC 旅程场景执行记录 —— 当前环境（本地 dev · mock 态 · zh 呈态）

- 日期：2026-11-13
- 场景脚本：`.asdm/workspace/docs/Sprints/v0.0.1/part02/v0.0.1-Part02-KBank-POC-Journey.md`（八步旅程）
- 环境：本地 dev 双载体（BO :6203 `VITE_ABNK_DATA_LOCALE=zh-cn` / mobile :6280 `--dart-define=ABNK_DATA_LOCALE=zh-cn` + semantics define），mock 模式，UI 预置 zh；自动化 agent-browser
- **执行口径（重要）**：旅程设计稿中「证照过期拦截过滤器」与「首页过期横幅」属 POC 增量，**尚未开发**（`app_exception.dart:16` 预留 403 分支；gateway 无拦截实现；`home_page.dart` 显式不做横幅）——本跑覆盖「当前状态 + 已实现部分」，Step 4/5 的「交易不被拦」实测输出即为旅程 §1.3 要求的**缺口证据**（POC 开场演示形态），与 P3.5 gap-report 结论一致
- Part03 叠加验证：全程 zh 呈态下走完旅程，末尾以 Phase 7 运行时语言切换（数据随切 + 内存态重置）收尾

## 步骤矩阵（8 步 + bonus）

| 步骤 | 旅程动作 | 预期（旅程口径） | 实测 | 截图 |
|---|---|---|---|---|
| **Step 1** | BO 定位过期证照客户 | 客户列表证照状态列标红 + 详情证照「已过期」 | ✅ 列表：王POC-A1107104347（client 28）标「已过期」、李/赵 POC「有效」；详情证照区已过期态 | `step1-bo-login-clients.png` / `step1-bo-client-detail-expired.png` |
| **Step 2** | 手机银行客户 A 登录 | alice 登录成功进入首页 | ✅ alice/password 登录成功（mock 口令） | `step2-3-mobile-login-home.png` |
| **Step 3** | 首页账户总览 + 过期状态 | 旅程设计含首页红色横幅 | ⚠️ **横幅未实现（POC 增量，显式不做）**；账户总览正常（11: ¥10,000 / 12: ¥0）；证照过期态在「我的」页证件信息（只读）呈现（chip「已过期」）——实现面 | `step2-3-mobile-login-home.png` / `step3-mobile-profile-identity-expired.png` |
| **Step 4** | 发起转账 ¥10（11→12） | 旅程目标态=被拦截；当前态=放行 | ✅ **转账成功（流水号 100，余额 ¥9,990）——拦截未实现，缺口证据成立** | `step4-mobile-transfer-success-gap.png` |
| **Step 5** | 定期开户 / 贷款申请 | 目标态=拦截；当前态=放行 | ✅ 定期开户成功（¥1,000，新户 0000**0200）；贷款申请提交成功（流水号 900）——两项均不被拦（缺口证据） | `step5-mobile-fd-opened-gap.png` / `step5b-mobile-loan-applied-gap.png` |
| **Step 6** | 交易明细（只读） | 只读查询正常，新流水可见 | ✅ 明细含本人账户转账 -¥10 + 定期开户 -¥1,000 新流水 | `step6-mobile-transactions.png` |
| **Step 7** | BO 更新证照有效期（修复） | 编辑到期日 → 状态推导变「有效」 | ✅ 详情证照编辑：到期日 → **2099-12-31**（日历面板选 2099-12-31）→ 保存 → 「到期状态（推导）: 有效」；mock 提交回显（刷新还原） | `step7-bo-identifier-fixed-valid.png` |
| **Step 8** | 修复后复转 | 目标态=拦截解除后成功；当前态=本就放行 | ✅ 转账 ¥20 成功（流水号 100，余额 ¥9,980）+ 明现新流水「本人账户转账 -¥20」——「修复生效 + 交易成功 + 新流水」环节闭环；「拦截→解除」差过滤器（未开发） | `step8-mobile-transfer-again-success.png` / `step8-mobile-transactions-new-entry.png` |
| **Bonus** | Part03 Phase 7 叠加演示 | 语言切 English → UI 切 en + **数据集随切** + mock 内存态重置 | ✅ UI 变 en（Welcome back）+ 数据变 `ABNK Current Savings` + **余额重置回 ¥10,000.00**（Step 8 的 ¥9,980 被重置=切换重置语义实证） | `bonus-mobile-switch-en-data-follows.png` |

## console / errors 判据

- 全程 `agent-browser errors` 空、error/exception 计数 0（两载体均无红错）

## 执行过程要点记录（工具层）

1. **antd DatePicker 自动化**：到期日编辑须走「面板层级点选」（年 → 年代 → 年 → 月 → 日格）；`fill` 直设 DOM 值不会更新 rc-picker 内部 Dayjs（提交仍携旧值 2020-01-01——toast「证照已更新（到期日 2020-01-01）」实测暴露）；Escape 会取消未点日的选择。最终路径：选择年份 → 选择年代 → 2090-2099 → 2099 → 12月 → 31。
2. **Flutter web 会话边界**：浏览器导航离开 mobile 载体再返回 = 应用实例重载，内存态（登录会话 + mock 数据改动）全部重置——mock「刷新还原」设计；重新登录走全新流程即可。
3. **Flutter 文本输入连接损坏坑**：应用重启后语义树残留旧值、真实表单为空（截图揭示红框校验提示）；孤儿 `<input>` 抢占 document.activeElement 吞键盘事件（`document.activeElement.blur()` 可解）；根治 = `agent-browser close` 后全新会话（本次最终采用）。此为 agent-browser × Flutter web 会话边界问题，非应用缺陷。

## 数据与状态边界

- 全程 mock 内存态：BO 证照编辑与 mobile 交易互不相通（无共享后端）；Step 7 的修复在 mobile 侧无感知（无拦截链路可解）——与当前实现一致
- 归档后两 dev server 已停（:6203/:6280 端口清空实测）；浏览器会话已关

## 结论

KBank POC 旅程八步在当前环境可走通的部分全部通过并留证；「拦截过滤器 + 首页横幅」两个 POC 增量缺口以实测输出方式固化（与旅程 §1.3「当前状态的直观证据」口径一致，可作为 POC 开场演示素材）；Part03 交付项（双语词条、双语数据集、Phase 7 运行时数据切换）在旅程流程内叠加验证通过。
