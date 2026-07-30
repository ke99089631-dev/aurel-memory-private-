---
doc_id: AURELIAN-INSTITUTION-STATUS-v1
tags: [institution, status, dashboard, pinned, top-level]
type: status
rank: 司令室・常設ステータス（会長がいつでも開く1枚）
created: 2026-07-30
updated: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# Aurelian — 機関ステータス v1

> **これは会長がいつでも開く「機関の全体像＋現在地＋会長判断待ち」1枚**。重要決定・GO・数値が変わるたびに更新する。Chairman Navigation Layer の実体。

> **情報源の役割分担（Stage 3+4 で確定）**
> - `institution_state.json` = **機械可読の単一情報源（source of truth）**。数値・状態・カウントの正本。
> - `INSTITUTION-STATUS.md`（本書） = 会長向けの**説明・理由・次の一手**。json と整合させる。
> - `aurelian_command.html` = 上記を**読取専用で表示**する中央司令画面（操作ボタンなし）。
> - AUREL = 両方を参照して会長に説明する統括CEO。
> 数値が食い違う場合は json を正とし、本書を追随更新する。

---

## 0. 機関の最終目的（一行）
複数の独立利益源を持ち、**破産回避を最優先の床とした上で**、資本を保全しながら複利で増殖させるAI投資機関。会長=オーナー/最終決定者、AUREL=統括CEO。

---

## 1. 正式組織図（要約）
```
会長 KEIKI MAEDA
  └ 統括CEO AUREL
      ├ Institutional Core（共通基盤: 台帳/防衛/バス/アロケータ/観測/執行）※利益源ではない
      ├ Proprietary Investment Division（自己勘定）※現在 実弾ゼロ・paper群のみ
      ├ Prop Trading Division（プロップ・読取専用/g4_境界）
      ├ Research and Evolution
      ├ Audit and Risk
      └ Future Strategy Divisions（枠）
```
詳細 → ORG-CHART.md ／ Core の定義 → INSTITUTIONAL-CORE.md ／ 機械可読の正本 → institution_state.json

---

## 2. 各Divisionの現在フェーズ

| Division | フェーズ | 実弾 |
|---|---|---|
| Institutional Core | 骨格〜一部稼働 | ― |
| Proprietary Investment | paper群のみ稼働（ETH実弾は2026-07-30 武装解除） | **実弾ゼロ**（ETH口座衝突のため停止） |
| Prop Trading | Phase 7（$25k実弾GO待ち・dry継続）／維持機=MM0凍結済 | 未（受験料GO待ち） |
| Research and Evolution | 骨格 | ― |
| Audit and Risk | 一部稼働（台帳/防衛） | ― |
| Future Strategy | 枠のみ | ― |

---

## 3. 稼働中の利益源【確認済】
- ⚠️ **現在、実弾で動いている利益源はゼロ**（2026-07-30時点）。
- **ETH自律枠**: 2026-06-16 LIVE開始 → **2026-07-30 武装解除（live:false）**。理由=発注先(login 27972608)が会長の裁量トレード口座と同一で衝突。会長GOで停止。再武装は会長GO必須。
- 日足19 / 4h暗号8 = paper（練習）継続。実弾ではない。
- プロップ = dry-run（受験準備段階・利益源ではない）。
- **意味**: 機関は現在「守り＋準備」フェーズ。次の実弾利益源は (a) ETHを別口座で再武装 か (b) プロップ合格後の実弾運用。いずれも会長GO待ち。

---

## 4. 完成済 / 未完成 / 進行中

**完成済（稼働）**:
- ETH自律枠 LIVE 運用ループ
- 日足19 / 4h暗号8 の paper 運用ループ
- プロップ G4 dry-run（4営業日連続ゼロ欠測）
- AUREL在宅デーモン :7878 + 司令室 :7891 + 死活監視/自動復活/記憶バックアップ

**骨格のみ（活性化待ち）**:
- 統合台帳・資本アロケータの本活性化
- research/evolution の実運用投入
- BTC/LTC 枠（武装解除）

**未完成（枠のみ）**:
- Future Strategy Divisions

**進行中（今回の作業）**:
- Stage 3+4：機関状態モデル（institution_state.json）・中央司令画面（aurelian_command.html）・Core/Audit責任境界（INSTITUTIONAL-CORE.md）の確定

---

