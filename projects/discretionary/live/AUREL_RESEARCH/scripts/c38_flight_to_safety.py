# -*- coding: utf-8 -*-
"""
[cycle38 研究レーン 2026-11-11] 【探索・参加者行動／ヘッジ需要（収益機会の源泉マップ §8 新行: 安全資産需要 flight-to-safety）】
金の最も引用される機構「安全資産（safe haven）」を、我々のデータ（US500 M5 bid・XAU M5 bid・既存キャッシュのみ）で
**事象ベース・日次**で在/外に分けて検証する。問いは 2 つ:
  H1（同時・構造の記述）: 米株の現物時間（09:30–16:00 ET）が大きく下げた日に、金は同じ時間に上がるか（Baur–Lucey 2010 の safe haven の定義＝極端な
     株安日の金リターン）。c20 は 5 分格子の同時相関の符号が 2014-19 負 → 2020+ 正と反転すると記述した。事象ベース（極端日）で同じか。
  H2（予測・流れの持続＝主）: 株安事象の**後**（16:00 ET D → 16:00 ET D+1）に金が無条件より上がるか＝ヘッジ需要の流れ（ETF 創設・機関の
     リバランス・個人の保険買い）が同時刻で完結せず翌セッションへ持ち越される（Baele et al. 2020 "Flights to safety" の持続・ETF フローの T+1）。
AI らしい角度: 「極端日」を**その時点で既知の trailing sd**（60 有効日）で定義（look-ahead なし）し、同じ大きさの**株高事象（UP）をボラ一致の対照**
として置く（株安日の後の金の動きが「荒い週の金のドリフト」の別名でないことを対照で潰す）。入口フィルタではない・本番とは独立の市場記述。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/US500_m5_close.npz（2012-01〜2026-06-09・bid）・data/macro/XAU_m5_close.npz（bid）・data/refute_c4_scan_paths_2010_2026.json（ゲート ㉛）。
  既存キャッシュのみ・scan 無し・M5 読込なし・MT5 無し・外部通信無し。読込後に min/max 時刻（⑩）・曜日別 flat 比率（⑪）を印字。
価格の時計: c22 と同じ P(T) = ts == T−300 の足の close（格子の穴は NaN・⑫）。取引日 D = ET 現地の月〜金（暦）。
株の事象（F_t 可測）: r_eq(D) = ln P_eq(16:00 D) − ln P_eq(09:30 D)（bp）。有効 = 有限 ∧ ≠0。sd60(D) = D より前の 60 有効日の r_eq の標本 sd（D を含まない）。
  DOWN(D) = r_eq < −θ·sd60／UP(D) = r_eq > +θ·sd60／REST = それ以外（sd60 有限）。主 θ = 1.5・感度 θ = 2.0（記述）。
金の窓（bp・XAU bid）: SAME = ln Pg(16:00 D) − ln Pg(09:30 D)／NEXT = ln Pg(16:00 D+1) − ln Pg(16:00 D)（D+1 = 次の暦平日・主）／
  NEXT_ON = 16:00 D → 09:30 D+1／NEXT_CASH = 09:30 → 16:00 D+1／NEXT_k = 16:00 D → 16:00 D+k（k=2..5・記述・流れの水平線）。
  金の窓が**厳密 0**（米国祝日の stale・㉒）または NaN の日は除外し、窓×期間の厳密 0 比率を印字（>20% は判定不可）。
窓: 在 2012-20／外 2021-26H1／近年 2024-26H1（D2・窓別・16 年一括は使わない）。判定は在で決め外で確認。
統計: 群平均の差 Δ = mean(事象) − mean(対照)・se = √(se²+se²)・Welch t・MDE = 2se。
  置換帰無（⑨）: 事象ラベルを**週循環シフト**（平日索引を 5k ずらす・k ∈ [1, 窓の週数−1]・2000 回・窓内で循環）→ 片側 p（予測方向）と両側 p。
  クラスタ（2020-03 等の連続事象日）はシフトで保存される。
判定（Bonferroni(2)・名目 0.025）:
  H1 PASS（safe haven は両窓で成立）= Δ_same(DOWN−UP) >0 ∧ 在 t≥2 ∧ 外 同符号 t≥1.5。予測（c20 から）: 在 >0・外 <0（符号反転）＝PASS しない見込みを先に書く。
  H2 PASS（流れの持続）= Δ_next(DOWN−REST) >0 ∧ 在 t≥2 ∧ 置換 p<0.025 ∧ 外 同符号 t≥1.5。副（ボラ一致）: Δ_next(DOWN−UP) >0 を併記（DOWN−REST が
     立っても DOWN−UP が立たなければ「荒い日の後の金の正」＝safe haven 固有ではない）。
決着可能性（㉝・数字を見る前）: 金 NEXT の日次 sd ≈100 bp・θ=1.5 で事象 ≈7% → 在 ≈150 事象・se ≈8 bp・MDE ≈17 bp／外 ≈90・MDE ≈22 bp。
  文献級（10〜30 bp）の中央 +15 bp なら 在 期待 t ≈1.8・外 ≈1.4＝**境界（決着は在∧外の同符号で補う）**。θ=2.0 は事象半分＝MDE 1.4 倍。
陽性対照: DOWN 日の金 NEXT に +15 bp を注入 → Δ の t が ≥1.5 増える（検出力）。負の対照: 同じ事象定義を US500 自身の NEXT CASH に適用（株の反転/継続・記述）。
ゲート ㉛（本番接続）: scan 本（refute_c4）のうち建玉が (16:00 ET D, 16:00 ET D+1] に入る本を D の事象で分け、在 2012-20 の Δμ（R* = R + ft·決着・
  DOWN−REST・Welch t）・Δx（pp）・x0 look-ahead 対照を印字。在 |Δμ| <0.048R → 「決着不能・外は走らせない」。
事前の最重大反証: (1) 事象日は危機週に群がる（2020-03・2022）→ 有効 n は名目より小さい（NW・週シフト置換で読む）。(2) 事象期の金のドリフトは
  レジーム固有（2020 急騰・2022 利上げで下落）→ UP 対照（同じボラ状態）で潰す。(3) bid のみ・Dukascopy 1 社。(4) ETF フローは米国現物時間に集中する
  ので「翌日 CASH」に局在するはず（NEXT_ON と NEXT_CASH を分けて印字）。(5) 2012-13 の US500 は夜間 stale（c22）だが CASH は無事（端点の厳密 0 比率を印字）。
(6) コスト: 1 日保有・往復 0.16 USD ＝ 0.4〜1.0 bp＋swap（未記録）→ 文献級なら受け取れる桁だが H2 が立たなければ問いにしない。
昇格候補・入口/出口規則の提案ではない。seed 20261111。
"""
import os, time, math, json
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c38_flight_to_safety_result.md"); L = []
NY = "America/New_York"; SEED = 20261111; rng = np.random.default_rng(SEED)
THETA = 1.5; THETA2 = 2.0; NPERM = 2000; SD_N = 60
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle38] 安全資産需要（flight-to-safety）: 米株の極端日の同時・翌セッションの金 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c38_flight_to_safety.py)")

