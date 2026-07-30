---
doc_id: AURELIAN-DIVISION-PROP-v1
tags: [institution, division, prop, read-only, g4]
type: division-charter
rank: 第3層（Division個別規程）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# Prop Trading Division（プロップ事業部門）規程 v1 — 読取専用登録

> **上位**: AI投資機関憲章 v1（第9条 プロップ事業の独立性）
> **原則**: この Division は既に設計・実装・運用条件が確定している。機関への統合は**読取専用**で行う。

---

## 1. 事業内容
- FundingPips 2-Step Standard チャレンジ（G4）。
- 現在フェーズ: **Phase 7**（$25k×1本の実弾GO待ち。dry-run 継続中）。
- 実行系: G4 runner（`g4_*.py`）、専用MT5端末 `C:\FundingPips-MT5\terminal64.exe`、専用venv `C:\Users\user\FundingPipsTrial\venv`。
- 口座番号 40000162046 はログイン番号=公開可。

---

## 2. 保護境界（不可侵）

**`g4_` プレフィックスを機関の保護境界として正式登録する。** 以下を機関は一切行わない：

1. `g4_` で始まるコードを**変更しない**。
2. `g4_` データへ**書き込まない**。
3. プロセスを**停止・再起動・変更しない**。
4. タスクスケジューラを**変更しない**。
5. 仮想環境・依存関係・設定・ログ形式を**変更しない**。
6. 既存システム（Empire側）と**結合しない**。

**許可される機能は3つのみ**：状態把握 / 結果表示 / 異常報告。

---

## 3. 読取対象（状態把握に使うファイル・読取専用）

| ファイル | 用途 |
|---|---|
| `g4_heartbeat.json` | 生死・稼働状態（live_idle 等）・srv_skew の把握 |
| `g4_daily/YYYY-MM-DD.json` | 当日の売買計画（EP/SL/TP/lots/RR）— 表示は公開ルール順守 |
| `g4_watchdog.log` | watchdog 稼働ログ（bat が g4_ プレフィックスで出力） |
| `g4_dashboard.html` / `g4_public.png` | プロップ盤（公開PNGは公開ルール順守） |

---

## 4. 公開ルール（ViewB 公開PNG）
**載せないもの**: ログインID/パスワード・サーバ名・ブローカーID・.envパス・絶対残高($)・EP/SL/TP価格・ロット数・pid/host/ファイルパス・srv_skew生値・未確定の決定。
**載せてよいもの**: 生死 / 稼働率% / カレンダーの色 / シグナル本数。

---

## 5. セキュリティ（不可侵）
- 研究は全て読取専用。お金は1円も動かさない（--dry only、runner は order_send を呼ばない）。
- Trial password（`C:\Users\user\FundingPipsTrial\.env`）は**表示・保存・ログ・書込を一切しない**。
- G2 聖域は不可侵。US100 数値は最終。凍結バックテスタ `session_breakout_trackA.py` は変更禁止（SHA256 74f1cacf...）。
- 実弾（受験料の支払い）は会長の最終GO後にのみ。物理的な送信・支払いは会長の手で。

---

## 改定
- v1（2026-07-30）: 初版。読取専用登録。稼働システムへ干渉なし。
