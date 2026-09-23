# -*- coding: utf-8 -*-
"""
壁→壁 コックピット Phase2: 静的ウェブチャート生成器（携帯で見える金の地図）。
  役割: 貯めた金M5(ヒストリカル)を読み、
        - ローソク足
        - 自動の壁(箱の上下=黄 / 中間=青)
        - 直近ブレイクのメジャードムーブTP目標線
        - JST時間帯の背景シェード(本物帯07-12=緑, ダマシ巣00-05=赤)
        を1枚の自己完結HTMLに描く（外部ライブラリ不要=携帯のネットに依存しない）。
  ★これは承認不要の読取のみ。ライブ価格はPhase3(MT5橋)で後から乗せる。
  出力: chart.html（同フォルダ）。serve_chart.py が Tailscale:8793 で配る。
金ゼロ・読取のみ・発注なし。
"""
import os
import sys
import json
import datetime as dt

# 車線2の資産を再利用（壁の幾何は backtest と同じ定義に揃える）
sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall")
import pandas as pd  # noqa: E402
from m5_loader import load_m5  # noqa: E402

RANGE_W = 100          # 箱検出窓（backtest_mm と同じ ≈8h）
SL_PAD_FR = 0.33       # 参考: SL は壁内側 幅×この割合
OUT_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chart.html")


def latest_m5(n_bars=240, symbol="xauusd"):
    """利用可能な最新チャンクから直近 n_bars 本の M5 を返す（UTC index）。"""
    # チャンクは四半期。最新から遡って十分な本数を確保。
    today = dt.date.today()
    # 直近1年を広めに読んで末尾を取る（データ末端が数ヶ月前でも末尾を拾う）
    a = (today.replace(year=today.year - 1)).isoformat()
    b = (today + dt.timedelta(days=1)).isoformat()
    m5 = load_m5(a, b, symbol=symbol)
    if len(m5) == 0:
        raise RuntimeError("M5 データ0本: %s..%s" % (a, b))
    return m5.tail(n_bars)