## 5. 直近の重要決定と理由
- **2026-07-30 機関昇格方針決定**（会長）: ゼロ再構築せず、既存AssetEmpireの骨格を活用し正式なAI投資機関へ昇格・再編成。理由=骨格が既に~90%完成しており、再構築は破壊的で無駄。
- **2026-07-30 機関名 Aurelian（アウレリアン）確定**（会長裁可。旧暫定案 AUREL Capital は却下）。
- **2026-07-30 プロップは読取専用登録**（g4_保護境界）。理由=設計確定済・干渉は事故リスク。
- **2026-06-16 ETH自律枠 常時GO**（会長）: 枠内自律運用を許可。

---

## 6. 次の最優先作業
1. Stage 3+4 成果物の会長レビュー（institution_state.json / INSTITUTIONAL-CORE.md / aurelian_command.html / 本ステータス）。
2. **Stage 5：実弾利益源の選定**（会長判断）— (a) ETHを別口座で再武装 か (b) プロップ合格後の実弾運用。
3. Institutional Core（台帳/アロケータ）本活性化計画の策定（会長GO後）。
4. プロップ Phase 7 の実弾GO判断（会長）。

---

## 7. ⚠️ 会長判断待ち（未解決）

| # | 事項 | 内容 |
|---|---|---|
| J-1 | 機関名の確定 | ✅ 解決。**Aurelian（アウレリアン）で確定**（会長裁可 2026-07-30）。 |
| J-2 | **ETH口座衝突** | ✅ **解決（2026-07-30 会長GO）**。会長が「27972608は今、手で取引している同じ口座」と確定回答→衝突確認。**eth sleeve を live:false に武装解除**（`autopilot_config.json`、バックアップ `autopilot_config.backup_2026-07-30_pre-eth-disarm.json`）。武装解除時 eth position=flat（開玉なし・巻き戻し不要）。btc/ltcは元からfalse。台帳記録＝`institution_freeze_ledger.sqlite` seq=2（hash 59494f61…）。**再武装は会長の最終GO必須。** プロセス(autopilot.py)は停止せず・configの値変更のみ。 |
| J-3 | プロップ実弾GO | Phase 7 の $25k×1本 受験料支払いGO。 |
| J-4 | Core活性化 | 台帳/アロケータ本活性化への着手可否（Stage 3）。 |
| J-5 | 維持機の系譜 | 維持機はMM0凍結済（`archive/2026-07-30_maintenance_17hrp_freeze`・専用台帳seq=1）。審査終了まで改善探索禁止（凍結保存のみ）。 |
| J-6 | 維持機-8%接触率の権威確定 | ~~再走を許可するか会長判断待ち~~ → **会長裁定 2026-07-30: B＝当面据え置き**（合格前で未定すぎる・将来改良の余地を残す）。再走せず現状維持。合格が視野に入ってから会長指示で扱う。 |
| J-7 | 凍結台帳の統合先 | MM0凍結は専用 `institution_freeze_ledger.sqlite` に記録（ライブDB競合回避）。特定の統合台帳へ寄せるべきか会長判断待ち。 |

---

## 8. 各システム稼働状態【確認済 2026-07-30】
- AUREL在宅デーモン :7878 = pid 13092（07-25 22:40〜）稼働
- 司令室 :7891 = pid 14272 稼働
- ETHAutopilot = 毎時稼働継続（タスク/プロセスは止めていない）。ただし eth sleeve `live:false` のため**実弾発注はしない**（paper計算のみ）。
- GitSync = 15分毎 result 0（last 09:22）
- HealthMonitor = 5分毎 result 0（last 09:34）
- プロップ G4 = dry-run 稼働（heartbeat live_idle）

---

## 9. プロップDivision隔離状態
- 保護境界 `g4_` プレフィックス正式登録済。
- 機関からの操作は**読取専用**（状態把握/結果表示/異常報告のみ）。
- コード・データ・プロセス・タスク・venv・ログ形式へ**今回一切干渉していない**。

---

## 10. 全体構築進捗
- 骨格構築: ~90%（既存AssetEmpire）
- 正式機関化（登録・憲章・組織図・ステータス）: **Stage 1+2 完了（監査合格）**
- 統治・表示・監査基盤（状態モデル・中央司令画面・責任境界）: **Stage 3+4 完了（本更新）**
- 本活性化（台帳/アロケータ実運用）＋実弾利益源選定: **Stage 5 以降（会長GO待ち）**

---

## 改定
- v1（2026-07-30）: 初版。Stage 1+2 で制定。
- v1.1（2026-07-30）: Stage 3+4 反映。institution_state.json との役割分担明記／組織図の実弾表記を実弾ゼロへ是正／次の最優先を Stage 5 実弾利益源選定へ更新／進捗に Stage 3+4 完了を追記。
