# -*- coding: utf-8 -*-
"""
反証レーン 2026-11-24 09:30 — 対象: cycle64 (09:40) メタ監査 4 の肯定形主張
=========================================================================
PROMOTED.md は空（昇格候補ゼロ）。c64 は市場主張を含まない「メタ」サイクルだが、
**数値で断言した肯定形の結論**を持つ＝「研究機関の方法論層は write-only である」。
これを壊しにいく。壊す対象（c64 が自分で「盲点を数値で特定」と書いた量）:

  T1: 方法論候補（番号 ≥50）の再利用率 = **2/35 = 6%**（本文再言及でも 9/35 = 26%）
  T2: その対照 = 番号 <50 未採用 **20/40 = 50%**（6% を病理に見せている比較群）
  T3: 冒頭「必ず入れる方法論」の採用は **c16 以降 0 件（48 サイクル）**
  T4: backlog open **118 → 203**（+6/サイクル）・**判定済み 0**
  T5: 計器の盲目（対象 cycle 旧 regex 0/11・判定語 n/a 8/11）
  T6: 自己校正「事前予測 7 問中 当たり 3・外れ 2・判定不能 2」

GATE（数字を一切報告する前に・独立再実装で一致しなければ停止）:
  c64 の M10/M5 を再現する: backlog 候補番号 90（最大 108）・adopted [4,13,15,16,17]・
  初出が取れた候補 80（≥50 が 35・<50 未採用 40）・再利用 2/35・本文 9/35・<50 20/40・
  c50-63 の事前固定引用リスト（c54 [31,69,72,78] / c56 [2,61,72] / c63 [95] 等）・
  M5 open 203・前向き 39・needs 37・方法論 80・行数 384。

事前固定（数字を見る前に書いた・この docstring が正本）:

  A1 コーパス検閲（scope）. c64 の採掘器は `if kind == 'R': ... continue` で **REFUTE 節 65 本を
     まるごと落としている**（cand_by_cyc は研究レーン節のみ）。しかし両レーンとも「- 事前固定」
     という同じ見出しを使う（corpus 全体で 77 行）。全節（研究＋反証）を時系列 ordinal で並べ、
     「初出より後の節の事前固定ブロックでの引用」で再利用率を再計算する。
     陽性対照: c64 本文は「反証レーンが c54/c55/c56/c59 の事前固定で『候補 75 に従い』と明記」と
     書いている＝候補 75 は既知の真の再利用。拡張コーパスでも 75 が 0 なら A1 は失敗（私の負け）。
     判定規則 D-A1: 拡張再利用率 ≥0.50 → **T1 は「6%」の形で broken**／0.26–0.50 → T1 弱化
     （6% はレーン検閲の産物・「過半は未使用」は残る）／<0.26 → T1 は A1 を survive。

  A2 曝露（survivorship / immortal-candidate bias）. 候補 35 件の分母には c63 生まれ（後続サイクル 0）
     が入る。曝露 = 初出より後の節数。曝露バケット別の率・at-risk（候補 × 後続節）当たりの引用率・
     曝露を揃えた（後続 研究サイクル ≥10）部分集合での ≥50 vs <50 を印字。
     判定規則 D-A2: 揃えた曝露で ≥50 と <50 の差が **<0.15**（c64 は 0.44）→ **T2 broken**
     （「6% vs 50%」は品質差でなく年齢差）。

  A3 採掘器の偽陽性（placebo / 負の対照）. CAND_NUM の最終分枝 `([①-⑳…])(?=[^\w]|$)` は
     **文脈なしの丸数字を全部候補番号として拾う**（テンプレ節の「①帰無集合」「②推定器」が候補 1・2 に化ける）。
     (a) 事前固定ブロックの全ヒットを「regex 分枝」×「直前 8 字に 候補|方法論 があるか」で分類。
     (b) 存在しない番号（111–130）を注入して採掘器が何を返すか。
     (c) 年代矛盾（候補 66・96 の初出が c24＝番号が生まれる前）を該当行の印字で偽陽性と確定。
     判定規則 D-A3: <50 群の 20 件の引用のうち **≥50%** が「候補/方法論 文脈なしの丸数字」なら
     **T2 の 50% は引用の測定として broken**。

  A4 内容指紋（c64 が自分で登記した決着条件）. c64 の「最も重大な反証」は
     「6% は番号の明示引用しか数えていない。決着条件 = 候補ごとに内容の指紋（キーワード 2〜3 語）を
     定義して事前固定行をスキャンし、番号引用との差を印字する」。これを実行する。
     指紋 = backlog の候補定義行から、コーパス（全節の事前固定ブロック）での df が最小かつ df ≥2 の
     内容トークン 3 語（漢字 2 字以上連・カタカナ連・ラテン語）。df ≥2 を課すのは照合可能性の保証（検出力）。
     一致 = 後続節の事前固定ブロックに 3 語すべてが出現（感度分析として 2/3 も印字）。
     **校正（c64 が登記していない部分・これが無いと指紋は語彙重複を測るだけ）**: 同じ指紋を
     **初出より前**の節に当てたプラセボ率を測り、差 Δ と並べ替え検定（初出サイクルを 2000 回シャッフル）で p を出す。
     判定規則 D-A4: post ≥0.50 ∧ Δ ≥0.20 → **T1 broken**／post ≥0.26 ∧ Δ ≥0.10 → T1 弱化／
     それ以外 → T1 survive（指紋でも使われていない）。

  A5 帳簿（T4）. open `- [ ]` 行のうち本文に解決標識（済|完了|採用|棄却|保留|却下|[x]）を持つ行を数える。
     「判定済み 0」が測定値か定数かもソースで確認する。
     判定規則 D-A5: open 行の **≥10%** が解決標識つき → 「open 203・判定済み 0」は未裁定量の過大表示＝T4 弱化。

  A6 自己校正の再採点（T6）. A1/A4 で M10 が 30% を超えれば M10 の「当たり」は「外れ」に反転し 2/7。
     さらに 3 つの当たりのうち「計器が過小側に偏っていれば自動的に当たる」ものと
     「自分がやらなかった作業を自分が予測した（自己成就）」ものを数える。
     判定規則 D-A6: 当たり 3 のうち **≥2** が計器保証または自己成就 → **T6 は校正の証拠として broken**。

  多重検定: 攻撃は 6 本（T1 に 3・T2 に 2・T4/T6 に各 1）。統計的検定は A4 の並べ替え 1 本のみ＝
     Bonferroni α = 0.05/6 = 0.0083 を A4 に課す（p ≥0.0083 なら「差あり」と書かない）。
  look-ahead: 読むのは 2026-11-24 09:30 時点のファイル。c64 自身の節（cycle64）は
     **引用側コーパスから除外**（自分を数えると再利用率が上がる＝私に有利な汚染）。
     ただし候補 109/110 の初出は c64 なので分母にも入れない（≥50 の分母は c64 以前生まれのみ＝c64 と同じ 35 を維持）。
  survivorship: findings に書かれなかったサイクルは両レーンで見えない（c64 と同じ限界・継承）。
  D2: 市場の数字を扱わない（メタ監査の監査）。seed: 並べ替えは seed 20261124（決定論）。
  入出力: 読む = AUREL_RESEARCH/findings/*.md・backlog.md・scripts/c64_meta_audit4.py・data/c64_meta_audit4_result.md。
     書く = data/refute_c64_metareuse.md と同名 _run.log のみ。発注なし・本番編集なし・MT5 なし・外部通信なし・scan なし。

  事前の最重大反証（自分の攻撃への）:
    (i) A1 は「反証レーンも方法論候補を使っている」を示すだけで、「研究レーンが使っていない」は壊れない可能性がある
        → レーン別に分解して印字し、研究レーンだけの率も必ず出す。
    (ii) 内容指紋は語彙が被るほど偽陽性が出る＝A4 のプラセボ校正が無ければ無意味（だから校正を事前固定した）。
    (iii) n=35（曝露を揃えると更に減る）＝率の se ≈0.08 以上。D-A1/D-A2 の閾値差は 1–2 se 級で
        「壊れた」は点推定の話でしかない → 区間（Wilson 95%）も併記する。
"""
import re, glob, os, sys, io, json, math
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, 'findings', '2026-11-*.md')))

