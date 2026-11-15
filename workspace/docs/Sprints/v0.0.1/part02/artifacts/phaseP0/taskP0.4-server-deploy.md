# 任务 P0.4 服务器平台形态部署记录（abnk-vm001 · D7 公网直暴露口径）

> 部署时间：2026-11-07｜执行依据：`v0.0.1-Part02-PhaseP0-Platform-Prod-Form.md` 任务 P0.4
> 口径调整：D7（2026-11-07 用户拍板）——平台 8080 直接公网暴露（原「内网回环 + SSH 隧道」废弃）
> 服务器：abnk-vm001（Azure VM，Ubuntu 24.04 x86_64）｜部署根 `~/deploy`｜仓库 `~/source/abnk-system`（main）

## VP0.4.1 服务器就绪实测

```
$ $PROD_SSH "echo OK && docker --version && docker compose version && df -h / && free -h"
OK
Docker version 29.9.2, build a82e528
Docker Compose version v5.6.1
/dev/root        123G  3.7G  120G   3% /
Mem:  7.7Gi  634Mi  6.6Gi(available 7.1Gi)
```

判据：OK ✓｜双版本号 ✓｜磁盘可用 120G ≥ 20G ✓｜内存可用 7.1Gi ≥ 4G ✓

## VP0.4.2 代码就位（push 前经用户确认）

- 本地三提交按任务域分拆：`7ca659b`（P0.2 探查）/ `49aaca0`（P0.3 种子）/ `7287020`（P0.4 部署制品）
- push：`1920169..7287020 main -> main` ✓
- 服务器 `git pull` 后 HEAD = `7287020 feat(deploy): 任务 P0.4 服务器平台栈部署制品（D7 公网直暴露口径）`
- 判据：HEAD = 本地推送 commit，零漂移 ✓

## VP0.4.3 WAR 上传校验

```
本地:  bd1f12c86385b2f58fdb8058f8cac30ed1f100039f9063a76def8f0e6030e545  fineract-provider.war (210,051,470 bytes)
服务器: bd1f12c86385b2f58fdb8058f8cac30ed1f100039f9063a76def8f0e6030e545  /home/azureuser/deploy/fineract-provider.war
```

判据：两侧 sha256 完全一致 ✓
附带部署根就位：`.env`（私有仓 `platform.env` scp 上传）+ `initdb/01-init-abnk.sh`（仓内复制，755）

## VP0.4.4 平台建栈（镜像构建 + compose up）

- 镜像构建：`docker build -f ~/source/abnk-system/deploy/prod/Dockerfile.fineract -t abnk-fineract:ad988473 ~/deploy` → 18.9s，1.01GB
- compose up：`abnk-pg-platform Up (healthy)`（5432 仅内网）+ `abnk-fineract Up 0.0.0.0:8080->8080`（D7 公网绑定）
- 就绪：**APACHE FINERACT IS READY 出现于 ~240s**（4 min，上限 20 min）；grep 计数 = 1
- 首迁核对：initdb 预建 `fineract_tenants`/`fineract_default` 两库 ✓；`databasechangelog` = **2061**（与开发库/本地生产形态库三方水位精确一致）✓

判据：两 service Up ✓｜grep ≥1 ✓

## VP0.4.5 服务器本地健康

```
$ $PROD_SSH "curl -s http://localhost:8080/fineract-provider/actuator/health"
{"groups":["liveness","readiness"],"status":"UP"}
```

判据：`"status":"UP"` ✓

## VP0.4.6 公网可达（D7 口径）

```
$ curl -m 8 -s http://amazingbank.ai:8080/fineract-provider/actuator/health
{"groups":["liveness","readiness"],"status":"UP"}    # HTTP 200，首探即过（NSG 8080 已由用户放行）
```

判据：公网 health UP ✓（部署前实测为超时——NSG 拦截；用户 Azure Portal 放行后即通）

## VP0.4.7 种子施加（公网直连，无隧道）

- 前置坑（新库独有，已归档）：`enable-business-date` 配置 changelog 默认 **false**（本地栈系早期启用过）——首次施加 403 `business.date.is.not.enabled`；经 `PUT /configurations/44 {"enabled":true}` 启用后重跑通过
- 施加：`ABNK_BASE_URL=http://amazingbank.ai:8080/fineract-provider/api/v1 python3 seed_poc.py` → 退出码 **0**，16 断言全过
- 服务器新库数据：客户 A=1（过期证照，源账户 1 余额 10000 / 目标账户 2）、B=2（有效证照，储蓄 3 + 定期 4，maturity 2027-11-07）、C=3（贷款 1，逾期 40 天，分档 ABNK_POC_OD，overdueSinceDate 2026-12-07）；业务日期推进至 2027-01-16（单向）
- 公网回读抽查：A/B/C 各 `totalFilteredRecords=1` ✓；贷款 1 `inArrears=true` + `classification=ABNK_POC_OD` ✓
- 证据：`artifacts/phaseP0/seed-poc-server-evidence.json`（含 vp047PublicVerify 节）
- 一次性演示口令：已存 `.github-private/kbank-poc/gateway-demo-passwords.json`（instances.server 节）；`data/gateway_users.json` 同步为服务器实例（alice clientId=1 / bob=2）

判据：退出码 0 ✓｜公网回读 ≥1 ✓

## VP0.4.8 归档（本文件）

七个判据各一节，无空格 ✓

---

## 附：与本地栈的差异归档

| 维度 | 本地生产形态栈（P0.1/P0.3） | 服务器平台栈（P0.4） |
|---|---|---|
| 入口 | `http://localhost:8081` | `http://amazingbank.ai:8080`（公网直暴露，D7） |
| PG | `abnk-pg-prod` 宿主 5433 映射 | `abnk-pg-platform` 仅 compose 内网 |
| Fineract 载体 | WAR 卷挂载（tomcat 官方镜像） | WAR 打进镜像 `abnk-fineract:ad988473` |
| enable-business-date | true（早期已启用） | false → true（部署时 PUT /configurations/44 启用） |
| 种子数据 | TS=1107104347（client 28/29/30） | TS=1107114626（client 1/2/3，全新库） |
