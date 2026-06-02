---
tags: [project/imperialflow, L4, trading, fx, crypto, cme, mev, active]
type: project
created: 2026-05-19
---

# Project: ImperialFlow

> Masterの "L4 金融増殖装置" 第1号。**全天候型**多軸統合トレードシステム。
> 並走相手: [[cypher]] / 司令: [[Identity/AUREL]]、Master [[Identity/Master]]

## Vision (2026-05-30 全天候化ピボット)
**Bridgewater 流の全天候戦略**：
複数 regime（Sunny / Stormy-Bull / Cloudy / Crisis / Range）× 複数戦略の
ポートフォリオで、**マクロ環境がどう転がっても plus を取りに行く**設計。
旧 lead-lag 中心ビジョンを内包しつつ、Crisis 装備（gold/USD basket）と
カバレッジ拡張（momentum / mean-rev / vol-sell / fx-carry）で広げる。

FX (MT5/Vantage) + 暗号資産 (Bitget) + CME 先物 + Base MEV + マクロ ETF を統合。
**重要**: regime 分類は日次〜数時間スパンなので 15 分遅延 yfinance で十分。
**全天候化により Polygon 加入は lead-lag 戦略 1 つの依存条件**まで縮減。

## Status (2026-05-25 PM4:13)
- ✅ **AUDIT_MODE で稼働中**（5/19 → 5/20 PC シャットダウン → 5/25 再起動）
- ✅ **再起動により QF 配線済の新コードが初稼働中**（5/19 の wiring 修正が初めて load された）
- 口座: **MT5 login=27972608** / Vantage / leverage 1:1000
- equity: **MT5=$53.50 USD / Bitget spot=$44.19 USDT / total=$97.69**
- データソース: yfinance（15分遅延）→ Polygon リアルタイム化が次マイルストーン
- CME ブロック / Whale 検知 / Dashboard (8050) は稼働確認済
- MEV モジュール停止中（少額資本では発動条件未満）
- `kelly_fraction = 0.05`（保守設定）
- 並走相手 [[cypher]] と 2026-12 末に PnL 比較予定

## QF 監査結果（2026-05-26 AM0、再起動後 8 時間稼働）
- **IF プロセス再起動済**（5/25 16:08）→ ディスク上の QF 配線コードが**初稼働中**
- ただし 8 時間稼働で **`[SIGNAL]` ログ 0 件 / `[QF]` ログ 0 件**
- 直接の原因：上流の CME signals が yfinance 15分遅延データだとほぼ生成されない → ArbEngine の lead-lag signal も生まれない → `_execute_lead_lag` 自体が呼ばれない
- **これは bug ではなく構造的制約**：Polygon 加入で初めて QF が本来の役目を果たす
- 結論：**IF は事実上 idle**。プロセスは健全（MT5/Bitget/CME-VF/Whale/Dashboard 全部稼働）だが、メイン戦略（lead-lag）は Polygon 加入待ち

## QF 配線の内容（ディスクと稼働プロセスで一致 — 5/25 16:08 再起動で同期済）
- シグナル発火 → arb_engine の rolling 60秒 follower 価格履歴を取得
- MC15K + Hurst regime + Merton jump で勝率/期待値/VaR/Kelly を算出
- 3 ゲート: `P(profit) >= min_probability_profit (60%)` / `VaR > -max_var (2%)` / `confidence >= 0.35`
- サイジング: `QF Kelly` を採用（上限 = 設定 kelly_fraction × 4 = 0.20）
- 履歴不足/例外時は `raw_Kelly = 0.05` フェイルセーフで動作継続
- `arb_engine.get_price_history()` 公開アクセサ
- **問題なし、上流シグナル不足で fire していないだけ** — Polygon 加入の瞬間に活性化する設計通り

## Roadmap

### 旧 Roadmap（lead-lag 中心、ピボット前）
| Phase | Goal | Status |
|---|---|---|
| 0 | コード基盤、Polygon 加入前の paper 動作確認 | ✅ |
| 0.5 | **QuantumFlow 配線** | ✅ 2026-05-19 |
| 1 | Polygon 加入 + cme_connector 改修（QF 入力 tick の real-time 化） | ⏭ (now optional) |

