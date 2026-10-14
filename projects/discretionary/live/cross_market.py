# -*- coding: utf-8 -*-
"""
会長の仮説検証: 壁→壁(外壁ブレイク→リテスト戻り入り→測った分TP)は金専用の偶然か、
  それとも構造の普遍則か。同じエンジン(backtest_v3)に金以外のM5を食わせて外壁×リテストの成績を見る。
  データ源= Yahoo(yfinance, M5・直近60日)=稼働中のMT5端末に一切触れない独立ソース。
  ※グロス(スプレッド未控除)=「構造が効くか」を見る1次検証。net判定は後段。金ゼロ・読取のみ・発注なし。
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, yfinance as yf
from backtest_v3 import backtest_v3

SYMS = [
    ("GC=F",     "金先物(基準・答え合わせ)"),
    ("EURUSD=X", "ユーロドル(FX)"),
    ("GBPUSD=X", "ポンドドル(FX)"),
    ("ES=F",     "S&P500先物(株指数)"),
    ("NQ=F",     "ナスダック100先物(株指数)"),
    ("BTC-USD",  "ビットコイン(暗号資産・24/7)"),
]

def fetch_m5(sym):
    df = yf.download(sym, period="60d", interval="5m", auto_adjust=False,
                     progress=False, threads=False)
    if df is None or not len(df):
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close"})
    df = df[["open","high","low","close"]].dropna()
    idx = pd.DatetimeIndex(df.index)
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    else:
        idx = idx.tz_convert("UTC")
    df.index = idx
    return df

def rstats(d):
    if d is None or not len(d):
        return None
    R = d["R"].to_numpy(dtype=float)
    tp = int((d["exit_reason"] == "TP").sum())
    cum = np.cumsum(R); peak = np.maximum.accumulate(cum); dd = float((cum - peak).min())
    return dict(n=len(d), tp_rate=100*tp/len(d), winrate=100*float((R>0).mean()),
                avgR=float(R.mean()), sumR=float(R.sum()), maxDD=dd)

def line(label, s):
    if not s:
        return "  %-14s データなし" % label
    return ("  %-14s %3d本 TP率%4.0f%% 勝率%4.0f%% 平均%+.3fR 合計%+6.1fR 最大DD%6.1fR"
            % (label, s["n"], s["tp_rate"], s["winrate"], s["avgR"], s["sumR"], s["maxDD"]))

print("=== 壁→壁 クロスマーケット検証 (M5・Yahoo直近60日・グロス) ===\n")
summary = []
for sym, name in SYMS:
    try:
        m5 = fetch_m5(sym)
    except Exception as e:
        print("【%s】%s\n  取得失敗: %s\n" % (sym, name, str(e)[:70])); continue
    if m5 is None or len(m5) < 300:
        print("【%s】%s\n  データ不足(%s本)\n" % (sym, name, 0 if m5 is None else len(m5))); continue
    tr = backtest_v3(m5, record_skips=True)
    alls = rstats(tr)
    take = rstats(tr[tr["decision"]=="TAKE"]) if len(tr) else None
    print("【%s】%s  (M5 %d本 ≈%.0f日)" % (sym, name, len(m5), len(m5)*5/60/24))
    print(line("全候補(純構造)", alls))
    print(line("TAKE(採点通過)", take))
    print()
    if alls: summary.append((name, alls, take))

print("=== まとめ（純構造=外壁ブレイク→リテストを全部取った場合の1本あたりR）===")
for name, a, t in summary:
    mark = "✅プラス" if a["avgR"]>0 else "❌マイナス"
    print("  %-22s 全候補 平均%+.3fR (%d本) %s" % (name, a["avgR"], a["n"], mark))
