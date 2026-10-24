# Amazing Bank 工作区说明

> 本文档面向 **Amazing Bank（ABNK）开发者**，介绍 `amazingbank-ws` 工作区的整体结构与快速启动路径，帮助新成员（含 AI coding agent）快速开展 ABNK 的日常开发与调试工作。

---

## 1. 工作区总览

`amazingbank-ws` 是一个**容器目录**（本身不是 git 仓库），将 Amazing Bank IT 系统开发所需的资源集中管理。各子目录独立管理（各自是独立的 git 仓库或运行时生成目录）。

```
amazingbank-ws/
├── .asdm/                        # ABNK 项目资产仓库（工具集 + 规划文档），独立 git 仓库
│   ├── README.md                 #   本文件（工作区说明）
│   ├── toolsets/                 #   AI agent 工具集
│   │   └── abnk-harness-toolset/ #     调试工具集（abnk-debugger）
│   │       ├── manifest.json     #       工具集元数据（guid / registry_id / commands）
│   │       ├── config.json       #       ★ ABNK 环境单一事实源（进程 / 端口 / 鉴权 / 端点）
│   │       ├── README.md         #       工具集说明
│   │       ├── INSTALL.md        #       安装指南（JDK 25 / VS Code / 快捷命令）
│   │       ├── actions/          #       动作指令
│   │       │   └── abnk-debugger.md
│   │       └── specs/            #       内部规范
│   │           ├── process-management-spec.md
│   │           ├── log-reading-spec.md
│   │           ├── log-augmentation-spec.md
│   │           └── fix-scheduling-spec.md
│   └── workspace/                #   工作区文档
│       └── docs/
│           └── planning/         #     Amazing Bank 规划文档
│               └── abnk-design/  #       产品 / 架构 / 数据模型 / 运行治理 / 演进
├── abnk-system/                  # 基础设施编排（阶段一 = PostgreSQL）
│   └── deploy/
│       ├── docker-compose.yml    #   abnk-pg 服务（项目名固定 abnk-system）
│       ├── .env                  #   环境变量默认值
│       └── README.md             #   命令与两条硬约束说明
├── .codebuddy/                   # CodeBuddy 快捷命令（工作区根，非 git 管理）
├── fineract/                     # ABNK 核心代码仓库（amazingbank/fineract，develop 分支）
└── logs/                         # 运行时日志（fineract.log + postgres.log + PID），运行时生成
```

**目录速查表：**

| 目录 | 性质 | 用途 | 是否必需 |
|---|---|---|---|
| `.asdm` | git 仓库（github.com:amazingbank/amazingbank-asdm） | 工具集、规划文档 | 必需 |
| `abnk-system` | git 仓库（github.com:amazingbank/abnk-system） | **基础设施编排**（当前仅 PostgreSQL compose，含 Kafka/Keycloak 接入模板） | 必需 |
| `fineract` | git 仓库（github.com:amazingbank/fineract，develop） | **ABNK 核心账务引擎**（当前阶段唯一代码仓库） | 必需 |
| `.codebuddy` | 非 git | CodeBuddy `/abnk-debugger` 快捷命令 | 推荐 |
| `logs` | 运行时生成 | 栈进程日志与 PID | 自动生成 |

> **`abnk-system` 必须克隆到 `amazingbank-ws/abnk-system/`**。其 `deploy/.env` 里 `ABNK_LOGS_DIR=../../logs` 是相对 compose 文件位置解析的（PostgreSQL 日志要落到工作区统一的 `logs/postgres.log`，与 `logs/fineract.log` 并列，`abnk-debugger` 依赖该布局）。放在别的路径就把该变量改成绝对路径。

---

## 2. 项目背景

**Amazing Bank（ABNK）** 的目标是基于 **Apache Fineract** 构建完整的银行 IT 系统。

- **Fineract** 是 Apache 顶级开源项目、成熟的核心银行系统（core banking），提供客户 / 存款 / 贷款 / 会计 / 报表 / 多租户 / 批处理作业等完整能力，被全球众多数字银行与微金融机构使用。
- 本工作区持有其 fork（`amazingbank/fineract`，`develop` 分支），是 ABNK 的演进基线。
- **当前阶段目标**：先确保 Fineract 在本机可运行、可断点调试，作为后续一切工作的前提。

