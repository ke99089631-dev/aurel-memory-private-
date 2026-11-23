# -*- coding: utf-8 -*-
"""
c64 メタ監査 4（憲章 F.6: 10 サイクルに 1 回・前回 c49 11-18・backlog「次メタ（c59 頃）」＝5 サイクル遅延で実施）
=====================================================================================
問い: c49 が c40-48 で出した「研究レーン自身の統計」と、c49 が出した 4 提案 (a)〜(d) の効果を、c50-63（c49 の **外**・
  14 サイクル）で同じ採掘器（c39/c49 の正規表現を変更しない）で再計算し、研究方法の盲点を 1 つ数値で特定する。
  在 = c40-48（c49 の数字の再現 = GATE）／外 = c50-63。参考列 c1-39。

GATE（数字を一切報告する前に）: 旧 regex で c40-48 の M2 全ペア n 47・校正群 |t_在|<1 → 外 同符号∧|t_外|≥1.5 = 6/17（35%）・
  M6 対象 c40-48 n 8・broken 6 を再現できなければ停止（c49 result.md の値）。

事前固定（数字を見る前・この docstring）:
  M1 t 分布: 外 c50-63 の在ラベル t の sd は c40-48（R 3.26・構造 2.10）と同程度。構造セル主流が続くと予測（R 単位 在トークン/cycle ≤2）。
  M2 再現率: 在 |t|≥2 → 外 同符号∧|t|≥1.5 は 全ペアで 40〜60%（c1-39 56%・c40-48 53%）。
  M8（㊶ 率・新）: 校正群（|t_在|<1）の「外 同符号∧|t_外|≥1.5」率。c1-39 7%・c40-48 35%。予測: c50-63 は **≤20%**（提案 (a) の
     帰無集合/推定器検査の節が効くなら帰無 6.7% に寄る）。>30% なら「在 null → 外 立つ」型の量産が構造化している。
  M6 反証 broken 率（対象 c50-63）: c1-39 51%・c40-48 75%。予測 H_A: 提案 (a) が効けば **≤60%**。≥70% なら (a) は broken 率を下げていない。
     破壊の種類（判定行キーワード）も c49 と同じ辞書で分類。H_BLIND（統制/推定器型が過半）の再検。
  M9（未反証の正・新）: cells.csv の forward=yes または verdict PASS の行のうち、同じ cycle を「対象: cycleN」に持つ REFUTE 節が
     1 本も無いもの。予測: **c40 C2 金 LAST~ON は依然 未反証**（提案 (b) 追跡簿は運用されていない）・未反証の正 ≥3 件。
  M10（方法論候補の再利用・新）: backlog/findings に現れる候補番号（方法論候補 N／方法論 N 候補／㉚ 型）を集め、
     番号 ≥50（c44 以降に生まれた候補）のうち、**生まれた後のサイクルの「- 事前固定」行**で引用されたものの割合。
     予測: **<30%**（c49 の盲点「書いた規則が次の事前固定に使われない」は続いている）。採用（冒頭「必ず入れる方法論」行）数は 17 → 不変と予測。
  M11（提案 (a) テンプレ 3 節の遵守・新）: c50-63 の研究レーン節の「- 事前固定」行に ①帰無集合/プラセボ（プラセボ|帰無|置換|双子|対照）
     ②推定器バイアス検査（第 2 の測定|λ|機械項|EIV|推定器|バイアス）③family 宣言（family|Bonferroni|Holm|BH|セル数|族）が含まれる割合。
     予測: ① ≥80%・③ ≥60%・**② ≤40%**（最も実装されにくい節）。② の有無と対象サイクルの反証 verdict の対応表を印字（n 小・記述）。
  M7 cells.csv: 行数（c49 26）・cycle 別・verdict・forward=yes・R 単位 条件づけセル ≥30 か（経験ベイズの条件）・c1-39 遡及登記の有無
     （提案 (d)・予測: **未着**）・mde 単位列の分離（予測: 未着）。
  M5 backlog: open [ ]・前向き・needs・方法論候補 行数（c49: 118／29／25／43）。判定済み前向きセル 0（M5 延長なし）。
  入出力: 読むのは findings/*.md・backlog.md・data/cells.csv のみ。書くのは data/c64_meta_audit4_result.md・c64_meta_audit4_tokens.json。
  scan 無し・MT5 無し・外部通信無し・発注無し。実行 ≈1 s。
  事前の最重大反証: (i) 本文 t は選択された数字＝「報告の再現率」（c39/c49 と同じ）。(ii) 外 c50-63 は c49 の提案を知った研究レーンが
    書いた＝純粋な外ではなく「提案の遵守率」と「効果」を同時に測っている（遵守が低ければ効果の有無は言えない）。(iii) 反証 ≈14 本・
    率の se ≈0.12〜0.13 で 75% → 60% の差は 1 se 級＝決着不能の可能性を事前に宣言（判定語は差でなく区間で書く）。(iv) 候補番号の
    採掘は書式依存（「候補 90」「方法論 ㉛」「(候補 93)」）→ 取り漏れは再利用率を**過小**に見せる＝M10 の <30% は保守側に偏る。
    (v) TARGET regex は見出しの「対象: **cycle63」（** 挟み）を取り漏らす → 旧 regex（GATE 用）と拡張 regex（報告用）の両方を印字。
"""
import re, glob, os, sys, io, json, csv
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, 'findings', '2026-11-*.md')))
CUT0, CUT1 = 39, 49   # c1-39 参考 / 在 c40-49 / 外 c50-63

