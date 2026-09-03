---
tags: [institution, design, sensor, roadmap]
type: design
date: 2026-09-03
status: draft-v1（会長GOで着工・紙のみ・金ゼロ）
---

# Aurelian Sensor Registry v1 — 機関の「目・耳」の棚卸し台帳

> 会長GO（2026-09-03）で着手。外部AIの「Sensor Universe / Sensor Discovery」構想 ＋ AURELの「新しい血＝既存と相関しない情報源」を合流させた最初の一手。
> **目的**: 37系統の材料それぞれを [接続状態・入手経路・費用・頻度・過去履歴・品質・対既存相関の見込み・入手容易性] で棚卸しし、拡張の優先順位を「相関の低さ × 入手の易しさ」で決める。
> **規律（不変）**: 一度に全部入れない。1本ずつ入れ→ガントレットにかけ→**壁が実際に何%動いたかを実測**し、動いた分だけ残す。材料増設と同時に偽陽性率（多重検定）を監視する。紙・金ゼロ・読取専用・鍵は会長のみ。

## 現状の視界（実ファイルで確認・2026-09-03）
機関が今つないでいるのは、37系統のうち実質 **3系統**：
- **① Price**: `data/bars_*.csv` = **58銘柄OHLC**（米株ETF SPY/QQQ/IWM・セクター11本 XLx・国別ETF EWx/INDA/EEM/EFA・FX 8本・コモディティ WTI/GLD/COPPER/CORN/NATGAS/XAU/XAG・暗号 BTC/ETH/SOL 他・VIX・債券ETF TLT/IEF/HYG）
- **㉒ Macro（FRED・無料鍵不要）**: `external_macro.json` = **3系列**（T10Y2Y 利回り曲線 / BAMLH0A0HYM2 HY信用スプレッド / STLFSI4 金融ストレス）※今は「守りの一票」のみ、方向シグナル未使用
- **㉖ Event（ForexFactory・無料鍵不要）**: `event_calendar.json` = 週次の経済指標予定表（国/日付/時刻/重要度High-Med-Low）※今はカレンダー門（休場判定）中心

→ **視界の約9割はまだ暗い。** ただし後述の通り、暗い部分の一部は「今持っている58本から金ゼロで絞り出せる」。

## ★重要な発見 — Tier 0：新規データ取得ゼロで作れる「準・新しい血」
以下4系統は**外部データを一切買わず・鍵も要らず・今日から**、既存の58barから計算できる。値段の生データとは「負け方」が違う（相関構造・分散のメタ情報）ので、σを下げる血になり得る。最優先の実験対象。
| # | 系統 | 既存barから作れるもの | 対既存相関の見込み |
|---|------|----------------------|------|
| ⑩ | Volatility | Realized Vol / Vol-of-Vol（各銘柄の実現ボラ・その変化） | 中（値段の二次モーメント＝一次と負け方が違う） |
| ⑲ | Correlation | Rolling相関・相関崩壊/急上昇の検知 | **低**（相関そのものはレジーム変化の先行情報） |
| ⑳ | Dispersion | 指数 vs 構成銘柄・銘柄間分散（XLx群やETF群で算出） | **低** |
| ㉑ | Cross-Asset | 株×債×金×原油×FX×暗号の異常な連動/乖離 | 中〜低 |

