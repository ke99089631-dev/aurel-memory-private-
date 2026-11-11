# -*- coding: utf-8 -*-
"""
c39 メタ監査 2（憲章 F.6: 10 サイクルに 1 回のメタ問い・前回 c29・backlog「次メタの問い（c39 頃）」）
=====================================================================================
問い: 研究レーン自身の 38 サイクル分の findings（研究レーン節のみ・REFUTE 節は別集計）を**データ**として、
  (M1) 研究レーンが報告する t 統計量の分布は「ほぼ全部 null」と整合するか（条件づけ R 単位 vs 構造 bp/pp 単位）
  (M2) 在（in-sample）で |t|≥2 を報告したセルは 外（out-of-sample）で同符号 ∧ |t|≥1.5 をどれだけ再現したか
       （帰無なら同符号∧|t_外|≥1.5 の率 ≈ 0.5×0.134 = 6.7%）
  (M3) ゲート ㉛（c29 で導入・在 |Δμ|<0.048R なら外を走らせない）の前後比較: 走らせなかった数 vs 走らせて null だった数
  (M4) R 単位 MDE の中央値は前後で下がったか（c29 時点 0.081R・64 件）
  (M5) 前向き（新データ待ち）セルの件数と、実際に判定できた数（M5 延長が無い限り 0）

事前固定（数字を見る前・この docstring）:
  データ = findings/2026-11-04..11-11.md の「## [cycleN 研究レーン]」節の本文（REFUTE 節は除外して別集計）。
  トークン = 同一行内で (在|外|近年) ラベルの直後 ≤90 字に現れる「<効果値><単位>? (t <値>)」。
    単位: 直後 12 字に R→'R'、pp→'pp'、bp→'bp'、vol pt→'volpt'、%→'pct'、無し→'none'。
    除外: ラベル〜t の窓に 陽性|注入|x0|mfe_bar0|look-ahead|負の対照 を含む（対照は帰無の検定ではない）。
  ペア = 同一行で 在トークンの後に最初に来る 外トークン（近年は副）。同一サイクル内の重複ペア（同値）は 1 件に畳む。
  判定（前に書く・記述統計の閾値）:
    M1: R 単位の在 t（除外後）: sd ≤1.3 ∧ |t|≥2 の比率 ≤10% なら「条件づけはほぼ帰無」。構造単位は sd >2 を予測。
    M2: R 単位ペアで |t_在|≥2 → 外 同符号∧|t_外|≥1.5 の率を印字。≤50% なら「在の有意は外を半分以上外す」。
        構造単位は ≥50% を予測（再開 pop・時刻帯などの事実）。|t_在|<1 群（帰無の校正）の率を併記（期待 ≈6.7%）。
    M3: 前（c1-28）/後（c30-38）で 外 R 単位ペア数/サイクル と「ゲート ㉛ 不通過」件数を印字。後の方が小さければ「ゲートは効いた」。
    M4: R 単位 MDE 中央値 前 vs 後。後 < 前×0.8 なら「下がった」、それ以外は「下がっていない」。
    M5: backlog の「[ ] … 前向き」行数・needs data/cache 行数・M5 延長の言及数。判定済み = M5 延長が 2026-06 のままなら 0。
  入出力: 読むのは findings/*.md と backlog.md のみ。書くのは data/c39_meta_audit2_result.md。scan 無し・MT5 無し・外部通信無し。
  事前の最重大反証: t トークンは独立セルではなく（同じ効果が見出し・本文・次の枝に再掲）、正規表現のペア付けは誤対応し得る。
    同じ量の再掲は (cycle, t_在, t_外) の重複排除で畳むが、別の切り口の同一効果（θ=1.5/2.0 等）は残る → 率は「報告の再現率」
    であって「独立仮説の再現率」ではない。前後比較は n=28 vs 9 サイクルで、後半が構造系に偏った設計変更と交絡する。
"""
import re, glob, os, sys, io, json
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, 'findings', '2026-11-*.md')))

HDR = re.compile(r'^## \[(cycle(\d+)[^\]]*|REFUTE)\]')
LAB = re.compile(r'(在|外|近年)')
TOK = re.compile(r'([+−\-]?\d+\.\d+|[+−\-]?\d+)\s*(R|pp|bp|vol pt|%)?[^()（）]{0,25}?[（(・\s](?:NW\s*|Welch\s*)?t\s*([+−\-]?\d+\.\d+)')
LINE_UNIT = re.compile(r'\d\s?(R\b|bp|pp|vol pt)')
EXCL = re.compile(r'陽性|注入|x0|mfe_bar0|look-ahead|負の対照|対照')
MDE = re.compile(r'MDE\s*[≈±]?\s*(\d+\.?\d*)(?:[〜~\-−]\d+\.?\d*)?\s*(R|pp|bp|vol pt|%)?')
GATE = re.compile(r'ゲート\s*㉛\s*(不通過|=|：|:)|走らせ(ない|ず)')

