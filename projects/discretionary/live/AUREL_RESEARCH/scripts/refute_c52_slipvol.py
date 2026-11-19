# -*- coding: utf-8 -*-
"""
REFUTE cycle52 (2026-11-19 09:30 反証レーン) — 対象 = c52 の唯一の規則上の正 H_S2
=====================================================================================
対象の主張（c52 06:40・findings/2026-11-19.md L45・cells.csv）:
  H_S2 PASS（規則上）: Spearman rho(sl_slip_pt, atr14) = +0.141（n 157・置換 p(片側) 0.047）
                      ∧ 滑り比 sl_slip/atr14 の帯 A−B |t| = 0.80 < 2
  読み: 「SL 滑りは時計に固有分を持たず、弱くボラに追随する（ボラの顔）」
  併せて壊しに行く副産物 (b): 「SL 滑り 合計 2.09R（gross +55.4R の 3.8%）の 44% が週末持ち越し 1 本
                      （S-0521・7.179 USD = 0.924R）＝滑りは時計でなく週末ギャップの尻尾に住む」
  （H_S1 は既に null＝壊す余地なし。c52 自身の最重大反証 (i) は「sim は実約定でない」＝実 fill 無しでは決着不能
    としてあるので、そこには寄らず、sim の数字をそのまま受け入れたまま統計側だけで壊しに行く。）

補遺 C の 6 手を H_S2 に当てる:
  T0  複製（同一母集団・同一推定器で c52 の 20 セルを再現。ledger は 09:30 に 10411 行へ成長 → 時刻 cut で n157 を復元）
  T0b 推定器: c52 の spearman() は argsort 二段＝順序順位でタイ平均をしない。sl_slip は =0 が 5%（タイ）
      → scipy の タイ補正 Spearman と比較。rho/p が閾値 0.05 を跨ぐなら PASS は実装の産物。
  T0c 置換 p の モンテカルロ誤差: 3000 draws・p=0.047 → se(p)=sqrt(p(1-p)/3000)=0.0039＝95%CI [0.039,0.055]
      ＝0.05 と分離できない。200k draws で解像度を上げて再判定。
  A1  多重検定補正: c52 の判定セルは 2（H_S1・H_S2）→ Bonferroni α 0.025・Holm。さらに H_S2 自身の連言 2 条件。
  A2  プラセボ/帰無の作り直し（★本命）: atr14 は日内ほぼ一定・SL は同日に束で出る → i.i.d. シャッフルは帰無 sd を
      過小評価する。(a) 日ブロック置換 (b) 円環シフト (c) 日クラスタ bootstrap CI (d) 有効 n = 日数
  A3  共通トレンド交絡: rho(atr14, t)・rho(sl_slip, t) が同符号なら rho は見かけ。時刻を統制した偏 Spearman。
  A4  機構の同定（単位交絡）: c52 自身が rho(slip, risk)=+0.213 > rho(slip, atr)=+0.141 を印字している。
      risk=|entry−sl| は壁距離の機械的関数。偏相関 rho(slip,atr|risk) と rho(slip,risk|atr) を比べ、
      「ボラの顔」でなく「SL 距離の顔」なら機構の帰属が壊れる。R 単位 rho(slip/risk, atr14) も見る。
  A5  影響力: LOO（1 本抜き 157 通り）・上位 k 抜き・日単位 jackknife（LODO）
  A6  別の在外分割: c52 は exit_time 前後半のみ。side／月（9/10/11）／奇偶日／wall_kind で符号安定性。
  A7  サバイバーシップ（c52 の留保 (iii) の拡張）: 注釈欠落 45/202（22%）が atr14 に依存するなら 157 は
      共変量で選択された標本＝rho にバイアス。c52 は R と（未確認の）時刻しか見ていない。
  A8  コスト 2 倍 ＋ 副産物 (b): sl_slip ×2 での gross 比・max share の jackknife・
      週末持ち越しラベルの置換検定（n=2）・再開 SL 率 2/8 vs 基準 SL 率。
  A9  陽性対照 ＋ rho の MDE: 既知の単調関係を注入して各帰無が検出できるか・最小検出 rho*。

判定規則（数字を見る前に固定）:
  BREAK-1 成立 ⇔ A2 の いずれか 1 つ以上の正しい帰無（日ブロック置換 / 円環シフト / 日クラスタ bootstrap）で
                 p(片側) ≥ 0.05 または 95%CI が 0 を含む。
  BREAK-2 成立 ⇔ A1 の Bonferroni/Holm 閾値（α 0.025）を p が超える。
  BREAK-3 成立 ⇔ A3 の 偏 Spearman（時刻統制）で rho が符号反転 または |rho| が半分未満。
  BREAK-4 成立 ⇔ A4 で rho(slip,atr|risk) が |0.07| 未満（半減）かつ rho(slip,risk|atr) が それを上回る
                 ＝「ボラ」への帰属が同定されない。
  BREAK-5 成立 ⇔ A5 の 日単位 jackknife で rho の符号が反転する日が 1 つ以上ある。
  BREAK-6 成立 ⇔ A6 の 4 つの別分割のうち 1 つ以上で rho ≤ 0。
  BREAK-7 成立 ⇔ A7 で 注釈欠落本の atr14 分布が 注釈あり本と Welch |t| ≥ 2 で違う。
  BREAK-8 成立 ⇔ A8 で 週末ラベルの置換 p(片側) ≥ 0.05（＝「尻尾は週末」が 1 本の事後ラベル）。
  各 BREAK は 1 条件 1 行で印字（11-19 03:40 の方法論候補 72: 連言で書いて not broken を印字する再発を防ぐ）。
  総合: BREAK-1 または BREAK-2 が成立 → H_S2 の「PASS（規則上）」は broken。
        A4/A3 が成立 → 「ボラの顔」という読み（機構の帰属）は broken（相関の有無とは別に数える）。
        BREAK-8 成立 → 副産物 (b) の「週末ギャップの尻尾」は broken。

安全: 読むのは ../setup_ledger.jsonl のみ（読取・編集なし）。書込は AUREL_RESEARCH/data/ のみ。
      発注/デモ発注/本番編集/プロセス・schtask・執行機・ライブサーバ接触/MT5 接続/プロップ参照/秘密 なし。
      D2: 台帳は 2026-09〜11 の 1 窓（近年）のみ・16 年一括なし。seed 20261119（c52 と同一）。
"""
import json, time, collections, itertools
from datetime import datetime, timezone, timedelta, date
from zoneinfo import ZoneInfo
import numpy as np
from scipy import stats

