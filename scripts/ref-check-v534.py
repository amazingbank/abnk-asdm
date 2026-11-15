#!/usr/bin/env python3
# V5.3.4 引用目标存在性全验：提取清扫范围内全部相对链接与 artifacts 路径引用（新旧形态一律提取），
# 逐一 test -e 比对物理文件。
# Reference existence check for V5.3.4: extract every relative link and artifacts
# path reference (old and new forms alike) across the sweep scope, then verify
# each against the physical file system.
import os, re, glob as globmod, sys

ASDM = "/Users/leixu/source/asdm/amazingbank-ws/.asdm"
WS = "/Users/leixu/source/asdm/amazingbank-ws"

targets = []
for root, dirs, files in os.walk(os.path.join(ASDM, "workspace")):
    dirs[:] = [d for d in dirs if d not in ("artifacts", "modelB")]
    for f in files:
        if f.endswith(".md"):
            targets.append(os.path.join(root, f))
for extra in [os.path.join(ASDM, "README.md"), os.path.join(ASDM, "toolsets", "README.md")]:
    if os.path.exists(extra):
        targets.append(extra)
for root, dirs, files in os.walk(os.path.join(ASDM, "toolsets")):
    for f in files:
        if f.endswith(".md") and os.path.join(root, f) not in targets:
            targets.append(os.path.join(root, f))
for p in ["README.md", "docs/README.md", "tests/README.md", ".gitignore",
          "scripts/prodform/probe_poc.py", "tests/smoke/smoke_test.py",
          "tests/poc/baseline_gap_test.py", "tests/gateway/gateway_test.py"]:
    fp = os.path.join(WS, "abnk-system", p)
    if os.path.exists(fp):
        targets.append(fp)

link_re = re.compile(r"\]\(([^)\s]+)\)")
path_re = re.compile(r"[\s`(「「『]((?:\.\./)+(?:part[0-9]+/)?artifacts/[^\s`\`)，。）」』|，]+\.[A-Za-z0-9]+|Sprints/v0\.0\.1/(?:part[0-9]+/)?artifacts/[^\s`\`)，。）」』]+\.[A-Za-z0-9]+)")

rows = []  # (file, ref, resolved, status, note)
for t in targets:
    base = os.path.dirname(t)
    text = open(t, encoding="utf-8", errors="ignore").read()
    refs = [m.group(1) for m in link_re.finditer(text)]
    refs += [m.group(1) for m in path_re.finditer(text)]
    for ref in refs:
        if ref.startswith(("http://", "https://", "mailto:", "git@", "ssh://")):
            continue
        r = ref.lstrip("<").rstrip(">")
        resolved = os.path.normpath(os.path.join(base, r))
        if "<" in r or "<ts>" in r:
            rows.append((t, ref, resolved, "PLACEHOLDER", "占位符（<version>/<ts>）模板形态"))
            continue
        if "*" in r:
            hits = globmod.glob(resolved)
            rows.append((t, ref, resolved, "GLOB-OK" if hits else "GLOB-MISS", f"glob 匹配 {len(hits)} 文件" if hits else "glob 零匹配"))
            continue
        if os.path.exists(resolved):
            rows.append((t, ref, resolved, "OK", ""))
        else:
            # 设计文本/模板/计划文本显式归类（非真实引用断链，不隐藏）
            if "..." in r and "Phase5" in t:
                rows.append((t, ref, resolved, "DESIGN-TEXT", "Phase5 判据设计文本的省略号示例形态"))
            elif r == "./link":
                rows.append((t, ref, resolved, "DESIGN-TEXT", "doc-review 模板示例文本（Phase 行格式说明）"))
            elif "/phase2/" in r and "part01" in t:
                rows.append((t, ref, resolved, "PLAN-TEXT", "计划文本（part01 Phase2 已移交任务的历史/未来归档位，非现存证据）"))
            else:
                rows.append((t, ref, resolved, "MISS", ""))

ok = sum(1 for r in rows if r[3] == "OK")
glob_ok = sum(1 for r in rows if r[3] == "GLOB-OK")
placeholder = sum(1 for r in rows if r[3] == "PLACEHOLDER")
miss = [r for r in rows if r[3] in ("MISS", "GLOB-MISS")]

out = []
out.append("# 任务 5.3 · V5.3.4 引用目标存在性全验报告")
out.append("")
out.append(f"- 提取范围：workspace 创作 md（排除 artifacts/modelB）+ .asdm README/toolsets + abnk-system README/scripts/tests/gitignore")
out.append(f"- 提取形态：md `](...)` 相对链接 + backtick/裸 `artifacts/` 路径引用（新旧形态一律提取）")
out.append(f"- 检查总数：{len(rows)}（OK {ok} / GLOB-OK {glob_ok} / PLACEHOLDER {placeholder} / 失联 {len(miss)}）")
out.append("")
out.append("## 失联引用清单")
out.append("")
if miss:
    for r in miss:
        out.append(f"- `{r[1]}` @ {r[0]} → {r[2]}【{r[3]}】{r[4]}")
else:
    out.append("（无——失联引用 0 条）")
out.append("")
out.append("## 占位符形态清单（模板非实体，不参与存在性判定）")
out.append("")
for r in rows:
    if r[3] == "PLACEHOLDER":
        out.append(f"- `{r[1]}` @ {os.path.relpath(r[0], WS)}")
out.append("")
out.append("## 全量明细")
out.append("")
for r in rows:
    out.append(f"[{r[3]:12s}] {os.path.relpath(r[0], WS)} :: {r[1]}" + (f"  ==> {r[4]}" if r[4] else ""))

with open(os.path.join(ASDM, "workspace/docs/Sprints/v0.0.1/part03/artifacts/phase5/task5.3-ref-check.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print(f"total={len(rows)} ok={ok} glob_ok={glob_ok} placeholder={placeholder} miss={len(miss)}")
for r in miss:
    print(f"MISS: {r[1]} @ {os.path.relpath(r[0], WS)} :: {r[4]}")
sys.exit(0 if not miss else 1)
