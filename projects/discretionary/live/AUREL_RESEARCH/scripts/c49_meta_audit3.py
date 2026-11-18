# -*- coding: utf-8 -*-
"""
c49 メタ監査 3（憲章 F.6: 10 サイクルに 1 回・前回 c39 11-11・backlog「次メタ（c49 頃）」）
=====================================================================================
問い: c39 が c1-39 の findings 本文から出した「研究レーン自身の統計」を、c40-48（c39 の後に生まれた 9 サイクル＝
  c39 の設計変更〔ゲート ㉛・双子設計・cells.csv〕の **外**）で再計算し、研究方法の盲点を 1 つ数値で特定する。
  在 = c1-39 の本文（c39 の数字の再現）／外 = c40-48 の本文（c39 以後）。両方同じ採掘器（c39 の正規表現を変更しない）。

事前固定（数字を見る前・この docstring）:
  M1 t 分布: 外（c40-48）の R 単位 在ラベル t の sd は在（c1-39）2.23 より小さいか同程度（≤2.3）と予測（ゲートで条件づけセルが減るため）。
  M2 在→外 再現率: (a) R 単位 |t_在|≥2 → 外 同符号∧|t_外|≥1.5 は c1-39 で 54%（c39 報告）。c40-48 でも「条件づけ Δμ 型は 0/n・構造型 ≥50%」を予測。
     (b) 校正群（|t_在|<1）の「外 同符号∧|t_外|≥1.5」率は帰無 6.7% の 2 倍以内（≤13%）なら採掘は健全。c39 では 7%（R 単位）・21%（全単位）。
  M3 ゲート ㉛: c40-48 の「ゲート ㉛ 不通過」「走らせない/ず」言及は ≥1/サイクル（c30-38 は 4+9/9）。
  M4 MDE: c40-48 の R 単位 MDE 中央値 ≤0.06R（c30-38 0.050R）。構造単位（bp）は印字のみ。
  M5 前向きセル: backlog の [ ] 前向き行 ≥20（c39 時点 20）・判定済み 0（金 M5 延長は 2026-06 のまま）。
  M6（新・本メタの核）反証レーンの判定語を**対象サイクル別**に採掘: 「- 判定:」行の最初の verdict 語（broken/survived/inconclusive/void）。
     予測: c40-48 を対象にした反証（≥8 本）のうち broken ≥50%。c39 以前（c1-39 対象）の broken 率と比べる。
     さらに破壊の種類を 判定行のキーワードで分類（推定器/統制 = 機械項|λ|EIV|統制|媒介|過剰統制|偽腕|look|plac|プラセボ・
     多重検定 = Holm|Bonferroni|BH|family|多重・検出力 = MDE|検出力|決着不能・時代 = 最新|㊶|在だけ|外だけ|レジーム）。
     予測（盲点の仮説 H_BLIND）: c40-48 の broken の過半は「統制の欠落（推定器）」型であり、多重検定型・検出力型ではない。
     → 当たれば研究レーンの事前固定テンプレに「帰無集合＝推定器の検定（方法論 54/57/60/63）」を必須項目として入れる提案。
  M7 cells.csv（c40 から運用）: 行数・verdict 分布・gate 不通過数・forward=yes 数・R 単位セルの |Δ_在| と MDE_在 の中央値。
  入出力: 読むのは findings/*.md・backlog.md・data/cells.csv のみ。書くのは data/c49_meta_audit3_result.md・data/c49_meta_audit3_tokens.json。
  scan 無し・MT5 無し・外部通信無し・発注無し。
  事前の最重大反証: (i) 本文 t は選択された数字（c39 と同じ）＝「報告の再現率」で独立仮説の再現率ではない。(ii) 判定語の採掘は
    「- 判定:」行の書式に依存し、1 本の反証が複数対象（第 2 撃）を持つと対象サイクルの対応が崩れる → 判定行を全部印字して手検査。
    (iii) 9 サイクルは少ない（率の se ≈0.17）。(iv) 研究レーンが c45 以降「反証の申し送り」を踏まえてセルを書いた＝外は純粋な外ではない。
"""
import re, glob, os, sys, io, json, csv
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, 'findings', '2026-11-*.md')))
CUT = 39  # 在 = cycle <= 39 / 外 = cycle >= 40