T0 = time.time()
SEED = 20261119
rng = np.random.default_rng(SEED)
ET = ZoneInfo("America/New_York")
LEDGER = "../setup_ledger.jsonl"
OUT = "data/refute_c52_slipvol_result.md"
lines = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

BREAKS = {}
def brk(key, cond, text):
    BREAKS[key] = bool(cond)
    P(f"  [{key}] {'BREAK' if cond else 'not broken'} — {text}")

# ============================== 母集団の復元（c52 と同一ロジック） ==============================
rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]
setups = [r for r in rows if r.get("kind") == "setup" and "id" in r]
st = {r["id"]: dict(r) for r in setups}
n_upd = 0
for r in rows:
    if r.get("kind") == "update":
        tid = r.get("target")
        if tid in st:
            n_upd += 1
            for k, v in r.items():
                if k not in ("kind", "target"):
                    st[tid][k] = v
fin = list(st.values())
P(f"# REFUTE c52 — H_S2 rho(sl_slip, atr14) を壊しに行く（実行 {datetime.now().strftime('%Y-%m-%d %H:%M')}）")
P("")
P(f"rows {len(rows)} setup {len(setups)} update 適用 {n_upd}  （c52 06:38 時点 rows 10396 setup 566 → 成長 {len(rows)-10396} 行）")

def build(rs):
    out = []; n_top_only = n_mismatch = n_noann = 0
    for r in rs:
        ra = r.get("reaccel") or {}
        if r.get("exit_reason") and not ra.get("exit_reason"): n_top_only += 1
        er = ra.get("exit_reason")
        if not er: continue
        ent, sl, et, en_t = ra.get("entry"), ra.get("sl"), ra.get("exit_time"), ra.get("entry_time")
        if ent is None or sl is None or et is None: continue
        ann_ok = r.get("exit_time") == et
        if r.get("exit_time") is None: n_noann += 1
        elif not ann_ok: n_mismatch += 1
        out.append(dict(id=r["id"], er=er, R=ra.get("R"), exit_time=int(et),
                        entry_time=int(en_t) if en_t else None,
                        risk=abs(float(ent) - float(sl)), side=r.get("side"), wall_kind=r.get("wall_kind"),
                        atr14=(r.get("features") or {}).get("atr14"),
                        slip=r.get("slip_pt") if ann_ok else None,
                        sl_slip=r.get("sl_slip_pt") if ann_ok else None,
                        tp_ok=r.get("tp_fill_ok") if ann_ok else None, spread=r.get("spread_pt"),
                        entry_top=r.get("entry"), entry_re=ra.get("entry"), hold=ra.get("hold_bars")))
    return out, n_top_only, n_mismatch, n_noann

closed_now, n_top_only, n_mismatch, n_noann = build(fin)
P(f"reaccel closed（現在）{len(closed_now)} 内訳 {dict(collections.Counter(c['er'] for c in closed_now))}"
  f"  衛生: top-level のみ {n_top_only}・注釈なし {n_noann}・不一致 {n_mismatch}  （c52: 387 / 93・57・43）")

# c52 の n157 を復元する時刻 cut を探す（ledger 成長の影響を外す）
sl_now = [c for c in closed_now if c["er"] == "SL" and c["sl_slip"] is not None]
P(f"SL×注釈あり（現在）n {len(sl_now)}  （c52: 157）")
CUT = None
if len(sl_now) != 157:
    ts_sorted = sorted(c["exit_time"] for c in sl_now)
    if len(sl_now) > 157:
        CUT = ts_sorted[156]
        P(f"→ 成長分を外すため exit_time ≤ {datetime.fromtimestamp(CUT, timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC で cut")
