# -*- coding: utf-8 -*-
"""
[cycle32 補足 b・事後・記述] SET C = 同 ET スロット ∧ ±28 日 ∧ **建玉前 1 時間の実現ボラ V_pre が本の [0.8,1.25] 倍**（<K なら [0.67,1.5]）
— 本体 c32 の事前反証 (ii)「レンジ一致は pre の局所ボラ状態を揃えない（ΔL_pre 在 +0.105 > ΔL_post +0.048）」を直接検査する。
  SET C で ΔL_pre ≈ 0 を確認した上で ΔL_post が残れば「壁抜け固有の事後ボラ」、消えれば「局所ボラ状態の持ち越し」。
  併記: 同 side 方向ドリフト（本 vs SET C）・Δρ。判定には使わない（事後）。seed 20261110。
"""
import os, json, time
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c32b_prevol_matched.md"); NY = "America/New_York"
rng = np.random.default_rng(20261110); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle32 補足 b] 建玉前 1 時間ボラ一致プラセボ（SET C）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c32b_prevol_matched.py)")
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
NB = len(ts); r = np.zeros(NB); r[1:] = np.diff(C); flat = r == 0.0
dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
SLOT = (dt_ny.hour.to_numpy() * 12 + dt_ny.minute.to_numpy() // 5).astype(np.int32); WD = dt_ny.weekday.to_numpy().astype(np.int8)
sess = dt_ny + pd.Timedelta(hours=6); SESS = sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy()
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True)
pos = np.clip(np.searchsorted(ts, T["entry_time"].to_numpy()), 0, NB - 1); ok = ts[pos] == T["entry_time"].to_numpy()
T = T[ok].reset_index(drop=True); I0 = pos[ok]
SGN = np.where(T["side"].to_numpy() == "BUY", 1.0, -1.0); RISK = T["risk"].to_numpy(); YEAR = T["year"].to_numpy()
PRE = np.arange(-12, 0); POST = np.arange(1, 13); POST2 = np.arange(13, 37)
def vpre(I): return np.sqrt((r[np.asarray(I)[:, None] + PRE[None, :]] ** 2).mean(1))
okb = (I0 - 12 >= 0) & (I0 + 36 < NB); I2 = np.where(okb, I0, 100)
VAL = okb & (SESS[I2 - 12] == SESS[I2]) & (SESS[I2 + 36] == SESS[I2]) & (flat[I2[:, None] + POST[None, :]].sum(1) <= 3) & (WD[I2] <= 4)
near = np.zeros(NB, dtype=bool)
for d in range(-12, 13): near[np.clip(I0 + d, 0, NB - 1)] = True
IV = I0[VAL]; DAY = (T["entry_time"].to_numpy()[VAL] // 86400); YR = YEAR[VAL]; SG = SGN[VAL]; RK = RISK[VAL]
K = 4; D = np.array([d for d in range(-28, 29) if d != 0])
Cd = np.clip(IV[:, None] + 288 * D[None, :], 13, NB - 37)
okc = (SLOT[Cd] == SLOT[IV][:, None]) & (WD[Cd] <= 4) & (~flat[Cd]) & (~near[Cd]) & (SESS[Cd - 12] == SESS[Cd]) & (SESS[Cd + 36] == SESS[Cd])
okc &= flat[Cd[:, :, None] + POST[None, None, :]].sum(2) <= 3
Vp_t = vpre(IV); Vp_c = np.sqrt((r[Cd[:, :, None] + PRE[None, None, :]] ** 2).mean(2))
ratio = Vp_c / np.maximum(Vp_t[:, None], 1e-9)
ok1 = okc & (ratio >= 0.8) & (ratio <= 1.25); ok2 = okc & (ratio >= 0.67) & (ratio <= 1.5)
okc = np.where((ok1.sum(1) >= K)[:, None], ok1, ok2)
P = np.full((len(IV), K), -1, dtype=np.int64)
for q in range(len(IV)):
    c = Cd[q][okc[q]]
    if len(c) >= K: P[q] = rng.choice(c, size=K, replace=False)
okP = (P >= 0).all(1)
say(f"- 母数 {len(IV)}・SET C 確保 {okP.sum()}（候補中央値 {np.median(okc.sum(1)):.0f}）・V_pre 比（プラセボ/本）中央値 {np.median(ratio[P>=0] if False else (vpre(P[okP].ravel())/np.repeat(Vp_t[okP],K))):.3f}")
def stats(I):
    I = np.asarray(I); rp = r[I[:, None] + PRE[None, :]]; ro = r[I[:, None] + POST[None, :]]; r2 = r[I[:, None] + POST2[None, :]]
    Vp = np.sqrt((rp ** 2).mean(1)); Vo = np.sqrt((ro ** 2).mean(1)); V2 = np.sqrt((r2 ** 2).mean(1))
    zo = ro / np.maximum(Vo, 1e-9)[:, None]
    return dict(Vp=Vp, Vo=Vo, V2=V2, num=(zo[:, :-1] * zo[:, 1:]).sum(1), den=(zo[:, :-1] ** 2).sum(1), sum_o=ro.sum(1), ro=ro)
def ct(d, day):
    d = np.asarray(d, float); n = len(d); m = d.mean(); s = pd.DataFrame({"d": d - m, "g": day}).groupby("g")["d"].sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / n; return m, se, m / se
def lg(x): return np.log(np.maximum(x, 1e-6))
I = IV[okP]; Pk = P[okP]; day = DAY[okP]; yr = YR[okP]; sg = SG[okP]; rk = RK[okP]
st = stats(I); pl = [stats(Pk[:, k]) for k in range(K)]
lVo = np.mean([lg(p["Vo"]) for p in pl], 0); lVp = np.mean([lg(p["Vp"]) for p in pl], 0); lV2 = np.mean([lg(p["V2"]) for p in pl], 0)
nump = np.sum([p["num"] for p in pl], 0); denp = np.sum([p["den"] for p in pl], 0); drp = np.mean([p["sum_o"] for p in pl], 0)
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
for w, (y0, y1) in WIN.items():
    m = (yr >= y0) & (yr <= y1); d = day[m]
    a = ct(lg(st["Vo"][m]) - lVo[m], d); b = ct(lg(st["Vp"][m]) - lVp[m], d); c = ct(lg(st["V2"][m]) - lV2[m], d)
    df = pd.DataFrame({"nt": st["num"][m], "dt": st["den"][m], "np": nump[m], "dp": denp[m], "g": d}).groupby("g").sum().to_numpy()
    rt = df[:, 0].sum() / df[:, 1].sum(); rp_ = df[:, 2].sum() / df[:, 3].sum()
    bs = []
    for _ in range(1000):
        s = df[rng.integers(0, len(df), len(df))].sum(0); bs.append(s[0] / s[1] - s[2] / s[3])
    se_r = np.std(bs)
    dt_ = ct(sg[m] * st["sum_o"][m] / rk[m], d); dp_ = ct(sg[m] * drp[m] / rk[m], d); dd = ct(sg[m] * (st["sum_o"][m] - drp[m]) / rk[m], d)
    prof = np.sqrt((st["ro"][m] ** 2).mean(0)) / np.sqrt(np.mean([(p["ro"][m] ** 2).mean(0) for p in pl], 0))
    say(f"- **{w}** n {m.sum()}: ΔL_pre {b[0]:+.4f} (t {b[2]:+.2f})［一致確認］・**ΔL_post {a[0]:+.4f} (se {a[1]:.4f}・t {a[2]:+.2f}・MDE {2*a[1]:.4f})**・ΔL_post2 {c[0]:+.4f} (t {c[2]:+.2f})")
    say(f"  - ρ_1 post 本 {rt:+.4f}／SET C {rp_:+.4f}・Δρ {rt-rp_:+.4f} (z {(rt-rp_)/se_r:+.2f})；方向ドリフト 本 {dt_[0]:+.4f}R (t {dt_[2]:+.2f})／同 side SET C {dp_[0]:+.4f}R (t {dp_[2]:+.2f})・**対差 {dd[0]:+.4f}R (t {dd[2]:+.2f})**")
    say(f"  - 足別 RMS 比 j=1..12: " + " ".join(f"{x:.2f}" for x in prof))
# 方向ドリフトの足別プロファイル（本 − 同 side プラセボ・R 単位・累積）
for w, (y0, y1) in WIN.items():
    m = (yr >= y0) & (yr <= y1)
    cum_t = np.cumsum((sg[m][:, None] * st["ro"][m] / rk[m][:, None]).mean(0)); cum_p = np.cumsum(np.mean([(sg[m][:, None] * p["ro"][m] / rk[m][:, None]).mean(0) for p in pl], 0))
    say(f"- {w} 累積 方向ドリフト（本−プラセボ・R）j=1..12: " + " ".join(f"{x:+.3f}" for x in (cum_t - cum_p)))
say(f"- 実行時間 {time.time()-T0:.1f}s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
