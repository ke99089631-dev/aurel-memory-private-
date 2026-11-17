# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-18 03:30 / 第 2 段（第 1 段の結果を見た後に宣言する規則）]
第 1 段の結果: R1 ★完全再現／R2 ☠λ=0.308（機械項 +0.384 = DiD の 78%）／**R3 主判定は ★不発（外 β_PRE調整 +0.280・t 1.68 で閾値 0.246／1.5 をわずかに超えた）**／
             R4 ★+0.310 (1.84)／R5 ★caliper +0.286 (1.32)／R6 ☠偽腕 +0.404 vs 実測 +0.563（p 0.14）／R7 ☠Holm 0.2445。
第 1 段が残した 3 つの穴を、第 2 段として先に規則を書いてから埋める:
  穴① R3/R4/R5 が +0.28〜+0.31 に揃った。これが「本物の残差」か「偽腕でも出る残差」か未決着
      （R6 は DiD 版しか偽腕に当てていない）。→ S1。
  穴② 第 1 段の α_腕 表は切片に落ちた時刻ダミーを含み腕間比較に使えない（ANN_J は 8/14 時のみ・UJ は全時刻）。
      c47 の読みの第 2 の脚「UJ は状態を変えない（ΔE_W3 ≈0）」は未検定のまま。→ S2。
  穴③ λ は腕で違う（ANN_J 0.193・UJ 0.541）。共通 λ の 1 本の線で contrast を 1 つの数にするのは
      どちらかの腕を support 外へ外挿している可能性。→ S3。
  穴④ 第 1 段 R6 の偽腕候補プールは全年（窓期を切っていない）＝λ の年代差 0.264/0.308 が混ざる。→ S1 で窓期限定版も出す。
  穴⑤ decluster は先着採用なので UJ の W3 窓に後続 5σ ジャンプが入り得る（UJ の W3 水準を上げ DiD を ANN 不利＝保守側へ）。→ S4。

=== 第 2 段の破壊規則（数字を見る前に宣言） ===
 S1 BREAK-ADJ-PLACEBO（本段の主判定）: 第 1 段 R6 と**完全に同一の偽腕構成**（同 ET 時 × ρ_PRE ±0.15 の非事象足・事象ゼロ）に
    **R3 と同一の仕様**（ρ_W3 ~ treat + ρ_PRE + log z + 時刻 FE・日クラスタ）を当てる。NFAKE=300・窓期限定プール版も併記。
    **当たり条件 = 偽腕の β 平均 ≥ 0.5 · 実測 ρ 版 β ∨ 実測の片側経験 p > 0.05**（＝PRE 共変量版の +0.28 も事象ゼロで出る）。
    不発なら「+0.28 は偽腕では出ない残差」＝ c47 の DiD は大きさは壊れたが残差は本物、と書く。
 S2 BREAK-UJ-FLAT（c47 の読みの第 2 の脚）: 「予定外ジャンプは vol 状態を変えない」を正しく測る。
    腕ごとの **PRE 調整済み超過水準 A_腕 = Ē_W3 − λ_pop · Ē_PRE**（λ_pop = 第 1 段 R2 の窓期別母集団 λ）を ET 日クラスタ bootstrap 1000 回で。
    **当たり条件 = UJ の A_W3 が 外で > 0 かつ t ≥ 2**（＝UJ も状態を作っており「変えない」は推定器の産物）。
 S3 BREAK-NOSINGLE（contrast が 1 つの数に定まらない）: 交互作用仕様 E_W3 ~ treat + E_PRE + treat·(E_PRE − c) + log z + 時刻 FE を
    c = 0（ANN_J の居場所）と c = Ē_PRE,UJ（UJ の居場所）で評価。
    **当たり条件 = 外の β_treat(c=0) と β_treat(c=Ē_PRE,UJ) の差が 0.20 以上**（＝評価点で結論が変わる＝単一の DiD 値は定義されない）。
 S4 BREAK-FOLLOWON（記述→規則化）: UJ の W3 窓 [t0+25 足, t0+48 足] に別の declustered 5σ ジャンプが入る事象を除外して再推定。
    **当たり条件 = 除外後の DiD_W3(外) が +0.60 以上**（＝第 1 段までの DiD はむしろ過小で、私の破壊は逆方向に効いていた）。
 S5（記述・判定外）: 第 1 段 R3 の閾値感度。β<0.5·0.492 と |t|<1.5 という私の書き方が結論を握った度合いを明示する。
