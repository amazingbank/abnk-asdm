---
sprint: v0.0.1
part: part04
phase: 4
status: completed
date: 2026-11-17
evidence: ../
locale: zh-CN
---
# 任务 4.4 —— 发布手册与数据更新链固化（CI 未实跑期间的发布唯一事实源）

- 日期：2026-11-17；执行人：AI（abnk-debugger 会话）
- 定位：portal 发布是**手动链**（CI workflow 属 roadmap，未实跑——如实口径）。本手册**复述**任务 4.1–4.3 实际执行过的命令链（零臆造——每段命令可在 `task4.1-container-report.md` / `task4.2-release-record.md` 找到执行记录与真实输出），是数据更新与发版的可复现性保障。
- 服务器侧三仓获取形态（已知坑 7 定形）：abnk-asdm / abnk-devportal 两 public 仓 = **HTTPS 匿名 clone**（`~/source/` 下，零新增凭证面）；abnk-system 既有 SSH deploy key clone（`git pull` 对齐）。

## 一、发布前置（每次必查）

```bash
# 0) 敏感信息审计（prod-deploy Step 0 强制门，失败即中止）
bash .github-private/abnk-prod/scripts/audit-sensitive-info.sh          # 期望 exit 0（6 节全过）

# 1) 三仓干净且已推送（portal / system / asdm——HEAD 必须已到 origin/main）
git -C abnk-devportal status --short && git -C abnk-system status --short && git -C .asdm status --short   # 期望全空
```

## 二、本地校验（发布前门槛，零生产影响）

```bash
cd abnk-devportal
bash scripts/sync-data.sh                 # 期望尾行 sync OK + data-as-of OK（index 最后 commit 哈希与日期——页脚标注的源头）
npm run typecheck && npm run lint         # 期望双 exit 0
rm -rf dist && npm run build              # 期望 ✓ built（⚠️ IDE safe-delete shim 会拦截 vite 批量清空旧 dist（>500 文件）——先手动清空或 mv 旧 dist 再构建）
grep -o "数据截至 {date}（index commit {commit}）" dist/assets/index-*.js   # 期望命中（页脚词条已进产物）
```

> 版本与 tag：tag 源 = `package.json` version（website Iron Rule 4 同口径）；**发布前 patch 递增**（0.1.0 → 0.1.1 → 0.1.2），**禁止覆盖已推送 tag**（已知坑 2；回滚靠拉历史 tag）。

## 三、服务器三仓获取与基线核对

```bash
# 首次（两 public 仓不在服务器时）
ssh azureuser@<PROD_HOST> "git clone --quiet https://github.com/amazingbank/abnk-devportal.git ~/source/abnk-devportal \
  && git clone --quiet https://github.com/amazingbank/abnk-asdm.git ~/source/abnk-asdm"

# 每次（三仓对齐到本地推送的 HEAD——漂移即中止）
ssh azureuser@<PROD_HOST> "cd ~/source/abnk-devportal && git pull --quiet origin main && git log --oneline -1 \
  && cd ~/source/abnk-asdm && git pull --quiet origin main && git log --oneline -1 \
  && cd ~/source/abnk-system && git pull --quiet origin main && git log --oneline -1"
```

## 四、构建与发布（⚠️ 生产铁门：push / compose 切换前问用户）

```bash
# 1) 服务器构建（x86_64 原生；BuildKit 双附加上下文——asdm 数据 + system tokens）
ssh azureuser@<PROD_HOST> 'cd ~/source/abnk-devportal && docker build \
  -t ghcr.io/amazingbank/abnk-devportal:<version> \
  --build-context asdm=$HOME/source/abnk-asdm \
  --build-context tokens=$HOME/source/abnk-system/channels/shared . 2>&1 | tail -5'
# 期望：✓ built in …s（构建内 npm ci → npm run sync（含 data-as-of 锚点捕获 + 只读性证明，容器内 .git 真实运行）→ vite build）

# 2) 【用户确认后】push ghcr 公共包（D5 口径；首次推送新包需在 GitHub UI 翻转 Public）
ssh azureuser@<PROD_HOST> 'docker push ghcr.io/amazingbank/abnk-devportal:<version>'
# 匿名复验（本机 ghcr 已登录时用 token manifest 探测代匿名）：
curl -s "https://ghcr.io/token?scope=repository:amazingbank/abnk-devportal:pull" …   # 期望 manifest GET 200

# 3) 部署根 .env 更新镜像 tag（首版 append，此后 sed 原位替换）
ssh azureuser@<PROD_HOST> 'sed -i.bak "s|^ABNK_DEVPORTAL_IMAGE=.*|ABNK_DEVPORTAL_IMAGE=ghcr.io/amazingbank/abnk-devportal:<version>|" ~/deploy/.env && rm ~/deploy/.env.bak'

# 4) 【用户确认后】单服务滚动 up（其余容器零感知）+ 按纪律重启入口 nginx
ssh azureuser@<PROD_HOST> 'cd ~/source/abnk-system && \
  docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-devportal \
  && docker restart abnk-nginx'
# ⚠️ restart abnk-nginx 必做（2026-11-12 纪律：滚动 recreate 换容器 IP，nginx upstream 缓存陈旧会错路由；亦加载 server 块变更）
```

