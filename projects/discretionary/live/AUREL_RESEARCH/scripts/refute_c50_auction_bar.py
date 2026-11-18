# -*- coding: utf-8 -*-
"""
[反証レーン] 対象 = cycle50 (2026-11-18 18:45) の唯一の正の持ち越し
 = 補足 b (2) / 判定 (4) の事後・記述:
   「**AM 10:30 / PM 15:00 LBMA オークションの直前 5 分の沈み（AM 10:25 足 P1 -1.34 t -7.7 /
     P3 -0.65 t -5.7 / P4 -1.07 t -7.9・PM 14:55 足 P2 -2.21 / P3 -0.90 / P4 -0.86）と
     直後 5 分の戻し（10:35 足 +0.71/+0.47/+0.32/+0.24）が 4 期間すべてで持続し、AM は金固有
     （US500 同スロット |t|<=1.5）**」
 ＋ c50 が cells.csv に登記した前向きセル
   「10:25 London 足 <0 かつ t<=-3 かつ 10:35 足 >0 (t>=1.5) かつ US500 同足 |t|<1.5」
（c50 の主セル C1 は既に null = 壊す余地なし。c50 自身の「最も重大な反証 (ii)」は
 「bid のみ・オークション前のスプレッド拡大で機械的に出る形・決着は XAU ask M1【要取得】」
 ＝ ask が無いので決着不能としてある。本反証は **ask を使わずに同じ機械的仮説を検定する**:
 同じ 5 分間を「最終ティック（close-close）」「初回ティック（open-open）」「足内（open->close）」
 の 3 通りで測り、さらに足の継ぎ目（gap = o(10:25) - c(10:20)）に分解する。）

== 事前固定（数字を見る前・この docstring がそのまま判定規則） ==
データ: XAU_m5_ohlc.npz（= close npz と close 完全一致・ts は足の**開始**時刻・probe で確認）
        US500_m5_close.npz・US100_m5_close.npz。London 現地・平日・足ラベル = 開始時刻。
日集合: c50 と同一の ok（9:50-16:45 の全足 notna かつ 14:30-15:25 の 12 足中 非 flat >= 8）。
期間: P1 <=2013-12-31 / P2 2014-01-01..2015-03-19 / P3 2015-03-20..2020-12-31 / P4 >=2021-01-01。

T0 複製: c50 の AM/PM 足平均 (bp) と t を再現（|差| <= 0.02 bp を一致とする）。再現しなければ以降は無効。

T1 【多重検定・family を正しく取る】288 London スロット x 4 期間 = 1152 の t を全部出す。
    BREAK-1 = P4 で t<=-3 のスロットが **10 個以上**あり、かつ 10:25 がその中で最も負の 3 位以内に入らない
    （= 「オークション直前」という名札は 288 の中から拾った 1 つに過ぎない）。

T2 【機構の置換: 分 mod 60 のプラセボ】10:25 と 14:55 はどちらも「:30 / :00 の直前 5 分」。
    London 07-21 時・**オークション時（10 時・15 時）を除く**全スロットを分(0,5,..,55)で束ね、
    分別の平均 bp と t を出す。
    BREAK-2 = P4 で 分=25 と 分=55 の両方が負かつ t<=-3（= 沈みは「半時間格子の直前足」一般の顔で
    オークション固有でない）。

T3 【時計の帰属】オークションは BST でも GMT でも 10:30 London。固定 UTC 時刻の駆動なら
    10:25 London は BST 日だけ当たる。10:25 足を BST 日 / GMT 日に分け、差の t を出す。
    BREAK-3 = P4 で |mean_BST - mean_GMT| の t >= 2 かつ 片方の |t| < 1.5。
    併記（診断）: 固定 UTC 格子・固定 ET 格子での 08:00-12:00 帯の最大 |t| スロット。

T4 【bid 最終ティック人工物（ask 無しで検定）】同一 5 分間（10:25-10:30 / 14:55-15:00）を
    R_cc = lnc(10:25)-lnc(10:20)（c50 の測り方・最終ティック）
    R_oo = lno(10:30)-lno(10:25)（初回ティック）
    R_co = lnc(10:25)-lno(10:25)（足内）
    で測り、R_cc = R_co + GAP（GAP = lno(10:25)-lnc(10:20) = 足の継ぎ目）に分解。
    BREAK-4 = P4 で |mean R_oo| < 0.5 * |mean R_cc| または t(R_oo) > -2
    （= 沈みは 10:30:00 の最終 bid にだけ居て次ティックには無い = 配信/気配の形）。
    併記: CLV = (c-l)/(h-l) の当該足 vs 同日 10-11 時平均、HL 中点リターン。

T5 【頑健性・OOS】中央値 / 10% トリム平均 / NW(lag5) t / 年別符号 /
    P4 の in 2021-24 -> out 2025-26H1 の分割。
    BREAK-5 = P4 out (2025-26H1) で 10:25 足の点推定が 0 以上、または |t| < 1.5 かつ MDE > |in の点推定|。

T6 【コスト 2 倍】正味（10:25->10:45・14:55->15:15）から往復 0.16 USD（期間別 bp 換算）を 1 倍・2 倍引く。
    BREAK-6 = P4 で 1 倍コスト後の正味 <= 0（= 受け取れない）。

T7 【対照の検出力】c50 の「金固有」は US500 の |t|<=1.5 に依っている。London 10:25 は 05:25 ET
    ＝米株 CFD のプレマーケットで flat 率が高い。US500/US100 の当該スロットの flat 率・sd・
    MDE(= 2*se) を印字。
    BREAK-7 = P4 で US500 の MDE > 1.07 bp（= 金の効果量）＝対照に検出力が無く「金固有」は未確立。

判定: broken = BREAK-1..4 のうち **2 つ以上**が成立（機構・測り方の破壊）。
      inconclusive = 1 つだけ、または T0 不一致。
      survived = BREAK-1..4 がどれも成立しない。
      BREAK-5/6/7 は「受取り可能性」「対照の主張」への別建ての判定として併記（主判定には混ぜない）。
D2 遵守: 期間別のみ。16 年一括の水準は edge 判定に使わない（T1/T2 の family 分布は構造テストの母数）。
読取りのみ・発注なし・MT5 なし・外部通信なし・書込は AUREL_RESEARCH/ 配下のみ。seed 20261118。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
np.random.seed(20261118)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c50_auction_bar.md"); L = []
def say(s=""):
    print(s, flush=True); L.append(s)

BP = 1e4
def S(h, m): return h * 12 + m // 5
def lab(s): return f"{s // 12:02d}:{(s % 12) * 5:02d}"

def stat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x)
    if n < 3: return (np.nan, np.nan, n, np.nan)
    se = x.std(ddof=1) / math.sqrt(n)
    return (x.mean(), x.mean() / se if se > 0 else np.nan, n, se)

def nw_t(x, lag=5):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x); e = x - x.mean()
    g0 = (e * e).sum() / n; s = g0
    for k in range(1, lag + 1):
        gk = (e[k:] * e[:-k]).sum() / n
        s += 2 * (1 - k / (lag + 1)) * gk
    if s <= 0: return np.nan
    return x.mean() / math.sqrt(s / n)

say(f"# [反証レーン] c50 オークション直前 5 分の沈み — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c50_auction_bar.py)")
say("")
say("対象 = c50 補足 b (2) / 判定 (4) の事後記述「AM 10:25 / PM 14:55 London 足の沈み → 直後の戻しが 4 期間持続・AM は金固有」＋ 前向きセル。事前固定は本 script の docstring（数字を見る前に確定）。")

# ---------- データ ----------
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64)
op = z["open"].astype(float); hi = z["high"].astype(float); lo = z["low"].astype(float); cl = z["close"].astype(float)
t_utc = pd.to_datetime(ts, unit="s", utc=True)
t_lon = t_utc.tz_convert("Europe/London")
wd = t_lon.weekday.to_numpy()
slot = t_lon.hour.to_numpy() * 12 + t_lon.minute.to_numpy() // 5
day = pd.DatetimeIndex(t_lon.tz_localize(None)).normalize()
utc_off = (t_lon.utcoffset().total_seconds() if hasattr(t_lon, "utcoffset") else None)
off_h = (t_lon.tz_localize(None) - t_utc.tz_localize(None)).total_seconds() / 3600.0  # 0 or 1
r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)); flat = (cl == np.roll(cl, 1))

mwd = wd <= 4
df = pd.DataFrame({"day": day[mwd], "slot": slot[mwd],
                   "lo_c": np.log(cl[mwd]), "lo_o": np.log(op[mwd]),
                   "hi": hi[mwd], "low": lo[mwd], "c": cl[mwd],
                   "flat": flat[mwd].astype(int), "bst": (off_h[mwd] > 0.5).astype(int)})
piv = lambda col: df.pivot_table(index="day", columns="slot", values=col, aggfunc="first").reindex(columns=range(288))
C = piv("lo_c"); O = piv("lo_o"); H = piv("hi"); LO = piv("low"); CC = piv("c"); F = piv("flat"); B = piv("bst")
d = pd.DatetimeIndex(C.index)
Cv, Ov, Hv, LOv, CCv, Fv = C.to_numpy(), O.to_numpy(), H.to_numpy(), LO.to_numpy(), CC.to_numpy(), F.to_numpy()
bst_day = np.nanmax(B.to_numpy(), axis=1) > 0.5

# c50 と同じ ok
rng = list(range(S(9, 50), S(16, 45)))
ok = np.isfinite(Cv[:, rng]).all(axis=1) & (np.nansum(1 - Fv[:, S(14, 30):S(15, 30)], axis=1) >= 8)
PER = {"P1 2010-13": (d <= "2013-12-31"), "P2 2014-15/03": (d >= "2014-01-01") & (d <= "2015-03-19"),
       "P3 2015/03-20 - 20": (d >= "2015-03-20") & (d <= "2020-12-31"), "P4 2021-26H1": (d >= "2021-01-01")}
PER = {k: (v.to_numpy() if hasattr(v, "to_numpy") else v) & ok for k, v in PER.items()}
say(f"- データ: XAU_m5_ohlc.npz（{len(ts)} 足・2010-01-01..2026-06-30・ts = 足開始・close は c50 の close npz と完全一致）・US500/US100_m5_close.npz・**多年 scan 無し・M5 読込なし・MT5 なし・外部通信なし・発注なし**。London 平日 {len(d)} 日 → c50 と同じ ok **{int(ok.sum())}** 日（" + " / ".join(f"{k} {int(v.sum())}" for k, v in PER.items()) + ")")

def bar_cc(s):  # c50 の測り方: 足 s（= s..s+5分）のリターン = c(s) - c(s-1)
    return (Cv[:, s] - Cv[:, s - 1]) * BP

say("")
say("## T0 複製（c50 の数字と一致するか・|差|<=0.02 bp を一致とする）")
say("")
say("| 足 (London) | " + " | ".join(PER.keys()) + " | c50 記載 |")
say("|---|---|---|---|---|---|")
C50 = {S(10, 25): "P1 -1.34(-7.7) / P2 +0.06 / P3 -0.65(-5.7) / P4 -1.07(-7.9)",
       S(10, 30): "P1 -1.64(-7.8) / P3 -0.30 / P4 +0.08",
       S(10, 35): "+0.71(4.0) / +0.47 / +0.32(2.9) / +0.24(1.8)",
       S(14, 55): "P1 -0.52(-1.7) / P2 -2.21(-5.3) / P3 -0.90(-4.3) / P4 -0.86(-3.5)",
       S(15, 5): "+0.76 / +1.13 / +0.28 / +0.83 (t 2.1/2.4/1.3/2.7)"}
rep = {}
for s, note in C50.items():
    x = bar_cc(s); row = [f"**{lab(s)}**"]
    for k, m in PER.items():
        mu, t, n, se = stat(x[m]); rep[(s, k)] = (mu, t, n, se); row.append(f"{mu:+.2f} ({t:+.1f})")
    say("| " + " | ".join(row) + f" | {note} |")

# ---------- T1 ----------
say("")
say("## T1 多重検定 — 288 London スロット x 4 期間 の t 全数（family を正しく取る）")
say("")
TS = {}
for k, m in PER.items():
    tt = np.full(288, np.nan); mm = np.full(288, np.nan); nn = np.zeros(288, int)
    for s in range(1, 288):
        mu, t, n, se = stat(bar_cc(s)[m]); tt[s] = t; mm[s] = mu; nn[s] = n
    TS[k] = (tt, mm, nn)
say("| 期間 | 有効スロット | t<=-3 | t<=-4 | t>=+3 | Bonferroni |t|>=3.46 (0.05/288 両側) | 10:25 の t / 最負順位 | 14:55 の t / 最負順位 |")
say("|---|---|---|---|---|---|---|---|")
for k in PER:
    tt, mm, nn = TS[k]
    v = np.isfinite(tt); nv = int(v.sum())
    neg3 = int((tt[v] <= -3).sum()); neg4 = int((tt[v] <= -4).sum()); pos3 = int((tt[v] >= 3).sum())
    bonf = int((np.abs(tt[v]) >= 3.46).sum())
    order = np.argsort(np.where(np.isfinite(tt), tt, np.inf))  # 最も負が先頭
    rk = {s: int(np.where(order == s)[0][0]) + 1 for s in (S(10, 25), S(14, 55))}
    say(f"| {k} | {nv} | **{neg3}** | {neg4} | {pos3} | {bonf} | {tt[S(10,25)]:+.1f} / **{rk[S(10,25)]} 位** | {tt[S(14,55)]:+.1f} / **{rk[S(14,55)]} 位** |")
say("")
for k in PER:
    tt, mm, nn = TS[k]
    order = np.argsort(np.where(np.isfinite(tt), tt, np.inf))[:8]
    say(f"- {k} 最も負の 8 スロット: " + " ｜ ".join(f"{lab(s)} {mm[s]:+.2f} (t {tt[s]:+.1f})" for s in order))
BREAK1 = {}
for k in PER:
    tt, _, _ = TS[k]; v = np.isfinite(tt)
    order = np.argsort(np.where(np.isfinite(tt), tt, np.inf))
    rk = int(np.where(order == S(10, 25))[0][0]) + 1
    BREAK1[k] = (int((tt[v] <= -3).sum()) >= 10) and (rk > 3)

# ---------- T2 ----------
say("")
say("## T2 分 mod 60 のプラセボ — 「:30/:00 の直前 5 分」は一般に沈むか（London 07-21 時・10 時/15 時を除く）")
say("")
HOURS = [h for h in range(7, 21) if h not in (10, 15)]
say("| 分 | " + " | ".join(PER.keys()) + " |")
say("|---|---|---|---|---|")
M2 = {}
for mi in range(0, 60, 5):
    row = [f"**:{mi:02d}**" if mi in (25, 55) else f":{mi:02d}"]
    for k, m in PER.items():
        pool = []
        for h in HOURS:
            s = S(h, mi)
            if s == 0: continue
            x = bar_cc(s)[m]; pool.append(x[np.isfinite(x)])
        x = np.concatenate(pool); mu, t, n, se = stat(x); M2[(mi, k)] = (mu, t, n, se)
        row.append(f"{mu:+.3f} ({t:+.1f})")
    say("| " + " | ".join(row) + " |")
BREAK2 = {k: (M2[(25, k)][0] < 0 and M2[(25, k)][1] <= -3 and M2[(55, k)][0] < 0 and M2[(55, k)][1] <= -3) for k in PER}
say("")
say("- 参考: 同じ束ね方で **10 時・15 時を含めた**場合の :25 / :55 ＝ " + " ｜ ".join(
    f"{k}: " + " / ".join(
        f":{mi:02d} {stat(np.concatenate([bar_cc(S(h,mi))[m][np.isfinite(bar_cc(S(h,mi))[m])] for h in range(7,21)]))[0]:+.3f}"
        for mi in (25, 55)) for k, m in PER.items()))

# ---------- T3 ----------
say("")
say("## T3 時計の帰属 — オークションは BST でも GMT でも 10:30 London")
say("")
say("| 足 | 期間 | BST 日 | GMT 日 | 差 (BST-GMT) t |")
say("|---|---|---|---|---|")
BREAK3 = {}
for s in (S(10, 25), S(14, 55)):
    for k, m in PER.items():
        x = bar_cc(s)
        a = x[m & bst_day]; b = x[m & (~bst_day)]
        ma, ta, na, sea = stat(a); mb, tb, nb, seb = stat(b)
        if np.isfinite(sea) and np.isfinite(seb):
            td = (ma - mb) / math.sqrt(sea ** 2 + seb ** 2)
        else:
            td = np.nan
        say(f"| {lab(s)} | {k} | {ma:+.2f} (t {ta:+.1f}, n {na}) | {mb:+.2f} (t {tb:+.1f}, n {nb}) | {td:+.2f} |")
        if s == S(10, 25):
            BREAK3[k] = (abs(td) >= 2) and (min(abs(ta), abs(tb)) < 1.5)
say("")
say("- 診断（固定 UTC / 固定 ET 格子での 08:00-12:00 帯・P4 の最も負のスロット）:")
for tzn, nm in (("UTC", "UTC"), ("America/New_York", "ET")):
    tz = t_utc.tz_convert(tzn) if tzn != "UTC" else t_utc
    sl2 = tz.hour.to_numpy() * 12 + tz.minute.to_numpy() // 5
    dd2 = pd.DatetimeIndex(tz.tz_localize(None)).normalize()
    f2 = pd.DataFrame({"day": dd2[mwd], "slot": sl2[mwd], "lc": np.log(cl[mwd])})
    P2 = f2.pivot_table(index="day", columns="slot", values="lc", aggfunc="first").reindex(columns=range(288))
    d2 = pd.DatetimeIndex(P2.index); v2 = P2.to_numpy(); m4 = (d2 >= "2021-01-01").to_numpy()
    lo_s, hi_s = (S(8, 0), S(12, 0)) if nm == "UTC" else (S(4, 0), S(8, 0))
    best = []
    for s in range(max(1, lo_s), hi_s):
        x = (v2[:, s] - v2[:, s - 1]) * BP
        mu, t, n, se = stat(x[m4])
        if np.isfinite(t): best.append((t, s, mu, n))
    best.sort()
    say(f"  - {nm} 格子: " + " ｜ ".join(f"{lab(s)} {mu:+.2f} (t {t:+.1f}, n {n})" for t, s, mu, n in best[:4]))
say(f"  - London 格子 P4 の 10:25: {TS['P4 2021-26H1'][1][S(10,25)]:+.2f} (t {TS['P4 2021-26H1'][0][S(10,25)]:+.1f})")

# ---------- T4 ----------
say("")
say("## T4 bid 最終ティック人工物（ask 無しで検定）— 同じ 5 分間を 3 通りに測る")
say("")
say("R_cc = lnc(s)-lnc(s-1)〔最終ティック・c50 の測り方〕 / R_oo = lno(s+1)-lno(s)〔初回ティック・同一区間〕 / R_co = lnc(s)-lno(s)〔足内〕 / GAP = lno(s)-lnc(s-1)〔足の継ぎ目〕。恒等式 R_cc = GAP + R_co。")
say("")
say("| 足 | 期間 | R_cc | R_oo | R_co（足内） | GAP（継ぎ目） | GAP 占有 |")
say("|---|---|---|---|---|---|---|")
BREAK4 = {}
MIDR = {}
for s in (S(10, 25), S(14, 55)):
    for k, m in PER.items():
        r_cc = (Cv[:, s] - Cv[:, s - 1]) * BP
        r_oo = (Ov[:, s + 1] - Ov[:, s]) * BP
        r_co = (Cv[:, s] - Ov[:, s]) * BP
        gap = (Ov[:, s] - Cv[:, s - 1]) * BP
        o = [stat(x[m]) for x in (r_cc, r_oo, r_co, gap)]
        share = o[3][0] / o[0][0] if abs(o[0][0]) > 1e-9 else np.nan
        say(f"| {lab(s)} | {k} | {o[0][0]:+.2f} (t {o[0][1]:+.1f}) | **{o[1][0]:+.2f} (t {o[1][1]:+.1f})** | {o[2][0]:+.2f} (t {o[2][1]:+.1f}) | {o[3][0]:+.2f} (t {o[3][1]:+.1f}) | {share*100:.0f}% |")
        if s == S(10, 25):
            BREAK4[k] = (abs(o[1][0]) < 0.5 * abs(o[0][0])) or (o[1][1] > -2)
        MIDR[(s, k)] = o
say("")
say("- HL 中点リターン（(h+l)/2 の対数差・同じ足番号差）と CLV = (c-l)/(h-l)（当該足 vs 同日 10-11 時 / 14-15 時の平均）:")
mid = np.log((Hv + LOv) / 2.0)
for s, ref in ((S(10, 25), (S(10, 0), S(11, 0))), (S(14, 55), (S(14, 0), S(15, 0)))):
    clv = (CCv[:, s] - LOv[:, s]) / np.where(Hv[:, s] - LOv[:, s] > 0, Hv[:, s] - LOv[:, s], np.nan)
    clv_ref = np.nanmean(((CCv - LOv) / np.where(Hv - LOv > 0, Hv - LOv, np.nan))[:, ref[0]:ref[1]], axis=1)
    out = []
    for k, m in PER.items():
        mm2, t2, n2, _ = stat((mid[:, s] - mid[:, s - 1])[m])
        a = np.nanmean(clv[m]); b = np.nanmean(clv_ref[m])
        out.append(f"{k}: HLmid {mm2:+.2f} (t {t2:+.1f}) ・CLV {a:.3f} vs 参照 {b:.3f}")
    say(f"  - {lab(s)}: " + " ｜ ".join(out))

# ---------- T5 ----------
say("")
say("## T5 頑健性・OOS（10:25 足）")
say("")
say("| 期間 | 平均 | 中央値 | 10% トリム | t (iid) | t (NW lag5) | 正味 >0 の日 % |")
say("|---|---|---|---|---|---|---|")
x25 = bar_cc(S(10, 25))
from scipy import stats as sps
for k, m in PER.items():
    x = x25[m]; x = x[np.isfinite(x)]
    mu, t, n, se = stat(x)
    say(f"| {k} (n {n}) | {mu:+.3f} | {np.median(x):+.3f} | {sps.trim_mean(x, 0.1):+.3f} | {t:+.2f} | {nw_t(x):+.2f} | {(x>0).mean()*100:.1f}% |")
yrs = d.year.to_numpy()
say("")
say("- 年別（10:25 足・bp・n>=100 の年）: " + " ".join(
    f"{y}:{x25[(yrs==y)&ok][np.isfinite(x25[(yrs==y)&ok])].mean():+.2f}" for y in range(2010, 2027)
    if ((yrs == y) & ok).sum() >= 100))
m4 = PER["P4 2021-26H1"]
inm = m4 & (d <= "2024-12-31").to_numpy(); outm = m4 & (d >= "2025-01-01").to_numpy()
mi_, ti_, ni_, sei_ = stat(x25[inm]); mo_, to_, no_, seo_ = stat(x25[outm])
say(f"- **P4 の in/out 分割**: in 2021-24 {mi_:+.3f} bp (t {ti_:+.2f}, n {ni_}) → out 2025-26H1 **{mo_:+.3f} bp (t {to_:+.2f}, n {no_}・MDE 2se {2*seo_:.3f})**")
BREAK5 = (mo_ >= 0) or (abs(to_) < 1.5 and 2 * seo_ > abs(mi_))

# ---------- T6 ----------
say("")
say("## T6 コスト 2 倍 — 正味（沈み＋戻し）から往復 0.16 USD を 1 倍 / 2 倍")
say("")
say("| 窓 | 期間 | 正味 bp (t) | 価格 | 往復 bp | net -1x | net -2x |")
say("|---|---|---|---|---|---|---|")
BREAK6 = {}
for nm, (s0, s1) in (("AM 10:25->10:45", (S(10, 25) - 1, S(10, 45))), ("PM 14:55->15:15", (S(14, 55) - 1, S(15, 15)))):
    for k, m in PER.items():
        net = (Cv[:, s1] - Cv[:, s0]) * BP
        mu, t, n, se = stat(net[m])
        px = np.nanmean(CCv[m, S(10, 25)])
        rt = 0.16 / px * BP
        say(f"| {nm} | {k} | {mu:+.2f} ({t:+.1f}) | {px:.0f} | {rt:.2f} | {-mu-rt:+.2f} | {-mu-2*rt:+.2f} |")
        if nm.startswith("AM"):
            BREAK6[k] = (-mu - rt) <= 0

# ---------- T7 ----------
say("")
say("## T7 対照の検出力 — 「金固有」は US500 の |t|<=1.5 に依る。その対照に検出力はあるか")
say("")
say("| 銘柄 | 期間 | London 10:25 足 bp (t) | n | flat 率 | sd bp | **MDE 2se** | 金の効果量 |")
say("|---|---|---|---|---|---|---|---|")
BREAK7 = {}
gold_eff = {k: abs(rep[(S(10, 25), k)][0]) for k in PER}
for fn, nmx in (("US500_m5_close.npz", "US500"), ("US100_m5_close.npz", "US100")):
    zz = np.load(os.path.join(MAC, fn)); tsu = zz["ts"].astype(np.int64); clu = zz["close"].astype(float)
    tu = pd.to_datetime(tsu, unit="s", utc=True).tz_convert("Europe/London")
    wdu = tu.weekday.to_numpy(); slu = tu.hour.to_numpy() * 12 + tu.minute.to_numpy() // 5
    dayu = pd.DatetimeIndex(tu.tz_localize(None)).normalize()
    mu_ = wdu <= 4
    fu = pd.DataFrame({"day": dayu[mu_], "slot": slu[mu_], "lc": np.log(clu[mu_]), "px": clu[mu_]})
    Pu = fu.pivot_table(index="day", columns="slot", values="lc", aggfunc="first").reindex(columns=range(288))
    du = pd.DatetimeIndex(Pu.index); Puv = Pu.to_numpy()
    xu = (Puv[:, S(10, 25)] - Puv[:, S(10, 25) - 1]) * BP
    flatu = (Puv[:, S(10, 25)] == Puv[:, S(10, 25) - 1])
    PERU = {"P1 2010-13": (du <= "2013-12-31"), "P2 2014-15/03": (du >= "2014-01-01") & (du <= "2015-03-19"),
            "P3 2015/03-20 - 20": (du >= "2015-03-20") & (du <= "2020-12-31"), "P4 2021-26H1": (du >= "2021-01-01")}
    for k, mk in PERU.items():
        mk = mk.to_numpy() if hasattr(mk, "to_numpy") else mk
        x = xu[mk]; fr = np.nanmean(flatu[mk]) * 100
        mu2, t2, n2, se2 = stat(x)
        if not np.isfinite(se2): continue
        say(f"| {nmx} | {k} | {mu2:+.2f} ({t2:+.1f}) | {n2} | {fr:.0f}% | {np.nanstd(x[np.isfinite(x)], ddof=1):.1f} | **{2*se2:.2f}** | {gold_eff.get(k, float('nan')):.2f} |")
        if nmx == "US500":
            BREAK7[k] = 2 * se2 > gold_eff.get(k, 0)

# ---------- 判定 ----------
say("")
say("## 判定（事前固定の規則に機械的に当てる）")
say("")
say("| BREAK | 内容 | " + " | ".join(PER.keys()) + " |")
say("|---|---|---|---|---|---|")
rows = [("BREAK-1", "288 スロット中 t<=-3 が 10 個以上 かつ 10:25 が最負 3 位外", BREAK1),
        ("BREAK-2", ":25 と :55 が一般に沈む（10/15 時 除外・t<=-3）", BREAK2),
        ("BREAK-3", "BST 日 / GMT 日 の差 t>=2 かつ 片方 |t|<1.5", BREAK3),
        ("BREAK-4", "R_oo が R_cc の半分未満 または t(R_oo)>-2（最終ティック人工物）", BREAK4)]
for nm, desc, dd in rows:
    say(f"| {nm} | {desc} | " + " | ".join("**YES**" if dd.get(k) else "no" for k in PER) + " |")
say(f"| BREAK-5 | P4 の OOS 2025-26H1 で消失 | {'**YES**' if BREAK5 else 'no'} （全期間共通判定） |||| ")
say("| BREAK-6 | 1 倍コスト後の正味 <=0 | " + " | ".join("**YES**" if BREAK6.get(k) else "no" for k in PER) + " |")
say("| BREAK-7 | US500 対照の MDE > 金の効果量（検出力なし） | " + " | ".join("**YES**" if BREAK7.get(k) else "no" for k in PER) + " |")
n_break_p4 = sum(1 for nm, desc, dd in rows if dd.get("P4 2021-26H1"))
verdict = "broken" if n_break_p4 >= 2 else ("inconclusive" if n_break_p4 == 1 else "survived")
say("")
say(f"- **P4（最新期・前向きセルの対象期）で成立した BREAK-1..4 の数 = {n_break_p4} → 主判定 = `{verdict}`**")
say(f"- 受取り可能性: BREAK-6 (P4) = {'YES（コスト後に受け取れない）' if BREAK6.get('P4 2021-26H1') else 'no'}／OOS: BREAK-5 = {'YES' if BREAK5 else 'no'}／対照の主張: BREAK-7 (P4) = {'YES（金固有は未確立）' if BREAK7.get('P4 2021-26H1') else 'no'}")
say("")
say(f"- 実行 {time.time()-T0:.1f} s・読取りのみ・発注なし・MT5 なし・外部通信なし・プロップ参照なし・書込は data/refute_c50_auction_bar.md と本 script のみ。seed 20261118")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