# ---- c39/c49 の採掘器（変更しない） ----
HDR = re.compile(r'^## \[(cycle(\d+)[^\]]*|REFUTE)\]')
LAB = re.compile(r'(在|外|近年)')
TOK = re.compile(r'([+−\-]?\d+\.\d+|[+−\-]?\d+)\s*(R|pp|bp|vol pt|%)?[^()（）]{0,25}?[（(・\s](?:NW\s*|Welch\s*)?t\s*([+−\-]?\d+\.\d+)')
LINE_UNIT = re.compile(r'\d\s?(R\b|bp|pp|vol pt)')
EXCL = re.compile(r'陽性|注入|x0|mfe_bar0|look-ahead|負の対照|対照')
MDE = re.compile(r'MDE\s*[≈±]?\s*(\d+\.?\d*)(?:[〜~\-−]\d+\.?\d*)?\s*(R|pp|bp|vol pt|%)?')
TARGET = re.compile(r'対象[:：]\s*(?:cycle|c)(\d+)')
TARGET2 = re.compile(r'対象[:：]?\s*[\*\s]*(?:cycle|c)(\d+)')  # 拡張（** 挟み・コロン省略）
VERD = re.compile(r'(broken|survived|inconclusive|void)', re.I)
KW = {
    'estimator/control': re.compile(r'機械項|λ|EIV|統制|媒介|過剰統制|偽腕|プラセボ|look-ahead|推定器|測定誤差|第 2 の測定|同時刻', re.I),
    'multiplicity': re.compile(r'Holm|Bonferroni|BH|family|多重', re.I),
    'power': re.compile(r'MDE|検出力|決着不能|達成不能'),
    'regime/in-only': re.compile(r'最新|㊶|在だけ|外だけ|在のみ|外のみ|レジーム|時代'),
}
# ---- 新規（M10/M11） ----
CIRC = {}
for i, ch in enumerate('①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'): CIRC[ch] = i + 1
for i, ch in enumerate('㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟'): CIRC[ch] = 21 + i
for i, ch in enumerate('㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿'): CIRC[ch] = 36 + i
CAND_NUM = re.compile(r'方法論\s*(?:候補\s*)?(\d{2,3})\b|方法論\s*(?:候補\s*)?([①-⑳㉑-㉟㊱-㊿])|候補\s*(\d{2,3})\b|方法論\s*([①-⑳㉑-㉟㊱-㊿])|([①-⑳㉑-㉟㊱-㊿])(?=[^\w]|$)')
TEMPL = {
    '①帰無集合/プラセボ': re.compile(r'プラセボ|帰無|置換|双子|対照|偽事象|偽腕'),
    '②推定器バイアス検査': re.compile(r'第 ?2 の測定|λ|機械項|EIV|推定器|バイアス|陽性対照|注入'),
    '③family 宣言': re.compile(r'family|Bonferroni|Holm|BH|セル数|族|多重'),
}

def num(s):
    return float(s.replace('−', '-').replace('+', ''))