if CUT is not None:
    closed = [c for c in closed_now if c["exit_time"] <= CUT]
else:
    closed = closed_now
sl_an = sorted([c for c in closed if c["er"] == "SL" and c["sl_slip"] is not None], key=lambda c: c["exit_time"])
sl_all = [c for c in closed if c["er"] == "SL"]
sl_na = [c for c in sl_all if c["sl_slip"] is None]
for c in closed:
    d = datetime.fromtimestamp(c["exit_time"], timezone.utc).astimezone(ET)
    c["h"] = d.hour; c["et_date"] = d.date(); c["wd"] = d.weekday()
    c["month"] = d.month
    if c["entry_time"]:
        di = datetime.fromtimestamp(c["entry_time"], timezone.utc).astimezone(ET)
        c["h_in"] = di.hour; c["in_date"] = di.date(); c["in_wd"] = di.weekday()
    else:
        c["h_in"] = None; c["in_date"] = None; c["in_wd"] = None
for c in sl_an:
    c["A"] = 8 <= c["h"] <= 9

xa = [c for c in sl_an if c["atr14"]]
X = np.array([c["sl_slip"] for c in xa], float)       # SL 滑り USD
Y = np.array([c["atr14"] for c in xa], float)         # atr14 USD
RK = np.array([c["risk"] for c in xa], float)         # |entry-sl| USD
Tm = np.array([c["exit_time"] for c in xa], float)    # 時刻（トレンド統制用）
DAY = np.array([c["et_date"].toordinal() for c in xa])
N = len(xa)

# ============================== T0 複製 ==============================
P("")
P("## T0 複製（c52 と同一母集団・同一推定器）")
def sp_c52(x, y):
    """c52 の spearman(): argsort 二段＝順序順位・タイ平均なし"""
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])
rho_c52 = sp_c52(X, Y)
rho_scipy, p_scipy = stats.spearmanr(X, Y)
P(f"- n {N}（c52 157）  rho [c52 推定器] {rho_c52:+.4f}（c52 公表 +0.141）"
  f"  rho(sl_slip, risk) {sp_c52(X, RK):+.4f}（c52 +0.213）")
P(f"- 在(前半) {sp_c52(X[:N//2], Y[:N//2]):+.4f}（c52 +0.152）／外(後半) {sp_c52(X[N//2:], Y[N//2:]):+.4f}（c52 +0.177）")
med = np.median(X); P(f"- sl_slip 中央値 {med:+.4f}・平均 {X.mean():+.4f}・p90 {np.percentile(X,90):+.4f}・max {X.max():+.4f} USD"
                      f"（c52 +0.027/+0.103/+0.149/+7.179）")
P(f"→ 複製 {'OK' if abs(rho_c52-0.141)<0.004 and N==157 else '不一致（以下は復元した母集団の数字）'}")

# ---- T0b タイ補正 ----
P("")
P("## T0b 推定器: タイ（sl_slip=0 が 5%）の扱い")
nt_x = N - len(np.unique(X)); nt_y = N - len(np.unique(Y))
P(f"- タイで潰れている本数 sl_slip {nt_x}・atr14 {nt_y}（ユニーク {len(np.unique(X))}／{len(np.unique(Y))}）")
P(f"- rho: c52 の順序順位 {rho_c52:+.4f}  vs scipy タイ平均順位 {rho_scipy:+.4f}  差 {rho_scipy-rho_c52:+.4f}"
  f"；scipy 漸近 p(片側) {p_scipy/2:.4f}")
brk("BREAK-0b", abs(rho_scipy - rho_c52) > 0.02, f"タイ補正で rho が 0.02 超動く（{rho_c52:+.4f}→{rho_scipy:+.4f}）")

# ---- T0c 置換 p の MC 誤差 ----
P("")
P("## T0c 置換 p の モンテカルロ解像度（c52 は 3000 draws で p 0.047）")
se3000 = np.sqrt(0.047 * 0.953 / 3000)
P(f"- c52 の p=0.047 の MC se = {se3000:.4f} → 95%CI [{0.047-1.96*se3000:.4f}, {0.047+1.96*se3000:.4f}]"
  f"  ＝閾値 0.05 を {'含む（分離不能）' if 0.047+1.96*se3000 > 0.05 else '含まない'}")
NPERM = 200000
rx_obs = stats.rankdata(X); ry_obs = stats.rankdata(Y)
rx_c = rx_obs - rx_obs.mean(); ry_c = ry_obs - ry_obs.mean()
den = np.sqrt((rx_c**2).sum() * (ry_c**2).sum())
cnt = 0
for _ in range(NPERM):
    cnt += (rx_c @ rng.permutation(ry_c)) / den >= rho_scipy
p_iid = (cnt + 1) / (NPERM + 1)
P(f"- i.i.d. 置換 {NPERM} draws（タイ補正順位・片側）p = {p_iid:.5f}"
  f"  MC se {np.sqrt(p_iid*(1-p_iid)/NPERM):.5f}")
P(f"→ c52 の帰無（i.i.d.）でも p は {'0.05 の両側にまたがらず ' + ('有意' if p_iid<0.05 else '非有意')}")

