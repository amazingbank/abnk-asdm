---
sprint: v0.0.1
part: part04
phase: 4
status: in_progress
date: 2026-11-17
evidence: ../
locale: zh-CN
---
# 任务 4.2 —— ghcr 公共镜像发布与生产部署（两阶段铁门）发布记录

- 日期：2026-11-17；执行人：AI（abnk-debugger 会话）
- 定位：portal 首次生产发布——服务器侧构建 + ghcr push（确认门①）→ dev 子域接入既有反代 + 两阶段上线（确认门②）→ 公网终验 → 回滚演练。纪律沿用 `abnk-prod-deploy.md`（两阶段 + 用户确认铁门；本记录兼作 Release Note）。

## 镜像 tag

- **`ghcr.io/amazingbank/abnk-devportal:0.1.0`**（tag 源 = abnk-devportal 仓 `package.json` version——对齐 website Iron Rule 4 口径）
- 首推：ghcr 上 `amazingbank/abnk-devportal` 包不存在（匿名 manifest 探测 403 = 未创建）——无覆盖风险（已知坑 2 天然满足）
- ⚠️ ghcr 包首次推送默认 private——push 后需在 GitHub（`amazingbank` org → Packages → abnk-devportal → Package settings）将可见性改为 **Public**，匿名 pull 复验（V4.2.1）才可能通过；此步需用户/组织管理员在 UI 执行

## Phase A：发版前核验（已完成，全部本地/只读）

| 检查项 | 结果 | 证据 |
|---|---|---|
| 敏感信息审计（prod-deploy Step 0 强制门） | ✅ exit 0 | 6 节全过（凭据模式/密钥形态/PAT 扫描/private repo 完整性） |
| 服务器就绪 | ✅ | SSH OK；Docker 29.9.2 + compose 5.6.1；磁盘 96G 空闲；80/443 由 abnk-nginx 绑定 |
| TLS 证书 | ✅ | `notAfter=May 12 2027`；SAN `*.amazingbank.ai + amazingbank.ai`——dev 子域零新增覆盖 |
| DNS | ✅ | `dig +short dev.amazingbank.ai` → 20.6.8.119（= abnk-vm001，已生效） |
| ghcr 公共口径先例 | ✅ | `abnk-mweb:1.0.1` 匿名 manifest 200（D5 口径既有包成立）；服务器已 `docker login ghcr.io`（auths 含 ghcr.io，push 凭证在位） |
| 仓推送基线 | ✅（3/3 对齐） | `.asdm`/`abnk-devportal`/`abnk-system` 本地 HEAD 均已推送 origin/main；服务器 abnk-system 落后本地（Phase B `git pull` 对齐） |
| 本地编排验证 | ✅ | compose config（含 drill env + override）exit 0；入口 nginx-gateway.conf `nginx -t` syntax OK |

### Phase A 本地改动（abnk-system 仓，dev 子域接入既有拓扑）

| 文件 | 改动 |
|---|---|
| `deploy/prod/compose-abnk-prod.yaml` | 新增 `abnk-devportal` 服务（`:?` 硬失败闸 + bo/mweb 同形态 healthcheck；头注释六容器→七后端/五→六镜像） |
| `deploy/prod/nginx-gateway.conf` | 新增 `dev.amazingbank.ai → abnk-devportal:80` server 块（api/app/bo 模式第四次适用；分流矩阵注释同步） |
| `deploy/prod/env/abnk-fullstack.env.example` | 新增 `ABNK_DEVPORTAL_IMAGE` 模板（双语注释） |
| `deploy/prod/env/abnk-fullstack.drill.env` | 同步 `ABNK_DEVPORTAL_IMAGE=abnk-devportal:0.1.0`（演练 :? 闸对齐） |

## 服务器侧三仓获取形态（已知坑 7 定形——待 4.4 手册固化）

| 仓 | 服务器路径 | 获取方式 | 说明 |
|---|---|---|---|
| abnk-system | `~/source/abnk-system`（既有） | `git pull`（SSH deploy key 既有） | compose/nginx conf/凭证链所在；仅需对齐本次 dev 接入提交 |
| abnk-devportal | `~/source/abnk-devportal`（新增） | `git clone https://github.com/amazingbank/abnk-devportal.git` | public 仓 HTTPS 匿名 clone（只读意图，无需 deploy key） |
| abnk-asdm | `~/source/abnk-asdm`（新增） | `git clone https://github.com/amazingbank/abnk-asdm.git` | public 仓 HTTPS 匿名 clone（构建数据源附加上下文） |
| tokens | `~/source/abnk-system/channels/shared`（既有随仓） | 无需单独获取 | design-tokens 附加上下文直接用既有 abnk-system clone |