## 37系統 拡張レジストリ
凡例 — 接続: ✅接続済 / 🟡値段代理のみ(構造データ未) / ⬜未接続 ｜ 費用: 無=無料鍵不要 / 鍵=無料要鍵 / $=有料 / infra=要低遅延インフラ
| # | 系統 | 接続 | 入手経路(例) | 費用 | 頻度 | 過去履歴 | 対既存相関 | 入手容易性 | Tier |
|---|------|------|------------|------|------|---------|-----------|-----------|------|
| ① | Price | ✅ | 既存bars | 無 | 日次 | 有 | — | — | 済 |
| ② | Volume | ⬜ | データ源にOHLCV | 無〜鍵 | 日次 | 有 | 中 | 易 | 1 |
| ③ | Order Book | ⬜ | 取引所L2 | $/infra | RT | 弱 | 中 | 難 | 3 |
| ④ | Order Flow(CVD/Delta) | ⬜ | Tick/約定方向 | $/infra | RT | 弱 | 中 | 難 | 3 |
| ⑤ | Liquidity(spread/depth) | ⬜ | 板/スプレッド | $/infra | RT | 弱 | 中 | 難 | 3 |
| ⑥ | Positioning(COT) | ⬜ | CFTC COT | 無 | 週次 | 有 | **低** | 中(整形要) | 1 |
| ⑦ | Crowd(節目/Stop集中) | 🟡 | 既存barから推定 | 無 | 日次 | 有 | 中 | 易 | 2 |
| ⑧ | Open Interest | ⬜ | 先物/暗号OI | 無〜鍵 | 日次 | 中 | 中 | 中 | 2 |
| ⑨ | Options(IV/skew/gamma) | ⬜ | オプション連鎖 | $ | 日次 | 中 | **低** | 難($) | 3 |
| ⑩ | Volatility(RV/逆ボラ) | ✅**恒久接続(2026-09-03)** | sensor_inv_vol.py(walk-forward) | 無 | 日次 | 有 | 中 | 易 | **済** |
| ⑪ | Futures Curve | ⬜ | 期先価格 | 無〜$ | 日次 | 中 | 中 | 中 | 2 |
| ⑫ | Funding/Basis | ⬜ | 暗号取引所API | 無 | 日次 | 有 | 中 | 易(暗号) | 2 |
| ⑬ | Interest Rates | 🟡 | FRED拡張 | 無 | 日次 | 有 | 中 | 易 | 1 |
| ⑭ | Yield Curve | 🟡 | FRED(既1系列→多点) | 無 | 日次 | 有 | 中 | 易 | 1 |
| ⑮ | Credit(HY/IG/CDS) | 🟡 | FRED(既HY→IG追加) | 無 | 日次 | 有 | **低** | 易 | 1 |
| ⑯ | FX Structure(DXY/強弱) | 🟡 | 既存FX 8本+DXY | 無 | 日次 | 有 | 中 | 易 | 1 |
| ⑰ | Capital Flow(ETF flow) | ⬜ | ETF資金流出入 | 鍵/$ | 日次 | 中 | **低** | 中 | 2 |
| ⑱ | Breadth(A/D,52w高安) | ⬜ | 指数構成の参加率 | 無〜鍵 | 日次 | 中 | **低** | 中 | 1 |
| ⑲ | Correlation | 🟡→**Tier0** | **既存barで算出** | 無 | 日次 | 有 | **低** | 易 | **0** |
| ⑳ | Dispersion | 🟡→**Tier0** | **既存barで算出** | 無 | 日次 | 有 | **低** | 易 | **0** |
| ㉑ | Cross-Asset | 🟡→**Tier0** | **既存barで算出** | 無 | 日次 | 有 | 中〜低 | 易 | **0** |
| ㉒ | Macro(CPI/雇用/PMI) | ✅一部 | FRED拡張 | 無 | 月次 | 有 | 中 | 易 | 1 |
| ㉓ | Central Banks | 🟡 | FOMC日程(Event含) | 無 | 不定 | 有 | 中 | 易 | 1 |
| ㉔ | Econ Surprise | ⬜ | 予想vs実績(FF consensus) | 無〜鍵 | 不定 | 中 | **低** | 中 | 1 |
| ㉕ | News | ⬜ | ニュースフィード+NLP | 鍵/$ | RT | 弱 | 低 | 難(NLP) | 3 |
| ㉖ | Event | ✅ | ForexFactory | 無 | 週次 | 有 | 中 | 易 | 済/活用 |
| ㉗ | Sentiment(Fear/Greed) | ⬜ | 調査/指数 | 無〜鍵 | 日次 | 中 | 中 | 中 | 2 |
| ㉘ | Earnings | ⬜ | EPS/Rev/Guidance | $ | 四半期 | 有 | **低** | 難($) | 3 |
| ㉙ | Corporate Actions | ⬜ | Buyback/M&A/Insider | 鍵/$ | 不定 | 中 | 低 | 中 | 3 |
| ㉚ | Commodity Physical | ⬜ | 在庫/生産/季節性 | 無〜$ | 週次 | 中 | 中 | 中 | 2 |
| ㉛ | Crypto On-chain | ⬜ | Exchange flow/Whale | 無〜鍵 | 日次 | 有 | 中 | 中 | 2 |
| ㉜ | Derivatives Stress | ⬜ | 清算/Funding異常 | 無(暗号) | 日次 | 中 | 中 | 中 | 2 |
| ㉝ | Geopolitics | ⬜ | 事件/制裁/選挙 | 鍵/$ | 不定 | 弱 | 低 | 難 | 3 |
| ㉞ | Fiscal | ⬜ | 財政/国債発行 | 無(FRED) | 月次 | 有 | 中 | 易 | 2 |
| ㉟ | Banking/Liquidity | 🟡 | FRED(準備預金/Repo/BS) | 無 | 週次 | 有 | **低** | 易 | 1 |
| ㊱ | Microstructure | ⬜ | Quote頻度/Impact | infra | RT | 弱 | 中 | 難 | 3 |
| ㊲ | Historical Memory | 🟡 | 上記の時系列保存 | 無 | — | — | — | 既`market_memory` | 0 |

