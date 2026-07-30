---
doc_id: AURELIAN-ADVISOR-DIRECTIVE-STAGE34-v1
tags: [institution, directive, source-of-truth, advisor, stage3, stage4]
type: source-directive
rank: 指示原本（Stage 3+4・ChatGPTアドバイザー承認）
created: 2026-07-30
registered: 2026-07-30
owner: AUREL（統括CEO）
source: 会長（KEIKI MAEDA）経由 ChatGPTアドバイザー
approver: 会長（KEIKI MAEDA）
---

# 機関構築 指示原本 — Stage 3+4（連続実行）

> **これは Stage 3+4 の指示原本（source of truth）。** Stage 1+2 監査を「合格」と裁定した上での次段階指示。
> **監査合格の裁定（2026-07-30 会長）**: Aurelian正式成立・Institutional Core独立配置・憲章階層・Prop読取専用登録・INSTITUTION-STATUS.md・レガシー精査・非干渉を承認。
> **ETH武装解除の裁定**: 会長承認下の武装解除は正しい判断。これは後退ではなく、**機関監査が初めて実際の資本・実行経路の衝突を発見し防止した成果**として正式に決定履歴へ記録する。
> **今回の目的**: 見た目の刷新ではない。**Aurelianの現在状態を単一情報源で管理し、AUREL・機関ステータス文書・中央司令画面が同じ状態を参照する構造**を作る。

---

## Stage 3：機関状態モデルと中央司令画面

1. **単一情報源 `institution_state.json` を新設**。既存DBスキーマ変更せず、institution配下の独立新規ファイル。保持項目: 機関名/全体フェーズ/各Division状態とフェーズ/Core状態/各利益源の稼働区分/LIVE・PAPER・DRY RUN・FROZEN・DISARMED状態/使用口座と用途区分/実弾稼働数/保護境界/稼働中システム/完成済/未完成/進行中/警告と異常/会長判断待ち/次の最優先/最近の重要決定/最終更新日時/更新理由/各情報の取得元/確認済み事実と推測の区別。
2. **INSTITUTION-STATUS.md を状態データと整合**。完全自動生成は不要。役割分離: json=機械可読の単一情報源／md=会長向けの説明・理由・次の一手／AUREL=両方を参照して説明する統括CEO。
3. **dashboard.html は変更しない。** 代わりに `aurelian_command.html` を別ファイルで新設。初期版は**読取専用**（操作・実行・停止・再起動・設定変更ボタンを付けない）。表示: 【機関総覧】総合状態/フェーズ/実弾数/paper数/dry-run数/frozen・disarmed数/異常数/会長判断待ち数/最終更新。【Division一覧】Proprietary/Prop/Research and Evolution/Audit and Risk/Future — 各々 状態/フェーズ/稼働モード/利益源/最終更新/警告/次の一手。【会長ナビゲーション】何を構築/現在地/次に何を/なぜ/会長判断事項/最近の重要決定。【保護・安全状態】g4_境界/人格UI保護/実弾ロック/凍結資産/非干渉。
4. **既存 g4_dashboard・dashboard.html・aurel_life.html は埋め込まない。** リンク/参照先として表示のみ。無理に1つへ結合しない。

## Stage 4：責任境界と正式所属

1. **Institutional Core を正式定義**: ledger / defense / bus / allocator / observatory / execution gateway。
2. **Audit and Risk と役割分離**: Core=記録・防衛・信号・資本配分・観測・執行ゲートを**実行する技術基盤**。Audit and Risk=それらの設定・動作・結果・例外・違反・資本リスクを**監督し会長とAURELへ報告する統治部門**。（例: ledger=記録するシステム／Audit=記録の完全性を検査する部署。defense=リスク制御を実行／Risk=制御基準と違反を監督）。所有関係と監督関係を正式文書に。
3. **各既存モジュールについて確定**: 正式名称/所属/目的/入力/出力/実行権限/監督部署/保護レベル/現在状態/依存先。
4. **利益源と共通基盤を分離**: Core自体は利益源ではない。Proprietary と Prop が利益源を保有し、Coreが両者を支える。Propへの接続は引き続き読取専用（Coreからg4_へ命令・書込みしない）。

## 今回の記録事項（正式な重要決定として記録）
- Aurelianは正式に成立した。
- 実弾稼働は現在ゼロ。
- ETH自律枠は口座衝突のため DISARMED。
- 維持機は FROZEN。
- プロップドライランは ACTIVE / DRY RUN / READ ONLY。
- 現在の機関フェーズは「統治・表示・監査基盤の構築」。
- Stage 5の実弾利益源選定は Stage 3+4 完了後に行う。

## 今回の変更禁止
既存取引コード変更／g4_関連書込み／実行中プロセス停止・再起動／タスクスケジューラ変更／既存DBスキーマ変更／dashboard.html変更／g4_dashboard変更／aurel_life.html変更／ETH自律枠の再武装／実弾設定変更／既存ファイル削除／操作ボタンの実装 — いずれも禁止。

## 完了報告（提出物10件）
1. institution_state.json の構造と現在値 / 2. INSTITUTION-STATUS.md 更新内容 / 3. aurelian_command.html 画面構成 / 4. Institutional Core 正式定義 / 5. Audit and Risk との責任境界 / 6. 各既存モジュール所属表 / 7. 利益源と共通基盤の分離確認 / 8. 作成・変更ファイル一覧 / 9. 非干渉確認 / 10. Stage 5 で会長が判断すべき事項。

---

## 改定
- v1（2026-07-30）: Stage 3+4 指示原本を登録。
