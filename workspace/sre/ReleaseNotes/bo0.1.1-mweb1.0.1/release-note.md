# ABNK App Channels Release — bo 0.1.1 + mweb 1.0.1（Part03 i18n 双语全量）

**版本**：`abnk-bo:0.1.1` + `abnk-mweb:1.0.1`（ghcr 公共包）
**日期**：2026-11-12
**状态**：🟡 预部署（Phase A 完成，等待用户确认）
**分支**：`main`
**发版类型**：双服务滚动（bo + mweb 单服务 recreate；其余五容器零感知，无 down）

## 基线信息

| 仓库 | 本次基线（HEAD） | 新提交数（服务器基线 19bb0f6 起） |
|------|-----------------|---------|
| `abnk-system`（发版对象——bo/mweb 两渠道） | `aa020f7` | 11 commits（Part03 Phase 1–4 + P3.6 apk 修复等） |
| `abnk-asdm`（进度文档） | `8dba059` | — |

## 变更内容（Part03 双语 i18n 与中英切换，Phase 1–4）

- **backoffice**（Phase 1–2）：零依赖 i18n 体系（8 命名空间词条 + localStorage 事实源 + antd/dayjs 联动）、错误码化（ApiError + 双语 errors 词条）、mock 数据集双语两套 + 部署期切换（Vite 构建注入）
- **mobile-banking**（Phase 3–4）：gen-l10n 体系（ARB 双语，中文为源英文语义重写）、语言切换（AppState + shared_preferences 持久化）、fixtures 双语两套 + 编译期数据集选择（`--dart-define ABNK_DATA_LOCALE`）
- **本次发版拍板——应用数据默认英文**（D3 部署期决策）：两 Dockerfile ARG 缺省与部署 env 均为 `en-us`；运行时 UI 语言切换不切数据集（UI 语言仍各自跟随用户选择/系统语言）
- **版本递增**（Iron Rule 4 patch 纪律）：bo `0.1.0→0.1.1`（package.json）、mweb `1.0.0+1→1.0.1+2`（pubspec，build number 不入 tag）

## 环境就绪检查（Phase A 实测 2026-11-12）

| 检查项 | 状态 |
|--------|------|
| Step 0 敏感信息审计（6 节） | ✅ 通过（含 l10n arb 误报白名单修正 1 项，`.github-private` 615b63c） |
| Step 1 双仓干净已推送 | ✅ abnk-system `aa020f7` / abnk-asdm `8dba059`（origin/main..HEAD = 0） |
| Step 2 版本确定 | ✅ bo `0.1.1` / mweb `1.0.1`（不与运行中 tag 复用：在产 0.1.0 / 1.0.0） |
| Step 3 SSH/Docker | ✅ SSH OK；Docker 29.9.2 / Compose v5.6.1 |
| Step 3 磁盘/内存 | ✅ 102G 可用 / 5.1Gi 可用 |
| Step 3 端口 80/443 | ✅ abnk-nginx 入口占用（正常态） |
| Step 3 部署根 env | ✅ `~/deploy/.env` 在位（ABNK_DEPLOY_ROOT=/home/azureuser/deploy） |
| Step 3 TLS 证书 | ✅ notAfter 2027-05-12（> 30 天） |
| Step 3 七容器现状 | ✅ 全部 Up (healthy)；在产镜像 bo:0.1.0 / mweb:1.0.0 |

## 部署命令（Phase B 在服务器执行）

