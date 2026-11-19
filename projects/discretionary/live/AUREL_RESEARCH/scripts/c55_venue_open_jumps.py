# -*- coding: utf-8 -*-
"""
[cycle55 研究レーン] 2026-11-20 — 【探索・市場構造（情報到着の塊・会場の開場）】
金スポット（XAUUSD bid・5 分）の「ジャンプ」（季節ボラで標準化した裾）は、主要会場の開場直後 15 分に
**日内ボラ季節性が説明する以上に**集中するか。問いの位置: §8 に無い行「情報到着の塊（lumpy information arrival）」。
機構（誰の行動）: 開場時には休場中に溜まった注文（アジアの現物需要・生産者ヘッジ・ETF 創設・SGE の輸入銀行）が
板に不連続に当たり、価格発見が拡散的でなく跳躍的になる（Admati–Pfleiderer 1988 の取引集中・開場の価格発見）。
なぜ解消されないか: 方向を持たない（分散のタイミング）ので裁定の対象でない。
我々への含意: (1) c45 の「予定外ジャンプ UJ」（非定時分）の何割が実は**開場という予定時刻**のジャンプか（H_SCHED の読みの精錬）
(2) SL ハザードは c21 で「ボラの顔」だが、ジャンプ（SL を飛び越える）と拡散（飛び越えない）は滑りに対して別物。
昇格候補・入口/出口規則の提案ではない。

=== 事前固定（この docstring を書いてから数字を見る・seed 20261120） ===
データ: data/macro/XAU_m5_close.npz（bid・暦格子・前値埋め）。r = Δln close（bp）・足 = 開始時刻ラベル。非 flat のみ。
  除外: ET 17:00–18:10 の足（再開人工物 ㉙）・土日（各会場の現地時計で月〜金）。
標準化（会場ごとに現地時計）: UTC 固定 = SGE 09:00 CST（=01:00 UTC・中国 DST 無し）／東京 08:45 JST（=23:45 UTC・記述のみ）；
  Europe/London = London 08:00；America/New_York = COMEX 08:20 ET・NYSE 09:30 ET。各 (年, 現地 5 分スロット) で
  σ = 1.4826·MAD（非 flat・平日・セル n≥100 else NaN）・z = r/σ。→ 帰無「裾の形はスロットで同じ」なら |z|≥c の率はスロット一様。
ジャンプ: |z| ≥ 4（主）・|z| ≥ 5（副）。足単位で数える（decluster 無し）・日単位（窓に ≥1 本）も印字。
窓 W = 開場足を含む 3 足 [open, open+15)。対照 C = [open−60, open−5] ∪ [open+15, open+70]（各 12 足）から下記の予定公表足を除く:
  ET 08:30/08:35・10:00/10:05・14:00/14:05（米 定時公表・毎週木曜 08:30 新規失業保険を含む）；London 07:00/07:05（ONS）；
  UTC 01:15/01:20（PBoC 中間値 09:15 CST）。COMEX は W = {08:20, 08:25} の 2 足（08:30 足は公表＝W からも除く）。
統計: ρ = (J_W/N_W)/(J_C/N_C)・se(ln ρ) = sqrt(1/J_W + 1/J_C)（Poisson）・片側 p（ρ>1）。
  プラセボ位置 family: 近傍 [open−60, open+70] 内で W と同じ幅の連続窓を全位置に滑らせ（除外足を含む位置は捨てる）実窓の順位。
  MDE: ρ* = exp(2.8·sqrt(1/E[J_W|ρ=1] + 1/J_C))（80% 検出力・片側 5%）。
期間: 在 2010-01〜2020-12／外 2021-01〜2026-06／近年 2024-01〜2026-06（D2: 期間別・16 年一括は無し）。
主判定 H_OPEN（会場 4 = SGE・London・COMEX・NYSE・Bonferroni 4・条件は 1 行ずつ独立印字 → 旗から合成・方法論 72/75）:
  (a) 在 ρ>1 ∧ 片側 p ≤ 0.0125  (b) 外 ρ>1 ∧ p ≤ 0.10  (c) 在 プラセボ位置 family で実窓の順位 1  → PASS = (a)∧(b)∧(c)。他は null（MDE 併記）。
  予測方向（事前）: SGE・London は現物/OTC の開場＝正、COMEX 08:20 は電子化で意味を失っている可能性＝弱い正〜0、NYSE は金に直接の会場でない＝0。
陽性対照: ET 08:30 の 2 足 {08:30, 08:35}（定時公表の時計）を同じ道具で → ρ ≫ 1 が出なければ道具が壊れている。
負の対照（偽の開場）: 05:00 UTC・11:00 London・12:00 ET（開場でない時刻）→ ρ ≈ 1。
東京 08:45 JST は記述のみ（JPX/TOCOM 日中立会の開始時刻の 2010-16 の履歴が記憶で未確認・08:50 JST 公表が W に重なる）。
c45 の精錬（記述）: c45 キャッシュの UJ 937 本のうち 4 会場の開場 W（ET 換算）に落ちる本の率 vs 平日非 flat 足の W 占有率 → 濃縮倍率。
ゲート ㉛（印字のみ・証拠ではない）: scan 本（refute_c4 json）で SGE 開場窓に建玉（UTC 01:00–01:10 = JST 10:00–10:10・本番帯 jh10）
  vs 対照（UTC 00:00–00:55 ∪ 01:15–02:10 建玉）の R* の Δμ（在 |Δμ|<0.048R なら外は参考のみ）。他会場は本番帯外＝該当なし。
事前の最重大反証候補: ①bid のみ・1 社 CFD＝開場時のスプレッド拡大・気配飛びが bid の「ジャンプ」を作る（XAU ask M1【要取得】）
  ②スロット標準化は年単位＝DST 切替週（英・米の不一致週）に現地時計で揃えても UTC 固定会場の季節ステップが 1 時間ずれる（UTC 会場は影響なし・London/NY は現地時計で無事）
  ③「開場」の定義は会場の公式時刻（記憶・SGE 09:00・London 08:00 は OTC の慣行時刻で公式開場では無い）④MAD 標準化は裾の重さを
  スロット一様と仮定していない＝ρ は「裾の相対的な重さ」であって「情報量」ではない ⑤日クラスタ（同日 2 足連続ジャンプ）→ 日単位版を併記。
scan 無し・M5 原本読込なし・MT5 なし。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd
from scipy.stats import norm

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c55_venue_open_jumps_result.md")
SEED = 20261120; rng = np.random.default_rng(SEED)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle55] 会場の開場直後 15 分のジャンプ集中（季節ボラ標準化）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c55_venue_open_jumps.py)")

# ---------- load ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); r *= 1e4; flat = (r == 0)
t_utc = pd.to_datetime(ts, unit="s", utc=True)
year = t_utc.year.to_numpy()
WDN = ['月','火','水','木','金','土','日']
wd_u = t_utc.weekday.to_numpy()
say(f"- npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {flat.mean()*100:.1f}%・曜日別(UTC) "
    + " ".join(f"{WDN[w]}{flat[wd_u==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")

# ET clock for the reopen-artifact exclusion (all venues)
t_et = t_utc.tz_convert("America/New_York")
et_slot = (t_et.hour * 12 + t_et.minute // 5).to_numpy(); et_wd = t_et.weekday.to_numpy()
def S(h, m): return h * 12 + m // 5
excl_reopen = (et_slot >= S(17, 0)) & (et_slot <= S(18, 5))   # 17:00–18:10 ET
base_ok = (~flat) & (~excl_reopen)
say(f"- ET 17:00–18:10 除外 {excl_reopen.sum()} 本・非 flat ∧ 除外後 {base_ok.sum()} 本")

CLOCKS = {}
def clock(name):
    if name in CLOCKS: return CLOCKS[name]
    if name == "UTC": tl = t_utc
    else: tl = t_utc.tz_convert(name)
    slot = (tl.hour * 12 + tl.minute // 5).to_numpy(); wd = tl.weekday.to_numpy()
    day = pd.DatetimeIndex(tl.tz_localize(None)).normalize().to_numpy()
    # slot-standardization per (year, slot) on weekday, base_ok bars
    ok = base_ok & (wd <= 4)
    df = pd.DataFrame({"y": year[ok], "s": slot[ok], "r": r[ok]})
    g = df.groupby(["y", "s"])["r"]
    med = g.transform("median"); mad = (df["r"] - med).abs().groupby([df["y"], df["s"]]).transform("median")
    n = g.transform("size")
    sig = 1.4826 * mad.to_numpy(); sig[n.to_numpy() < 100] = np.nan
    zz = np.full(len(r), np.nan); zz[ok] = df["r"].to_numpy() / sig
    ncell_small = int((g.size() < 100).sum())
    CLOCKS[name] = dict(slot=slot, wd=wd, day=day, z=zz, ok=ok & np.isfinite(zz), small=ncell_small)
    med_abs = np.nanmedian(np.abs(zz[ok])); p4 = np.nanmean(np.abs(zz[ok]) >= 4) * 100; p5 = np.nanmean(np.abs(zz[ok]) >= 5) * 100
    say(f"- 時計 {name}: 標準化セル n<100 で NaN {ncell_small} 個・|z| 中央値 {med_abs:.3f}（正規 0.674）・|z|≥4 {p4:.3f}%・|z|≥5 {p5:.3f}%（正規 0.0063／0.00006%）")
    return CLOCKS[name]

PERIODS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def excluded_slots(clockname):
    ex = set()
    if clockname == "America/New_York":
        for h, m in [(8, 30), (8, 35), (10, 0), (10, 5), (14, 0), (14, 5)]: ex.add(S(h, m))
    if clockname == "Europe/London":
        for h, m in [(7, 0), (7, 5)]: ex.add(S(h, m))
    if clockname == "UTC":
        for h, m in [(1, 15), (1, 20)]: ex.add(S(h, m))
    return ex

def analyze(name, clockname, open_slot, wlen=3, thr=4, verbose=True, extra_excl=()):
    C = clock(clockname); slot = C["slot"]; ok = C["ok"]; zz = C["z"]; day = C["day"]
    ex = excluded_slots(clockname) | set(extra_excl)
    W = [open_slot + k for k in range(wlen) if (open_slot + k) not in ex]
    Cb = [open_slot + k for k in range(-12, 0)] + [open_slot + k for k in range(3, 15)]
    Cb = [s for s in Cb if s not in ex and s not in W]
    res = {}
    for pname, y0, y1 in PERIODS:
        m = ok & (year >= y0) & (year <= y1)
        jump = np.abs(zz) >= thr
        inW = m & np.isin(slot, W); inC = m & np.isin(slot, Cb)
        JW, NW, JC, NC = int((inW & jump).sum()), int(inW.sum()), int((inC & jump).sum()), int(inC.sum())
        rW = JW / max(NW, 1); rC = JC / max(NC, 1)
        rho = rW / rC if rC > 0 else np.nan
        se = math.sqrt(1 / max(JW, 0.5) + 1 / max(JC, 0.5))
        zst = math.log(rho) / se if rho > 0 else np.nan
        p1 = 1 - norm.cdf(zst) if np.isfinite(zst) else np.nan
        EJW = rC * NW
        mde = math.exp(2.8 * math.sqrt(1 / max(EJW, 0.5) + 1 / max(JC, 0.5)))
        # day-level
        dW = pd.Series(jump[inW]).groupby(day[inW]).max(); dC_rate = 1 - (1 - rC) ** len(W)
        rho_day = dW.mean() / dC_rate if dC_rate > 0 else np.nan
        # placebo positions within [open-12, open+14]
        ranks = []
        real = rho
        cand = []
        for st in range(open_slot - 12, open_slot + 15 - wlen + 1):
            Wp = [st + k for k in range(wlen)]
            if any(s in ex for s in Wp): continue
            Cp = [st + k for k in range(-12, 0)] + [st + k for k in range(wlen, wlen + 12)]
            Cp = [s for s in Cp if s not in ex and s not in Wp]
            iW = m & np.isin(slot, Wp); iC = m & np.isin(slot, Cp)
            jw, nw, jc, nc = (iW & jump).sum(), iW.sum(), (iC & jump).sum(), iC.sum()
            rp = (jw / max(nw, 1)) / max(jc / max(nc, 1), 1e-12)
            cand.append((st, rp))
        rhos = np.array([c[1] for c in cand]); rank = int((rhos > real).sum() + 1) if cand else -1
        res[pname] = dict(JW=JW, NW=NW, JC=JC, NC=NC, rho=rho, z=zst, p=p1, mde=mde, rho_day=rho_day, nday=int(len(dW)), rank=rank, nfam=len(cand), fam_max=float(np.nanmax(rhos)) if cand else np.nan)
        if verbose:
            say(f"  - {pname}: W {len(W)} 足 J/N {JW}/{NW}（率 {rW*1e4:.2f}/万）・C {len(Cb)} 足 {JC}/{NC}（{rC*1e4:.2f}/万）→ **ρ {rho:.2f}**（ln se {se:.3f}・z {zst:+.2f}・片側 p {p1:.4f}・MDE ρ* {mde:.2f}）・日単位 ρ_day {rho_day:.2f}（日 {len(dW)}）・プラセボ位置 順位 {rank}/{len(cand)}（family max ρ {res[pname]['fam_max']:.2f}）")
    return res

say("\n## 1. 主判定 H_OPEN（|z|≥4・W = 開場 3 足・C = ±1 時間 24 足 − 公表足）")
VENUES = [("SGE 09:00 CST (01:00 UTC)", "UTC", S(1, 0), 3, ()),
          ("London 08:00 (Europe/London)", "Europe/London", S(8, 0), 3, ()),
          ("COMEX 08:20 ET (2 足・08:30 公表足除外)", "America/New_York", S(8, 20), 2, ()),
          ("NYSE 09:30 ET", "America/New_York", S(9, 30), 3, ())]
MAIN = {}
for vn, ck, osl, wl, exx in VENUES:
    say(f"- **{vn}**")
    MAIN[vn] = analyze(vn, ck, osl, wlen=wl, thr=4, extra_excl=exx)
say("\n### 判定（条件 1 行ずつ・Bonferroni 4 → 在 p≤0.0125）")
verdicts = {}
for vn in MAIN:
    a = MAIN[vn]["在 2010-20"]; b = MAIN[vn]["外 2021-26H1"]
    ca = (a["rho"] > 1) and (a["p"] <= 0.0125); cb = (b["rho"] > 1) and (b["p"] <= 0.10); cc = (a["rank"] == 1)
    v = "PASS" if (ca and cb and cc) else "null"
    verdicts[vn] = v
    say(f"- {vn}: (a) 在 ρ>1 ∧ p≤0.0125: {'成立' if ca else '不成立'}（ρ {a['rho']:.2f} p {a['p']:.4f}）／(b) 外 ρ>1 ∧ p≤0.10: {'成立' if cb else '不成立'}（ρ {b['rho']:.2f} p {b['p']:.4f}）／(c) 在 順位 1: {'成立' if cc else '不成立'}（{a['rank']}/{a['nfam']}）→ **{v}**")

say("\n## 2. 副（|z|≥5）")
SEC = {}
for vn, ck, osl, wl, exx in VENUES:
    say(f"- **{vn}**")
    SEC[vn] = analyze(vn, ck, osl, wlen=wl, thr=5, extra_excl=exx)

say("\n## 3. 陽性対照（ET 08:30 公表 2 足 {08:30,08:35}・対照は公表足を除かず近傍）")
# positive control: treat 08:30/08:35 as W; need controls without excluding them: use custom exclusion set excluding only 10:00/10:05 etc.
def analyze_pc(thr):
    C = clock("America/New_York"); slot = C["slot"]; ok = C["ok"]; zz = C["z"]
    W = [S(8, 30), S(8, 35)]; Cb = [S(8, 30) + k for k in range(-12, 0)] + [S(8, 30) + k for k in range(2, 14)]
    for pname, y0, y1 in PERIODS:
        m = ok & (year >= y0) & (year <= y1); jump = np.abs(zz) >= thr
        inW = m & np.isin(slot, W); inC = m & np.isin(slot, Cb)
        JW, NW, JC, NC = (inW & jump).sum(), inW.sum(), (inC & jump).sum(), inC.sum()
        rho = (JW / NW) / (JC / NC); se = math.sqrt(1 / max(JW, .5) + 1 / max(JC, .5))
        say(f"  - |z|≥{thr} {pname}: W {JW}/{NW}・C {JC}/{NC} → ρ {rho:.2f}（z {math.log(rho)/se:+.1f}）")
analyze_pc(4); analyze_pc(5)

say("\n## 4. 負の対照（偽の開場: 05:00 UTC・11:00 London・12:00 ET・3 足）")
NEG = {}
for vn, ck, osl in [("05:00 UTC", "UTC", S(5, 0)), ("11:00 London", "Europe/London", S(11, 0)), ("12:00 ET", "America/New_York", S(12, 0))]:
    say(f"- **{vn}**"); NEG[vn] = analyze(vn, ck, osl, wlen=3, thr=4)

say("\n## 5. 記述: 東京 08:45 JST（23:45 UTC・JPX/TOCOM 日中立会・開始時刻の履歴は記憶・08:50 JST 公表が W 内）")
TK = analyze("Tokyo", "UTC", S(23, 45), wlen=3, thr=4)
say("- 23:50 UTC（08:50 JST 公表足）を W から除いた版:")
TK2 = analyze("Tokyo-ex0850", "UTC", S(23, 45), wlen=3, thr=4, extra_excl=(S(23, 50),))

say("\n## 6. 記述: 開場 ±1 時間の 5 分プロファイル（|z|≥4 率・在／外・/万足）")
def profile(name, clockname, open_slot, thr=4):
    C = clock(clockname); slot = C["slot"]; ok = C["ok"]; zz = C["z"]
    rows = []
    for k in range(-12, 15):
        s = open_slot + k
        line = [f"{k*5:+d}"]
        for pname, y0, y1 in PERIODS[:2]:
            m = ok & (year >= y0) & (year <= y1) & (slot == s)
            line.append(f"{(np.abs(zz[m])>=thr).mean()*1e4:.1f}" if m.sum() else "-")
        rows.append(line)
    say(f"- {name}: 分(開場から) → 在／外 の |z|≥4 率（/万足）: " + " ".join(f"[{a}:{b}/{c}]" for a, b, c in rows))
for vn, ck, osl, wl, exx in VENUES: profile(vn, ck, osl)

say("\n## 7. c45 の精錬: UJ（予定外・非定時分）937 本のうち開場 W に落ちる率 vs 平日非 flat 足の W 占有率")
j45 = pd.read_csv(os.path.join(DATA, "c45_jumps_5sigma_declustered.csv"))
j45_t = pd.to_datetime(j45["ts"], unit="s", utc=True)
def in_window(tt, clockname, open_slot, wlen):
    tl = tt if clockname == "UTC" else tt.tz_convert(clockname)
    sl = (tl.hour * 12 + tl.minute // 5).to_numpy()
    return (sl >= open_slot) & (sl < open_slot + wlen)
Wmask45 = np.zeros(len(j45), bool); Wmask_all = np.zeros(len(ts), bool)
for vn, ck, osl, wl, exx in VENUES:
    wl_eff = wl if "COMEX" not in vn else 2
    Wmask45 |= in_window(pd.DatetimeIndex(j45_t), ck, osl, wl_eff)
    Cc = clock(ck); Wmask_all |= np.isin(Cc["slot"], [osl + k for k in range(wl_eff)])
occ = Wmask_all[base_ok & (wd_u <= 4)].mean()
for cls in ["UJ", "SJ", "EVDAY"]:
    mm = (j45["cls"] == cls).to_numpy()
    for pname, y0, y1 in PERIODS[:2]:
        yy = j45_t.year.to_numpy(); mp = mm & (yy >= y0) & (yy <= y1)
        k = int((Wmask45 & mp).sum()); n = int(mp.sum())
        share = k / max(n, 1); enr = share / occ
        se = math.sqrt(share * (1 - share) / max(n, 1)) if n else np.nan
        say(f"- {cls} {pname}: 開場 W に {k}/{n} = {share*100:.1f}%（足占有率 {occ*100:.2f}% → 濃縮 {enr:.1f}×・z {(share-occ)/se if se else float('nan'):+.1f}）")
# per-venue breakdown for UJ
say("- UJ の会場別（全期間）: " + " / ".join(f"{vn.split(' ')[0]} {int((in_window(pd.DatetimeIndex(j45_t), ck, osl, (wl if 'COMEX' not in vn else 2)) & (j45['cls']=='UJ').to_numpy()).sum())}" for vn, ck, osl, wl, exx in VENUES))

say("\n## 8. ゲート ㉛（印字のみ）: scan 本の SGE 開場窓建玉（UTC 01:00–01:10）vs 対照建玉（00:00–00:55 ∪ 01:15–02:10）の R*")
sc = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
sc = pd.DataFrame(sc if isinstance(sc, list) else sc.get("rows", sc))
et_col = "entry_time"
tt = pd.to_datetime(sc[et_col], utc=True, errors="coerce") if sc[et_col].dtype == object else pd.to_datetime(sc[et_col], unit="s", utc=True)
sl_u = (tt.dt.hour * 12 + tt.dt.minute // 5).to_numpy(); yy = tt.dt.year.to_numpy()
ft = 0.1 / sc["risk"].astype(float).to_numpy(); Rstar = sc["R"].astype(float).to_numpy() + np.where(sc["exit"].astype(str).isin(["SL", "TP"]), 0.0, ft)
inW = np.isin(sl_u, [S(1, 0), S(1, 5)]); inC = np.isin(sl_u, list(range(S(0, 0), S(0, 55) + 1)) + list(range(S(1, 15), S(2, 10) + 1)))
for pname, y0, y1 in PERIODS:
    m = (yy >= y0) & (yy <= y1)
    a = Rstar[m & inW]; b = Rstar[m & inC]
    if len(a) > 5 and len(b) > 5:
        d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        say(f"- {pname}: W n {len(a)} R̄* {a.mean():+.3f} vs C n {len(b)} {b.mean():+.3f} → Δμ {d:+.3f}R（t {d/se:+.2f}・MDE {2*se:.3f}）")
    else:
        say(f"- {pname}: n 不足（W {len(a)}・C {len(b)}）")
say(f"- scan json 列: {list(sc.columns)[:12]} …・n {len(sc)}")

say(f"\n- 実行時間 {time.time()-T0:.1f} s・seed {SEED}・読んだのは XAU_m5_close.npz・c45 csv・refute_c4 json のみ（多年 scan 無し・MT5 無し）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", OUT)
