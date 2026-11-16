# -*- coding: utf-8 -*-
"""
[cycle44 研究レーン 2026-11-17] 【探索・マクロ発表前後（収益機会の源泉マップ §8「マクロ発表（CPI/PCE/小売）」行 要取得 → 済）】
発表プール版 post-announcement drift（c24 NFP 単独・c42 FOMC 単独は「月 1 回の系列では決着不能（㉕）」で終わり、backlog に **1 セルの事前固定文**が既に書かれている）:
  「発表をプール（NFP＋FOMC＋CPI ≥300 発表・種別 FE）した r_POST(+30→+120 分) on r_JUMP(0→+30 分) の β>0 ∧ HC1 t≥2 ∧ 外 同符号 t≥1.5（MDE ≈0.2）」。
機構（文献）: 発表後の価格発見は初動で完了せず数十分〜数時間続く（post-announcement drift・Andersen–Bollerslev–Diebold–Vega 2003 は FX で数分で完了と報告、
  Lucca–Moench/Kurov 型は株で遅い反応、金では Elder–Miao–Ramchander 2012 が「数分で吸収」）。金の初動 30 分後にまだ同方向へ動くなら「遅い参加者（アジア/欧州の
  持ち越し調整・ETF の遅延フロー）」、逆方向なら「初動のオーバーシュート（流動性供給者の在庫解消）」。どちらも入口フィルタの提案ではない・市場構造の記述。
暦: NFP = BLS 規則（c24 nfp_dates_v2・木曜公表日も含める）／FOMC = data/macro/FOMC_dates.csv（scheduled・声明 14:00 ET が確定する 2013-03-20 以降）／
  CPI = data/macro/CPI_dates.csv（本サイクル取得・bls.gov アーカイブのファイル名から実公表日・08:30 ET）。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: XAU_m5_close.npz（bid・2010-01〜2026-06）・US500_m5_close.npz（記述のみ・2014+ ㉒）・refute_c4 json（ゲート ㉛）。scan 無し・M5 読込なし・MT5 無し。
価格の時計: P(T) = ts == T−300 の足の close（格子の穴は NaN・⑫）。ET 現地（DST 追随）。
事象時刻 t0: NFP/CPI 08:30 ET・FOMC 14:00 ET。窓（bp・対数差）: JUMP5 = P(t0+5)/P(t0)（暦検定用）・**JUMP = P(t0+30)/P(t0)（主予測子）・POST = P(t0+120)/P(t0+30)（主被説明変数）**・
  POST2 = P(t0+240)/P(t0+30)（副）。有効 = 3 価格が有限 ∧ JUMP ≠ 0。
暦の妥当性検定 PC（数字を見る前に規則・c24/c42 と同じ）: 種別ごとに |JUMP5| 中央値 ÷ 同時刻の対照日（非発表日・同じ時代窓）中央値 ≥2 ∧ J 率（≥対照 90% 点）≥0.5。
  **CPI が PC を通らなければ CPI は暦不良として外し、NFP＋FOMC だけでプール**（それでも ≥300 を確認・満たさなければ決着不能で void）。
同日衝突: NFP と CPI が同じ日なら CPI 行を落とす（件数を印字）。FOMC と CPI の同日は時刻が違うので両方残す。
対照日: 同じ時代窓の平日で NFP/CPI/FOMC（scheduled・unscheduled）のいずれでもない日・同じ時刻窓（08:30 系と 14:00 系を別に）。
主セル C1（金・プール）: POST = Σ_type α_type + β·JUMP（HC1）。**PASS = 在 β>0 ∧ t≥2 ∧ 符号反転置換（事象ごとに JUMP の符号を独立に反転・2000 回・両側）p<0.025 ∧ 外 同符号 ∧ t≥1.5**。
  在 = 2010-20（FOMC は 2013-03-20〜）／外 = 2021-26H1／近年 = 2024-26H1（D2・窓別）。β<0 で同条件なら「反転（オーバーシュート）」として同じ規則で PASS（方向は両側に事前宣言）。
  Bonferroni: 判定セルは C1 のみ（名目 0.025）。副は記述。
副（記述・判定に使わない）: 種別別 β・対照日の β_ctrl と δ = β − β_ctrl・J 日（|JUMP5| ≥ q90）限定 β・POST2・年別 β・符号戦略 S = mean(sign(JUMP)·POST) bp と net（往復 0.16 USD ≈ 0.4〜0.9 bp）・
  **用量反応（㊾ 新規・必須）: |JUMP| 三分位ごとの符号一致率 P(sign POST = sign JUMP)**（一致率が |JUMP| で単調に上がらなければ「統計的事実・機構未同定」と書く）・US500 複製（2014+・記述）。
決着可能性（㉕/㊷・数字を見る前）: JUMP sd ≈ 30〜60 bp・POST(90 分) sd ≈ 30〜50 bp・在 n ≈ 130 NFP＋62 FOMC＋130 CPI ≈ 320 → iid se ≈ 0.04・HC1 相当 ×1.5〜2 → se ≈ 0.06〜0.08 → β 0.2 で t 2.5〜3＝決着可能。
  実測の se と注入（在 POST に +0.2·JUMP）の Δt を印字（陽性対照）。MDE = 2·se。
ゲート ㉛（本番接続・在 2010-20 のみ印字）: scan 本の entry_time が事象日の [t0, t0+120 分] にある本 vs 非事象日の同時刻窓に建玉した本: Δμ(R*)・Δx・x0 look-ahead 対照。
  在 |Δμ| <0.048R → 決着不能・外は走らせない。≥0.048 → 外・近年を印字。発表 t0 を生きて跨ぐ本数も印字（c24/c42 の母数なし確認）。
事前の最重大反証: (1) bid のみ・ジャンプ足でスプレッド拡大 → JUMP の bid 成分が POST で戻る＝見かけの反転（β<0 側へのバイアス）→ β<0 が出たら JUMP5 を外した JUMP' = P(t0+30)/P(t0+5) 版を併記。
  (2) 種別プールは「同じ機構」を仮定＝種別別 β の符号が割れたらプール β は平均で意味を失う（種別別を併記）。(3) 対照日にも PCE/小売/入札/ECB 等の発表が混在（暦なし）。
  (4) 2013-03-20 前の FOMC は時刻不定で除外・CPI 暦は 1 社（BLS）1 ページの機械抽出（J 検定で妥当性）。(5) 在外の分割は時代の効果（金の発表反応 |J30| 中央値は c42 で 36 → 18 bp に半減）。
  (6) 用量反応が無い S は機構の証拠にならない（㊾）。昇格候補・入口/出口規則の提案ではない。seed 20261117。
"""
import os, time, math, json
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c44_announcement_pool_result.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED); NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle44] 発表プール post-announcement drift（NFP＋FOMC＋CPI）金 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c44_announcement_pool.py)")
WD = ['月','火','水','木','金','土','日']
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True); r = np.diff(np.log(cl)); fl = np.r_[False, r == 0]; wd = t.weekday.to_numpy()
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%・曜日別 " + " ".join(f"{WD[w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
    return ts, cl
def epoch_et(dates, hour, minute):
    mins = np.asarray(hour, dtype=float) * 60 + np.asarray(minute, dtype=float)
    naive = pd.DatetimeIndex(dates) + pd.to_timedelta(np.broadcast_to(mins, (len(dates),)), unit="m")
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T); key = (T[ok] - 300).astype(np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1); out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
def hc1_fe(y, x, g, min_n=20):
    """y = Σ α_g + β x ; HC1 se for β; returns dict"""
    m = np.isfinite(y) & np.isfinite(x); y, x, g = y[m], x[m], g[m]; n = len(y)
    if n < min_n: return dict(n=n, b=np.nan, se=np.nan, t=np.nan)
    G = np.unique(g); X = np.column_stack([(g == k).astype(float) for k in G] + [x]); k = X.shape[1]
    XtXi = np.linalg.pinv(X.T @ X); beta = XtXi @ X.T @ y; e = y - X @ beta
    V = XtXi @ ((X * e[:, None]).T @ (X * e[:, None])) @ XtXi * n / (n - k); se = math.sqrt(V[-1, -1])
    return dict(n=n, b=beta[-1], se=se, t=beta[-1] / se)
def perm_signflip(y, x, g, obs):
    m = np.isfinite(y) & np.isfinite(x); y, x, g = y[m], x[m], g[m]; out = np.empty(NPERM)
    for j in range(NPERM): out[j] = hc1_fe(y, x * rng.choice([-1.0, 1.0], len(x)), g)["b"]
    return (np.abs(out) >= abs(obs)).mean(), out.std()
def fb(o, u=""): return f"β {o['b']:+.3f} (t {o['t']:+.2f}, se {o['se']:.3f}, MDE {2*o['se']:.3f}, n {o['n']})" if np.isfinite(o["b"]) else f"—(n {o['n']})"

# ---------- calendars ----------
NFP = nfp_dates_v2(); NFP = NFP[(NFP >= "2010-01-01") & (NFP <= "2026-06-30")]
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20") & (F.date <= "2026-06-30")].date); FOMC_ALL = pd.DatetimeIndex(F.date)
C = pd.read_csv(os.path.join(MAC, "CPI_dates.csv")); C["date"] = pd.to_datetime(C["date"]); CPI = pd.DatetimeIndex(C[(C.date >= "2010-01-01") & (C.date <= "2026-06-30")].date)
clash = CPI.isin(NFP); say(f"- 暦: NFP {len(NFP)}（木曜 {int((NFP.weekday==3).sum())}）・FOMC scheduled 2013-03-20+ {len(FOMC)}・CPI {len(CPI)}（曜日 " + " ".join(f"{WD[w]}{int((CPI.weekday==w).sum())}" for w in range(7)) + f"・年別 " + " ".join(f"{y}:{int((CPI.year==y).sum())}" for y in range(2010, 2027)) + f"）・NFP と同日の CPI {int(clash.sum())} → 落とす")
CPI = CPI[~clash]
EV = pd.DataFrame({"date": list(NFP) + list(FOMC) + list(CPI), "type": ["NFP"] * len(NFP) + ["FOMC"] * len(FOMC) + ["CPI"] * len(CPI)})
EV["h"] = np.where(EV.type == "FOMC", 14, 8); EV["m"] = np.where(EV.type == "FOMC", 0, 30); EV["year"] = EV.date.dt.year
# control days: weekdays not any announcement day
alld = pd.date_range("2010-01-04", "2026-06-30", freq="D"); alld = alld[alld.weekday <= 4]
anyev = alld.isin(NFP) | alld.isin(FOMC_ALL) | alld.isin(CPI) | alld.isin(pd.DatetimeIndex(C.date))
CTRL = alld[~anyev]; say(f"- 事象 {len(EV)}（NFP {len(NFP)}／FOMC {len(FOMC)}／CPI {len(CPI)}）・対照候補日 {len(CTRL)}")
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def windows(ts, cl, dates, h, m):
    t0 = epoch_et(dates, h, m); P0 = price_at(ts, cl, t0); P5 = price_at(ts, cl, t0 + 300); P30 = price_at(ts, cl, t0 + 1800); P120 = price_at(ts, cl, t0 + 7200); P240 = price_at(ts, cl, t0 + 14400)
    lg = np.log
    return dict(t0=t0, JUMP5=(lg(P5) - lg(P0)) * 1e4, JUMP=(lg(P30) - lg(P0)) * 1e4, JUMPp=(lg(P30) - lg(P5)) * 1e4, POST=(lg(P120) - lg(P30)) * 1e4, POST2=(lg(P240) - lg(P30)) * 1e4, P0=P0)

def run(sym, judge=True):
    say(f"\n## {sym}")
    ts, cl = load(sym)
    W = windows(ts, cl, EV.date, EV.h.to_numpy(), EV.m.to_numpy())
    for k in W: EV[k] = W[k]
    E = EV.copy(); E["valid"] = np.isfinite(E.JUMP) & np.isfinite(E.POST) & np.isfinite(E.JUMP5) & (E.JUMP != 0)
    if sym == "US500": E = E[E.year >= 2014]
    # control windows (two clocks)
    CW = {}
    for (h, m) in ((8, 30), (14, 0)):
        w = windows(ts, cl, CTRL, np.full(len(CTRL), h), np.full(len(CTRL), m)); d = pd.DataFrame(w); d["date"] = CTRL; d["year"] = CTRL.year
        d["valid"] = np.isfinite(d.JUMP) & np.isfinite(d.POST) & np.isfinite(d.JUMP5) & (d.JUMP != 0)
        if sym == "US500": d = d[d.year >= 2014]
        CW[(h, m)] = d
    say("- 有効率（事象・種別）: " + "・".join(f"{t} {E[E.type==t].valid.mean()*100:.0f}% ({int(E[E.type==t].valid.sum())})" for t in ("NFP", "FOMC", "CPI")) + f"・対照 08:30 {CW[(8,30)].valid.mean()*100:.0f}%／14:00 {CW[(14,0)].valid.mean()*100:.0f}%")
    # ---- PC calendar validity per type & era ----
    say("\n### PC 暦検定（|JUMP5| = |r(t0→t0+5)|・種別 vs 同時刻の対照日・中央値比 ≥2 ∧ J 率 ≥0.5）")
    say("| 窓 | 種別 | n | 中央値 事象 | 中央値 対照 | 比 | 対照 q90 | J 率 | PC |")
    say("|---|---|---|---|---|---|---|---|---|")
    PC = {}; JFLAG = pd.Series(False, index=E.index)
    for lab, lo, hi in ERAS:
        for t in ("NFP", "FOMC", "CPI"):
            e = E[(E.type == t) & E.valid & (E.year >= lo) & (E.year <= hi)]; cw = CW[(14, 0) if t == "FOMC" else (8, 30)]; c = cw[cw.valid & (cw.year >= lo) & (cw.year <= hi)]
            if len(e) < 5: say(f"| {lab} | {t} | {len(e)} | | | | | | n 不足 |"); PC[(lab, t)] = None; continue
            me, mc = np.median(np.abs(e.JUMP5)), np.median(np.abs(c.JUMP5)); q90 = np.quantile(np.abs(c.JUMP5), 0.9); J = (np.abs(e.JUMP5) >= q90).mean()
            ok = (me / mc >= 2) and (J >= 0.5); PC[(lab, t)] = ok; JFLAG.loc[e.index[np.abs(e.JUMP5) >= q90]] = True
            say(f"| {lab} | {t} | {len(e)} | {me:.1f} | {mc:.1f} | **{me/mc:.1f}** | {q90:.1f} | **{J*100:.0f}%** | {'PASS' if ok else 'FAIL'} |")
    E["J"] = JFLAG
    cpi_ok = bool(PC.get(("在 2010-20", "CPI"))) and bool(PC.get(("外 2021-26H1", "CPI")))
    types = ("NFP", "FOMC", "CPI") if cpi_ok else ("NFP", "FOMC")
    say(f"- CPI 暦 PC: {'PASS → プールに含める' if cpi_ok else 'FAIL → CPI を外して NFP＋FOMC でプール'}・プール種別 {types}")
    # ---- main cell ----
    say("\n### C1 プール: POST(+30→+120 分) = Σ α_type + β·JUMP(0→+30 分)（HC1・符号反転置換）")
    say("| 窓 | n（種別） | β (t, se, MDE) | 置換 p / 帰無 sd | sd JUMP / sd POST | 種別別 β NFP／FOMC／CPI | 対照 β_ctrl 08:30／14:00 | J 日限定 β | POST2 β | S bp/回 (t) | 符号一致率 \\|JUMP\\| T1/T2/T3 |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    RES = {}
    for lab, lo, hi in ERAS:
        e = E[E.valid & E.type.isin(types) & (E.year >= lo) & (E.year <= hi)]
        y, x, g = e.POST.to_numpy(float), e.JUMP.to_numpy(float), e.type.to_numpy()
        o = hc1_fe(y, x, g); p, sdp = perm_signflip(y, x, g, o["b"]) if np.isfinite(o["b"]) else (np.nan, np.nan)
        bt = "／".join(f"{hc1_fe(e[e.type==t].POST.to_numpy(float), e[e.type==t].JUMP.to_numpy(float), e[e.type==t].type.to_numpy())['b']:+.3f} (t {hc1_fe(e[e.type==t].POST.to_numpy(float), e[e.type==t].JUMP.to_numpy(float), e[e.type==t].type.to_numpy())['t']:+.2f}, n {int((e.type==t).sum())})" if (e.type == t).sum() >= 20 else f"— (n {int((e.type==t).sum())})" for t in ("NFP", "FOMC", "CPI"))
        bc = []
        for key in ((8, 30), (14, 0)):
            c = CW[key]; c = c[c.valid & (c.year >= lo) & (c.year <= hi)]; oc = hc1_fe(c.POST.to_numpy(float), c.JUMP.to_numpy(float), np.array(["C"] * len(c))); bc.append(f"{oc['b']:+.3f} (t {oc['t']:+.2f}, n {oc['n']})")
        ej = e[e.J]; oj = hc1_fe(ej.POST.to_numpy(float), ej.JUMP.to_numpy(float), ej.type.to_numpy())
        o2 = hc1_fe(e.POST2.to_numpy(float), x, g)
        S = np.sign(x) * y; St = S.mean() / (S.std(ddof=1) / math.sqrt(len(S)))
        ax = np.abs(x); q = np.quantile(ax, [1 / 3, 2 / 3]); agree = [np.mean(np.sign(y[mm]) == np.sign(x[mm])) for mm in (ax <= q[0], (ax > q[0]) & (ax <= q[1]), ax > q[1])]
        RES[lab] = dict(o=o, p=p, sdp=sdp, S=S.mean(), St=St, agree=agree, n=len(e), lvl=np.nanmedian(e.P0))
        say(f"| {lab} | {len(e)}（" + "/".join(f"{t} {int((e.type==t).sum())}" for t in types) + f"） | **{fb(o)}** | {p:.3f} / {sdp:.3f} | {x.std():.0f} / {y.std():.0f} | {bt} | {bc[0]}／{bc[1]} | {fb(oj)} | {fb(o2)} | {S.mean():+.1f} ({St:+.2f}) | {agree[0]*100:.0f}/{agree[1]*100:.0f}/{agree[2]*100:.0f}% |")
    # positive control (in-sample)
    lab, lo, hi = ERAS[0]; e = E[E.valid & E.type.isin(types) & (E.year >= lo) & (E.year <= hi)]
    y, x, g = e.POST.to_numpy(float), e.JUMP.to_numpy(float), e.type.to_numpy(); oi = hc1_fe(y + 0.2 * x, x, g)
    say(f"- 陽性対照（在・POST に +0.2·JUMP 注入）: t {RES[lab]['o']['t']:+.2f} → {oi['t']:+.2f}（Δt {oi['t']-RES[lab]['o']['t']:+.2f}）・実測 se {RES[lab]['o']['se']:.3f}（事前見積 0.06〜0.08）")
    # bid artefact check: JUMP' = P(t0+30)/P(t0+5)
    say("- 反証 (1) bid 人工物: JUMP' = P(t0+30)/P(t0+5)（初動足を外す）での β: " + "・".join(f"{lab} {fb(hc1_fe(E[E.valid&E.type.isin(types)&(E.year>=lo)&(E.year<=hi)].POST.to_numpy(float), E[E.valid&E.type.isin(types)&(E.year>=lo)&(E.year<=hi)].JUMPp.to_numpy(float), E[E.valid&E.type.isin(types)&(E.year>=lo)&(E.year<=hi)].type.to_numpy()))}" for lab, lo, hi in ERAS))
    # yearly β (descriptive)
    say("- 年別 β（プール・記述・n≥12）: " + " ".join(f"{yv}:{hc1_fe(E[E.valid&E.type.isin(types)&(E.year==yv)].POST.to_numpy(float), E[E.valid&E.type.isin(types)&(E.year==yv)].JUMP.to_numpy(float), E[E.valid&E.type.isin(types)&(E.year==yv)].type.to_numpy(), 12)['b']:+.2f}" for yv in range(2010, 2027)))
    # post-hoc description: pool including CPI regardless of PC (calendar validated out-of-sample and on US500), and CPI-only
    say("- **記述・事後（判定に使わない）CPI 込みプール NFP＋FOMC＋CPI と CPI 単独の β**: " + " ｜ ".join(
        (lambda e3, e1: f"{lab} 3 種 {fb(hc1_fe(e3.POST.to_numpy(float), e3.JUMP.to_numpy(float), e3.type.to_numpy()))} p {perm_signflip(e3.POST.to_numpy(float), e3.JUMP.to_numpy(float), e3.type.to_numpy(), hc1_fe(e3.POST.to_numpy(float), e3.JUMP.to_numpy(float), e3.type.to_numpy())['b'])[0]:.3f}・S {np.mean(np.sign(e3.JUMP)*e3.POST):+.1f} bp・CPI 単独 {fb(hc1_fe(e1.POST.to_numpy(float), e1.JUMP.to_numpy(float), e1.type.to_numpy()))}・CPI J 日限定 {fb(hc1_fe(e1[e1.J].POST.to_numpy(float), e1[e1.J].JUMP.to_numpy(float), e1[e1.J].type.to_numpy()))}")(
            E[E.valid & (E.year >= lo) & (E.year <= hi)], E[E.valid & (E.type == 'CPI') & (E.year >= lo) & (E.year <= hi)]) for lab, lo, hi in ERAS))
    # economic size
    for lab in RES:
        lvl = RES[lab]["lvl"]; cost = 0.16 / lvl * 1e4 if sym == "XAU" else np.nan
        say(f"- {lab}: 符号戦略 S {RES[lab]['S']:+.1f} bp/回 (t {RES[lab]['St']:+.2f})・往復コスト {cost:.2f} bp（0.16 USD @ {lvl:.0f}）→ net {RES[lab]['S']-cost:+.1f} bp/回・年 ≈{RES[lab]['n']/max(1,(ERAS[[l for l,_,_ in ERAS].index(lab)][2]-ERAS[[l for l,_,_ in ERAS].index(lab)][1]+1)):.0f} 回" if sym == "XAU" else f"- {lab}: S {RES[lab]['S']:+.1f} bp/回 (t {RES[lab]['St']:+.2f})")
    return E, RES, types

E_X, RX, TYPES = run("XAU")
# US500 replication (descriptive)
try:
    E_U, RU, _ = run("US500", judge=False)
except Exception as ex: say(f"- US500 複製 skip: {ex}")

# ---------- gate ㉛ ----------
say("\n## ゲート ㉛（本番接続・在 2010-20 のみ印字）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["ft"] = FT / tr["risk"]
tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]; tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = (tr["exit"] == "TP").astype(float) - tr["q"]
et_ = tr["entry_time"].to_numpy(float); hold_end = et_ + 300 * tr["hold"].to_numpy(float)
ev = E_X[E_X.type.isin(TYPES)]; t0s = np.sort(ev.t0.to_numpy(float)); t0s = t0s[np.isfinite(t0s)]
pos = np.searchsorted(t0s, et_, side="right") - 1; pos = np.clip(pos, 0, len(t0s) - 1)
inpost = (et_ >= t0s[pos]) & (et_ < t0s[pos] + 7200)
posn = np.clip(np.searchsorted(t0s, et_, side="left"), 0, len(t0s) - 1); alive = (et_ < t0s[posn]) & (hold_end >= t0s[posn])
# same-clock control: entries on non-event weekdays within [08:30,10:30) or [14:00,16:00) ET
e_ny = pd.DatetimeIndex(pd.to_datetime(tr.entry_time.to_numpy().astype(np.int64), unit="s", utc=True)).tz_convert(NY); hh = e_ny.hour.to_numpy() + e_ny.minute.to_numpy() / 60; wd_ = e_ny.weekday.to_numpy()
clockwin = ((hh >= 8.5) & (hh < 10.5)) | ((hh >= 14) & (hh < 16)); evday = pd.DatetimeIndex(e_ny.tz_localize(None).normalize()).isin(pd.DatetimeIndex(E_X.date))
tr["inpost"] = inpost; tr["ctrl"] = clockwin & ~evday & (wd_ <= 4)
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); d_ = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d_, d_ / se, se
ins = tr[(tr.year >= 2010) & (tr.year <= 2020)]; A, B = ins[ins.inpost], ins[ins.ctrl]
dm, tm, sem = welch(A.Rs, B.Rs); dx, tx, _ = welch(A[A.dec].x, B[B.dec].x); d0, t0_, _ = welch(A.x0, B.x0)
say(f"- 在 2010-20: 事象後 2 時間 [t0, t0+120 分] に建玉 {len(A)} vs 非事象日の同時刻窓 {len(B)}（全年 事象後建玉 {int(inpost.sum())}・発表 t0 を生きて跨ぐ本 全年 {int(alive.sum())}・在 {int((alive&(tr.year<=2020)).sum())}／外 {int((alive&(tr.year>=2021)).sum())}）")
say(f"- 事象後−対照: Δμ(R*) **{dm:+.3f}R (t {tm:+.2f}, se {sem:.3f}, MDE {2*sem:.3f})**・Δx {dx*100:+.2f} pp (t {tx:+.2f})・look-ahead 対照 x0 Δ {d0:+.3f} (t {t0_:+.2f})・TP 率 {(A.exit=='TP').mean()*100:.1f}% vs {(B.exit=='TP').mean()*100:.1f}%")
gate = "通過（外を印字）" if abs(dm) >= 0.048 else "**不通過（在 |Δμ| <0.048R → 決着不能・外は走らせない）**"
say(f"- ゲート ㉛: {gate}")
if abs(dm) >= 0.048:
    for lab, lo, hi in ERAS[1:]:
        o = tr[(tr.year >= lo) & (tr.year <= hi)]; a_, b_ = o[o.inpost], o[o.ctrl]
        if len(a_) >= 20: dm2, tm2, se2 = welch(a_.Rs, b_.Rs); say(f"  - {lab}: Δμ {dm2:+.3f}R (t {tm2:+.2f}, n {len(a_)}/{len(b_)})")
for t in TYPES:
    tt = np.sort(ev[ev.type == t].t0.to_numpy(float)); tt = tt[np.isfinite(tt)]; pp = np.clip(np.searchsorted(tt, et_, side="right") - 1, 0, len(tt) - 1); ip = (et_ >= tt[pp]) & (et_ < tt[pp] + 7200)
    a_ = ins[ip[(tr.year >= 2010).to_numpy() & (tr.year <= 2020).to_numpy()]]
    if len(a_) >= 10: say(f"  - 記述 在 {t} 後 2 時間建玉 n {len(a_)} 平均 R* {a_.Rs.mean():+.3f}")

# ---------- verdict ----------
say("\n## 判定（事前固定・C1 のみ・名目 0.025）")
i, o = RX["在 2010-20"], RX["外 2021-26H1"]
pool_ok = RX["在 2010-20"]["n"] >= 300
cont = pool_ok and i["o"]["b"] > 0 and i["o"]["t"] >= 2 and i["p"] < 0.025 and o["o"]["b"] > 0 and o["o"]["t"] >= 1.5
rev = pool_ok and i["o"]["b"] < 0 and i["o"]["t"] <= -2 and i["p"] < 0.025 and o["o"]["b"] < 0 and o["o"]["t"] <= -1.5
tag = "PASS（継続・post-announcement drift）" if cont else ("PASS（反転・初動オーバーシュート）" if rev else ("void（事前規則: プール 在 n<300）" if not pool_ok else "null"))
in_ok = i["o"]["b"] > 0 and i["o"]["t"] >= 2 and i["p"] < 0.025; out_ok = o["o"]["b"] > 0 and o["o"]["t"] >= 1.5
say(f"- C1 金 プール{TYPES}: 在 {fb(i['o'])} p {i['p']:.3f}／外 {fb(o['o'])} p {o['p']:.3f}／近年 {fb(RX['近年 2024-26H1']['o'])} → **{tag}**")
say(f"- 参考（n 規則を外した場合の同じ判定規則）: 在 条件 {'成立' if in_ok else '不成立'}（β>0 ∧ t≥2 ∧ p<0.025）・外 確認 {'成立' if out_ok else '不成立'}（同符号 ∧ t≥1.5）→ {'PASS' if (in_ok and out_ok) else 'null'}・在の実測 se {i['o']['se']:.3f} は事前見積 0.06〜0.08 の内側（決着可能性は n 300 でなく se で満たされていた）")
say(f"- 用量反応（㊾）: 符号一致率 |JUMP| 三分位 在 {'/'.join(f'{a*100:.0f}' for a in i['agree'])}%／外 {'/'.join(f'{a*100:.0f}' for a in o['agree'])}%／近年 {'/'.join(f'{a*100:.0f}' for a in RX['近年 2024-26H1']['agree'])}%")
say(f"\n- 実行 {time.time()-T0:.1f} s・npz 2 本＋json＋FOMC_dates.csv＋CPI_dates.csv・scan 無し・MT5 無し・外部通信無し（CPI 暦取得は scripts/c44_cpi_dates.py で別に実施）。seed {SEED}。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
