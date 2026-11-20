# -*- coding: utf-8 -*-
"""
[cycle57 研究レーン] 2026-11-20 — 【探索・マイクロストラクチャー／行動（源泉マップ §8: 注文集積・心理的水準の第 2 行）】
内生的な価格水準＝「前セッションの高値・安値」は障壁（反発）か磁石（加速通過）か。
背景: c26 は外生的なキリ番（50/100 USD）で「占有が 21〜25% 少なく・接近後 1 時間の横断が +2.6〜3.2 pp 高い」＝磁石型を
確認した。Osler (2003, JF) は FX の逆指値が「直近の高値/安値の直外」に集積し（損切り）・指値（利食い）が直内に集積すると報告。
前日高値/安値は trader lore の「サポート/レジスタンス」（反発）でもあり、機構は正反対 → 方向は事前に決めず両側で検定・
事前の予測（記録）は c26 と同じ磁石型（P(通過) > 擬似水準）。入口フィルタではない（市場構造の記述・RW/擬似水準対照つき）。

事前固定（検証前に書く・結果を見てから変えない・seed 20261120・乱数は bootstrap のみ）:
  データ: data/macro/XAU_m5_ohlc.npz（bid・完全格子・前値埋め）。flat 足 = close==前足 close ∧ high==low（週末/閉場）除外。
        セッション日 d = (ET+6h) の暦日（18:00 ET 始まり・c31/c36 と同じ）。有効セッション = 月〜金 ∧ 非 flat 足 ≥100。
        窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括の数字は判定に使わない）。
  水準: H_{d-1}, L_{d-1}（前有効セッションの高値・安値・直前セッションが有効でない日は除外）。
        R_{d-1} = H−L。擬似水準（プラセボ）P_m = L + m·R, m ∈ {0.2, 0.35, 0.5, 0.65, 0.8}（レンジ内部・同じ向きの接近を同じ条件づけで作る）。
        外部水準 m ∈ {1.25, 1.5}（上）・{−0.25, −0.5}（下）は「既にブレイクした後」の記述（判定に使わない）。
        帯 δ = max(0.05·R_{d-1}, 0.30 USD)。
  接近イベント（セッション d 内・水準ごとに最初の 1 回）: 上向き接近 = close_{t-1} < X−δ ∧ X−δ ≤ close_t < X（下から帯に入る）。
        下向き接近 = close_{t-1} > X+δ ∧ X < close_t ≤ X+δ。H は上向きのみ・L は下向きのみ・内部 P_m は両向き（向き別に集計）。
        建玉足 t の後、K=24 本（2 時間）以内の先着: CROSS = close ≥ X+δ（上向き接近の場合）／RETREAT = close ≤ X−3δ。
        入口は X−δ 付近なので両バリアは入口から ±2δ の対称＝無ドリフト RW なら P(CROSS 先着 | 決着) = 0.5。
        未決着（K 本以内にどちらも触れない）は censor として率を別に印字。主統計は p_cross = CROSS/(CROSS+RETREAT)。
  主セル（2・Bonferroni 2）: D_H = p_cross(H, 上向き) − p_cross(内部 P_m プール, 上向き)／D_L = p_cross(L, 下向き) − p_cross(内部プール, 下向き)。
        se = 2 比率（独立近似・1 セッション 1 事象/水準）・セッション日ブロック bootstrap（2000）で se を併記（主は bootstrap）。
        判定 PASS = 在 |D| ≥ 0.03 ∧ |z_boot| ≥ 2.5 ∧ 外 同符号 ∧ |z| ≥ 1.5。D>0 = 磁石・D<0 = 障壁。MDE(2se) 併記。
        副: RW 帰無 p_cross=0.5 からの差（真の水準・擬似水準それぞれ）・K=12（1 時間）感度・δ=0.10R 感度・月曜（週末跨ぎ）除外版。
  陽性対照: 同じ機械を G=50 USD キリ番（最近傍水準・両向き）に当て c26 の「磁石 +2.6〜3.2 pp（横断率）」と同符号の p_cross 超過が
        出るか（道具の校正）。注入対照: 在 H の CROSS を 5 pp 分 RETREAT に反転させて z を印字。
  ゲート ㉛（本番 path・記述）: scan 19404 本。entry ≈ npz close(entry_time)（建玉足 close・誤差 ≤ 数 USD/10）。
        BUY: TP = entry + b·risk・Z=1 if entry < H_{d-1} ≤ TP（前セッション高値が TP までの道に挟まる）；SELL 対称（L_{d-1}）。
        Δμ(R*) = mean(R*|Z=1) − mean(R*|Z=0)・R* = R + ft·1{SL,TP}・ft=0.1/risk。在 |Δμ| ≥ 0.048 で外を印字（通過しても証拠ではない・㉛ 訂正）。
  事前の最重大反証: (i) bid のみ・1 社（δ ≥ 0.30 USD はスプレッド 0.16〜0.4 と同桁・帯の端が気配で汚れる）；
        (ii) 内部擬似水準への「上向き接近」は H への接近よりセッション初期に起きやすい（時刻組成が違う）→ 接近時刻（ET 時）の分布を
        真/擬似で印字し、ET 時 FE 版の D を併記；(iii) H への上向き接近は「当日すでに上昇」を条件づける（モメンタム）が、内部水準の
        上向き接近も同じ向きの条件づけなので差分で消える＝ただし移動距離は違う（H までは L から R 全部・P_0.5 までは半分）→
        接近直前 1 時間のリターン（bp）を真/擬似で印字；(iv) 1 セッション 1 事象の独立近似は同日の H/L/内部事象が相関 → 日ブロック
        bootstrap を主にする；(v) 前セッション高値の定義（bid の 5 分高値）は実約定の高値と違い、注文が集積する「見える高値」は
        ベンダーで違う（決着不能・記録）。
  D2: 窓別・16 年一括なし。昇格候補・入口/出口規則の提案ではない。
入力: data/macro/XAU_m5_ohlc.npz・data/refute_c4_scan_paths_2010_2026.json。scan 無し・M5 読込なし・MT5 無し・外部通信無し。
出力: data/c57_prior_session_extremes_barrier_result.md・data/c57_run.log。
"""
import os, sys, json, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c57_prior_session_extremes_barrier_result.md")
rng = np.random.default_rng(20261120); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
def utc(x): return dt.datetime.fromtimestamp(int(x), dt.timezone.utc)
say(f"# [cycle57] 前セッション高値/安値は障壁か磁石か — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c57_prior_session_extremes_barrier.py)")

