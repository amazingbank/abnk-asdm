#!/usr/bin/env python3
# gen-sprint-index.py —— Sprint index/metrics 生成器（dev portal 数据管线生产侧）。
# 定位（Part04 Plan D4「提取入库、构建纯复制」）：本脚本是 abnk-asdm 仓的
# 自审工具——从 Sprints 树的 front-matter 生成结构化索引与指标，产出物入库
# （workspace/index 的 git history 即数据可信度审计记录），portal 侧只做
# 只读复制、零提取逻辑。
# 用法：
#   python3 gen-sprint-index.py                 生成（含三重校验，fail-loud）
#   python3 gen-sprint-index.py --verify         校验模式：重解析比对磁盘产物
#   python3 gen-sprint-index.py --refresh-loc    重跑 count-loc.sh 更新 LOC 快照
#   python3 gen-sprint-index.py --help           用法说明
# 产出物：
#   $INDEX/sprint-v0.0.1.yaml      Sprint→Part→Phase→Task 层级索引 + portal-content
#                                   分区条目（Part04 任务 2.3 locale 路由：同 doc id
#                                   逐 locale 注册，单语条目带 fallback 标记——渲染
#                                   层按此路由，无需扫描目录）
#   $INDEX/metrics-v0.0.1.json     指标（第一批清单口径，Part04 Phase1 已知坑 6）
#   $INDEX/loc-snapshot-v0.0.1.md  LOC 快照（--refresh-loc 显式更新；默认只读）
# 三重校验（fail-loud，无静默跳过路径）：
#   1. index vs front-matter 零漂移（生成即校验；--verify 全量重比对）
#   2. metrics vs 源报告零漂移（四数字从 Test-Report 正文提取，非硬编码）
#   3. front-matter 解析失败/非法值 → exit 1（精确到 文件:字段）
# 退出码：0 = 成功/校验通过；1 = 校验失败或解析失败
#
# Sprint index/metrics generator: the producing side of the dev portal data
# pipeline.
# Positioning (Part04 Plan D4 "extract-and-commit, build-by-copy"): a
# self-audit tool of the abnk-asdm repo — it turns Sprints-tree front-matter
# into a structured index and metrics, and the outputs are committed (the git
# history of workspace/index IS the data-trust audit trail); the portal side
# only copies, never extracts.
# Usage:
#   gen-sprint-index.py            generate (triple validation, fail-loud)
#   gen-sprint-index.py --verify   verify mode: re-parse, compare with disk
#   gen-sprint-index.py --refresh-loc   rerun count-loc.sh to refresh the LOC snapshot
#   gen-sprint-index.py --help     show this header
# Outputs:
#   sprint-v0.0.1.yaml      Sprint → Part → Phase → Task hierarchy index, plus
#                           portal-content section entries (Part04 task 2.3
#                           locale routing: one entry per locale of the same
#                           doc id; monolingual docs carry a fallback marker —
#                           the render side routes on this, no dir scanning)
#   metrics-v0.0.1.json     metrics (first-batch list, Part04 Phase1 pitfall 6)
#   loc-snapshot-v0.0.1.md  LOC snapshot (explicit --refresh-loc; read-only by default)
# Triple validation (fail-loud, no silent-skip path):
#   1. index vs front-matter: zero drift (validated on generate; --verify re-checks)
#   2. metrics vs source report: zero drift (four numbers extracted from the
#      Test-Report body, never hardcoded)
#   3. front-matter parse failure / illegal value → exit 1 (precise file:field)
# Exit codes: 0 = pass; 1 = validation or parse failure
import json
import os
import re
import subprocess
import sys
from datetime import date as _date

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASDM = os.path.dirname(SCRIPT_DIR)  # .asdm/scripts/ → .asdm/
SPRINTS = os.path.join(ASDM, "workspace/docs/Sprints/v0.0.1")
INDEX = os.path.join(ASDM, "workspace/index")
PLANNING = os.path.join(ASDM, "workspace/docs/planning/abnk-design")
PORTAL_CONTENT = os.path.join(ASDM, "workspace/docs/portal-content")
COUNT_LOC = os.path.join(PLANNING, "00-baseline/count-loc.sh")
TEST_REPORT_REL = "part02/Phase2Results/zh-CN/v0.0.1-Part02-PhaseP2-Test-Report.md"