def live_m5_and_tick(n_bars=240):
    """MT5 読取橋から今の M5(UTC index) と現在ティックを取る。橋が使えなければ例外。"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mt5_bridge
    mt5 = mt5_bridge.connect()          # 口座27972608限定・発注なし・安全弁つき
    try:
        df = mt5_bridge.m5_bars(mt5, n_bars)
        tick = mt5_bridge.live_tick(mt5)
    finally:
        mt5.shutdown()                  # 接続は掴みっぱなしにしない（読んだら離す）
    df = df.set_index("dt")
    return df[["open", "high", "low", "close"]], tick


def current_box(m5):
    """末尾時点の箱(直近 RANGE_W 本)= 上壁/下壁/中間壁/幅。"""
    w = m5.tail(RANGE_W)
    up = float(w["high"].max())
    dn = float(w["low"].min())
    mid = (up + dn) / 2.0
    return {"up": up, "dn": dn, "mid": mid, "width": up - dn}


def detect_last_break(m5):
    """末尾側から直近のブレイク(終値が上/下壁を抜けた点)を探し、メジャードムーブTPを付す。"""
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    n = len(c)
    for i in range(n - 1, RANGE_W, -1):
        up = float(h[i - RANGE_W:i].max())
        dn = float(l[i - RANGE_W:i].min())
        width = up - dn
        if width <= 0:
            continue
        if c[i] < dn and c[i - 1] >= dn:
            wall = dn
            return {"idx": i, "dir": "DOWN", "wall": wall, "width": width,
                    "tp": wall - width, "sl": wall + width * SL_PAD_FR}
        if c[i] > up and c[i - 1] <= up:
            wall = up
            return {"idx": i, "dir": "UP", "wall": wall, "width": width,
                    "tp": wall + width, "sl": wall - width * SL_PAD_FR}
    return None


def build_payload(n_bars=240):
    # まず MT5 橋から今の値。取れなければ履歴にフォールバック（承認前/PC不在でも地図は出る）。
    tick = None
    source = "live"
    try:
        m5, tick = live_m5_and_tick(n_bars)
        if len(m5) == 0:
            raise RuntimeError("live 0本")
    except Exception as e:
        source = "hist"
        sys.stderr.write("[live不可→履歴] %s\n" % (e,))
        m5 = latest_m5(n_bars)
    idx = m5.index
    bars = [{
        "t": int(pd.Timestamp(idx[k]).timestamp()),
        "o": round(float(m5["open"].iloc[k]), 3),
        "h": round(float(m5["high"].iloc[k]), 3),
        "l": round(float(m5["low"].iloc[k]), 3),
        "c": round(float(m5["close"].iloc[k]), 3),
    } for k in range(len(m5))]
    box = current_box(m5)
    brk = detect_last_break(m5)
    return {
        "symbol": "XAUUSD (金) M5",
        "generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M JST"),
        "data_end": pd.Timestamp(idx[-1]).tz_convert("Asia/Tokyo").strftime("%Y-%m-%d %H:%M JST"),
        "note": ("LIVE（MT5橋・読取専用）" if source == "live"
                 else "ヒストリカル（データ末端まで）。MT5橋が繋がればライブに切替。"),
        "source": source,
        "tick": tick,
        "bars": bars,
        "box": {k: round(v, 3) for k, v in box.items()},
        "break": ({k: (round(v, 3) if isinstance(v, float) else v)
                   for k, v in brk.items()} if brk else None),
        "range_w": RANGE_W,
    }


HTML = r"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>壁→壁 チャート（金M5）</title>
<style>
  html,body{margin:0;background:#0d1117;color:#c9d1d9;font-family:-apple-system,Segoe UI,Roboto,sans-serif;-webkit-text-size-adjust:100%}
  #hd{padding:8px 12px;font-size:13px;line-height:1.5;border-bottom:1px solid #21262d}
  #hd b{color:#e6edf3}
  .tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;margin-right:5px}
  .yel{background:#3a3410;color:#e3c94a} .blu{background:#0e2740;color:#58a6ff}
  .grn{background:#0f2b17;color:#56d364} .red{background:#3a1113;color:#f85149}
  #wrap{width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
  canvas{display:block;touch-action:pan-x}
  #legend{padding:6px 12px;font-size:11px;color:#8b949e;border-top:1px solid #21262d}
</style></head><body>
<div id="hd">
  <b>__SYMBOL__</b> ・ 生成 __GENERATED__<br>
  データ末端: __DATA_END__<br>
  <span class="tag yel">黄=箱の上下壁</span><span class="tag blu">青=中間壁</span>
  <span class="tag grn">本物帯 JST07-12</span><span class="tag red">ダマシ巣 JST00-05</span>
</div>
<div id="wrap"><canvas id="cv"></canvas></div>
<div id="legend" id="lg"></div>
<script>
const P = __PAYLOAD__;
const bars = P.bars, box = P.box, brk = P.break;
const DPR = Math.max(1, window.devicePixelRatio||1);
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const CW = Math.max(9, Math.floor((Math.min(window.innerWidth,900)-70)/Math.max(60,bars.length))); // 足幅
const PADL=8, PADR=62, PADT=8, PADB=22;
const plotW = bars.length*CW;
const W = PADL+plotW+PADR;
const H = Math.max(360, Math.min(window.innerHeight-150, 620));
cv.style.width=W+'px'; cv.style.height=H+'px';
cv.width=W*DPR; cv.height=H*DPR; ctx.scale(DPR,DPR);

// 価格レンジ（壁・TPも収める）
let lo=Infinity, hi=-Infinity;
for(const b of bars){ lo=Math.min(lo,b.l); hi=Math.max(hi,b.h); }
const tick=P.tick; const nowPx = tick ? (tick.bid+tick.ask)/2 : null;
const extra=[box.up,box.dn,box.mid]; if(brk){extra.push(brk.tp,brk.sl,brk.wall);} if(nowPx!=null){extra.push(nowPx);}
for(const v of extra){ if(v!=null){lo=Math.min(lo,v); hi=Math.max(hi,v);} }
const pad=(hi-lo)*0.06||1; lo-=pad; hi+=pad;
const gy=p=>PADT+(hi-p)/(hi-lo)*(H-PADT-PADB);
const gx=i=>PADL+i*CW;

// JST時間帯シェード（本物帯/ダマシ巣）
for(let i=0;i<bars.length;i++){
  const d=new Date(bars[i].t*1000);
  const jh=(d.getUTCHours()+9)%24;
  let col=null;
  if(jh>=7&&jh<12) col='rgba(86,211,100,0.07)';
  else if(jh>=0&&jh<5) col='rgba(248,81,73,0.07)';
  if(col){ ctx.fillStyle=col; ctx.fillRect(gx(i),PADT,CW,H-PADT-PADB); }
}

// 壁ライン
function hline(p,color,dash,label){
  if(p==null)return; ctx.save(); ctx.strokeStyle=color; ctx.lineWidth=1;
  ctx.setLineDash(dash||[]); ctx.beginPath();
  ctx.moveTo(PADL,gy(p)); ctx.lineTo(PADL+plotW,gy(p)); ctx.stroke();
  ctx.setLineDash([]); ctx.fillStyle=color; ctx.font='10px monospace';
  ctx.fillText(label+' '+p.toFixed(2), PADL+plotW+3, gy(p)+3); ctx.restore();
}
hline(box.up,'#e3c94a',[4,3],'上壁');
hline(box.dn,'#e3c94a',[4,3],'下壁');
hline(box.mid,'#58a6ff',[2,4],'中間');
if(brk){
  hline(brk.tp,'#56d364',[6,4],'TP');
  hline(brk.sl,'#f85149',[2,3],'SL');
}
// 現在価格（ライブ時のみ・白実線）
if(nowPx!=null){ hline(nowPx,'#ffffff',[],'現在'); }

// ローソク
for(let i=0;i<bars.length;i++){
  const b=bars[i], x=gx(i)+CW/2, up=b.c>=b.o;
  const col=up?'#26a641':'#f85149';
  ctx.strokeStyle=col; ctx.fillStyle=col; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(x,gy(b.h)); ctx.lineTo(x,gy(b.l)); ctx.stroke();
  const y1=gy(b.o), y2=gy(b.c), top=Math.min(y1,y2), hgt=Math.max(1,Math.abs(y2-y1));
  ctx.fillRect(gx(i)+1, top, Math.max(1,CW-2), hgt);
}
// ブレイク地点マーカー
if(brk){
  const x=gx(brk.idx)+CW/2;
  ctx.fillStyle=brk.dir==='UP'?'#56d364':'#f85149';
  ctx.beginPath(); ctx.arc(x, gy(brk.wall), 3, 0, 7); ctx.fill();
}
// 凡例テキスト
const lg=document.getElementById('legend');
let txt='箱幅 '+box.width.toFixed(2)+' (上'+box.up.toFixed(1)+'/下'+box.dn.toFixed(1)+')';
if(brk){ txt+=' ｜ 直近ブレイク='+(brk.dir==='UP'?'上':'下')+' 壁'+brk.wall.toFixed(1)
        +' → TP'+brk.tp.toFixed(1)+' / SL'+brk.sl.toFixed(1); }
else { txt+=' ｜ 直近ブレイクなし（レンジ内）'; }
if(tick){ txt+=' ｜ 現在 bid'+tick.bid.toFixed(2)+'/ask'+tick.ask.toFixed(2)
        +' spread'+tick.spread_bps.toFixed(2)+'bps'; }
lg.textContent=txt+' ｜ '+P.note;
// LIVEバッジをヘッダ先頭に
const hd=document.getElementById('hd');
if(hd){ const b=document.createElement('span');
  b.textContent = (P.source==='live'?'● LIVE':'○ 履歴');
  b.style.cssText='float:right;font-size:11px;padding:1px 8px;border-radius:10px;'
    +(P.source==='live'?'background:#0f2b17;color:#56d364':'background:#2a2a2a;color:#999');
  hd.insertBefore(b, hd.firstChild); }
// 右端(最新)にスクロール
document.getElementById('wrap').scrollLeft=plotW;
</script></body></html>"""


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 240
    payload = build_payload(n)
    html = (HTML
            .replace("__SYMBOL__", payload["symbol"])
            .replace("__GENERATED__", payload["generated"])
            .replace("__DATA_END__", payload["data_end"])
            .replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False)))
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] %s (%d本, 末端 %s)" % (OUT_HTML, len(payload["bars"]), payload["data_end"]))
    if payload["break"]:
        b = payload["break"]
        print("  直近ブレイク %s 壁%.1f 幅%.1f TP%.1f SL%.1f"
              % (b["dir"], b["wall"], b["width"], b["tp"], b["sl"]))


if __name__ == "__main__":
    main()
