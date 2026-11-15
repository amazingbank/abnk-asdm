#!/usr/bin/env python3
# add-frontmatter.py —— 全 workspace 创作 markdown 注入 YAML front-matter（三 profile 路由）
# Front-matter injector: prepend structured YAML metadata to every authored
# workspace markdown, routed into three profiles by file path.
#
# 用法 / Usage:
#   python3 .asdm/scripts/add-frontmatter.py            # 注入（幂等：已注入文件跳过）
#   python3 .asdm/scripts/add-frontmatter.py --check    # 只校验不注入（覆盖率 + schema + 交叉验证）
#
# profile 字段 / profile fields:
#   sprint-doc   : sprint / part / phase / status / date / evidence / locale / doc-note / moved_to
#   planning-doc : section / status / locale
#   release-note : version / date / locale
#
# status/date 反填口径 / backfill rules:
#   - Phase 文档 status 从对应 Plan「进度概要」Phase 级行词表映射：
#     ✅→completed / ⏳→pending / 🚧→in_progress / 🔁→moved / 🟢·排期·远期→planned-backlog
#   - date：完成态取 Plan 括注日期（多日期取最后一个=最终完成日）；无日期态取注入执行日（状态快照日）
#   - Plan 文档自身 status = Phase 行聚合（任一 in_progress→in_progress；全 completed→completed；
#     其余混合/全 pending→pending；全 planned→planned-backlog）
#   - 不注入对象：Part 桶内 artifacts 证据 md、Sprint 级 artifacts/README.md、planning/modelB（证据与外部资料永不分层、不注入）
import os
import re
import sys

ASDM = "/Users/leixu/source/asdm/amazingbank-ws/.asdm"
SPRINTS = os.path.join(ASDM, "workspace/docs/Sprints/v0.0.1")
TODAY = "2026-11-16"  # 注入执行日（状态快照日）/ injection date (status snapshot day)

PHASE_ROW = re.compile(r"^\|\s*\*\*\[Phase ([\wP]+)\]\(\./([^)]+)\)\*\*")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
STATUS_WORDS = [("✅", "completed"), ("⏳", "pending"), ("🚧", "in_progress"),
                ("🔁", "moved"), ("🟢", "planned-backlog"), ("🟡", "draft")]

# part03 特殊项（方案要点 5 / 任务 5.4 改动详情）
DOC_NOTES = {
    ("part03", "5"): "范围扩展（资产归仓 + front-matter 同车）",
    ("part03", "7"): "插入性质（D3 修订触发）",
}
MOVED_TO = {("part03", "5"): "part04:1.1"}  # 移交声明（文末）→ 承接方


def map_status(text):
    # 词表映射 / vocabulary mapping
    for emoji, word in STATUS_WORDS:
        if emoji in text:
            return word
    if "排期" in text or "远期" in text:
        return "planned-backlog"
    return None


def parse_plan(path):
    # 解析 Plan「进度概要」Phase 级行 → {phase_key: (doc_name, status, date)}
    rows = {}
    for line in open(path, encoding="utf-8"):
        m = PHASE_ROW.match(line)
        if m:
            phase_key, doc = m.group(1), m.group(2)
            status = map_status(line)
            dates = DATE_RE.findall(line)
            date = dates[-1] if (status == "completed" and dates) else None
            rows[phase_key] = (os.path.basename(doc), status, date)
    return rows


def aggregate(plan_rows):
    # Plan 文档自身状态聚合 / aggregate part-level status
    st = {r[1] for r in plan_rows.values()}
    if "in_progress" in st:
        return "in_progress"
    if st == {"completed"}:
        return "completed"
    if st == {"pending"}:
        return "pending"
    if st <= {"planned-backlog"}:
        return "planned-backlog"
    return "in_progress"  # completed+pending 混合


def yaml_escape(v):
    v = str(v)
    if re.match(r"^[\w./:-]+$", v):
        return v
    return '"' + v.replace('"', '\\"') + '"'


def fm_text(fields):
    lines = ["---"]
    for k, v in fields.items():
        if v is None or v == "":
            continue
        lines.append(f"{k}: {yaml_escape(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def inject(path, header):
    # 头部插入（正文零改动）/ prepend in place, body untouched
    body = open(path, encoding="utf-8").read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + body)


def parse_fm(path):
    # 行式解析 front-matter（yaml.safe_load 等价口径：键: 值）
    lines = open(path, encoding="utf-8").read().split("\n")
    if not lines or lines[0] != "---":
        return None, 0
    fields = {}
    end = None
    for i in range(1, min(len(lines), 50)):
        if lines[i] == "---":
            end = i
            break
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", lines[i])
        if m:
            v = m.group(2).strip().strip('"')
            fields[m.group(1)] = v
    return (fields if end else None), (end + 1 if end else 0)


def targets():
    # 收集注入对象（创作树口径：排除 artifacts / modelB）
    out = []
    for root, dirs, files in os.walk(os.path.join(ASDM, "workspace")):
        dirs[:] = [d for d in dirs if d not in ("artifacts", "modelB")]
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.join(root, f))
    return sorted(out)