# ============================== A1 多重検定 ==============================
P("")
P("## A1 多重検定補正（c52 が事前固定した判定セルは 2: H_S1 片側・H_S2）")
p_hs1 = 0.650  # c52 在の H_S1 置換 p
ps = {"H_S1(在)": p_hs1, "H_S2(rho)": p_iid}
P(f"- Bonferroni α = 0.05/2 = 0.025 → H_S2 p {p_iid:.4f} vs 0.025")
order = sorted(ps.items(), key=lambda kv: kv[1])
holm = []
for i, (k, p) in enumerate(order):
    thr = 0.05 / (2 - i)
    holm.append((k, p, thr, p < thr))
    P(f"- Holm 段 {i+1}: {k} p {p:.4f} vs 閾値 {thr:.4f} → {'通過' if p < thr else '棄却できない'}")
    if p >= thr: break
brk("BREAK-2", p_iid >= 0.025, f"Bonferroni 閾値 0.025 を H_S2 の p {p_iid:.4f} が超える")

# ============================== A2 帰無の作り直し（本命） ==============================
P("")
P("## A2 帰無の作り直し — atr14 は日内ほぼ一定・SL は同日に束で出る（i.i.d. 置換は帰無 sd を過小評価する）")
dcount = collections.Counter(DAY)
P(f"- 束の実態: SL 本 {N} が ET 日 {len(dcount)} 日に分布（1 日あたり 平均 {N/len(dcount):.2f} 本・max {max(dcount.values())} 本）")
# 日内 atr14 の分散分解（ICC）
grand = Y.mean(); ss_tot = ((Y - grand)**2).sum()
ss_b = sum(len(Y[DAY == d]) * (Y[DAY == d].mean() - grand)**2 for d in np.unique(DAY))
P(f"- atr14 の日間分散シェア（R²_between）= {ss_b/ss_tot:.3f}  ＝日が決まれば atr14 はほぼ決まる"
  f"（日内 sd 平均 {np.mean([Y[DAY==d].std() for d in np.unique(DAY) if (DAY==d).sum()>1]):.3f} vs 全体 sd {Y.std():.3f} USD）")
ss_bx = sum(len(X[DAY == d]) * (X[DAY == d].mean() - X.mean())**2 for d in np.unique(DAY))
P(f"- sl_slip の日間分散シェア = {ss_bx/((X-X.mean())**2).sum():.3f}")

# (a) 日ブロック置換: 日の順序を入れ替えて y を時間順の x に当て直す
P("")
P("### A2(a) 日ブロック置換（日の順序をシャッフル・日内の束と atr14 の日内一定性を保つ）")
days_uniq = [d for d in dict.fromkeys(DAY)]           # 時間順
blocks = [np.where(DAY == d)[0] for d in days_uniq]
NB = 20000
cnt = 0; null_b = np.empty(NB)
for i in range(NB):
    perm = rng.permutation(len(blocks))
    yb = np.concatenate([Y[blocks[j]] for j in perm])
    r = stats.spearmanr(X, yb).statistic
    null_b[i] = r; cnt += r >= rho_scipy
p_block = (cnt + 1) / (NB + 1)
P(f"- 日ブロック置換 {NB} draws: p(片側) = {p_block:.4f}"
  f"  帰無 sd {null_b.std():.4f}（i.i.d. 帰無 sd {1/np.sqrt(N-1):.4f} → 膨張率 {null_b.std()*np.sqrt(N-1):.2f}×）")
P(f"  帰無分布 95 パーセンタイル rho = {np.percentile(null_b,95):+.4f}  vs 観測 {rho_scipy:+.4f}")

# (b) 円環シフト
P("")
P("### A2(b) 円環シフト（y の自己相関を厳密に保つ・156 通りの完全列挙）")
shifts = np.arange(1, N)
null_s = np.array([stats.spearmanr(X, np.roll(Y, k)).statistic for k in shifts])
p_shift = (np.sum(null_s >= rho_scipy) + 1) / (len(shifts) + 1)
P(f"- 円環シフト（全 {len(shifts)} 通り）: p(片側) = {p_shift:.4f}"
  f"  帰無 sd {null_s.std():.4f}（膨張率 {null_s.std()*np.sqrt(N-1):.2f}×）"
  f"  95 パーセンタイル {np.percentile(null_s,95):+.4f}")
P(f"  観測 rho の順位 = {int(np.sum(null_s >= rho_scipy))+1} / {len(shifts)+1}")

# (c) 日クラスタ bootstrap
P("")
P("### A2(c) 日クラスタ bootstrap（日を復元抽出・束の相関を保った CI）")
NBOOT = 20000
boot = np.empty(NBOOT); nb_ok = 0
for i in range(NBOOT):
    pick = rng.integers(0, len(blocks), len(blocks))
    idx = np.concatenate([blocks[j] for j in pick])
    xb, yb = X[idx], Y[idx]
    if len(np.unique(xb)) < 3 or len(np.unique(yb)) < 3:
        boot[i] = np.nan; continue
    boot[i] = stats.spearmanr(xb, yb).statistic; nb_ok += 1
