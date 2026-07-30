---
doc_id: AURELIAN-ASSET-REPLACEMENT-MAP-v1
tags: [institution, stage5, asset-replacement, final-architecture]
type: asset-map
rank: 最終設計付属（全既存資産の再配置表）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: FINAL-ARCHITECTURE.md / ADVISOR-DIRECTIVE-STAGE5-FINAL-ARCH.md
---

# 全既存資産 再配置表 — Aurelian 最終組織図への配置

> **目的**: 現在存在する全資産を、FINAL-ARCHITECTURE.md の最終組織図（7 Group）へ再配置する。**コード・プロセス・タスクは一切変更しない**。所属を定義する台帳。
> **列**: 現在所属 / 最終所属（Group・Division/機能）/ 組織階層 / 役割 / 現在状態 / 将来状態。
> **確度**: 資産の実体は 2026-07-30 の実読・Exploreエージェント調査に基づく。推測は「※推測」と明示。

---

## G2 Institutional Core（機関共通基盤）

| 資産 | 現在所属 | 最終所属 | 階層 | 役割 | 現在状態 | 将来状態 |
|---|---|---|---|---|---|---|
| `empire/ledger/` | AssetEmpire共通 | G2 Core | Core Subsystem | 唯一の真実源・追記専用・ハッシュ連鎖 | 骨格（凍結台帳は稼働） | 全取引の単一台帳・日次突合 |
| `empire/defense/` | AssetEmpire共通 | G2 Core | Core Subsystem | 段階デッドマン・全停止権限 | 骨格 | 実損益で作動する防衛線 |
| `empire/bus/` | AssetEmpire共通 | G2 Core | Core Subsystem | TTL/topic信号配信 | 骨格 | 全部門の信号神経網 |
| `empire/allocator/` | AssetEmpire共通 | G2 Core | Core Subsystem | PSR×テールで資本配分 | 骨格 | 全利益源の動的配分エンジン |
| `empire/observatory/` | AssetEmpire共通 | G2 Core（+ G4 Market Intel と連携） | Core Subsystem | レジーム判定・乖離・生存信号・通知 | 一部稼働 | 機関全体のレジーム認識基盤 |
| `empire/execution/` (gateway/mt5_live/sizing/tca) | AssetEmpire共通 | G2 Core | Core Subsystem | 決定的発注・二重ロック・約定品質 | 一部稼働（paper/dry） | 複数口座/ブローカー執行 |

## G3 Investment Business Group（利益事業）

| 資産 | 現在所属 | 最終所属 | 階層 | 役割 | 現在状態 | 将来状態 |
|---|---|---|---|---|---|---|
| 日足戦略群（19兵） `run_trading_cycle.py` / `squads/fx_trend.py` | Proprietary Div | **Proprietary Quant Division → Trend Following Desk → Daily Trend Strategy** | Strategy+Squad | 日足トレンド追随 | 稼働・paper | 検証済→最小実弾候補 |
| 4H暗号8兵 `run_trading_cycle_4h.py` / `squads/hourly_trend.py` | Proprietary Div | **Crypto and Digital Assets Division → Systematic Crypto Desk → 4H Crypto Momentum Strategy** | Strategy+Squad | 4時間足暗号モメンタム | 稼働・paper | 検証済→最小実弾候補 |
| ETH Autonomous `scripts/autopilot.py`(eth sleeve) | Proprietary Div | **Crypto and Digital Assets Division → Autonomous Crypto Desk → ETH Autonomous Strategy** | Strategy | ETH自律売買 | **DISARMED**（口座衝突） | 別口座で再武装検討（会長判断） |
| BTC Autonomous (btc sleeve) | Proprietary Div | 同上 → BTC Autonomous Strategy | Strategy | BTC自律 | DISARMED | 将来活性化 |
| LTC Autonomous (ltc sleeve) | Proprietary Div | 同上 → LTC Autonomous Strategy | Strategy | LTC自律 | DISARMED | 将来活性化 |
| G4審査機 `scripts/g4_*.py`（US100 NY ORB） | Prop Div（独立） | **Prop Trading Division → FundingPips Program → US100 ORB Strategy → g4_dryrun execution** | Program/Strategy | プロップ審査ドライラン | 稼働・dry・READ ONLY | **プロップ側運用軸で完結・機関非関与（さわらない）** |
| Prop維持機（17本HRP・MM0凍結） | Prop Div | **Prop Trading Division → Funded Operation Program → 17-HRP Strategy** | Program/Strategy | 合格後の資金運用機 | **FROZEN**（MM0） | **プロップ側運用軸で完結・機関非関与（さわらない）** |