def build_header(path):
    # 按路径路由三 profile / route to profile by path
    rel = os.path.relpath(path, ASDM)
    if rel.startswith("workspace/docs/Sprints/"):
        m = re.match(r"workspace/docs/Sprints/v([\d.]+)/part(\d+)/(.+)", rel)
        part = f"part{m.group(2)}"
        fname = os.path.basename(path)
        plan_rows = PLAN_CACHE.get(part)
        if fname.endswith("-Plan.md"):
            phase, status, date = "plan", aggregate(plan_rows), TODAY
            src = "plan-aggregate"
        else:
            pm = re.search(r"Phase([\wP]+?)(?:-|\.md)", fname)
            if pm is None:
                # 非 Plan 非 Phase 命名的伴生文档（如 KBank-POC-Journey 设计稿）：phase 省略，
                # status/date 从文档头「> **状态**：」抽取（🟡→draft），无则 pending。
                # Companion doc without Phase naming: omit phase, take status from doc header.
                body_head = open(path, encoding="utf-8").read()[:800]
                sm = re.search(r"\*\*状态\*\*[:：]\s*([^\n>]+)", body_head)
                status = map_status(sm.group(1)) if sm else "pending"
                return {"sprint": "v" + m.group(1), "part": part, "status": status,
                        "date": (DATE_RE.findall(sm.group(1)) or [TODAY])[0] if sm else TODAY,
                        "evidence": "./artifacts/", "locale": "zh-CN"}, "sprint-doc", "doc-header"
            phase = pm.group(1)
            row = plan_rows.get(phase)
            if row and row[1]:
                _, status, date = row
                src = "plan-row"
            else:  # 副文档（如 Phase2Results 测试报告）取同名 Phase 行兜底
                base = re.sub(r"^v[\d.]+-Part\d+-", "", fname).split("-")[0]
                row = plan_rows.get(base)
                _, status, date = row if row and row[1] else (None, "pending", None)
                src = "plan-row-sibling"
            date = date or TODAY
        fields = {"sprint": "v" + m.group(1), "part": part, "phase": phase,
                  "status": status, "date": date,
                  "evidence": ("../../artifacts/" if "Phase2Results" in rel else "./artifacts/"),
                  "locale": "zh-CN",
                  "doc-note": DOC_NOTES.get((part, str(phase))),
                  "moved_to": MOVED_TO.get((part, str(phase)))}
        return fields, "sprint-doc", src
    if rel.startswith("workspace/sre/ReleaseNotes/"):
        version = rel.split("/")[3]
        date = TODAY
        body = open(path, encoding="utf-8").read()
        dm = re.search(r"\*\*日期\*\*[:：]\s*(\d{4}-\d{2}-\d{2})", body)
        if dm:
            date = dm.group(1)
        return {"version": version, "date": date, "locale": "zh-CN"}, "release-note", "release-body"
    if rel == "workspace/docs/README.md":
        return {"section": "workspace-structure", "status": "stable", "locale": "zh-CN"}, "planning-doc", "fixed"
    if rel.startswith("workspace/docs/planning/abnk-design/"):
        parts = rel.split("/")
        section = parts[4] if len(parts) > 5 else "abnk-design"  # 分区目录名 or 根 README
        status = "stable"
        body = open(path, encoding="utf-8").read()
        am = re.search(r"^- 状态[:：]\s*(Accepted|Proposed|Rejected|Superseded)", body, re.M)
        if am:
            status = am.group(1).lower()
        return {"section": section, "status": status, "locale": "zh-CN"}, "planning-doc", "planning-body"
    return None, None, None


REQUIRED = {"sprint-doc": ["sprint", "part", "status", "date", "locale"],
            "planning-doc": ["section", "status", "locale"],
            "release-note": ["version", "date", "locale"]}

PLAN_CACHE = {}
for p in ["part01", "part02", "part03", "part04"]:
    pp = os.path.join(SPRINTS, p, "zh-CN", "v0.0.1-Part" + p[4:] + "-Plan.md")
    if os.path.exists(pp):
        PLAN_CACHE[p] = parse_plan(pp)


def main():
    check_only = "--check" in sys.argv
    files = targets()
    injected, skipped, issues = [], [], []

    for path in files:
        fields, profile, src = build_header(path)
        if profile is None:
            issues.append(f"UNROUTED: {path}")
            continue
        existing, _ = parse_fm(path)
        if existing is not None:
            skipped.append(path)
            # 交叉验证（V5.4.3）：已注入文件比对 front-matter 与 Plan 口径
            if profile == "sprint-doc" and fields.get("phase") != "plan":
                for k in ("status",):
                    if existing.get(k) != fields.get(k):
                        issues.append(f"DRIFT[{k}]: {os.path.relpath(path, ASDM)} fm={existing.get(k)} plan={fields.get(k)}")
                if existing.get("date") != fields.get("date") and fields.get("status") == "completed":
                    issues.append(f"DRIFT[date]: {os.path.relpath(path, ASDM)} fm={existing.get('date')} plan={fields.get('date')}")
            for k in REQUIRED[profile]:
                if not existing.get(k):
                    issues.append(f"SCHEMA: {os.path.relpath(path, ASDM)} missing {k}")
            continue
        if not check_only:
            inject(path, fm_text(fields))
        injected.append((path, profile, src))

    print(f"targets={len(files)} injected={len(injected)} already={len(skipped)} issues={len(issues)}")
    for p, profile, src in injected:
        print(f"  + [{profile}/{src}] {os.path.relpath(p, ASDM)}")
    for i in issues:
        print(f"  ! {i}")
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
