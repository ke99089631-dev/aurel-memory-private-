# -*- coding: utf-8 -*-
"""
[cycle42 研究レーン 2026-11-16] FOMC 声明日（statement day）暦の取得 — DATA_MAP §6 の【要取得】CPI/FOMC 暦のうち FOMC を閉じる。
取得元: federalreserve.gov（公開・無料・API キー不要）
  - 過去年: https://www.federalreserve.gov/monetarypolicy/fomchistorical<YYYY>.htm  の <h5>…Meeting - YYYY</h5>
  - 近年:   https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm  の fomc-meeting__month / fomc-meeting__date（年見出し "YYYY FOMC Meetings"）
規約: 声明日 = 会合の最終日（2 日会合は 2 日目）。unscheduled（臨時・電話会合）は scheduled=0 で別記（主分析は scheduled のみ）。
   声明時刻（ET）: 2013-03-20 以降は全会合 14:00。2011-04〜2012-12 の記者会見会合は 12:30・それ以外 14:15 → POST 窓は 2013-03-20 以降のみ使う。
出力: data/macro/FOMC_dates.csv（date,year,scheduled,label,source）。読取のみ・外部通信は federalreserve.gov のみ。
"""
import os, re, sys, time, urllib.request
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); MAC = os.path.join(ROOT, "data", "macro")
OUT = os.path.join(MAC, "FOMC_dates.csv")
HDR = {"User-Agent": "Mozilla/5.0"}
MON = {m: i for i, m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"], 1)}
MON.update({m[:3]: i for m, i in list(MON.items())}); MON.update({"Sept": 9})
def parse_months(tok):
    """'April' / 'April/May' / 'Jan/Feb' -> (m1, m2 or None); None if unknown"""
    parts = [p.strip() for p in tok.split("/")]
    if not all(p in MON for p in parts): return None
    return MON[parts[0]], (MON[parts[-1]] if len(parts) > 1 else None)
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=25).read().decode("utf-8", "ignore")
rows = []
def add(y, m1, d1, m2, d2, label, src):
    # statement day = last day; range may cross month (m2 given)
    mm = m2 if m2 else m1; dd = d2 if d2 is not None else d1
    sched = 0 if re.search(r"unscheduled|notation vote|conference call", label, re.I) else 1
    rows.append(dict(date=pd.Timestamp(year=y, month=mm, day=dd).strftime("%Y-%m-%d"), year=y, scheduled=sched, label=label.strip(), source=src))
t0 = time.time()
# historical pages
for y in range(2010, 2021):
    url = f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm"
    try: html = get(url)
    except Exception as e: print(y, "ERR", e); continue
    heads = re.findall(r"<h5[^>]*>([^<]*Meeting[^<]*|[^<]*Conference Call[^<]*|[^<]*unscheduled[^<]*)</h5>", html, re.I)
    n0 = len(rows)
    for h in heads:
        # formats: "January 27-28 Meeting - 2015" / "April 30-May 1 Meeting - 2019" / "March 15 Meeting (unscheduled) - 2020"
        m = re.match(r"\s*([A-Z][a-z]+(?:/[A-Z][a-z]+)?)\s+(\d{1,2})(?:\s*-\s*(?:([A-Z][a-z]+)\s+)?(\d{1,2}))?\s*(.*)", h)
        if not m: print("  unparsed:", h); continue
        mo1, d1, mo2, d2, rest = m.groups(); pm = parse_months(mo1)
        if pm is None: print("  unparsed month:", h); continue
        m1, m2 = pm
        if mo2: m2 = MON.get(mo2, m2)
        add(y, m1, int(d1), m2, int(d2) if d2 else None, h, f"hist{y}")
    print(y, "entries", len(rows) - n0)
# calendar page (recent years)
html = get("https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm")
blocks = re.split(r"(\d{4}) FOMC Meetings", html)
# blocks: [pre, year, body, year, body, ...]
for i in range(1, len(blocks) - 1, 2):
    y = int(blocks[i]); body = blocks[i + 1]
    ents = re.findall(r'fomc-meeting__month[^>]*>\s*<strong>([^<]*)</strong>\s*</div>\s*<div class="fomc-meeting__date[^>]*>([^<]*)<', body)
    n0 = len(rows)
    for mon, dstr in ents:
        lab = dstr; dstr_clean = re.sub(r"[*†]|\(.*?\)", "", dstr).strip()
        pm = parse_months(mon)
        if pm is None: print("  unparsed month", mon); continue
        nums = re.findall(r"\d{1,2}", dstr_clean)
        if not nums: print("  unparsed date", y, mon, dstr); continue
        d1 = int(nums[0]); d2 = int(nums[-1]) if len(nums) > 1 else None
        m1, m2 = pm
        if d2 is not None and m2 is None and d2 < d1: m2 = m1 % 12 + 1  # cross-month without explicit second month
        unsched = bool(re.search(r"unscheduled", dstr, re.I))
        add(y, m1, d1, m2, d2, f"{mon} {dstr}" + (" (unscheduled)" if unsched else ""), "calendars")
    print(y, "cal entries", len(rows) - n0)
df = pd.DataFrame(rows).drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
df["wd"] = pd.to_datetime(df["date"]).dt.weekday
os.makedirs(MAC, exist_ok=True); df.to_csv(OUT, index=False, encoding="utf-8")
print(f"\nsaved {OUT}: {len(df)} rows ({df.scheduled.sum()} scheduled) {df.date.min()}〜{df.date.max()} in {time.time()-t0:.1f}s")
print(df.groupby("year").agg(n=("date","size"), sched=("scheduled","sum")).T.to_string())
print("weekday of scheduled statement days:", df[df.scheduled==1].wd.value_counts().sort_index().to_dict(), "(0=Mon)")
print(df[df.scheduled==0].to_string())