survived（c47 側）= S1 不発 ∧ S2 不発。broken = S1 当たり ∨ S2 当たり。
入力 = data/c47_events_excess.csv ＋ XAU_m5_close.npz ＋ c45 ジャンプ CSV（第 1 段と同一）。seed 20261118。
出力 data/refute_c47_did_mechanics_b.md。読取専用・発注なし・本番編集なし・外部通信なし。
"""
import os, math, time, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c47_did_mechanics_b.md"); L = []
NY = "America/New_York"; SEED = 20261118; rng = np.random.default_rng(SEED)
W_SIG = 5520; NFAKE = 300; CAL = 0.15; NBOOT = 1000
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
LAM_POP = {"在 2010-20": 0.264, "外 2021-26H1": 0.308, "近年 2024-26H1": 0.353}  # 第 1 段 R2

def say(s=""):
    print(s, flush=True); L.append(s)

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def dummies(vals):
    u = sorted(pd.unique(vals))[1:]
    if not u: return np.zeros((len(vals), 0))
    return np.column_stack([(np.asarray(vals) == v).astype(float) for v in u])

def fit(o, ycol, treat, ctrlarm, extra=(), inter=None, fe=("hr",)):
    o = o[(o.cls == treat) | (o.cls == ctrlarm)]
    cols = [ycol] + list(extra) + ["logz"]
    o = o[np.isfinite(o[cols]).all(axis=1)]
    if (o.cls == treat).sum() < 5 or (o.cls == ctrlarm).sum() < 5: return np.nan, np.nan, {}, 0, 0
    d = (o.cls == treat).to_numpy(float); y = o[ycol].to_numpy(float)
    parts = [np.ones(len(o)), d]; names = ["const", "treat"]
    for c in extra: parts.append(o[c].to_numpy(float)); names.append(c)
    if inter is not None:
        col, c0 = inter
        parts.append(d * (o[col].to_numpy(float) - c0)); names.append("inter")
    parts.append(o["logz"].to_numpy(float)); names.append("logz")
    for f in fe:
        H = dummies(o[f].to_numpy())
        if H.shape[1]: parts.append(H); names += [f"{f}_{j}" for j in range(H.shape[1])]
    X = np.column_stack(parts)
    beta, V, G = ols_cluster(y, X, o["day"].to_numpy())
    cf = {n: (beta[i], math.sqrt(max(V[i, i], 0))) for i, n in enumerate(names) if n in ("treat", "inter") or n in extra}
    return beta[1], math.sqrt(max(V[1, 1], 0)), cf, int((o.cls == treat).sum()), int((o.cls == ctrlarm).sum())

def tt(b, se): return (b / se) if (se and se > 0 and np.isfinite(se)) else float("nan")
def f2(b, se): return f"{b:+.3f} (t {tt(b,se):+.2f})"

say("# [REFUTE 2026-11-18 03:30 第2段] 第 1 段が残した 4 つの穴（S1〜S4）")
say(f"- 第 2 段の破壊規則は docstring に先に宣言（第 1 段の数字は見たが S1〜S4 の数字は未見）・seed {SEED}")
say("")

EV = pd.read_csv(os.path.join(DATA, "c47_events_excess.csv")); EV["day"] = EV.et_date
for w in ["W1", "W2", "W3", "W4"]:
    EV["d" + w] = EV["E_" + w] - EV["E_PRE"]
    EV["dr" + w] = EV["rho_" + w] - EV["rho_PRE"]
def sub(lo, hi): return EV[(EV.year >= lo) & (EV.year <= hi)]

# ---- npz（第 1 段と同一前処理） ----
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
N = len(ts); tt_ = pd.to_datetime(ts, unit="s", utc=True); tny = tt_.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yrs = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4; nf = np.isfinite(r) & (r != 0)
r2 = np.where(nf, r * r, 0.0); c2 = np.r_[0.0, np.cumsum(r2)]; cn = np.r_[0, np.cumsum(nf.astype(np.int64))]
idx = np.arange(N); lo_ = idx - 1 - W_SIG; hi_ = idx - 1; valid = (lo_ >= 0)
S2_ = np.where(valid, c2[np.clip(hi_ + 1, 0, N)] - c2[np.clip(lo_ + 1, 0, N)], np.nan)
NN_ = np.where(valid, cn[np.clip(hi_ + 1, 0, N)] - cn[np.clip(lo_ + 1, 0, N)], 0)
sig = np.sqrt(np.where(NN_ >= 1000, S2_ / np.maximum(NN_, 1), np.nan)); z = np.abs(r) / sig

def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d12 = pd.Timestamp(year=y, month=m, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
CPI = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
evdays = pd.DatetimeIndex(sorted(set(list(nfp_dates_v2().normalize()) + list(pd.DatetimeIndex(F.date).normalize()) + list(CPI.normalize()))))
isevbar = np.asarray(etdate.isin(evdays)); trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
JC = pd.read_csv(os.path.join(DATA, "c45_jumps_5sigma_declustered.csv")); J5 = np.sort(JC.ts.to_numpy(np.int64))
last_j = np.searchsorted(J5, ts, side="right") - 1
since_j = np.where(last_j >= 0, ts - J5[np.clip(last_j, 0, None)], 10 ** 9)
elig = nf & trading & ~isevbar & np.isfinite(sig) & (z < 5) & (since_j >= 14400)

def win_logrv(ii, a, b, nmin):
    ii = np.asarray(ii, np.int64); out = np.full(len(ii), np.nan)
    ok = (ii + a >= 0) & (ii + b < N)
    s = c2[np.clip(ii + b + 1, 0, N)] - c2[np.clip(ii + a, 0, N)]
    n = cn[np.clip(ii + b + 1, 0, N)] - cn[np.clip(ii + a, 0, N)]
    good = ok & (n >= nmin) & (s > 0); out[good] = np.log(s[good] / n[good]); return out
RPRE = win_logrv(idx, -12, -1, 6) - 2 * np.log(sig)
RW3 = win_logrv(idx, 25, 48, 12) - 2 * np.log(sig)
say(f"- npz {N} 本・適格足 {int(elig.sum())}（第 1 段と同一定義）")
say("")

# ================= S1 BREAK-ADJ-PLACEBO =================
say("## S1 BREAK-ADJ-PLACEBO（主判定・偽腕に R3 と同じ PRE 共変量仕様を当てる）")
say("| 窓 | プール | 実測 ρ 版 β_adj (t) | 偽腕 β_adj 平均 (sd) | 超過 | 片側経験 p | 参考: 偽腕 DiD 平均 |")
say("|---|---|---|---|---|---|---|")
S1 = {}
for pool_mode in ["全年", "窓期限定"]:
    for lab, lo, hi in ERAS[:2]:
        o = sub(lo, hi)
        o = o[o.cls.isin(["ANN_J", "UJ"]) & np.isfinite(o[["rho_PRE", "rho_W3", "drW3"]]).all(axis=1)].copy()
        if pool_mode == "全年":
            pm = elig & np.isfinite(RPRE) & np.isfinite(RW3)
        else:
            pm = elig & np.isfinite(RPRE) & np.isfinite(RW3) & (yrs >= lo) & (yrs <= hi)
        by_hr = {}
        for h in range(24):
            a = idx[pm & (hr == h)]
            if len(a): by_hr[h] = (a, np.sort(RPRE[a]), np.argsort(RPRE[a]))
        cand = []
        for _, row in o.iterrows():
            h = int(row.hr)
            if h not in by_hr: cand.append(np.array([], np.int64)); continue
            arr, pv_s, srt = by_hr[h]
            aa = np.searchsorted(pv_s, row.rho_PRE - CAL); bb = np.searchsorted(pv_s, row.rho_PRE + CAL, side="right")
            cand.append(arr[srt[aa:bb]])
        b_real, se_real, _, nt, nc = fit(o.rename(columns={"rho_W3": "y", "rho_PRE": "x"}), "y", "ANN_J", "UJ", extra=("x",))
        treat = (o.cls == "ANN_J").to_numpy(); lz = o.logz.to_numpy()
        bs = np.full(NFAKE, np.nan); bd = np.full(NFAKE, np.nan)
        for q in range(NFAKE):
            pick = np.array([(c[rng.integers(len(c))] if len(c) else -1) for c in cand]); ok = pick >= 0
            if ok.sum() < 30: continue
            p_ = pick[ok]
            dd = pd.DataFrame({"y": RW3[p_], "x": RPRE[p_], "logz": lz[ok], "hr": hr[p_],
                               "day": etdate[p_].strftime("%Y-%m-%d"), "cls": np.where(treat[ok], "ANN_J", "UJ")})
            dd["dy"] = dd.y - dd.x
            dd = dd[np.isfinite(dd[["y", "x"]]).all(axis=1)]
            bs[q] = fit(dd, "y", "ANN_J", "UJ", extra=("x",))[0]
            bd[q] = fit(dd, "dy", "ANN_J", "UJ")[0]
        v = bs[np.isfinite(bs)]; vd = bd[np.isfinite(bd)]
        p_emp = float((v >= b_real).mean()) if len(v) else float("nan")
        say(f"| {lab} | {pool_mode} | {f2(b_real,se_real)} | **{v.mean():+.3f}** ({v.std(ddof=1):.3f}・{len(v)} 回) | {b_real-v.mean():+.3f} | **{p_emp:.4f}** | {vd.mean():+.3f} |")
        S1[(pool_mode, lab)] = (b_real, v.mean(), p_emp)
br, fk, pe = S1[("窓期限定", "外 2021-26H1")]
s1_hit = (fk >= 0.5 * br) or (pe > 0.05)
say(f"- **S1 判定: {'☠BREAK-ADJ-PLACEBO が当たった（PRE 共変量版の残差も事象ゼロで出る）' if s1_hit else '★不発（+0.28 は偽腕では出ない＝本物の残差）'}**"
    f" [窓期限定・外: 偽平均 {fk:+.3f} ≥ 0.5·実測 {0.5*br:+.3f} → {fk>=0.5*br} / 経験 p {pe:.4f} > 0.05 → {pe>0.05}]")
say("")

# ================= S2 BREAK-UJ-FLAT =================
say("## S2 BREAK-UJ-FLAT（c47 の読みの第 2 の脚「UJ は vol 状態を変えない」を正しい λ で測る）")
say(f"- A_腕 = Ē_W3 − λ_pop·Ē_PRE（λ_pop は第 1 段 R2 の窓期別母集団 λ）・ET 日クラスタ bootstrap {NBOOT} 回")
say("| 窓 | 腕 | n | Ē_PRE | Ē_W3 | ΔE_W3（λ=1・c47b の読み） | **A_W3 = Ē_W3 − λ·Ē_PRE (t)** | vol 比 exp(A/2) |")
say("|---|---|---|---|---|---|---|---|")
S2R = {}
for lab, lo, hi in ERAS[:2]:
    lam = LAM_POP[lab]
    for arm in ["ANN_J", "UJ", "SJ"]:
        o = sub(lo, hi); o = o[(o.cls == arm) & np.isfinite(o[["E_PRE", "E_W3"]]).all(axis=1)]
        if len(o) < 10: continue
        days = o.day.to_numpy(); ud = np.unique(days)
        gi = {d: np.where(days == d)[0] for d in ud}
        A = o.E_W3.mean() - lam * o.E_PRE.mean()
        bb = np.empty(NBOOT)
        for q in range(NBOOT):
            pick = np.concatenate([gi[d] for d in rng.choice(ud, size=len(ud), replace=True)])
            s = o.iloc[pick]; bb[q] = s.E_W3.mean() - lam * s.E_PRE.mean()
        se = bb.std(ddof=1)
        say(f"| {lab} | {arm} | {len(o)} | {o.E_PRE.mean():+.3f} | {o.E_W3.mean():+.3f} | {(o.E_W3-o.E_PRE).mean():+.3f} | **{A:+.3f} (t {A/se:+.2f})** | {math.exp(A/2):.2f} |")
        S2R[(lab, arm)] = (A, se)
A_uj, se_uj = S2R[("外 2021-26H1", "UJ")]
s2_hit = (A_uj > 0) and (A_uj / se_uj >= 2)
say(f"- **S2 判定: {'☠BREAK-UJ-FLAT が当たった（UJ も状態を作っている＝「変えない」は推定器の産物）' if s2_hit else '★不発'}**"
    f" [外 UJ A_W3 {A_uj:+.3f}・t {A_uj/se_uj:+.2f}]")
say("")

# ================= S3 BREAK-NOSINGLE =================
say("## S3 BREAK-NOSINGLE（腕で λ が違う: contrast は評価点で変わるか）")
say("| 窓 | λ̂_ANN_J | λ̂_UJ | β_treat @ E_PRE=0（ANN の居場所） | β_treat @ E_PRE=Ē_UJ（UJ の居場所） | 差 | 交互作用 係数 (t) |")
say("|---|---|---|---|---|---|---|")
S3 = {}
for lab, lo, hi in ERAS[:2]:
    o = sub(lo, hi); o = o[o.cls.isin(["ANN_J", "UJ"]) & np.isfinite(o[["E_PRE", "E_W3"]]).all(axis=1)]
    c1 = 0.0; c2_ = o[o.cls == "UJ"].E_PRE.mean()
    b0, se0, cf0, _, _ = fit(o, "E_W3", "ANN_J", "UJ", extra=("E_PRE",), inter=("E_PRE", c1))
    b1, se1, cf1, _, _ = fit(o, "E_W3", "ANN_J", "UJ", extra=("E_PRE",), inter=("E_PRE", c2_))
    ia, iase = cf0.get("inter", (np.nan, np.nan))
    lam_a = [np.nan, np.nan]
    for j, arm in enumerate(["ANN_J", "UJ"]):
        s = o[o.cls == arm]; H = dummies(s.hr.to_numpy())
        X = np.column_stack([np.ones(len(s)), s.E_PRE.to_numpy(), H])
        bq, Vq, _ = ols_cluster(s.E_W3.to_numpy(), X, s.day.to_numpy()); lam_a[j] = bq[1]
    say(f"| {lab} | {lam_a[0]:+.3f} | {lam_a[1]:+.3f} | {f2(b0,se0)} | {f2(b1,se1)} | **{b0-b1:+.3f}** | {f2(ia,iase)} |")
    S3[lab] = abs(b0 - b1)
s3_hit = S3["外 2021-26H1"] >= 0.20
say(f"- **S3 判定: {'☠BREAK-NOSINGLE が当たった（評価点で contrast が変わる＝単一の DiD 値は定義されない）' if s3_hit else '★不発'}** [外 差 {S3['外 2021-26H1']:.3f}]")
say("")

# ================= S4 BREAK-FOLLOWON =================
say("## S4 BREAK-FOLLOWON（UJ の W3 窓に後続 5σ ジャンプが入る事象を除外）")
pos_ev = np.searchsorted(ts, EV.ts.to_numpy(np.int64)); pos_ev = np.clip(pos_ev, 0, N - 1)
has_follow = np.zeros(len(EV), bool)
for i_, p_ in enumerate(pos_ev):
    a, b = ts[min(p_ + 25, N - 1)], ts[min(p_ + 48, N - 1)]
    k = np.searchsorted(J5, a); has_follow[i_] = (k < len(J5)) and (J5[k] <= b)
EV["follow"] = has_follow
say("| 窓 | 腕 | 後続ジャンプ有り | 有りの Ē_W3 | 無しの Ē_W3 | 除外後 DiD_W3 (t) | 除外後 PRE 共変量 β (t) | 元 DiD |")
say("|---|---|---|---|---|---|---|---|")
S4 = {}
for lab, lo, hi in ERAS[:2]:
    o = sub(lo, hi); o = o[o.cls.isin(["ANN_J", "UJ"])]
    for arm in ["ANN_J", "UJ"]:
        s = o[o.cls == arm]
        say(f"| {lab} | {arm} | {int(s.follow.sum())}/{len(s)} | {s[s.follow].E_W3.mean():+.3f} | {s[~s.follow].E_W3.mean():+.3f} | — | — | — |")
    k = o[~o.follow]
    bd_, sed_, _, nt, nc = fit(k, "dW3", "ANN_J", "UJ")
    ba_, sea_, _, _, _ = fit(k, "E_W3", "ANN_J", "UJ", extra=("E_PRE",))
    b0_, se0_, _, _, _ = fit(o, "dW3", "ANN_J", "UJ")
    say(f"| {lab} | 除外後（n {nt}/{nc}） | — | — | — | **{f2(bd_,sed_)}** | {f2(ba_,sea_)} | {b0_:+.3f} |")
    S4[lab] = bd_
s4_hit = S4["外 2021-26H1"] >= 0.60
say(f"- **S4 判定: {'☠BREAK-FOLLOWON が当たった（除外すると DiD は大きくなる＝私の破壊は逆方向）' if s4_hit else '★不発'}** [外 除外後 {S4['外 2021-26H1']:+.3f}]")
say("")

# ================= S5 閾値感度（記述） =================
say("## S5（記述・判定外）第 1 段 R3 の閾値が結論を握った度合い")
o = sub(2021, 2026)
b_adj, se_adj, _, _, _ = fit(o, "E_W3", "ANN_J", "UJ", extra=("E_PRE",))
b_did, se_did, _, _, _ = fit(o, "dW3", "ANN_J", "UJ")
say(f"- 外 DiD_W3 {b_did:+.3f} (t {tt(b_did,se_did):+.2f}) → PRE 共変量 {b_adj:+.3f} (t {tt(b_adj,se_adj):+.2f})：**点推定は {100*(1-b_adj/b_did):.0f}% 減・t は {tt(b_did,se_did):.2f}→{tt(b_adj,se_adj):.2f}**")
say(f"- 私の R3 閾値は「|t|<1.5 ∨ β<0.5·0.492=0.246」。実測 t {tt(b_adj,se_adj):.2f}・β {b_adj:.3f} ＝ **どちらも閾値のすぐ外側**。")
say(f"- 閾値を「|t|<2（名目有意の喪失）」と書いていれば当たっていた（t {tt(b_adj,se_adj):.2f} < 2）。"
    f"「β<0.6·DiD={0.6*b_did:.3f}」でも当たっていた。**破壊規則の書き方が判定を握った**（反証 11-17 15:40 (ii)・21:30 (ii) と同じ再演）。")
say(f"- MDE（2se）{2*se_adj:.3f} > 点推定 {b_adj:.3f} ＝ **PRE 共変量版は検出力不足で『0 ではない』と言えない**（c47 の最重大反証 (ii) と同じ壁）。")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
