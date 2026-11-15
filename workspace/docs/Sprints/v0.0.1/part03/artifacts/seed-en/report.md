# Fineract 演示库英文种子重施加 —— 操作与验证记录

- 日期：2026-11-13；拍板：线上业务数据英文单语（「业务数据不需要双语，种子英文重施加」）
- 范围：生产演示库 `fineract_default`（POC 种子，非真实生产数据）

## 变更链

| # | 动作 | 结果 |
|---|---|---|
| 1 | `seed_poc.py` 参数化 `ABNK_SEED_LANG`（缺省 en-us；zh-cn 显式回退；en 为 D2 语义重写：Wang/Li/Zhao 拼音 + 英文银行业产品名 + National ID 描述） | `2189158` |
| 2 | `fineract_default` drop schema → Fineract 重启 Liquibase 重建 → healthy | 旧中文种子清空 |
| 3 | 重跑种子（`ABNK_SEED_LANG=en-us`，Fineract 容器内网直连） | 全断言过：客户 1/2/3、源余额 10000、贷款逾期 40 天分档 ABNK_POC_OD、FD maturity 2027-11-12 |
| 4 | 重建坑位：`c_configuration id=44 enable-business-date` 重建后为 f——SQL 恢复 true 后施加成功（首次记录） | 已记录 |
| 5 | 网关用户表随种子轮换 → 网关镜像 `0.1.0→0.1.1` 重建 + push + `.env` tag 更新 + 滚动 up + **restart abnk-nginx（up 后纪律）** | digest `sha256:14dc6559…` |
| 6 | 新口令归档 `.github-private/…/gateway-demo-passwords.json` server 节轮换 | `534d8dc` |

## 新演示口令（server 节，2026-11-13 起生效）

- BO：`admin` / `ZcG66aDTWqODWHzi`
- mobile：`alice` / `Yk5sROsoPCfmz2rB`、`bob` / `YRtE5YyES9nSY3YE`

## 数据库实证（`fineract_default`）

- `m_client`：Wang POC-A1112174148 / Li POC-B… / Zhao POC-C…
- `m_savings_product`：ABNK-POC Current Savings 1112174148 / ABNK-POC Fixed Deposit 1112174148
- `m_product_loan`：ABNK-POC Consumer Loan 1112174148
- 证照描述：National ID (expired) / National ID (valid) ×2

## 线上端到端验证（全部实测）

| 通道 | 验证 | 结果 |
|---|---|---|
| 网关 /login（客户） | alice 新口令 | 200，token 签发，clientId=1（新映射） |
| 网关 /bo/login（运营） | admin 新口令 | 200，role=ADMIN |
| 网关 bo 通道 `/bo/api/v1/clients` | 客户列表 | Wang/Li POC-* 英文 ✅ |
| 网关客户通道 `/abnk/api/v1/me` | alice 档案 | displayName `Wang P.`、office `Head Office` ✅ |
| 网关客户通道 `/abnk/api/v1/me/accounts` | 账户产品名 | `ABNK-POC Current Savings 1112174148` ✅ |
| BO UI（`bo.amazingbank.ai`） | admin 登录走查 | 登录成功；页脚数据源文案 `(Wang/Li/Zhao POC-A/B/C…)` 英文；截图 `bo-online-english-clients.png` |
| mobile UI | 线上镜像无 semantics define，UI 走查不适用——以客户通道 API 数据层验证为准 | ✅ |

## 边界说明

- 业务日期随种子推进到 `2027-01-21`（贷款逾期 40 天分档态），与首次施加同口径（单向不回拨）
- mobile mock fixtures（clientId 28/29）为本地 mock 通道数据，与线上 remote 无关，不受本次影响
- 旧口令（`GrOu2YORpUMHa_vx` 等）随用户表轮换全部失效