**Fineract 关键事实（已核实）**：

| 项 | 值 | 位置 |
|---|---|---|
| 构建 | Gradle 9.7.1（wrapper） | `gradle/wrapper/gradle-wrapper.properties` |
| **JDK** | **25（toolchain 硬要求）** | `build.gradle:418` |
| 启动类 | `org.apache.fineract.ServerApplication`（fineract-provider） | `fineract-provider/build.gradle:326` |
| 形态 | Spring Boot + 内嵌 Tomcat（无需外部容器） | `ServerApplication.java` |
| 端口 | 8443，默认强制 HTTPS（自签 `keystore.jks`） | `application.properties:480,484` |
| 数据库 | PostgreSQL（MariaDB/MySQL 已废弃）+ 两个库 | `application.properties:503-506` |
| 迁移 | Liquibase，随启动自动执行 | `application.properties:532-533` |
| 快速启动 | `./gradlew devRun`（跳过质量门禁） | `fineract-provider/build.gradle:449` |
| 默认鉴权 | Basic Auth `mifos:password` | `README.md:102` |

---

## 3. 快速启动（从零到可调试）

### 前置条件

- **JDK 25**（硬门槛，见下）
- **Docker Desktop**（PostgreSQL 容器宿主）
- 本机无本地 PostgreSQL 服务——一律走容器

### 步骤一：安装 JDK 25

> ⚠️ **`sdk install java <ver>` 在本机必定失败**（sdkman 处理不了 Adoptium 的 307→302 双重跳转，报 `The archive was corrupt`）。改用 curl 直取 + 本地安装，见 `toolsets/abnk-harness-toolset/INSTALL.md` 第 3 节。

```bash
curl -L --max-time 600 -o /tmp/jdk25-tem.tar.gz \
  "https://api.adoptium.net/v3/binary/latest/25/ga/mac/aarch64/jdk/hotspot/normal/eclipse"
cd /tmp && tar -xzf jdk25-tem.tar.gz

export SDKMAN_DIR="$HOME/.sdkman"; source "$HOME/.sdkman/bin/sdkman-init.sh"
printf 'n\n' | sdk install java 25.0.5+8-tem /tmp/jdk-25.0.5+8/Contents/Home

# ⚠️ 上一步只是软链到 /tmp（会被系统清理），必须移到永久位置
rm -f ~/.sdkman/candidates/java/25.0.5+8-tem
mv /tmp/jdk-25.0.5+8/Contents/Home ~/.sdkman/candidates/java/25.0.5+8-tem

~/.sdkman/candidates/java/25.0.5+8-tem/bin/java -version   # 25.x
java -version                                                # 仍为 21——全局未被污染
```

> 不要 `sdk default`，以免污染本机 17/21 项目。目录级隔离见 `fineract/.sdkmanrc`。

### 步骤二：起数据库并建库

数据库由 `abnk-system/deploy/docker-compose.yml` 声明式管理：

```bash
docker info >/dev/null 2>&1 || open -a Docker    # 守护进程未起时先拉起 Docker Desktop
cd abnk-system/deploy
docker compose up -d                              # 项目名已固定为 abnk-system
cd ../..

# 建两个库（首次）
cd fineract
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  ./gradlew createPGDB -PdbName=fineract_tenants
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  ./gradlew createPGDB -PdbName=fineract_default
cd ..
```

> **两个易踩的坑**
> 1. 数据卷必须挂 `/var/lib/postgresql`（父目录），**不能**挂 `/var/lib/postgresql/data`——PostgreSQL 18+ 改用版本化子目录，挂错启动即失败。
> 2. compose 文件必须显式写 `name: abnk-system`——否则项目名取目录名 `deploy`，会与 AOS 等项目的 `deploy/` 撞名，`down`/`--remove-orphans` 会误停人家的容器。
>
> 容器账号刻意用 `root` / `postgres`，与 Fineract 代码默认值三方对齐，**零环境变量覆盖**即可跑通。

