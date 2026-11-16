---
sprint: v0.0.1
part: part04
phase: 1
task: 1.2
status: completed
date: 2026-11-16
locale: zh-CN
---
# 任务 1.2 骨架验收记录 — portal 工程骨架与数据消费契约

> 执行环境：Node v22.23.1 / npm 10.9.8 / macOS；`$PORTAL` = `amazingbank-ws/abnk-devportal`（origin `git@github.com:amazingbank/abnk-devportal.git`，空仓 init）。前置复验：abnk-asdm 基线干净（porcelain = 0，任务 1.1 产出物已由用户提交入库）。

## V1.2.1 仓 init 与骨架三绿 ✅

- remote 核验：`git remote -v` 命中 origin（fetch/push 均指向 `git@github.com:amazingbank/abnk-devportal.git`），空工作树。
- 骨架落位（第三次同构复刻 abnk-website）：`package.json`（dev/build/lint/typecheck/preview/sync，npm）+ `vite.config.ts`（:6203/:6204，strictPort，ABNK_DEVPORTAL_PORT env）+ `tsconfig.{json,app,node}.json`（app 开 `resolveJsonModule`）+ `eslint.config.js`（+ node globals 段）+ `postcss.config.js` + `index.html` + `src/{main.tsx,App.tsx,index.css,vite-env.d.ts}` + `src/components/{Nav,Footer}.tsx` + `public/favicon.svg`。
- 三命令实测（2026-11-16）：`npm install` exit 0；`npm run typecheck` exit 0；`npm run lint` exit 0；`npm run build` exit 0（41 modules，dist 三产物 0.94 kB html / 9.01 kB css / 148.63 kB js）。
- 首跑修复记录：`build` 首跑失败于 `border-taupe/30`（taupe 族无 DEFAULT 档位，透明度修饰必须挂具体档位——design-tokens 契约）；改 `border-taupe-300/60` 后三绿。CSS 产物 9.01 kB 证明 tailwind 已消费 design-tokens.json（经 `ABNK_DEVPORTAL_TOKENS` env 覆盖机制，fail-loud）。

## V1.2.2 i18n 同构复刻就位 ✅

- `ls` 双侧比对（diff 零差异，MODULES_IDENTICAL）：`index.ts / interpolate.ts / locale.ts / locale-context.ts / locale-provider.tsx / locale-url.ts / resources.ts / use-locale.ts / locales/`——8 模块 + locales 目录同名同构。
- `locales/{zh-cn,en-us}/{common,home}.json` 双语骨架占位词条就位；`resources.ts` 保留 `Widen` + `satisfies` 编译期结构校验（en↔zh 键结构一致）。
- portal 差异（记录）：`DEFAULT_LOCALE = 'zh-cn'`（D3：内容 zh 全量主语言，与官网 en 优先相反）；`LOCALE_STORAGE_KEY = 'abnk-devportal-locale'`。

## V1.2.3 数据契约编译期校验（首个真实样本）✅

- `bash scripts/sync-data.sh` exit 0（3 映射复制 + 只读性证明内置）。
- 样例制备（一次性转换，非构建提取）：`python3 -c "import yaml,json; json.dump(...)"` → `src/data/sprint.sample.json`，exit 0。
- `sample.check.ts`：`import sprint from './sprint.sample.json'` + `import metrics from './index/metrics-v0.0.1.json'`，`satisfies Widen<SprintIndex>` / `satisfies Widen<Metrics>`（JSON import 字符串推断为宽 string，枚举值校验由生成器 fail-loud 词表承担——V1.1.7 已演示，两层互补零漂移面）。
- `npm run typecheck` exit 0（V123_TYPECHECK_OK）——任务 1.1 产出物通过契约，生成器与 schema 双侧口径一致。
- 结构事实核对（与 V1.1.2 首跑报告一致）：`parts=4 docs=24 tasks=74 moved_to=1`；metrics `adr=10 vp=34/34 unit=57/57 e2e=55/55 drift=0`。

## V1.2.4 sync 只读性证明（硬门）✅

- 基线：`git -C $ASDM status --porcelain | wc -l` → **0**（任务 1.1 产出物已入库，无遗留暂存条目）。
- 跑 `bash $PORTAL/scripts/sync-data.sh` → sync OK；复测同命令 → **0**（前后一致，READONLY_PROOF_OK）。
- 脚本内建同口径证明（porcelain 前后逐字节比对，破坏即 exit 2）。
- 复制清单（--check 干跑 + 实测统计归档）：

| 映射 | 源 | 目标 | 规模 |
|---|---|---|---|
| 1 | `../.asdm/workspace/index` | `src/data/index/` | 3 文件（sprint yaml + metrics/loc） |
| 2 | `../.asdm/workspace/docs/Sprints` | `src/data/sprints/` | 406 文件 / 28 MB（md 61 + 证据素材 345，排除 .DS_Store） |
| 3 | `../.asdm/workspace/docs/planning/abnk-design` | `src/data/planning/abnk-design/` | 42 文件 |

- 合计 29 MB；`--check` 干跑输出 3 映射清单未落盘，exit 0。

## V1.2.5 gitignore 双侧纪律相反的验证 ✅

- portal 侧：`.gitignore:19` 命中 `src/data/`；`git check-ignore src/data/sprint.sample.json` 输出确认拷贝产物被忽略。
- asdm 侧：`git check-ignore workspace/index` 无输出 → `tracked-ok`；`git ls-files workspace/index` 三产出物在跟踪清单。

## 最终态三绿复验 ✅

- `npm run typecheck && npm run lint && npm run build` 全部 exit 0（FINAL_THREE_GREEN，含 `schema.ts` + `sample.check.ts` 后的最终态）。
- devportal 仓 git 状态：15 条 untracked（骨架首个提交内容，提交时机由用户决定；`src/data/` 不在其中——gitignore 纪律生效）。

## 结论

任务 1.2 全部步骤（V1.2.1–V1.2.5）通过：abnk-devportal 工程骨架三绿、i18n 机制第三次同构复刻就位、消费契约 `schema.ts` 与生成器产出物互证成立、sync 只读复制链带证明闭环、双侧 git 纪律相反且各自就位。Phase 2/3 的数据消费前置（契约锁定）达成。