HDR = re.compile(r'^## \[(cycle(\d+)[^\]]*|REFUTE)\]')
LAB = re.compile(r'(在|外|近年)')
TOK = re.compile(r'([+−\-]?\d+\.\d+|[+−\-]?\d+)\s*(R|pp|bp|vol pt|%)?[^()（）]{0,25}?[（(・\s](?:NW\s*|Welch\s*)?t\s*([+−\-]?\d+\.\d+)')
LINE_UNIT = re.compile(r'\d\s?(R\b|bp|pp|vol pt)')
EXCL = re.compile(r'陽性|注入|x0|mfe_bar0|look-ahead|負の対照|対照')
MDE = re.compile(r'MDE\s*[≈±]?\s*(\d+\.?\d*)(?:[〜~\-−]\d+\.?\d*)?\s*(R|pp|bp|vol pt|%)?')
TARGET = re.compile(r'対象[:：]\s*(?:cycle|c)(\d+)')
VERD = re.compile(r'(broken|survived|inconclusive|void)', re.I)
KW = {
    'estimator/control': re.compile(r'機械項|λ|EIV|統制|媒介|過剰統制|偽腕|プラセボ|look-ahead|推定器|測定誤差|第 2 の測定|同時刻', re.I),
    'multiplicity': re.compile(r'Holm|Bonferroni|BH|family|多重', re.I),
    'power': re.compile(r'MDE|検出力|決着不能|達成不能'),
    'regime/in-only': re.compile(r'最新|㊶|在だけ|外だけ|在のみ|外のみ|レジーム|時代'),
}

def num(s):
    return float(s.replace('−', '-').replace('+', ''))

sections = []  # (kind, cyc, lines, header, file)
for f in FILES:
    cur = None
    for line in open(f, encoding='utf-8'):
        m = HDR.match(line)
        if m:
            kind = 'R' if m.group(1) == 'REFUTE' else 'C'
            cyc = int(m.group(2)) if kind == 'C' else None
            cur = [kind, cyc, [line.rstrip('\n')], line.rstrip('\n'), os.path.basename(f)]
            sections.append(cur)
        elif cur is not None:
            cur[2].append(line.rstrip('\n'))

def mine(lines):
    toks_all, pairs = [], []
    for ln in lines:
        labs = [(m.start(), m.group(1)) for m in LAB.finditer(ln)]
        if not labs:
            continue
        toks = []
        for i, (pos, lab) in enumerate(labs):
            end = labs[i + 1][0] if i + 1 < len(labs) else len(ln)
            win = ln[pos + len(lab):min(end, pos + len(lab) + 90)]
            m = TOK.search(win)
            if not m:
                continue
            unit = {None: 'none', 'R': 'R', 'pp': 'pp', 'bp': 'bp', 'vol pt': 'volpt', '%': 'pct'}[m.group(2)]
            if unit == 'none':
                cnt = {}
                for mu in LINE_UNIT.finditer(ln):
                    u = {'R': 'R', 'bp': 'bp', 'pp': 'pp', 'vol pt': 'volpt'}[mu.group(1)]
                    cnt[u] = cnt.get(u, 0) + 1
                if cnt:
                    unit = max(cnt, key=cnt.get) + '?'
                elif re.search(r'Δμ|R\*|R 単位|\bR\b', ln):
                    unit = 'R?'
            excl = bool(EXCL.search(ln[max(0, pos - 40):pos + len(lab) + m.end()]))
            toks.append(dict(label=lab, eff=num(m.group(1)), unit=unit, t=num(m.group(3)), excl=excl))
        toks_all.extend(toks)
        for i, tk in enumerate(toks):
            if tk['label'] != '在':
                continue
            for tk2 in toks[i + 1:]:
                if tk2['label'] == '在':
                    break
                if tk2['label'] == '外':
                    pairs.append((tk, tk2))
                    break
    return toks_all, pairs