### 新 Roadmap — 全天候化（2026-05-30 ピボット）
| Phase | Goal | Status |
|---|---|---|
| **WA-0** | 設計書 + Weather Classifier 骨格 | ✅ 2026-05-30 AM5:00 |
| **WA-1** | 既存戦略を `strategies/` に分離 + BaseStrategy 契約 + Registry | ✅ 2026-05-30 AM5:48 |
| **WA-2a** | gold_long 戦略（Crisis 主装備、XAU/USD long） | ✅ 2026-05-30 AM5:48 |
| **WA-2b** | momentum 戦略（SMA/EMA × 5d return on BTC）| ✅ 2026-05-30 AM5:55 |
| **WA-2c** | mean_rev 戦略（BB + RSI on BTC）| ✅ 2026-05-30 AM5:55 |
| **WA-3** | WeatherDirector + main.py 統合 + 5戦略自動 register | ✅ 2026-05-30 AM6:00 |
| **WA-4** | 残戦略（fx_carry, usd_basket, vol_sell） + 再起動 | ✅ 2026-05-30 AM6:24 |
| **WA-5** | retro 校正 + crisis warning 強化 + QF kelly bug 修正 | ✅ 2026-05-31 AM5:00 |
| WA-6 | AUDIT_MODE での paper PnL 検証 | (skipped — 直接 LIVE 化) |
| WA-7 | **LIVE 開始（既存 equity $97.69 で）** | ✅ 2026-05-31 AM6:49 |
| WA-8 | 実弾 capital 追加投入（Master 判断）| 計画 |

## Polygon 加入判断（2026-05-30 AM5:43 Master 質問への回答）

**結論：当面加入見送り推奨（capital が ¥500K-1M に育つまで）**

数字根拠:
- Polygon Advanced $199/月 = 年 $2,400 ≒ ¥360K
- Master 投入予定 capital ¥200-500K → $1,300-3,300
- lead-lag の最大配分（Sunny 時）30%、kelly 0.05 → 1 trade あたり $45 規模
- lead-lag 1 trade typical 利益 0.2-0.5% = $0.09-0.23
- 月 $199 取り戻しに 800-2200 trade 必要、現実は 30-150 trade/月
- **数字が成立しない**

加入を検討すべき分岐点:
1. capital が $6,500+ に育つ
2. vol-selling 本格化（options real-time が要る）
3. WA-5 完了後の再評価
4. lead-lag が他戦略より圧倒的 Sharpe を出すと判明した時

→ **全天候化 → lead-lag は 8 戦略の 1 つに格下げ → Polygon は luxury feature 化**

## WA-1 + WA-2a 実装詳細（2026-05-30 AM5:48）

### 新規モジュール
- `core/strategies/__init__.py` — public API
- `core/strategies/base.py` — `BaseStrategy` ABC + `StrategySignal` / `StrategyContext` dataclass + `SignalSide` enum
  - 共通契約: `compatible_regimes` 宣言 / `generate_signal(ctx)` 実装 / 副作用なし（発注は Director）
- `core/strategies/registry.py` — `StrategyRegistry` + グローバル `REGISTRY`
- `core/strategies/lead_lag_strategy.py` — 旧 `_execute_lead_lag` から signal 生成部分のみ抽出
  - regime: sunny / stormy_bull / range
  - QF ゲート保持（P/VaR/conf 3 ゲート）
- `core/strategies/cross_arb_strategy.py` — `ArbitrageEngine.get_active_opportunity` を signal 化
  - regime: 全 5（環境を選ばない arb 性質）
- `core/strategies/gold_long_strategy.py` — **NEW Crisis 主装備**
  - regime: crisis / cloudy
  - トリガ条件: (1) 5日 +1% 以上の XAU momentum OR (2) macro vol_score>0.5 + gld 20d>0
  - cooldown 1h で重複発火防止
  - confidence: momentum のみ 0.3 / macro 確証込み 0.8