# ---------- c64 の採掘器（1 文字も変えずに移植・GATE 用） ----------
HDR = re.compile(r'^## \[(cycle(\d+)[^\]]*|REFUTE)\]')
CIRC = {}
for i, ch in enumerate('①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'): CIRC[ch] = i + 1
for i, ch in enumerate('㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟'): CIRC[ch] = 21 + i
for i, ch in enumerate('㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿'): CIRC[ch] = 36 + i
CAND_NUM = re.compile(r'方法論\s*(?:候補\s*)?(\d{2,3})\b|方法論\s*(?:候補\s*)?([①-⑳㉑-㉟㊱-㊿])|候補\s*(\d{2,3})\b|方法論\s*([①-⑳㉑-㉟㊱-㊿])|([①-⑳㉑-㉟㊱-㊿])(?=[^\w]|$)')

OUT = []
def pr(s=''):
    print(s); OUT.append(s)

def cands_of(s):
    out = set()
    for m in CAND_NUM.finditer(s):
        g = [x for x in m.groups() if x]
        if not g:
            continue
        v = g[0]
        out.add(CIRC[v] if v in CIRC else int(v))
    return out

def cand_hits(s):
    """ヒットごとに (番号, 分枝, 文脈つきか, マッチ文字列, 前後文脈) を返す（A3 用）。"""
    hits = []
    for m in CAND_NUM.finditer(s):
        gi = next((i for i, x in enumerate(m.groups()) if x), None)
        if gi is None:
            continue
        v = m.group(gi + 1)
        num = CIRC[v] if v in CIRC else int(v)
        lo = max(0, m.start() - 8)
        ctx = s[lo:m.end() + 4].replace('\n', ' ')
        explicit = gi in (0, 1, 2, 3)  # 候補/方法論 を伴う分枝
        hits.append(dict(num=num, branch=gi, explicit=explicit, raw=m.group(0), ctx=ctx))
    return hits