> 三仓全 public → HTTPS 匿名 clone 即可，零新增凭证面（与 website 私有仓 deploy key 模式差异：公开仓无需 key）。

## Phase B：部署命令链（待用户确认后执行）

```bash
# 0) 本地提交并推送三仓（确认门①的前置——服务器构建以远端 commit 为基线）
#    abnk-devportal: Dockerfile/nginx.conf/.dockerignore（任务 4.1 交付）
#    abnk-system: deploy/prod 四文件（dev 子域接入）
#    .asdm: Part04 Phase4 文档勾选 + artifacts/phase4 归档（数据截至此 commit）

# 1) 服务器三仓获取与基线核对
ssh azureuser@20.6.8.119 "git clone https://github.com/amazingbank/abnk-devportal.git ~/source/abnk-devportal \
  && git clone https://github.com/amazingbank/abnk-asdm.git ~/source/abnk-asdm \
  && cd ~/source/abnk-system && git pull \
  && cd ~/source/abnk-devportal && git log --oneline -1 \
  && cd ~/source/abnk-asdm && git log --oneline -1"
# 核对：两个新 clone HEAD = 本地推送 commit

# 2) 服务器侧构建（V4.2.1）
ssh azureuser@20.6.8.119 "cd ~/source/abnk-devportal && docker build \
  -t ghcr.io/amazingbank/abnk-devportal:0.1.0 \
  --build-context asdm=~/source/abnk-asdm \
  --build-context tokens=~/source/abnk-system/channels/shared ."

# 3) 【确认门①】push ghcr 公共包（问用户后执行）
ssh azureuser@20.6.8.119 "docker push ghcr.io/amazingbank/abnk-devportal:0.1.0"
# + 用户在 GitHub UI 把包可见性设为 Public；随后匿名 pull 复验（本机执行）：
docker pull ghcr.io/amazingbank/abnk-devportal:0.1.0   # 期望：匿名可拉

# 4) 部署根 .env 追加镜像变量（首版 = append，非 sed 替换）
ssh azureuser@20.6.8.119 "grep -q ABNK_DEVPORTAL_IMAGE ~/deploy/.env || \
  echo 'ABNK_DEVPORTAL_IMAGE=ghcr.io/amazingbank/abnk-devportal:0.1.0' >> ~/deploy/.env"

# 5) 容器层起服务（V4.2.2 阶段一——单服务滚动，其余七容器零感知）
ssh azureuser@20.6.8.119 "cd ~/source/abnk-system && \
  docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-devportal"
# 容器层验证（反代链路预检——经 abnk-nginx 容器解析 portal 容器名）：
ssh azureuser@20.6.8.119 "docker exec abnk-nginx wget -q -O- http://abnk-devportal:80/ | head -c 200; \
  docker compose --env-file ~/deploy/.env -f ~/source/abnk-system/deploy/prod/compose-abnk-prod.yaml ps abnk-devportal"

# 6) 【确认门②】接入公网反代（问用户后执行）——restart 入口 nginx 加载新 server 块
ssh azureuser@20.6.8.119 "docker restart abnk-nginx"
# （滚动 up 后 restart abnk-nginx 同时满足 2026-11-12 nginx upstream 缓存纪律）

# 7) 公网终验（V4.2.3，本机执行）
curl -sI https://dev.amazingbank.ai/ | head -1                          # 期望 200
# 四路径走查 + 双语切换 + 截图归档 $ART/screenshots/

# 8) 回滚演练（V4.2.4，只验不切）
docker pull ghcr.io/amazingbank/abnk-devportal:0.1.0                     # 历史链路可达性
```

## 回滚链

- 单服务镜像切换：`sed` 改 `~/deploy/.env` 的 `ABNK_DEVPORTAL_IMAGE` → `compose up -d abnk-devportal` + `docker restart abnk-nginx`（与 website 同式）
- 首版无历史 tag——回滚退路 = 下线（compose `stop abnk-devportal` + restart 入口），v0.1.0 即回滚锚点
- 无数据库/状态迁移——回滚即镜像切换，无需数据恢复

## 用户确认门状态

- **确认门①（镜像 push + 三仓提交推送授权）**：⏸ 待用户回复
- **确认门②（公网反代接入）**：⏸ 待容器层验证后单独询问

## 风险与备注

- ghcr 包可见性翻转需 GitHub UI 操作（用户/组织管理员）——匿名复验前完成
- dev 子域接入不改任何既有 server 块（纯增量 server 块 + 新服务）——对 api/app/bo/官网的回归面收敛为 `docker restart abnk-nginx`（秒级，全栈其余容器不 recreate）
- 首次发布后 portal 数据截至 = `.asdm` 本次推送 commit（页脚标注任务 4.4 接线）