### Smoke test 結果（2026-05-30 AM5:48）
- 3 戦略 register 成功
- live regime classify: range（cross_arb + lead_lag が active）
- gold_long を Crisis macro でテスト → **BUY XAUUSD conf=0.80 size=$4.88 発火**
- 全 py_compile OK

## WA-5 完了（2026-05-31 AM5:00）

### 1. 旧バグ修正: QuantumFlowConfig.kelly_fraction
quantum_flow.py が `self.cfg.kelly_fraction` を参照していたが `QuantumFlowConfig` には未定義
→ `RiskConfig.kelly_fraction` だけ持っていた。
5/30 14:05 以降数千行 WARNING を出していた（fallback で動作継続していたので機能影響はゼロだが、ログノイズ）
修正: `QuantumFlowConfig` に `kelly_fraction: float = 0.05` 追加

### 2. 新規 retro validator: `core/weather/retro.py`
- yfinance で 8 年分の macro データ取得
- 日次で WeatherClassifier を回し、12 個の既知歴史事件と照合
- 月別 regime 分布表 + match rate + 校正示唆を出力
- `python -m core.weather.retro` で実行

### 3. Classifier 校正 — match rate 30% → 70%
**校正前の問題**:
- match rate 30% — ほとんどの期間が "range" に潰れる
- COVID 級の極端事象しか拾えない
- 2022-06 CPI / 2023 SVB / 2023-10 等の真の Crisis を全て見逃し

**校正 3 点**:
1. **BTC 重み 1.0 → 0.4** (risk_score、BTC ノイズで SPY signal が打ち消される問題)
2. **vol_score 算出変更**: `max(abs(VIX-20)/15, rel(60d 比))` — sustained crisis で mean が上がって rel が下がる盲点を解消
3. **regime 閾値緩和** + **soft 分類追加**: ±0.3 → ±0.2、SPY/TLT 補正閾値 0.3 → 0.2

**校正後 (8年 retro)**:
- match rate 30% → **70%**
- **Crisis 6/6 全 OK** (COVID, CPI shock, SVB, Israel war 等)
- bull 側 (2024 AI bull, early 2024 rally) は依然 range に潰れる傾向 — 残課題

### 4. Crisis Warning 強化 — multi-anomaly 検出
旧: SPY/TLT 単一指標のみ → 警告 or 非表示
新: **4 種 anomaly 合成**:
- A: SPY/TLT 30日相関 > 0.4（株債同方向）
- B: VIX > 25（絶対水準）or VIX 60日比 +35% 超（スパイク）
- C: GLD 20d > +3% AND DXY 20d > +1%（safe-haven 殺到）
- D: SPY 20d < -5%（株急落）

判定:
- regime=crisis → 赤点滅 + anomaly 件数表示
- 2+ anomaly → 橙 "EARLY CRISIS WARNING"
- 1 anomaly → 弱橙 "anomaly:"
- 0 → 非表示

### 反映タイミング
全変更はディスク上。**稼働中 IF (PID 13076) は未反映**。次回再起動で:
- QF kelly_fraction WARNING 消失
- 新 classifier で regime 判定がより正確に（今後 Crisis 寄りの signal でちゃんと crisis 認定される）
- Dashboard の Crisis Warning bar が multi-anomaly 表示に

## WA-4 + 再起動完了（2026-05-30 AM6:24）

### 残 3 戦略の実装
- `fx_carry_strategy.py` — AUD/JPY long carry trade（sunny/range/stormy_bull 互換）
  - トリガ: AUD/JPY 20d > +1.5% + VIX < 18 + DXY 20d < 2%
  - 円安 risk-on 局面の利子差収益
- `usd_basket_strategy.py` — Crisis 副 hedge（crisis 専用）
  - トリガ: regime=crisis + VIX > 25 + DXY 20d > 0
  - EUR/USD short で USD strength を取る
- `vol_sell_strategy.py` — 低 vol filler（sunny/cloudy/range 互換）
  - トリガ: vol_score < -0.2 + VIX < 18 + BTC BB position 0.15-0.4 or 0.6-0.85 + RSI 35-65
  - options 接続なしの代替として BB-mid fade で vol premium 収益 proxy