```bash
# 1) git pull + HEAD 核对（必须 = aa020f7）
cd ~/source/abnk-system && git checkout main && git pull origin main && git log --oneline -1

# 2) 服务端构建两镜像（x86_64 原生；数据集英文显式注入——D3 部署期决策）
docker build -f channels/backoffice/Dockerfile \
  -t ghcr.io/amazingbank/abnk-bo:0.1.1 \
  --build-arg ABNK_DATA_LOCALE=en-us channels/backoffice
docker build -f channels/mobile-banking/Dockerfile \
  -t ghcr.io/amazingbank/abnk-mweb:1.0.1 \
  --build-arg ABNK_DATA_LOCALE=en-us channels/mobile-banking

# 3) push ghcr（公共包；禁止覆盖既有 tag）
docker push ghcr.io/amazingbank/abnk-bo:0.1.1
docker push ghcr.io/amazingbank/abnk-mweb:1.0.1

# 4) 部署根 .env 更新（sed 原位替换三行：两镜像 tag + 数据语言决策记录）
sed -i.bak 's|^ABNK_BO_IMAGE=.*|ABNK_BO_IMAGE=ghcr.io/amazingbank/abnk-bo:0.1.1|' ~/deploy/.env
sed -i.bak 's|^ABNK_MWEB_IMAGE=.*|ABNK_MWEB_IMAGE=ghcr.io/amazingbank/abnk-mweb:1.0.1|' ~/deploy/.env
grep -q '^ABNK_DATA_LOCALE=' ~/deploy/.env && sed -i 's|^ABNK_DATA_LOCALE=.*|ABNK_DATA_LOCALE=en-us|' ~/deploy/.env || echo 'ABNK_DATA_LOCALE=en-us' >> ~/deploy/.env
rm -f ~/deploy/.env.bak

# 5) 双服务滚动 up（无 down；tag 变化触发 bo/mweb recreate，其余五容器零感知）
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-bo abnk-mweb

# 6) 验证：七容器 healthy + bo/app/api 公网探活 + 数据语言抽查（英文数据串在 bundle）
docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml ps
curl -s -o /dev/null -w 'bo: %{http_code}\n' https://bo.amazingbank.ai/
curl -s -o /dev/null -w 'app: %{http_code}\n' https://app.amazingbank.ai/
curl -s https://api.amazingbank.ai/actuator/health
curl -s https://bo.amazingbank.ai/ | grep -c "ABNK Current Savings"   # ≥1 = 英文数据集已烘焙
docker exec abnk-mweb sh -c "grep -c 'ABNK Fixed Deposit' /usr/share/nginx/html/assets/fixtures/en-us/accounts.json || grep -rl 'en-us' /usr/share/nginx/html/main.dart.js"
```

## 回滚预案（与 Step 5 同式镜像切换，无数据迁移）

```bash
sed -i.bak 's|^ABNK_BO_IMAGE=.*|ABNK_BO_IMAGE=ghcr.io/amazingbank/abnk-bo:0.1.0|;s|^ABNK_MWEB_IMAGE=.*|ABNK_MWEB_IMAGE=ghcr.io/amazingbank/abnk-mweb:1.0.0|' ~/deploy/.env && rm -f ~/deploy/.env.bak \
  && cd ~/source/abnk-system && docker compose --env-file ~/deploy/.env \
  -f deploy/prod/compose-abnk-prod.yaml up -d abnk-bo abnk-mweb
```

## 执行进度跟踪

- [x] ✅ Step 0：敏感信息审计（6 节全过）
- [x] ✅ Step 1：双仓干净已推送（abnk-system HEAD: `aa020f7`）
- [x] ✅ Step 2：版本确定（bo `0.1.1` / mweb `1.0.1`）
- [x] ✅ Step 3：服务器就绪（SSH/Docker/磁盘/端口/证书/七容器/在产 tag）
- [x] ✅ Step 4：Release Note 生成 → ⏸ **IRON GATE：等待用户「确认发版」**
- [ ] ⬜ Step 5：服务器 git pull + HEAD 核对（= aa020f7）
- [ ] ⬜ Step 6：docker build + push（bo 0.1.1 / mweb 1.0.1，数据集 en-us）
- [ ] ⬜ Step 7：.env 三行更新 + 双服务滚动 up
- [ ] ⬜ Step 8：部署验证（七容器 + 三子域 + 数据语言抽查）
- [ ] ⬜ Step 9：Release Note 回填 + commit

## 风险与备注

- **中断窗口**：仅 bo/mweb 两静态站各自 recreate 的秒级窗口；官网/网关/Fineract/PG 零感知。
- **数据默认英文**：bo bundle 仅含 en-us 数据集（Vite tree-shaking 判据已在 Phase 2 V2.2.3 双向验证）；mweb 双集进包、编译期选择（define 传播两向测试 V4.2.5 已验）。
- **ghcr 挂账沿存**：org 包可见性 public 的网页操作挂账（VP3.5.4）不阻塞——服务器本地构建后 up 直接命中本地镜像。
- **Flutter 构建时长**：mweb 约 4 分钟（SDK 归档缓存命中后更快）；bo 约 1 分钟。
