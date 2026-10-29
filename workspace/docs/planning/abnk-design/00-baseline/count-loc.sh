#!/usr/bin/env bash
# Fineract 代码库分类行数统计
# 用法: ./count-loc.sh [fineract 根目录]
#   不传参数时, 默认从脚本位置回溯到 workspace 根目录下的 fineract/
#   00-baseline -> abnk-design -> planning -> docs -> workspace -> .asdm -> workspace-root (共 6 层)
# 输出: markdown 表格 (类别 | 文件数 | 行数)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FINERACT="${1:-}"
if [[ -z "$FINERACT" ]]; then
    FINERACT="$(cd "$SCRIPT_DIR/../../../../../../fineract" 2>/dev/null && pwd)"
fi

if [[ ! -d "$FINERACT" ]]; then
    echo "错误: 目录不存在: $FINERACT" >&2
    echo "用法: $0 [fineract 根目录]" >&2
    exit 1
fi

# 统计口径: 排除构建产物与 .git 目录, 统计物理行数
PRUNE=(-type d \( -name build -o -name .gradle -o -name .git -o -name out -o -name target -o -name node_modules \) -prune)

stat_class() {
    local label="$1"
    shift
    local list count lines
    list=$(find "$FINERACT" "${PRUNE[@]}" -o -type f \( "$@" \) -print)
    if [[ -z "$list" ]]; then
        count=0
        lines=0
    else
        count=$(printf '%s\n' "$list" | wc -l | tr -d ' ')
        lines=$(printf '%s\n' "$list" | tr '\n' '\0' | xargs -0 cat 2>/dev/null | wc -l | tr -d ' ')
    fi
    printf "| %s | %s | %s |\n" "$label" "$count" "$lines"
}

echo "统计对象: ${FINERACT} ($(date +%Y-%m-%d))"
echo
echo "| 类别 | 文件数 | 行数 |"
echo "|---|---:|---:|"

# --- Java (手写代码, 排除两个自动生成的 client 模块) ---
stat_class "Java 生产代码 (src/main/java, 不含生成 SDK)" \
    -path "*/src/main/java/*" -name "*.java" -not -path "*fineract-client*"

stat_class "Java 测试代码 (src/test/java, 不含生成 SDK)" \
    -path "*/src/test/java/*" -name "*.java" -not -path "*fineract-client*"

stat_class "Java 自动生成 SDK (fineract-client + fineract-client-feign)" \
    -name "*.java" \( -path "*/fineract-client/*" -o -path "*/fineract-client-feign/*" \)

# --- 数据库 ---
stat_class "Liquibase changelog (db/changelog 下的 XML)" \
    -name "*.xml" -path "*/db/changelog/*"

stat_class "SQL (迁移脚本 / 演示备份)" \
    -name "*.sql"

stat_class "Avro schema (.avsc)" \
    -name "*.avsc"

# --- 测试资产 ---
stat_class "Cucumber E2E (.feature)" \
    -name "*.feature"

# --- 构建逻辑 ---
stat_class "Gradle 构建脚本 (.gradle)" \
    -name "*.gradle"

stat_class "buildSrc Groovy" \
    -path "*buildSrc/*" -name "*.groovy"

# --- 文档 ---
stat_class "AsciiDoc 文档 (.adoc)" \
    -name "*.adoc"

stat_class "PlantUML 图 (.puml)" \
    -name "*.puml"

# --- 配置 ---
stat_class "配置文件 (.properties / .yml / .yaml / .env)" \
    \( -name "*.properties" -o -name "*.yml" -o -name "*.yaml" -o -name "*.env" \)

# --- 总计: 所有文本文件 (不区分类别/语言, 仅排除二进制文件) ---
# 二进制裁剪列表按需补充
stat_class "**全部文本文件总计**" \
    -type f \
    -not -name "*.png" -not -name "*.jpg" -not -name "*.jpeg" -not -name "*.gif" \
    -not -name "*.ico" -not -name "*.jar" -not -name "*.zip" -not -name "*.gz" \
    -not -name "*.tar" -not -name "*.pdf" -not -name "*.woff" -not -name "*.woff2" \
    -not -name "*.ttf" -not -name "*.otf" -not -name "*.class" -not -name "*.bin"
