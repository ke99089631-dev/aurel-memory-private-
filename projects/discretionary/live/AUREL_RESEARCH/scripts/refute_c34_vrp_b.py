# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-11 補足 b・事後・記述] refute_c34_vrp R6 の自己検査:
  1 日（建玉セッション日）RV に対する scan の β（在 t 2.61／外 2.80／近年 2.43）は、保有窓の足そのものがセッション RV に含まれる
  （TP 到達＝大きな動き＝RV 上昇）ため機械的な正相関を含む。保有窓の足を除いた同セッションの RV（RV1x）で β を再計算し、
  機械的な分と「建玉日の他の時間帯もボラが高いか（本当のボラ露出）」を分ける。21 日前向き RV も建玉日を除いた版（RVfx）を併記。
  さらに 2026-01 の分散単位 −16.5 の正体（どの前向き窓か・GVZ と RVf の日次）を印字。
書き込み: data/refute_c34_vrp_b.md・data/refute_c34_vrp_b_run.log のみ。
"""
import os, time, json
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c34_vrp_b.md"); NY = "America/New_York"; H = 21
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [refute c34 補足 b] 1 日 RV 露出の機械的成分の分離 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c34_vrp_b.py)")
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
lc = np.log(C); r2 = np.zeros(len(C)); r2[1:] = np.diff(lc) ** 2; flat = r2 == 0
dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY); sess = dt_ny + pd.Timedelta(hours=6)
S = sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy()
df = pd.DataFrame({"s": S, "r2": r2, "nf": (~flat).astype(np.int32)}); g = df.groupby("s", sort=True)
D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum()}); D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d")
D = D[(D["date"].dt.weekday <= 4) & (D["nf"] >= 100)].reset_index(drop=True)
rv = D["rv"].to_numpy(); n = len(D); cs = np.concatenate([[0.0], np.cumsum(rv)]); i = np.arange(n)
ann = lambda x, h: 100 * np.sqrt(np.maximum(252.0 / h * x, 0))
D["RVf"] = np.nan; ok = i + H < n; D.loc[ok, "RVf"] = ann(cs[i[ok] + H + 1] - cs[i[ok] + 1], H)
D["RVfx"] = np.nan; D.loc[ok, "RVfx"] = ann(cs[i[ok] + H + 1] - cs[i[ok] + 2], H - 1)   # 建玉日の翌日から 20 日
D["RV1"] = ann(rv, 1)
GV = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"), na_values="."); GV.columns = ["date", "IV"]; GV["date"] = pd.to_datetime(GV["date"]); GV = GV.dropna()
D = D.merge(GV, on="date", how="left")
cs_bar = np.concatenate([[0.0], np.cumsum(r2)])
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True); FT = J["frozen"]["FEED_TOL"]
e_ny = pd.to_datetime(T["entry_time"], unit="s", utc=True).dt.tz_convert(NY) + pd.Timedelta(hours=6); T["sdate"] = e_ny.dt.normalize().dt.tz_localize(None)
ent_jst = pd.to_datetime(T["entry_time"], unit="s", utc=True) + pd.Timedelta(hours=9)
T["avail"] = (ent_jst - pd.Timedelta(hours=7)).dt.normalize().dt.tz_localize(None) - pd.Timedelta(days=1)
K = D[["date", "IV"]].dropna().rename(columns={"date": "kdate"}).sort_values("kdate")
T = pd.merge_asof(T.sort_values("avail"), K, left_on="avail", right_on="kdate", direction="backward", tolerance=pd.Timedelta(days=7))
T = T.merge(D[["date", "RV1", "RVf", "RVfx", "rv", "nf"]].rename(columns={"date": "sdate"}), on="sdate", how="left").sort_values("entry_time").reset_index(drop=True)
# 保有窓の Σr² を同セッションから除く
ie = np.searchsorted(ts, T["entry_time"].to_numpy()); hold = T["hold"].to_numpy().astype(int); ix = np.minimum(ie + hold, len(ts) - 1)
hold_r2 = cs_bar[ix + 1] - cs_bar[np.minimum(ie + 1, len(ts) - 1)]
# 保有窓がセッション日をまたぐ本は除外（セッション外の足を引かないため）
sd_end = S[np.minimum(ix, len(S) - 1)]; sd_ent = S[np.minimum(ie, len(S) - 1)]; same = sd_end == sd_ent
T["RV1x"] = np.where(same, 100 * np.sqrt(np.maximum(252.0 * (T["rv"].to_numpy() - hold_r2), 0)), np.nan)
T["VSv1"] = (T["RV1"] ** 2 - T["IV"] ** 2) / 100; T["VSv1x"] = (T["RV1x"] ** 2 - T["IV"] ** 2) / 100
T["VSv21"] = (T["RVf"] ** 2 - T["IV"] ** 2) / 100; T["VSv21x"] = (T["RVfx"] ** 2 - T["IV"] ** 2) / 100
T["day"] = T["entry_time"] // 86400; dec = T["exit"].isin(["TP", "SL"]) & T["IV"].notna()
say(f"- 決着 ∧ IV {dec.sum()}・保有窓が建玉セッション内に収まる本 {(dec & same).sum()}（{(same[dec]).mean()*100:.1f}%）・hold 中央値 {np.median(hold):.0f} 本・保有窓 Σr² の建玉日 Σr² に占める割合 中央値 {np.nanmedian(hold_r2[dec & same] / T.loc[dec & same, 'rv'])*100:.1f}%")
def cl_ols(y, x, day):
    y = np.asarray(y, float); x = np.asarray(x, float); xm = x - x.mean(); b = (xm * y).sum() / (xm ** 2).sum(); a = y.mean() - b * x.mean()
    u = y - a - b * x; s = pd.DataFrame({"d": xm * u, "g": day}).groupby("g")["d"].sum().to_numpy(); se = np.sqrt((s ** 2).sum()) / (xm ** 2).sum(); return b, se, b / se
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
say("| 窓 | n | 露出 | β (R per 分散単位・日cl t) | mean VS | 予算 (R) |")
say("|---|---|---|---|---|---|")
for w, (y0, y1) in WIN.items():
    for lab, col, msk in (("1 日 全体", "VSv1", same), ("1 日 保有窓除外 (RV1x)", "VSv1x", same), ("21 日 全体", "VSv21", np.ones(len(T), bool)), ("21 日 建玉日除外 (RVfx)", "VSv21x", np.ones(len(T), bool))):
        m = dec & msk & (T["year"] >= y0) & (T["year"] <= y1) & T[col].notna(); d = T[m]; b, se, t = cl_ols(d["R"], d[col], d["day"]); mv = d[col].mean()
        say(f"| {w} | {len(d)} | {lab} | {b:+.5f} ({t:+.2f}) | {mv:+.2f} | {b*mv:+.4f} |")
# 建玉前（セッション開始〜建玉足）と手仕舞い後（exit 足〜セッション終了）に分ける（同セッション内の本のみ・RV は年率化せず Σr² を 1e4 倍）
s_start = np.searchsorted(S, S[np.minimum(ie, len(S) - 1)], side="left"); s_end = np.searchsorted(S, S[np.minimum(ie, len(S) - 1)], side="right") - 1
pre_r2 = cs_bar[np.minimum(ie + 1, len(ts) - 1)] - cs_bar[s_start]; post_r2 = cs_bar[s_end + 1] - cs_bar[ix + 1]
T["pre"] = np.where(same, pre_r2 * 1e4, np.nan); T["post"] = np.where(same, post_r2 * 1e4, np.nan); T["IVd"] = (T["IV"] / 100) ** 2 / 252 * 1e4
say("\n## 建玉前 vs 手仕舞い後（同セッション・Σr²×1e4・GVZ の日次分散 IVd と同単位・分散サプライズ = Σr² − IVd×(足数/288)）")
nb_pre = (ie - s_start + 1); nb_post = (s_end - ix)
T["VSpre"] = T["pre"] - T["IVd"] * nb_pre / 288; T["VSpost"] = T["post"] - T["IVd"] * nb_post / 288
say("| 窓 | n | 露出 | β (R per 単位・日cl t) | 足数 中央値 |")
say("|---|---|---|---|---|")
for w, (y0, y1) in WIN.items():
    for lab, col, nbv in (("建玉前", "VSpre", nb_pre), ("手仕舞い後", "VSpost", nb_post)):
        m = dec & same & (T["year"] >= y0) & (T["year"] <= y1) & T[col].notna() & (nbv >= 12); d = T[m]; b, se, t = cl_ols(d["R"], d[col], d["day"])
        say(f"| {w} | {len(d)} | {lab} | {b:+.5f} ({t:+.2f}) | {np.median(nbv[m.to_numpy()]):.0f} |")
# 2026-01 の正体
say("\n## 2026-01 の分散単位 −16.5 の正体（日次・GVZ vs RVf・RV1）")
d = D[(D["date"] >= "2026-01-01") & (D["date"] <= "2026-02-28")].copy(); d["VRPvar"] = (d["IV"] ** 2 - d["RVf"] ** 2) / 100
say("- " + " | ".join(f"{r.date.strftime('%m-%d')}: GVZ {r.IV:.0f} RVf {r.RVf:.0f} RV1 {r.RV1:.0f} VRPv {r.VRPvar:+.0f}" for _, r in d[d["date"].dt.day % 3 == 1].iterrows()))
top = D.assign(VRPvar=(D["IV"] ** 2 - D["RVf"] ** 2) / 100).nlargest(5, "RV1")[["date", "IV", "RV1", "RVf", "VRPvar"]]
say("- 2010-26 の RV1 上位 5 日: " + "；".join(f"{r.date.date()} RV1 {r.RV1:.0f}% GVZ {r.IV:.0f} RVf {r.RVf:.0f} VRPv {r.VRPvar:+.1f}" for _, r in top.iterrows()))
# 2026 を 1 月の窓（RVf が 1 月下旬〜2 月上旬を含む日）抜きで
d26 = D[(D["date"].dt.year == 2026) & D["IV"].notna() & D["RVf"].notna()].copy(); d26["VRPvar"] = (d26["IV"] ** 2 - d26["RVf"] ** 2) / 100
ex = d26[d26["date"] >= "2026-02-10"]
say(f"- 2026 全体 n{len(d26)} 分散単位 {d26['VRPvar'].mean():+.2f}／2026-02-10 以降 n{len(ex)} {ex['VRPvar'].mean():+.2f}（vol pt {(ex['IV']-ex['RVf']).mean():+.2f}）")
say(f"\n- 実行時間 {time.time()-T0:.1f}s・look-ahead（記述）・scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