def pre_block(lines):
    """c64 と同じ「- 事前固定」ブロック抽出（箇条書き＋直下のサブ箇条書き）。"""
    pre, grab = [], False
    for l in lines[1:]:
        if re.match(r'^\s*-\s*\**事前固定', l):
            grab = True; pre.append(l); continue
        if grab:
            if re.match(r'^\s{2,}-', l):
                pre.append(l); continue
            grab = False
    return '\n'.join(pre)

# ---------- 節の読み込み（全節・時系列 ordinal つき） ----------
sections = []
for f in FILES:
    cur = None
    for line in open(f, encoding='utf-8'):
        m = HDR.match(line)
        if m:
            kind = 'R' if m.group(1) == 'REFUTE' else 'C'
            cyc = int(m.group(2)) if kind == 'C' else None
            cur = dict(kind=kind, cyc=cyc, lines=[line.rstrip('\n')], header=line.rstrip('\n'),
                       file=os.path.basename(f))
            sections.append(cur)
        elif cur is not None:
            cur['lines'].append(line.rstrip('\n'))
for i, s in enumerate(sections):
    s['ord'] = i
    s['txt'] = '\n'.join(s['lines'])
    s['pre'] = pre_block(s['lines'])
    s['cands_body'] = cands_of(s['txt'])
    s['cands_pre'] = cands_of(s['pre'])

bl_txt = open(os.path.join(ROOT, 'backlog.md'), encoding='utf-8').read()
bl = bl_txt.split('\n')

pr('# [REFUTE] c64 メタ監査 4 の「方法論層は write-only（再利用率 6%）」を壊す')
pr(f'- 節 {len(sections)}（研究 {sum(1 for s in sections if s["kind"]=="C")}・REFUTE {sum(1 for s in sections if s["kind"]=="R")}）'
   f'・事前固定ブロックを持つ節 {sum(1 for s in sections if s["pre"])}'
   f'（研究 {sum(1 for s in sections if s["kind"]=="C" and s["pre"])}・REFUTE {sum(1 for s in sections if s["kind"]=="R" and s["pre"])}）')

# =========================================================================
# GATE: c64 の M10/M5 を独立再実装で再現
# =========================================================================
pr('\n## GATE — c64 の M10/M5 の再現')
cand_by_cyc = {}
for s in sections:
    if s['kind'] == 'R':
        continue
    c = s['cyc']
    d = cand_by_cyc.setdefault(c, dict(pre=set(), body=set()))
    d['pre'] |= s['cands_pre']; d['body'] |= s['cands_body']

bl_cands = {v for v in cands_of(bl_txt) if 1 <= v <= 130}
hdr_line = bl[4] if len(bl) > 4 else ''
adopted = cands_of(hdr_line)

first_cyc = {}
for c in sorted(cand_by_cyc):
    for v in cand_by_cyc[c]['body']:
        if 1 <= v <= 130 and v not in first_cyc:
            first_cyc[v] = c
reuse = {}
for v, c0 in first_cyc.items():
    reuse[v] = dict(first=c0,
                    pre=sorted(c for c in cand_by_cyc if c > c0 and v in cand_by_cyc[c]['pre']),
                    body=sorted(c for c in cand_by_cyc if c > c0 and v in cand_by_cyc[c]['body']))