## 五、上线验证

```bash
# 容器层（公网接入前）
ssh azureuser@<PROD_HOST> 'docker exec abnk-nginx wget -q -S -O /dev/null http://abnk-devportal:80/ 2>&1 | grep "HTTP/1.1 200"'

# 公网（本机）
curl -sI https://dev.amazingbank.ai/ | head -1                                   # 期望 HTTP/2 200
for p in "/" "/zh-cn" "/zh-cn/timeline/part04/task/4.1" "/zh-cn/metrics" "/zh-cn/evidence"; do
  curl -s -o /dev/null -w "$p -> %{http_code}\n" "https://dev.amazingbank.ai$p"; done   # 期望全 200（真实路由；SPA reset 假阳性排除——下钻走 UI 点击）
curl -s -o /dev/null -w "evidence=%{http_code}\n" https://dev.amazingbank.ai/evidence/part02/phaseP1/screenshots/bo-05-loan-ops.png   # 期望 200
# 回归面（既有子域不受影响）
for h in amazingbank.ai app.amazingbank.ai bo.amazingbank.ai; do curl -s -o /dev/null -w "$h %{http_code}\n" https://$h/; done        # 期望全 200
# 页脚数据截至标注（V4.4.2 判据）：dev.amazingbank.ai 页脚日期 == 服务器 asdm clone 的 workspace/index 最后 commit 日期
ssh azureuser@<PROD_HOST> 'git -C ~/source/abnk-asdm log -1 --format="%cd %h" --date=short -- workspace/index'
# 界面走查（双语/下钻/console）用 playwright-cli，截图归档 $ART/screenshots/
```

> 已知路由坑（0.1.0 实测沉淀）：`dist/evidence` 物理目录会遮蔽同名 SPA 路由（目录 301 → 资产 location =404）——portal nginx.conf 已修（SPA fallback 无 `$uri/` + 尾斜杠规范重定向 + `absolute_redirect off`）；排查时先试裸 `/evidence` 与 `/evidence/` 两种形态。

## 六、回滚链（与 Step 四.4 同式，仅镜像切换）

```bash
ssh azureuser@<PROD_HOST> 'sed -i.bak "s|^ABNK_DEVPORTAL_IMAGE=.*|ABNK_DEVPORTAL_IMAGE=ghcr.io/amazingbank/abnk-devportal:<previous-version>|" ~/deploy/.env && rm ~/deploy/.env.bak \
  && cd ~/source/abnk-system && docker compose --env-file ~/deploy/.env -f deploy/prod/compose-abnk-prod.yaml up -d abnk-devportal \
  && docker restart abnk-nginx'
# 历史 tag 可达性（回滚演练，只验不切）：docker pull ghcr.io/amazingbank/abnk-devportal:<previous-version>
# 无数据库/状态迁移——回滚即镜像切换，无需数据恢复；首版（0.1.0）即回滚锚点
```

## 七、数据更新触发条件（何时重发布）

| 触发事件 | 动作 | 说明 |
|---|---|---|
| abnk-asdm 仓 index 产出物变更（`workspace/index/*`——生成器重跑 + commit） | 全链重发布（四→五节） | 页脚「数据截至」自动刷新（sync 捕获新 commit）；**生成器重跑是 asdm 仓动作**：`.asdm/scripts/` 生成器 → `--verify` 三产物齐核 → commit → push |
| abnk-asdm 内容变更（Sprints 文档 / 证据素材 / planning / portal-content） | 全链重发布 | 服务器 `git pull` 三仓后构建即纳入（含 public/evidence 四桶与 manifest 守恒计数刷新） |
| portal 仓代码变更（组件/样式/路由） | patch 递增 + 全链重发布 | 本地二节门槛先过；tag 不可覆盖 |
| 仅想刷新数据、零代码变更 | 服务器 pull asdm + 重建（tag 仍须递增） | 镜像内数据 = 构建时快照（D4 build-time 静态）；「数据截至」= index 最后 commit，如实标注 |

> CI 自动化（roadmap）：以上链路全部可脚本化，但当前**未实跑**——本手册即过渡期唯一事实源（D6 诚实性：不虚标 CI）。
