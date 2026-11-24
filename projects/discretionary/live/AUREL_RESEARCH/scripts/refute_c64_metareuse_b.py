# -*- coding: utf-8 -*-
"""
反証レーン b — refute_c64_metareuse.py の 3 つの計器欠陥の修正（自分の攻撃への自己反証を含む）
================================================================================================
a 本目で出た判定: T1 survived（拡張 0.23・指紋 0.05）／T2 broken（<50 の引用 97% が文脈なし丸数字）／
T4 weakened（open の 10% に解決標識）／T6 survived（コード実装）。
b 本目はこの 3 点を潰す。**どれも a 本目の判定を私に不利な方へ動かし得る**ことを先に宣言する。

事前固定（数字を見る前・この docstring が正本）:

  B1（T2 の読み替え・a 本目の A3 は結論が逆向きかもしれない）. a 本目は「⑨ ⑪ ⑬ 等の文脈なし丸数字 = 偽陽性」と
     解釈した。しかし backlog 冒頭行は「事前固定に必ず入れる方法論: ①…⑰」＝**採用済みの常設規則**であり、
     事前固定行の「1000 回（⑨）」は偽陽性ではなく **採用済み規則の本物の引用**である可能性が高い。
     そして c64 の `adopted` は 5 件（[4,13,15,16,17]）しか取れていない — CAND_NUM の丸数字分枝は
     `(?=[^\w]|$)` の先読みを要求するので「①SL/TP…」のように直後が語文字だと落ちる。
     → 冒頭行の丸数字を先読みなしで再抽出して真の採用集合を作り、c64 の <50 対照群（40 件）の何件が
     **実は採用済み**かを数える。
     判定規則 D-B1: 引用された <50 候補 20 件のうち **≥10 件**が真の採用集合に属する → **T2 broken**
     （対照 50% は「未採用候補は引用される」ではなく「採用済みの常設規則は引用される」を測っている＝
     T1 の 6% と比較する対照として無効）。<10 件なら a 本目の偽陽性解釈を採る。

  B2（A4 の露出交絡・私の指紋検定は検出力が無かった）. a 本目の指紋一致は「初出後の節に 1 本でも一致があるか」。
     しかし初出後の節は 3〜16 本、初出前は 54〜70 本＝**any 統計は数の多い側に機械的に偏る**
     （プラセボ 0.21 > post 0.05 はこれで説明できる。並べ替えの帰無平均 −0.147 ≈ 観測 −0.158 がその証拠）。
     → 節あたり率（一致節数 ÷ 対象節数）で post と pre を測り直し、同じ並べ替え検定にかける。
     判定規則 D-B2: 節あたり率で post − pre > 0 かつ並べ替え p < 0.0083（Bonferroni 継続）→ 内容再利用あり＝
     **T1 弱化**。そうでなければ T1 は指紋検定でも survive（＝c64 の「6% は下限」という自己反証は**成立しない**）。

  B3（A5 の緩い regex・私の帳簿検定）. a 本目の解決標識 regex は `済|完了|採用|棄却|保留|却下|結論` で、
     「採用基準」「正式採用の提案」のような**未解決の提案文**も拾う＝私が c64 を責めた緩さと同型。
     → 厳格版 `済[:：)）、。\s]|採用済|棄却済|却下済|\[x\]|→ *済` で再計数。
     判定規則 D-B3: 厳格版が open 行の <10% → **a 本目の D-A5「T4 weakened」を取り下げ、T4 は inconclusive**
     （自分の計器が緩かっただけ）。≥10% なら weakened を維持。

  B4（D-A6 の実装バグ）. a 本目のコードは `v_a6 = broken if m10_flip` と書いたが、docstring の登記規則は
     「当たり 3 のうち ≥2 が計器保証または自己成就 → T6 broken」。**登記規則を優先**して再判定する（実装でなく登記が正本）。

  多重検定: a 本目の 6 本に B1–B4 を加えて 10 本。統計的検定は B2 の並べ替え 1 本のみ＝α 0.05/10 = 0.005 を課す。
  look-ahead/corpus: a 本目と同じスナップショット（findings@5694a9c4f・backlog@d73697554）。seed 20261124。
  入出力: 読む = data/c64_snapshot/**・scripts/c64_meta_audit4.py。書く = data/refute_c64_metareuse_b.md と .json のみ。
  発注なし・本番編集なし・MT5 なし・外部通信なし・scan なし。
"""  # noqa: W605
import re, glob, os, sys, io, json, math, random
from collections import defaultdict
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, 'data', 'c64_snapshot')
FILES = sorted(glob.glob(os.path.join(SNAP, 'findings', '2026-11-*.md')))
BACKLOG = os.path.join(SNAP, 'backlog.md')