sections = []
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
gate_by_cyc, mde_by_cyc, verd_hdr, prefix_by_cyc, cand_by_cyc, body_by_cyc = {}, {}, {}, {}, {}, {}
refutes = []
for kind, cyc, lines, header, fname in sections:
    txt = '\n'.join(lines)
    if kind == 'R':
        tm = TARGET.search(header); tm2 = TARGET2.search(header)
        target = int(tm.group(1)) if tm else None
        target2 = int(tm2.group(1)) if tm2 else None
        vline = next((l for l in lines if re.match(r'^\s*-\s*\**判定', l)), '')
        vm = VERD.search(vline)
        verdict = vm.group(1).lower() if vm else 'n/a'
        kinds = [k for k, rx in KW.items() if rx.search(vline)]
        refutes.append(dict(file=fname, header=header[:120], target=target, target2=target2, verdict=verdict,
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
    # 事前固定 行（「- 事前固定」で始まる箇条書き＋その直下のサブ箇条書き）
    pre = []
    grab = False
    for l in lines[1:]:
        if re.match(r'^\s*-\s*\**事前固定', l):
            grab = True; pre.append(l); continue
        if grab:
            if re.match(r'^\s{2,}-', l):
                pre.append(l); continue
            grab = False
    prefix_by_cyc[cyc] = '\n'.join(pre)
    body_by_cyc[cyc] = txt
    def cands(s):
        out = set()
        for m in CAND_NUM.finditer(s):
            g = [x for x in m.groups() if x]
            if not g:
                continue
            v = g[0]
            out.add(CIRC[v] if v in CIRC else int(v))
        return out
    cand_by_cyc[cyc] = dict(pre=cands('\n'.join(pre)), body=cands(txt))

P = [r for r in rows_pairs if not r['excl']]
T = [r for r in rows_tok if not r['excl']]
out = []
def pr(s=''):
    print(s); out.append(s)

pr('# c64 メタ監査 4 — c49 の問いを c50-63（外）で再計算 ＋ ㊶ 率（M8）・未反証の正（M9）・方法論候補の再利用（M10）・テンプレ遵守（M11）')
pr(f'files {len(FILES)}・研究レーン節 {sum(1 for s in sections if s[0]=="C")}（c≤39: {sum(1 for s in sections if s[0]=="C" and s[1]<=CUT0)}・c40-49: {sum(1 for s in sections if s[0]=="C" and CUT0<s[1]<=CUT1)}・c≥50: {sum(1 for s in sections if s[0]=="C" and s[1]>CUT1)}）・REFUTE 節 {len(refutes)}')
pr(f'研究レーン節の cycle 一覧: {sorted(c for c in verd_hdr)}')
pr(f'トークン（重複排除）{len(rows_tok)}・除外 {sum(r["excl"] for r in rows_tok)} → 使用 {len(T)}；在→外 ペア {len(rows_pairs)}・除外 {sum(r["excl"] for r in rows_pairs)} → 使用 {len(P)}')

RU = ('R', 'R?'); SU = ('bp', 'bp?', 'pp', 'pp?', 'volpt', 'pct')
def win(rows, lo, hi):
    return [r for r in rows if lo <= r['cyc'] <= hi]
WIN = {'参考 c1-39': (1, CUT0), '在 c40-49': (CUT0 + 1, CUT1), '外 c50-63': (CUT1 + 1, 99)}

# ---- GATE: c49 の数字の再現（旧 regex・c40-48 窓） ----
pr('\n## GATE（c49 result.md の再現・旧 regex・窓 c40-48）')
P4048 = [r for r in P if 40 <= r['cyc'] <= 48]
cal = [r for r in P4048 if abs(r['t_in']) < 1]
cal_hit = sum(1 for r in cal if np.sign(r['t_in']) == np.sign(r['t_out']) and abs(r['t_out']) >= 1.5)
ref4048 = [r for r in refutes if r['target'] is not None and 40 <= r['target'] <= 48]
nb4048 = sum(1 for r in ref4048 if r['verdict'] == 'broken')
gate_ok = (len(P4048) == 47 and len(cal) == 17 and cal_hit == 6 and len(ref4048) == 8 and nb4048 == 6)
pr(f'- M2 全ペア c40-48 n {len(P4048)}（c49: 47）・校正群 n {len(cal)} hit {cal_hit}（c49: 17／6）・M6 対象 c40-48 n {len(ref4048)} broken {nb4048}（c49: 8／6）→ **GATE {"PASS" if gate_ok else "FAIL"}**')
if not gate_ok:
    pr('GATE FAIL — 以降の数字は c49 と直接比較できない（採掘器か findings の書式が変わった）。停止。')
    open(os.path.join(ROOT, 'data', 'c64_meta_audit4_result.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    sys.exit(1)

pr('\n## M1 研究レーンの t 分布（在ラベル・単位別・除外後）')
pr('| 窓 | unit | n | n/cycle | mean t | sd t | frac |t|>=2 | frac |t|>=3 | max |t| |')
pr('|---|---|---|---|---|---|---|---|---|')
m1 = {}
ncyc = {wn: sum(1 for c in verd_hdr if lo <= c <= hi) for wn, (lo, hi) in WIN.items()}
for wn, (lo, hi) in WIN.items():
    for ug, uname in ((RU, 'R(+R?)'), (SU, '構造'), (('none',), 'none')):
        ts = np.array([r['t'] for r in win(T, lo, hi) if r['label'] == '在' and r['unit'] in ug])
        if len(ts) < 3:
            pr(f'| {wn} | {uname} | {len(ts)} | | | | | | |'); continue
        d = dict(n=len(ts), per=len(ts) / max(1, ncyc[wn]), mean=float(ts.mean()), sd=float(ts.std(ddof=1)), f2=float((np.abs(ts) >= 2).mean()),
                 f3=float((np.abs(ts) >= 3).mean()), mx=float(np.abs(ts).max()))
        m1[f'{wn}|{uname}'] = d
        pr(f"| {wn} | {uname} | {d['n']} | {d['per']:.2f} | {d['mean']:+.2f} | {d['sd']:.2f} | {d['f2']:.3f} | {d['f3']:.3f} | {d['mx']:.1f} |")
pr('帰無の期待: sd 1.00・|t|>=2 4.6%・|t|>=3 0.27%。')

pr('\n## M2 在→外 再現率（同一行ペア・除外後）＋ M8 ㊶ 率（校正群）')
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
                         opp15=float((~same & a15).mean()), mean_tout=float(tout.mean()), hits=int((same & a15).sum()))
        d = r_out[nm]
        pr(f"| {nm} | {d['n']} | {d['same']:.2f} | {d['rep15']:.2f} ({d['hits']}) | {d['rep2']:.2f} | {d['opp15']:.2f} | {d['mean_tout']:+.2f} |")
    return r_out
m2 = {}
for wn, (lo, hi) in WIN.items():
    Pw = win(P, lo, hi)
    m2[f'{wn}|R'] = rep_table([r for r in Pw if r['unit'] in RU], f'{wn} R 単位（R?含む）')
    m2[f'{wn}|struct'] = rep_table([r for r in Pw if r['unit'] in SU], f'{wn} 構造単位')
    m2[f'{wn}|all'] = rep_table(Pw, f'{wn} 全ペア')
pr('帰無の期待: 同符号 0.50・同符号∧|t_外|>=1.5 0.067・同符号∧|t_外|>=2 0.023')
def se_p(p, n):
    return float(np.sqrt(max(p * (1 - p), 0.067 * 0.933) / max(n, 1)))
m8 = {}
for wn in WIN:
    d = m2[f'{wn}|all'].get('<1')
    if d:
        m8[wn] = dict(n=d['n'], rate=d['rep15'], hits=d['hits'], se=se_p(d['rep15'], d['n']), z_vs_null=(d['rep15'] - 0.067) / se_p(0.067, d['n']))
        pr(f"- M8 ㊶ 率 {wn}: {d['hits']}/{d['n']} = {d['rep15']:.2f}（se {m8[wn]['se']:.2f}・帰無 0.067 に対する z {m8[wn]['z_vs_null']:+.1f}）")
pr('\n### 外 c50-63 の 校正群 |t_在|<1 で 外 同符号∧|t_外|>=1.5 のペア（検査用・誤対応は手で除く）')
for r in sorted([r for r in win(P, CUT1 + 1, 99) if abs(r['t_in']) < 1 and abs(r['t_out']) >= 1.5 and np.sign(r['t_in']) == np.sign(r['t_out'])], key=lambda r: r['cyc']):
    pr(f"- c{r['cyc']}: 在 {r['eff_in']:+.4f}{r['unit']} (t {r['t_in']:+.2f}) → 外 {r['eff_out']:+.4f} (t {r['t_out']:+.2f})")
pr('\n### 外 c50-63 の |t_在|>=2 ペア（検査用）')
for r in sorted([r for r in win(P, CUT1 + 1, 99) if abs(r['t_in']) >= 2], key=lambda r: r['cyc']):
    pr(f"- c{r['cyc']}: 在 {r['eff_in']:+.4f}{r['unit']} (t {r['t_in']:+.2f}) → 外 {r['eff_out']:+.4f} (t {r['t_out']:+.2f})")

pr('\n## M3 ゲート ㉛・見出し判定（窓別）')
def cyc_stats(cs):
    nR_out = sum(1 for r in P if r['cyc'] in cs and r['unit'] in RU)
    nR_in = sum(1 for r in T if r['cyc'] in cs and r['unit'] in RU and r['label'] == '在')
    gates = sum(gate_by_cyc.get(c, (0, 0))[0] for c in cs); norun = sum(gate_by_cyc.get(c, (0, 0))[1] for c in cs)
    v = {k: sum(verd_hdr[c][k] for c in cs if c in verd_hdr) for k in ('PASS', 'null', 'FAIL', 'gate')}
    return dict(ncyc=len(cs), R_pairs=nR_out, R_in_tokens=nR_in, gate_mentions=gates, norun_mentions=norun, hdr=v)
m3 = {}
for wn, (lo, hi) in WIN.items():
    cs = [c for c in verd_hdr if lo <= c <= hi]
    d = cyc_stats(cs); m3[wn] = d
    pr(f"- {wn}: サイクル {d['ncyc']}・R 単位 在→外 ペア {d['R_pairs']}（/cycle {d['R_pairs']/max(1,d['ncyc']):.2f}）・R 単位 在トークン {d['R_in_tokens']}（/cycle {d['R_in_tokens']/max(1,d['ncyc']):.2f}）・「ゲート ㉛ 不通過」{d['gate_mentions']}・「走らせない/ず」{d['norun_mentions']}・見出し判定 {d['hdr']}")
pr('- 見出し判定 c50-63: ' + '・'.join(f"c{c}:P{verd_hdr[c]['PASS']}/n{verd_hdr[c]['null']}/F{verd_hdr[c]['FAIL']}/g{verd_hdr[c]['gate']}" for c in sorted(verd_hdr) if c >= 50))
pr('- 見出しに underpowered を含む c50-63: ' + ', '.join(f"c{c}" for kind, c, lines, header, fn in sections if kind == 'C' and c >= 50 and 'underpowered' in header))

pr('\n## M4 MDE（R 単位・pp は ×0.024R 換算・bp は印字のみ）')
m4 = {}
for wn, (lo, hi) in WIN.items():
    cs = [c for c in mde_by_cyc if lo <= c <= hi]
    R = [v for c in cs for v, u in mde_by_cyc[c] if u == 'R']
    Rn = [v for c in cs for v, u in mde_by_cyc[c] if u == 'none' and v < 1.0]
    PP = [v * 0.024 for c in cs for v, u in mde_by_cyc[c] if u == 'pp']
    BP = [v for c in cs for v, u in mde_by_cyc[c] if u == 'bp']
    m4[wn] = {k: (len(v), float(np.median(v)) if v else None) for k, v in (('R', R), ('R_none', Rn), ('PP_R', PP), ('BP', BP))}
    pr(f"- {wn}: MDE R 明示 n {len(R)} 中央値 {np.median(R) if R else None}・単位無し(<1) n {len(Rn)} 中央値 {round(float(np.median(Rn)),3) if Rn else None}・pp→R n {len(PP)} 中央値 {round(float(np.median(PP)),4) if PP else None}・bp n {len(BP)} 中央値 {np.median(BP) if BP else None}")

pr('\n## M5 前向きセル・needs data・方法論候補（backlog.md・本サイクルの追記前に読む）')
bl_txt = open(os.path.join(ROOT, 'backlog.md'), encoding='utf-8').read()
bl = bl_txt.split('\n')
open_lines = [l for l in bl if re.match(r'^\s*- \[ \]', l)]
fwd = [l for l in open_lines if '前向き' in l]
needs = [l for l in open_lines if re.search(r'needs (data|cache)', l)]
meth = [l for l in open_lines if re.search(r'方法論', l)]
m5 = dict(open=len(open_lines), forward=len(fwd), needs=len(needs), method=len(meth),
          forward_since_2026_07=sum(1 for l in fwd if '2026-07' in l), m5_ext=sum(len(re.findall(r'延長', l)) for l in bl),
          lines=len(bl))
pr(f"- open [ ] 行 {m5['open']}・うち 前向き {m5['forward']}（2026-07 以降待ち {m5['forward_since_2026_07']}）・needs data/cache {m5['needs']}・方法論 行 {m5['method']}・「延長」言及 {m5['m5_ext']}・backlog 行数 {m5['lines']}（c49: open 118・前向き 29/23・needs 25・方法論 43）")
pr('- 判定済み前向きセル: 0（金 M5 は 2026-06 まで・DATA_MAP §1・本サイクル時点で延長なし）')

pr('\n## M6 反証レーンの判定語（対象サイクル別）')
pr(f'REFUTE 節 {len(refutes)}・対象 cycle 取得 旧 regex {sum(1 for r in refutes if r["target"] is not None)}／拡張 {sum(1 for r in refutes if r["target2"] is not None)}・判定行あり {sum(1 for r in refutes if r["vline"])}')
def vtab(rs, name):
    c = {k: sum(1 for r in rs if r['verdict'] == k) for k in ('broken', 'survived', 'inconclusive', 'void', 'n/a')}
    n = len(rs); nb = c['broken']; nn = n - c['n/a']
    rate = nb / max(1, nn)
    pr(f"- {name}: n {n}・broken {nb}・survived {c['survived']}・inconclusive {c['inconclusive']}・void {c['void']}・n/a {c['n/a']}・broken 率 {rate:.2f}（se {np.sqrt(rate*(1-rate)/max(1,nn)):.2f}）")
    kc = {k: 0 for k in KW}
    for r in rs:
        if r['verdict'] == 'broken':
            for k in r['kinds']:
                kc[k] += 1
    pr(f"  broken の判定行キーワード（重複可）: {kc}")
    return dict(counts=c, kinds=kc, rate=rate, n_judged=nn)
m6 = {}
for key in ('target', 'target2'):
    pr(f'### {key}（{"旧 regex" if key=="target" else "拡張 regex"}）')
    m6[key] = {}
    m6[key]['c1-39'] = vtab([r for r in refutes if r[key] is not None and r[key] <= CUT0], '対象 c1-39')
    m6[key]['c40-49'] = vtab([r for r in refutes if r[key] is not None and CUT0 < r[key] <= CUT1], '対象 c40-49')
    m6[key]['c50-63'] = vtab([r for r in refutes if r[key] is not None and r[key] > CUT1], '対象 c50-63')
    m6[key]['na'] = vtab([r for r in refutes if r[key] is None], '対象 不明')
pr('\n### 対象 c50-63 の反証（拡張 regex・手検査用・判定行 先頭 260 字）')
for r in [r for r in refutes if r['target2'] is not None and r['target2'] > CUT1]:
    pr(f"- {r['file']} → c{r['target2']} [{r['verdict']}] kinds={r['kinds']}: {r['vline'][:260]}")
pr('\n### 対象 不明の反証（拡張 regex でも・見出し先頭）— c49 以降分のみ')
for r in [r for r in refutes if r['target2'] is None and r['file'] >= '2026-11-18.md']:
    pr(f"- {r['file']} [{r['verdict']}]: {r['header'][:120]}")

pr('\n## M7 cells.csv')
cells = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'cells.csv'), encoding='utf-8')))
cols = list(cells[0].keys()) if cells else []
def fnum(s):
    try:
        return float(str(s).replace('−', '-').replace('+', ''))
    except Exception:
        return None