hi50 = [v for v in sorted(first_cyc) if v >= 50 and v not in adopted]
lo50 = [v for v in sorted(first_cyc) if v < 50 and v not in adopted]
k_hi = sum(1 for v in hi50 if reuse[v]['pre']); k_hi_body = sum(1 for v in hi50 if reuse[v]['body'])
k_lo = sum(1 for v in lo50 if reuse[v]['pre'])

open_lines = [l for l in bl if re.match(r'^\s*- \[ \]', l)]
m5 = dict(open=len(open_lines), fwd=sum(1 for l in open_lines if '前向き' in l),
          needs=sum(1 for l in open_lines if re.search(r'needs (data|cache)', l)),
          meth=sum(1 for l in open_lines if '方法論' in l), lines=len(bl))

gate = {
    'bl_cands=90': len(bl_cands) == 90,
    'max=108': (max(bl_cands) if bl_cands else 0) == 108,
    'adopted=[4,13,15,16,17]': sorted(adopted) == [4, 13, 15, 16, 17],
    'first_cyc=80': len(first_cyc) == 80,
    'hi50=35': len(hi50) == 35,
    'lo50=40': len(lo50) == 40,
    'reuse_hi=2': k_hi == 2,
    'reuse_hi_body=9': k_hi_body == 9,
    'reuse_lo=20': k_lo == 20,
    'open=203': m5['open'] == 203,
    'fwd=39': m5['fwd'] == 39,
    'needs=37': m5['needs'] == 37,
    'meth=80': m5['meth'] == 80,
    'bl_lines=384': m5['lines'] == 384,
}
for k, v in gate.items():
    pr(f'  - {k}: {"OK" if v else "MISMATCH"}')
pr(f'  - 実測: 候補番号 {len(bl_cands)}（最大 {max(bl_cands)}）・adopted {sorted(adopted)}・初出 {len(first_cyc)}'
   f'・hi50 {len(hi50)}・lo50 {len(lo50)}・再利用 hi {k_hi}/{len(hi50)}・本文 {k_hi_body}/{len(hi50)}・lo {k_lo}/{len(lo50)}'
   f'・open {m5["open"]}・前向き {m5["fwd"]}・needs {m5["needs"]}・方法論 {m5["meth"]}・行 {m5["lines"]}')
GATE_PASS = all(gate.values())
pr(f'  - **GATE {"PASS" if GATE_PASS else "FAIL"}**')
if not GATE_PASS:
    pr('\nGATE FAIL — 再現できないので判定を出さずに停止する（憲章 C・事前固定どおり）。')
    open(os.path.join(ROOT, 'data', 'refute_c64_metareuse.md'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
    sys.exit(1)

def wilson(k, n):
    if n == 0:
        return (None, None)
    z = 1.959964
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))

# =========================================================================
# A1 コーパス検閲（REFUTE 節 65 本を戻す）
# =========================================================================
pr('\n## A1 コーパス検閲 — c64 の採掘器は REFUTE 節をまるごと落としている')
pr('  - c64 scripts/c64_meta_audit4.py の該当行: `for kind, cyc, lines, header, fname in sections:` → `if kind == \'R\': ... continue`'
   '（cand_by_cyc/prefix_by_cyc は研究レーン節のみ）')
# 全節 ordinal 軸での初出と後続引用
first_ord, first_kind = {}, {}
for s in sections:
    for v in s['cands_body']:
        if 1 <= v <= 130 and v not in first_ord:
            first_ord[v] = s['ord']; first_kind[v] = s['kind']
# 引用側コーパスから cycle64 節を除外（look-ahead 汚染の排除・事前固定どおり）
CITE = [s for s in sections if not (s['kind'] == 'C' and s['cyc'] == 64)]
def later_cites(v, lane=None):
    o0 = first_ord.get(v)
    if o0 is None:
        return []
    return [s for s in CITE if s['ord'] > o0 and v in s['cands_pre'] and (lane is None or s['kind'] == lane)]

ext = {}
for v in hi50:
    cs = later_cites(v)
    ext[v] = dict(all=[s['ord'] for s in cs],
                  R=[s['ord'] for s in cs if s['kind'] == 'R'],
                  C=[s['ord'] for s in cs if s['kind'] == 'C'],
                  labels=[(s['kind'], s['cyc'], s['file']) for s in cs])
