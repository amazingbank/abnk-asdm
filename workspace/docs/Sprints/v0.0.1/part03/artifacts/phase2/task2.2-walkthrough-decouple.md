# 任务 2.2 界面走查记录（V2.2.4 数据解耦）

> 日期：2026-11-12 · dev server：http://localhost:6203（`VITE_ABNK_DATA_LOCALE=en-us` 重启实例，mock 模式）· UI 语言 = zh-cn（localStorage `abnk-locale`）

## V2.2.4 数据语言与 UI 语言解耦（en 数据 + zh UI）

| 步骤 | 操作 | 断言输出 |
|---|---|---|
| 登录 | admin/password（登录口径不随数据集变） | 成功进入 `/clients` |
| 客户列表 | UI 保持 zh-cn，读取表格行 | 页头「客户列表」、菜单「客户列表/贷款运营」为中文；数据行为 `Alex POC-A1107104347` / `Ben POC-B1107104347` / `Chloe POC-C1107104347`（英文数据集） |
| 客户详情 `/clients/28` | 读取整页文本 | `isZhUI=true`（客户详情/客户信息/证照信息等标签中文）；`savingsProduct=true`（ABNK Current Savings）；`idType=true`（National ID）；`noZhData=true`（无「活期储蓄/身份证」中文数据残留） |

截图：`task2.2-walkthrough-decouple.png`。

## 结论

- 数据集语言（部署期 `VITE_ABNK_DATA_LOCALE`）与 UI 语言（localStorage）完全解耦，决策 D3 兑现。
- 运营员 displayName（`ABNK Operations Admin`）语言中性单值，不随数据集切换。