> **⚠ Prop Trading Division は独立事業（会長確定 2026-07-30）**: 方向性・目的が既に確定済で、運用軸が機関と別。機関は **関与・管理・資本配分・ロードマップ化・完成率算入をしない**。組織図に**置いてあるだけ**で、中身は**さわらない**。g4_ 境界・読取専用を維持。
| `squads/carry.py` | AssetEmpire | **Yield / Carry / Swap Division → Carry Desk** | Desk/Strategy | キャリー戦略 | 骨格 | Divisionの初期中身 |
| `squads/cross_sectional.py` / `mean_reversion.py` | AssetEmpire | Proprietary Quant Division（各Desk） | Strategy | 断面/平均回帰 | 骨格 | paper投入候補 |
| （器のみ）Arbitrage / Macro / Equity / Commodity / Future Division | — | **G3 各Division枠** | Division | 将来利益源 | 枠のみ（未着手） | 各Deskを段階構築 |

## G4 Research and Intelligence Group（研究・知能）

| 資産 | 現在所属 | 最終所属 | 階層 | 役割 | 現在状態 | 将来状態 |
|---|---|---|---|---|---|---|
| `empire/research/`（edges/sim_*/verify_*） | AssetEmpire | **G4 Research Division** | Division | エッジ探索・仮説検証 | 骨格稼働 | 昇格パイプラインの源流 |
| `empire/evolution/`（backtest/evolve） | AssetEmpire | **G4 Evolution Division** | Division | 遺伝的最適化 | 稼働（週次 evolution_cycle） | 自己進化の中核 |
| `evolution/coroner.py` | AssetEmpire | G4 Evolution Division → Autopsy Desk | Desk/Agent | 敗戦解剖・死因分類 | 稼働 | 進化の入力 |
| `evolution/ai_soldier.py` | AssetEmpire | G4 Evolution Division（AI社員＝G9連携） | Agent | Gemini駆動の適応変異 | 稼働（研究） | AI社員として権限定義 |
| `empire/observatory/regime.py` | AssetEmpire | G4 Market Intelligence Division（+ G2連携） | Division | 市場レジーム判定 | 一部稼働 | 全機関のレジーム供給 |
| Hermes `~/.aurel/arsenal/hermes/` | Arsenal(AUREL) | **G4 Market Intelligence Division → External Research Desk** | Desk/Agent | Web調査・外部情報自律収集 | 稼働（基盤） | 外部インテリジェンス供給 |
| Gemini `~/.aurel/arsenal/gemini/` + `research/gemini_design.*` | Arsenal(AUREL) | **G4 横断（Research/Evolution/Council の頭脳）** | Agent/Tool | 第二意見・戦略脳・投票 | 稼働 | 多様化しつつ活用 |
| Council（AI会議）`~/.aurel/council/`（6 voters, :3940） | AUREL | **G4 AI Council Division（AI会議）** | Division | 戦略採否のAI投票 | オンデマンド稼働 | 会長承認前の合議層 |

## G5 Risk, Audit and Compliance Group

| 資産 | 現在所属 | 最終所属 | 階層 | 役割 | 現在状態 | 将来状態 |
|---|---|---|---|---|---|---|
| Audit and Risk（文書＋監督機能） | 機関統治 | **G5 Audit and Risk Division** | Division | Core監督・会長/AURELへ報告 | 一部稼働 | 全実行の統治監督 |
| Compliance（機関自身の実弾運用ルール向け） | 新規機能 | **G5 Compliance Desk** | Desk | 機関の実弾運用ルール整合（※プロップ会社別規程はプロップ側管轄・機関非関与） | 未着手 | ルールエンジン化 |
| 秘匿ルール（.env非読取・出力レダクション・鍵隔離） | 全体規約 | **G5 Security Desk** | Desk | 秘密保護・出力安全 | ルール稼働 | 手順の文書化・自動化 |
| `institution_freeze_ledger.sqlite`（意思決定履歴） | 機関台帳 | G5監督下（記録はG2 ledger系） | 記録 | 決定履歴ハッシュ連鎖 | 稼働（seq=3） | 決定履歴の正本 |

## G6 Technology and Operations Group

