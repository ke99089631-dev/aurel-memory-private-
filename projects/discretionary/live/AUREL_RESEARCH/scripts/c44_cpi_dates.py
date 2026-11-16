# -*- coding: utf-8 -*-
"""
[cycle44 研究レーン 2026-11-17] CPI（米消費者物価指数）公表日暦の取得 — DATA_MAP §6 の【要取得】「CPI／PCE／小売の時刻付き公表日」のうち CPI を閉じる（㊺: 公開・無料・規則で機械抽出できる暦は当サイクルで取る）。
取得元: bls.gov の CPI ニュースリリース・アーカイブ https://www.bls.gov/bls/news-release/cpi.htm（公開・無料・API キー不要・1 ページ）
規則: リンクのファイル名 cpi_MMDDYYYY.(htm|pdf|txt) の 8 桁が**実際の公表日**（政府閉鎖等で遅れた回も実公表日で載る＝暦規則の近似より正確）。
公表時刻: 08:30 ET（BLS 恒例・全期間）。参照月はファイル名には無い（本サイクルでは不要）。
検査（㉔）: 年あたり件数（通常 12・閉鎖年は 11〜12）・曜日分布（土日 0）・隣接間隔（中央値 ≈30 日）を印字。暦のボラ陽性対照（J 検定）は c44_announcement_pool.py 側で行う。
出力: data/macro/CPI_dates.csv（date,year,wd,source）。読取のみ・外部通信は bls.gov のみ。
"""
import os, re, time, urllib.request
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); MAC = os.path.join(ROOT, "data", "macro")
OUT = os.path.join(MAC, "CPI_dates.csv"); URL = "https://www.bls.gov/bls/news-release/cpi.htm"
t0 = time.time()
html = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "ignore")
print(f"fetched {len(html)} chars in {time.time()-t0:.1f}s")
raw = re.findall(r"cpi_(\d{2})(\d{2})(\d{4})\.(?:htm|pdf|txt)", html)
dates = sorted({pd.Timestamp(year=int(y), month=int(m), day=int(d)) for m, d, y in raw})
print(f"filenames {len(raw)} -> unique dates {len(dates)} ({dates[0].date()}〜{dates[-1].date()})")
df = pd.DataFrame({"date": [d.strftime("%Y-%m-%d") for d in dates]})
df["year"] = [d.year for d in dates]; df["wd"] = [d.weekday() for d in dates]; df["source"] = "bls_archive_filename"
df = df[(df.year >= 2008)].reset_index(drop=True)
os.makedirs(MAC, exist_ok=True); df.to_csv(OUT, index=False, encoding="utf-8")
print(f"saved {OUT}: {len(df)} rows {df.date.min()}〜{df.date.max()} in {time.time()-t0:.1f}s")
print("per-year count (㉔):", df.groupby("year").size().to_dict())
print("weekday (0=Mon):", df.wd.value_counts().sort_index().to_dict())
gaps = pd.to_datetime(df.date).diff().dt.days.dropna()
print(f"gap days: median {gaps.median():.0f}・min {gaps.min():.0f}・max {gaps.max():.0f}・gaps>40: " + ", ".join(f"{df.date[i-1]}->{df.date[i]} ({int(g)})" for i, g in zip(gaps.index, gaps) if g > 40))
print("Friday releases (NFP 衝突候補):", df[df.wd == 4].date.tolist())