boot = boot[~np.isnan(boot)]
lo, hi = np.percentile(boot, [2.5, 97.5])
P(f"- 日クラスタ bootstrap（{len(boot)} 有効）: rho 95%CI = [{lo:+.4f}, {hi:+.4f}]"
  f"  P(rho ≤ 0) = {np.mean(boot <= 0):.4f}  中央値 {np.median(boot):+.4f}")
# 本単位 bootstrap（比較用・c52 が暗黙に仮定した独立性）
b2 = np.empty(5000)
for i in range(5000):
    idx = rng.integers(0, N, N)
    b2[i] = stats.spearmanr(X[idx], Y[idx]).statistic if len(np.unique(X[idx]))>2 else np.nan
b2 = b2[~np.isnan(b2)]
P(f"- 参考: 本単位 bootstrap 95%CI = [{np.percentile(b2,2.5):+.4f}, {np.percentile(b2,97.5):+.4f}]"
  f"  P(rho≤0) {np.mean(b2<=0):.4f}  ＝独立を仮定すると CI は {(hi-lo)/(np.percentile(b2,97.5)-np.percentile(b2,2.5)):.2f} 倍狭く見える")

# (d) 有効 n
P("")
P("### A2(d) 有効 n（日が単位なら）")
nd = len(dcount)
t_157 = rho_scipy * np.sqrt((N - 2) / (1 - rho_scipy**2))
t_nd = rho_scipy * np.sqrt((nd - 2) / (1 - rho_scipy**2))
P(f"- rho {rho_scipy:+.4f}: n=157 なら t {t_157:+.3f}（片側 p {1-stats.t.cdf(t_157, N-2):.4f}）／"
  f"n=日数 {nd} なら t {t_nd:+.3f}（片側 p {1-stats.t.cdf(t_nd, nd-2):.4f}）")
# 日平均に潰した相関（最も保守的）
dX = np.array([X[DAY == d].mean() for d in np.unique(DAY)])
dY = np.array([Y[DAY == d].mean() for d in np.unique(DAY)])
rd, pd_ = stats.spearmanr(dX, dY)
P(f"- 日平均に潰した rho（n {len(dX)} 日）= {rd:+.4f}（両側 p {pd_:.4f}・片側 {pd_/2:.4f}）")

brk("BREAK-1", (p_block >= 0.05) or (p_shift >= 0.05) or (lo <= 0),
    f"正しい帰無で非有意 — 日ブロック置換 p {p_block:.4f}・円環シフト p {p_shift:.4f}・日クラスタ CI 下限 {lo:+.4f}")

# ============================== A3 共通トレンド ==============================
P("")
P("## A3 共通トレンド交絡（9 週の窓で atr14 と USD 建ての滑りが同時に増えていれば rho は見かけ）")
r_yt = stats.spearmanr(Y, Tm).statistic; r_xt = stats.spearmanr(X, Tm).statistic
P(f"- rho(atr14, 時刻) = {r_yt:+.4f}  rho(sl_slip, 時刻) = {r_xt:+.4f}"
  f"  （同符号なら共通トレンドで rho が湧く）")
def partial_sp(x, y, *z):
    """順位化してから偏相関"""
    r = np.column_stack([stats.rankdata(v) for v in (x, y) + z])
    C = np.corrcoef(r, rowvar=False)
    P_ = np.linalg.pinv(C)
    return -P_[0, 1] / np.sqrt(P_[0, 0] * P_[1, 1])
rp_t = partial_sp(X, Y, Tm)
k = 3
t_p = rp_t * np.sqrt((N - 1 - k) / max(1e-12, 1 - rp_t**2))
P(f"- 偏 Spearman rho(sl_slip, atr14 | 時刻) = {rp_t:+.4f}（単純 {rho_scipy:+.4f} の {rp_t/rho_scipy:.2f} 倍）"
  f"  t {t_p:+.2f}")
brk("BREAK-3", (rp_t * rho_scipy < 0) or (abs(rp_t) < abs(rho_scipy) / 2),
    f"時刻を統制すると rho が符号反転 or 半減（{rho_scipy:+.4f} → {rp_t:+.4f}）")

# ============================== A4 機構の同定 ==============================
P("")
P("## A4 機構の同定 — 「ボラの顔」か「SL 距離の顔」か（c52 自身が rho(slip,risk)=+0.213 > rho(slip,atr)=+0.141 を印字）")
r_xr = stats.spearmanr(X, RK).statistic; r_yr = stats.spearmanr(Y, RK).statistic
P(f"- 単純: rho(slip, atr14) {rho_scipy:+.4f}／rho(slip, risk) {r_xr:+.4f}／rho(atr14, risk) {r_yr:+.4f}")
rp_atr = partial_sp(X, Y, RK)
rp_rk = partial_sp(X, RK, Y)
P(f"- 偏: rho(slip, atr14 | risk) = {rp_atr:+.4f}   rho(slip, risk | atr14) = {rp_rk:+.4f}")
# R 単位（滑りを risk で割る＝台帳の実効単位）に直すと何が残るか
XR = X / RK
r_Rr = stats.spearmanr(XR, Y)
P(f"- R 単位: rho(sl_slip/risk, atr14) = {r_Rr.statistic:+.4f}（両側 p {r_Rr.pvalue:.4f}）"
  f"  ＝台帳が実際に負うコスト単位では {'符号維持' if r_Rr.statistic>0 else '符号反転'}")