k_ext = sum(1 for v in hi50 if ext[v]['all'])
k_ext_R = sum(1 for v in hi50 if ext[v]['R'])
k_ext_C = sum(1 for v in hi50 if ext[v]['C'])
k_only_R = sum(1 for v in hi50 if ext[v]['R'] and not ext[v]['C'])
pr(f'  - 拡張コーパス（研究＋反証・cycle64 節を引用側から除外）での再利用率 **{k_ext}/{len(hi50)} = {k_ext/len(hi50):.2f}**'
   f' Wilson95 {wilson(k_ext, len(hi50))}（c64: 2/35 = 0.06）')
pr(f'  - レーン分解: 反証レーンの事前固定で引用 {k_ext_R}/{len(hi50)}・研究レーンのみ {k_ext_C}/{len(hi50)}'
   f'・**反証だけが引用（c64 には原理的に見えない） {k_only_R}/{len(hi50)}**')
pr('  - 陽性対照 候補 75（c64 本文「反証レーンが c54/c55/c56/c59 の事前固定で『候補 75 に従い』と明記」）: '
   f'c64 の採掘器 {reuse[75]["pre"] or "—"}／拡張 {ext[75]["labels"] or "—"}')
pr('  - 候補別（拡張で引用が見つかったもの）:')
for v in hi50:
    if ext[v]['all']:
        pr(f'    - 候補 {v}: 初出 ord {first_ord[v]}（{first_kind[v]}）→ 引用 {ext[v]["labels"]}')

# =========================================================================
# A2 曝露（survivorship）
# =========================================================================
pr('\n## A2 曝露 — 分母 35 に「生まれたばかりで引用される機会が無い」候補が入っている')
N_ORD = len(sections)
def expo(v):
    o0 = first_ord.get(v)
    return sum(1 for s in CITE if s['ord'] > o0 and s['pre'])  # 後続の「事前固定を持つ節」数
def expo_cyc(v):
    c0 = first_cyc.get(v)
    return sum(1 for c in cand_by_cyc if c > c0)
rows = [(v, first_cyc[v], expo_cyc(v), expo(v), bool(reuse[v]['pre']), bool(ext[v]['all'])) for v in hi50]
pr('  - 曝露バケット（後続 研究サイクル数）× 引用率:')
for lo, hi in ((0, 2), (3, 5), (6, 10), (11, 99)):
    sub = [r for r in rows if lo <= r[2] <= hi]
    if sub:
        k1 = sum(1 for r in sub if r[4]); k2 = sum(1 for r in sub if r[5])
        pr(f'    - 後続 {lo}–{hi} サイクル: n {len(sub)}・c64 採掘器 {k1}/{len(sub)} = {k1/len(sub):.2f}'
           f'・拡張 {k2}/{len(sub)} = {k2/len(sub):.2f}')
# at-risk 率
ar_hi = sum(len(ext[v]['all']) for v in hi50); ar_hi_n = sum(expo(v) for v in hi50)
lo_ext = {v: later_cites(v) for v in lo50}
ar_lo = sum(len(lo_ext[v]) for v in lo50); ar_lo_n = sum(expo(v) for v in lo50)
pr(f'  - at-risk（候補 × 後続の事前固定節）当たり引用: ≥50 {ar_hi}/{ar_hi_n} = {ar_hi/max(1,ar_hi_n):.4f}'
   f'／<50 {ar_lo}/{ar_lo_n} = {ar_lo/max(1,ar_lo_n):.4f}')
# 曝露を揃える: 後続 研究サイクル ≥10
m_hi = [v for v in hi50 if expo_cyc(v) >= 10]; m_lo = [v for v in lo50 if expo_cyc(v) >= 10]
def rate(vs, key):
    if not vs:
        return (0, 0, None)
    k = sum(1 for v in vs if (reuse[v]['pre'] if key == 'c64' else later_cites(v)))
    return (k, len(vs), k / len(vs))
r1 = rate(m_hi, 'c64'); r2 = rate(m_lo, 'c64'); r3 = rate(m_hi, 'ext'); r4 = rate(m_lo, 'ext')
pr(f'  - 曝露を揃えた（後続 研究サイクル ≥10）: ≥50 c64 {r1[0]}/{r1[1]} = {r1[2] if r1[2] is None else round(r1[2],2)}'
   f'／<50 c64 {r2[0]}/{r2[1]} = {r2[2] if r2[2] is None else round(r2[2],2)}'
   f'  ‖ 拡張 ≥50 {r3[0]}/{r3[1]} = {r3[2] if r3[2] is None else round(r3[2],2)}'
   f'／<50 {r4[0]}/{r4[1]} = {r4[2] if r4[2] is None else round(r4[2],2)}')
