# -*- coding: utf-8 -*-
"""
[cycle24 研究レーン 2026-11-09] 【探索・マクロ発表前後（収益機会の源泉マップ）】米雇用統計（NFP・毎月第 1 金曜 08:30 ET）の発表窓を
**カレンダーだけで導出**し（needs data「マクロ発表カレンダー」のうち NFP は外部データ無しで導ける）、金 XAU M5 close（Dukascopy bid）で
(H1) 発表ジャンプ後の 55 分に継続/反転があるか、(H2) 発表前 02:00→08:30 ET に「発表前ドリフト/静穏」があるか（Lucca–Moench 2015 の pre-FOMC drift の NFP 版）、
(H3) 再加速の本が発表をまたぐとき残り path e=R*−cl_k に情報があるか（cl_k マルコフ性の “外生ジャンプ” 版・cycle18 の pop 横断と同型）を在/外で検証する。
入口フィルタ提案ではない。既存キャッシュのみ（XAU/US100 M5 close npz・c8 csv・c1 json・refute_c2 npz）・scan 無し・MT5 無し・外部通信無し。

=== 事前固定（この docstring を書いてから数字を見る）===
カレンダー: NFP 候補日 = 各月の第 1 金曜（ET 暦・2010-01〜2026-06）。例外（1/1・7/4 が第 1 金曜→前後にずれる・政府閉鎖 2013-10 等）は
  **データで検出**する: J（ジャンプあり）= |r_JUMP| ≥ 同じ窓（在/外 別）の「他の金曜」の |r_JUMP| 90% 点。J 率と非 J の候補日を列挙する（事後の除外規則は大きさのみ・符号不使用）。
  第 2 金曜の J 率も印字（ずれた発表の受け皿）。他の金曜にも 08:30 発表（CPI/小売等・暦で導けない）が混ざる＝対照は「薄い」側に偏る（needs data に記録）。
価格の時計: P(T) = ts == T−300 の足の close（格子の穴は NaN・⑫ ts 一致）。ET 現地（DST 追随）。
窓（ET・日 D = 金曜）: PRE 02:00→08:30／JUMP 08:30→08:35（08:30 足 1 本）／JUMP2 08:30→08:40／POST 08:35→09:30／POST2 08:40→09:30／
  POSTL 08:35→11:00／DAY 08:30→16:00。RV_PRE = Σ r² (02:00〜08:25 足)・RV_POST = Σ r² (08:35〜09:25 足)。bp 単位。
  除外: JUMP または POST が NaN、または 08:30 足が flat かつ非 NFP（祝日）。
陽性対照 PC（カレンダー検証・これが通らなければ全部 inconclusive）: 在・外とも「NFP 候補日の |r_JUMP| 中央値 ÷ 他の金曜の中央値 ≥ 2」∧「J 率 ≥ 50%」。
H1（主・両側）: J 日で r_POST = α + β·r_JUMP（HC1）。PASS = 在 |t|≥2 ∧ 外 同符号 |t|≥1.5。符号一致率・中央値も。
  対照: (a) 他の金曜 全日の β、(b) 他の金曜で |r_JUMP| ≥ 同 90% 点の「非 NFP ジャンプ日」の β（ジャンプ一般か NFP 固有か）。
  MDE = 2·se(β)。注入: 外 J 日の r_POST に +0.10·r_JUMP を足して Δt。
H2（両側）: PRE 平均 NFP 候補日 − 他の金曜。PASS = 在 |t|≥2 ∧ 外 同符号 |t|≥1.5。RV_PRE 比（中央値）は記述（「静穏」の有無）。
H3（深化接続・両側）: 建玉が同じ ET セッション（(D−1) 18:00 以降〜D 08:20 ET）で、08:20 足（k: entry_time+300k = ts(08:20)）で生存（hold>k・k≥1）の再加速 closed 本。
  e = R*−cl_k（R*=R+ft·1{SL,TP} ①）。NFP J 日 − 他の金曜 の e 差（建玉日クラスタ）。PASS = 在 |t|≥2 ∧ 外 同符号 |t|≥1.5。MDE 併記。
  記述: 次 12 本（〜09:20）で決着する比率（ハザード・NFP > 他 が期待＝陽性対照）、側符号つき受取り SGN·r_JUMP·P/risk の平均、exit 内訳。
  整合性（⑩⑫）: path k−6→k の価格変化と npz 07:50→08:20 close 差で |差|≤0.02 USD 比率を印字（<90% で H3 inconclusive）。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括の edge 判定はしない）。US100（2012+）は H1 のみ複製・記述。
経済的大きさ: |r_JUMP| 中央値（bp）と口座スプレッド 0.16 USD の往復 bp（期間中央値価格で換算）を並べる。
多重検定: 判定は H1/H2/H3 の 3 セル（Bonferroni 併記 |t|≥2.39）。窓の変種（JUMP2/POST2/POSTL/DAY）・US100・年別は記述。
事前の最重大反証: (i) bid のみ（ジャンプ足で spread 拡大→bid が沈む・US100 c16c で −0.4 bp）→ 符号対称な β には効きにくいが PRE/DAY 平均には効き得る。
  (ii) 他の金曜にも 08:30 発表 → 対照が薄く H1 対照 (b) で分離。(iii) 1 足 5 分の「ジャンプ」は発表の一部しか捉えない（08:30:00 の初動は 08:25 足に入らない・JUMP2 で感度）。
  (iv) NFP 日の n ≈ 130（在）/ 65（外）＝β の MDE は大きい。seed 20261109。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
# CAL v1 = 第 1 金曜（事前固定の原案）／ v2 = BLS 公表規則「参照週（前月 12 日を含む日〜土）の終わりから 3 週間後の金曜・1/1 は +7 日・7/4 は前日木曜」
#   v2 は v1 の PC FAIL（J 率 48%<50%）を見た後に、制度の規則（リターンに当てはめたものではない）で暦を直した第 2 パス。findings に v1 FAIL と併記する。
CAL = sys.argv[1] if len(sys.argv) > 1 else "v1"
OUT = os.path.join(DATA, "c24_nfp_announcement_result.md" if CAL == "v1" else f"c24_nfp_announcement_{CAL}_result.md"); L = []
NY = "America/New_York"; SEED = 20261109; rng = np.random.default_rng(SEED)
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle24] NFP 発表窓（{'第 1 金曜' if CAL=='v1' else 'BLS 規則 v2'} 08:30 ET・暦導出）— 金のジャンプ後継続/反転・発表前ドリフト・横断本の残り path — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c24_nfp_announcement.py {CAL})")

def nfp_dates_v2(y0=2009, y1=2026):
    """BLS Employment Situation: 参照週 = 前月 12 日を含む 日〜土。公表 = その土曜 + 20 日（3 週後の金曜）。1/1 → +7 日、7/4 → −1 日（木）。"""
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)  # Saturday of ref week
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

WD = ['月','火','水','木','金','土','日']
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)); fl = r == 0; wd = t.weekday.to_numpy()
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%・曜日別 " + " ".join(f"{WD[w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
    return ts, cl, r, fl

def epoch_et(dates, hour, minute, day_offset=0):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def idx_of_bar(ts, T):
    """index of bar whose ts == T (bar start); -1 if none/NaN"""
    out = np.full(len(T), -1); ok = np.isfinite(T)
    key = T[ok].astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, pos, -1); return out
def price_at(ts, cl, T):
    """P(T) = close of bar with ts == T-300"""
    i = idx_of_bar(ts, T - 300); return np.where(i >= 0, cl[np.clip(i, 0, len(cl)-1)], np.nan)

def hc1_reg(y, x):
    """y = a + b x ; HC1 robust se for b"""
    m = np.isfinite(y) & np.isfinite(x); y = y[m]; x = x[m]; n = len(y)
    if n < 20: return dict(b=np.nan, se=np.nan, t=np.nan, n=n, a=np.nan, agree=np.nan)
    X = np.column_stack([np.ones(n), x]); XtXi = np.linalg.inv(X.T @ X); beta = XtXi @ X.T @ y; e = y - X @ beta
    meat = (X * e[:, None]).T @ (X * e[:, None]); V = XtXi @ meat @ XtXi * n / (n - 2)
    se = math.sqrt(V[1, 1]); agree = np.mean(np.sign(y[x != 0]) == np.sign(x[x != 0]))
    return dict(b=beta[1], se=se, t=beta[1] / se, n=n, a=beta[0], agree=agree)
def mstats(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 10: return dict(n=n, mean=np.nan, se=np.nan, t=np.nan, med=np.nan, pos=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return dict(n=n, mean=m, se=se, t=m / se, med=np.median(x), pos=(x > 0).mean())
def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 10 or len(b) < 10: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, se, d / se
def ols_cluster(y, Z, cl_):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); G = 0
    for c in np.unique(cl_):
        idx = cl_ == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G += 1
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G

# ---------- calendar ----------
fridays = pd.date_range("2010-01-01", "2026-06-30", freq="D"); fridays = fridays[fridays.weekday == 4]
if CAL == "v1":
    first_fri = np.array([d.day <= 7 for d in fridays]); second_fri = np.array([(d.day > 7) & (d.day <= 14) for d in fridays])
else:
    V2 = nfp_dates_v2(); first_fri = fridays.isin(V2); second_fri = fridays.isin(V2 + pd.Timedelta(days=7))
    v1set = np.array([d.day <= 7 for d in fridays])
    say(f"- v2 暦: NFP 日 {first_fri.sum()}（金曜のみ・木曜公表 {sum(1 for d in V2 if d.weekday()==3 and pd.Timestamp('2010-01-01')<=d<=pd.Timestamp('2026-06-30'))} 日は除外）・v1 第 1 金曜と一致 {(first_fri & v1set).sum()}・v2 のみ（第 2 金曜へずれ）{(first_fri & ~v1set).sum()}・v1 のみ（非公表日）{(~first_fri & v1set).sum()}")
    say("  - v2 のみ: " + " ".join(str(d.date()) for d, a, b in zip(fridays, first_fri, v1set) if a and not b))
    say("  - v1 のみ: " + " ".join(str(d.date()) for d, a, b in zip(fridays, first_fri, v1set) if b and not a))
YR = fridays.year.to_numpy()
say(f"- 金曜 {len(fridays)} 日（2010-01〜2026-06）・NFP 候補 {first_fri.sum()}・{'第 2 金曜' if CAL=='v1' else 'NFP+7 日'} {second_fri.sum()}")

ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def build(sym, ts, cl, r, fl, dates):
    lg = np.log; P = lambda h, m: price_at(ts, cl, epoch_et(dates, h, m))
    p0200, p0830, p0835, p0840, p0930, p1100, p1600 = P(2, 0), P(8, 30), P(8, 35), P(8, 40), P(9, 30), P(11, 0), P(16, 0)
    W = {}
    W["PRE"] = (lg(p0830) - lg(p0200)) * 1e4; W["JUMP"] = (lg(p0835) - lg(p0830)) * 1e4; W["JUMP2"] = (lg(p0840) - lg(p0830)) * 1e4
    W["POST"] = (lg(p0930) - lg(p0835)) * 1e4; W["POST2"] = (lg(p0930) - lg(p0840)) * 1e4; W["POSTL"] = (lg(p1100) - lg(p0835)) * 1e4
    W["DAY"] = (lg(p1600) - lg(p0830)) * 1e4
    # realized variance via cumsum of r^2 over bar indices
    cs = np.cumsum(r ** 2)
    i0200 = idx_of_bar(ts, epoch_et(dates, 2, 0)); i0825 = idx_of_bar(ts, epoch_et(dates, 8, 25)); i0835 = idx_of_bar(ts, epoch_et(dates, 8, 35)); i0925 = idx_of_bar(ts, epoch_et(dates, 9, 25))
    okp = (i0200 >= 0) & (i0825 >= 0); okq = (i0835 >= 0) & (i0925 >= 0)
    RVP = np.full(len(dates), np.nan); RVQ = np.full(len(dates), np.nan)
    RVP[okp] = (cs[i0825[okp]] - cs[i0200[okp] - 1]) * 1e8; RVQ[okq] = (cs[i0925[okq]] - cs[i0835[okq] - 1]) * 1e8
    i0830 = idx_of_bar(ts, epoch_et(dates, 8, 30)); flat0830 = np.where(i0830 >= 0, fl[np.clip(i0830, 0, len(fl)-1)], True)
    valid = np.isfinite(W["JUMP"]) & np.isfinite(W["POST"]) & np.isfinite(W["PRE"])
    return dict(W=W, RVP=RVP, RVQ=RVQ, flat0830=flat0830, valid=valid, lvl=p0830)

# ---------- XAU ----------
say("\n## XAU")
ts, cl, r, fl = load("XAU"); D = build("XAU", ts, cl, r, fl, fridays)
v = D["valid"] & ~(D["flat0830"] & ~first_fri)  # exclude holiday-flat non-NFP days
say(f"- 有効金曜 {v.sum()}（除外 {(~v).sum()}: NaN/祝日 flat）・NFP 候補 有効 {(v & first_fri).sum()}・他の金曜 有効 {(v & ~first_fri).sum()}")
# spread in bp
for lab, lo, hi in ERAS:
    m = v & (YR >= lo) & (YR <= hi); lvl = np.nanmedian(D["lvl"][m]); say(f"- {lab}: 08:30 価格中央値 {lvl:.0f} USD → 口座 spread 0.16 USD 往復 = {0.16/lvl*1e4:.2f} bp・1 bp = {lvl*1e-4:.2f} USD")

# PC: calendar validation + J flag
J = np.zeros(len(fridays), bool); Q90 = {}
say("\n### PC カレンダー検証（|r_JUMP| 08:30→08:35・bp）")
say("| 窓 | NFP 候補 n | 中央値 |r| NFP | 中央値 |r| 他金曜 | 比 | 他金曜 90% 点 | J 率（NFP 候補） | 第 2 金曜 J 率 | 他金曜（第 1/2 除く）J 率 |")
say("|---|---|---|---|---|---|---|---|---|")
PC_OK = {}
for lab, lo, hi in ERAS:
    m = v & (YR >= lo) & (YR <= hi); aj = np.abs(D["W"]["JUMP"])
    nf = m & first_fri; of = m & ~first_fri; q90 = np.nanquantile(aj[of], 0.9); Q90[lab] = q90
    J[nf & (aj >= q90)] = True
    ratio = np.nanmedian(aj[nf]) / np.nanmedian(aj[of]); jr = (aj[nf] >= q90).mean(); jr2 = (aj[m & second_fri] >= q90).mean(); jro = (aj[m & ~first_fri & ~second_fri] >= q90).mean()
    PC_OK[lab] = (ratio >= 2) and (jr >= 0.5)
    say(f"| {lab} | {nf.sum()} | {np.nanmedian(aj[nf]):.2f} | {np.nanmedian(aj[of]):.2f} | **{ratio:.2f}** | {q90:.2f} | **{jr*100:.0f}%** | {jr2*100:.0f}% | {jro*100:.0f}% |")
nonJ = [str(d.date()) for d, f, jj, vv in zip(fridays, first_fri, J, v) if f and vv and not jj]
say(f"- 非 J の NFP 候補日（ジャンプ無し＝発表ずれ/閉鎖/祝日の疑い・{len(nonJ)} 日）: " + " ".join(nonJ))
# second Fridays with jump (shifted releases)
sJ = [str(d.date()) for d, f, vv, a in zip(fridays, second_fri, v, np.abs(D["W"]["JUMP"])) if f and vv and a >= Q90["在 2010-20" if d.year <= 2020 else "外 2021-26H1"]]
say(f"- J 相当の第 2 金曜（{len(sJ)} 日・ずれた発表 or 他の 08:30 発表）: " + " ".join(sJ))
PC_ALL = PC_OK["在 2010-20"] and PC_OK["外 2021-26H1"]
say(f"- **PC 判定: {'PASS（暦導出の NFP 窓は実データで確認）' if PC_ALL else 'FAIL → 以下 inconclusive'}**")

# H1
RES = {}
say("\n### H1 ジャンプ後 55 分（POST 08:35→09:30）の r_JUMP への回帰 β（HC1）・符号一致率")
say("| 窓 | 群 | n | β | t | MDE(2se) | 符号一致 | mean POST bp (t) | mean JUMP bp | med |JUMP| |")
say("|---|---|---|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    m = v & (YR >= lo) & (YR <= hi); aj = np.abs(D["W"]["JUMP"])
    groups = {"NFP J 日": m & J, "他の金曜 全日": m & ~first_fri, "他の金曜 非NFPジャンプ日(|r|≥q90)": m & ~first_fri & (aj >= Q90[lab]), "NFP 候補 全日": m & first_fri}
    for g, gm in groups.items():
        rg = hc1_reg(D["W"]["POST"][gm], D["W"]["JUMP"][gm]); sp = mstats(D["W"]["POST"][gm]); sj = mstats(D["W"]["JUMP"][gm])
        RES[(lab, g)] = rg
        say(f"| {lab} | {g} | {rg['n']} | {rg['b']:+.3f} | {rg['t']:+.2f} | {2*rg['se']:.3f} | {rg['agree']*100:.0f}% | {sp['mean']:+.2f} ({sp['t']:+.1f}) | {sj['mean']:+.2f} | {np.nanmedian(np.abs(D['W']['JUMP'][gm])):.2f} |")
# variants
say("\n- 窓の変種（NFP J 日・β / t）: " + " ｜ ".join(
    f"{lab}: JUMP2→POST2 {hc1_reg(D['W']['POST2'][v&J&(YR>=lo)&(YR<=hi)], D['W']['JUMP2'][v&J&(YR>=lo)&(YR<=hi)])['b']:+.3f} (t{hc1_reg(D['W']['POST2'][v&J&(YR>=lo)&(YR<=hi)], D['W']['JUMP2'][v&J&(YR>=lo)&(YR<=hi)])['t']:+.2f})・"
    f"JUMP→POSTL {hc1_reg(D['W']['POSTL'][v&J&(YR>=lo)&(YR<=hi)], D['W']['JUMP'][v&J&(YR>=lo)&(YR<=hi)])['b']:+.3f} (t{hc1_reg(D['W']['POSTL'][v&J&(YR>=lo)&(YR<=hi)], D['W']['JUMP'][v&J&(YR>=lo)&(YR<=hi)])['t']:+.2f})・"
    f"JUMP→DAY−JUMP {hc1_reg((D['W']['DAY']-D['W']['JUMP'])[v&J&(YR>=lo)&(YR<=hi)], D['W']['JUMP'][v&J&(YR>=lo)&(YR<=hi)])['b']:+.3f} (t{hc1_reg((D['W']['DAY']-D['W']['JUMP'])[v&J&(YR>=lo)&(YR<=hi)], D['W']['JUMP'][v&J&(YR>=lo)&(YR<=hi)])['t']:+.2f})"
    for lab, lo, hi in ERAS))
# injection
m = v & J & (YR >= 2021); r0 = hc1_reg(D["W"]["POST"][m], D["W"]["JUMP"][m]); r1 = hc1_reg(D["W"]["POST"][m] + 0.10 * D["W"]["JUMP"][m], D["W"]["JUMP"][m])
say(f"- 注入（外 J 日・POST に +0.10·JUMP）: t {r0['t']:+.2f} → {r1['t']:+.2f}（Δt {r1['t']-r0['t']:+.2f}・{'検出可' if r1['t']-r0['t']>=2 else '検出不可'}）")
# magnitude: RV post vs pre, |JUMP| percentiles
say("- |r_JUMP| NFP J 日 分位（bp）: " + " ｜ ".join(f"{lab} p25/p50/p75/p90 " + "/".join(f"{np.nanquantile(np.abs(D['W']['JUMP'][v&J&(YR>=lo)&(YR<=hi)]), q):.1f}" for q in (0.25, 0.5, 0.75, 0.9)) for lab, lo, hi in ERAS))

# H2
say("\n### H2 発表前 PRE 02:00→08:30（bp）: NFP 候補日 − 他の金曜（Welch）・RV_PRE 比・RV_POST 比")
say("| 窓 | NFP mean (t, n) | 他金曜 mean (t, n) | 差 | t | MDE(2se) | RV_PRE 中央値 NFP/他 | RV_POST(08:35–09:30) 中央値 NFP/他 | DAY mean NFP (t) | DAY mean 他 (t) |")
say("|---|---|---|---|---|---|---|---|---|---|")
H2 = {}
for lab, lo, hi in ERAS:
    m = v & (YR >= lo) & (YR <= hi); a = D["W"]["PRE"][m & first_fri]; b = D["W"]["PRE"][m & ~first_fri]
    d, se, t = welch(a, b); sa = mstats(a); sb = mstats(b); H2[lab] = dict(d=d, se=se, t=t)
    rvp = np.nanmedian(D["RVP"][m & first_fri]) / np.nanmedian(D["RVP"][m & ~first_fri]); rvq = np.nanmedian(D["RVQ"][m & first_fri]) / np.nanmedian(D["RVQ"][m & ~first_fri])
    da = mstats(D["W"]["DAY"][m & first_fri]); db = mstats(D["W"]["DAY"][m & ~first_fri])
    say(f"| {lab} | {sa['mean']:+.2f} ({sa['t']:+.1f}, {sa['n']}) | {sb['mean']:+.2f} ({sb['t']:+.1f}, {sb['n']}) | {d:+.2f} | {t:+.2f} | {2*se:.2f} | {rvp:.2f} | {rvq:.2f} | {da['mean']:+.2f} ({da['t']:+.1f}) | {db['mean']:+.2f} ({db['t']:+.1f}) |")

# ---------- US100 H1 (descriptive) ----------
say("\n## US100（H1 複製・記述・2012+・08:30 ET は現物前＝配信 spread 3.4 pt 帯）")
tsU, clU, rU, flU = load("US100"); fU = fridays[fridays.year >= 2012]; DU = build("US100", tsU, clU, rU, flU, fU); YU = fU.year.to_numpy(); ffU = np.asarray(first_fri)[np.asarray(fridays.year >= 2012)]
vU = DU["valid"] & ~(DU["flat0830"] & ~ffU)
for lab, lo, hi in ERAS:
    m = vU & (YU >= lo) & (YU <= hi); aj = np.abs(DU["W"]["JUMP"]); q90 = np.nanquantile(aj[m & ~ffU], 0.9); JU = m & ffU & (aj >= q90)
    rg = hc1_reg(DU["W"]["POST"][JU], DU["W"]["JUMP"][JU]); rp = hc1_reg(DU["W"]["POST"][m & ~ffU], DU["W"]["JUMP"][m & ~ffU])
    say(f"- {lab}: NFP 候補 |r_JUMP| 中央値比 {np.nanmedian(aj[m&ffU])/np.nanmedian(aj[m&~ffU]):.2f}・J 率 {(aj[m&ffU]>=q90).mean()*100:.0f}%・J 日 β {rg['b']:+.3f} (t{rg['t']:+.2f}, n{rg['n']}, 一致 {rg['agree']*100:.0f}%)・他金曜 β {rp['b']:+.3f} (t{rp['t']:+.2f})")

# ---------- H3 trades ----------
say("\n## H3 再加速 closed 本が NFP 発表（08:30 ET）を生きてまたぐとき（アンカー 08:20 足・cl_k = 08:25 close）")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy()
Jn = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c1_et = np.sort(np.array([t["entry_time"] for t in Jn["trades"]])); assert np.array_equal(c1_et, ET)
FT = Jn["frozen"]["FEED_TOL"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64)
assert len(off) - 1 == N and np.all(np.diff(off) == HOLD + 1)
e_ny = pd.to_datetime(ET, unit="s", utc=True).tz_convert(NY); E_H = e_ny.hour.to_numpy(); E_M = e_ny.minute.to_numpy(); E_WD = e_ny.weekday.to_numpy()
say(f"- 本 {N}・FEED_TOL {FT}・npz 規約 OK")
# anchor Friday: entry Fri before 08:20 ET -> same date ; entry Thu >= 18:00 ET -> next date
e_date = e_ny.normalize()
before = (E_WD == 4) & ((E_H < 8) | ((E_H == 8) & (E_M < 20))); after = (E_WD == 3) & (E_H >= 18)
anc = e_date.where(before, e_date + pd.Timedelta(days=1)); use = before | after
anc_key = (anc.year * 10000 + anc.month * 100 + anc.day).to_numpy()
fri_key = (fridays.year * 10000 + fridays.month * 100 + fridays.day).to_numpy()
T0820 = epoch_et(fridays, 8, 20); T0750 = epoch_et(fridays, 7, 50)
P0825 = price_at(ts, cl, T0820 + 300); P0755 = price_at(ts, cl, T0750 + 300)
dfF = pd.DataFrame({"T0820": T0820, "dP": P0825 - P0755, "P": P0825, "jump": D["W"]["JUMP"], "isNFP": first_fri, "J": J, "valid": v, "yr": YR}, index=fri_key)
dd = dfF.reindex(anc_key)
TSa = dd["T0820"].to_numpy(); kk = np.full(N, -1); mm = use & np.isfinite(TSa); dt = np.where(mm, TSa - ET, np.nan)
good = mm & (dt > 0) & (np.mod(dt, 300) == 0); kk[good] = (dt[good] // 300).astype(int)
alive = good & (HOLD > kk) & (kk >= 1) & dd["valid"].to_numpy().astype(bool)
say(f"- 候補（木夜〜金 08:20 建玉）{use.sum()}・金曜 08:20 足で生存 {alive.sum()}（NFP 候補日 {(alive & dd['isNFP'].to_numpy().astype(bool)).sum()}・うち J 日 {(alive & dd['J'].to_numpy().astype(bool)).sum()}・他の金曜 {(alive & ~dd['isNFP'].to_numpy().astype(bool)).sum()}）")
i = np.flatnonzero(alive & (kk >= 6))
dpath = SGN[i] * (clR[off[i] + kk[i]] - clR[off[i] + kk[i] - 6]) * RISK[i]; dnpz = dd["dP"].to_numpy()[i]; diff = np.abs(dpath - dnpz)
fr = (diff <= 0.02).mean(); say(f"- 整合性（⑩⑫）path k−6→k vs npz 07:50→08:20 close: |差|≤0.02 USD **{fr*100:.1f}%**（n{len(i)}・ρ {np.corrcoef(dpath, dnpz)[0,1]:.4f}）")
ALIGN_OK = fr >= 0.9
isN = dd["isNFP"].to_numpy().astype(bool); isJ = dd["J"].to_numpy().astype(bool)
say("\n| 窓 | 群 | n (日) | e mean (日cl t) | cl_k mean | 12 本内決着率 | 受取り SGN·jump·P/risk mean (t) | exit SL/TP/TIME % | hold 中央値 | BUY 比 |")
say("|---|---|---|---|---|---|---|---|---|---|")
H3 = {}
for lab, lo, hi in ERAS:
    wm = alive & (YEAR >= lo) & (YEAR <= hi)
    rows = {}
    for g, gm in (("NFP J 日", wm & isJ), ("NFP 候補 全日", wm & isN), ("他の金曜", wm & ~isN)):
        ii = np.flatnonzero(gm)
        if len(ii) < 10: say(f"| {lab} | {g} | {len(ii)} | 不足 | | | | | | |"); rows[g] = None; continue
        clk = clR[off[ii] + kk[ii]]; e = RSTAR[ii] - clk; day_ = anc_key[ii]
        b, se, G = ols_cluster(e, np.ones((len(ii), 1)), day_)
        rec = SGN[ii] * dd["jump"].to_numpy()[ii] * 1e-4 * dd["P"].to_numpy()[ii] / RISK[ii]; br, ser, _ = ols_cluster(rec, np.ones((len(ii), 1)), day_)
        haz = (HOLD[ii] <= kk[ii] + 12).mean(); ex = pd.Series(EXIT[ii]).value_counts(normalize=True)
        rows[g] = dict(e=e, day=day_, mean=b[0], se=se[0])
        say(f"| {lab} | {g} | {len(ii)} ({G}) | {b[0]:+.3f} ({b[0]/se[0]:+.2f}) | {clk.mean():+.3f} | {haz*100:.0f}% | {br[0]:+.4f} ({br[0]/ser[0]:+.2f}) | {ex.get('SL',0)*100:.0f}/{ex.get('TP',0)*100:.0f}/{ex.get('TIME',0)*100:.0f} | {np.median(HOLD[ii]):.0f} | {(SGN[ii]>0).mean():.2f} |")
    a = rows.get("NFP J 日"); b_ = rows.get("他の金曜")
    if a and b_:
        y = np.r_[a["e"], b_["e"]]; xg = np.r_[np.ones(len(a["e"])), np.zeros(len(b_["e"]))]; cl_ = np.r_[a["day"], b_["day"]]
        beta, se, G = ols_cluster(y, np.column_stack([np.ones(len(y)), xg]), cl_); H3[lab] = dict(d=beta[1], se=se[1], t=beta[1] / se[1])
        say(f"- {lab}: e 差（NFP J − 他金曜）**{beta[1]:+.3f}R (日cl t{beta[1]/se[1]:+.2f}, MDE {2*se[1]:.3f}R)**")
    else: H3[lab] = dict(d=np.nan, se=np.nan, t=np.nan)

# ---------- verdicts ----------
say("\n## 判定（事前固定・3 セル・Bonferroni(3) |t|≥2.39 併記）")
if not PC_ALL:
    say("- PC FAIL → H1/H2/H3 すべて inconclusive（暦導出の NFP 窓がデータで確認できない）")
else:
    I1 = RES[("在 2010-20", "NFP J 日")]; O1 = RES[("外 2021-26H1", "NFP J 日")]
    h1 = abs(I1["t"]) >= 2 and np.sign(I1["b"]) == np.sign(O1["b"]) and abs(O1["t"]) >= 1.5
    say(f"- H1 継続/反転: 在 β {I1['b']:+.3f} (t{I1['t']:+.2f})／外 β {O1['b']:+.3f} (t{O1['t']:+.2f}) → **{'PASS' if h1 else 'null'}**（MDE 在 {2*I1['se']:.3f}／外 {2*O1['se']:.3f}）")
    I2 = H2["在 2010-20"]; O2 = H2["外 2021-26H1"]
    h2 = abs(I2["t"]) >= 2 and np.sign(I2["d"]) == np.sign(O2["d"]) and abs(O2["t"]) >= 1.5
    say(f"- H2 発表前ドリフト: 在 差 {I2['d']:+.2f} bp (t{I2['t']:+.2f})／外 {O2['d']:+.2f} (t{O2['t']:+.2f}) → **{'PASS' if h2 else 'null'}**（MDE 在 {2*I2['se']:.2f}／外 {2*O2['se']:.2f} bp）")
    I3 = H3["在 2010-20"]; O3 = H3["外 2021-26H1"]
    if not ALIGN_OK or not np.isfinite(I3["t"]) or not np.isfinite(O3["t"]): say(f"- H3: inconclusive（整合 {fr*100:.1f}% または n 不足）")
    else:
        h3 = abs(I3["t"]) >= 2 and np.sign(I3["d"]) == np.sign(O3["d"]) and abs(O3["t"]) >= 1.5
        say(f"- H3 横断本 e 差: 在 {I3['d']:+.3f}R (t{I3['t']:+.2f})／外 {O3['d']:+.3f}R (t{O3['t']:+.2f}) → **{'PASS' if h3 else 'null'}**（MDE 在 {2*I3['se']:.3f}／外 {2*O3['se']:.3f}R）")
say(f"\n実行 {time.time()-T0:.1f} s・seed {SEED}・入力 既存キャッシュのみ（XAU/US100 npz・c8 csv・c1 json・refute_c2 npz）・scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