rows_pairs, rows_tok = [], []
gate_by_cyc, mde_by_cyc, verd_hdr = {}, {}, {}
refutes = []  # dict(file, header, target, verdict, verdict_line, kinds)
for kind, cyc, lines, header, fname in sections:
    txt = '\n'.join(lines)
    if kind == 'R':
        tm = TARGET.search(header)
        target = int(tm.group(1)) if tm else None
        vline = next((l for l in lines if re.match(r'^\s*-\s*\**判定', l)), '')
        vm = VERD.search(vline)
        verdict = vm.group(1).lower() if vm else 'n/a'
        kinds = [k for k, rx in KW.items() if rx.search(vline)]
        refutes.append(dict(file=fname, header=header[:110], target=target, verdict=verdict,
                            vline=vline[:400], kinds=kinds))
        continue
    toks, pairs = mine(lines)
    seen = set()
    for a, b in pairs:
        key = (cyc, a['unit'], round(a['t'], 2), round(b['t'], 2))
        if key in seen:
            continue
        seen.add(key)
        rows_pairs.append(dict(cyc=cyc, unit=a['unit'], t_in=a['t'], t_out=b['t'], eff_in=a['eff'], eff_out=b['eff'],
                               excl=a['excl'] or b['excl']))
    seen_t = set()
    for tk in toks:
        key = (cyc, tk['label'], tk['unit'], round(tk['t'], 2), round(tk['eff'], 4))
        if key in seen_t:
            continue
        seen_t.add(key)
        rows_tok.append(dict(cyc=cyc, **tk))
    gate_by_cyc[cyc] = (len(re.findall(r'ゲート\s*㉛\s*不通過', txt)), len(re.findall(r'走らせ(?:ない|ず)', txt)))
    mde_by_cyc[cyc] = [(float(m.group(1)), m.group(2) or 'none') for m in MDE.finditer(txt)]
    verd_hdr[cyc] = dict(PASS=len(re.findall(r'PASS', header)), null=len(re.findall(r'null', header)),
                         FAIL=len(re.findall(r'FAIL', header)), gate=len(re.findall(r'ゲート\s*㉛\s*不通過', header)))

P = [r for r in rows_pairs if not r['excl']]
T = [r for r in rows_tok if not r['excl']]
out = []
def pr(s=''):
    print(s); out.append(s)

pr('# c49 メタ監査 3 — c39 の 5 問を c40-48（外）で再計算 ＋ 反証レーンの判定語（M6）＋ cells.csv（M7）')
pr(f'files {len(FILES)}・研究レーン節 {sum(1 for s in sections if s[0]=="C")}（c≤{CUT}: {sum(1 for s in sections if s[0]=="C" and s[1]<=CUT)}・c≥{CUT+1}: {sum(1 for s in sections if s[0]=="C" and s[1]>CUT)}）・REFUTE 節 {len(refutes)}')
pr(f'トークン（重複排除）{len(rows_tok)}・除外 {sum(r["excl"] for r in rows_tok)} → 使用 {len(T)}；在→外 ペア {len(rows_pairs)}・除外 {sum(r["excl"] for r in rows_pairs)} → 使用 {len(P)}')

RU = ('R', 'R?'); SU = ('bp', 'bp?', 'pp', 'pp?', 'volpt', 'pct')
def win(rows, lo, hi):
    return [r for r in rows if lo <= r['cyc'] <= hi]
WIN = {'在 c1-39': (1, CUT), '外 c40-48': (CUT + 1, 99)}

pr('\n## M1 研究レーンの t 分布（在ラベル・単位別・除外後）')
pr('| 窓 | unit | n | mean t | sd t | frac |t|>=2 | frac |t|>=3 | max |t| |')
pr('|---|---|---|---|---|---|---|---|')
m1 = {}
for wn, (lo, hi) in WIN.items():
    for ug, uname in ((RU, 'R(+R?)'), (SU, '構造'), (('none',), 'none')):
        ts = np.array([r['t'] for r in win(T, lo, hi) if r['label'] == '在' and r['unit'] in ug])
        if len(ts) < 3:
            pr(f'| {wn} | {uname} | {len(ts)} | | | | | |'); continue
        d = dict(n=len(ts), mean=float(ts.mean()), sd=float(ts.std(ddof=1)), f2=float((np.abs(ts) >= 2).mean()),
                 f3=float((np.abs(ts) >= 3).mean()), mx=float(np.abs(ts).max()))
        m1[f'{wn}|{uname}'] = d
        pr(f"| {wn} | {uname} | {d['n']} | {d['mean']:+.2f} | {d['sd']:.2f} | {d['f2']:.3f} | {d['f3']:.3f} | {d['mx']:.1f} |")
pr('帰無の期待: sd 1.00・|t|>=2 4.6%・|t|>=3 0.27%。c39 報告（R 明示・在 c1-38）: n 13 sd 2.23 |t|>=2 46%')