## 拡張の順序（相関の低さ × 入手の易しさ）
- **Tier 0（今日・金ゼロ・データ取得ゼロ）**: ⑩RV・⑲Correlation・⑳Dispersion・㉑CrossAsset を既存58barから算出しサーフェス化。㊲Historical Memory は `market_memory.py` が既に器を持つ。→ **最初の実験はここ**。買わずに「新しい種類の血」を4本試せる。
- **Tier 1（無料・鍵不要・相関低・要整形）**: FRED深掘り（⑬⑭⑮㉒㉟＝多点利回り曲線/IGスプレッド/準備預金）、㉔EconSurprise（ForexFactory consensus）、⑥COT（CFTC無料）、⑱Breadth。既配線のFRED/Eventを土台に増点。
- **Tier 2（無料だが別市場 or 要処理）**: ⑫Funding/Basis・㉛On-chain・㉜DerivStress（暗号系API無料）、⑧OI、⑪FuturesCurve、⑦Crowd。
- **Tier 3（有料 or 難・後回し）**: ⑨Options・③④⑤板/フロー・㉕News・㉘Earnings・㉝Geopolitics・㊱Microstructure。効けば大きいがノイズ大・費用/インフラ要。会長の投資判断が要る領域。

## Sensor Discovery（外部AI案・既存フローの自然な延長）
機関は既に `frontier.wall_diagnosis → discovery.research_requests` で「壁の律速を狙う研究要求」を自動生成し、`proposals.py`（起案→会長二重ロック）の器を持つ。保留 H-0010(uncharted/data_insufficient) が原始形。
→ **拡張案**: Discoveryが「この仮説はデータ不足で裁けない(data_insufficient)」と判定したとき、単にHOLDするのでなく **SENSOR REQUEST を起案**する（必要な系統・候補データ源・費用/履歴/品質のAUREL調査を添付）→会長承認→レジストリに追加→過去データ取得→market_memory→Discovery再開。「見るべきものそのもの」を機関が発見する。着工は本レジストリの Tier 0/1 が回り始めてから（順序を守る）。

## 未決・会長判断が要る点
1. **偽陽性の門**: 材料を増やすと多重検定で偽エッジが増える。Tier 0 着工と同時に「サーフェスあたりの棄却率/採用率」を監視する小さな計器を足すか（AUREL推奨=足す）。
2. **Tier 3の投資判断**: Options/News/Earnings/Alt-data は有料。費用対効果はTier 0/1で「新しい血が実際に壁を動かすか」を見てから判断（今は判断材料不足＝保留が正しい）。
3. 着工の最初の1本: AUREL推奨 = **⑲Correlation**（対既存相関が最も低い見込み・算出容易・レジーム変化の先行情報）。
