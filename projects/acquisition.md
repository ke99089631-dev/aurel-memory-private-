---
tags: [project, acquisition, distribution, sns, cross-cutting]
type: project
updated: 2026-08-30
---

# 集客部 — 共有記憶（全体から見える）

> 会長が 2026-08-30 新設。**全事業横断の集客エンジン（流通の臓器）**。
> 特定事業の子ではなく、車販売・プロップ英語圏・LocalBoost・将来事業が「顧客」として発注する横断部署。
> 作業フォルダ `C:\Users\user\Acquisition`。AUREL本体が専用空間で担当。

## なぜ作ったか
- SNS/SEO/HP流入はどの事業でも同じ型が使える。バラバラに作ると毎回ゼロから。
- 一箇所に貯めれば勝ち筋が資産として溜まり、事業間で転用できる（車販売→プロップ）。
- 数字を一元管理してどこに力を入れるか判断する。
- localboost原則と整合：「AIが下げるのは生産コストだけ。流通と信頼のコストは1円も下がらない」→ **流通を専門部署で持つ = 下がらないコストに正面から投資する**。

## 担当範囲
SNS基本管理 / 戦略 / ツール連携（Playwright武器庫・design/brand/stop-slop・gsheets再利用）/ SEO / HPへの流動（ファネル）/ アクセス数管理。

## 安全境界（この部署特化）
- 公開発信は会長GO後（承認ゲート）。下書き・分析・設計は自由、公開だけ止める。
- 広告＝金が動くものは二重ロック後。鍵ゼロ。
- 秘密は出さない・外部送信しない。プロップ(g4_)資産・口座・.env非接触。
- 全工程まず紙のみ・金ゼロ。

## 現在地（2026-08-30）
- Phase 0 完了：器を新設（CONCEPT/STATE/ROADMAP/共有記憶）。公開ゼロ・アカウント接続ゼロ・広告ゼロ。
- 最初のパイロット＝**車販売のSNS集客**（一番キャッシュに近い）。
- 次＝Phase 1「車販売パイロットの戦略1枚（紙のみ）」。

## ドキュメント
- 正本CONCEPT: `C:\Users\user\Acquisition\CONCEPT.md`
- 現状1枚: `C:\Users\user\Acquisition\STATE.md`
- ロードマップ: `C:\Users\user\Acquisition\ROADMAP.md`

## 専用部屋（PC＋携帯で同一台帳）
- **ノードID=`p_2488d8dd`**（表示名「集客部」）。車販売と同じくランダムID方式。
- **PCコンソール**: `http://127.0.0.1:7878` の上部タブ「集客部」（`C:\Users\user\aurel\aurel.mjs` が projects/ を走査してタブ化。API `POST /api/projects` でライブ追加＝再起動不要）。boundCwd=`C:\Users\user\Acquisition`、model=opus。
- **携帯窓口**: `http://100.73.107.61:8790`（Tailscale内のみ）。ルームキー=`acquisition`（`aurel_chat_server.py` ROOMS、`start_chat_rooms.vbs` で自動起動）。
- 履歴台帳: `C:\Users\user\.aurel\projects\p_2488d8dd\messages.jsonl`（PC・携帯で共有）。ノード記憶: 同フォルダ `memory\MEMORY.md`。
- 本体部屋(指令室)から分離した理由: 本体は投資/車販売で渋滞するため、集客は独立部屋で回す。

## 変更履歴
- 2026-08-30：新設。名前確定＝集客部。器一式作成。PCコンソール(タブ p_2488d8dd)＋携帯(8790)を開設し本体から分離。両者は同一台帳を共有。