WD = ['月','火','水','木','金','土','日']
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    r = np.diff(np.log(cl)); fl = np.r_[False, r == 0]; wd = t.weekday.to_numpy()
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%・曜日別 " + " ".join(f"{WD[w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
    return ts, cl

def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out

ts_e, cl_e = load("US500"); ts_g, cl_g = load("XAU")
dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy()
Pe = lambda h, m, off=0: price_at(ts_e, cl_e, epoch_et(dates, h, m, off))
lg = np.log
# gold price at 16:00 / 09:30 on weekday index i+k : use shifted date arrays
def Pg_idx(h, m, k):
    """gold price at h:m ET on the weekday k positions after each date (NaN past end)."""
    out = np.full(N, np.nan)
    if k >= N: return out
    d2 = dates[k:]; v = price_at(ts_g, cl_g, epoch_et(d2, h, m)); out[:N - k] = v; return out

r_eq = (lg(Pe(16, 0)) - lg(Pe(9, 30))) * 1e4
valid_eq = np.isfinite(r_eq) & (r_eq != 0)
# trailing sd60 over prior valid days (excluding D)
s = pd.Series(np.where(valid_eq, r_eq, np.nan))
sd60 = s.dropna().shift(1).rolling(SD_N).std().reindex(s.index).to_numpy()
# gold windows
g1600 = Pg_idx(16, 0, 0); g0930 = Pg_idx(9, 30, 0); g1600n = Pg_idx(16, 0, 1); g0930n = Pg_idx(9, 30, 1)
G = {}
G["SAME"] = (lg(g1600) - lg(g0930)) * 1e4
G["NEXT"] = (lg(g1600n) - lg(g1600)) * 1e4
G["NEXT_ON"] = (lg(g0930n) - lg(g1600)) * 1e4
G["NEXT_CASH"] = (lg(g1600n) - lg(g0930n)) * 1e4
for k in range(2, 6): G[f"NEXT_{k}"] = (lg(Pg_idx(16, 0, k)) - lg(g1600)) * 1e4
# equity own next cash (negative control)
E_next_cash = np.full(N, np.nan); E_next_cash[:N - 1] = r_eq[1:]

ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
base = valid_eq & np.isfinite(sd60)
say(f"\n- 取引日候補 {N}・株 CASH 有効日 {valid_eq.sum()}・sd60 有限 {base.sum()}・sd60 中央値 {np.nanmedian(sd60[base]):.0f} bp・r_eq sd {np.nanstd(r_eq[base]):.0f} bp")
say("- 金の窓の厳密 0 比率（㉒・base 日）: " + "・".join(f"{k} {np.mean(np.isfinite(G[k][base]) & (G[k][base]==0))*100:.1f}%/NaN {np.mean(~np.isfinite(G[k][base]))*100:.1f}%" for k in ["SAME","NEXT","NEXT_ON","NEXT_CASH","NEXT_5"]))
say(f"- 株 CASH 端点の厳密 0（年別・候補日中）: " + " ".join(f"{y}:{np.mean((r_eq[yr==y]==0)|~np.isfinite(r_eq[yr==y]))*100:.0f}%" for y in range(2012, 2027)))

def grp(x, m):
    x = x[m]; x = x[np.isfinite(x) & (x != 0)]; n = len(x)
    if n < 5: return dict(n=n, mean=np.nan, se=np.nan, med=np.nan, pos=np.nan)
    return dict(n=n, mean=x.mean(), se=x.std(ddof=1) / math.sqrt(n), med=np.median(x), pos=(x > 0).mean())
def delta(x, ma, mb):
    a, b = grp(x, ma), grp(x, mb)
    if a["n"] < 5 or b["n"] < 5: return dict(d=np.nan, se=np.nan, t=np.nan, a=a, b=b)
    se = math.sqrt(a["se"] ** 2 + b["se"] ** 2); return dict(d=a["mean"] - b["mean"], se=se, t=(a["mean"] - b["mean"]) / se, a=a, b=b)
def f(d, mde=True):
    if not np.isfinite(d["d"]): return f"—(n{d['a']['n']}/{d['b']['n']})"
    return f"{d['d']:+.1f} bp (t{d['t']:+.2f}" + (f", MDE {2*d['se']:.1f}" if mde else "") + f", n{d['a']['n']}/{d['b']['n']})"

def events(theta, m):
    dn = m & (r_eq < -theta * sd60); up = m & (r_eq > theta * sd60); rest = m & ~dn & ~up; return dn, up, rest

def perm_p(x, m, ev, obs, nperm=NPERM):
    """week-cyclic shift of event labels within window m (index positions of weekdays); returns one-sided (>= obs) and two-sided p."""
    idx = np.where(m)[0]; L_ = len(idx); lab = ev[idx]; xv = x[idx]; ok = np.isfinite(xv) & (xv != 0)
    nweeks = L_ // 5; ks = rng.integers(1, max(2, nweeks), size=nperm); out = np.empty(nperm)
    for j, k in enumerate(ks):
        sh = np.roll(lab, 5 * int(k)); a = xv[sh & ok]; b = xv[~sh & ok]
        out[j] = a.mean() - b.mean() if len(a) >= 5 and len(b) >= 5 else np.nan
    out = out[np.isfinite(out)]
    return (out >= obs).mean(), (np.abs(out) >= abs(obs)).mean(), np.std(out)

RES = {}
for theta, tag in [(THETA, "主 θ=1.5"), (THETA2, "感度 θ=2.0")]:
    say(f"\n## {tag}")
    say("- 事象数（年別 DOWN/UP）: " + " ".join(f"{y}:{int((events(theta, base)[0] & (yr==y)).sum())}/{int((events(theta, base)[1] & (yr==y)).sum())}" for y in range(2012, 2027)))
    say("\n| 期間 | n DOWN/UP/REST | r_eq DOWN 平均 | H1 SAME DOWN−UP | SAME DOWN−REST | H2 NEXT DOWN−REST | NEXT DOWN−UP | NEXT_ON DOWN−REST | NEXT_CASH DOWN−REST | US500 自身 NEXT CASH DOWN−REST |")
    say("|---|---|---|---|---|---|---|---|---|---|")
    for lab, lo, hi in ERAS:
        m = base & (yr >= lo) & (yr <= hi); dn, up, rest = events(theta, m)
        d_same_du = delta(G["SAME"], dn, up); d_same_dr = delta(G["SAME"], dn, rest)
        d_next_dr = delta(G["NEXT"], dn, rest); d_next_du = delta(G["NEXT"], dn, up)
        d_on = delta(G["NEXT_ON"], dn, rest); d_cash = delta(G["NEXT_CASH"], dn, rest); d_eq = delta(E_next_cash, dn, rest)
        RES[(theta, lab)] = dict(dn=dn, up=up, rest=rest, m=m, same_du=d_same_du, next_dr=d_next_dr, next_du=d_next_du)
        say(f"| {lab} | {dn.sum()}/{up.sum()}/{rest.sum()} | {np.nanmean(r_eq[dn]):+.0f} bp | {f(d_same_du)} | {f(d_same_dr, False)} | {f(d_next_dr)} | {f(d_next_du)} | {f(d_on, False)} | {f(d_cash, False)} | {f(d_eq, False)} |")
    # levels (unconditional) and horizons
    say("\n| 期間 | 金 SAME 無条件 | 金 NEXT 無条件 | DOWN 日 SAME 平均 | UP 日 SAME 平均 | DOWN 日 NEXT 平均（正の日%） | NEXT_2 DOWN−REST | NEXT_3 | NEXT_5 |")
    say("|---|---|---|---|---|---|---|---|---|")
    for lab, lo, hi in ERAS:
        R = RES[(theta, lab)]; dn, up, rest, m = R["dn"], R["up"], R["rest"], R["m"]
        gs, gn = grp(G["SAME"], m), grp(G["NEXT"], m); a, b, c = grp(G["SAME"], dn), grp(G["SAME"], up), grp(G["NEXT"], dn)
        hz = [delta(G[f"NEXT_{k}"], dn, rest) for k in (2, 3, 5)]
        say(f"| {lab} | {gs['mean']:+.1f} (se {gs['se']:.1f}) | {gn['mean']:+.1f} (se {gn['se']:.1f}) | {a['mean']:+.1f} (t{a['mean']/a['se']:+.1f}) | {b['mean']:+.1f} (t{b['mean']/b['se']:+.1f}) | {c['mean']:+.1f} ({c['pos']*100:.0f}%) | " + " | ".join(f"{h['d']:+.1f} (t{h['t']:+.1f})" for h in hz) + " |")

# permutation + positive control for main θ
say("\n## 置換帰無（週循環シフト・2000 回）と陽性対照（主 θ=1.5）")
for lab, lo, hi in ERAS:
    R = RES[(THETA, lab)]; m, dn, rest = R["m"], R["dn"], R["rest"]
    # H2 DOWN - REST : treat UP as part of "others" for the shift test? keep REST definition: shifted labels vs complement
    obs = R["next_dr"]["d"]; p1, p2, sdp = perm_p(G["NEXT"], m, dn, obs)
    obs1 = R["same_du"]["d"]
    # positive control: inject +15 bp on DOWN NEXT
    xinj = G["NEXT"].copy(); xinj[dn] += 15.0; dinj = delta(xinj, dn, rest)
    say(f"- {lab}: H2 Δ_next(DOWN−補集合) 観測 {obs:+.1f} bp・置換 片側 p {p1:.3f}・両側 p {p2:.3f}・帰無 sd {sdp:.1f} bp（名目 se {R['next_dr']['se']:.1f}）／陽性対照 +15 bp 注入 → t {R['next_dr']['t']:+.2f} → {dinj['t']:+.2f}")

# H1 sign regime by year (descriptive)
say("\n## 記述: 年別 SAME DOWN−UP（θ=1.5・符号レジーム）")
say("| 年 | n DOWN/UP | SAME DOWN−UP | NEXT DOWN−REST |"); say("|---|---|---|---|")
for y in range(2012, 2027):
    m = base & (yr == y); dn, up, rest = events(THETA, m)
    a = delta(G["SAME"], dn, up); b = delta(G["NEXT"], dn, rest)
    say(f"| {y} | {dn.sum()}/{up.sum()} | {a['d']:+.1f} (t{a['t']:+.1f}) | {b['d']:+.1f} (t{b['t']:+.1f}) |" if np.isfinite(a["d"]) and np.isfinite(b["d"]) else f"| {y} | {dn.sum()}/{up.sum()} | — | — |")

# ---------- gate ㉛: production connection ----------
say("\n## ゲート ㉛（本番接続・在 2012-20 のみ印字）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["ft"] = FT / tr["risk"]
tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]; tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = (tr["exit"] == "TP").astype(float) - tr["q"]
t16 = epoch_et(dates, 16, 0)  # epoch of 16:00 ET on each weekday
et_ = tr["entry_time"].to_numpy(float)
pos = np.searchsorted(t16, et_, side="left") - 1   # D such that t16[D] < entry <= t16[D+1]
ok = (pos >= 0) & (pos < N - 1); tr["D"] = np.where(ok, pos, -1)
dn_all, up_all, rest_all = events(THETA, base)
tr["ev"] = np.where(tr["D"] >= 0, np.where(dn_all[np.clip(tr["D"], 0, N - 1)], "DOWN", np.where(up_all[np.clip(tr["D"], 0, N - 1)], "UP", np.where(base[np.clip(tr["D"], 0, N - 1)], "REST", "NA"))), "NA")
ins = tr[(tr["year"] >= 2012) & (tr["year"] <= 2020) & (tr["ev"] != "NA")]
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); d_ = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d_, d_ / se, se
A, B = ins[ins.ev == "DOWN"], ins[ins.ev == "REST"]
dm, tm, sem = welch(A.Rs, B.Rs); dx, tx, _ = welch(A[A.dec].x, B[B.dec].x); d0, t0, _ = welch(A.x0, B.x0)
AU = ins[ins.ev == "UP"]; dmu, tmu, _ = welch(AU.Rs, B.Rs)
say(f"- 在 2012-20 本 {len(ins)}（DOWN 翌セッション建玉 {len(A)}／UP {len(AU)}／REST {len(B)}・付与率 {(tr.ev!='NA').mean()*100:.1f}%）")
say(f"- DOWN−REST: Δμ(R*) **{dm:+.3f}R (t {tm:+.2f}, se {sem:.3f}, MDE {2*sem:.3f})**・Δx {dx*100:+.2f} pp (t {tx:+.2f})・look-ahead 対照 x0 Δ {d0:+.3f} (t {t0:+.2f})／UP−REST Δμ {dmu:+.3f}R (t {tmu:+.2f})")
gate = "通過（外を印字）" if abs(dm) >= 0.048 else "**不通過（在 |Δμ| <0.048R → 決着不能・外は走らせない）**"
say(f"- ゲート ㉛: {gate}")
if abs(dm) >= 0.048:
    for lab, lo, hi in ERAS[1:]:
        o = tr[(tr["year"] >= lo) & (tr["year"] <= hi) & (tr["ev"] != "NA")]
        a_, b_ = o[o.ev == "DOWN"], o[o.ev == "REST"]
        if len(a_) >= 20: dm2, tm2, se2 = welch(a_.Rs, b_.Rs); say(f"  - {lab}: Δμ {dm2:+.3f}R (t {tm2:+.2f}, n {len(a_)}/{len(b_)})")

# ---------- verdict ----------
say("\n## 判定（事前固定の規則で機械的に）")
i1, o1 = RES[(THETA, "在 2012-20")]["same_du"], RES[(THETA, "外 2021-26H1")]["same_du"]
h1 = (i1["d"] > 0) and (i1["t"] >= 2) and (o1["d"] > 0) and (o1["t"] >= 1.5)
say(f"- H1（safe haven 同時・両窓）: 在 {f(i1)}／外 {f(o1)} → **{'PASS' if h1 else 'null（符号反転または MDE 以下）'}**")
i2, o2 = RES[(THETA, "在 2012-20")]["next_dr"], RES[(THETA, "外 2021-26H1")]["next_dr"]
obs = i2["d"]; p1, _, _ = perm_p(G["NEXT"], RES[(THETA, "在 2012-20")]["m"], RES[(THETA, "在 2012-20")]["dn"], obs)
h2 = (i2["d"] > 0) and (i2["t"] >= 2) and (p1 < 0.025) and (o2["d"] > 0) and (o2["t"] >= 1.5)
i2u, o2u = RES[(THETA, "在 2012-20")]["next_du"], RES[(THETA, "外 2021-26H1")]["next_du"]
say(f"- H2（流れの持続 NEXT DOWN−REST）: 在 {f(i2)} 置換 p {p1:.3f}／外 {f(o2)}／副 DOWN−UP 在 {f(i2u)}・外 {f(o2u)} → **{'PASS' if h2 else 'null'}**")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
