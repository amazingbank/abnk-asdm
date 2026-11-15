# 任务 2.2 界面走查记录（V2.2.5 回归与全英文一致性）

> 日期：2026-11-12 · dev server：http://localhost:6203（mock 模式；两轮重启均先 `lsof -ti:6203 -sTCP:LISTEN | xargs kill` 清口）

## V2.2.5 ① 默认态回归（不设 env → 默认 zh-cn 数据）

| 操作 | 断言输出 |
|---|---|
| 无 env 重起 dev server → 客户列表 | 页头「客户列表」；数据行回归中文姓名：`王POC-A1107104347` / `李POC-B1107104347` / `赵POC-C1107104347`——默认数据无回归 |

## V2.2.5 ② en 数据 + en UI 一致性

| 操作 | 断言输出 |
|---|---|
| `VITE_ABNK_DATA_LOCALE=en-us npm run dev` 重起 → UI 切 en-us（localStorage `abnk-locale`）→ 客户列表 | 页头 `Clients`、菜单 `Clients / Loan Operations`；数据行 `28 Alex POC-A1107104347 ABNK-POC-A-1107104347 13504347001 …`；`noZhMix=true`（全页正则无中文字符，无中英夹杂） |
| 客户详情 `/clients/30` | `allEn=true`；`hasLoanProduct=true`（ABNK POC Consumer Loan 1107104347）；`hasIdentifier=true`（National ID） |

截图：`task2.2-walkthrough-regression.png`。

## 结论

- ① 默认部署（`ABNK_DATA_LOCALE=zh-cn` 缺省）行为不变，无回归。
- ② en 数据 + en UI 呈现完整一致的英文形态，数据与界面语言同英文无夹杂。
