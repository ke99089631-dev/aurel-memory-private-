# -*- coding: utf-8 -*-
"""
[反証レーン 続き・走 4] 走 2／走 3 で 2 回 失敗した 2 点を直して裁定する。

(A) **London ローカル → UTC グリッド添字の変換バグ（私の side・2 回目）**。
    走 2 は tz-aware DatetimeIndex に .view("int64") を使って全滅。走 3 は .asi8 に直したが
    **pandas 3.0 の DatetimeIndex は datetime64[us] 分解能なので asi8 はマイクロ秒**で、
    1e9 で割ったため 1000 倍ずれて全部グリッド外＝再び n=0。走 4 は
    `astype("datetime64[s]").astype("int64")` で単位非依存にする。
    → c50 の LBMA PRE 足（London 10:25／14:55・分 :25／:55）と「同じ 分-of-hour の他スロット」
      基準線を期間別に出し、BREAK-K1 を**初めて数で**裁定する。
      条件（走 1 で事前固定したものを引き継ぐ）: 時計ビンが沈みの 50% 以上を説明 → BROKEN。

(B) 走 3 の BREAK-N3（持続性）は**ドリフト交絡で解釈不能**。60 分の累積はアジア午前の期間ドリフト
    （c54 自身が P0 で +0.14 bp/足と報告）を拾うため、P0 AM の累積が +456% になるなど非単調。
    走 4 はドリフト調整版: 累積 − k × （その期間・そのスロット帯の 1 足平均）で測り直す。
    条件（走 4 で事前固定・走 3 の N3 を置換）:
      BREAK-N3': ドリフト調整後の累積が +30 分時点で +5 分値の 50% 未満（AM と PM の両方）
                 → 直後の正は一時的な流動性の窪み＝c54 の機構候補（輸入銀行の裁定買いによる
                   価格発見）は支持されない。片方だけなら「部分的」。

seed 20261119。読取り専用・npz のみ。
"""
import os, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c54_sge_d_result.md")
SEED = 20261119; rng = np.random.default_rng(SEED)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
VERD = []
def brk(tag, cond, obs, broken):
    say(f"- [{tag}] 条件: {cond}")
    say(f"  - 観測: {obs}")
    say(f"  - 判定: {'BROKEN' if broken else 'not broken'}")
    VERD.append((tag, bool(broken)))

say(f"# [REFUTE c54 走 4] c50 の沈みの分解・持続性のドリフト調整 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c54_sge_d.py)")

z = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
r_raw = np.zeros(len(cl)); r_raw[1:] = np.diff(np.log(cl)); r_raw *= 1e4
flat_raw = (r_raw == 0)
t0 = (ts[0] // 86400) * 86400; t1 = ((ts[-1] // 86400) + 1) * 86400 - 300
N = (t1 - t0) // 300 + 1; ND = N // 288
G = np.full(N, np.nan); FL = np.zeros(N, bool); PRESENT = np.zeros(N, bool)
gi = (ts - t0) // 300; G[gi] = r_raw; FL[gi] = flat_raw; PRESENT[gi] = True
day_start = t0 + np.arange(ND) * 288 * 300
dday = pd.to_datetime(day_start, unit="s", utc=True)
dwd = dday.weekday.to_numpy()
dnorm = pd.DatetimeIndex(dday.tz_localize(None))
def S(h, m): return h * 12 + m // 5
AMS, PMS = S(2, 15), S(6, 15)
minute_of_hour = (np.arange(288) % 12) * 5
P0 = (dnorm >= "2010-01-01") & (dnorm <= "2016-04-18")
P1 = (dnorm >= "2016-04-19") & (dnorm <= "2020-12-31")
P2 = (dnorm >= "2021-01-01"); PR = (dnorm >= "2024-01-01")
PERS = [("P0", P0), ("P1", P1), ("P2", P2), ("近年", PR)]

def stat(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return dict(n=n, m=np.nan, se=np.nan, t=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
    return dict(n=n, m=m, se=se, t=m / se if se > 0 else np.nan)
def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    d = a.mean() - b.mean(); return d, d / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))

# ---------- (A) unit-independent London-local -> grid slot ------------------------------------------
def london_slot(hh, mm):
    loc = dnorm + pd.Timedelta(hours=hh, minutes=mm)
    aware = loc.tz_localize("Europe/London", nonexistent="NaT", ambiguous="NaT")
    bad = np.asarray(pd.isna(aware))
    naive = aware.tz_convert("UTC").tz_localize(None)            # unit-independent, tz-free
    sec = np.asarray(naive.values).astype("datetime64[s]").astype("int64")
    out = np.full(ND, -1, dtype=np.int64)
    g = (sec - t0) // 300
    okm = (~bad) & (g >= 0) & (g < N)
    out[okm] = g[okm]
    return out

# self-check: the mapping must land on minute mm and on London-local hour hh
chk = london_slot(10, 25); v = chk[chk >= 0]
say(f"- 変換の自己検査: 有効 {len(v)}/{ND} 日・UTC スロットの分 "
    f"{sorted(set(((v % 288) % 12) * 5))}（:25 のみであるべき）・UTC 時の分布 "
    f"{dict(pd.Series((v % 288) // 12).value_counts().sort_index())}（9 時 = BST・10 時 = GMT であるべき）")
assert set(((v % 288) % 12) * 5) == {25}, "分が :25 でない＝変換バグ"

lon_band = np.isin(np.arange(288) // 12, list(range(7, 17)))
C50 = [("c50-P1 2010-13", (dnorm >= "2010-01-01") & (dnorm <= "2013-12-31")),
       ("c50-P2 2014-01〜2015-03-19", (dnorm >= "2014-01-01") & (dnorm <= "2015-03-19")),
       ("c50-P3 2015-03-20〜2020", (dnorm >= "2015-03-20") & (dnorm <= "2020-12-31")),
       ("c50-P4 2021-26H1", (dnorm >= "2021-01-01"))]
C50REF = {("AM", "c50-P1 2010-13"): -1.34, ("AM", "c50-P2 2014-01〜2015-03-19"): +0.06,
          ("AM", "c50-P3 2015-03-20〜2020"): -0.65, ("AM", "c50-P4 2021-26H1"): -1.07,
          ("PM", "c50-P1 2010-13"): -0.52, ("PM", "c50-P2 2014-01〜2015-03-19"): -2.21,
          ("PM", "c50-P3 2015-03-20〜2020"): -0.90, ("PM", "c50-P4 2021-26H1"): -0.86}

say("\n## A c50 の LBMA 沈み（PRE 足）と「同 分-of-hour の他スロット（London 帯 UTC 07–16）」基準線")
K1 = {}; rep_hit = 0; rep_tot = 0
for tag, (ah, am_) in [("AM", (10, 30)), ("PM", (15, 0))]:
    ph, pm_ = (ah, am_ - 5) if am_ >= 5 else (ah - 1, 55)
    gs = london_slot(ph, pm_)
    pres = (gs >= 0) & (dwd <= 4)
    pres = pres & PRESENT[np.clip(gs, 0, N - 1)]
    own = np.full(ND, np.nan); own[pres] = G[gs[pres]]
    mo = pm_; cols = np.flatnonzero(lon_band & (minute_of_hour == mo))
    say(f"\n### {tag} オークション {ah:02d}:{am_:02d} London → PRE 足 {ph:02d}:{pm_:02d}（分 :{mo:02d}）・基準線 {len(cols)} スロット")
    for nm, msk in C50:
        a = own[msk]; a = a[np.isfinite(a)]
        rows = np.flatnonzero(msk & (dwd <= 4))
        idx = rows[:, None] * 288 + cols[None, :]
        keep = PRESENT[idx] & (idx != gs[rows][:, None])
        bl = G[idx][keep]
        sa = stat(a); sb = stat(bl); d_, t_ = welch(a, bl)
        ref = C50REF.get((tag, nm))
        rep_tot += 1
        okrep = (ref is not None) and abs(sa["m"] - ref) <= 0.06
        rep_hit += okrep
        share = (sb["m"] / sa["m"] * 100) if (sa["m"] < 0 and sb["m"] < 0) else 0.0
        say(f"- {nm}: PRE 足 **{sa['m']:+.3f} bp (t {sa['t']:+.2f}, n {sa['n']})**"
            + (f"〔c50 公表 {ref:+.2f} → {'再現' if okrep else '**差**'}〕" if ref is not None else "")
            + f"／同分 :{mo:02d} 基準線 {sb['m']:+.3f} (t {sb['t']:+.2f}, n {sb['n']})"
            + f"／**超過 {d_:+.3f} (Welch t {t_:+.2f})**・時計ビンが説明する割合 {share:.0f}%")
        K1[(tag, nm)] = (sa["m"], sb["m"], d_, t_, share)
say(f"- c50 の公表値の再現 **{rep_hit}/{rep_tot}**（許容 ±0.06 bp・c50 の窓定義が bid/London DST で私と同一なら一致するはず）")
sh = [v[4] for k, v in K1.items() if v[0] < 0 and v[1] < 0]
med = float(np.median(sh)) if sh else float("nan")
brk("BREAK-K1 (走 4・初めて数で裁定)",
    "c50 の沈みが「分 :25／:55 の時計ビン」でおおむね説明される（説明割合の中央値 ≥ 50%）",
    "／".join(f"{k[0]} {k[1].split()[0]} 沈み {v[0]:+.2f}・基準線 {v[1]:+.2f}・超過 {v[2]:+.2f}(t {v[3]:+.1f})・説明 {v[4]:.0f}%"
              for k, v in K1.items()) + f" → 負×負セルの説明割合 中央値 **{med:.0f}%**",
    (not math.isnan(med)) and med >= 50)

# ---------- (B) drift-adjusted persistence ---------------------------------------------------------
say("\n## B 持続性（ドリフト調整）— 累積 − k×（同期間・同帯の 1 足平均）")
def band_mean(msk, s0, span=12):
    """mean 5-min return over the slots s0..s0+span-1 in the same period = local drift per bar"""
    rows = np.flatnonzero(msk & (dwd <= 4))
    idx = (rows[:, None] * 288 + np.arange(s0, s0 + span)[None, :]).ravel()
    v = G[idx][PRESENT[idx]]
    return v.mean() if len(v) else np.nan

for lab, s0 in [("AM 02:15", AMS), ("PM 06:15", PMS)]:
    for nm, msk in PERS:
        mu = band_mean(msk, s0, 12)
        rows = np.flatnonzero(msk & (dwd <= 4)); idx = rows * 288
        okall = np.ones(len(rows), bool)
        for k in range(12): okall &= PRESENT[idx + s0 + k]
        acc = np.zeros(len(rows)); ser = []
        for k in range(12):
            acc = acc + G[idx + s0 + k]
            s = stat(acc[okall] - mu * (k + 1)); ser.append((k, s["m"], s["t"]))
        f5 = ser[0][1]; f30 = ser[5][1]; f60 = ser[11][1]
        say(f"- {lab} {nm} (ドリフト {mu:+.3f} bp/足): 調整累積 +5 分 {f5:+.3f}({ser[0][2]:+.1f})"
            f"・+15 分 {ser[2][1]:+.3f}({ser[2][2]:+.1f})・+30 分 {f30:+.3f}({ser[5][2]:+.1f})"
            f"・+60 分 {f60:+.3f}({ser[11][2]:+.1f})"
            + (f"・+30/+5 = {f30/f5*100:.0f}%" if f5 != 0 else ""))
        if nm == "P1":
            if lab.startswith("AM"): am_r = f30 / f5
            else: pm_r = f30 / f5
brk("BREAK-N3' (走 3 の N3 を置換)",
    "ドリフト調整後の累積が +30 分時点で +5 分値の 50% 未満（AM と PM の両方）＝一時的な流動性の窪み",
    f"AM P1 +30/+5 = {am_r*100:.0f}%・PM P1 = {pm_r*100:.0f}%",
    (am_r < 0.50) and (pm_r < 0.50))
say(f"- 片方だけなら「部分的」: AM {'<50%' if am_r<0.5 else '≥50%'}・PM {'<50%' if pm_r<0.5 else '≥50%'}")

say("\n## 走 4 のまとめ")
for tag, v in VERD: say(f"- {tag}: {'BROKEN' if v else 'not broken'}")
say(f"- 実行 {time.time()-T0:.1f} s・seed {SEED}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\nwrote {OUT}")