### バグ修正
- `_price_helpers.py` の `get_recent_closes` cache hit path: 旧 logic で DataFrame に `["Close"]` していて IndexingError → 既に squeeze 済の Series をそのまま返すよう修正

### 稼働中 IF プロセスの切替
- PID 7624（5/25 16:08 起動、110.3h 連続稼働）を停止
- 新コード（全天候 + 8 戦略 + Director + Tier 0 dashboard）で起動
- 新 PID launch — AUDIT_MODE=true / AUDIT_MINUTES=60 で paper 検証スタート

### 初稼働ログ抜粋（2026-05-30 06:24:25）
```
[REG] 8 戦略 全 register 成功
[REG] 8 戦略 全 start 成功
[DIRECTOR] WeatherDirector online | registered=8 strategies | dry_run=True
[WEATHER] macro fetched | VIX=15.32 | SPY 20d=+5.3% | GLD 20d=-1.5%
                        | DXY 20d=+0.9% | BTC 20d=-8.9%
[DIRECTOR] regime=range conf=0.20 | risk=+0.02 vol=-0.53
           | active strategies: ['lead_lag', 'cross_arb', 'mean_rev',
                                 'vol_sell', 'fx_carry']
[APP] Weather panel callbacks registered
Dashboard: http://127.0.0.1:8050
```

→ **全天候 IF 初稼働成功**。8 戦略 / Director / Tier 0 ダッシュボード全て live。

### 全戦略のサマリ表
| name | compatible | venue | symbol | trigger | base kelly |
|---|---|---|---|---|---|
| lead_lag | sunny/storm/range | mt5/bitget | EURUSD/BTC etc | CME lead-lag signal | QF Kelly |
| cross_arb | ALL | bitget | BTC/USDT etc | spread > 5bps | from opp |
| gold_long | crisis/cloudy | mt5 | XAUUSD | momentum + macro | 0.05 |
| momentum | sunny/storm | bitget | BTC/USDT | 4 trend conditions | 0.05 |
| mean_rev | cloudy/range | bitget | BTC/USDT | BB+RSI extreme | 0.04 |
| fx_carry | sunny/storm/range | mt5 | AUDJPY | 20d>+1.5% + macro | 0.04 |
| usd_basket | crisis | mt5 | EURUSD short | crisis confirmed | 0.04 |
| vol_sell | sunny/cloudy/range | bitget | BTC/USDT | BB mid + low vol | 0.03 |

## Dashboard 全天候 UI 拡張（2026-05-30 AM6:09 着手 → AM6:20 完了）

### 新規 Tier 0「全天候セクション」を既存 dashboard 上部に挿入
既存の Cosmic Network / KPI strip / 思考ログ等は維持、上に新セクションを追加する非破壊改修。

### 構成要素
1. **REGIME ヘッダ**: 大きな regime ラベル（恐慌/CRISIS, 横這/RANGE 等）+ confidence + risk/vol gauges
2. **MACRO カード strip**: VIX / SPY 20d / GLD 20d / DXY 20d / BTC 20d / SPY-TLT corr の 6 カード（severity 別の左ボーダー色分け）
3. **STRATEGY ROSTER**: 8 戦略の縦並び、active(●緑) / inactive(○グレー) / 未実装(░ 半透明)
4. **ALLOCATION MATRIX**: 5 regime × 8 戦略の表、現在 regime 行を金色ハイライト
5. **DIRECTOR LIVE SIGNAL FEED**: WeatherDirector が生成した signal の時系列リスト
6. **CRISIS WARNING バー**: 通常時非表示、SPY/TLT corr > 0.5 で橙、regime=crisis で赤点滅

### 新規ファイル
- `dashboard/weather_panel.py` — 全 layout + render + callback、約 380 行
- `dashboard/assets/style.css` 末尾に `/* ALL-WEATHER · Tier 0 panel */` セクション追記、約 200 行 CSS

### app.py への組み込み
- `_weather_section_import()` lazy import 関数追加
- レイアウトで `dcc.Interval` の直後に Tier 0 として挿入
- `create_app()` で `register_weather_callbacks(app, imperial)` 呼出