# portal-content 分区词表（Part04 任务 2.3 locale 路由增量）：
#   PORTAL_STATUS —— 内容侧状态词表（planning-doc profile 的 status 值域）；
#   PORTAL_LOCALES —— locale 叶子层词表，列表顺序即注册顺序（zh 全量主、
#   en-US 增量语义重写——D3/D4 口径）。
# Vocabulary for the portal-content partition (Part04 task 2.3 locale routing):
#   PORTAL_STATUS — the content-side status vocabulary (value domain of the
#   planning-doc profile's status field);
#   PORTAL_LOCALES — the locale-leaf vocabulary; list order is registration
#   order (zh full coverage first, en-US incremental semantic rewrites — per
#   decisions D3/D4).
PORTAL_STATUS = {"published", "in_progress", "draft"}
PORTAL_LOCALES = ["zh-CN", "en-US"]

# 状态词表（与 Part03 Phase5 注入脚本 add-frontmatter.py 共用口径——同族
# 脚本，口径漂移 = 互证失败）。
# Status vocabulary (shared with the Part03 Phase5 injector add-frontmatter.py
# — sibling scripts: a vocabulary drift would fail the cross-check).
STATUS_WORDS = [("✅", "completed"), ("⏳", "pending"), ("🚧", "in_progress"),
                ("🔁", "moved"), ("🟢", "planned-backlog"), ("🟡", "draft")]
VALID_STATUS = {w for _, w in STATUS_WORDS}

# 挂账清单（人工维护常量，D6 诚实性铁律——机械 grep「挂账」标记不可靠，
# 每条带出处与复验计划；演进口径随 CI 首版由用户拍板）。
# Blocked-items list (manually curated, per the D6 honesty rule — grepping a
# "blocked" marker is unreliable; every entry cites its source and replay
# plan; evolution of this list is a CI-v1 user decision).
BLOCKED_ITEMS = [
    {"id": "part03-v6.3.4-android-carrier",
     "title": "mobile Android 载体走查（V6.3.4 段挂账）",
     "part": "part03",
     "source": "Sprints/v0.0.1/part03/artifacts/phase6/task6.3-final-walkthrough.md",
     "replay": "Android 模拟器可用时以同一 drive 口径重跑（ABNK_SHOT_PREFIX=android）"},
    {"id": "part02-p3.6-apple-signing",
     "title": "Apple 签名段（VP3.6.3 挂起——Apple 账号条件门未到位）",
     "part": "part02",
     "source": "Sprints/v0.0.1/part02/artifacts/phaseP3/taskP3.6-mobile-package.md",
     "replay": "Apple 开发者账号到位后补签名与 TestFlight 上架"},
]

# Plan 进度概要表的行形态。
# Row shapes of the Plan progress tables.
PHASE_ROW_LINKED = re.compile(
    r"^\|\s*\*\*\[Phase ([\wP]+)\]\(\./([^)]+)\)\*\*\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|")
PHASE_ROW_PLAIN = re.compile(
    r"^\|\s*\*\*Phase ([\wP]+)\*\*\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|")
TASK_ROW = re.compile(
    r"^\|\s*\|\s*任务\s+([\wP.]+)[:：]\s*(.+?)\s*\|\s*(.+?)\s*\|")

# Test-Report 指标提取形态（四数字一律从报告正文提取）。
# Metric extraction shapes from the Test-Report (all four numbers are pulled
# from the report body, never hardcoded).
RE_VP = re.compile(r"(\d+)/(\d+)\s*全过")
RE_UNIT = re.compile(r"(\d+)/(\d+)\s*全绿")
RE_ASSERT = re.compile(r"(\d+)/(\d+)\s*断言")
RE_DRIFT = re.compile(r"DRIFT:\s*(\d+)")


def fail(path, field, message):
    # fail-loud：精确报错退出，绝不静默跳过/降级。
    # fail-loud: exit with a precise error; never skip or degrade silently.
    print(f"ERROR: {path}: {field}: {message}", file=sys.stderr)
    sys.exit(1)