pr('\n## M2 在→外 再現率（同一行ペア・除外後）')
def rep_table(rows, name):
    pr(f'### {name}: n {len(rows)}')
    pr('| |t_在| bin | n | 外 同符号 | 外 同符号∧|t_外|>=1.5 | 外 同符号∧|t_外|>=2 | 外 逆符号∧|t_外|>=1.5 | mean t_外 |')
    pr('|---|---|---|---|---|---|---|')
    r_out = {}
    for lo, hi, nm in ((0, 1, '<1'), (1, 2, '1-2'), (2, 99, '>=2'), (3, 99, '>=3')):
        sub = [r for r in rows if lo <= abs(r['t_in']) < hi]
        if not sub:
            pr(f'| {nm} | 0 | | | | | |'); continue
        same = np.array([np.sign(r['t_in']) == np.sign(r['t_out']) for r in sub])
        a15 = np.array([abs(r['t_out']) >= 1.5 for r in sub]); a2 = np.array([abs(r['t_out']) >= 2 for r in sub])
        tout = np.array([r['t_out'] * np.sign(r['t_in']) for r in sub])
        r_out[nm] = dict(n=len(sub), same=float(same.mean()), rep15=float((same & a15).mean()), rep2=float((same & a2).mean()),
                         opp15=float((~same & a15).mean()), mean_tout=float(tout.mean()))
        d = r_out[nm]
        pr(f"| {nm} | {d['n']} | {d['same']:.2f} | {d['rep15']:.2f} | {d['rep2']:.2f} | {d['opp15']:.2f} | {d['mean_tout']:+.2f} |")
    return r_out
m2 = {}
for wn, (lo, hi) in WIN.items():
    Pw = win(P, lo, hi)
    m2[f'{wn}|R'] = rep_table([r for r in Pw if r['unit'] in RU], f'{wn} R 単位（R?含む）')
    m2[f'{wn}|struct'] = rep_table([r for r in Pw if r['unit'] in SU], f'{wn} 構造単位')
    m2[f'{wn}|all'] = rep_table(Pw, f'{wn} 全ペア')
pr('帰無の期待: 同符号 0.50・同符号∧|t_外|>=1.5 0.067・同符号∧|t_外|>=2 0.023')
pr('\n### 外 c40-48 の R 単位 |t_在|>=2 ペア（検査用・誤対応は手で除く）')
for r in sorted([r for r in win(P, CUT + 1, 99) if r['unit'] in RU and abs(r['t_in']) >= 2], key=lambda r: r['cyc']):
    pr(f"- c{r['cyc']}: 在 {r['eff_in']:+.4f}{r['unit']} (t {r['t_in']:+.2f}) → 外 {r['eff_out']:+.4f} (t {r['t_out']:+.2f})")
pr('\n### 外 c40-48 の 構造単位 |t_在|>=2 ペア（検査用）')
for r in sorted([r for r in win(P, CUT + 1, 99) if r['unit'] in SU and abs(r['t_in']) >= 2], key=lambda r: r['cyc']):
    pr(f"- c{r['cyc']}: 在 {r['eff_in']:+.3f}{r['unit']} (t {r['t_in']:+.2f}) → 外 {r['eff_out']:+.3f} (t {r['t_out']:+.2f})")
pr('\n### 外 c40-48 の 校正群 |t_在|<1 で 外 |t_外|>=1.5 のペア（検査用）')
for r in sorted([r for r in win(P, CUT + 1, 99) if abs(r['t_in']) < 1 and abs(r['t_out']) >= 1.5], key=lambda r: r['cyc']):
    pr(f"- c{r['cyc']}: 在 {r['eff_in']:+.4f}{r['unit']} (t {r['t_in']:+.2f}) → 外 {r['eff_out']:+.4f} (t {r['t_out']:+.2f})")

pr('\n## M3 ゲート ㉛（前 c1-28・中 c30-38・後 c40-48）')
def cyc_stats(cs):
    nR_out = sum(1 for r in P if r['cyc'] in cs and r['unit'] in RU)
    nR_in = sum(1 for r in T if r['cyc'] in cs and r['unit'] in RU and r['label'] == '在')
    gates = sum(gate_by_cyc.get(c, (0, 0))[0] for c in cs); norun = sum(gate_by_cyc.get(c, (0, 0))[1] for c in cs)
    v = {k: sum(verd_hdr[c][k] for c in cs if c in verd_hdr) for k in ('PASS', 'null', 'FAIL', 'gate')}
    return dict(ncyc=len(cs), R_pairs=nR_out, R_in_tokens=nR_in, gate_mentions=gates, norun_mentions=norun, hdr=v)