r_Rr2 = stats.spearmanr(XR, RK)
P(f"- R 単位: rho(sl_slip/risk, risk) = {r_Rr2.statistic:+.4f}（両側 p {r_Rr2.pvalue:.4f}）")
# 滑り比 sl_slip/atr14 が atr14 と無関係か（比例性の検査）
r_ratio = stats.spearmanr(X / Y, Y)
P(f"- 比例性: rho(sl_slip/atr14, atr14) = {r_ratio.statistic:+.4f}（両側 p {r_ratio.pvalue:.4f}）"
  f"  ＝0 でなければ「滑りはボラに比例」という形も成り立たない")
brk("BREAK-4", abs(rp_atr) < 0.07 and abs(rp_rk) > abs(rp_atr),
    f"risk を統制すると atr14 の寄与が半減以下（{rho_scipy:+.4f}→{rp_atr:+.4f}）かつ risk の寄与 {rp_rk:+.4f} が上回る")

# ============================== A5 影響力 ==============================
P("")
P("## A5 影響力（LOO・上位 k 抜き・日単位 jackknife）")
loo = np.array([stats.spearmanr(np.delete(X, i), np.delete(Y, i)).statistic for i in range(N)])
iw = int(np.argmin(loo)); ib = int(np.argmax(loo))
P(f"- LOO（157 通り）rho 範囲 [{loo.min():+.4f}, {loo.max():+.4f}]"
  f"  最も効いている 1 本 = {xa[iw]['id']}（抜くと {loo[iw]:+.4f}）")
ordX = np.argsort(-X)
for kk in (1, 2, 3, 5):
    keep = np.setdiff1d(np.arange(N), ordX[:kk])
    r = stats.spearmanr(X[keep], Y[keep]).statistic
    P(f"- 滑り上位 {kk} 本を抜く → rho {r:+.4f}（n {len(keep)}）")
lodo = {}
for d in np.unique(DAY):
    keep = DAY != d
    if keep.sum() < 10: continue
    lodo[d] = stats.spearmanr(X[keep], Y[keep]).statistic
vals = np.array(list(lodo.values()))
neg = [(date.fromordinal(int(d)), v) for d, v in lodo.items() if v <= 0]
P(f"- 日単位 jackknife（LODO・{len(lodo)} 日）rho 範囲 [{vals.min():+.4f}, {vals.max():+.4f}]"
  f"  符号反転する日 {len(neg)} 日" + (f": {neg[:4]}" if neg else ""))
worst = sorted(lodo.items(), key=lambda kv: kv[1])[:3]
P("  最も効いている日: " + ", ".join(f"{date.fromordinal(int(d))}(抜くと {v:+.4f}・n{int((DAY==d).sum())})" for d, v in worst))
brk("BREAK-5", len(neg) >= 1, f"1 日抜くだけで rho が符号反転する日が {len(neg)} 日")

# ============================== A6 別の在外分割 ==============================
P("")
P("## A6 別の在外分割（c52 は exit_time 前後半のみ）")
def split_report(name, keyf):
    groups = collections.defaultdict(list)
    for i, c in enumerate(xa): groups[keyf(c)].append(i)
    outs = []
    for g, idx in sorted(groups.items(), key=lambda kv: str(kv[0])):
        if len(idx) < 12: outs.append(f"{g}: n{len(idx)}(不足)"); continue
        idx = np.array(idx)
        r = stats.spearmanr(X[idx], Y[idx])
        outs.append(f"{g}: rho {r.statistic:+.4f} (n {len(idx)}・両側 p {r.pvalue:.3f})")
    P(f"- {name}: " + " | ".join(outs))
    return [stats.spearmanr(X[np.array(i)], Y[np.array(i)]).statistic
            for g, i in groups.items() if len(i) >= 12]
r_side = split_report("side", lambda c: c["side"])
r_mon = split_report("決着月", lambda c: c["month"])
r_par = split_report("奇偶日（ET 日の ordinal）", lambda c: "偶日" if c["et_date"].toordinal() % 2 == 0 else "奇日")
r_wk = split_report("wall_kind", lambda c: c["wall_kind"])
r_h = split_report("決着 ET 午前/午後", lambda c: "ET00-11" if c["h"] <= 11 else "ET12-23")
allsub = r_side + r_mon + r_par + r_wk + r_h
nneg = sum(1 for v in allsub if v <= 0)
P(f"- 全 {len(allsub)} 部分集合のうち rho ≤ 0 は {nneg} 個（符号安定性）")
brk("BREAK-6", nneg >= 1, f"別分割の部分集合 {len(allsub)} 個中 {nneg} 個で rho ≤ 0")