vd = {}
for c in cells:
    v = c['verdict'][:12]
    v = 'PASS' if v.startswith('PASS') else 'null' if v.startswith('null') else 'broken' if 'broken' in c['verdict'][:20] else 'underpowered' if 'underpowered' in c['verdict'][:20] else 'gate' if 'ゲート' in c['verdict'] else '記述' if c['verdict'].startswith('記述') else 'other'
    vd[v] = vd.get(v, 0) + 1
Rcells = [c for c in cells if 'R' in c['unit'] and c['kind'].startswith('条件')]
dR = [abs(fnum(c['delta_in'])) for c in Rcells if fnum(c['delta_in']) is not None]
mR = [fnum(c['mde_in']) for c in Rcells if fnum(c['mde_in']) is not None]
fwd_yes = [c for c in cells if c['forward'].strip().lower().startswith('yes')]
gate_no = sum(1 for c in cells if '不通過' in c['gate'])
def cycnum(s):
    m = re.search(r'c(\d+)', s)
    return int(m.group(1)) if m else None
retro = [c for c in cells if (cycnum(c['cycle']) or 99) <= 39 and not c['cycle'].startswith('refute')]
kinds = {}
for c in cells:
    k = c['kind'][:3]
    kinds[k] = kinds.get(k, 0) + 1
