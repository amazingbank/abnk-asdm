# Task P1.4 Backoffice 走查记录（ABNK 运营后台 mock 原型）

- 日期：2026-11-07
- 载体：`npm run dev`（Vite 7 dev server，`http://localhost:6203`，端口规范 `docs/port-allocation.md` 6203/6204 成对预留号）
- 驱动：playwright-cli（1440×900 桌面视口）；截图目录 `artifacts/phaseP1/screenshots/`（bo-01~bo-05）
- 数据：mock（`src/api/mock/mockData/clients.json`，P0.3 种子快照口径：王/李/赵 POC-A/B/C，业务日期 2027-03-29）；登录口令 admin / password（原型专用明文）
- 工程：Vite + React 18 + AntD v5 + react-router v6；主题 = P1.2 交付 `abnkTheme.ts`（copper 主色 + warmwhite 容器 + 自托管 variable 字体四族）

## 走查路径（四节主路径，每步截屏）

| # | 页面 | 操作 | 观察结果 | 截图 |
|---|------|------|----------|------|
| 1 | 登录 | 打开 `/` → 重定向 `/login`（路由守卫生效） | 品牌 eyebrow（AMAZING BANK 等宽字距）+ serif 标题「Backoffice 运营后台」+ 表单（用户名/口令）+ mock 演示口令提示 | `bo-01-login.png` |
| 2 | 客户列表 | admin/password 登录 → `/clients` | 三客户表格：**证照状态列**——王POC-A「已过期」红标（2020-01-01）/ 李POC-B「有效」绿标（2099-12-31）/ 赵POC-C「有效」；搜索框 + 行点击跳详情 + 数据口径脚注 | `bo-02-client-list.png` |
| 3 | 客户详情 | 点击客户 A（王，clientId=28）→ `/clients/28` | 客户信息卡（客户号/外部编号/姓名/手机/邮箱/机构/状态）+ **证照信息卡**（身份证 / ID-A-1107104347 / 签发 2015-01-01 / 到期 2020-01-01 / 推导「已过期」）+ **编辑表单**（到期日 DatePicker 预填 + 证件号/说明可选 + 保存按钮）+ 账户信息卡（活期 ¥10,000/¥0 两账户） | `bo-03-client-detail.png` |
| 4 | 证照编辑（mock 提交回显） | 到期日改 2030-12-31 → 保存证照变更 | 成功提示「证照已更新（到期日 2030-12-31）」；详情重读回显：到期日 2030-12-31、推导状态 **已过期→有效**（状态翻转由到期日对业务日期 2027-03-29 推导）；复跑改 2029-06-30 二次回显确认 | `bo-04a-identifier-updated.png` / `bo-04b-identifier-edit-success.png` |
| 5 | 贷款运营（只读操作位） | 侧栏菜单 → `/loan-ops` | 信息横幅「POC 基线只读——审批/放款为预埋操作位，P2.5 网关内部通道（/bo/api/*）接入后启用」；客户 C 贷款 6 行：Active + **逾期 40 天（ABNK_POC_OD）** 红标（Tooltip：逾期起算 2027-02-17 / 逾期总额 ¥8,791.58）；**审批/放款按钮 disabled** | `bo-05-loan-ops.png` |

附加观察：浏览器重开（sessionStorage 清空）后访问 `/loan-ops` 被重定向回 `/login`——RequireAuth 路由守卫二次验证 ✓。

## console 观察记录

- 未捕获异常（红错）：**0**；warning：**0**
  - 过程修复 1 例：首跑 favicon.ico 404 红错 ×2 → 新增 `public/favicon.svg`（char 底 + copper M 品牌标）+ `index.html` link 登记，复跑清零
  - React Router future flag 警告 ×2 → `BrowserRouter future={{ v7_startTransition, v7_relativeSplatPath }}` 显式开启后清零
  - 终态 console：仅 1 条 INFO（React DevTools 下载提示，框架级，无碍）
- 静态门槛（VP1.4.1–VP1.4.3）：typecheck 0 错误 / eslint 0 错误 0 警告 / `vite build` ✓（dist/ 备料 P3.4）/ 页面层 `fetch|axios` grep = 0

## 范围备注（显式不做，POC 演示增量承接）

- 证照过期标红（列表「已过期」红标为状态展示，非拦截标红动线）
- 权限矩阵、审批流（贷款审批/放款写操作为 P2.5 预埋禁用位）
- 证照新增/删除（仅 expiry_date 编辑——P0.2 实测 identifiers PUT 口径）