if r1[2] is not None and r2[2] is not None:
    pr(f'  - **差（<50 − ≥50）: c64 の非調整 0.44 → 曝露調整 {r2[2]-r1[2]:+.2f}（c64 採掘器）／{r4[2]-r3[2]:+.2f}（拡張）**')

# =========================================================================
# A3 採掘器の偽陽性（placebo）
# =========================================================================
pr('\n## A3 採掘器の偽陽性 — 文脈なしの丸数字が「候補の引用」に化ける')
tot, expl, bare = 0, 0, []
for s in CITE:
    for h in cand_hits(s['pre']):
        tot += 1
        if h['explicit']:
            expl += 1
        else:
            bare.append((s['kind'], s['cyc'], h['num'], h['ctx']))
pr(f'  - 全節の事前固定ブロック内ヒット {tot}・候補/方法論 文脈つき {expl}・**文脈なしの丸数字 {len(bare)}**')
pr('  - 文脈なしヒットの例（最大 12・ctx は前後）:')
for b in bare[:12]:
    pr(f'    - {b[0]}{b[1] if b[1] else ""} → 候補 {b[2]} と解釈: 「{b[3][:60]}」')
# <50 群の引用の内訳
lo_expl, lo_bare = 0, 0
for v in lo50:
    for s in lo_ext[v]:
        hs = [h for h in cand_hits(s['pre']) if h['num'] == v]
        if any(h['explicit'] for h in hs):
            lo_expl += 1
        elif hs:
            lo_bare += 1
pr(f'  - **<50 群（対照・c64 の 20/40 = 50%）の引用 延べ {lo_expl+lo_bare} のうち 文脈なし {lo_bare}'
   f'（{lo_bare/max(1,lo_expl+lo_bare):.0%}）**')
lo50_expl_cands = sum(1 for v in lo50 if any(any(h['explicit'] and h['num'] == v for h in cand_hits(s['pre'])) for s in lo_ext[v]))
pr(f'  - 文脈つき引用だけを数えた <50 の再利用率: {lo50_expl_cands}/{len(lo50)} = {lo50_expl_cands/len(lo50):.2f}（c64: 20/40 = 0.50）')
# (b) 存在しない番号の注入
ghost = [v for v in range(111, 131) if v in bl_cands or v in first_cyc]
pr(f'  - 注入（存在しない番号 111–130）: 採掘器が候補として返したもの {ghost or "なし"}')
# (c) 年代矛盾
pr('  - 年代矛盾（番号が存在し得ない時期に初出と判定された候補）:')
for v in (66, 96):
    c0 = first_cyc.get(v)
    sec = next((s for s in sections if s['kind'] == 'C' and s['cyc'] == c0), None)
    ln = next((l for l in sec['lines'] if v in cands_of(l)), '') if sec else ''
    pr(f'    - 候補 {v}: 初出 c{c0} / 該当行「{ln.strip()[:120]}」')

# =========================================================================
# A4 内容指紋（c64 が登記した決着条件）＋ プラセボ校正
# =========================================================================
pr('\n## A4 内容指紋（c64 の登記した決着条件）＋ 初出前プラセボ校正')
DEFLINE = {}
for l in bl:
    for m in re.finditer(r'方法論\s*候補\s*(\d{2,3})', l):
        v = int(m.group(1))
        if v not in DEFLINE or len(l) > len(DEFLINE[v]):
            DEFLINE[v] = l
TOKRX = re.compile(r'[一-龥]{2,}|[ァ-ヴ][ァ-ヴー]+|[A-Za-z][A-Za-z0-9_]{2,}')
STOP = set('候補 方法論 事前 固定 反証 判定 結果 場合 必要 今回 以下 以上 本数 中央 印字 併記 規則 使用 確認 記述 全部 一行 一回'.split())
PRE_BLOCKS = [(s, s['pre']) for s in CITE if s['pre']]
df = defaultdict(int)
for s, p in PRE_BLOCKS:
    for t in set(TOKRX.findall(p)):
        df[t] += 1
fp = {}
for v in hi50:
    l = DEFLINE.get(v, '')
    if not l:
        continue
    body = re.sub(r'^.*?方法論\s*候補\s*\d{2,3}[^）)]*[）)]?[:：]?', '', l)
    toks = [t for t in dict.fromkeys(TOKRX.findall(body)) if t not in STOP and len(t) >= 2 and df.get(t, 0) >= 2]
    toks.sort(key=lambda t: (df[t], -len(t)))
    if len(toks) >= 3:
        fp[v] = toks[:3]