m7 = dict(n=len(cells), cols=cols, by_cycle={k: sum(1 for c in cells if c['cycle'] == k) for k in sorted(set(c['cycle'] for c in cells))},
          verdict=vd, forward_yes=len(fwd_yes), gate_fail=gate_no, cond_R_cells=len(Rcells),
          cond_absdelta_in_median=float(np.median(dR)) if dR else None, cond_mde_in_median=float(np.median(mR)) if mR else None,
          kinds=kinds, retro_c1_39=len(retro), mde_unit_col=any('unit' in k and 'mde' in k.lower() for k in cols))
pr(f"- 行 {m7['n']}（c49: 26）・列 {cols}")
pr(f"- cycle 別 {m7['by_cycle']}")
pr(f"- verdict 分布 {m7['verdict']}・forward=yes {m7['forward_yes']}・ゲート不通過 {m7['gate_fail']}・kind（先頭 3 字） {m7['kinds']}")
pr(f"- 条件づけ R セル {m7['cond_R_cells']}（経験ベイズ条件 ≥30: {'達' if m7['cond_R_cells']>=30 else '未達'}）: |Δ_在| 中央値 {m7['cond_absdelta_in_median']}・MDE_在 中央値 {m7['cond_mde_in_median']}")
pr(f"- 提案 (d): c1-39 遡及登記 行 {m7['retro_c1_39']}（予測 0）・mde 単位列の分離 {'有' if m7['mde_unit_col'] else '無'}")

