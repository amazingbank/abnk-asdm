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

- **`ghcr.io/amazingbank/abnk-devportal:0.1.1`**（线上运行版本；tag 源 = abnk-devportal 仓 `package.json` version——对齐 website Iron Rule 4 口径）
- 发布轨迹：`0.1.0`（首推，digest `sha256:e7e589dd…`）→ **V4.2.3 公网走查发现路由层缺陷** → 修复发版 `0.1.1`（digest `sha256:de1861fe…`，commit `294557a`）；两 tag 均已推送、均不可覆盖（已知坑 2 天然满足）
- 包可见性：用户已在 GitHub UI 翻转 Public——匿名 manifest 复验 0.1.0 / 0.1.1 双 200（D5 公共口径落地；本机 ghcr 已登录，匿名性经 token manifest 探测成立）

### 0.1.1 修复（V4.2.3 走查抓出的路由层缺陷）

- 现象：裸 `/evidence` → 301（目录重定向，Location 协议降级 http）→ `/evidence/` → 资产 location `=404`——SPA 路由被 `dist/evidence` 物理目录遮蔽（V4.1.3 本地验证只测了深链与资产文件，未测目录同名路由——测试缺口记入教训）
- 修复（portal 仓 `nginx.conf`）：SPA fallback 去除 `$uri/` 目录形态（目录不再触发 301）+ `location = /evidence/` 尾斜杠规范重定向 + `absolute_redirect off`（相对 Location 不降级协议）
- 验证：本地六项冒烟（裸 200 / 尾斜杠 301 / 语言路由 200 / 资产 200 / 深链 200 / 缺失资产 404）全过后再上服务器；公网复验全过（见下）

## Phase A：发版前核验（已完成，全部本地/只读）

| 检查项 | 结果 | 证据 |
|---|---|---|
| 敏感信息审计（prod-deploy Step 0 强制门） | ✅ exit 0 | 6 节全过（凭据模式/密钥形态/PAT 扫描/private repo 完整性） |
| 服务器就绪 | ✅ | SSH OK；Docker 29.9.2 + compose 5.6.1；磁盘 96G 空闲；80/443 由 abnk-nginx 绑定 |
| TLS 证书 | ✅ | `notAfter=May 12 2027`；SAN `*.amazingbank.ai + amazingbank.ai`——dev 子域零新增覆盖 |
| DNS | ✅ | `dig +short dev.amazingbank.ai` → <PROD_HOST>（= abnk-vm001，已生效） |
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

> **执行状态（2026-11-17）**：B0–B5 已执行并全过（真实输出见文末「Phase B 执行记录」）；⏸ 停在确认门②（ghcr 包可见性翻转 + 公网反代接入）。

