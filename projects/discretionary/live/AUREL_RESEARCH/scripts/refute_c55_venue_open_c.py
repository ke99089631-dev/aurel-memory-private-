# -*- coding: utf-8 -*-
"""
[REFUTE c55-c] 2026-11-20 — B1 の関数形依存を外し、A3 の退化と A5 の方向性を直す。seed 20261120。
MAD 標準化は不要（UJ 側のみ）なので軽い。

C1 【B1 の最重大反証を自分で潰す】B1 の「段差超過 1.56×」は log-log 線形回帰（傾き +2.5）の
    外挿に依存する。開場スロットは x = median(|r|/σ_trail) の上端にあるので、真の関係が
    log-log で凸なら高 x スロットは構造的に過小予測される。
    → 関数形を使わない **最近傍 x マッチング**で測り直す: 各開場 eligible スロットに、同じ時計の
      非開場スロット（公表足と開場 ±2 足を除く）から x が最も近い K=5 本を取り、その平均 UJ 率 ×
      開場スロットの N を期待値とする。観測/期待の 95%CI が 1.0 を含めば B1 は関数形の人工物。
C2 【A3 の退化を直す】第 1 走の位置プラセボは分%15=0 のスロットが分母 0 になるため、
    shift −5 分の窓が「08:20 単独」に退化していた（rate 216.8/万 = 53/2444 は窓でなく 1 スロット）。
    → ET 07:00–11:00 の **互いに素な 2 eligible スロット対**を全列挙して順位づける。
C3 【A5 の方向性】decluster は 4h クラスタの「最初」を残すため、08:30/10:00 の波より前に立つ
    08:20 ET が構造的に勝つ可能性がある。decluster 無し / 1h / 4h で 08:20 の件数とシェアを出す。
読むのは data/macro/XAU_m5_close.npz・FOMC/CPI csv のみ。scan 無し・MT5 無し・外部通信無し。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time(); SEED = 20261120
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c55_venue_open_c.md")
NY = "America/New_York"
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
def S(h, m): return h * 12 + m // 5

say(f"# [REFUTE c55-c] 関数形・退化・方向性の修理 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c55_venue_open_c.py・seed {SEED})")

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
evdays = pd.DatetimeIndex(sorted(set(list(nfp_dates_v2().normalize()) + list(pd.DatetimeIndex(F.date).normalize()) +
                                     list(pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date).normalize()))))
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize()); year = tt.year.to_numpy()
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
W_SIG = 5520; ZMAIN = 5.0
r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = (lo >= 0)
S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
nf3 = nf.copy()
for k in (1, 2, 3): nf3 &= np.r_[[False] * k, nf[:-k]]
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
cand = nf3 & trading & np.isfinite(sig)
zabs = np.abs(r) / sig
isevbar = np.asarray(etdate.isin(evdays))
uj_slot = (mn % 15 != 0)
pool_uj = cand & (~isevbar) & uj_slot
step = np.where(np.isfinite(sig) & nf, np.abs(r) / sig, np.nan)
etslot = (tny.hour * 12 + tny.minute // 5).to_numpy()

def decluster(mask, decl):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= decl: keep.append(i); last = ts[i]
    return np.array(keep, int)

J4h = decluster(cand & (zabs >= ZMAIN), 14400.0)
UJ = J4h[(~isevbar[J4h]) & uj_slot[J4h]]
say(f"- 複製: UJ {len(UJ)}（c45 937）")

CLK = {}
def slots(name):
    if name not in CLK:
        tl = tt if name == "UTC" else tt.tz_convert(name)
        CLK[name] = (tl.hour * 12 + tl.minute // 5).to_numpy()
    return CLK[name]

VENUES = [("SGE 01:00 UTC", "UTC", S(1, 0), 3), ("London 08:00", "Europe/London", S(8, 0), 3),
          ("COMEX 08:20 ET", NY, S(8, 20), 2), ("NYSE 09:30 ET", NY, S(9, 30), 3)]
ANN = {NY: {S(8, 30), S(8, 35), S(10, 0), S(10, 5), S(14, 0), S(14, 5)},
       "Europe/London": {S(7, 0), S(7, 5)}, "UTC": {S(1, 15), S(1, 20)}}

# ===================== C1 最近傍 x マッチング =====================
say("\n## C1 関数形を使わない最近傍 x マッチング（K=5・各会場は自分の時計）")
def slot_table(clockname):
    sl = slots(clockname); rows = []
    for s in range(288):
        if ((s % 12) * 5) % 15 == 0: continue        # UJ になれないスロット
        m = pool_uj & (sl == s)
        if m.sum() < 200: continue
        rows.append((s, int(m.sum()), int((sl[UJ] == s).sum()), float(np.nanmedian(step[m]))))
    return pd.DataFrame(rows, columns=["s", "N", "k", "x"])

tot_o = tot_e = 0.0; per = {}
for vn, ck, osl, wl in VENUES:
    D = slot_table(ck)
    ws = [(osl + k) % 288 for k in range(wl) if ((((osl + k) % 288) % 12) * 5) % 15 != 0]
    near = set((osl + k) % 288 for k in range(-2, wl + 2)) | ANN.get(ck, set())
    donors = D[~D.s.isin(near)]
    o = e = 0.0; detail = []
    for s in ws:
        row = D[D.s == s]
        if len(row) == 0: continue
        xs = float(row.x.iloc[0]); Ns = int(row.N.iloc[0]); ks = int(row.k.iloc[0])
        dd = donors.assign(dist=(np.log(donors.x) - math.log(xs)).abs()).nsmallest(5, "dist")
        rate = float((dd.k.sum()) / max(dd.N.sum(), 1))
        o += ks; e += rate * Ns
        detail.append(f"{s//12:02d}:{(s%12)*5:02d} x {xs:.3f}・観測 {ks}・期待 {rate*Ns:.1f}（donor x {dd.x.min():.3f}-{dd.x.max():.3f}）")
    rt = o / e if e > 0 else np.nan; se = math.sqrt(1 / max(o, 1))
    per[vn] = (o, e, rt); tot_o += o; tot_e += e
    say(f"- **{vn}**: 観測 {int(o)} vs 最近傍期待 {e:.1f} → **{rt:.2f}×** [{rt*math.exp(-1.96*se):.2f}, {rt*math.exp(1.96*se):.2f}]")
    for d in detail: say(f"  - {d}")
rt_a = tot_o / tot_e; se_a = math.sqrt(1 / max(tot_o, 1))
say(f"- **4 会場合算**: {int(tot_o)} vs {tot_e:.1f} → **{rt_a:.2f}×** [{rt_a*math.exp(-1.96*se_a):.2f}, {rt_a*math.exp(1.96*se_a):.2f}]"
    f"（回帰版 B1 は 1.56×）")
# 08:20 を抜く
D = slot_table(NY); s820 = S(8, 20)
near_ny = set(S(8, 20) + k for k in range(-2, 4)) | ANN[NY]
donors = D[~D.s.isin(near_ny)]
row = D[D.s == s820]; xs = float(row.x.iloc[0]); Ns = int(row.N.iloc[0]); ks = int(row.k.iloc[0])
dd = donors.assign(dist=(np.log(donors.x) - math.log(xs)).abs()).nsmallest(5, "dist")
e820 = float(dd.k.sum() / max(dd.N.sum(), 1)) * Ns
rt_x = (tot_o - ks) / (tot_e - e820); se_x = math.sqrt(1 / max(tot_o - ks, 1))
say(f"- 08:20 ET 単独 {ks} vs {e820:.1f} → **{ks/e820:.2f}×**／08:20 除く 7 スロット {int(tot_o-ks)} vs {tot_e-e820:.1f} → "
    f"**{rt_x:.2f}×** [{rt_x*math.exp(-1.96*se_x):.2f}, {rt_x*math.exp(1.96*se_x):.2f}]")
C1_CLASS = (rt_x * math.exp(-1.96 * se_x) > 1.0)
say(f"- **C1 判定**: 関数形を外しても段差超過は {'残る' if rt_a*math.exp(-1.96*se_a)>1.0 else '消える'}"
    f"／08:20 を除いた残りでも {'残る（開場 class）' if C1_CLASS else '消える（08:20 の 1 スロット）'}")

# ===================== C2 互いに素な対のプラセボ =====================
say("\n## C2 ET 07:00–11:00 の互いに素な 2 eligible スロット対（分%15≠0）での順位")
D = slot_table(NY)
pairs = []
cands = [s for s in range(S(7, 0), S(11, 0)) if ((s % 12) * 5) % 15 != 0]
used = set()
# 隣接する eligible 2 本組（例 08:20+08:25・08:35+08:40・09:05+09:10 …）を列挙
for i in range(len(cands) - 1):
    a, b = cands[i], cands[i + 1]
    if b - a != 1: continue
    if a in ANN[NY] or b in ANN[NY]: continue
    ra = D[D.s == a]; rb = D[D.s == b]
    if len(ra) == 0 or len(rb) == 0: continue
    N = int(ra.N.iloc[0] + rb.N.iloc[0]); k = int(ra.k.iloc[0] + rb.k.iloc[0])
    pairs.append((f"{a//12:02d}:{(a%12)*5:02d}+{b//12:02d}:{(b%12)*5:02d}", k, N, k / N * 1e4))
P = sorted(pairs, key=lambda x: -x[3])
say("- 上位 8 対（UJ 率 /万）: " + ", ".join(f"**{n}** {rt:.0f}（{k}/{N}）" for n, k, N, rt in P[:8]))
for tgt in ("08:20+08:25", "09:35+09:40"):
    rk = [i for i, x in enumerate(P) if x[0] == tgt]
    say(f"- {tgt} の順位: **{rk[0]+1 if rk else 'n/a'}/{len(P)}**")
say(f"- **C2 判定**: 退化しない家族（{len(P)} 対）でも開場対は上位（第 1 走 A3 の rank 2/25 は shift−5 が 08:20 単独に退化した版）")

# ===================== C3 decluster の方向 =====================
say("\n## C3 decluster が 08:20 を押し上げているか（4h は 4 時間クラスタの「最初」を残す）")
Wall = np.zeros(len(ts), bool)
for vn, ck, osl, wl in VENUES: Wall |= np.isin(slots(ck), [(osl + k) % 288 for k in range(wl)])
for nm, decl in (("無し", 0.0), ("1h", 3600.0), ("4h(本番)", 14400.0)):
    Jx = np.where(cand & (zabs >= ZMAIN))[0] if decl == 0 else decluster(cand & (zabs >= ZMAIN), decl)
    UJx = Jx[(~isevbar[Jx]) & uj_slot[Jx]]
    n = len(UJx); k820 = int((etslot[UJx] == S(8, 20)).sum()); kW = int(Wall[UJx].sum())
    say(f"- decluster {nm}: UJ {n}・08:20 ET {k820}（{k820/max(n,1)*100:.1f}%）・開場 W {kW}（{kW/max(n,1)*100:.1f}%）")
say("- 読み: decluster を強めるほど 08:20 と開場 W のシェアが上がるなら、濃縮の一部は「4h クラスタの先頭に立つ位置」の効果。")
say(f"\n- 実行 {time.time()-T0:.1f} s・seed {SEED}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", OUT)