pr(f'  - 指紋が作れた候補 {len(fp)}/{len(hi50)}（定義行が取れた {sum(1 for v in hi50 if v in DEFLINE)}・df ≥2 の内容語 3 つ以上）')
def fp_match(v, s, need=3):
    return sum(1 for t in fp[v] if t in s['pre']) >= need
post3 = post2 = pre3 = pre2 = 0
det = []
for v in fp:
    o0 = first_ord[v]
    aft = [s for s, _ in PRE_BLOCKS if s['ord'] > o0]
    bef = [s for s, _ in PRE_BLOCKS if s['ord'] < o0]
    a3 = [s for s in aft if fp_match(v, s, 3)]; b3 = [s for s in bef if fp_match(v, s, 3)]
    a2 = [s for s in aft if fp_match(v, s, 2)]; b2 = [s for s in bef if fp_match(v, s, 2)]
    post3 += bool(a3); pre3 += bool(b3); post2 += bool(a2); pre2 += bool(b2)
    det.append((v, fp[v], len(aft), len(bef), len(a3), len(b3), len(a2), len(b2)))
n_fp = len(fp)
pr(f'  - **3/3 一致: 初出後 {post3}/{n_fp} = {post3/n_fp:.2f}（Wilson {wilson(post3,n_fp)}）／初出前プラセボ {pre3}/{n_fp} = {pre3/n_fp:.2f}'
   f'・Δ {post3/n_fp - pre3/n_fp:+.2f}**')
pr(f'  - 2/3 一致（感度）: 初出後 {post2}/{n_fp} = {post2/n_fp:.2f}／プラセボ {pre2}/{n_fp} = {pre2/n_fp:.2f}・Δ {post2/n_fp - pre2/n_fp:+.2f}')
# 並べ替え検定: 初出 ordinal をシャッフルして Δ の帰無分布
import random
random.seed(20261124)
ords_pre = [s['ord'] for s, _ in PRE_BLOCKS]
obs = post3 / n_fp - pre3 / n_fp
null = []
births = [first_ord[v] for v in fp]
for _ in range(2000):
    perm = births[:]; random.shuffle(perm)
    a = b = 0
    for v, o0 in zip(fp, perm):
        aft = any(fp_match(v, s, 3) for s, _ in PRE_BLOCKS if s['ord'] > o0)
        bef = any(fp_match(v, s, 3) for s, _ in PRE_BLOCKS if s['ord'] < o0)
        a += aft; b += bef
    null.append(a / n_fp - b / n_fp)
import numpy as np
null = np.array(null)
p_perm = float((np.sum(null >= obs) + 1) / (len(null) + 1))
pr(f'  - 並べ替え検定（初出 ordinal を 2000 回シャッフル・seed 20261124）: 観測 Δ {obs:+.3f}'
   f'・帰無 平均 {null.mean():+.3f}（sd {null.std():.3f}）・**p {p_perm:.4f}**（Bonferroni α 0.0083）')
pr('  - 候補別（指紋 / 後続節 / 前節 / 3-3 後 / 3-3 前）:')
for d in sorted(det, key=lambda x: -x[4])[:18]:
    pr(f'    - 候補 {d[0]}: {d[1]} → 後 {d[4]}/{d[2]}・前 {d[5]}/{d[3]}（2/3: 後 {d[6]}・前 {d[7]}）')

# =========================================================================
# A5 帳簿（T4）
# =========================================================================
pr('\n## A5 帳簿 — 「open 203・判定済み 0」')
RES = re.compile(r'済|完了|採用|棄却|保留|却下|不要と判定|結論')
res_lines = [l for l in open_lines if RES.search(l)]
meth_lines = [l for l in open_lines if '方法論' in l]
meth_res = [l for l in meth_lines if RES.search(l)]
pr(f'  - open `- [ ]` 行 {len(open_lines)} のうち本文に解決標識（済/完了/採用/棄却/保留/却下/結論）を持つ行 **{len(res_lines)}'
   f'（{len(res_lines)/len(open_lines):.0%}）**・方法論 open 行 {len(meth_lines)} 中 {len(meth_res)}（{len(meth_res)/max(1,len(meth_lines)):.0%}）')
for l in meth_res[:6]:
    pr(f'    - 例: {l.strip()[:150]}')
