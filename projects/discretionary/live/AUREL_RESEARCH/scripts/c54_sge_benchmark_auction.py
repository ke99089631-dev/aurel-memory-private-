# -*- coding: utf-8 -*-
"""
[cycle54 研究レーン] 2026-11-19 — 【探索・市場構造（ベンチマーク執行の集中・会場横断の複製）】
上海黄金交易所（SGE）の「上海金ベンチマーク価格」オークション（2016-04-19 開始・10:15／14:15 北京時間・1 kg 現物バー・RMB 建て）は、
LBMA オークションで c50 が 4 期間すべてで見た **「オークション直前 5 分の沈み → 直後 5 分の戻し」** を XAUUSD スポット（USD・bid）にも残すか。
問いの位置: §8「ベンチマーク執行の集中」行の**会場横断の複製**。c50 の形が LBMA 固有（ロンドンのディーラー慣行）か
ベンチマーク・オークション一般（顧客注文の事前捌き）かは、別会場で同じ形が出るかで分かれる。2016-04-19 の開始日が
**時間内プラセボ（開始前は同じ時刻に何も無い）**を与える＝c50 に無かった対照。

=== 事前固定（この docstring を書いてから数字を見る） ===
外部確認（WebSearch 1 回・2026-11-19）: SGE 公式（en.sge.com.cn 537284／537464）・World Gold Council プレスリリース＝開始 2016-04-19・
  オークション 10:15 と 14:15 上海時間。中国は DST 無し → **10:15 CST = 02:15 UTC・14:15 CST = 06:15 UTC（通年固定）**。
データ: data/macro/XAU_m5_close.npz（bid・暦格子・前値埋め・⑪ flat 比率印字）。足は開始時刻ラベル。r(t) = lnC(t) − lnC(t−5min)（bp）
  = 足 t の 5 分間の値動き。**PRE 足 = 02:10 UTC 足（02:10–02:15 = オークション開始直前 5 分）・POST 足 = 02:15 UTC 足**（c50 の 10:25／10:35 London と同じ規約）。
  PM: PRE 06:10・POST 06:15。
有効日: UTC 月〜金 ∧ 窓 ±30 分（13 足）の非 flat ≥8 ∧ 必要スロットが格子に存在。中国の祝日（SGE 休場・年 ≈11〜15 平日・5%）は
  暦が導出できないので**落とさない**（処置が薄まる方向＝null に保守的・PASS には出ない）。
期間（UTC 日付・制度日付で事前固定）: P0 = 2010-01-01〜2016-04-18（開始前・時間内プラセボ）／P1 = 2016-04-19〜2020-12-31（在）／
  P2 = 2021-01-01〜2026-06（外）／近年 = 2024-01-01〜2026-06（記述）。D2: 期間別・16 年一括の水準は edge 判定に使わない。
主セル C1 H_DIP（AM オークション・方向つき・条件は 1 行ずつ独立に印字し判定は旗から合成＝方法論候補 72/75）:
  (a) P1 mean r(02:10) < 0 ∧ t ≤ −2
  (b) P2 mean r(02:10) < 0 ∧ t ≤ −1.5
  (c) P0 の同足が t ≤ −2 で負ではない（時間内プラセボが清い）
  (d) 差 (P1∪P2) − P0 の Welch t ≤ −2
  (e) 13 足 family（01:40〜02:40）で 02:10 足の t が P1 で最小（順位 1/13）
  PASS = (a)∧(b)∧(c)∧(d)∧(e)。(a)∧(b) だけ成立し (c) が偽なら「制度非依存（開始前からある）＝人工物か別機構」と読む。他は null（MDE = 2·se）。
副セル C2 H_REB（AM・方向つき・Bonferroni(2) で主と family）: P1 mean r(02:15) > 0 ∧ t ≥ 2.24 ∧ P2 t ≥ 1.5 ∧ P0 は t ≥ 2.24 でない。
副セル C3 PM オークション（06:10／06:15）: C1/C2 と同形・Bonferroni(2・会場内 2 オークション)で 在 閾値 |t| 2.24。
  **混同（事前に書く）**: 06:15 UTC = 15:15 JST = JPX/TOCOM 金先物 日中立会の引け → P0 にも存在する定常の混同＝P0 との差分 (d) で消える前提。
プラセボ時刻（同じ「15 分過ぎ」の構造・AM 側のみ）: 01:10/01:15・03:10/03:15・04:10/04:15・05:10/05:15 UTC（P1 で |t| ≥ 2 になる本数を印字）。
family 校正: 13 足の t の sd（≈1 なら帰無校正 OK）・Bonferroni(13) 片側閾値 2.5。
反転 C4（記述）: β(r_POST on r_PRE)（HC1 t）期間別・プラセボ時刻でも。
ボラ C5（記述・方法論候補 69 改訂版）: V = mean r(PRE)² ÷ 隣接 12 足の mean r²（日ブートストラップ 1000・95% CI）と
  **最小検出増幅 k* = 1/CI 下限**（k* が 1.3 超なら「痕跡の有無」の判定に使わない・印字のみ）。
ゲート ㉛（印字のみ・証拠ではない）: scan 本（refute_c4 json → entry_time 昇順・fullpaths off と hold の整合 assert・方法論候補 78 の
  0≤k≤hold assert）で 建玉 UTC 22:00(前日)〜02:05 ∧ hold ≥ j_pre+1 の本（同 ET セッション・02:10 足を生きて跨ぐ）について
  side 符号つき path 変化 Δcl = clR[j_pre+1] − clR[j_pre−1]（02:10＋02:15 の 2 足・R 単位）を P0／P1／P2 で印字。|Δμ| と MDE。
  期待（数字を見る前）: 沈み+戻しは方向に無差別 → side 符号つきでは ≈0。建玉帯 jh7-12（JST 07–12）= UTC 22–03 なので本番帯の本が多数 該当。
経済的大きさ: bp と口座スプレッド（0.16 USD を当該期の価格で bp 化）の比。1 bp ≈ 在 0.037R／外 0.050R（c18）。
look-ahead なし（全窓 事後の記述・条件づけは時刻のみ）。多重検定: 判定 C1 1 セル＋C2（Bonferroni 2）＋C3（会場内 Bonferroni 2）。
  13 足 profile・プラセボ時刻・年別・C4・C5 は記述。survivorship: 単一銘柄・連続 CFD 系列・銘柄選択なし。
事前の最重大反証候補: ①bid のみ・1 社 CFD＝オークション前後のスプレッド拡大で bid が沈む人工物（c50 と同じ）→ P0 との差分で
  「2016-04 を境に bid の挙動が変わった」を要求する形になるので、Dukascopy の配信変更が同時期なら誤帰属（⑰）。②02:15 UTC は
  北京 10:15 だが 東京 11:15・シンガポール 10:15 でもあり、他の定時事象（中国 10:00 公表は 02:00 UTC・PBoC 固定 09:15 CST = 01:15 UTC）
  と 15 分ずれている＝直接の混同は無いが「アジア午前の一般的な癖」はプラセボ時刻で見る。③XAUUSD スポットは SGE 現物（RMB・輸入枠・
  上海プレミアム）の測定点ではない＝null は「スポット USD 経路の否定」に限る。④中国祝日の希釈 5%。⑤P0 は 2010-16 で
  5 分 lag1 負自己相関（c19）が強い期間＝反転係数 C4 の P0 vs P1 差はその別名になり得る。
seed 20261119。scan 無し・M5 原本読込なし・MT5 なし。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c54_sge_benchmark_auction_result.md")
SEED = 20261119; rng = np.random.default_rng(SEED)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle54] 上海金ベンチマーク・オークション（02:15／06:15 UTC・2016-04-19 開始）の直前沈み・直後戻し — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c54_sge_benchmark_auction.py)")

# ---------- load ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = (r == 0)
t_utc = pd.to_datetime(ts, unit="s", utc=True)
wd = t_utc.weekday.to_numpy(); hour = t_utc.hour.to_numpy(); minute = t_utc.minute.to_numpy()
slot = hour * 12 + minute // 5
day = pd.DatetimeIndex(t_utc.tz_localize(None)).normalize()
WDN = ['月','火','水','木','金','土','日']
say(f"- npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {flat.mean()*100:.1f}%・曜日別(UTC) "
    + " ".join(f"{WDN[w]}{flat[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")

def S(h, m): return h * 12 + m // 5
bp = 1e4
# slots 00:30 .. 08:00 UTC (covers AM/PM windows and placebo hours)
SLOTS = list(range(S(0, 30), S(8, 0) + 1))
sel = np.isin(slot, SLOTS) & (wd <= 4)
df = pd.DataFrame({"day": day[sel], "slot": slot[sel], "r": r[sel] * bp, "flat": flat[sel].astype(int)})
R = df.pivot_table(index="day", columns="slot", values="r", aggfunc="first").reindex(columns=SLOTS)
F = df.pivot_table(index="day", columns="slot", values="flat", aggfunc="first").reindex(columns=SLOTS)
days = pd.DatetimeIndex(R.index)
Rv = R.to_numpy(); Fv = F.to_numpy()
def col(h, m): return SLOTS.index(S(h, m))

def window_ok(h, m):  # ±30 min around the auction start (13 bars: h:m-30 .. h:m+30)
    c = col(h, m); cols = list(range(c - 6, c + 7))
    grid = np.isfinite(Rv[:, cols]).all(axis=1)
    nf = (1 - np.nan_to_num(Fv[:, cols], nan=1)).sum(axis=1)
    return grid & (nf >= 8), cols

okAM, colsAM = window_ok(2, 15); okPM, colsPM = window_ok(6, 15)
say(f"- UTC 平日 {len(days)} 日 → AM 窓 OK {okAM.sum()} 日・PM 窓 OK {okPM.sum()} 日（落とした = 週末跨ぎ/祝日停止/格子穴・AM {(~okAM).sum()}・PM {(~okPM).sum()}）")

PER = {"P0 2010-01〜2016-04-18 開始前": (days >= "2010-01-01") & (days <= "2016-04-18"),
       "P1 2016-04-19〜2020 在": (days >= "2016-04-19") & (days <= "2020-12-31"),
       "P2 2021-26H1 外": (days >= "2021-01-01"),
       "近年 2024-26H1": (days >= "2024-01-01")}
P12 = PER["P1 2016-04-19〜2020 在"] | PER["P2 2021-26H1 外"]

def stat(x):
    x = x[np.isfinite(x)]; n = len(x); m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); t = m / se if se > 0 else np.nan
    nz = (x != 0).sum(); zs = ((x < 0).sum() - nz / 2) / math.sqrt(nz / 4) if nz > 0 else np.nan
    return dict(n=n, m=m, se=se, t=t, mde=2 * se, neg=(x < 0).mean(), zsign=zs, med=np.median(x), sd=x.std(ddof=1))
def diff_t(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    return (a.mean() - b.mean()) / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
def fmt(s): return f"**{s['m']:+.3f} bp (t {s['t']:+.2f}, n {s['n']}, MDE {s['mde']:.3f})** 下落足 {s['neg']*100:.1f}% (符号 z {s['zsign']:+.2f}) sd {s['sd']:.2f}"

def profile(ok, cols, h, m, label):
    """13-bar profile per period; return dict period->(array of stats), and the PRE/POST stats."""
    say(f"\n### {label}: ±30 分 5 分足プロファイル（bp/足・列 = 足開始 UTC・t は日 = 独立観測）")
    out = {}
    cpre = col(h, m) - 1 - (cols[0]); cpost = cpre + 1
    for k, msk in PER.items():
        mm = msk & ok; X = Rv[mm][:, cols]
        st = [stat(X[:, j]) for j in range(len(cols))]
        tt = np.array([s['t'] for s in st])
        lab = [f"{(SLOTS[c]//12):02d}:{(SLOTS[c]%12)*5:02d}" for c in cols]
        say(f"- {k} (n {mm.sum()}): " + " ".join(f"{lab[j]} {st[j]['m']:+.2f}({tt[j]:+.1f})" for j in range(len(cols))))
        say(f"  - t の sd {tt.std(ddof=1):.2f}・|t|≥2 {int((np.abs(tt)>=2).sum())}/13・PRE 足 {lab[cpre]} の t 順位（小さい順）{int((tt <= tt[cpre]).sum())}/13・POST 足 {lab[cpost]} の t 順位（大きい順）{int((tt >= tt[cpost]).sum())}/13")
        out[k] = dict(st=st, tt=tt, pre=st[cpre], post=st[cpost], X=X, cpre=cpre, cpost=cpost, mask=mm)
    return out

AM = profile(okAM, colsAM, 2, 15, "AM オークション 10:15 CST = 02:15 UTC")
PM = profile(okPM, colsPM, 6, 15, "PM オークション 14:15 CST = 06:15 UTC")

def judge(prof, ok, cols, h, m, name, t_in=2.0, t_out=1.5, t_pl=2.0):
    say(f"\n## {name}")
    k0, k1, k2 = "P0 2010-01〜2016-04-18 開始前", "P1 2016-04-19〜2020 在", "P2 2021-26H1 外"
    pre0, pre1, pre2 = prof[k0]['pre'], prof[k1]['pre'], prof[k2]['pre']
    post0, post1, post2 = prof[k0]['post'], prof[k1]['post'], prof[k2]['post']
    cpre = prof[k1]['cpre']; cpost = prof[k1]['cpost']
    xpre = Rv[:, cols[cpre]]; xpost = Rv[:, cols[cpost]]
    say(f"- PRE 足（直前 5 分）: P0 {fmt(pre0)}／P1 {fmt(pre1)}／P2 {fmt(pre2)}／近年 {fmt(prof['近年 2024-26H1']['pre'])}")
    say(f"- POST 足（直後 5 分）: P0 {fmt(post0)}／P1 {fmt(post1)}／P2 {fmt(post2)}／近年 {fmt(prof['近年 2024-26H1']['post'])}")
    td_pre = diff_t(xpre[P12 & ok], xpre[PER[k0] & ok]); td_post = diff_t(xpost[P12 & ok], xpost[PER[k0] & ok])
    say(f"- 差 (P1∪P2) − P0: PRE 足 {np.nanmean(xpre[P12&ok]) - np.nanmean(xpre[PER[k0]&ok]):+.3f} bp (Welch t {td_pre:+.2f})・POST 足 {np.nanmean(xpost[P12&ok]) - np.nanmean(xpost[PER[k0]&ok]):+.3f} bp (t {td_post:+.2f})")
    # H_DIP legs
    a = (pre1['m'] < 0) and (pre1['t'] <= -t_in)
    b = (pre2['m'] < 0) and (pre2['t'] <= -t_out)
    c = not (pre0['t'] <= -t_pl)
    d = td_pre <= -2
    e = int((prof[k1]['tt'] <= prof[k1]['tt'][cpre]).sum()) == 1
    say(f"- H_DIP 条件 (a) P1 PRE m<0 ∧ t≤−{t_in}: 観測 m {pre1['m']:+.3f} t {pre1['t']:+.2f} → {'成立' if a else '不成立'}")
    say(f"- H_DIP 条件 (b) P2 PRE m<0 ∧ t≤−{t_out}: 観測 m {pre2['m']:+.3f} t {pre2['t']:+.2f} → {'成立' if b else '不成立'}")
    say(f"- H_DIP 条件 (c) P0 PRE が t≤−{t_pl} でない（時間内プラセボ清い）: 観測 t {pre0['t']:+.2f} → {'成立' if c else '不成立'}")
    say(f"- H_DIP 条件 (d) (P1∪P2)−P0 の t≤−2: 観測 t {td_pre:+.2f} → {'成立' if d else '不成立'}")
    say(f"- H_DIP 条件 (e) P1 13 足で PRE 足の t が最小: 順位 {int((prof[k1]['tt'] <= prof[k1]['tt'][cpre]).sum())}/13 → {'成立' if e else '不成立'}")
    if a and b and c and d and e: v = "PASS（開始後にだけ直前沈み）"
    elif a and b and not c: v = "制度非依存（開始前からある負＝人工物か別機構・PASS ではない）"
    else: v = "null"
    say(f"- **判定 H_DIP: {v}**（MDE P1 {pre1['mde']:.3f}／P2 {pre2['mde']:.3f} bp）")
    # H_REB legs
    a2 = (post1['m'] > 0) and (post1['t'] >= 2.24)
    b2 = (post2['m'] > 0) and (post2['t'] >= 1.5)
    c2 = not (post0['t'] >= 2.24)
    say(f"- H_REB 条件 (a) P1 POST m>0 ∧ t≥2.24: 観測 m {post1['m']:+.3f} t {post1['t']:+.2f} → {'成立' if a2 else '不成立'}")
    say(f"- H_REB 条件 (b) P2 POST t≥1.5: 観測 t {post2['t']:+.2f} → {'成立' if b2 else '不成立'}")
    say(f"- H_REB 条件 (c) P0 POST が t≥2.24 でない: 観測 t {post0['t']:+.2f} → {'成立' if c2 else '不成立'}")
    v2 = "PASS" if (a2 and b2 and c2) else ("制度非依存（PASS ではない）" if (a2 and b2) else "null")
    say(f"- **判定 H_REB: {v2}**（MDE P1 {post1['mde']:.3f}／P2 {post2['mde']:.3f} bp）")
    # yearly PRE bar
    yrs = days.year
    say("- 年別 PRE 足 平均 (t): " + " ".join(f"{y} {stat(xpre[(yrs==y)&ok])['m']:+.2f}({stat(xpre[(yrs==y)&ok])['t']:+.1f})" for y in range(2010, 2027) if ((yrs==y)&ok).sum() > 50))
    # C4 reversal
    say("- C4 反転 β(POST on PRE)（HC1 t・記述）: " + "／".join(
        f"{k}: β {np.polyfit(xpre[msk&ok], xpost[msk&ok], 1)[0]:+.3f} (t {hc1_t(xpre[msk&ok], xpost[msk&ok]):+.2f})" for k, msk in PER.items()))
    # C5 vol ratio with bootstrap and k*
    for k, msk in PER.items():
        X = prof[k]['X']; pre2v = X[:, cpre] ** 2; nb = [j for j in range(X.shape[1]) if j not in (cpre, cpost)]
        nbv = X[:, nb].mean(axis=1) if False else (X[:, nb] ** 2).mean(axis=1)
        V = pre2v.mean() / nbv.mean(); n = len(pre2v); bs = []
        for _ in range(1000):
            idx = rng.integers(0, n, n); bs.append(pre2v[idx].mean() / nbv[idx].mean())
        lo, hi = np.percentile(bs, [2.5, 97.5]); kstar = 1 / lo if lo > 0 else np.inf
        Vp = (X[:, cpost] ** 2).mean() / nbv.mean()
        say(f"- C5 ボラ比 {k}: V_PRE {V:.3f} [95% CI {lo:.3f}, {hi:.3f}]・最小検出増幅 k* {kstar:.2f}{'（>1.3 → 痕跡判定に使わない）' if kstar > 1.3 else ''}・V_POST {Vp:.3f}")
    return dict(v=v, v2=v2, pre1=pre1, pre2=pre2, pre0=pre0, post1=post1, post2=post2, td_pre=td_pre, td_post=td_post)

def hc1_t(x, y):
    m = np.isfinite(x) & np.isfinite(y); x = x[m]; y = y[m]; n = len(x)
    X = np.column_stack([np.ones(n), x]); beta = np.linalg.lstsq(X, y, rcond=None)[0]; u = y - X @ beta
    XtXi = np.linalg.inv(X.T @ X); V = XtXi @ (X.T * (u ** 2)) @ X @ XtXi * n / (n - 2)
    return beta[1] / math.sqrt(V[1, 1])

JAM = judge(AM, okAM, colsAM, 2, 15, "C1/C2 AM オークション（主）")
JPM = judge(PM, okPM, colsPM, 6, 15, "C3 PM オークション（副・会場内 Bonferroni 2 → 在 閾値 2.24）", t_in=2.24, t_out=1.5, t_pl=2.24)

# ---------- placebo hours (same 'quarter past' structure) ----------
say("\n## プラセボ時刻（同じ「15 分過ぎ」の PRE/POST 足・AM 側の対照）")
npl = 0
for h in (1, 3, 4, 5):
    ok_h, cols_h = window_ok(h, 15); cpre = col(h, 15) - 1; cpost = col(h, 15)
    line = []
    for k, msk in PER.items():
        s_pre = stat(Rv[msk & ok_h, cpre]); s_post = stat(Rv[msk & ok_h, cpost])
        line.append(f"{k[:2]} PRE {s_pre['m']:+.2f}({s_pre['t']:+.1f}) POST {s_post['m']:+.2f}({s_post['t']:+.1f})")
        if k.startswith("P1") and (abs(s_pre['t']) >= 2 or abs(s_post['t']) >= 2): npl += 1
    say(f"- {h:02d}:10／{h:02d}:15 UTC: " + "・".join(line))
say(f"- P1 で |t|≥2 を出したプラセボ時刻（PRE か POST）: {npl}/4")

# ---------- economic size ----------
for k, msk in PER.items():
    mm = msk & okAM; px = np.exp(lc[np.isin(day, days[mm]) & (slot == S(2, 10))]).mean() if mm.sum() else np.nan
    say(f"- 経済的大きさ {k}: 当該期 02:10 UTC 平均価格 {px:.0f} USD → 口座スプレッド 0.16 USD = {0.16/px*1e4:.2f} bp（往復 {0.32/px*1e4:.2f}）vs PRE 足 {AM[k]['pre']['m']:+.3f} bp・POST 足 {AM[k]['post']['m']:+.3f} bp")

# ---------- gate ㉛ (print only) ----------
say("\n## ゲート ㉛（印字のみ）: 02:10 UTC 足を生きて跨ぐ scan 本の side 符号つき 2 足 path 変化（R）")
try:
    J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))["trades"]
    tj = pd.DataFrame(J).sort_values(["entry_time", "hold"], kind="stable").reset_index(drop=True)
    fp = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); off = fp["off"].astype(np.int64); clR = fp["clR"]
    ho = np.diff(off) - 1
    if not np.array_equal(ho, tj["hold"].to_numpy()):
        # c53 hygiene: reorder within duplicate entry_time groups to match off order
        bad = np.where(ho != tj["hold"].to_numpy())[0]
        say(f"  - hold 不一致 {len(bad)} 本 → 同時刻組を off 順に並べ替え（c53 衛生）")
        tj["_ho"] = ho
        for et, g in tj.groupby("entry_time"):
            if len(g) > 1 and not np.array_equal(g["hold"].to_numpy(), g["_ho"].to_numpy()):
                idx = g.index.to_numpy(); want = g["_ho"].to_numpy()
                order = []
                pool = list(idx)
                for wv in want:
                    pick = next(i for i in pool if tj.at[i, "hold"] == wv); order.append(pick); pool.remove(pick)
                tj.loc[idx, tj.columns.difference(["_ho"])] = tj.loc[order, tj.columns.difference(["_ho"])].to_numpy()
        assert np.array_equal(np.diff(off) - 1, tj["hold"].to_numpy()), "off/hold 規約 不一致"
    et = tj["entry_time"].to_numpy(); hold = tj["hold"].to_numpy()
    tsec = pd.to_datetime(et, unit="s", utc=True)
    secs = (tsec.hour * 3600 + tsec.minute * 60 + tsec.second).to_numpy()
    # auction day = UTC date of the 02:10 bar: entries 22:00-23:59 UTC → next day; 00:00-02:05 → same day
    base = (et // 86400) * 86400
    t0210 = np.where(secs >= 22 * 3600, base + 86400 + 2 * 3600 + 600, base + 2 * 3600 + 600)
    jpre = (t0210 - et) // 300
    alive = ((secs >= 22 * 3600) | (secs <= 2 * 3600 + 300)) & (jpre >= 1) & (hold >= jpre + 1) & ((t0210 - et) % 300 == 0)
    dow = pd.to_datetime(t0210, unit="s", utc=True).weekday.to_numpy()
    alive &= dow <= 4
    idx = np.where(alive)[0]
    assert (jpre[idx] - 1 >= 0).all() and (jpre[idx] + 1 <= hold[idx]).all()   # 方法論候補 78
    dcl = clR[off[idx] + jpre[idx] + 1] - clR[off[idx] + jpre[idx] - 1]
    dpre = clR[off[idx] + jpre[idx]] - clR[off[idx] + jpre[idx] - 1]
    # verify time alignment vs npz: compare path bar change with npz r at 02:10 (unsigned via side)
    side = np.where(tj["side"].to_numpy()[idx] == "BUY", 1.0, -1.0); risk = tj["risk"].to_numpy()[idx]
    pos = np.searchsorted(ts, t0210[idx]); okp = (pos < len(ts)) & (ts[np.minimum(pos, len(ts)-1)] == t0210[idx])
    npz_dpx = np.diff(cl)[pos[okp] - 1]  # close[0210] - close[0205]
    path_dpx = dpre[okp] * risk[okp] * side[okp]
    agree = np.mean(np.abs(npz_dpx - path_dpx) <= 0.02)
    say(f"  - 該当本 {len(idx)}（jh7-12 {int(np.isin(tj['jh'].to_numpy()[idx], range(7,13)).sum())}）・path 02:10 足 Δ と npz の一致（|差|≤0.02 USD）{agree*100:.1f}%（c18/c21 の整合）")
    ety = pd.to_datetime(t0210[idx], unit="s", utc=True)
    for k, (lo, hi) in {"P0": ("2010-01-01", "2016-04-18"), "P1 在": ("2016-04-19", "2020-12-31"), "P2 外": ("2021-01-01", "2027-01-01"), "近年": ("2024-01-01", "2027-01-01")}.items():
        m = (ety >= lo) & (ety <= hi)
        s2 = stat(dcl[m]); s1 = stat(dpre[m]); sb = np.mean(side[m] > 0) if m.sum() else np.nan
        say(f"  - {k}: n {m.sum()}・BUY 比 {sb*100:.0f}%・Δcl(02:10+02:15) {s2['m']:+.4f}R (t {s2['t']:+.2f}, MDE {s2['mde']:.4f})・Δcl(02:10 のみ) {s1['m']:+.4f}R (t {s1['t']:+.2f})")
except Exception as ex:
    say(f"  - ゲート計算 失敗: {ex!r}（主判定には影響なし）")

say(f"\n- 実行 {time.time()-T0:.1f} s・seed {SEED}・多年 scan 無し・MT5 無し・外部通信 = WebSearch 1 回（事前・暦確認）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"[saved] {OUT}")