m3 = {}
for nm, cs in (('pre c1-28', [c for c in verd_hdr if c <= 28]), ('mid c30-38', [c for c in verd_hdr if 30 <= c <= 38]),
               ('post c40-48', [c for c in verd_hdr if c >= 40])):
    d = cyc_stats(cs); m3[nm] = d
    pr(f"- {nm}: サイクル {d['ncyc']}・R 単位 在→外 ペア {d['R_pairs']}（/cycle {d['R_pairs']/max(1,d['ncyc']):.2f}）・R 単位 在トークン {d['R_in_tokens']}（/cycle {d['R_in_tokens']/max(1,d['ncyc']):.2f}）・「ゲート ㉛ 不通過」{d['gate_mentions']}・「走らせない/ず」{d['norun_mentions']}・見出し判定 {d['hdr']}")
pr('- 見出し判定 c40-48: ' + '・'.join(f"c{c}:P{verd_hdr[c]['PASS']}/n{verd_hdr[c]['null']}/F{verd_hdr[c]['FAIL']}/g{verd_hdr[c]['gate']}" for c in sorted(verd_hdr) if c >= 40))

pr('\n## M4 MDE（R 単位・pp は ×0.024R 換算・bp は印字のみ）')
m4 = {}
for nm, cs in (('pre c1-28', [c for c in mde_by_cyc if c <= 28]), ('mid c30-38', [c for c in mde_by_cyc if 30 <= c <= 38]),
               ('post c40-48', [c for c in mde_by_cyc if c >= 40])):
    R = [v for c in cs for v, u in mde_by_cyc[c] if u == 'R']
    Rn = [v for c in cs for v, u in mde_by_cyc[c] if u == 'none' and v < 1.0]
    PP = [v * 0.024 for c in cs for v, u in mde_by_cyc[c] if u == 'pp']
    BP = [v for c in cs for v, u in mde_by_cyc[c] if u == 'bp']
    m4[nm] = {k: (len(v), float(np.median(v)) if v else None) for k, v in (('R', R), ('R_none', Rn), ('PP_R', PP), ('BP', BP))}
    pr(f"- {nm}: MDE R 明示 n {len(R)} 中央値 {np.median(R) if R else None}・単位無し(<1) n {len(Rn)} 中央値 {np.median(Rn) if Rn else None}・pp→R n {len(PP)} 中央値 {round(float(np.median(PP)),4) if PP else None}・bp n {len(BP)} 中央値 {np.median(BP) if BP else None}")

pr('\n## M5 前向きセル・needs data（backlog.md）')
bl = open(os.path.join(ROOT, 'backlog.md'), encoding='utf-8').read().split('\n')
open_lines = [l for l in bl if re.match(r'^\s*- \[ \]', l)]
fwd = [l for l in open_lines if '前向き' in l]
needs = [l for l in open_lines if re.search(r'needs (data|cache)', l)]
meth = [l for l in open_lines if re.search(r'方法論', l)]
m5 = dict(open=len(open_lines), forward=len(fwd), needs=len(needs), method=len(meth),
          forward_since_2026_07=sum(1 for l in fwd if '2026-07' in l), m5_ext=sum(len(re.findall(r'延長', l)) for l in bl))
pr(f"- open [ ] 行 {m5['open']}・うち 前向き {m5['forward']}（2026-07 以降待ち {m5['forward_since_2026_07']}）・needs data/cache {m5['needs']}・方法論候補 {m5['method']}・「延長」言及 {m5['m5_ext']}（c39: open 74・前向き 20/16・needs 18）")
pr('- 判定済み前向きセル: 0（金 M5 は 2026-06 まで・DATA_MAP §1）')

pr('\n## M6 反証レーンの判定語（対象サイクル別・「- 判定:」行の最初の verdict 語）')
pr(f'REFUTE 節 {len(refutes)}・対象 cycle 取得 {sum(1 for r in refutes if r["target"] is not None)}・判定行あり {sum(1 for r in refutes if r["vline"])}')
def vtab(rs, name):
    c = {k: sum(1 for r in rs if r['verdict'] == k) for k in ('broken', 'survived', 'inconclusive', 'void', 'n/a')}
    n = len(rs); nb = c['broken']; ns = c['survived']
    pr(f"- {name}: n {n}・broken {nb}・survived {ns}・inconclusive {c['inconclusive']}・void {c['void']}・n/a {c['n/a']}・broken 率（判定ありのうち） {nb/max(1,n-c['n/a']):.2f}")
    kc = {k: 0 for k in KW}
    for r in rs:
        if r['verdict'] == 'broken':
            for k in r['kinds']:
                kc[k] += 1
    pr(f"  broken の判定行キーワード（重複可）: {kc}")
    return dict(counts=c, kinds=kc)
