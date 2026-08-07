---
doc_id: AURELIAN-MARKET-MEMORY-FOUNDRY-PROPOSAL-v1
tags: [institution, reference, market-memory, strategy-foundry, future-concept, proposal]
type: reference
status: Market Memory v0 BUILT (2026-08-07, 会長GO「実装しよう」); Strategy Foundry = future concept (未着工・席のみ確保)
created: 2026-08-07
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: 会長＋アドバイザーがまとめた提案資料（未確定）
---

# Market Memory / Strategy Foundry — 提案リファレンス v1

> **位置づけ**: 会長がアドバイザーと相談してまとめた2つのアイディア。**未確定・未採用・未着工**。AURELが読んで意見を述べた（2026-08-07）。着工GAはまだ出ていない。

---

## アイディアA — Market Memory / Historical Market Archive（build-now候補）

- **本質**: 市場そのものの歴史（相場が何をしてきたか）を意味情報として保存する共有地層。
- **Hypothesis Ledger との違い**: Ledger=Aurelianの研究史（自分が何を仮説し殺したか）。Market Memory=市場の歴史（世界が何をしてきたか）。主語が違う。混ぜない。
- **共有資産**: Discovery内部の道具ではなく、全器官（Discovery/Validation/Frontier/evidence）が読む共有基盤。
- **Market State Fingerprint**: 過去の市場状態を意味情報ベクトル（Volatility/Risk-Off/流動性/相関/レジーム/Tail-Event 等）で表現 → 「構造的に似た過去レジーム」の類似検索。
- **要件**: 成功例だけでなく**失敗例も**検索する。look-ahead/leakage/survivorship を防ぐ（Point-in-Time正確性）。小さく始めて拡張可能に。既存資産を先に使う。
- **15節=12点の実機確認リスト**（着工前に調査すべき）／**15.1**: ゼロから作る前に既存資産を棚卸しすること。

## アイディアB — Strategy Foundry（future concept, DO NOT build now）

- **本質**: 受注設計工房（Discoveryの逆）。会長が「こういう戦略が欲しい」と言うと、実現可能な最善を設計して返す。
- **11節の原則（AUREL強く支持）**: Foundryは会長の要求を**拒絶できなければならない**。望まれた物ではなく実現可能な最善を返す。Class-C（人工的リターン）や不可能な要求は突き返す。
- **方針**: 今は作らない。**公式Future Conceptとして席だけ確保**。

---

## 実機棚卸し結果（2026-08-07 AUREL調査・読取専用）

- **bars_*.csv 58本**（暗号資産 ADA/BNB/BTC/DOGE/ETH/LTC、FX AUD/EUR/GBP/NZD/DXY、国別ETF EEM/EFA/EWA/EWC/EWG/EWH/EWJ/EWQ/EWT/EWU/EWW/EWY/EWZ/GLD/HYG/IEF/INDA/IWM、コモディティ COPPER/CORN/NATGAS）。日足OHLC（date,open,high,low,close、**volume無し**）。約2.75年（2023-11-11〜2026-08-06、~1001行）。
- **rates_*.csv 8通貨**（AUD/CAD/CHF/EUR/GBP/JPY/NZD/USD）金利データ。
- **既存サーフェス**: circulation_digest.json（レジーム/世界情報を内包）、macro_causal.json、event_driven.json、evidence.json、evolved_configs.json。
- **無いもの**: オプション/IV/ニュース/流動性/fingerprint/archive の専用データファイルは**存在しない**（価格OHLC＋金利＋一部macro/eventサーフェスのみ）。
- evidence.py: BARS_GLOB=data/bars_*.csv, _MARKET_ENABLED=True, _SURFACE_BASKET でサーフェス→instrument basket、_read_bar_returns 読取専用。

---

## AUREL の意見（2026-08-07・Fable5で会長に提出済み）

1. **二段構え（NOW=Market Memory / FUTURE=Foundry）は正しい**。
2. Market Memory は長期循環の空白「Frontier→Discovery→**???**→Validation」の??? を埋める。アーキテクチャ的に一貫。**作る価値がある候補**。
3. **最大の急所 = Point-in-Time正確性（リーク・先読み・生存者バイアスの排除）**。ここを外すと「嘘の歴史」になり全て無意味。Class-C自動棄却と同じ魂。
4. **配置 = G2 Core（恒久記憶・読取共有・単一ライター・append-only）**。progress.py の規律を踏襲。
5. **第10の循環ではない**。①情報・④知識・⑤失敗の3循環に血を送る一器官。9本は不変。
6. **正直な位置づけ**: 壁（Frontier）は動かさない。壁を動かすのは第2ギア（新Edge/新Source）だけ。Market Memory は **Discoveryの精度を上げる**＝偽陽性Edge（Class-BをClass-A誤認）を採用前に炙り出す＝⑤失敗循環の直接強化。
7. **v0は残酷なほど小さく**: 既存58本＋金利＋既存レジームラベルでFingerprintスキーマ定義。IV/ニュース/流動性は器だけ空けてロードマップ。成功+失敗の両検索。Point-in-Time最初から強制。豊かさは後・正確さは最初から。
8. **Foundryの拒絶原則は機関の背骨**。今ある器官（Discovery/Validation/Frontier）を最初から「Foundry再利用可能・拒絶できる」設計思想で育てる。今日から効く原則。

---

## 実装状況（2026-08-07 更新）

- **Market Memory v0 = 構築済み**（会長GO「実装しよう」）。詳細は CIRCULATION-ARCHITECTURE.md の建設ログ「Market Memory 資料庫 v0」。
  - `circulation/market_memory.py`（読取専用・単一書き手 market_memory.json・append-only・Point-in-Time）。
  - live: n_days=480（2024-09〜2026-08）tail_events=8。API: current_state / similar_regimes / tail_regimes / stress_edge。
  - 週次サイクル run_progress_cycle.bat に相乗り（既存 AURELIAN_progress_weekly で溜まり続ける）。
  - selftest PASS(7)。
- **未実施（次候補）**: ダッシュボード搭載（現在の地合い＋類似過去局面＋過去最悪局面パネル）。IV/ニュース/流動性データの器（実機に該当データ無し→ロードマップ）。類似検索のローリング正規化格上げ。Discovery/Validation への stress_edge 配線。
- **Strategy Foundry**: 未着工・公式Future Conceptとして席のみ確保。11節の拒絶原則は今ある器官の設計思想に反映。

## 不変条件（2026-08-07時点）
- 9循環 9/9・採用0・live LOCKED・金ゼロ・凍結資産/プロップ非接触。