### カラー方針
- regime 別アクセント: sunny=ゴールド、stormy_bull=シアン、cloudy=グレー、crisis=赤（点滅）、range=白
- macro カード severity: positive=緑左ボーダー、negative=赤、danger=赤+glow、warning=橙
- allocation matrix 現在行: ゴールドのグラデーション + 左ボーダー
- crisis bar: 警告(橙) / アクティブ(赤+pulse animation)

### 検証
- py_compile OK
- `from dashboard.weather_panel import *` 全 OK
- `build_weather_section()` → Dash html.Div 返却確認
- `render_regime_label` で各 regime のラベル＋色取得 OK

### 次の IF 再起動時に活性化
現稼働 IF (PID 7624) は 5/25 16:08 起動の旧 dashboard。再起動後 http://127.0.0.1:8050 で新 dashboard が表示される。

## WA-2b/c + WA-3 実装詳細（2026-05-30 AM5:55 → AM6:00）

### 新規モジュール
- `core/strategies/_price_helpers.py` — yfinance OHLC 取得共通 helper（10 分キャッシュ）+ SMA/EMA/RSI/Bollinger/pct_return
- `core/strategies/momentum_strategy.py` — BTC-USD 4 条件 trend confirm（EMA50>EMA200 / SMA20>SMA50 / price>SMA20 / 5d ret > +1%）
- `core/strategies/mean_rev_strategy.py` — BTC BB 下バンド + RSI<30 で long、または upper + RSI>70 で short
- `core/weather/director.py` — **WeatherDirector**：classify ループ（10分）+ signal ループ（30秒）の 2 段、AUDIT_MODE 時は dry_run、戦略の suggested_size × 配分 weight でサイズ確定、MT5/Bitget 自動 dispatch

### main.py 統合
- 5 戦略を `__init__` で REGISTRY に自動登録
- `weather_director = WeatherDirector(self, dry_run=audit_mode)` 構築
- `start()` で Director 起動、`stop()` で停止
- `state["weather"]` で dashboard に regime/配分/直近 signal expose

### 全 5 戦略 × 5 regime active マトリクス（live test 結果）
| regime | active strategies |
|---|---|
| sunny | lead_lag, cross_arb, **momentum** |
| stormy_bull | lead_lag, cross_arb, **momentum** |
| cloudy | cross_arb, **gold_long**, **mean_rev** |
| crisis | cross_arb, **gold_long** |
| range（今の市場）| lead_lag, cross_arb, **mean_rev** |

### yfinance バグ修正
- yf.download() が単一 ticker でも MultiIndex columns を返す事象を `_price_helpers.get_recent_closes` でフラット化 + squeeze + dropna 対応

### 動作確認
- 全 py_compile OK
- `import main` + `ImperialFlow()` インスタンス化 + `weather_director` 属性確認 + REGISTRY 5 戦略確認 全て成功
- **次の IF プロセス再起動で全天候 IF が稼働開始する状態**

## 全天候化 — 2026-05-30 AM5 ピボット詳細

### 新規モジュール
- `docs/ALL_WEATHER_DESIGN.md` — 12 セクションの設計書（regime taxonomy / 戦略 × regime マトリクス / allocator / 段階的実装計画 / 成功基準）
- `core/weather/__init__.py` — public API export
- `core/weather/macro_signals.py` — yfinance ベース macro 取得（VIX/SPY/TLT/GLD/DXY/BTC + 30日相関）+ 10分キャッシュ
- `core/weather/classifier.py` — `WeatherClassifier`、5 regime ルールベース v1 + ヒステリシス (連続 3 同一で confirm)
- `core/weather/allocator.py` — `StrategyAllocator` + `ALLOCATION` 配分表（5 regime × 8 戦略 = 40 cell）

### Weather Taxonomy（5 regime）
| Regime | risk | vol | 代表戦略 |
|---|---|---|---|
| Sunny | on | low | momentum / lead_lag / fx_carry |
| Stormy-Bull | on | high | momentum / lead_lag |
| Cloudy | off | low | mean_rev / cross_arb / vol_sell |
| Crisis | off | high | **gold_long / usd_basket** |
| Range | mid | mid | cross_arb / mean_rev / vol_sell |