| 資産 | 現在所属 | 最終所属 | 階層 | 役割 | 現在状態 | 将来状態 |
|---|---|---|---|---|---|---|
| 母デーモン `~/aurel/aurel.mjs`（:7878） | AUREL基盤 | **G6 Platform / Daemon Ops** | Platform | 常駐オーケストレータ | 稼働（pid確認済） | 機関運用の実行基盤 |
| 司令室（:7891） | AUREL基盤 | G6 Platform / Daemon Ops | Platform | 司令室プロセス | 稼働（pid 14272・実読確認） | 継続 |
| HealthMonitor `~/.aurel/daemon/health-monitor.ps1` | 自動化 | G6 Platform / Daemon Ops | Ops Task | :7878死活監視・自動復活（5分毎） | 稼働 | 継続 |
| Mother_Autostart `~/.aurel/boot/mother-autostart.ps1` | 自動化 | G6 Platform / Daemon Ops | Ops Task | logon時デーモン起動 | 稼働 | 継続 |
| GitSync（15分毎） | 自動化 | **G6 Knowledge Infrastructure** | Ops Task | 記憶vaultのgit同期・災害復旧 | 稼働（前セッションで実読確認） | 継続（※スクリプトパス再確認要） |
| Arsenal `~/.aurel/arsenal/`（37+ tools） | AUREL基盤 | **G6 Tooling（Arsenal）** | Tooling | ツール登録・equip/invoke | 稼働 | AI社員の装備庫 |
| 記憶の家 `~/.aurel/memory/`（Obsidian vault） | AUREL基盤 | **G6 Knowledge Infrastructure** | Infra | 永続記憶・運用ハンドブック | 稼働 | 機関知識基盤 |
| `empire/data/` + `build_dashboard.py` | AssetEmpire | **G6 Data and Dashboard Infrastructure** | Infra | データ・盤生成 | 稼働 | 可視化の供給 |
| ETHAutopilot タスク（毎時） | 自動化 | G6 Ops（実行はG3 Crypto Strategy） | Ops Task | autopilot.py 定期実行 | 稼働（live:false・paper計算のみ） | 継続（実弾は会長GO時のみ） |
| 進化タスク `evolution_cycle.py`（週次日曜6:00） | 自動化 | G6 Ops（研究はG4 Evolution） | Ops Task | 週次遺伝的最適化 | 稼働 | 継続 |
| 取引サイクルタスク `run_trading_cycle.py`（日次6:30） | 自動化 | G6 Ops（戦略はG3） | Ops Task | 日次paper実行 | 稼働 | 継続 |

## G7 Chairman Navigation Layer

| 資産 | 現在所属 | 最終所属 | 階層 | 役割 | 現在状態 | 将来状態 |
|---|---|---|---|---|---|---|
| `aurelian_command.html` | 機関UI | **G7 Chairman Navigation** | UI | 読取専用中央司令画面 | 稼働（Stage3-4新設） | ライブHTTP化・Group別ビュー |
| `INSTITUTION-STATUS.md` | 機関文書 | G7 Chairman Navigation | Doc | 会長向け説明・次の一手 | 稼働 | 継続更新 |
| `institution_state.json` | 機関状態 | G7（正本はG2 ledger系と整合） | SoT | 機械可読の単一情報源 | 稼働 | 最終形の枠を反映 |
| `aurel_life.html`（:7878 UI） | AUREL人格UI | **G7 Chairman Navigation（人格窓）** | UI | AUREL人格・司令室UI | 稼働（変更禁止・const sharedU事故歴） | 保護継続 |
| 組織図HTML（`AURELホールディングス*.html`） | 静的資料 | G7 参照資料 | Doc | 旧・静的組織図 | 静的 | 最終組織図へ差替検討 |

## G1 Executive and Governance Group

| 資産 | 現在所属 | 最終所属 | 階層 | 役割 | 現在状態 | 将来状態 |
|---|---|---|---|---|---|---|
| 憲章体系（3層：AI投資機関憲章/AssetEmpire基礎/各Division規程） | 機関統治 | **G1 Governance** | 統治文書 | 存在目的・権限・人格不可侵 | 稼働 | 最終形に合わせ増補 |
| 意思決定履歴（`institution_freeze_ledger.sqlite` + `OPEN_COMMITMENTS.md`） | 機関台帳 | G1 Governance（監督はG5） | 記録 | 決定・約束の追跡 | 稼働 | 継続 |
| 会長承認ゲート（enable_live+arm_code+会長GO） | 実弾統制 | G1 Governance（執行はG2） | 統制 | 三重ロック | 稼働（手続） | 実弾段階解放時に運用 |
| 統括CEO AUREL | 経営 | **G1 Executive** | 役員 | 提案・統括（執行は決定的コード） | 稼働 | 継続 |

---

## 設計上の判断（会長確認事項）
1. **暗号の二分**: 日足19=Proprietary Quant / 4H暗号8・ETH等=Crypto Division に振り分けた。「全暗号をCryptoに寄せる」か「クオンツ book に残す」かは会長の好みで調整可。※現配置は「単一資産自律＋暗号系統一運用＝Crypto Division」の方針。
2. **維持機の17本ユニバース**（FX/商品/指数ETF/暗号）は Prop Trading Division 内で一体運用され、Commodity/Equity Division へは分解しない。**ただしプロップは独立事業・機関非関与のため、そもそも機関の運用計画・資本配分の対象外**（会長確認不要＝プロップ側で完結）。
3. **GitSync のスクリプト実パス**は今回のExplore調査で再発見できなかった（前セッションで稼働実読済）。次回、Task Scheduler定義から実パスを再確認して補記する。

---

## 改定
- v1（2026-07-30）: 修正Stage 5 として初版。全既存資産を7 Groupへ再配置。