pr('\n## M9 未反証の正（cells.csv forward=yes ∨ verdict PASS × REFUTE 対象 cycle）')
ref_targets = set(r['target2'] for r in refutes if r['target2'] is not None)
pos = [c for c in cells if c['forward'].strip().lower().startswith('yes') or c['verdict'].startswith('PASS')]
unref = []
for c in pos:
    cy = cycnum(c['cycle'])
    hit = cy in ref_targets if cy else False
    if not hit:
        unref.append(c)
m9 = dict(n_pos=len(pos), n_unrefuted=len(unref), refute_targets=sorted(ref_targets),
          unrefuted=[dict(cycle=c['cycle'], cell=c['cell'][:70], t_out=c['t_out'], verdict=c['verdict'][:40]) for c in unref])
pr(f"- 正の候補行（forward=yes ∨ PASS）{len(pos)}・そのうち対象 cycle に REFUTE が 1 本も無い {len(unref)}（REFUTE 対象 cycle 集合 {sorted(ref_targets)}）")
for c in unref:
    pr(f"  - {c['cycle']} | {c['cell'][:80]} | t_out {c['t_out']} | {c['verdict'][:50]}")
pr('- 注: 「対象 cycle に REFUTE がある」は主セルが攻撃されたことを意味しない（別セルの可能性）。forward=yes の最古の未反証 = 提案 (b) の「渡すべき対象」。')