def num(s):
    return float(s.replace('−', '-').replace('+', ''))

sections = []  # (kind, cyc, lines)
for f in FILES:
    cur = None
    for line in open(f, encoding='utf-8'):
        m = HDR.match(line)
        if m:
            kind = 'R' if m.group(1) == 'REFUTE' else 'C'
            cyc = int(m.group(2)) if kind == 'C' else None
            cur = [kind, cyc, [line.rstrip('\n')]]
            sections.append(cur)
        elif cur is not None:
            cur[2].append(line.rstrip('\n'))

def mine(lines):
    """return list of dict(label, eff, unit, t, excl) in order per line, and pairs"""
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
                # infer from the line: the unit most often attached to numbers on this line
                cnt = {}
                for mu in LINE_UNIT.finditer(ln):
                    u = {'R': 'R', 'bp': 'bp', 'pp': 'pp', 'vol pt': 'volpt'}[mu.group(1)]
                    cnt[u] = cnt.get(u, 0) + 1
                if cnt:
                    unit = max(cnt, key=cnt.get) + '?'
                elif re.search(r'Δμ|R\*|R 単位|\bR\b', ln):
                    unit = 'R?'
            excl = bool(EXCL.search(ln[max(0, pos - 40):pos + len(lab) + m.end()]))
            toks.append(dict(label=lab, eff=num(m.group(1)), unit=unit, t=num(m.group(3)), excl=excl, line=ln))
        toks_all.extend(toks)
        # pairs: 在 followed by first 外
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

res = {}
rows_pairs = []
rows_tok = []
gate_by_cyc, mde_by_cyc, verdict_by_cyc = {}, {}, {}
refute_tok, refute_verd = [], {'survived': 0, 'broken': 0, 'inconclusive': 0}
for kind, cyc, lines in sections:
    toks, pairs = mine(lines)
    if kind == 'R':
        refute_tok.extend(toks)
        txt = '\n'.join(lines)
        for k in refute_verd:
            refute_verd[k] += len(re.findall(k, txt))
        continue
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
        rows_tok.append(dict(cyc=cyc, **{k: tk[k] for k in ('label', 'unit', 't', 'eff', 'excl')}))
    txt = '\n'.join(lines)
    gate_by_cyc[cyc] = (len(re.findall(r'ゲート\s*㉛\s*不通過', txt)), len(re.findall(r'走らせ(?:ない|ず)', txt)))
    mdes = []
    for m in MDE.finditer(txt):
        v, u = float(m.group(1)), m.group(2)
        mdes.append((v, u or 'none'))
    mde_by_cyc[cyc] = mdes
    head = lines[0] if lines else ''
    # verdicts are in the header line of the section (the '## ' line was consumed; use first 3 lines + header)
verd_hdr = {}
for f in FILES:
    for line in open(f, encoding='utf-8'):
        m = HDR.match(line)
        if m and m.group(1) != 'REFUTE':
            cyc = int(m.group(2))
            verd_hdr[cyc] = dict(PASS=len(re.findall(r'PASS', line)), null=len(re.findall(r'null', line)),
                                 FAIL=len(re.findall(r'FAIL', line)), gate=len(re.findall(r'ゲート\s*㉛\s*不通過', line)))

P = [r for r in rows_pairs if not r['excl']]
T = [r for r in rows_tok if not r['excl']]
out = []
def pr(s=''):
    print(s); out.append(s)

pr('# c39 メタ監査 2 — 研究レーンの t の分布・在→外 再現率・ゲート ㉛ 前後・MDE・前向きセル')
pr(f'files {len(FILES)}・研究レーン節 {sum(1 for s in sections if s[0]=="C")}・REFUTE 節 {sum(1 for s in sections if s[0]=="R")}')
pr(f'トークン（研究レーン・重複排除）{len(rows_tok)}・除外(対照/注入) {sum(r["excl"] for r in rows_tok)} → 使用 {len(T)}')
pr(f'在→外 ペア（重複排除）{len(rows_pairs)}・除外 {sum(r["excl"] for r in rows_pairs)} → 使用 {len(P)}')
pr(f'REFUTE 節トークン {len(refute_tok)}・verdict 語 {refute_verd}')