K_MAIN, K_ALT = 24, 12
DELTA_FRAC, DELTA_FLOOR = 0.05, 0.30
M_INT = [0.2, 0.35, 0.5, 0.65, 0.8]
M_EXT_UP, M_EXT_DN = [1.25, 1.5], [-0.25, -0.5]
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

# ---------------- データ ----------------
z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); O = z["open"].astype(float); H = z["high"].astype(float); Lo = z["low"].astype(float); C = z["close"].astype(float)
say(f"- npz {len(TS)} 本 {utc(TS[0])} 〜 {utc(TS[-1])} UTC・close min {C.min():.1f} max {C.max():.1f}（⑩）")
flat = np.r_[True, (C[1:] == C[:-1]) & (H[1:] == Lo[1:])]
wd_all = ((TS // 86400) + 3) % 7
say("- flat 比率 曜日別: " + ", ".join(f"{n}:{flat[wd_all==i].mean()*100:.1f}%" for i, n in enumerate("月火水木金土日")) + f"・全体 {flat.mean()*100:.1f}%（⑪）")
et = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
sess = (et + pd.Timedelta(hours=6)).normalize().values.astype("datetime64[D]")
et_hour = et.hour.values
sess_wd = pd.DatetimeIndex(sess).weekday.values  # 0=月
year = et.year.values
keep = ~flat
idx = np.flatnonzero(keep)
sess_k = sess[idx]; C_k = C[idx]; H_k = H[idx]; L_k = Lo[idx]; hr_k = et_hour[idx]; yr_k = year[idx]; wd_k = sess_wd[idx]
# セッション集計
us, inv = np.unique(sess_k, return_inverse=True); ns = len(us)
cnt = np.bincount(inv, minlength=ns)
hi_s = np.full(ns, -np.inf); np.maximum.at(hi_s, inv, H_k)
lo_s = np.full(ns, np.inf); np.minimum.at(lo_s, inv, L_k)
wd_s = pd.DatetimeIndex(us).weekday.values
valid = (cnt >= 100) & (wd_s <= 4)
# 直前の有効セッション（並び順で直前・暦の隣接は問わない: 月曜の直前は金曜）
prev_idx = np.full(ns, -1)
last = -1
for i in range(ns):
    prev_idx[i] = last
    if valid[i]: last = i
use_s = valid & (prev_idx >= 0)
# 直前有効セッションが暦で 4 日以上前（祝日跨ぎ等）は記述用に旗
gap_days = np.where(prev_idx >= 0, (us - us[np.maximum(prev_idx, 0)]).astype("timedelta64[D]").astype(int), 99)
say(f"- セッション {ns}・有効（月〜金 ∧ 非 flat ≥100）{valid.sum()}・判定に使う（直前有効あり）{use_s.sum()}・"
    f"直前が 1 日 {(use_s & (gap_days==1)).sum()}／3 日（週末）{(use_s & (gap_days==3)).sum()}／その他 {(use_s & ~np.isin(gap_days,[1,3])).sum()}")
Rng_prev = np.where(prev_idx >= 0, hi_s[np.maximum(prev_idx, 0)] - lo_s[np.maximum(prev_idx, 0)], np.nan)
say(f"- 前セッション レンジ R 中央値（USD）: " + "・".join(f"{wn} {np.nanmedian(Rng_prev[use_s & (pd.DatetimeIndex(us).year.values>=lo) & (pd.DatetimeIndex(us).year.values<=hi)]):.1f}" for wn,(lo,hi) in WIN.items()))

# セッションごとの取引足の範囲（inv はソート済み idx 順なので連続）
starts = np.r_[0, np.flatnonzero(np.diff(inv)) + 1]; ends = np.r_[starts[1:], len(inv)]

def first_passage(xlev, direction, s_i, delta, K):
    """セッション s_i 内で水準 xlev への direction（+1 上向き/−1 下向き）接近の最初の 1 回を探し、先着を返す。
    戻り値: None（接近なし） or dict(cross=1/0/None(censor), t_hr, pre60)"""
    a, b = starts[s_i], ends[s_i]
    c = C_k[a:b]
    if direction > 0:
        inband = (c >= xlev - delta) & (c < xlev)
        prev_out = np.r_[True, c[:-1] < xlev - delta]
    else:
        inband = (c <= xlev + delta) & (c > xlev)
        prev_out = np.r_[True, c[:-1] > xlev + delta]
    ev = np.flatnonzero(inband & prev_out)
    ev = ev[ev >= 1]  # 直前足が同セッション内に要る
    if len(ev) == 0: return None
    t = ev[0]
    seg = c[t + 1:t + 1 + K]
    if direction > 0:
        hit_c = np.flatnonzero(seg >= xlev + delta); hit_r = np.flatnonzero(seg <= xlev - 3 * delta)
    else:
        hit_c = np.flatnonzero(seg <= xlev - delta); hit_r = np.flatnonzero(seg >= xlev + 3 * delta)
    kc = hit_c[0] if len(hit_c) else 10**6; kr = hit_r[0] if len(hit_r) else 10**6
    if kc == 10**6 and kr == 10**6: cross = None
    else: cross = 1 if kc < kr else 0
    pre = (c[t] / c[max(t - 12, 0)] - 1) * 1e4 * direction  # 接近直前 1 時間のリターン（接近向き・bp）
    return dict(cross=cross, hr=hr_k[a + t], pre=pre, k=min(kc, kr) if cross is not None else K)

def collect(level_fn, labels, K, dfrac, name):
    """level_fn(s_i) -> list of (label, xlev, direction). 事象を DataFrame に集める。"""
    rows = []
    for s_i in np.flatnonzero(use_s):
        p = prev_idx[s_i]; Hp, Lp = hi_s[p], lo_s[p]; R = Hp - Lp
        delta = max(dfrac * R, DELTA_FLOOR)
        for lab, xlev, d in level_fn(s_i, Hp, Lp, R):
            r = first_passage(xlev, d, s_i, delta, K)
            if r is None: continue
            rows.append(dict(s=s_i, lab=lab, dir=d, cross=r["cross"], hr=r["hr"], pre=r["pre"], k=r["k"],
                             year=pd.Timestamp(us[s_i]).year, wd=wd_s[s_i], gap=gap_days[s_i]))
    df = pd.DataFrame(rows)
    say(f"- {name}: 事象 {len(df)}（K={K}・δ={dfrac:.2f}R）・censor 率 {df['cross'].isna().mean()*100:.1f}%・{time.time()-T0:.1f}s")
    return df

def levels_main(s_i, Hp, Lp, R):
    out = [("H", Hp, +1), ("L", Lp, -1)]
    for m in M_INT:
        out += [(f"I{m}", Lp + m * R, +1), (f"I{m}", Lp + m * R, -1)]
    for m in M_EXT_UP: out += [(f"E{m}", Lp + m * R, +1)]
    for m in M_EXT_DN: out += [(f"E{m}", Lp + m * R, -1)]
    return out

def levels_round(s_i, Hp, Lp, R):
    # G=50 の最近傍水準: セッション始値 ±2 本（接近が起き得る候補）・両向き
    a = starts[s_i]; c0 = C_k[a]
    base = np.floor(c0 / 50) * 50
    out = []
    for g in [base - 50, base, base + 50, base + 100]:
        out += [(f"G50", g, +1), (f"G50", g, -1)]
    return out

def two_prop(x1, n1, x0, n0):
    p1 = x1 / n1 if n1 else np.nan; p0 = x0 / n0 if n0 else np.nan
    se = np.sqrt(p1 * (1 - p1) / max(n1, 1) + p0 * (1 - p0) / max(n0, 1)) if n1 and n0 else np.nan
    return p1, p0, p1 - p0, se

def boot_D(df_t, df_p, B=2000):
    """セッション日ブロック bootstrap: D = p_cross(true) − p_cross(placebo)."""
    sd = np.unique(np.r_[df_t["s"].values, df_p["s"].values]); nd = len(sd)
    pos = {s: i for i, s in enumerate(sd)}
    it = np.array([pos[s] for s in df_t["s"].values]); ip = np.array([pos[s] for s in df_p["s"].values])
    xt = df_t["cross"].values.astype(float); xp = df_p["cross"].values.astype(float)
    ct_x = np.bincount(it, weights=xt, minlength=nd); ct_n = np.bincount(it, minlength=nd).astype(float)
    cp_x = np.bincount(ip, weights=xp, minlength=nd); cp_n = np.bincount(ip, minlength=nd).astype(float)
    idxb = rng.integers(0, nd, size=(B, nd))
    Db = ct_x[idxb].sum(1) / np.maximum(ct_n[idxb].sum(1), 1) - cp_x[idxb].sum(1) / np.maximum(cp_n[idxb].sum(1), 1)
    return Db.std(ddof=1)

def analyze(df, name, true_up="H", true_dn="L", pl_prefix="I", inject=None, extra=True):
    say(f"\n## {name}")
    res = {}
    dfr = df[df["cross"].notna()].copy(); dfr["cross"] = dfr["cross"].astype(int)
    for wn, (lo, hi) in WIN.items():
        w = dfr[(dfr["year"] >= lo) & (dfr["year"] <= hi)]
        for side, tl, d in [("上向き→H", true_up, +1), ("下向き→L", true_dn, -1)]:
            t_ = w[(w["lab"] == tl) & (w["dir"] == d)]; p_ = w[w["lab"].str.startswith(pl_prefix) & (w["dir"] == d)]
            if len(t_) < 20 or len(p_) < 20:
                say(f"- {wn} {side}: n 不足（true {len(t_)}・placebo {len(p_)}）"); continue
            p1, p0, D, se_i = two_prop(t_["cross"].sum(), len(t_), p_["cross"].sum(), len(p_))
            se_b = boot_D(t_, p_)
            zb = D / se_b
            z_rw_t = (p1 - 0.5) / np.sqrt(0.25 / len(t_)); z_rw_p = (p0 - 0.5) / np.sqrt(0.25 / len(p_))
            line = (f"- {wn} {side}: p_cross 真 {p1:.3f} (n {len(t_)}・RW z {z_rw_t:+.1f}) vs 擬似 {p0:.3f} (n {len(p_)}・RW z {z_rw_p:+.1f})"
                    f"・**D {D:+.4f}**（se_boot {se_b:.4f}・z_boot {zb:+.2f}・z_indep {D/se_i:+.2f}・MDE(2se) ±{2*se_b:.3f}）")
            if inject is not None and wn.startswith("在") and d > 0:
                xi = t_["cross"].values.copy(); flip = np.flatnonzero(xi == 1); nflip = int(round(inject * len(xi)))
                xi[flip[:nflip]] = 0; Di = xi.mean() - p0
                line += f"／陽性対照（CROSS −{inject*100:.0f} pp）D {Di:+.4f} z {Di/se_b:+.2f}"
            say(line)
            res[(wn, d)] = dict(D=D, z=zb, se=se_b, p1=p1, p0=p0, n1=len(t_), n0=len(p_))
            if extra:
                # 擬似水準 m 別
                by = p_.groupby("lab")["cross"].agg(["mean", "size"])
                say("  擬似水準別 p_cross: " + " ".join(f"{k}:{v['mean']:.3f}({int(v['size'])})" for k, v in by.iterrows()))
                # 外部水準（既ブレイク後）
                e_ = w[w["lab"].str.startswith("E") & (w["dir"] == d)]
                if len(e_):
                    bye = e_.groupby("lab")["cross"].agg(["mean", "size"])
                    say("  外部水準（既ブレイク・記述）: " + " ".join(f"{k}:{v['mean']:.3f}({int(v['size'])})" for k, v in bye.iterrows()))
                # 接近時刻・直前リターンの組成（反証 ii/iii）
                say(f"  接近 ET 時 中央値 真 {t_['hr'].median():.0f} vs 擬似 {p_['hr'].median():.0f}・直前 1h リターン（接近向き bp）中央値 真 {t_['pre'].median():+.1f} vs 擬似 {p_['pre'].median():+.1f}"
                    f"・censor 率 真 {1 - len(t_)/max(len(df[(df['lab']==tl)&(df['dir']==d)&(df['year']>=lo)&(df['year']<=hi)]),1):.3f}")
                # ET 時 FE 版 D（時刻ビン内差の加重平均）
                bins = [0, 3, 8, 12, 17, 24]
                num = den = 0.0
                for b0, b1 in zip(bins[:-1], bins[1:]):
                    tt = t_[(t_["hr"] >= b0) & (t_["hr"] < b1)]; pp = p_[(p_["hr"] >= b0) & (p_["hr"] < b1)]
                    if len(tt) >= 10 and len(pp) >= 10:
                        wgt = 1 / (tt["cross"].var(ddof=1) / len(tt) + pp["cross"].var(ddof=1) / len(pp) + 1e-9)
                        num += wgt * (tt["cross"].mean() - pp["cross"].mean()); den += wgt
                if den > 0: say(f"  ET 時 FE 版 D {num/den:+.4f}（se {1/np.sqrt(den):.4f}・z {num/den*np.sqrt(den):+.2f}）")
                # 月曜（週末跨ぎ）除外
                tm = t_[t_["gap"] == 1]; pm = p_[p_["gap"] == 1]
                if len(tm) >= 20 and len(pm) >= 20:
                    say(f"  直前セッションが前日（週末跨ぎ除外）: 真 {tm['cross'].mean():.3f} (n {len(tm)}) vs 擬似 {pm['cross'].mean():.3f} (n {len(pm)})・D {tm['cross'].mean()-pm['cross'].mean():+.4f}")
    return res

# ---------------- 主走 ----------------
df_main = collect(levels_main, None, K_MAIN, DELTA_FRAC, "主（K=24・δ=0.05R）")
res_main = analyze(df_main, f"主セル H_BARRIER（K={K_MAIN}・δ=0.05R・擬似 = レンジ内部 m∈{M_INT}）", inject=0.05)

say("\n### 判定（事前規則・条件は 1 行ずつ）")
verdict = {}
for d, nm in [(+1, "D_H（上向き→前セッション高値）"), (-1, "D_L（下向き→前セッション安値）")]:
    a = res_main.get(("在 2010-20", d)); b = res_main.get(("外 2021-26H1", d))
    if a is None or b is None: say(f"- {nm}: n 不足"); continue
    c1 = abs(a["D"]) >= 0.03; c2 = abs(a["z"]) >= 2.5; c3 = np.sign(a["D"]) == np.sign(b["D"]); c4 = abs(b["z"]) >= 1.5
    say(f"- {nm}: 在 |D|≥0.03 {c1} ({a['D']:+.4f})・在 |z|≥2.5 {c2} ({a['z']:+.2f})・外 同符号 {c3} ({b['D']:+.4f})・外 |z|≥1.5 {c4} ({b['z']:+.2f})"
        f" → **{'PASS' if (c1 and c2 and c3 and c4) else 'null'}**・方向 {'磁石(D>0)' if a['D']>0 else '障壁(D<0)'}（在の符号）")
    verdict[nm] = (c1 and c2 and c3 and c4)

# ---------------- 副: K=12・δ=0.10R ----------------
df_k12 = collect(levels_main, None, K_ALT, DELTA_FRAC, "副（K=12・δ=0.05R）")
analyze(df_k12, "副: K=12（1 時間）", extra=False)
df_d10 = collect(levels_main, None, K_MAIN, 0.10, "副（K=24・δ=0.10R）")
analyze(df_d10, "副: δ=0.10R", extra=False)

# ---------------- 陽性対照: G=50 キリ番（c26 磁石の再現） ----------------
df_g = collect(levels_round, None, K_MAIN, DELTA_FRAC, "陽性対照 G=50（両向き）")
say("\n## 陽性対照: G=50 キリ番の p_cross（同じ機械・擬似対照は主走の内部水準）")
dfr_g = df_g[df_g["cross"].notna()]; dfr_m = df_main[df_main["cross"].notna()]
for wn, (lo, hi) in WIN.items():
    g = dfr_g[(dfr_g["year"] >= lo) & (dfr_g["year"] <= hi)]; m = dfr_m[(dfr_m["year"] >= lo) & (dfr_m["year"] <= hi) & dfr_m["lab"].str.startswith("I")]
    for d, nm in [(+1, "上向き"), (-1, "下向き")]:
        gg = g[g["dir"] == d]; mm = m[m["dir"] == d]
        if len(gg) < 20: continue
        p1, p0, D, se_i = two_prop(gg["cross"].sum(), len(gg), mm["cross"].sum(), len(mm))
        se_b = boot_D(gg, mm)
        say(f"- {wn} {nm}: G50 p_cross {p1:.3f} (n {len(gg)}) vs 内部擬似 {p0:.3f} (n {len(mm)})・D {D:+.4f}（z_boot {D/se_b:+.2f}）・RW z {(p1-0.5)/np.sqrt(0.25/len(gg)):+.1f}")

# ---------------- ゲート ㉛（本番 path・記述） ----------------
say("\n## ゲート ㉛（記述）: 前セッション高値/安値が entry→TP の道に挟まる scan 本")
TR = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")))["trades"]
te = np.array([t["entry_time"] for t in TR], dtype=np.int64)
pos = np.searchsorted(TS, te); ok = (pos < len(TS)) & (TS[np.minimum(pos, len(TS)-1)] == te)
say(f"- scan 本 {len(TR)}・entry_time が npz 格子に一致 {ok.sum()}")
et_e = pd.to_datetime(te, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
sess_e = (et_e + pd.Timedelta(hours=6)).normalize().values.astype("datetime64[D]")
si = np.searchsorted(us, sess_e); si_ok = (si < ns) & (us[np.minimum(si, ns-1)] == sess_e) & ok
si_ok &= use_s[np.minimum(si, ns-1)]
rows = []
for i in np.flatnonzero(si_ok):
    t = TR[i]; p = prev_idx[si[i]]; Hp, Lp = hi_s[p], lo_s[p]
    entry = C[pos[i]]; s = 1 if t["side"] == "BUY" else -1
    tp = entry + s * t["b"] * t["risk"]
    Zt = (entry < Hp <= tp) if s > 0 else (tp <= Lp < entry)
    ft = 0.1 / t["risk"]; Rs = t["R"] + (ft if t["exit"] in ("SL", "TP") else 0.0)
    rows.append(dict(year=t["year"], Z=int(Zt), R=Rs, side=t["side"], b=t["b"]))
g = pd.DataFrame(rows)
for wn, (lo, hi) in WIN.items():
    w = g[(g["year"] >= lo) & (g["year"] <= hi)]
    z1, z0 = w[w["Z"] == 1]["R"], w[w["Z"] == 0]["R"]
    if len(z1) < 20: say(f"- {wn}: Z=1 n {len(z1)} 不足"); continue
    dm = z1.mean() - z0.mean(); se = np.sqrt(z1.var(ddof=1) / len(z1) + z0.var(ddof=1) / len(z0))
    say(f"- {wn}: Z=1 n {len(z1)} R̄* {z1.mean():+.3f}（b 中央値 {z1['b'].median() if False else w[w['Z']==1]['b'].median():.2f}） vs Z=0 n {len(z0)} {z0.mean():+.3f}（b {w[w['Z']==0]['b'].median():.2f}）"
        f"・Δμ {dm:+.3f}R (t {dm/se:+.2f}・MDE {2*se:.3f})・ゲート在閾 0.048 → {'印字' if (wn.startswith('在') and abs(dm)>=0.048) else '—'}")
say(f"- 注意: Z=1 は TP が遠い本に偏る（b 中央値を併記）＝幾何の差を含む記述。")

say(f"\n- 実行 {time.time()-T0:.1f} s・書込 {OUT}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
