# -*- coding: utf-8 -*-
"""
[反証レーン c50 補足 d] c50 の「最も重大な反証 (ii)」と本反証の C3 が残した唯一の未決着点
 = 「10:25-10:30 London の 5 分間にスプレッドが w USD 開くなら受取りは w だけ減る。
    w* = 0.1064 USD（P4・= 基準往復 0.16 の 0.67 倍）開けば受取りは 0」
を、**口座の spread_log.jsonl（本番ログ・読取りのみ）で直接測る**。
c50 は「決着は XAU ask M1【要取得】」としたが、受取りに効くのは Dukascopy の ask ではなく
**実際に約定する口座の気配**であり、それは既にこの環境に有る（DATA_MAP §4「口座 0.15/0.16 固定」）。

事前固定（数字を見る前）:
D1 被覆: spread_log.jsonl の期間・n・London スロット別の観測数を印字。スロットあたり n<30 なら
   「検出力不足」と明記して終える。
D2 主検定: London 10:25-10:30（＝沈みの 5 分）の平均スプレッドと、
   (a) 同日 10:00-11:00 の平均、(b) 全 London 時刻の平均 との差 Δw（USD）。
   PM 14:55-15:00 も同じ。
   BREAK-15 = Δw >= w*（= 0.1064 USD）→ 受取りは 0 以下 = **経済的に broken（決着）**。
   BREAK-16 = Δw が 0 と区別できない（|t| < 2 かつ 2se < 0.02 USD）→ **拡大は無い = c50 の反証 (ii) の
   「スプレッド拡大で機械的に出る」は口座の気配では否定**（＝人工物仮説の最後の逃げ場が閉じる）。
D3 補助: スプレッドの分布（値の種類）・>0.16 の比率のスロット別・1 分未満の最大値（瞬間拡大）。
   瞬間拡大が有るなら「平均は動かないが約定は悪い」形なので、スロット別の **最大値と 95 分位**も出す。
D4 衛生: ログの欠落（連続観測の間隔中央値・London スロット別の観測日数）。ログは執行機が動いている
   間だけ書かれる可能性があるので、「10:25 London にログが無い」なら検出力不足として明記。
注意: spread_log の期間（2026 秋）は XAU npz（..2026-06-30）の外。よって「同じ日の照合」はできず、
   測るのは **現在のコスト体制でのスロット別スプレッド水準**（＝前向き受取りに効く量）。期間差は明記。
読取りのみ（spread_log は本番ファイル・読取専用で開く）・発注なし・MT5 なし・外部通信なし・
書込は AUREL_RESEARCH/ 配下のみ。seed 20261118。
"""
import os, io, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LIVE = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c50_auction_bar_d.md"); L = []
def say(s=""):
    print(s, flush=True); L.append(s)
def S(h, m): return h * 12 + m // 5
def lab(s): return f"{s // 12:02d}:{(s % 12) * 5:02d}"
def stat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return (np.nan, np.nan, n, np.nan)
    se = x.std(ddof=1) / math.sqrt(n)
    return (x.mean(), x.mean() / se if se > 0 else np.nan, n, se)

WSTAR = 0.1064  # 補足 c の w*（P4）

say(f"# [反証レーン c50 補足 d] 口座スプレッドで w* を直接測る — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c50_auction_bar_d.py)")
say("")
say(f"問い: 10:25-10:30 London の 5 分でスプレッドは開くか。開くなら沈み（P4 gross +0.2664 USD）は受け取れない。分岐点 **w\\* = {WSTAR:.4f} USD**（補足 c）。")

