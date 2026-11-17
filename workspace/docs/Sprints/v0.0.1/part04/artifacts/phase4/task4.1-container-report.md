---
sprint: v0.0.1
part: part04
phase: 4
status: completed
date: 2026-11-17
evidence: ../
locale: zh-CN
---
# 任务 4.1 —— 容器化（多阶段构建 + nginx 静态直供）执行记录

- 日期：2026-11-17；执行人：AI（abnk-debugger 会话）
- 定位：Phase 3 产物的可部署/可回滚/可复现形态——复刻 abnk-website 容器先例产出镜像；本地验证止于「容器跑通 + curl 200」（已知坑 1：本地构建镜像不 push 不发布，发布在 4.2 服务器侧执行）。

## 执行时决策记录

| 决策点 | 结论 | 依据 |
|---|---|---|
| 构建上下文形态（Phase4 文档授权「执行时定并记入 4.4 手册」） | **BuildKit 附加上下文双注入**：`--build-context asdm=../.asdm` + `--build-context tokens=../abnk-system/channels/shared`，主 context 仍为 `$PORTAL`（`.`） | 保持 `cd $PORTAL && docker build … .` 的 context 语义不变；容器内重建「并排多仓」布局（`/workspace/.asdm` + `/workspace/abnk-devportal` + `/workspace/abnk-system/channels/shared`），`sync-data.sh` 与 `tailwind.config.js` 的相对寻址原样运行——构建对数据源零提取逻辑、与宿主机未提交状态解耦（D4「构建纯复制」的容器化延续） |
| 第三数据源（执行中发现） | **首轮构建失败暴露 `tailwind.config.js` 的 design-tokens 依赖**（`../abnk-system/channels/shared/design-tokens.json`，fail-loud）；以第二附加上下文注入修复，context 根收敛到 shared 子目录（92K） | portal 构建实为三仓依赖（asdm 数据 + system tokens + 本仓代码）；README「两仓并排前置」未覆盖 tokens 链，容器化把隐性依赖显式化；不传输整个 abnk-system 仓 |
| 容器内 sync 的只读性证明 | 容器内 `.asdm` 为目录快照而非 git 仓——`git -C` 失败静默跳过，证明退化为平凡成立 | 真实只读性由宿主侧执行同一脚本时验证（脚本内建 porcelain 前后比对）；镜像确定性由 `.dockerignore` 排除 `src/data`/`public/evidence` 保证（数据唯一来源 = 构建内 sync） |
| runtime 镜像基座 | `nginx:1.27-alpine`（计划文写 nginx:alpine，取 website 先例同版本钉扎） | 版本可复现优先于浮动 tag；website Dockerfile 先例同为 1.27-alpine |
| nginx 拓扑 | **仅 :80 内容服务面**，不设 :443 块、不做 HTTP→HTTPS 301 | 公网 TLS 终止在 abnk-nginx 入口容器（dev 子域反代，website 先例第四次适用）；容器内 301 会造成无限重定向环（website 0.1.2/0.1.3 前车之鉴）；纯静态直供无需 compose TLS 自检面 |
| 证据缓存策略 | `/evidence/` 一天公共缓存（max-age=86400）；`/assets/` 一年 immutable；`index.html` no-store | 证据文件名非内容哈希、发布链手动重发——一天缓存平衡新鲜度与回源；对齐/回滚口径以镜像 tag 为准（4.4 手册） |

## 改动清单

| 类别 | 仓 | 文件 | 说明 |
|---|---|---|---|
| 新建 | abnk-devportal | `Dockerfile` | 多阶段：node:22-alpine（apk bash+rsync → npm ci → COPY 仓 → 双附加上下文注入 → `npm run sync && npm run build`）→ nginx:1.27-alpine（dist 直供，EXPOSE 80） |
| 新建 | abnk-devportal | `nginx.conf` | :80 单 server：SPA fallback + `/evidence/`、`/assets/` 分层缓存头 + gzip + 安全响应头（复刻 website :80 面形态） |
| 新建 | abnk-devportal | `.dockerignore` | 排除 node_modules/dist/src/data/public/evidence——数据唯一来源为构建内 sync（镜像确定性） |

