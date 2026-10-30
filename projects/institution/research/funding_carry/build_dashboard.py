# -*- coding: utf-8 -*-
"""carry_dashboard_data.json を読んで尻尾ダッシュボードHTMLを1枚書く(読取のみ)。"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "carry_dashboard_data.json"), encoding="utf-8"))

xs, ys = d["curve_days"], d["curve_equity_pct"]
x0, x1 = min(xs), max(xs)
y0, y1 = min(ys), max(ys)
W, H, PAD = 900, 300, 40
def sx(x): return PAD + (x - x0) / (x1 - x0) * (W - 2 * PAD)
def sy(y): return H - PAD - (y - y0) / (y1 - y0 + 1e-9) * (H - 2 * PAD)
pts = " ".join("%.1f,%.1f" % (sx(x), sy(y)) for x, y in zip(xs, ys))
# ゼロ線
zero_y = sy(0) if y0 <= 0 <= y1 else None
# DD区間の帯
dd_x0, dd_x1 = sx(d["dd_from_days"]), sx(d["dd_to_days"])

zero_line = ('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#5b6472" stroke-dasharray="4 4"/>'
             % (PAD, zero_y, W - PAD, zero_y)) if zero_y else ""

html = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>キャリー畑 尻尾ダッシュボード</title>
<style>
 body{{background:#0f141b;color:#e6eaf0;font-family:"Segoe UI",system-ui,sans-serif;margin:0;padding:28px}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#8b95a3;font-size:13px;margin-bottom:22px}}
 .row{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:22px}}
 .card{{background:#172030;border:1px solid #243247;border-radius:12px;padding:18px 20px;min-width:180px;flex:1}}
 .lab{{color:#8b95a3;font-size:12px;margin-bottom:6px}}
 .val{{font-size:30px;font-weight:700}} .unit{{font-size:14px;color:#8b95a3;font-weight:400}}
 .good{{color:#3fb98a}} .warn{{color:#e0a23c}} .bad{{color:#e06c5a}}
 .note{{font-size:12px;color:#8b95a3;margin-top:6px}}
 .tail{{background:#2a1b1b;border:1px solid #5a3030;border-radius:12px;padding:16px 20px;margin-top:8px}}
 .tail h2{{font-size:15px;margin:0 0 8px;color:#e0a23c}}
 .tail li{{font-size:13px;margin:4px 0;color:#d6b9a0}}
 svg{{background:#0b1016;border:1px solid #243247;border-radius:12px}}
 .cap{{font-size:11px;color:#5b6472;margin-top:4px}}
</style></head><body>
<h1>キャリー畑 尻尾ダッシュボード</h1>
<div class="sub">{d['basket']} ・ 過去{d['days']}日({d['n_periods']}回の資金調達) ・ 生成 {d['generated']} ・ 読取のみ/発注なし ・ コスト往復{d['cost_roundtrip_pct']}%(個人想定)</div>

<div class="row">
  <div class="card"><div class="lab">① 普段の利回り(年率ネット)</div>
    <div class="val good">+{d['yield_net_annual_pct']}<span class="unit">%/年</span></div>
    <div class="note">グロス+{d['yield_gross_annual_pct']}%−コスト。地味=稼ぎ頭でない</div></div>
  <div class="card"><div class="lab">② 負け側だった割合</div>
    <div class="val warn">{d['pct_negative']}<span class="unit">%</span></div>
    <div class="note">この割合は「自分が払った」回。残りが受取</div></div>
  <div class="card"><div class="lab">③ 最悪の一撃(最大DD・料金ベース)</div>
    <div class="val good">{d['max_drawdown_pct']}<span class="unit">%</span></div>
    <div class="note">料金だけなら極浅。※下の尻尾注意を必ず読む</div></div>
</div>
<div class="row">
  <div class="card"><div class="lab">水面下の最長(進まなかった期間)</div>
    <div class="val warn">{d['longest_underwater_days']}<span class="unit">日</span></div>
    <div class="note">深さでなく「長さ」が痛み。約5ヶ月ほぼ横ばい</div></div>
  <div class="card"><div class="lab">一撃の最悪(1回ぶん)</div>
    <div class="val">{d['worst8h_pct']}<span class="unit">%</span> / +{d['best8h_pct']}<span class="unit">%</span></div>
    <div class="note">受取は+0.01%で頭打ち・払いは下に長い(非対称)</div></div>
  <div class="card"><div class="lab">畳むルールの発火</div>
    <div class="val">{d['fold_events']}<span class="unit">回</span></div>
    <div class="note">{d['fold_rule']}・期間の{d['fold_coverage_pct']}%で縮小合図</div></div>
</div>

<svg viewBox="0 0 {W} {H}" width="100%">
 {zero_line}
 <rect x="{dd_x0:.0f}" y="{PAD}" width="{(dd_x1-dd_x0):.0f}" height="{H-2*PAD}" fill="#e06c5a" opacity="0.08"/>
 <polyline points="{pts}" fill="none" stroke="#3fb98a" stroke-width="2"/>
 <text x="{PAD}" y="{H-12}" fill="#5b6472" font-size="11">0日</text>
 <text x="{W-PAD-30}" y="{H-12}" fill="#5b6472" font-size="11">{x1:.0f}日</text>
 <text x="{PAD}" y="{PAD-12}" fill="#8b95a3" font-size="11">累積キャリー(%)・赤帯=最大DD区間</text>
</svg>
<div class="cap">料金ベースの累積カーブ。右肩上がりだが、中盤に長い横ばい(赤帯=約{(d['dd_to_days']-d['dd_from_days']):.0f}日の停滞)。</div>

<div class="tail">
 <h2>⚠ この表に写っていない尻尾(会長が私に突きつけるべき点)</h2>
 <ul>
  <li>この最大DD −{abs(d['max_drawdown_pct'])}% は<b>資金調達料だけ</b>の曲線。本当の大負けはここに無い。</li>
  <li>真の尻尾=<b>証拠金・清算</b>。BTCが急騰すると売り先物側が証拠金を食い、薄いと清算される。無/低レバで運用する前提が崩れたら牙になる。</li>
  <li>真の尻尾=<b>ベーシス</b>。現物と先物が一時的にズレ、中立でも評価損が出る瞬間がある。</li>
  <li>だから結論は「<b>料金は安全に見えるが、危険は執行と証拠金に隠れている</b>」。年率{d['yield_net_annual_pct']}%の守りの袖として使うなら、無レバ＋畳むルール＋余力厚めが絶対条件。</li>
 </ul>
</div>
</body></html>"""

out = os.path.join(HERE, "carry_dashboard.html")
open(out, "w", encoding="utf-8").write(html)
print("WROTE", out)
