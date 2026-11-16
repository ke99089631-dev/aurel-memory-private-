# -*- coding: utf-8 -*-
"""
[cycle43 研究レーン 2026-11-17] 【探索・制度カレンダー／デリバティブ満期（収益機会の源泉マップ §8 新行: 指数デリバティブ満期日＝トリプルウィッチング・月次 OPEX の
引け圧力と翌営業日の反転）】
文献（記憶から・本サイクルは外部通信なし）: Stoll–Whaley 1987 JFE "Program trading and expiration-day effects" / 1991 FAJ "Expiration-day effects: what has changed?":
S&P 500 の指数先物・指数オプション・個別株オプションが同時に満期を迎える四半期第 3 金曜（トリプルウィッチング）の**引け 1 時間は出来高とボラが異常に高く**、
引けの価格圧力（裁定ポジションの巻き戻し・MOC 注文）は**翌営業日の寄りで反転**する（1980 年代 S&P で −0.3〜−0.4%）。1987 年以降は先物決済が寄り（SOQ）へ移され引け効果は
縮小したと報告。現代の機構候補 = ①S&P 指数リバランスが四半期第 3 金曜の引けに実施（MOC インバランス）②PM 決済の指数/ETF オプション（月次第 3 金曜）のディーラー・
ガンマ解消③レバレッジ ETF の引けリバランス。方法論 ㉝: **本拠（US500）で先に当て、立たなければ金で探さない**。金は同じ格子の対照（金には指数リバランスが無い・
GLD オプションは月次第 3 金曜満期＝弱い同型機構があり得る）。入口フィルタではない・本番とは独立の市場記述。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/US500_m5_close.npz（2012-01〜2026-06-09・bid）・XAU_m5_close.npz（bid）・refute_c4 json（ゲート ㉛）。既存キャッシュのみ・scan 無し・M5 読込なし・
  MT5 無し・外部通信無し。読込後に min/max 時刻（⑩）・曜日別 flat 比率（⑪）を印字。
暦（規則導出・外部データ不要・㉔ の件数検査 = 年あたり QW 4・OPEX 12 を通す）: OPEX = 各月第 3 金曜。QW（四半期満期・トリプルウィッチング）= 3/6/9/12 月の OPEX。
  第 3 金曜が NYSE 休場（聖金曜日のみ該当し得る・復活祭から導出）の年は満期が木曜へ移る → その月は事象集合から**除外**（曜日一致を守る・件数を印字）。
  MOPEX = OPEX − QW（月次のみ）。対照 = 事象でない金曜（同時代）。頑健版対照 = 第 2・第 4 金曜のみ（第 1 金曜 NFP・最終金曜 月末の組成を外す）。
価格の時計: c40 と同じ P(T) = ts == T−300 の足の close（穴は NaN・⑫）。取引日 D = ET 現地の暦日。
窓（bp・対数差・ET）: LAST = 15:30 → 16:00（主）／LAST5 = 15:55 → 16:00（記述・MOC の顔）／CASH = 09:30 → 15:30（同日の背景）／
  NEXT = D 16:00 → 次の営業日 D′ 10:00（主・反転の被説明変数）／GAP = 16:00 → D′ 09:30／FIRST = D′ 09:30 → 10:00（記述）。
  次の営業日 D′ = D より後の最初の平日で 09:30→10:00 が有限 ∧ ≠0（1 月・2 月の OPEX 翌月曜は MLK／大統領の日で休場 → 火曜になる・最大 5 暦日先まで探す）。
有効日 = 金曜 ∧ 使う窓が全部有限 ∧ LAST ≠ 0 ∧ CASH ≠ 0。窓×期間の厳密 0 比率を印字（>20% は判定不可・㉒）。13:00 早引け（感謝祭翌日・クリスマス前）は LAST=0 で落ちる。
統計:
  C1（引けのボラ）: VR = mean(LAST²|QW) / mean(LAST²|対照金曜)（同時代）。置換帰無 = 対照金曜から n_QW 日を無作為抽出 2000 回 → 片側 p（VR* ≥ VR）・帰無 sd（log）。
    併記: 中央値 |LAST| 比・LAST5 の VR・CASH の VR（「引けだけ」か「その日全体」か）・MOPEX の VR。
  C2（翌営業日の反転）: プール OLS（金曜のみ）NEXT = α + β·LAST + δ·(LAST·E) + γ·E、E = OPEX（月次全部・主・n が四半期の 3 倍で決着可能）。HC1 t・MDE = 2·se。
    置換帰無 = E ラベルを金曜の中で無作為に付け替え 2000 回（n_E 保存）→ 片側 p（δ* ≤ δ）。併記: E = QW の δ（記述）・β_E 単独・β_ctrl・符号戦略 S = mean(−sign(LAST)·NEXT | E) bp/日（t）。
窓: 在 2012-20／外 2021-26H1／近年 2024-26H1（D2・窓別・16 年一括は使わない）。判定は在で決め外で確認。年別（記述）。
判定（Bonferroni(2)・名目 0.025・主 2 セル・US500）:
  C1 PASS = VR_QW >1 ∧ 在 置換 p<0.025 ∧ 外 VR>1 ∧ p<0.10。
  C2 PASS = δ_OPEX <0 ∧ 在 HC1 t≤−2 ∧ 置換 p<0.025 ∧ 外 同符号 t≤−1.5。
  XAU（同じ ET 窓・同じ暦）: C1/C2 と同形を印字するが**判定セルではない**（㉝: US500 で立たなければ金で探さない・立てば金は「指数固有か市場共通か」の対照）。
決着可能性（㉝・数字を見る前）: LAST sd ≈ 25〜35 bp・NEXT sd ≈ 60〜90 bp。C1: n_QW 在 ≈ 36 → log VR の se ≈ √(2/36) ≈ 0.24 → VR 1.6 で z ≈ 2＝文献級（引け 1 時間でボラ 2 倍）は決着可能。
  C2: n_OPEX 在 ≈ 100 → se_δ ≈ 75/(30·√100)·√(1+100/360) ≈ 0.29 → δ −0.6（引けの 6 割を翌朝で返す）で t ≈ 2＝境界で決着可能・QW 単独（n 36）は se ≈ 0.45 で決着不能＝記述のみ。
陽性対照: 在 US500 の QW 日の LAST を 1.5 倍にして C1 の p が <0.025 になること／在 OPEX 日の NEXT に −0.5·LAST を注入して δ の t が ≤−2 になること（検出力）。
経済的大きさ（事前に書く）: 符号戦略 S（bp/日）vs 往復コスト US500 ≈ 0.4〜1 bp（c14・口座値は要取得）＋ 夜間保有 swap【要取得】。金 0.16 USD ≈ 0.4〜0.9 bp。
ゲート ㉛（本番接続・在 2010-20 のみ印字）: scan 本（refute_c4）で建玉日（ET 暦日）が OPEX 金曜の本 vs 他の金曜の本 → Δμ(R*)（Welch t）・Δx（pp）・x0 look-ahead 対照。
  QW 金曜も併記。在 |Δμ| <0.048R → 「決着不能・外は走らせない」。
事前の最重大反証: (1) 文献の効果は 1980 年代・先物の引け決済時代のもので、決済が寄りに移った後は縮小した（Stoll–Whaley 1991）→ null は「制度変更後」と読む。
  (2) bid のみ・Dukascopy 1 社・US500 は CFD（SPX/SPY ではない・MOC の板は見えない・CFD は 16:00 以降も取引されるので 16:00 の「引け」は現物の引けの写し）。
  (3) 2020 夏 68 営業日欠落（㊵）＝2020 の QW 6 月は無い可能性。(4) 第 3 金曜は月内位置（給与・月中フロー）と同一＝「満期固有」と「月中固有」は暦では分離できない
  （MOPEX と QW の差＝四半期固有分だけが満期由来と言える）。(5) LAST は引け前半時間のボラが高い（c21/c40）＝VR の分母も高い時間帯で比較している（同時刻比較なので公平）。
  (6) 反転 δ は NEXT の sd が大きく（夜間＋週末 64 時間）、在 n_OPEX ≈100 では δ −0.3 級は見えない（MDE を印字し「無い」と「見えない」を分ける ㊳）。
  (7) 翌営業日が火曜になる 1/2 月（MLK・大統領の日）は NEXT 窓が 88 時間＝分散不均一（HC1 で吸収・記述で除外版も印字）。
昇格候補・入口/出口規則の提案ではない。seed 20261117。
"""
import os, time, math, json, datetime as dt
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c43_expiration_day_effects_result.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED); NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle43] 指数デリバティブ満期日（QW トリプルウィッチング／月次 OPEX）の引けボラと翌営業日反転 — US500 本拠 → 金 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c43_expiration_day_effects.py)")

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