pr('\n## M1 研究レーンの t 分布（ラベル別×単位別・除外後）')
pr('| label | unit | n | mean t | sd t | frac |t|>=2 | frac |t|>=3 | max |t| |')
pr('|---|---|---|---|---|---|---|---|')
m1 = {}
for lab in ('在', '外', '近年'):
    for unit in ('R', 'R?', 'pp', 'pp?', 'bp', 'bp?', 'volpt', 'pct', 'none'):
        ts = np.array([r['t'] for r in T if r['label'] == lab and r['unit'] == unit])
        if len(ts) < 5:
            continue
        m1[(lab, unit)] = dict(n=len(ts), mean=float(ts.mean()), sd=float(ts.std(ddof=1)),
                               f2=float((np.abs(ts) >= 2).mean()), f3=float((np.abs(ts) >= 3).mean()), mx=float(np.abs(ts).max()))
        d = m1[(lab, unit)]
        pr(f"| {lab} | {unit} | {d['n']} | {d['mean']:+.2f} | {d['sd']:.2f} | {d['f2']:.3f} | {d['f3']:.3f} | {d['mx']:.1f} |")
pr('帰無の期待: sd 1.00・|t|>=2 4.6%・|t|>=3 0.27%')

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
        a15 = np.array([abs(r['t_out']) >= 1.5 for r in sub])
        a2 = np.array([abs(r['t_out']) >= 2 for r in sub])
        tout = np.array([r['t_out'] * np.sign(r['t_in']) for r in sub])
        r_out[nm] = dict(n=len(sub), same=float(same.mean()), rep15=float((same & a15).mean()), rep2=float((same & a2).mean()),
                         opp15=float((~same & a15).mean()), mean_tout=float(tout.mean()))
        d = r_out[nm]
        pr(f"| {nm} | {d['n']} | {d['same']:.2f} | {d['rep15']:.2f} | {d['rep2']:.2f} | {d['opp15']:.2f} | {d['mean_tout']:+.2f} |")
    return r_out
m2 = {}
RU = ('R', 'R?'); SU = ('bp', 'bp?', 'pp', 'pp?', 'volpt', 'pct')
m2['R'] = rep_table([r for r in P if r['unit'] in RU], 'R 単位（条件づけ・path・Δμ；R? は行から推定）')
m2['R_explicit'] = rep_table([r for r in P if r['unit'] == 'R'], 'R 単位（明示のみ）')
m2['struct'] = rep_table([r for r in P if r['unit'] in SU], '構造単位（bp/pp/vol pt/%；? は行から推定）')
m2['none'] = rep_table([r for r in P if r['unit'] == 'none'], '単位不明（none）')
m2['all'] = rep_table(P, '全ペア')
# stability split: cycles <=21 (through 11-07) vs >=22
m2['early'] = rep_table([r for r in P if r['cyc'] <= 21], '前半 c1-21（11-04〜11-07）')
m2['late'] = rep_table([r for r in P if r['cyc'] >= 22], '後半 c22-38（11-09〜11-11）')
pr('帰無の期待: 同符号 0.50・同符号∧|t_外|>=1.5 0.067・同符号∧|t_外|>=2 0.023')
# list the >=2 R pairs for inspection
pr('\n### R 単位 |t_在|>=2 のペア（検査用）')
for r in sorted([r for r in P if r['unit'] in RU and abs(r['t_in']) >= 2], key=lambda r: r['cyc']):
    pr(f"- c{r['cyc']}: 在 {r['eff_in']:+.3f}{r['unit']} (t {r['t_in']:+.2f}) → 外 {r['eff_out']:+.3f} (t {r['t_out']:+.2f})")
pr('\n### 構造単位 |t_在|>=2 のペア（検査用）')
for r in sorted([r for r in P if r['unit'] in SU and abs(r['t_in']) >= 2], key=lambda r: r['cyc']):
    pr(f"- c{r['cyc']}: 在 {r['eff_in']:+.2f}{r['unit']} (t {r['t_in']:+.2f}) → 外 {r['eff_out']:+.2f} (t {r['t_out']:+.2f})")