### Live test 結果（2026-05-30 AM5:07）
- macro: VIX 15.36（60d 平均 20.85 → 平静）/ SPY +5.3% / GLD -1.5% / DXY +0.8% / BTC -8.9%
- **REGIME = range** (risk_score +0.025, vol_score -0.53)
- 配分 active: cross_arb 40% / mean_rev 20% / vol_sell 20% / lead_lag 10% / fx_carry 10%
- 観察: SPY/TLT 30日相関が **+0.76**（通常負、隠れリスク兆候、早期 Crisis warning フラグ機構を WA-5 で検討）

### 戦略 × Regime カバレッジ（既存 → 全天候）
| Strategy | Sunny | StormyBull | Cloudy | Crisis | Range | Status |
|---|---|---|---|---|---|---|
| lead_lag | ✓ | ✓ | ~ | ✗ | ~ | 既存（ArbEngine）|
| cross_arb | ✓ | ✓ | ✓ | ✓ | ✓ | 既存（ArbEngine 部分）|
| momentum | ✓ | ✓ | — | — | — | **NEW (WA-2)** |
| mean_rev | — | — | ✓ | — | ✓ | **NEW (WA-2)** |
| vol_sell | ✓ | — | ✓ | — | ✓ | **NEW (WA-4)** |
| fx_carry | ✓ | ~ | — | ~ | ✓ | **NEW (WA-4)** |
| gold_long | — | — | — | ✓ | — | **NEW (WA-2)** ← 最重要 |
| usd_basket | — | — | — | ✓ | — | **NEW (WA-2)** |

### Polygon 依存の縮減
旧: IF 全体が Polygon 加入待ち（lead-lag 中心）
新: **lead-lag 戦略 1 つだけが Polygon 依存**。他 7 戦略は yfinance/MT5/Bitget で動く。
→ **Polygon 加入なしで全天候 IF は本格稼働可能**

## 重大な発見（2026-05-18 監査）→ 2026-05-19 解消
- ~~**QuantumFlowEngine が発注フローに未配線**~~ → **解消済 2026-05-19 AM5:15**
  - Monte Carlo 15K paths + Hurst regime detection + Merton jump diffusion + Kelly 自動算出が `_execute_lead_lag` の発注前ゲート + サイジングとして稼働開始。
  - `arb_engine.get_price_history()` で 60 秒 rolling 履歴を input、`stop_pct=0.02`、`target_pct = clip(|gap_pct| × 2, 0.005, 0.04)`、`horizon_bars = max(5, hold_s)` で評価。
  - Polygon 加入を待たずに既存 yfinance/Quandl tick で動作可能（精度は限定的）、Polygon 加入で QF の真価が発揮される設計。

## 設計ドキュメント
- `docs/POLYGON_MIGRATION.md` — cme_connector の Polygon 移行スコープ（3 区画 / 加入後 5 ステップ / 検証マイルストーン）

## .env 装填状況
- 装填済: MT5 (Vantage), Bitget, QuickNode (Base RPC), MEV wallet/key, Quandl
- 未装填: MEXC, Gate, Polygon, Flash Executor address

## Paths
- コード: `C:\Users\user\ImperialFlow\`
- 設定: `C:\Users\user\ImperialFlow\.env`
- ログ: `C:\Users\user\ImperialFlow\logs\imperialflow.log`
- ダッシュボード（起動時）: http://127.0.0.1:8050

## 起動コマンド
```powershell
cd C:\Users\user\ImperialFlow
.\venv\Scripts\Activate.ps1
$env:AUDIT_MODE = "true"
python main.py
```

## 並走 [[cypher]] との関係
- 両者を ¥100-200K の同条件で並走
- 5指標で評価：絶対PnL / Sharpe / 最大DD / 資本効率 / 稼働率
- 3つ以上で勝った方をメイン昇格
- 負け側は廃棄せず、保険・研究材料として温存

---
_Updated: 2026-05-19_