# ============================== A7 サバイバーシップ（c52 留保 (iii) の拡張） ==============================
P("")
P("## A7 サバイバーシップ: 注釈欠落 45/202 は共変量 atr14 に依存するか（c52 は R と時刻しか見ていない）")
P(f"- SL 本 {len(sl_all)}・注釈あり {len(sl_an)}・欠落 {len(sl_na)}（{len(sl_na)/max(1,len(sl_all)):.1%}）")
a_an = np.array([c["atr14"] for c in sl_an if c["atr14"]], float)
a_na = np.array([c["atr14"] for c in sl_na if c["atr14"]], float)
if len(a_na) >= 3:
    d = a_an.mean() - a_na.mean()
    se = np.sqrt(a_an.var(ddof=1)/len(a_an) + a_na.var(ddof=1)/len(a_na))
    tt = d/se
    P(f"- atr14: 注釈あり 平均 {a_an.mean():.3f}（中央値 {np.median(a_an):.3f}・n {len(a_an)}）vs"
      f" 欠落 平均 {a_na.mean():.3f}（中央値 {np.median(a_na):.3f}・n {len(a_na)}）"
      f"  Δ {d:+.3f} Welch t {tt:+.2f} MDE {2*se:.3f} USD・MW p {stats.mannwhitneyu(a_an,a_na).pvalue:.4f}")
    P(f"- risk: 注釈あり 中央値 {np.median([c['risk'] for c in sl_an]):.2f} vs 欠落 {np.median([c['risk'] for c in sl_na]):.2f} USD")
    hn = collections.Counter(c["h"]//2*2 for c in sl_na); ha = collections.Counter(c["h"]//2*2 for c in sl_an)
    P("- 欠落の ET 決着帯分布（c52 留保 (iii) の未確認分）: "
      + ", ".join(f"{h:02d}:{hn.get(h,0)}/{ha.get(h,0)+hn.get(h,0)}" for h in range(0,24,2) if ha.get(h,0)+hn.get(h,0)))
    dn = collections.Counter(c["et_date"] for c in sl_na)
    P(f"- 欠落の日集中: {len(dn)} 日に {len(sl_na)} 本（max {max(dn.values())} 本/日・"
      f"上位 3 日 {sorted(dn.items(), key=lambda kv:-kv[1])[:3]}）")
    brk("BREAK-7", abs(tt) >= 2, f"注釈欠落本の atr14 が有意に違う（Welch t {tt:+.2f}）= 157 は共変量で選択された標本")
else:
    brk("BREAK-7", False, "欠落本の atr14 が取れず検定不能")

# ============================== A8 コスト 2 倍 + 副産物 (b) ==============================
P("")
P("## A8 コスト 2 倍 ＋ 副産物 (b)「滑りは週末ギャップの尻尾に住む（44% が 1 本）」")
vr = np.array([c["sl_slip"]/c["risk"] for c in sl_an])
grossR = sum(c["R"] for c in closed if c["R"] is not None)
P(f"- SL 滑り 合計 {vr.sum():+.3f}R／{len(vr)} 本・gross ΣR {grossR:+.1f}R → シェア {vr.sum()/grossR:.2%}"
  f"（c52: 2.09R・55.4R・3.8%）")
P(f"- コスト 2 倍: {2*vr.sum():+.3f}R = gross の {2*vr.sum()/grossR:.2%}；"
  f"上位 1 本除外 {vr[np.argsort(-vr)][1:].sum():+.3f}R（2 倍なら {2*vr[np.argsort(-vr)][1:].sum():+.3f}R = {2*vr[np.argsort(-vr)][1:].sum()/grossR:.2%}）")
mx = vr.max(); share = mx/vr.sum()
P(f"- max share = {share:.1%}（c52 44%）")
# max share は重い尾なら普通に出る値か（bootstrap で max share の帰無分布）
bs = np.empty(20000)
for i in range(20000):
    s = vr[rng.integers(0, len(vr), len(vr))]
    bs[i] = s.max()/s.sum()
P(f"- max share の bootstrap 分布: 中央値 {np.median(bs):.1%}・95%CI [{np.percentile(bs,2.5):.1%}, {np.percentile(bs,97.5):.1%}]"
  f"  ＝この重い尾では max share {share:.0%} は {'想定内（1 本集中は分布の性質・週末ラベルの証拠ではない）' if np.percentile(bs,2.5) <= share <= np.percentile(bs,97.5) else '異常'}")
# 週末持ち越しラベルの検定
def is_wkend_carry(c):
    return c["in_wd"] == 4 and c["wd"] in (6, 0) and c["et_date"] > c["in_date"]
wk = [c for c in sl_an if is_wkend_carry(c)]
nw = [c for c in sl_an if not is_wkend_carry(c)]
P(f"- 週末持ち越し ∧ SL ∧ 注釈あり n {len(wk)}（{[c['id'] for c in wk]}）vs 他 n {len(nw)}")
if 1 <= len(wk) < len(sl_an):
    obs = np.mean([c["sl_slip"]/c["risk"] for c in wk]) - np.mean([c["sl_slip"]/c["risk"] for c in nw])
    pool = vr.copy(); nwk = len(wk); cnt = 0; NP2 = 100000
    for _ in range(NP2):
        pr = rng.permutation(pool)
        cnt += (pr[:nwk].mean() - pr[nwk:].mean()) >= obs
    p_wk = (cnt+1)/(NP2+1)
    P(f"- ラベル置換検定（週末 vs 他・滑り R）: Δ {obs:+.4f}R  置換 p(片側) = {p_wk:.4f}（n_週末 {nwk}）")
    # ラベルをランダムに付け替えたときに「max を含む n_wk 本」が選ばれる確率
    P(f"  参考: n_wk={nwk} 本を無作為に選んで max 本を含む確率 = {nwk/len(vr):.3%}"
      f"  ＝『最大の 1 本にラベルを後から読んだ』形の帰無確率")
    brk("BREAK-8", p_wk >= 0.05, f"週末ラベルの置換 p {p_wk:.4f} ≥ 0.05（n_週末 {nwk}・事後ラベル）")
else:
    brk("BREAK-8", True, f"週末持ち越し SL 注釈本が n {len(wk)}＝検定不能（c52 の n=2 主張は統計になっていない）")
# 週末持ち越しは SL になりやすいのか（基準率との比較）
carry_all = [c for c in closed if c["in_wd"] == 4 and c["in_date"] and c["et_date"] > c["in_date"] + timedelta(days=1)]
if carry_all:
    nsl = sum(1 for c in carry_all if c["er"] == "SL")
    base = np.mean([c["er"] == "SL" for c in closed])
    bt = stats.binomtest(nsl, len(carry_all), base, alternative="greater")
    P(f"- 週末持ち越し closed {len(carry_all)} 本の SL 率 {nsl}/{len(carry_all)} = {nsl/len(carry_all):.1%}"
      f"  vs 基準 SL 率 {base:.1%}（全 closed {len(closed)}）  二項片側 p {bt.pvalue:.3f}"
      f"  → 週末持ち越しは SL に {'なりやすい' if nsl/len(carry_all)>base else 'なりやすくない（むしろ低い）'}")
# 日曜再開 18 時 ET の SL
sun = [c for c in sl_an if c["wd"] == 6 and c["h"] == 18]
P(f"- 日曜再開 18 時 ET の SL 注釈本 n {len(sun)}"
  + (f"・滑り {[round(c['sl_slip']/c['risk'],3) for c in sun]}R" if sun else ""))

# ============================== A9 陽性対照 / rho の MDE ==============================
P("")
P("## A9 陽性対照と rho の最小検出力（各帰無が「本物」を見逃さないかの確認）")
for true_rho in (0.15, 0.25, 0.35, 0.50):
    # Y の順位に比例した単調成分を X に注入（既知の強さ）
    ry = stats.rankdata(Y); ry = (ry - ry.mean())/ry.std()
    hits_b = hits_s = 0; NS = 300
    for _ in range(NS):
        noise = rng.standard_normal(N)
        xi = true_rho*ry + np.sqrt(max(1e-9, 1-true_rho**2))*noise
        r_i = stats.spearmanr(xi, Y).statistic
        # 円環シフト帰無（安いので shift を使う）
        nl = np.array([stats.spearmanr(xi, np.roll(Y, k)).statistic for k in range(1, N, 4)])
        if (np.sum(nl >= r_i)+1)/(len(nl)+1) < 0.05: hits_s += 1
    P(f"- 注入 rho {true_rho:.2f}: 円環シフト帰無での検出率 {hits_s/NS:.2f}（{NS} 反復）")
# rho* = 円環シフト帰無の 95 パーセンタイル
P(f"- 最小検出 rho*（円環シフト帰無の 95 パーセンタイル）= {np.percentile(null_s,95):+.4f}"
  f"／日ブロック帰無 = {np.percentile(null_b,95):+.4f}  vs 観測 {rho_scipy:+.4f}")
P(f"→ c52 の rho {rho_scipy:+.4f} は、束を考慮した帰無の 95 パーセンタイル"
  f"（{max(np.percentile(null_s,95), np.percentile(null_b,95)):+.4f}）を {'超える' if rho_scipy > max(np.percentile(null_s,95), np.percentile(null_b,95)) else '超えない'}")

# ============================== 総合判定 ==============================
P("")
P("## 総合判定")
for k in sorted(BREAKS):
    P(f"- {k}: {'BREAK' if BREAKS[k] else 'not broken'}")
core = BREAKS.get("BREAK-1", False) or BREAKS.get("BREAK-2", False)
mech = BREAKS.get("BREAK-3", False) or BREAKS.get("BREAK-4", False)
P("")
P(f"**H_S2 の『PASS（規則上）』: {'broken' if core else 'survived'}**（BREAK-1 正しい帰無 / BREAK-2 多重検定）")
P(f"**『滑りはボラの顔』という機構の読み: {'broken' if mech else 'survived'}**（BREAK-3 トレンド / BREAK-4 risk との同定）")
P(f"**副産物 (b)『尻尾は週末』: {'broken' if BREAKS.get('BREAK-8') else 'survived'}**")
P("")
P(f"実行 {time.time()-T0:.1f} s・読んだのは {LEDGER} のみ（読取専用）・書込 {OUT}")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
