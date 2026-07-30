---
doc_id: AURELIAN-MAINTENANCE-MACHINE-MM0-v1
tags: [institution, prop, maintenance-machine, freeze, MM0, frozen]
type: machine-registry
rank: 第3層（Prop Division 内・合格後運用機の登録＋凍結記録）
created: 2026-07-30
status: FROZEN（改善探索禁止・審査終了まで）
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# 維持機（Maintenance Machine）登録 — MM0 凍結

> **上位**: DIVISION-PROP.md（Prop Trading Division）。維持機は**合格後にファンド口座を守る機械**。審査機（走らせる機械）とは別系統。
> **一行（会長）**: 「審査機は走らせる機械、維持機は守る機械だ。走らせる前に、守る機械を金庫に入れておけ。」

---

## 起源（会長訂正・確定 2026-07-30）
維持機は「維持機として作った」のではない。事業構想（16週で合格の瞬間を売る）が固まる前、AURELがAURELに最初に出した課題＝**「プロップ資金で安定運用する仕組み」**の成果物。年率10%前後を分散で数年守る機械が出来上がった。審査機へ転用したが「合格まで中央1年半」で不適合→**審査用として棄却→維持機として配置転換**。**二機体制の起源はこれ**。

---

## 確定構成（凍結・不可変）
- **17本** = FX7（EUR/GBP/JPY/AUD/CAD/CHF/NZD）+ 商品4（XAU/XAG/WTI/NATGAS）+ 指数3（SPY/QQQ/IWM＝US500/US100/US2000のETF近似）+ 暗号3（BTC/ETH/SOL）
- **配分**: HRP + vol正規化（HRP_BLEND=0.5・暗号袖 wb=0.2778）
- **運転点**: vol6%
- **嵐検知**: VIX/creditスロットル。SPY/HYG/IEF/VIXを**信号として読むのみ・建玉せず**（債券非取引でも嵐検知は生存）
- **証拠金**: 暗号レバ1:2 → 実効lmax≈7.2で軽拘束。FX(1:100)/商品・指数(1:50)はL_MAX=8で非拘束
- **床/日次**: 内側床0.08 / 本家失格床0.10 / 日次失格0.05 / 2-Step目標[0.08,0.05]

## 確定値（会長申告）
3暴落窓（2008 GFC / 2020-03 COVID / 2022株債同時安）で**床接触ゼロ・日次接触ゼロ**。24本版との差は暴落窓DDが約0.5%深いだけ。
⚠️ これらの生数値は各スクリプトのstdoutのみ＝**永続出力ファイル無し・実行日未記録**。権威的確定にはパラメータ不変での再走＋保存が要る（会長判断待ち）。

---

## MM0 凍結（2026-07-30 執行済）
- **スナップショット**: `empire/research/archive/2026-07-30_maintenance_17hrp_freeze/`（審査機G0と同形式・別ディレクトリ）
- **凍結物**: 定義16件（研究6中核＋分隊5＋支援3＋データ2）を複製しSHA256刻印。詳細は同dir `FREEZE.md`。
- **FREEZE.md SHA256**: `BE29F0CEDA5B8E61BF7B8040CDC27F5ABA644CB8111ED1489B031342F1B745C5`
- **台帳**: 専用ハッシュ連鎖台帳 `empire/data/institution_freeze_ledger.sqlite` に NOTE `MM0_FREEZE` seq=1（last_hash `c092104a1f4e2a89eb9cbf969ac283ab72ee9c33389c0d6eb646b9c81da860f4`）。
  - ※ライブ取引サイクルDBとの競合回避＋「別系統」原則のため専用台帳を採用。会長が特定の既存台帳への統合を望む場合は指示で移す。

### 定義中核ファイル（凍結対象）
- `research/`: sim_universe.py / wf_oos.py（HRP本体）/ wf_regime_throttle.py（VIX/credit）/ wf_crypto_hourly.py / realistic17_verify.py（17本定義ラッパ）/ two_stage_rocket.py
- `squads/`: fx_trend / mean_reversion / cross_sectional / carry / hourly_trend
- 支援MC: prop_lab.py / funded_survival.py / deployed_prop.py
- データ: realistic17_pools.json（v3_17/assembled_17/wb）/ prop_series.json（24本祖先）

## 生存確認（指示3・実測）
- 定義16件＋pools＋prop_series：ローカル存在（凍結内に複製）。
- bars_*.csv 58本存在。必要17銘柄＋VIX/HYG/IEF信号すべてpresent。
- 再現性：ローカルCSV/JSONのみで再走可・ネット不要・**口座/MT5非依存**。fetch_*だけネット依存だがキャッシュ保持で不要。
- **結論：口座が予告なく閉じても維持機の研究資産は失われない。**

## 未検証リスト（指示4・凍結中）
1. C-6（funded_config）: 週末フラット強制 / Profit Concentration / PRIME固有（2%日次停止・Smart Max Loss）整合。→合格視野＋会長指示で照合着手。
2. 指数3本ETF近似（SPY/QQQ/IWM）と CFD 24h足（UTC+3）の時間差＝未検証乖離。
3. 暗号レバ1:2の実効lmax拘束の精緻な袖別notional追跡。

## 拘束（指示5・恒久・審査終了まで）
維持機への改善・最適化・パラメータ探索を**一切行わない**。凍結保存のみ。触れてよいのはC-6照合のみ、かつ合格が視野に入ってから会長指示で着手。

---

## 改定
- v1（2026-07-30）: MM0凍結と同時に登録。
