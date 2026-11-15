#!/usr/bin/env python3
# 临时审计脚本：对触碰文件清单做 CJK 注释双语配对判定（任务 6.1 矩阵生成用）
# Temporary audit tool: check bilingual pairing of CJK comments (task 6.1 matrix).
#
# 判定口径（Phase 6 文档「按注释块判定双语配对」）：
#   注释块 = 连续注释行（空注释行 `//`/`#`/`*` 属于块内排版，遇非注释行断块）。
#   块内含 CJK 注释行时：
#   - 须存在英文注释行（无 CJK 且含字母），且第一个英文行位于最后一个 CJK 行
#     之后（中文在上、英文语义重写在下的两形态：同行 `中文 | English` 天然满足；
#     中文段 + 紧随英文段满足）；
#   - 否则该块的全部 CJK 行计为缺口。
#   豁免：行内含 `noqa-bilingual`；形态 A（同行 `中文 | English`）的行单独豁免。
import re
import sys

CJK = re.compile(r'[\u4e00-\u9fa5]')
COMMENT = re.compile(r'^\s*(//+|/\*+|\*+|#)')
WORD = re.compile(r'[A-Za-z]')
PAIR_A = re.compile(r'\|\s*[A-Za-z]')  # 形态 A：同行 `中文 | English`


def build_blocks(lines):
    """切注释块：连续注释行为一块，非注释行断块 / group consecutive comment lines."""
    blocks = []
    cur = []
    for lineno, ln in enumerate(lines, 1):
        if COMMENT.match(ln):
            cur.append((lineno, ln))
        else:
            if cur:
                blocks.append(cur)
                cur = []
    if cur:
        blocks.append(cur)
    return blocks


def scan(path: str):
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().splitlines()
    blocks = build_blocks(lines)
    cjk_count = 0
    gaps = []
    for block in blocks:
        cjk_lines = [(n, l) for n, l in block if CJK.search(l)]
        cjk_count += len(cjk_lines)
        if not cjk_lines:
            continue
        if all('noqa-bilingual' in l or PAIR_A.search(l) for _, l in cjk_lines):
            continue  # 全部豁免 / 形态 A
        en_positions = [n for n, l in block if not CJK.search(l) and WORD.search(l)]
        last_cjk = max(n for n, _ in cjk_lines)
        if en_positions and max(en_positions) > last_cjk:
            continue  # 块级配对：英文行组收尾于中文段之后（兼容块内多组中英对照）
        gaps.extend((n, l) for n, l in cjk_lines if 'noqa-bilingual' not in l and not PAIR_A.search(l))
    return cjk_count, gaps


def main():
    total_cjk = 0
    total_gap = 0
    for path in sys.argv[1:]:
        n, gaps = scan(path)
        total_cjk += n
        total_gap += len(gaps)
        tag = 'EMPTY' if n == 0 else ('OK' if not gaps else 'GAP')
        print(f'{tag}\t{n}\t{len(gaps)}\t{path}')
        for lineno, text in gaps:
            print(f'    {path}:{lineno}: {text.strip()}')
    print(f'== TOTAL cjk_lines={total_cjk} gap_lines={total_gap} ==', file=sys.stderr)


if __name__ == '__main__':
    main()