pr('\n## M10 方法論候補の再利用（番号の採掘・書式依存＝過小側）')
bl_cands = set()
for m in CAND_NUM.finditer(bl_txt):
    g = [x for x in m.groups() if x]
    if g:
        v = g[0]; bl_cands.add(CIRC[v] if v in CIRC else int(v))
bl_cands = {v for v in bl_cands if 1 <= v <= 130}
hdr_line = bl[4] if len(bl) > 4 else ''
adopted = set()
for m in CAND_NUM.finditer(hdr_line):
    g = [x for x in m.groups() if x]
    if g:
        v = g[0]; adopted.add(CIRC[v] if v in CIRC else int(v))
# 候補ごとの初出サイクル（findings 本文）と、その後の事前固定行での引用
first_cyc = {}
for c in sorted(cand_by_cyc):
    for v in cand_by_cyc[c]['body']:
        if 1 <= v <= 130 and v not in first_cyc:
            first_cyc[v] = c
reuse = {}
for v, c0 in first_cyc.items():
    later_pre = sorted(c for c in cand_by_cyc if c > c0 and v in cand_by_cyc[c]['pre'])
    later_body = sorted(c for c in cand_by_cyc if c > c0 and v in cand_by_cyc[c]['body'])
    reuse[v] = dict(first=c0, pre=later_pre, body=later_body)
def reuse_rate(vs):
    vs = [v for v in vs if v in reuse]
    if not vs:
        return (0, 0, None)
    k = sum(1 for v in vs if reuse[v]['pre'])
    return (len(vs), k, k / len(vs))