def map_status(text):
    # emoji/关键词 → 状态词（对齐注入脚本口径）。
    # Map emoji/keyword to a status word (injector-compatible vocabulary).
    for emoji, word in STATUS_WORDS:
        if emoji in text:
            return word
    if "排期" in text or "远期" in text:
        return "planned-backlog"
    return None


def parse_frontmatter(path, text):
    # 行式定位 `---` 边界后 yaml.safe_load（已知坑 3：不用 bash/正则手撕 YAML）。
    # Locate the `---` fence line-wise, then yaml.safe_load (known pitfall 3:
    # never hand-parse YAML with regex).
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        fail(path, "front-matter", "首行非 ---（缺结构化元数据头）")
    end = None
    for i in range(1, min(len(lines), 100)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        fail(path, "front-matter", "100 行内未找到闭合 ---")
    try:
        fm = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        fail(path, "front-matter", f"YAML 解析失败: {exc}")
    if not isinstance(fm, dict):
        fail(path, "front-matter", "front-matter 非键值结构")
    for key in ("sprint", "part", "status", "date", "locale"):
        if not fm.get(key):
            fail(path, key, "必填字段缺失或为空")
    if fm["status"] not in VALID_STATUS:
        fail(path, "status", f"非法状态值: {fm['status']!r}（词表: {sorted(VALID_STATUS)}）")
    return fm


def parse_portal_frontmatter(path, text):
    # portal-content 文档 front-matter（planning-doc profile：section/status/
    # locale 三必填——与 Sprints 的 sprint-doc profile 分开校验，必填集不同）。
    # Front-matter of a portal-content doc (planning-doc profile: section/
    # status/locale required — validated separately from the Sprints
    # sprint-doc profile, whose required-field set differs).
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        fail(path, "front-matter", "首行非 ---（缺结构化元数据头）")
    end = None
    for i in range(1, min(len(lines), 100)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        fail(path, "front-matter", "100 行内未找到闭合 ---")
    try:
        fm = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        fail(path, "front-matter", f"YAML 解析失败: {exc}")
    if not isinstance(fm, dict):
        fail(path, "front-matter", "front-matter 非键值结构")
    for key in ("section", "status", "locale"):
        if not fm.get(key):
            fail(path, key, "必填字段缺失或为空（planning-doc profile）")
    if fm["status"] not in PORTAL_STATUS:
        fail(path, "status",
             f"非法状态值: {fm['status']!r}（词表: {sorted(PORTAL_STATUS)}）")
    if fm["locale"] not in PORTAL_LOCALES:
        fail(path, "locale",
             f"非法 locale: {fm['locale']!r}（词表: {PORTAL_LOCALES}）")
    return fm


def collect_portal_content():
    # portal-content 分区遍历（Part04 任务 2.3 locale 路由）：分区 → locale
    # 叶子层 → md；同一 doc id 双 locale 时逐 locale 注册条目（双语 = 双
    # locale 注册），单语 doc 的条目带 fallback 标记（值 = 仅有 locale，
    # 渲染层据此回退，无需扫描目录）。front-matter section 必须与分区目录
    # 一致（双源校验，fail-loud）。
    # Traverse the portal-content partition (Part04 task 2.3 locale routing):
    # section → locale leaf → md; one entry per locale of the same doc id
    # (bilingual = both locales registered), and monolingual docs carry a
    # fallback marker (its value = the only available locale, so the render
    # side can fall back without scanning directories). The front-matter
    # section must match its partition directory (dual-source check, fail-loud).
    if not os.path.isdir(PORTAL_CONTENT):
        fail("workspace/docs/portal-content", "dir",
             "分区缺失（任务 2.2 起 portal-content 为数据契约组成部分）")
    docs = {}  # (section, doc) -> {locale: fm}
    for section in sorted(os.listdir(PORTAL_CONTENT)):
        sdir = os.path.join(PORTAL_CONTENT, section)
        if not os.path.isdir(sdir):
            continue
        for locale in sorted(os.listdir(sdir)):
            ldir = os.path.join(sdir, locale)
            if not os.path.isdir(ldir):
                continue
            if locale not in PORTAL_LOCALES:
                fail(f"portal-content/{section}", "locale-dir",
                     f"非法 locale 叶子层: {locale!r}（词表: {PORTAL_LOCALES}）")
            for fname in sorted(os.listdir(ldir)):
                if not fname.endswith(".md"):
                    continue
                path = os.path.join(ldir, fname)
                fm = parse_portal_frontmatter(
                    path, open(path, encoding="utf-8").read())
                if fm["section"] != section:
                    fail(f"portal-content/{section}/{locale}/{fname}", "section",
                         f"front-matter section={fm['section']!r} "
                         f"与分区目录 {section!r} 漂移")
                docs.setdefault((section, fname), {})[locale] = fm
    if not docs:
        fail("workspace/docs/portal-content", "docs", "未收集到任何 md（分区为空？）")
    entries = []
    for section, fname in sorted(docs):
        locales = docs[(section, fname)]
        for locale in PORTAL_LOCALES:  # 注册顺序：zh-CN 主、en-US 增量
            if locale not in locales:
                continue
            fm = locales[locale]
            entry = {"section": section, "doc": fname, "locale": locale,
                     "status": fm["status"]}
            if fm.get("date"):
                entry["date"] = str(fm["date"])
            if len(locales) == 1:
                entry["fallback"] = locale
            entries.append(entry)
    return entries


def collect_part(part_id):
    # 收集一个 Part 的全部文档 front-matter + Plan 表结构。
    # Collect every doc's front-matter plus the Plan table of one part.
    pdir = os.path.join(SPRINTS, part_id, "zh-CN")
    docs, plan_rows, tasks = [], [], []
    for fname in sorted(os.listdir(pdir)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(pdir, fname)
        fm = parse_frontmatter(path, open(path, encoding="utf-8").read())
        entry = {"doc": fname, "status": fm["status"], "date": str(fm["date"]),
                 "locale": fm["locale"], "evidence": fm.get("evidence", "")}
        if fm.get("phase") is not None:
            entry["phase"] = str(fm["phase"])
        for opt in ("doc-note", "moved_to"):
            if fm.get(opt):
                entry[opt] = str(fm[opt])
        docs.append(entry)
        if fname.endswith("-Plan.md"):
            plan_rows, tasks = parse_plan_table(path)
    docs.sort(key=lambda d: d["doc"])
    return docs, plan_rows, tasks


def parse_plan_table(path):
    # 解析 Plan 进度概要表：Phase 行（链接/无链接两形态）+ 任务行。
    # Parse the Plan progress table: phase rows (linked / plain forms) and
    # task rows.
    phases, tasks = [], []
    for line in open(path, encoding="utf-8"):
        m = PHASE_ROW_LINKED.match(line)
        if m:
            phases.append({"phase": m.group(1), "doc": os.path.basename(m.group(2)),
                           "title": m.group(3), "status_text": m.group(4)})
            continue
        m = PHASE_ROW_PLAIN.match(line)
        if m and "[Phase" not in line:
            phases.append({"phase": m.group(1), "doc": None, "title": m.group(2),
                           "status_text": m.group(3)})
            continue
        m = TASK_ROW.match(line)
        if m:
            tasks.append({"id": m.group(1), "title": m.group(2),
                          "status_text": m.group(3)})
    if not phases:
        fail(path, "进度概要", "未解析到任何 Phase 行（表结构漂移？）")
    for row in phases + tasks:
        word = map_status(row["status_text"])
        if word is None:
            fail(path, "status", f"无法映射状态: {row.get('phase', row.get('id'))!r} → {row['status_text']!r}")
        row["status"] = word
    return phases, tasks


def cross_validate(part_id, docs, plan_phases, plan_tasks):
    # 校验 1：Plan Phase 行 ↔ Phase 文档 front-matter 双源零漂移。
    # Validation 1: Plan phase rows vs phase-doc front-matter — zero drift
    # between the two sources.
    by_phase = {}
    for d in docs:
        if d.get("phase") and d["phase"] != "plan":
            by_phase.setdefault(d["phase"], []).append(d)
    for row in plan_phases:
        key = row["phase"]
        # 主文档 = 文件名含 Phase{key}；伴生文档（如 Test-Report）不参与行比对。
        # Primary doc = filename contains Phase{key}; companion docs (e.g.
        # the Test-Report) do not take part in row comparison.
        primary = [d for d in by_phase.get(key, []) if f"Phase{key}" in d["doc"]]
        if not primary:
            continue
        if primary[0]["status"] != row["status"]:
            rel = f"{part_id}/zh-CN/{primary[0]['doc']}"
            fail(rel, "status",
                 f"双源漂移——front-matter={primary[0]['status']!r} vs Plan 行={row['status']!r}"
                 f"（处置：修源双改，勿给生成器加容错）")
    return plan_phases, plan_tasks


def aggregate_plan_status(plan_phases):
    # Plan 自身状态聚合（对齐注入脚本 aggregate 规则）。
    # Aggregate the Plan's own status (injector-compatible aggregation).
    st = {r["status"] for r in plan_phases}
    if "in_progress" in st:
        return "in_progress"
    if st == {"completed"}:
        return "completed"
    if st == {"pending"}:
        return "pending"
    if st <= {"planned-backlog"}:
        return "planned-backlog"
    return "in_progress"


def extract_test_metrics():
    # 校验 2：四数字从 Test-Report 正文提取（metrics vs 源报告零漂移的
    # 机制保证——不存在硬编码路径）。
    # Validation 2: the four numbers are extracted from the Test-Report body
    # (the mechanism that guarantees metrics-vs-source zero drift — there is
    # no hardcoding path).
    path = os.path.join(SPRINTS, TEST_REPORT_REL)
    text = open(path, encoding="utf-8").read()
    def grab(regex, label):
        m = regex.search(text)
        if not m:
            fail(TEST_REPORT_REL, label, "指标提取失败（报告正文形态漂移？）")
        return int(m.group(1)), int(m.group(2)) if regex.groups == 2 else int(m.group(1))
    vp_p, vp_t = grab(RE_VP, "vp")
    unit_p, unit_t = grab(RE_UNIT, "unit_tests")
    asrt_p, asrt_t = grab(RE_ASSERT, "assertions")
    m = RE_DRIFT.search(text)
    if not m:
        fail(TEST_REPORT_REL, "contract_drift", "DRIFT 提取失败")
    return {"vp": {"passed": vp_p, "total": vp_t},
            "unit_tests": {"passed": unit_p, "total": unit_t},
            "e2e_assertions": {"passed": asrt_p, "total": asrt_t},
            "contract_drift": int(m.group(1)),
            "source": f"Sprints/v0.0.1/{TEST_REPORT_REL}"}


def count_dirs(glob_parts):
    # 计数工具：ADR 文件与各 Part artifacts 文件数（机械可提取源）。
    # Counting helpers: ADR files and per-part artifact file counts.
    result = {}
    for part_id in glob_parts:
        adir = os.path.join(SPRINTS, part_id, "artifacts")
        n = 0
        for root, dirs, files in os.walk(adir):
            n += len(files)
        result[part_id] = n
    return result


def count_adrs():
    # Count ADR files (numbered ADR-001..010, README excluded).
    adr_dir = os.path.join(PLANNING, "adr/zh-CN")
    return len([f for f in os.listdir(adr_dir)
                if f.endswith(".md") and re.match(r"^\d{3}-", f)])


def parse_loc_snapshot():
    # LOC 快照解析（快照由 --refresh-loc 显式生成；默认只读保证幂等轻量）。
    # Parse the LOC snapshot (created explicitly via --refresh-loc; default
    # runs only read it, keeping regeneration cheap and idempotent).
    snap = os.path.join(INDEX, "loc-snapshot-v0.0.1.md")
    if not os.path.exists(snap):
        fail("workspace/index/loc-snapshot-v0.0.1.md", "file",
             "LOC 快照缺失——先运行 --refresh-loc 生成")
    categories, total = [], None
    for line in open(snap, encoding="utf-8"):
        m = re.match(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", line.strip())
        if not m or "类别" in m.group(1) or "---" in line:
            continue
        row = {"label": m.group(1).strip("*"), "files": int(m.group(2)),
               "lines": int(m.group(3))}
        if "总计" in row["label"]:
            total = row
        else:
            categories.append(row)
    if total is None:
        fail("loc-snapshot-v0.0.1.md", "total", "总计行缺失（快照形态漂移）")
    return {"snapshot": "loc-snapshot-v0.0.1.md", "total": total,
            "categories": categories}


def sprint_rhythm(parts_docs):
    # Sprint 节奏：每 Part 的文档日期跨度（front-matter date 聚合）。
    # Sprint rhythm: per-part date span aggregated from front-matter dates.
    rhythm = []
    for part_id in sorted(parts_docs):
        dates = [d["date"] for d in parts_docs[part_id]["docs"] if d.get("date")]
        if not dates:
            continue
        lo, hi = min(dates), max(dates)
        try:
            days = (_date.fromisoformat(hi) - _date.fromisoformat(lo)).days
        except ValueError:
            days = None
        rhythm.append({"part": part_id, "start": lo, "end": hi, "days": days})
    return rhythm


def build_all():
    # 主构建：index + metrics（内存结构；写盘在 write_outputs）。
    # Main build: index + metrics in memory; persistence lives in
    # write_outputs.
    part_ids = sorted(d for d in os.listdir(SPRINTS)
                      if d.startswith("part") and os.path.isdir(os.path.join(SPRINTS, d)))
    if len(part_ids) < 4:
        fail("Sprints/v0.0.1", "parts", f"Part 目录不足 4 个: {part_ids}")
    parts_docs, parts_out, moved_count = {}, [], 0
    for pid in part_ids:
        docs, plan_phases, plan_tasks = collect_part(pid)
        plan_doc = next((d for d in docs if d["doc"].endswith("-Plan.md")), None)
        if plan_doc is None:
            fail(f"{pid}/zh-CN", "Plan", "未找到 Plan 文档")
        plan_status = aggregate_plan_status(plan_phases)
        if plan_status != plan_doc["status"]:
            fail(f"{pid}/zh-CN/{plan_doc['doc']}", "status",
                 f"Plan front-matter={plan_doc['status']!r} vs 表聚合={plan_status!r}（双源漂移）")
        cross_validate(pid, docs, plan_phases, plan_tasks)
        task_entries = []
        for t in plan_tasks:
            entry = {"id": t["id"], "title": t["title"], "status": t["status"]}
            note = re.sub(r"[｜|]", "/", t["status_text"]).strip()
            if note and note != t["status"]:
                entry["note"] = note
            task_entries.append(entry)
            if t["status"] == "moved":
                moved_count += 1
        parts_docs[pid] = {"docs": docs}
        parts_out.append({"id": pid, "status": plan_status, "date": plan_doc["date"],
                          "docs": docs, "tasks": task_entries})
    index = {"schema_version": 1, "sprint": "v0.0.1", "parts": parts_out,
             "portal_content": collect_portal_content()}
    evd = count_dirs(part_ids)
    metrics = {
        "schema_version": 1,
        "sprint": "v0.0.1",
        "test_report": extract_test_metrics(),
        "loc": parse_loc_snapshot(),
        "sprint_rhythm": sprint_rhythm(parts_docs),
        "moved_count": moved_count,
        "blocked_items": BLOCKED_ITEMS,
        "adr_count": count_adrs(),
        "evidence_density": {f"part{i[4:]}": evd[i] for i in sorted(evd)},
        "ci": {"status": "not_run",
               "note": "CI workflow 尚未建设（规划级）——如实标注未实跑（D6 诚实性）"},
    }
    return index, metrics


def write_outputs(index, metrics):
    # 写盘（幂等：内容确定、无时间戳；git diff 为零即幂等成立）。
    # Persist (idempotent: deterministic content, no timestamps; a zero git
    # diff IS the idempotency proof).
    ypath = os.path.join(INDEX, "sprint-v0.0.1.yaml")
    jpath = os.path.join(INDEX, "metrics-v0.0.1.json")
    with open(ypath, "w", encoding="utf-8") as fh:
        yaml.safe_dump(index, fh, allow_unicode=True, sort_keys=False,
                       default_flow_style=False)
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    return ypath, jpath


def verify():
    # --verify：重解析全部 front-matter 与磁盘产物逐条比对（V1.1.4 判据）。
    # --verify: re-parse every front-matter and compare entry-by-entry against
    # the on-disk artifacts (the V1.1.4 gate).
    index, metrics = build_all()
    ypath = os.path.join(INDEX, "sprint-v0.0.1.yaml")
    jpath = os.path.join(INDEX, "metrics-v0.0.1.json")
    for path in (ypath, jpath):
        if not os.path.exists(path):
            fail(os.path.relpath(path, ASDM), "file", "产物缺失——先运行生成模式")
    disk_index = yaml.safe_load(open(ypath, encoding="utf-8"))
    disk_metrics = json.load(open(jpath, encoding="utf-8"))
    if disk_index != index:
        print("ERROR: sprint-v0.0.1.yaml 与 front-matter 重解析结果存在漂移", file=sys.stderr)
        sys.exit(1)
    if disk_metrics != metrics:
        print("ERROR: metrics-v0.0.1.json 与源报告重提取结果存在漂移", file=sys.stderr)
        sys.exit(1)
    n_docs = sum(len(p["docs"]) for p in index["parts"])
    n_tasks = sum(len(p["tasks"]) for p in index["parts"])
    n_portal = len(index["portal_content"])
    n_en = sum(1 for e in index["portal_content"] if e["locale"] == "en-US")
    print(f"verify OK: parts={len(index['parts'])} docs={n_docs} tasks={n_tasks} "
          f"portal_docs={n_portal} portal_en={n_en} — index/front-matter 双向一致，metrics/源报告一致")


def refresh_loc():
    # --refresh-loc：显式重跑 count-loc.sh 更新快照（37s 量级，不进默认路径）。
    # --refresh-loc: explicitly rerun count-loc.sh to refresh the snapshot
    # (~37s; kept out of the default path).
    snap = os.path.join(INDEX, "loc-snapshot-v0.0.1.md")
    with open(snap, "w", encoding="utf-8") as fh:
        rc = subprocess.call(["bash", COUNT_LOC], stdout=fh,
                             stderr=subprocess.DEVNULL)
    if rc != 0:
        fail("count-loc.sh", "exit", f"退出码 {rc}")
    print(f"LOC 快照已更新: {os.path.relpath(snap, ASDM)}")


def usage():
    # 用法头存于脚本头部 `#` 注释块——--help 时原样回显（单一事实源，免两份漂移）。
    # The usage header lives in the leading `#` comment block — --help echoes
    # it verbatim (single source of truth, no duplicate to drift).
    lines = []
    for line in open(os.path.abspath(__file__), encoding="utf-8"):
        if line.startswith("#") or line.startswith("#!/"):
            lines.append(line.rstrip("\n"))
        elif line.strip():
            break
    print("\n".join(lines[1:]))  # 跳过 shebang / skip the shebang


def main():
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        usage()
        return
    if "--refresh-loc" in args:
        refresh_loc()
        return
    if "--verify" in args:
        verify()
        return
    if args:
        print(f"错误：未知参数: {args}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    index, metrics = build_all()
    ypath, jpath = write_outputs(index, metrics)
    n_docs = sum(len(p["docs"]) for p in index["parts"])
    n_tasks = sum(len(p["tasks"]) for p in index["parts"])
    n_portal = len(index["portal_content"])
    n_en = sum(1 for e in index["portal_content"] if e["locale"] == "en-US")
    moved = metrics["moved_count"]
    print(f"index OK: parts={len(index['parts'])} docs={n_docs} tasks={n_tasks} moved={moved} "
          f"portal_docs={n_portal} portal_en={n_en}")
    print(f"metrics OK: loc_total={metrics['loc']['total']['lines']} adr={metrics['adr_count']}")
    print(f"产出: {os.path.relpath(ypath, ASDM)} / {os.path.relpath(jpath, ASDM)}")


if __name__ == "__main__":
    main()