pr('\n## M3 ゲート ㉛ 前後（前 = c1-28・後 = c30-38）')
pre = [c for c in sorted(verd_hdr) if c <= 28]
post = [c for c in sorted(verd_hdr) if 30 <= c <= 38]
def cyc_stats(cs):
    nR_out = sum(1 for r in P if r['cyc'] in cs and r['unit'] in ('R', 'R?'))
    nR_in_only = sum(1 for r in T if r['cyc'] in cs and r['unit'] in ('R', 'R?') and r['label'] == '在')
    gates = sum(gate_by_cyc.get(c, (0, 0))[0] for c in cs)
    norun = sum(gate_by_cyc.get(c, (0, 0))[1] for c in cs)
    v = {k: sum(verd_hdr[c][k] for c in cs) for k in ('PASS', 'null', 'FAIL', 'gate')}
    return dict(ncyc=len(cs), R_pairs=nR_out, R_in_tokens=nR_in_only, gate_mentions=gates, norun_mentions=norun, hdr=v)
m3 = dict(pre=cyc_stats(pre), post=cyc_stats(post))
for k in ('pre', 'post'):
    d = m3[k]
    pr(f"- {k}: サイクル {d['ncyc']}・R 単位 在→外 ペア {d['R_pairs']}（/cycle {d['R_pairs']/d['ncyc']:.2f}）・R 単位 在トークン {d['R_in_tokens']}（/cycle {d['R_in_tokens']/d['ncyc']:.2f}）・「ゲート ㉛ 不通過」{d['gate_mentions']}・「走らせない/ず」{d['norun_mentions']}・見出し判定 {d['hdr']}")
pr('- 見出し判定（cycle 別）: ' + '・'.join(f"c{c}:P{verd_hdr[c]['PASS']}/n{verd_hdr[c]['null']}/F{verd_hdr[c]['FAIL']}/g{verd_hdr[c]['gate']}" for c in sorted(verd_hdr)))

pr('\n## M4 MDE（R 単位・pp は ×0.024R で換算して併記）')
def mde_stats(cs):
    R = [v for c in cs for v, u in mde_by_cyc.get(c, []) if u == 'R']
    Rn = [v for c in cs for v, u in mde_by_cyc.get(c, []) if u == 'none' and v < 1.0]
    PP = [v * 0.024 for c in cs for v, u in mde_by_cyc.get(c, []) if u == 'pp']
    BP = [v for c in cs for v, u in mde_by_cyc.get(c, []) if u == 'bp']
    return dict(R=R, R_none=Rn, PP_R=PP, BP=BP)
m4 = {}
for k, cs in (('pre', pre), ('post', post)):
    d = mde_stats(cs); m4[k] = {kk: (len(vv), float(np.median(vv)) if vv else None) for kk, vv in d.items()}
    pr(f"- {k}: MDE R 明示 n {m4[k]['R'][0]} 中央値 {m4[k]['R'][1]}・単位無し(<1) n {m4[k]['R_none'][0]} 中央値 {m4[k]['R_none'][1]}・pp→R n {m4[k]['PP_R'][0]} 中央値 {m4[k]['PP_R'][1]}・bp n {m4[k]['BP'][0]} 中央値 {m4[k]['BP'][1]}")
pr('- c29 時点の自己申告: R 単位 MDE 64 件 中央値 0.081R')

pr('\n## M5 前向きセル・needs data（backlog.md）')
bl = open(os.path.join(ROOT, 'backlog.md'), encoding='utf-8').read().split('\n')
open_lines = [l for l in bl if re.match(r'^\s*- \[ \]', l)]
fwd = [l for l in open_lines if '前向き' in l]
needs = [l for l in open_lines if re.search(r'needs (data|cache)', l)]
m5_ext = sum(len(re.findall(r'M5 延長|延長', l)) for l in bl)
m5 = dict(open=len(open_lines), forward=len(fwd), needs=len(needs), m5_ext_mentions=m5_ext,
          forward_since_2026_07=sum(1 for l in fwd if '2026-07' in l))
pr(f"- open [ ] 行 {m5['open']}・うち 前向き {m5['forward']}（2026-07 以降の新データ待ち {m5['forward_since_2026_07']}）・needs data/cache {m5['needs']}・「延長」言及 {m5['m5_ext_mentions']}")
pr('- 判定済み前向きセル: 0（金 M5 は 2026-06 まで＝延長未着・DATA_MAP §1）')

# dump
json.dump(dict(m1={f'{k[0]}|{k[1]}': v for k, v in m1.items()}, m2=m2, m3=m3, m4=m4, m5=m5, pairs=P, toks=T),
          open(os.path.join(ROOT, 'data', 'c39_meta_audit2_tokens.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
open(os.path.join(ROOT, 'data', 'c39_meta_audit2_result.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