m6 = {}
m6['pre'] = vtab([r for r in refutes if r['target'] is not None and r['target'] <= CUT], f'対象 c1-{CUT}')
m6['post'] = vtab([r for r in refutes if r['target'] is not None and r['target'] > CUT], f'対象 c{CUT+1}-48')
m6['na'] = vtab([r for r in refutes if r['target'] is None], '対象 cycle 不明（見出しに「対象: cycleN」無し）')
pr('\n### 対象 c40-48 の反証（手検査用・判定行 先頭 300 字）')
for r in [r for r in refutes if r['target'] is not None and r['target'] > CUT]:
    pr(f"- {r['file']} → c{r['target']} [{r['verdict']}] kinds={r['kinds']}: {r['vline'][:300]}")
pr('\n### 対象 cycle 不明の反証（見出し先頭）')
for r in [r for r in refutes if r['target'] is None]:
    pr(f"- {r['file']} [{r['verdict']}]: {r['header'][:110]}")

pr('\n## M7 cells.csv（c40 から運用）')
cells = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'cells.csv'), encoding='utf-8')))
def fnum(s):
    try:
        return float(str(s).replace('−', '-').replace('+', ''))
    except Exception:
        return None
vd = {}
for c in cells:
    v = c['verdict'][:12]
    v = 'PASS' if v.startswith('PASS') else 'null' if v.startswith('null') else 'broken' if 'broken' in c['verdict'][:20] else 'gate' if 'ゲート' in c['verdict'] else '記述' if c['verdict'].startswith('記述') else 'other'
    vd[v] = vd.get(v, 0) + 1
Rcells = [c for c in cells if 'R' in c['unit'] and c['kind'].startswith('条件')]
dR = [abs(fnum(c['delta_in'])) for c in Rcells if fnum(c['delta_in']) is not None]
mR = [fnum(c['mde_in']) for c in Rcells if fnum(c['mde_in']) is not None]
fwd_yes = sum(1 for c in cells if c['forward'].strip().lower().startswith('yes'))
gate_no = sum(1 for c in cells if '不通過' in c['gate'])
m7 = dict(n=len(cells), by_cycle={k: sum(1 for c in cells if c['cycle'] == k) for k in sorted(set(c['cycle'] for c in cells))},
          verdict=vd, forward_yes=fwd_yes, gate_fail=gate_no, cond_R_cells=len(Rcells),
          cond_absdelta_in_median=float(np.median(dR)) if dR else None, cond_mde_in_median=float(np.median(mR)) if mR else None,
          kinds={k: sum(1 for c in cells if c['kind'].startswith(k)) for k in ('条件', '構造', '暦', 'path')})
pr(f"- 行 {m7['n']}・cycle 別 {m7['by_cycle']}")
pr(f"- verdict 分布 {m7['verdict']}・forward=yes {m7['forward_yes']}・ゲート不通過 {m7['gate_fail']}・kind {m7['kinds']}")
pr(f"- 条件づけ R セル {m7['cond_R_cells']}: |Δ_在| 中央値 {m7['cond_absdelta_in_median']}・MDE_在 中央値 {m7['cond_mde_in_median']}")
pr('- 登記簿の規則上の PASS セル（検査用）: ' + '；'.join(f"{c['cycle']} {c['cell'][:50]} → {c['verdict'][:40]}" for c in cells if c['verdict'].startswith('PASS')))
pr('- 経験ベイズ縮小: 登記簿 R 単位 条件づけセル <30 → 未実施（c39 提案の条件未達）')

json.dump(dict(m1=m1, m2=m2, m3=m3, m4=m4, m5=m5, m6={k: v for k, v in m6.items()}, m7=m7, refutes=refutes, pairs=P),
          open(os.path.join(ROOT, 'data', 'c49_meta_audit3_tokens.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
open(os.path.join(ROOT, 'data', 'c49_meta_audit3_result.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