# ---------- 読み込み（読取専用） ----------
p = os.path.join(LIVE, "spread_log.jsonl")
rows = []
with io.open(p, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if "ts" in o and "spread_pt" in o:
            rows.append((int(o["ts"]), float(o["spread_pt"]), float(o.get("bid", np.nan))))
a = np.array(rows, dtype=float)
ts = a[:, 0].astype(np.int64); sp = a[:, 1]; bid = a[:, 2]
t_lon = pd.to_datetime(ts, unit="s", utc=True).tz_convert("Europe/London")
slot = t_lon.hour.to_numpy() * 12 + t_lon.minute.to_numpy() // 5
wd = t_lon.weekday.to_numpy(); dayl = pd.DatetimeIndex(t_lon.tz_localize(None)).normalize()
m = wd <= 4
say("")
say("## D1 被覆・衛生")
say("")
say(f"- spread_log.jsonl: 行 {len(rows)}／期間 **{t_lon.min():%Y-%m-%d %H:%M} .. {t_lon.max():%Y-%m-%d %H:%M} London**（= XAU npz の外 ..2026-06-30 → 同日照合は不可・測るのは現在のコスト体制のスロット別水準）")
say(f"- 平日のみ {int(m.sum())} 行・暦日 {len(set(dayl[m]))} 日・観測間隔 中央値 {np.median(np.diff(np.sort(ts[m]))):.0f} s・bid 範囲 {np.nanmin(bid):.0f}-{np.nanmax(bid):.0f} USD")
vals, cnts = np.unique(sp[m], return_counts=True)
say(f"- spread_pt の値（USD）: " + " ｜ ".join(f"{v:.2f}:{c/cnts.sum()*100:.1f}%" for v, c in zip(vals[:12], cnts[:12])) + (f" ｜ …計 {len(vals)} 種・最大 {vals.max():.2f}" if len(vals) > 12 else ""))
n_am = int((m & (slot == S(10, 25))).sum()); n_pm = int((m & (slot == S(14, 55))).sum())
say(f"- 当該スロットの観測数: 10:25 **{n_am}** 行（{len(set(dayl[m & (slot == S(10,25))]))} 日）／14:55 **{n_pm}** 行（{len(set(dayl[m & (slot == S(14,55))]))} 日）")
POWER = (n_am >= 30)

# ---------- D2 ----------
say("")
say("## D2 主検定 — 当該 5 分 vs 周辺・全時刻（USD）")
say("")
say("| スロット | n | 平均 | 中央値 | 95 分位 | 最大 | >0.16 比率 |")
say("|---|---|---|---|---|---|---|")
for s in range(S(10, 5), S(10, 55)):
    x = sp[m & (slot == s)]
    if len(x) == 0: continue
    bold = "**" if s in (S(10, 25), S(10, 30)) else ""
    say(f"| {bold}{lab(s)}{bold} | {len(x)} | {bold}{x.mean():.4f}{bold} | {np.median(x):.3f} | {np.quantile(x,0.95):.3f} | {x.max():.3f} | {(x>0.16).mean()*100:.1f}% |")
say("")
say("| スロット | n | 平均 | 中央値 | 95 分位 | 最大 | >0.16 比率 |")
say("|---|---|---|---|---|---|---|")
for s in range(S(14, 35), S(15, 25)):
    x = sp[m & (slot == s)]
    if len(x) == 0: continue
    bold = "**" if s in (S(14, 55), S(15, 0)) else ""
    say(f"| {bold}{lab(s)}{bold} | {len(x)} | {bold}{x.mean():.4f}{bold} | {np.median(x):.3f} | {np.quantile(x,0.95):.3f} | {x.max():.3f} | {(x>0.16).mean()*100:.1f}% |")

say("")
say("| 比較 | Δw (USD) | t | 2se | w\\* との関係 |")
say("|---|---|---|---|---|")
BREAK15 = {}; BREAK16 = {}
ref_hour = {S(10, 25): (S(10, 0), S(11, 0)), S(14, 55): (S(14, 0), S(15, 0))}
for s in (S(10, 25), S(14, 55)):
    x = sp[m & (slot == s)]
    for nm, ref in (("同日 10-11 時平均" if s == S(10, 25) else "同日 14-15 時平均",
                     sp[m & (slot >= ref_hour[s][0]) & (slot < ref_hour[s][1]) & (slot != s)]),
                    ("全 London 時刻（平日）", sp[m])):
        mu1, _, n1, se1 = stat(x); mu0, _, n0, se0 = stat(nm and ref)
        dw = mu1 - mu0; se = math.sqrt(se1 ** 2 + se0 ** 2); tt = dw / se if se > 0 else np.nan
        say(f"| {lab(s)} − {nm} | **{dw:+.5f}** | {tt:+.2f} | {2*se:.5f} | {'Δw >= w* → 受取り 0' if dw >= WSTAR else f'Δw は w* ({WSTAR:.4f}) の {dw/WSTAR*100:+.1f}%'} |")
        if nm.startswith("全"):
            BREAK15[s] = dw >= WSTAR
            BREAK16[s] = (abs(tt) < 2) and (2 * se < 0.02)

# ---------- D3 ----------
say("")
say("## D3 瞬間拡大（平均は動かなくても約定は悪い形か）")
say("")
say("- London スロット別 最大スプレッドの上位 8: " + " ｜ ".join(
    f"{lab(s)} {sp[m & (slot == s)].max():.2f}" for s in sorted(
        [s for s in range(288) if (m & (slot == s)).sum() > 0],
        key=lambda s: -sp[m & (slot == s)].max())[:8]))
say("- London スロット別 平均スプレッドの上位 8: " + " ｜ ".join(
    f"{lab(s)} {sp[m & (slot == s)].mean():.4f} (n {(m&(slot==s)).sum()})" for s in sorted(
        [s for s in range(288) if (m & (slot == s)).sum() >= 20],
        key=lambda s: -sp[m & (slot == s)].mean())[:8]))
say(f"- 10:25 と 10:30 の >0.16 比率 {(sp[m&(slot==S(10,25))]>0.16).mean()*100:.1f}% / {(sp[m&(slot==S(10,30))]>0.16).mean()*100:.1f}% ｜ 全時刻 {(sp[m]>0.16).mean()*100:.1f}%")

# ---------- 判定 ----------
say("")
say("## 判定（補足 d）")
say("")
say("| BREAK | 内容 | 10:25 | 14:55 |")
say("|---|---|---|---|")
say(f"| BREAK-15 | Δw >= w\\* = {WSTAR:.4f} USD → 経済的に broken（決着） | {'**YES**' if BREAK15.get(S(10,25)) else 'no'} | {'**YES**' if BREAK15.get(S(14,55)) else 'no'} |")
say(f"| BREAK-16 | Δw ≈ 0（\\|t\\|<2 かつ 2se<0.02）→ スプレッド拡大による人工物説は否定 | {'**YES**' if BREAK16.get(S(10,25)) else 'no'} | {'**YES**' if BREAK16.get(S(14,55)) else 'no'} |")
say("")
say("- 検出力: " + ("十分（10:25 のスロット n>=30）" if POWER else "**不足（10:25 のスロット n<30）→ 決着不能**"))
say("- 限界（必ず読む）: (1) 期間が npz の外（2026 秋のみ・" + f"{len(set(dayl[m]))} 営業日" + "）＝沈みを測った 2021-26H1 のスプレッドではない。(2) spread_log は**気配**で、約定の滑り・約定拒否は含まない（台帳の滑りは §4）。(3) ベンダーが Dukascopy ではなく口座の配信＝受取りに効くのはこちら、だが沈み自体は Dukascopy bid で測っている（両者の気配が同じ形とは限らない）。")
say("")
say(f"- 実行 {time.time()-T0:.1f} s・spread_log.jsonl は**読取専用で開いたのみ**（書込・編集なし）・発注なし・MT5 なし・外部通信なし・プロップ参照なし・秘密の読取/出力なし。seed 20261118")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