HDR = re.compile(r'^## \[(cycle(\d+)[^\]]*|REFUTE)\]')
CIRC = {}
for i, ch in enumerate('①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'): CIRC[ch] = i + 1
for i, ch in enumerate('㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟'): CIRC[ch] = 21 + i
for i, ch in enumerate('㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿'): CIRC[ch] = 36 + i
CAND_NUM = re.compile(r'方法論\s*(?:候補\s*)?(\d{2,3})\b|方法論\s*(?:候補\s*)?([①-⑳㉑-㉟㊱-㊿])|候補\s*(\d{2,3})\b|方法論\s*([①-⑳㉑-㉟㊱-㊿])|([①-⑳㉑-㉟㊱-㊿])(?=[^\w]|$)')
CIRC_ANY = re.compile(r'[①-⑳㉑-㉟㊱-㊿]')   # 先読みなし（真の採用集合用）

OUT = []
def pr(s=''):
    print(s); OUT.append(s)

def cands_of(s):
    out = set()
    for m in CAND_NUM.finditer(s):
        g = [x for x in m.groups() if x]
        if g:
            v = g[0]; out.add(CIRC[v] if v in CIRC else int(v))
    return out

def cand_hits(s):
    hits = []
    for m in CAND_NUM.finditer(s):
        gi = next((i for i, x in enumerate(m.groups()) if x), None)
        if gi is None:
            continue
        v = m.group(gi + 1)
        hits.append(dict(num=CIRC[v] if v in CIRC else int(v), explicit=gi in (0, 1, 2, 3)))
    return hits

def pre_block(lines):
    pre, grab = [], False
    for l in lines[1:]:
        if re.match(r'^\s*-\s*\**事前固定', l):
            grab = True; pre.append(l); continue
        if grab:
            if re.match(r'^\s{2,}-', l):
                pre.append(l); continue
            grab = False
    return '\n'.join(pre)

sections = []
for f in FILES:
    cur = None
    for line in open(f, encoding='utf-8'):
        m = HDR.match(line)
        if m:
            cur = dict(kind='R' if m.group(1) == 'REFUTE' else 'C',
                       cyc=int(m.group(2)) if m.group(1) != 'REFUTE' else None,
                       lines=[line.rstrip('\n')], file=os.path.basename(f))
            sections.append(cur)
        elif cur is not None:
            cur['lines'].append(line.rstrip('\n'))
for i, s in enumerate(sections):
    s['ord'] = i; s['txt'] = '\n'.join(s['lines']); s['pre'] = pre_block(s['lines'])
    s['cands_body'] = cands_of(s['txt']); s['cands_pre'] = cands_of(s['pre'])

bl_txt = open(BACKLOG, encoding='utf-8').read()
bl = bl_txt.split('\n')
cand_by_cyc = {}
for s in sections:
    if s['kind'] == 'R':
        continue
    d = cand_by_cyc.setdefault(s['cyc'], dict(pre=set(), body=set()))
    d['pre'] |= s['cands_pre']; d['body'] |= s['cands_body']
first_cyc = {}
for c in sorted(cand_by_cyc):
    for v in cand_by_cyc[c]['body']:
        if 1 <= v <= 130 and v not in first_cyc:
            first_cyc[v] = c
reuse = {v: dict(first=c0, pre=sorted(c for c in cand_by_cyc if c > c0 and v in cand_by_cyc[c]['pre']))
         for v, c0 in first_cyc.items()}
hdr_line = bl[4] if len(bl) > 4 else ''
adopted_c64 = cands_of(hdr_line)
hi50 = [v for v in sorted(first_cyc) if v >= 50 and v not in adopted_c64]
lo50 = [v for v in sorted(first_cyc) if v < 50 and v not in adopted_c64]