### 步骤三：启动 Fineract

```bash
mkdir -p logs
cd fineract
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  nohup ./gradlew devRun > ../logs/fineract.log 2>&1 &
echo $! >> ../logs/debug-process.pid
cd ..

# 等就绪（勿中断——中断会破坏 Liquibase changelog 账本）
for i in $(seq 1 1800); do grep -q "APACHE FINERACT IS READY" logs/fineract.log && break; sleep 1; done
grep "APACHE FINERACT IS READY" logs/fineract.log
```

> **实测耗时**（2026-10-24，M-series 12 核 / 64 GB）：`createPGDB` 首次 3m59s（含 Gradle 9.7.1 分发包下载）；`devRun` 到 READY 约 4.5 min（此时依赖已由 createPGDB 预热缓存），`Started ServerApplication in 82.6 seconds`。完全冷启动会更久，耐心等待，**中途不要 Ctrl-C**。
>
> 注意 `logs/debug-process.pid` 记录的是 Gradle 客户端 PID，**不是** Spring Boot 应用进程——`devRun` 会 fork 独立 JVM。停机一律按端口：`lsof -ti:8443 -sTCP:LISTEN | xargs kill`。

### 步骤四：验证

```bash
# 健康检查（自签证书必须 -k）
curl -sk https://localhost:8443/fineract-provider/actuator/health
# 期望：{"status":"UP","groups":["liveness","readiness"]}

# 业务 API（必须带租户头 + Basic Auth）
curl -sk https://localhost:8443/fineract-provider/api/v1/clients \
  -H 'Fineract-Platform-TenantId: default' \
  -H 'Authorization: Basic bWlmb3M6cGFzc3dvcmQ='
# 期望：{"totalFilteredRecords":0,"pageItems":[]}
```

### 步骤五：断点调试（可选）

```bash
# 1) 用 --debug-jvm 启动
cd fineract
JAVA_HOME="$HOME/.sdkman/candidates/java/25.0.5+8-tem" \
  nohup ./gradlew devRun --debug-jvm > ../logs/fineract.log 2>&1 &
cd ..
lsof -i:5005 -sTCP:LISTEN     # 确认 JDWP 口在监听

# 2) VS Code：打断点 → 打开 .vscode/launch.json 的 "Attach Fineract (:5005)" → F5
```

---

## 4. 调试工具集：abnk-debugger

```shell
/abnk-debugger <描述问题>
```

按 `.asdm/toolsets/abnk-harness-toolset/INSTALL.md` 安装后即可使用。工具集结构：

```
.asdm/toolsets/abnk-harness-toolset/
  - manifest.json                 # 工具集元数据
  - config.json                   # ABNK 环境配置（进程 / 端口 / 鉴权 / 端点）——单一事实源
  - README.md / INSTALL.md
  - actions/abnk-debugger.md      # 主调试 action（自驱循环）
  - specs/                        # 进程管理 / 日志读取 / 日志增强 / 修复调度
```

**设计要点**：`config.json` 驱动。Amazing Bank 后续接入的每个系统（前端 / Keycloak / Kafka / 自有业务服务）只需在 `processes[]` 追加一条，`abnk-debugger` 自动驱动整个栈，**action 文档无需改动**。

---

## 5. 日常工作提示

- **代码开发** → 在 `fineract/` 中进行；设计与规划文档见 `.asdm/workspace/docs/planning/`
- **调试排障** → 优先用 `/abnk-debugger`，日志集中在 `logs/`
- **改代码后** → Java 无 HMR，必须 `lsof -ti:8443 -sTCP:LISTEN | xargs kill` 后重启
- **杀进程** → 一律按端口（Gradle 会 fork JVM，杀 PID 杀不掉应用）
- **提交前** → `devRun` 会跳过质量门禁，提交前另跑 `./gradlew spotlessApply checkstyleMain`
- **扩展栈** → 新系统登记到 `.asdm/toolsets/abnk-harness-toolset/config.json`

---

*维护说明：本文档随工作区结构演进同步更新，修改请提交至 `amazingbank-asdm` 仓库（即 `.asdm`）。*
