# ABNK Website — Release Notes

**版本**：`0.1.5`（镜像 tag，= abnk-website 仓 package.json version）
**日期**：2026-11-17
**状态**：✅ 已完成（Phase B 部署与验证全过，2026-11-17）
**分支**：`main`

## 基线信息

| 仓库 | 本次基线（HEAD） | 新提交数 |
|------|-----------------|---------|
| `abnk-website`（主仓，发版对象） | `86e73b2` | 2 commits（`8bc3fe8` CTA + `86e73b2` bump） |
| `abnk-system`（从仓，编排引用——无变更） | `ad5f828` | 0（未变） |

## 变更内容

- `8bc3fe8` **feat(website): Asdm/OpenSource 板块新增 Dev Portal CTA**（Part04 任务 4.3）
  - `src/components/sections/Asdm.tsx` / `OpenSource.tsx`：板块尾各加一句文案 + `https://dev.amazingbank.ai` 外链（`target=_blank` + `noopener noreferrer`）
  - `src/i18n/locales/{zh-cn,en-us}/home.json`：`asdm` / `openSource` 键下新增 `portalCta`（en 语义重写，零新建命名空间）
  - 本地验证：typecheck / lint / build 三绿；dev server 双语渲染 + 点击穿透实测（新标签打开活域名）
- `86e73b2` chore(website): bump version 0.1.4 → 0.1.5

## 部署命令（Phase B 在服务器执行）

```bash
# Step 5 pull + 核对
ssh <PROD_SSH> "cd ~/source/abnk-website && git checkout main && git pull origin main && git log --oneline -1"   # 必须 = 86e73b2
# Step 6 构建 + push（ghcr 私有包——服务器已 docker login）
ssh <PROD_SSH> "cd ~/source/abnk-website && docker build -t ghcr.io/amazingbank/abnk-website:0.1.5 . 2>&1 | tail -10 && docker push ghcr.io/amazingbank/abnk-website:0.1.5"
# Step 7 .env tag 更新 + 单服务滚动 up
ssh <PROD_SSH> "sed -i.bak 's|^ABNK_WEBSITE_IMAGE=.*|ABNK_WEBSITE_IMAGE=ghcr.io/amazingbank/abnk-website:0.1.5|' ~/deploy/.env && grep '^ABNK_WEBSITE_IMAGE' ~/deploy/.env && rm ~/deploy/.env.bak \
  && cd ~/source/abnk-system && docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-website"
# + docker restart abnk-nginx（滚动 up 后强制纪律——nginx upstream 缓存）
```

## 执行进度跟踪

- [x] ✅ Step 0：敏感信息审计（6 节全过——本轮拦截 1 项生产 IP 字面量泄漏并已清除，复跑通过）
- [x] ✅ Step 1：双仓干净已推送（abnk-website HEAD: `86e73b2`；abnk-system 无变更）
- [x] ✅ Step 2：版本确定（`0.1.5`，运行中 0.1.4 → patch 递增，无 tag 复用）
- [x] ✅ Step 3：服务器就绪（SSH/Docker 29.9.2/磁盘 94G/端口 80·443 入口绑定/证书 2027-05-12/部署根 .env 在位/DNS 已验证）
- [x] ✅ Step 5：服务器 git pull + HEAD 核对（abnk-website = `86e73b2`，漂移零）
- [x] ✅ Step 6：docker build + push（ghcr 私有包，digest `sha256:a5b759d0…`）
- [x] ✅ Step 7：.env tag 更新（0.1.4 → 0.1.5）+ 单服务滚动 up abnk-website + restart abnk-nginx（其余容器 15h 未动零感知）
- [x] ✅ Step 8：部署验证（见下方验证结果）
- [x] ✅ Step 9：Release Note 回填 + commit

## 部署验证结果（2026-11-17 实测）

| 检查项 | 结果 |
|---|---|
| 运行镜像 | `ghcr.io/amazingbank/abnk-website:0.1.5`（docker inspect） |
| 容器状态 | 九容器全 healthy（abnk-website recreate 后 Up；其余 15h 未动） |
| HTTPS apex / www | 200 / 200；HTTP → 301（无重定向环） |
| 首页 title | `Amazing Bank（ABNK）— 一家银行，也是一个范本` |
| **CTA 上线核验** | 线上 bundle `/assets/index-Cd_0gaZk.js` 命中 `dev.amazingbank.ai` ×1（与本地构建同哈希——确定性构建互证）；Asdm/OpenSource 板块双语 CTA 生效 |
| 回归面 | api（health 200）/ app 200 / bo 200 / dev.amazingbank.ai 200 全过 |

## 环境就绪检查

| 检查项 | 状态 |
|--------|------|
| 敏感信息审计 | ✅（含本轮拦截处置：part04 发布记录 IP 字面量清除 + git 历史残留声明——用户已知悉） |
| TLS 证书（有效期/modulus） | ✅ notAfter 2027-05-12（*.amazingbank.ai） |
| DNS（amazingbank.ai / www） | ✅ 已生效（此前发布验证） |
| 端口 80/443 | ✅ abnk-nginx 入口绑定（八容器 healthy） |