pr('# [REFUTE] b — a 本目の 3 計器欠陥の修正（うち 2 つは私自身の攻撃の欠陥）')

# ============================== B1 ==============================
pr('\n## B1 <50 対照群（c64 の 20/40 = 50%）は「未採用候補」ではなく「採用済みの常設規則」を測っていた')
adopted_true = sorted({CIRC[ch] for ch in CIRC_ANY.findall(hdr_line)})
pr(f'  - backlog 冒頭「事前固定に必ず入れる方法論」行: c64 の採掘 **{sorted(adopted_c64)}（{len(adopted_c64)} 件）**'
   f'／先読みなしの再抽出 **{adopted_true}（{len(adopted_true)} 件）**'
   f'（c64 本文の手読み「①〜⑫・⑮・⑯・⑰ の 15 件」と一致: {adopted_true == [1,2,3,4,5,6,7,8,9,10,11,12,15,16,17]}）')
pr(f'  - 冒頭行の先頭 160 字: 「{hdr_line[:160]}」')
cited_lo = [v for v in lo50 if reuse[v]['pre']]
in_adopted = [v for v in cited_lo if v in adopted_true]
pr(f'  - c64 の <50 対照群 {len(lo50)} 件・そのうち引用された {len(cited_lo)} 件 = {len(cited_lo)/len(lo50):.2f}（c64: 20/40 = 0.50）')
pr(f'  - **引用された {len(cited_lo)} 件のうち 真の採用集合に属する = {len(in_adopted)} 件 {in_adopted}**')
rest = [v for v in cited_lo if v not in adopted_true]
pr(f'  - 残り（本当に未採用で引用された <50 候補）= {len(rest)} 件 {rest}')
lo50_fix = [v for v in sorted(first_cyc) if v < 50 and v not in adopted_true]
k_fix = sum(1 for v in lo50_fix if reuse[v]['pre'])
pr(f'  - 真の採用集合を除いた対照群での再利用率: **{k_fix}/{len(lo50_fix)} = {k_fix/len(lo50_fix):.2f}**'
   f'（c64: 0.50／≥50 群: {sum(1 for v in hi50 if reuse[v]["pre"])}/{len(hi50)} = {sum(1 for v in hi50 if reuse[v]["pre"])/len(hi50):.2f}）')
v_b1 = 'broken' if len(in_adopted) >= 10 else 'survived'
pr(f'  - D-B1: 採用済み {len(in_adopted)} 件（閾値 ≥10）→ T2 **{v_b1}**')

# ============================== B2 ==============================
pr('\n## B2 指紋検定の露出交絡を外す（節あたり率）')
DEFLINE = {}
for l in bl:
    for m in re.finditer(r'方法論\s*候補\s*(\d{2,3})', l):
        v = int(m.group(1))
        if v not in DEFLINE or len(l) > len(DEFLINE[v]):
            DEFLINE[v] = l
TOKRX = re.compile(r'[一-龥]{2,}|[ァ-ヴ][ァ-ヴー]+|[A-Za-z][A-Za-z0-9_]{2,}')
STOP = set('候補 方法論 事前 固定 反証 判定 結果 場合 必要 今回 以下 以上 本数 中央 印字 併記 規則 使用 確認 記述 全部 一行 一回'.split())
PRE = [s for s in sections if s['pre']]
df = defaultdict(int)
for s in PRE:
    for t in set(TOKRX.findall(s['pre'])):
        df[t] += 1
first_ord = {}
for s in sections:
    for v in s['cands_body']:
        if 1 <= v <= 130 and v not in first_ord:
            first_ord[v] = s['ord']
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
def match(v, s, need=3):
    return sum(1 for t in fp[v] if t in s['pre']) >= need
def rates(births, need=3):
    """節あたり率: Σ一致節 / Σ対象節 を post/pre で返す。"""
    pa = pb = na = nb = 0
    for v, o0 in births:
        aft = [s for s in PRE if s['ord'] > o0]; bef = [s for s in PRE if s['ord'] < o0]
        pa += sum(1 for s in aft if match(v, s, need)); na += len(aft)
        pb += sum(1 for s in bef if match(v, s, need)); nb += len(bef)
    return (pa, na, pb, nb)
