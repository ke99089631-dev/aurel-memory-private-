# -*- coding: utf-8 -*-
"""
[cycle44 研究レーン 2026-11-17] CPI（米消費者物価指数）公表日暦の取得 — DATA_MAP §6 の【要取得】「CPI／PCE／小売の時刻付き公表日」のうち CPI を閉じる（㊺: 公開・無料・規則で機械抽出できる暦は当サイクルで取る）。
取得元: bls.gov の CPI ニュースリリース・アーカイブ https://www.bls.gov/bls/news-release/cpi.htm（公開・無料・API キー不要・1 ページ）
規則: リンクのファイル名 cpi_MMDDYYYY.(htm|pdf|txt) の 8 桁が**実際の公表日**（政府閉鎖等で遅れた回も実公表日で載る＝暦規則の近似より正確）。
公表時刻: 08:30 ET（BLS 恒例・全期間）。参照月はファイル名には無い（本サイクルでは不要）。
**実行時の事実（2026-11-17）**: bls.gov は script クライアント（urllib・curl・完全なブラウザ風ヘッダ付き）に **HTTP 403**（bot フィルタ）。本スクリプトの regex 経路は 403 で止まるため、
  フォールバック = data/macro/CPI_dates_webfetch.txt（Claude Code の WebFetch で同ページを**年セクションごとに 1 回ずつ**読み、ファイル名の 8 桁だけを書き出した生リスト・2009〜2026 セクション・18 回）。
  LLM 要約経由なので「機械抽出」ではない → 検査（㉔）で担保: 年あたり件数 12（閉鎖年 2025 は 11・既知）・曜日 土日 0・隣接間隔 中央値 ≈30 日・既知の遅延回（2013-10-30・2025-10-24）が載る。
  ボラ陽性対照（J 検定）は c44_announcement_pool.py 側で行い、PC 不成立なら CPI を外す。bls.gov の 403 が解けたら regex 経路で上書きし一致を確認する（backlog）。
出力: data/macro/CPI_dates.csv（date,year,wd,source）。読取のみ・外部通信は bls.gov のみ。
"""
import os, re, time, urllib.request
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); MAC = os.path.join(ROOT, "data", "macro")
OUT = os.path.join(MAC, "CPI_dates.csv"); URL = "https://www.bls.gov/bls/news-release/cpi.htm"; FALLBACK = os.path.join(MAC, "CPI_dates_webfetch.txt")
t0 = time.time(); raw = []; source = "bls_archive_filename_regex"
try:
    html = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36", "Accept": "text/html"}), timeout=30).read().decode("utf-8", "ignore")
    raw = re.findall(r"cpi_(\d{8})\.(?:htm|pdf|txt)", html); print(f"fetched {len(html)} chars・filenames {len(raw)} in {time.time()-t0:.1f}s")
except Exception as e:
    print(f"regex 経路 失敗: {e!r} → フォールバック {os.path.basename(FALLBACK)}")
    raw = re.findall(r"\b(\d{8})\b", open(FALLBACK, encoding="utf-8").read()); source = "bls_archive_filename_via_webfetch_by_year"
dates = sorted({pd.Timestamp(year=int(s[4:8]), month=int(s[0:2]), day=int(s[2:4])) for s in raw})
print(f"unique dates {len(dates)} ({dates[0].date()}〜{dates[-1].date()})・source {source}")
df = pd.DataFrame({"date": [d.strftime("%Y-%m-%d") for d in dates]})
df["year"] = [d.year for d in dates]; df["wd"] = [d.weekday() for d in dates]; df["source"] = source
df = df[(df.year >= 2010)].reset_index(drop=True)
os.makedirs(MAC, exist_ok=True); df.to_csv(OUT, index=False, encoding="utf-8")
print(f"saved {OUT}: {len(df)} rows {df.date.min()}〜{df.date.max()} in {time.time()-t0:.1f}s")
print("per-year count (㉔・通常 12):", df.groupby("year").size().to_dict())
print("weekday (0=Mon):", df.wd.value_counts().sort_index().to_dict())
gaps = pd.to_datetime(df.date).diff().dt.days.dropna()
print(f"gap days: median {gaps.median():.0f}・min {gaps.min():.0f}・max {gaps.max():.0f}・gaps>40: " + ", ".join(f"{df.date[i-1]}->{df.date[i]} ({int(g)})" for i, g in zip(gaps.index, gaps) if g > 40))
print("day-of-month range:", pd.to_datetime(df.date).dt.day.min(), "-", pd.to_datetime(df.date).dt.day.max(), "・>20 日:", df[pd.to_datetime(df.date).dt.day > 20].date.tolist())
print("Friday releases (NFP 衝突候補):", df[df.wd == 4].date.tolist())
