# -*- coding: utf-8 -*-
"""c64: cells.csv に メタ 4 の 2 行を追記（csv.writer QUOTE_ALL・17 フィールド検証）。"""
import csv, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data', 'cells.csv')
rows = [
    ['c64', '2026-11-24', 'M10 方法論候補の再利用率: 番号 ≥50 の候補が初出より後のサイクルの「- 事前固定」行で引用された割合（本文再言及も併記）', 'メタ',
     'findings 14 ファイル＋backlog.md（2026-11-24 09:30 時点）', '割合', 'n/a', 'n/a', 'n/a', '2/35 = 0.06（本文再言及 9/35 = 0.26）', 'n/a', 'n/a',
     '予測 <30% 当たり: 方法論層の write-only 化（採用 0/48 サイクル・open 118→203・判定済み 0）', 'n/a', 'no（meta 5 c74 で「内容の指紋」版を併記）',
     'scripts/c64_meta_audit4.py', 'c50-63 の事前固定行の引用は 10 種・㉛ 7/13・採用候補の機械抽出 = 72・75・93・69（≥2 回引用 or 反証が再発防止を明記）・番号引用のみ＝下限（最重大反証）'],
    ['c64', '2026-11-24', 'M6 反証 verdict の採掘可能率（対象 c50-63・「- 判定:」1 行書式）＋手読み split 率', 'メタ',
     'findings REFUTE 節 65', '件数', 'c40-48 対象取得 8/8・判定語 8/8', 'n/a', 'n/a', 'c50-63 対象 旧 regex 0/11（拡張 11/11）・判定語 n/a 8/11・手読み split 11/11・副産物 broken 8/11', 'n/a', 'n/a',
     '計器の盲目（書式ドリフト）: broken 率は c53 以降 採掘不能・手読み 73% は「記述の衛生」で c40-48 75% と比較不能', 'n/a', 'no',
     'scripts/c64_meta_audit4.py', '方法論候補 109（機械可読 target/verdict 2 行・split-B/split-S 語彙）・110（メタに計器の自己診断・n/a 率 >20% で修正案）・H_BLIND は c50-63 で不成立（主型は過剰主張: 多重検定・se 独立合成・確定語・帰属）'],
]
with open(P, 'a', encoding='utf-8', newline='') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator='\n')
    for r in rows:
        assert len(r) == 17, len(r)
        w.writerow(r)
n = sum(1 for _ in open(P, encoding='utf-8'))
bad = [i for i, r in enumerate(csv.reader(open(P, encoding='utf-8'))) if len(r) != 17]
print(f'cells.csv lines {n}・17 フィールドでない行 {bad}')