hi50 = [v for v in sorted(first_cyc) if v >= 50 and v not in adopted]
lo50 = [v for v in sorted(first_cyc) if v < 50 and v not in adopted]
r_hi = reuse_rate(hi50); r_lo = reuse_rate(lo50)
r_hi_body = sum(1 for v in hi50 if reuse[v]['body'])
pr(f"- backlog に現れる候補番号 {len(bl_cands)}（最大 {max(bl_cands) if bl_cands else None}）・冒頭「必ず入れる方法論」行の採用番号 {sorted(adopted)}（{len(adopted)} 件・c49: 2 件採用と記録）")
pr(f"- findings 本文で初出が取れた候補 {len(first_cyc)}（番号 ≥50: {len(hi50)}・<50 未採用: {len(lo50)}）")
pr(f"- **再利用率（初出より後のサイクルの『- 事前固定』行で引用）**: 番号 ≥50 {r_hi[1]}/{r_hi[0]} = {r_hi[2] if r_hi[2] is None else round(r_hi[2],2)}（本文どこかでの再言及 {r_hi_body}/{r_hi[0]}）／番号 <50 未採用 {r_lo[1]}/{r_lo[0]} = {r_lo[2] if r_lo[2] is None else round(r_lo[2],2)}")
pr('- 番号 ≥50 の候補ごと（初出 → 事前固定での再引用サイクル）:')
for v in hi50:
    pr(f"  - 候補 {v}: 初出 c{reuse[v]['first']} → 事前固定 {['c%d'%c for c in reuse[v]['pre']] or '—'}・本文 {['c%d'%c for c in reuse[v]['body']] or '—'}")
pr('- 外 c50-63 の各サイクルの事前固定行が引用した候補番号:')
for c in sorted(cand_by_cyc):
    if c >= 50:
        pr(f"  - c{c}: {sorted(cand_by_cyc[c]['pre'])}（事前固定 行 文字数 {len(prefix_by_cyc[c])}）")
m10 = dict(bl_cands=len(bl_cands), adopted=sorted(adopted), first_cyc=first_cyc, reuse={str(k): v for k, v in reuse.items()},
           rate_hi50=r_hi, rate_lo50=r_lo, hi50_body=r_hi_body)

pr('\n## M11 提案 (a) テンプレ 3 節の遵守（c50-63 の「- 事前固定」行）× 対象サイクルの反証 verdict')
m11 = {}
ref_verd_by_target = {}
for r in refutes:
    if r['target2'] is not None:
        ref_verd_by_target.setdefault(r['target2'], []).append(r['verdict'])
rows11 = []
for c in sorted(prefix_by_cyc):
    pre = prefix_by_cyc[c]
    flags = {k: bool(rx.search(pre)) for k, rx in TEMPL.items()}
    rows11.append(dict(cyc=c, has_pre=len(pre) > 0, **flags, verd=ref_verd_by_target.get(c, [])))
for wn, (lo, hi) in WIN.items():
    sub = [r for r in rows11 if lo <= r['cyc'] <= hi and r['has_pre']]
    if not sub:
        continue
    d = {k: sum(1 for r in sub if r[k]) / len(sub) for k in TEMPL}
    d['n'] = len(sub); d['n_cyc'] = sum(1 for r in rows11 if lo <= r['cyc'] <= hi)
    m11[wn] = d
    pr(f"- {wn}: 事前固定行あり {d['n']}/{d['n_cyc']} サイクル・" + '・'.join(f"{k} {d[k]:.2f}" for k in TEMPL))
pr('- c50-63 サイクル別（① ② ③ ／ 反証 verdict）:')
for r in rows11:
    if r['cyc'] >= 50:
        pr(f"  - c{r['cyc']}: {'①' if r['①帰無集合/プラセボ'] else '－'}{'②' if r['②推定器バイアス検査'] else '－'}{'③' if r['③family 宣言'] else '－'}  事前固定行 {'有' if r['has_pre'] else '無'}  反証 {r['verd'] or '—'}")
# ② の有無 × broken
with2 = [r for r in rows11 if r['cyc'] >= 50 and r['has_pre'] and r['②推定器バイアス検査'] and r['verd']]
wo2 = [r for r in rows11 if r['cyc'] >= 50 and r['has_pre'] and not r['②推定器バイアス検査'] and r['verd']]
def brk(rs):
    v = [x for r in rs for x in r['verd'] if x != 'n/a']
    return (sum(1 for x in v if x == 'broken'), len(v))
pr(f"- ② あり: 反証 broken {brk(with2)[0]}/{brk(with2)[1]}・② なし: {brk(wo2)[0]}/{brk(wo2)[1]}（記述・n 小）")
m11['with2'] = brk(with2); m11['wo2'] = brk(wo2)

json.dump(dict(m1=m1, m2=m2, m3=m3, m4=m4, m5=m5, m6=m6, m7=m7, m8=m8, m9=m9, m10=m10, m11=m11, refutes=refutes, pairs=P, rows11=rows11),
          open(os.path.join(ROOT, 'data', 'c64_meta_audit4_tokens.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0, default=str)
open(os.path.join(ROOT, 'data', 'c64_meta_audit4_result.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