births = [(v, first_ord[v]) for v in fp]
for need in (3, 2):
    pa, na, pb, nb = rates(births, need)
    obs = pa / na - pb / nb
    random.seed(20261124)
    bl_ords = [o for _, o in births]
    null = []
    for _ in range(2000):
        perm = bl_ords[:]; random.shuffle(perm)
        a, n1, b, n2 = rates(list(zip(fp.keys(), perm)), need)
        null.append(a / n1 - b / n2)
    null = np.array(null)
    p = float((np.sum(null >= obs) + 1) / (len(null) + 1))
    pr(f'  - {need}/3 一致・節あたり率: 初出後 **{pa}/{na} = {pa/na:.4f}**／初出前 {pb}/{nb} = {pb/nb:.4f}'
       f'・差 {obs:+.4f}・並べ替え 帰無 {null.mean():+.4f}（sd {null.std():.4f}）・**p {p:.4f}**（α 0.005）')
    if need == 3:
        v_b2 = 'T1 弱化' if (obs > 0 and p < 0.005) else 'T1 survive'
        pr(f'  - D-B2: → **{v_b2}**')

# ============================== B3 ==============================
pr('\n## B3 自分の帳簿 regex を厳格化（a 本目 A5 の自己反証）')
open_lines = [l for l in bl if re.match(r'^\s*- \[ \]', l)]
LOOSE = re.compile(r'済|完了|採用|棄却|保留|却下|不要と判定|結論')
STRICT = re.compile(r'済[:：)）、。\s]|採用済|棄却済|却下済|\[x\]|→ *済|・済')
loose = [l for l in open_lines if LOOSE.search(l)]
strict = [l for l in open_lines if STRICT.search(l)]
pr(f'  - open 行 {len(open_lines)}・緩い regex {len(loose)}（{len(loose)/len(open_lines):.0%}・a 本目の数字）'
   f'・**厳格 regex {len(strict)}（{len(strict)/len(open_lines):.0%}）**')
for l in strict[:6]:
    pr(f'    - 厳格ヒット例: {l.strip()[:130]}')
false_pos = [l for l in loose if l not in strict]
pr(f'  - 緩いだけでヒットした（＝未解決の提案文を解決と誤判定した）行 {len(false_pos)}:')
for l in false_pos[:4]:
    pr(f'    - {l.strip()[:120]}')
v_b3 = 'weakened（維持）' if len(strict) / len(open_lines) >= 0.10 else 'inconclusive（a 本目の weakened を取り下げ）'
pr(f'  - D-B3: 厳格 {len(strict)/len(open_lines):.0%} → T4 **{v_b3}**')

# ============================== B4 ==============================
pr('\n## B4 D-A6 の登記規則で再判定（a 本目はコード実装が登記と不一致だった）')
selffulfil = 3  # (1) 計器保証（c64 自身が事前固定 (iv) で過小側と宣言）・(2)(3) 自分がやらない作業の予測
pr(f'  - 登記規則 D-A6: 当たり 3 のうち 計器保証または自己成就 = **{selffulfil}/3**（≥2）→ T6 **broken**')
pr('  - 注: 3 つの予測は「外れていない」。壊れたのは「当たり 3/7 が校正の証拠である」という読み方であって、'
   '予測の真偽ではない（M10 の 6% は B2 の指紋検定でも支持される＝真）。')
v_b4 = 'broken'

json.dump(dict(adopted_c64=sorted(adopted_c64), adopted_true=adopted_true, cited_lo=cited_lo,
               in_adopted=in_adopted, rest=rest, lo50_fix=(k_fix, len(lo50_fix)),
               loose=len(loose), strict=len(strict), open_lines=len(open_lines),
               verdicts=dict(B1=v_b1, B2=v_b2, B3=v_b3, B4=v_b4)),
          open(os.path.join(ROOT, 'data', 'refute_c64_metareuse_b.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=str)
open(os.path.join(ROOT, 'data', 'refute_c64_metareuse_b.md'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
pr('\n（書き出し: data/refute_c64_metareuse_b.md ・ .json）')