```bash
# 0) 本地提交并推送三仓（确认门①的前置——服务器构建以远端 commit 为基线）
#    abnk-devportal: Dockerfile/nginx.conf/.dockerignore（任务 4.1 交付）
#    abnk-system: deploy/prod 四文件（dev 子域接入）
#    .asdm: Part04 Phase4 文档勾选 + artifacts/phase4 归档（数据截至此 commit）

# 1) 服务器三仓获取与基线核对
ssh azureuser@<PROD_HOST> "git clone https://github.com/amazingbank/abnk-devportal.git ~/source/abnk-devportal \
  && git clone https://github.com/amazingbank/abnk-asdm.git ~/source/abnk-asdm \
  && cd ~/source/abnk-system && git pull \
  && cd ~/source/abnk-devportal && git log --oneline -1 \
  && cd ~/source/abnk-asdm && git log --oneline -1"
# 核对：两个新 clone HEAD = 本地推送 commit

# 2) 服务器侧构建（V4.2.1）
ssh azureuser@<PROD_HOST> "cd ~/source/abnk-devportal && docker build \
  -t ghcr.io/amazingbank/abnk-devportal:0.1.0 \
  --build-context asdm=~/source/abnk-asdm \
  --build-context tokens=~/source/abnk-system/channels/shared ."

# 3) 【确认门①】push ghcr 公共包（问用户后执行）
ssh azureuser@<PROD_HOST> "docker push ghcr.io/amazingbank/abnk-devportal:0.1.0"
# + 用户在 GitHub UI 把包可见性设为 Public；随后匿名 pull 复验（本机执行）：
docker pull ghcr.io/amazingbank/abnk-devportal:0.1.0   # 期望：匿名可拉

# 4) 部署根 .env 追加镜像变量（首版 = append，非 sed 替换）
ssh azureuser@<PROD_HOST> "grep -q ABNK_DEVPORTAL_IMAGE ~/deploy/.env || \
  echo 'ABNK_DEVPORTAL_IMAGE=ghcr.io/amazingbank/abnk-devportal:0.1.0' >> ~/deploy/.env"

# 5) 容器层起服务（V4.2.2 阶段一——单服务滚动，其余七容器零感知）
ssh azureuser@<PROD_HOST> "cd ~/source/abnk-system && \
  docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-devportal"
# 容器层验证（反代链路预检——经 abnk-nginx 容器解析 portal 容器名）：
ssh azureuser@<PROD_HOST> "docker exec abnk-nginx wget -q -O- http://abnk-devportal:80/ | head -c 200; \
  docker compose --env-file ~/deploy/.env -f ~/source/abnk-system/deploy/prod/compose-abnk-prod.yaml ps abnk-devportal"

# 6) 【确认门②】接入公网反代（问用户后执行）——restart 入口 nginx 加载新 server 块
ssh azureuser@<PROD_HOST> "docker restart abnk-nginx"
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

- **确认门①（镜像 push + 三仓提交推送授权）**：✅ 2026-11-17 用户回复「确认发版」——三仓推送（portal `f7a923a` / system `ad5f828` / asdm `f047242`）→ 服务器 clone + 构建成功 → push 成功（0.1.0 digest `sha256:e7e589dd…`；修复版 0.1.1 digest `sha256:de1861fe…`）
- **确认门②（公网反代接入）**：✅ 2026-11-17 用户回复「已转 Public，执行接入」——`docker restart abnk-nginx` 生效 dev server 块；包可见性同步翻转 Public

## 风险与备注

- **生产 IP 清除声明（2026-11-17，website 0.1.5 发版 Step 0 审计拦截）**：本记录原以字面量记录服务器 IP（8 处），触发 audit-sensitive-info 第 2 节失败——已全部替换为 `<PROD_HOST>`（`.github-private/abnk-prod/config.json` 解析，ADR-010 轻规则口径：IP 字面量不落 public 仓）。⚠️ 已推送的 git 历史（f047242…e739710 区间）仍含字面量——IP 同时经公网 DNS（amazingbank.ai A 记录）对外可见，实际暴露面未扩大；是否重写 git 历史由用户裁决（生产部署工具集不主动 force-push public 仓）。

- ghcr 包可见性翻转需 GitHub UI 操作（用户/组织管理员）——匿名复验前完成
- dev 子域接入不改任何既有 server 块（纯增量 server 块 + 新服务）——对 api/app/bo/官网的回归面收敛为 `docker restart abnk-nginx`（秒级，全栈其余容器不 recreate）
- 首次发布后 portal 数据截至 = `.asdm` 本次推送 commit（页脚标注任务 4.4 接线）

## Phase B 执行记录（2026-11-17，真实输出）

| 步骤 | 命令/动作 | 结果 |
|---|---|---|
| B0 三仓提交推送 | portal `f7a923a`（容器化三文件）/ system `ad5f828`（dev 接入四文件）/ asdm `f047242`（Phase4 归档） | ✅ 全部推送 origin/main |
| B1 服务器三仓获取 | clone HTTPS 匿名 devportal + asdm；system `git pull` | ✅ 三 HEAD 与本地推送逐字一致；system porcelain 干净 |
| B2 服务器构建 | `docker build --build-context asdm=$HOME/source/abnk-asdm --build-context tokens=$HOME/source/abnk-system/channels/shared .` | ✅ exit 0；`✓ built in 10.26s`；镜像 200MB；evidence 435 文件（含当日归档）；服务器侧 sync 只读性证明真实成立（clone 为真 git 仓，porcelain 前后一致） |
| B3 push ghcr | `docker push ghcr.io/amazingbank/abnk-devportal:0.1.0` | ✅ digest `sha256:e7e589ddd40f9c75fbf24573dd3e52df5c233354cb3380ca1a198ad3edebc49b`；基础层 Mounted from abnk-website |
| B3′ 匿名可见性探测 | ghcr 匿名 token manifest GET | ⚠️ 403 = 包已创建但默认 private——**待用户 UI 翻转 Public**（V4.2.1 匿名复验前置） |
| B4 部署根 env | append `ABNK_DEVPORTAL_IMAGE=ghcr.io/amazingbank/abnk-devportal:0.1.0` | ✅ |
| B5 容器层起服务 | `compose up -d abnk-devportal`（单服务滚动） | ✅ `Up (healthy)`；镜像 = 0.1.0 FQN；经 abnk-nginx 容器反代链路 200（HTML 直出）+ 深链 `/timeline/part02` 200；**其余八容器零感知（Up ~1h 未 recreate）** |
| B6 公网接入 | `docker restart abnk-nginx` | ✅ 用户确认门②后执行；九容器全 healthy |
| **B7 0.1.1 修复发版** | 公网走查发现缺陷 → 修复 → 重建 | ✅ portal `294557a`；服务器构建 exit 0 → push 0.1.1 → `.env` sed 更新 → 单服务 recreate + 按纪律 `docker restart abnk-nginx`（portal 容器换 IP，2026-11-12 nginx upstream 缓存纪律） |

## V4.2.1–V4.2.4 验收结果（终态）

| 步骤 | 结果 |
|---|---|
| V4.2.1 镜像发布 | ✅ 服务器侧构建 + push（0.1.0 / 0.1.1 双 tag）；匿名 manifest 复验双 200（用户翻转 Public 后）；tag 入本记录 |
| V4.2.2 子域接入与两阶段发布 | ✅ 容器层 200（经 abnk-nginx 反代链路 + 深链 200，其余八容器零感知）→ 用户确认 → 公网反代接入（restart 入口） |
| V4.2.3 公网上线终验 | ✅ `https://dev.amazingbank.ai/` HTTP/2 200；双语切换真实成立（UI 点击「切换语言」→ `/en-us/` + 英文标题）；四层下钻真实路由（`/zh-cn/timeline/part04/task/4.1`，Part04 任务 4.1/4.2 卡片在列——**叙事闭环成立**）；指标页/证据浏览 200；证据资产公网直供 200 + manifest 200；console 0 error；回归面（website/api/app/bo 四子域）全 200；截图 7 张归档 `screenshots/`（**Part04 核心交付达成——dev portal 上线**） |
| V4.2.4 回滚演练 | ✅ 服务器 `docker pull ghcr.io/amazingbank/abnk-devportal:0.1.0` 成功（首版 tag 可达，双 tag 201MB 在位缓存；不实际切换） |

> 走查过程发现并当日修复：0.1.0 的 `/evidence` 路由遮蔽缺陷（见「0.1.1 修复」节）——「先于生产暴露路由层缺陷」在公网终验环节兑现（0.1.0 在线窗口约 1 小时）。
> 数据新鲜度如实口径：portal 内容截至 abnk-asdm `f047242`（含 4.1 收口 + 4.2 Phase A 记录）；index 产出物上次生成于 Phase 3 收口——任务级状态以 index 时点为准（4.4 手册固化「index 再生成 → commit → 重发布」更新链）。