src = open(os.path.join(ROOT, 'scripts', 'c64_meta_audit4.py'), encoding='utf-8').read()
hard = [l for l in src.split('\n') if '判定済み' in l]
pr('  - 「判定済み 0」はソース上 測定値か定数か:')
for l in hard:
    pr(f'    - `{l.strip()[:160]}`')

# =========================================================================
# A6 自己校正の再採点（T6）
# =========================================================================
pr('\n## A6 自己校正の再採点')
m10_flip = (k_ext / len(hi50) >= 0.30) or ((post3 / n_fp) >= 0.30)
pr(f'  - c64 の採点: 当たり 3（M10 <30%・M7 遡及 0／単位列 無・採用数 不変）／外れ 2／判定不能 2')
pr(f'  - M10 の「<30%」は拡張 {k_ext/len(hi50):.2f}・内容指紋 {post3/n_fp:.2f} → '
   f'**{"反転（当たり → 外れ）" if m10_flip else "維持"}** → 当たり {2 if m10_flip else 3}/7')
pr('  - 当たり 3 件の性質: (1) M10 <30% = 採掘器が番号引用しか数えない＝過小側に偏ることを c64 自身が '
   '事前固定 (iv) で宣言済み＝**計器保証**。(2) M7「c1-39 遡及登記 0・mde 単位列 無」= その作業をするのは '
   '研究レーン自身＝**自己成就**（やらなければ当たる）。(3) 採用数 不変 = 冒頭行を編集するのも研究レーン自身＝**自己成就**。')

# =========================================================================
# 判定
# =========================================================================
pr('\n## 判定（事前固定した規則どおり）')
r_ext = k_ext / len(hi50); r_fp = post3 / n_fp; d_fp = obs
v_a1 = 'broken' if r_ext >= 0.50 else ('weakened' if r_ext >= 0.26 else 'survived')
v_a4 = 'broken' if (r_fp >= 0.50 and d_fp >= 0.20) else ('weakened' if (r_fp >= 0.26 and d_fp >= 0.10) else 'survived')
gap_adj = (r2[2] - r1[2]) if (r1[2] is not None and r2[2] is not None) else None
v_a2 = 'broken' if (gap_adj is not None and gap_adj < 0.15) else 'survived'
v_a3 = 'broken' if (lo_bare / max(1, lo_expl + lo_bare)) >= 0.50 else 'survived'
v_a5 = 'weakened' if (len(res_lines) / len(open_lines)) >= 0.10 else 'survived'
v_a6 = 'broken' if m10_flip else 'survived'
pr(f'  - D-A1（コーパス検閲）: 拡張 {r_ext:.2f} → T1 **{v_a1}**')
pr(f'  - D-A2（曝露調整）: 差 {gap_adj if gap_adj is None else round(gap_adj,2)} → T2 **{v_a2}**')
pr(f'  - D-A3（偽陽性）: <50 の文脈なし比率 {lo_bare/max(1,lo_expl+lo_bare):.0%} → T2 **{v_a3}**')
pr(f'  - D-A4（内容指紋）: post {r_fp:.2f}・Δ {d_fp:+.2f}・p {p_perm:.4f} → T1 **{v_a4}**')
pr(f'  - D-A5（帳簿）: 解決標識つき open 行 {len(res_lines)/len(open_lines):.0%} → T4 **{v_a5}**')
pr(f'  - D-A6（自己校正）: → T6 **{v_a6}**')

json.dump(dict(gate=gate, hi50=hi50, k_c64=k_hi, k_ext=k_ext, k_ext_R=k_ext_R, k_ext_C=k_ext_C, k_only_R=k_only_R,
               expo_rows=rows, ar=(ar_hi, ar_hi_n, ar_lo, ar_lo_n), matched=(r1, r2, r3, r4),
               fp={str(k): v for k, v in fp.items()}, post3=post3, pre3=pre3, post2=post2, pre2=pre2,
               n_fp=n_fp, p_perm=p_perm, obs=obs, bare=len(bare), tot_hits=tot, lo_bare=lo_bare, lo_expl=lo_expl,
               res_lines=len(res_lines), open_lines=len(open_lines),
               verdicts=dict(A1=v_a1, A2=v_a2, A3=v_a3, A4=v_a4, A5=v_a5, A6=v_a6)),
          open(os.path.join(ROOT, 'data', 'refute_c64_metareuse.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=str)
open(os.path.join(ROOT, 'data', 'refute_c64_metareuse.md'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
pr('\n（書き出し: data/refute_c64_metareuse.md ・ .json）')