# ---------- 暦（規則導出） ----------
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31; da = ((h + l - 7 * m + 114) % 31) + 1; return dt.date(y, mo, da)
def third_friday(y, m):
    d = dt.date(y, m, 1); off = (4 - d.weekday()) % 7; return d + dt.timedelta(days=off + 14)
OPEX, QW, DROPPED = set(), set(), []
for y in range(2012, 2027):
    gf = easter(y) - dt.timedelta(days=2)
    for m in range(1, 13):
        f3 = third_friday(y, m)
        if f3 == gf: DROPPED.append(f3); continue
        OPEX.add(f3)
        if m in (3, 6, 9, 12): QW.add(f3)
say(f"- 暦: OPEX 第 3 金曜 {len(OPEX)} 日（2012-2026・聖金曜日と重なり木曜へ移った月 {len(DROPPED)}: {', '.join(str(x) for x in DROPPED)} → 除外）・QW {len(QW)} 日（㉔ 件数検査: 年あたり " + " ".join(f"{y}:{sum(1 for d in QW if d.year==y)}/{sum(1 for d in OPEX if d.year==y)}" for y in range(2012, 2027)) + "）")

dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy(); lg = np.log
dser = dates.date
is_fri = dates.weekday.to_numpy() == 4
E_OPEX = np.array([d in OPEX for d in dser]); E_QW = np.array([d in QW for d in dser]); E_MO = E_OPEX & ~E_QW
# 第 2・第 4 金曜（頑健版対照）
dom = dates.day.to_numpy(); fri_k = np.where(is_fri, (dom - 1) // 7 + 1, 0)
ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def windows(ts, cl):
    P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
    p0930, p1000, p1530, p1555, p1600 = P(9, 30), P(10, 0), P(15, 30), P(15, 55), P(16, 0)
    W = {}
    W["LAST"] = (lg(p1600) - lg(p1530)) * 1e4
    W["LAST5"] = (lg(p1600) - lg(p1555)) * 1e4
    W["CASH"] = (lg(p1530) - lg(p0930)) * 1e4
    # 次の営業日 D′: off=1..5 暦日先で 09:30→10:00 が有限かつ ≠0 の最初
    nx0930 = np.full(N, np.nan); nx1000 = np.full(N, np.nan); nxoff = np.full(N, np.nan)
    for off in range(1, 6):
        a, b = P(9, 30, off), P(10, 0, off)
        ok = np.isnan(nx0930) & np.isfinite(a) & np.isfinite(b) & (a != b)
        nx0930[ok] = a[ok]; nx1000[ok] = b[ok]; nxoff[ok] = off
    W["NEXT"] = (lg(nx1000) - lg(p1600)) * 1e4
    W["GAP"] = (lg(nx0930) - lg(p1600)) * 1e4
    W["FIRST"] = (lg(nx1000) - lg(nx0930)) * 1e4
    W["NXOFF"] = nxoff
    return W

def hc1(y, X):
    n, k = X.shape; XtX_i = np.linalg.inv(X.T @ X); b = XtX_i @ X.T @ y; e = y - X @ b
    V = XtX_i @ (X.T * (e ** 2)) @ X @ XtX_i * n / (n - k); se = np.sqrt(np.diag(V)); return b, se
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se

def analyse(sym, W, judged):
    say(f"\n## {sym}")
    valid = is_fri & np.isfinite(W["LAST"]) & np.isfinite(W["CASH"]) & np.isfinite(W["NEXT"]) & (W["LAST"] != 0) & (W["CASH"] != 0)
    for nm in ("LAST", "LAST5", "CASH", "NEXT"):
        z = np.isfinite(W[nm]) & is_fri
        say(f"- 厳密 0 比率 {nm}（金曜・有限）: " + " ".join(f"{e}:{(W[nm][z&(yr>=a)&(yr<=b)]==0).mean()*100:.1f}%" for e, a, b in ERAS) + "（㉒）")
    say(f"- 有効金曜 {int(valid.sum())}（OPEX {int((valid&E_OPEX).sum())}・QW {int((valid&E_QW).sum())}・MOPEX {int((valid&E_MO).sum())}）・NEXT の暦日差: " + " ".join(f"{int(o)}日:{int(((W['NXOFF']==o)&valid).sum())}" for o in (1, 2, 3, 4, 5)))
    say(f"- 年別 有効 QW/OPEX: " + " ".join(f"{y}:{int((valid&E_QW&(yr==y)).sum())}/{int((valid&E_OPEX&(yr==y)).sum())}" for y in range(2012, 2027)))
    res = {}
    for e, a, b in ERAS:
        m = valid & (yr >= a) & (yr <= b); say(f"\n### {e}（有効金曜 n {int(m.sum())}）")
        ctrl = m & ~E_OPEX; ctrl24 = ctrl & ((fri_k == 2) | (fri_k == 4))
        # ---- C1 引けのボラ ----
        for lab, E in (("QW", E_QW), ("MOPEX", E_MO), ("OPEX", E_OPEX)):
            ev = m & E; nE = int(ev.sum())
            if nE < 5: say(f"- C1 {lab}: n {nE} <5 → 省略"); continue
            row = []
            for wn in ("LAST", "LAST5", "CASH"):
                x = W[wn]; xe, xc = x[ev], x[ctrl]; xe, xc = xe[np.isfinite(xe)], xc[np.isfinite(xc)]
                VR = np.mean(xe ** 2) / np.mean(xc ** 2); MR = np.median(np.abs(xe)) / np.median(np.abs(xc))
                sims = np.array([np.mean(rng.choice(xc, len(xe), replace=False) ** 2) for _ in range(NPERM)]) / np.mean(xc ** 2)
                p = float((sims >= VR).mean()); sd = float(np.std(np.log(sims)))
                row.append(f"{wn} VR **{VR:.2f}**（中央値比 {MR:.2f}・p {p:.3f}・帰無 log sd {sd:.2f}）")
                if wn == "LAST": res[(e, lab, "VR")] = (VR, p, nE)
            # 第 2・4 金曜対照
            xe = W["LAST"][ev]; xc = W["LAST"][ctrl24]; VR24 = np.mean(xe ** 2) / np.mean(xc ** 2)
            say(f"- C1 {lab}（n {nE} vs 対照金曜 {int(ctrl.sum())}）: " + "・".join(row) + f"・対照=第2/4金曜 LAST VR {VR24:.2f}（n_c {int(ctrl24.sum())}）")
        # ---- C2 翌営業日の反転 ----
        for lab, E in (("OPEX", E_OPEX), ("QW", E_QW), ("MOPEX", E_MO)):
            ev = m & E; nE = int(ev.sum())
            if nE < 5: say(f"- C2 {lab}: n {nE} <5 → 省略"); continue
            idx = m & (E | ~E_OPEX)  # 事象 ∪ 対照（他の OPEX は外す）
            y = W["NEXT"][idx]; x = W["LAST"][idx]; Ei = E[idx].astype(float)
            X = np.c_[np.ones(idx.sum()), x, x * Ei, Ei]
            b, se = hc1(y, X); dl, tdl = b[2], b[2] / se[2]
            # 置換: ラベル付け替え
            n_i = int(idx.sum()); k_e = int(Ei.sum()); sims = np.empty(NPERM)
            for i in range(NPERM):
                lab_ = np.zeros(n_i); lab_[rng.choice(n_i, k_e, replace=False)] = 1.0
                Xp = np.c_[np.ones(n_i), x, x * lab_, lab_]; bp = np.linalg.lstsq(Xp, y, rcond=None)[0]; sims[i] = bp[2]
            p = float((sims <= dl).mean()); sdn = float(np.std(sims))
            bE, seE = hc1(y[Ei == 1], np.c_[np.ones(k_e), x[Ei == 1]]); bC, seC = hc1(y[Ei == 0], np.c_[np.ones(n_i - k_e), x[Ei == 0]])
            S = -np.sign(x[Ei == 1]) * y[Ei == 1]; tS = S.mean() / (S.std(ddof=1) / math.sqrt(len(S)))
            Sc = -np.sign(x[Ei == 0]) * y[Ei == 0]; tSc = Sc.mean() / (Sc.std(ddof=1) / math.sqrt(len(Sc)))
            # 1/2 月（翌営業日が火曜）除外版
            nx1 = (W["NXOFF"] == 3)[idx]
            b2, se2 = hc1(y[nx1], np.c_[np.ones(nx1.sum()), x[nx1], x[nx1] * Ei[nx1], Ei[nx1]]) if nx1.sum() > 20 and Ei[nx1].sum() >= 5 else (np.full(4, np.nan), np.full(4, np.nan))
            say(f"- C2 {lab}（n_E {nE}・対照 {n_i-k_e}）: δ = β_E − β_ctrl **{dl:+.3f}（HC1 t {tdl:+.2f}・MDE {2*se[2]:.3f}・置換 p {p:.3f}・帰無 sd {sdn:.3f}）**・β_E {bE[1]:+.3f} (t {bE[1]/seE[1]:+.2f})・β_ctrl {bC[1]:+.3f} (t {bC[1]/seC[1]:+.2f})・符号戦略 S_E {S.mean():+.1f} bp/日 (t {tS:+.2f}) vs S_ctrl {Sc.mean():+.1f} (t {tSc:+.2f})・翌営業日=月曜のみ δ {b2[2]:+.3f} (t {b2[2]/se2[2]:+.2f})")
            if lab == "OPEX": res[(e, "OPEX", "delta")] = (dl, tdl, p, 2 * se[2])
            # 記述: 事象日の平均 LAST・NEXT・GAP
            say(f"  - 記述 {lab}: mean LAST {W['LAST'][ev].mean():+.1f} bp (対照 {W['LAST'][ctrl].mean():+.1f})・NEXT {W['NEXT'][ev].mean():+.1f} (対照 {W['NEXT'][ctrl].mean():+.1f})・GAP {W['GAP'][ev].mean():+.1f}・FIRST {W['FIRST'][ev].mean():+.1f}・CASH {W['CASH'][ev].mean():+.1f} (対照 {W['CASH'][ctrl].mean():+.1f})")
    # 年別（記述）
    say("- 年別 QW LAST VR（対 同年 対照金曜）: " + " ".join(f"{y}:{np.mean(W['LAST'][valid&E_QW&(yr==y)]**2)/np.mean(W['LAST'][valid&~E_OPEX&(yr==y)]**2):.2f}" for y in range(2012, 2027) if (valid&E_QW&(yr==y)).sum() >= 2))
    say("- 年別 OPEX 符号戦略 S（bp/日）: " + " ".join(f"{y}:{np.mean(-np.sign(W['LAST'][valid&E_OPEX&(yr==y)])*W['NEXT'][valid&E_OPEX&(yr==y)]):+.0f}" for y in range(2012, 2027) if (valid&E_OPEX&(yr==y)).sum() >= 5))
    # 陽性対照（在のみ）
    if judged:
        m = valid & (yr <= 2020); ctrl = m & ~E_OPEX; ev = m & E_QW
        xe = W["LAST"][ev] * 1.5; xc = W["LAST"][ctrl]; VR = np.mean(xe ** 2) / np.mean(xc ** 2)
        sims = np.array([np.mean(rng.choice(xc, len(xe), replace=False) ** 2) for _ in range(NPERM)]) / np.mean(xc ** 2); p1 = float((sims >= VR).mean())
        idx = m; y = W["NEXT"][idx].copy(); x = W["LAST"][idx]; Ei = E_OPEX[idx].astype(float); y = y - 0.5 * x * Ei
        b, se = hc1(y, np.c_[np.ones(idx.sum()), x, x * Ei, Ei])
        say(f"- 陽性対照（在）: QW LAST ×1.5 → VR {VR:.2f} p {p1:.3f}（検出力 {'あり' if p1 < 0.025 else '不足'}）；OPEX NEXT に −0.5·LAST 注入 → δ {b[2]:+.3f} t {b[2]/se[2]:+.2f}（{'あり' if b[2]/se[2] <= -2 else '不足'}）")
    return res, valid

# ---------- 実行 ----------
say("\n## データ")
R = {}
for sym in ("US500", "XAU"):
    ts, cl = load(sym); W = windows(ts, cl); R[sym] = analyse(sym, W, judged=(sym == "US500"))

# ---------- 判定 ----------
say("\n## 判定（事前固定・Bonferroni(2)・US500）")
res = R["US500"][0]
VRi, pi, nqi = res[("在 2012-20", "QW", "VR")]; VRo, po, nqo = res[("外 2021-26H1", "QW", "VR")]
c1 = (VRi > 1) and (pi < 0.025) and (VRo > 1) and (po < 0.10)
say(f"- C1 QW 引けボラ: 在 VR {VRi:.2f}（p {pi:.3f}・n {nqi}）／外 VR {VRo:.2f}（p {po:.3f}・n {nqo}） → **{'PASS' if c1 else 'null'}**")
di, ti, pdi, mi = res[("在 2012-20", "OPEX", "delta")]; do, to, pdo, mo = res[("外 2021-26H1", "OPEX", "delta")]
c2 = (di < 0) and (ti <= -2) and (pdi < 0.025) and (do < 0) and (to <= -1.5)
say(f"- C2 OPEX 翌営業日反転: 在 δ {di:+.3f}（t {ti:+.2f}・p {pdi:.3f}・MDE {mi:.3f}）／外 δ {do:+.3f}（t {to:+.2f}・p {pdo:.3f}・MDE {mo:.3f}） → **{'PASS' if c2 else 'null'}**")
say(f"- XAU は判定セルではない（㉝）。US500 の結果: C1 {'PASS' if c1 else 'null'}／C2 {'PASS' if c2 else 'null'}")

# ---------- ゲート ㉛ ----------
say("\n## ゲート ㉛（本番接続・在 2010-20 のみ印字）: 建玉 ET 暦日が OPEX 金曜の scan 本 vs 他の金曜の本")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; tr = pd.DataFrame(d["trades"])
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = (tr["exit"] == "TP").astype(float) - tr["q"]
e_ny = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(NY)
tr["d"] = e_ny.dt.date; tr["wd"] = e_ny.dt.weekday
OPEX_ALL, QW_ALL = set(), set()
for y in range(2010, 2027):
    gf = easter(y) - dt.timedelta(days=2)
    for mth in range(1, 13):
        f3 = third_friday(y, mth)
        if f3 == gf: continue
        OPEX_ALL.add(f3)
        if mth in (3, 6, 9, 12): QW_ALL.add(f3)
tr["opex"] = tr["d"].isin(OPEX_ALL); tr["qw"] = tr["d"].isin(QW_ALL)
ins = tr[(tr.year <= 2020) & (tr.wd == 4)]
for lab, col in (("OPEX", "opex"), ("QW", "qw")):
    a = ins[ins[col]]; b = ins[~ins.opex]
    dmu, tmu = welch(a.Rs, b.Rs); dx = 100 * (a[a.dec].x.mean() - b[b.dec].x.mean()); se = abs(dmu / tmu) if tmu != 0 else float("nan")
    x0cut = ins.x0.quantile(2 / 3); d0, t0_ = welch(ins[ins.x0 > x0cut].Rs, ins[ins.x0 <= x0cut].Rs)
    say(f"- 在 {lab} 金曜建玉 n {len(a)} vs 他の金曜 {len(b)}: Δμ **{dmu:+.3f}R (t {tmu:+.2f}・MDE {2*se:.3f})**・Δx {dx:+.2f} pp・TP 率 {100*(a.exit=='TP').mean():.1f} vs {100*(b.exit=='TP').mean():.1f}%・x0 対照 Δμ {d0:+.3f}R (t {t0_:+.1f})" + (f" → ゲート ㉛: |Δμ| {'<' if abs(dmu) < 0.048 else '≥'} 0.048R → **{'決着不能・外は走らせない' if abs(dmu) < 0.048 else '外を印字'}**" if lab == "OPEX" else ""))
    if lab == "OPEX" and abs(dmu) >= 0.048:
        outs = tr[(tr.year >= 2021) & (tr.wd == 4)]; a2 = outs[outs.opex]; b2 = outs[~outs.opex]; dmo, tmo = welch(a2.Rs, b2.Rs)
        say(f"  - 外 OPEX 金曜建玉 n {len(a2)} vs {len(b2)}: Δμ {dmo:+.3f}R (t {tmo:+.2f})")
say(f"\n（所要 {time.time()-T0:.1f} s・seed {SEED}・既存キャッシュのみ・scan 無し・外部通信無し）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