## 执行与验收记录（真实输出）

### V4.1.1 容器构建 ✅

- 命令（实际执行形态，双附加上下文）：
  ```bash
  cd /Users/leixu/source/asdm/amazingbank-ws/abnk-devportal && \
    docker build -t abnk-devportal:local \
      --build-context asdm=../.asdm \
      --build-context tokens=../abnk-system/channels/shared . \
      > $ART/build-v4.1.1.log 2>&1
  ```
- 结果：`exit=0`
- 成功信号（构建日志摘录）：
  - `[build 5/12] RUN npm ci --no-audit --no-fund` ✅
  - `evidence OK: 四桶直供 public/evidence/（合计 433 文件，含全量截图），资产清单 manifest.json 已生成` ✅
  - `sync OK: 4 个映射已复制到 src/data/（index/sprints/planning/abnk-design/portal-content）+ 四桶证据素材直供 public/evidence/（任务 3.5 建基 / 3.6 泛化），源仓只读性成立` ✅
  - `vite v7.3.8 building client environment for production...` + `✓ built in 2.14s` ✅
- 镜像存在：`abnk-devportal:local`，size=117MB（116636135 bytes），created=2026-11-17T00:33:22Z
- 过程记录：首轮构建失败于 `npm run build`（tailwind design-tokens 缺失——见决策表「第三数据源」），修复后本輪通过；失败轮日志已覆盖，教训沉淀在 Dockerfile 头注释与决策记录。

### V4.1.2 本地容器冒烟 ✅（容器保留至 V4.1.3 收口）

- 命令：`docker run -d --name abnk-devportal-smoke -p 6280:80 abnk-devportal:local`
- 结果：容器 `Up`（`0.0.0.0:6280->80/tcp`）
- `curl -s -o /dev/null -w "%{http_code}" http://localhost:6280/` → **200**
- `curl -s http://localhost:6280/ | grep -ci portal` → **1**（≥ 1 达标）
- 端口选取：6280（ABNK 6200–6299 本地调试段，执行前 `lsof` 确认空闲）

### V4.1.3 SPA fallback 与资产直供验证 ✅（配对清理）

- 深链（SPA fallback）：`curl http://localhost:6280/timeline/part02` → **200**
- 证据资产直供：`curl http://localhost:6280/evidence/part02/phaseP1/screenshots/bo-05-loan-ops.png` → **200**
- 附带核验：`/evidence/manifest.json` → 200；根 HTML `Cache-Control: no-store` 生效（`curl -sI /` 响应头命中）
- 配对清理：`docker rm -f abnk-devportal-smoke` → 容器已移除（`docker ps -a` 计数 0——临时环境改变随本步收口）

## 验收结论

任务 4.1 三步骤（V4.1.1–V4.1.3）全过：镜像构建成功且数据链路（asdm 四分区 + tokens）容器内闭环、静态直供与深链 fallback 正确、证据资产路径形态正确。本地镜像 `abnk-devportal:local` 未 push（已知坑 1——发布动作在任务 4.2 服务器侧执行，过用户确认铁门）。

## 遗留与移交

- **构建上下文形态（双附加上下文）已在本报告定死**——任务 4.2 服务器侧构建沿用同一命令形态，任务 4.4 手册照此固化（Phase4 已知坑 7 的「服务器侧两仓获取形态」部分：实际形态为三仓并排 clone + 双附加上下文注入，服务器侧完整链路在 4.2 执行时补齐记录）。
- portal 仓新增三文件（Dockerfile/nginx.conf/.dockerignore）未提交——提交时机由用户决定（Phase4「提交时机」备注）。
