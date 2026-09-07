---
tags: [institution, soldier, selection, proposal, awaiting-chairman-go]
type: proposal
status: 起案（会長GO待ち）
created: 2026-09-07
author: AUREL
scope: paper-only / zero-money / adoption-0 / live_gate LOCKED / prop(g4_) untouched
---

# 起案: 兵（trend_follow / mean_reversion）の銘柄選別を手書き→実測へ差し替える

> 会長号令「君の推しで」（2026-09-07）＝選択(a)を受領。以下は**書面の起案**であり、
> 器のコード・お金・鍵は一切動かしていない。**着工には別途この起案への会長GOが要る**。

## 1. なぜ（背景）
- 機関の兵は全員が**二層構造**になっている。損益計算は実バー20年のPoint-in-Time＝本物。
  だが「どの銘柄に賭けるか」の選別だけは**手書きの定数**で決まっていた。
  - `trend_follow.py` L51-56 `TF_INSTRUMENTS` … 各銘柄の `trend_strength`（手書き）を
    `TREND_CONFIRM_MIN=0.65` と比べるだけ（L79-81 `_held_ids`）。
  - `mean_reversion.py` L50 `MR_INSTRUMENTS` … 各銘柄の `typical_z_reach`（手書き）を
    `MR_Z_ENTRY=2.0` と比べるだけ（L93-95 `_held_ids`）。
- これは stat_arb で既に潰した病と**同型**（stat_arb は 9/7「AからBで」で実測へ差し替え済）。
- 9/7 に `soldier_screen.py`（新規・**兵のコードは無改変**・selftest PASS）で
  154銘柄×2戦法＝**328検定**を実測。関門＝期間外(前70/後30)・実測コスト差引・
  多重比較FDR(q=0.10)・時代持続性50%・同一物排除・G0(買えない指数/現金同等物を除外)。

## 2. 測定結果（実測・読取専用・金ゼロ・確定済）
- **採用9器**（全て×5コスト悪化でも基準内）:
  - 戻り取り(mean_reversion): XLK / EURGBP / EWA / QQQ / XLP / EURCHF / EZA / EWU（8）
  - トレンド(trend_follow): BTC（1）
- **トレンド兵は全滅**: 現行5器すべて不採用。154銘柄でトレンドで通ったのは BTC の1本だけ。
- **戻り兵は3/5生存**: EURGBP・EURCHF・NAS100(=QQQ) は実測でも本物。AUDCAD・USDJPY は根拠なし。
  ＝手書きの数字は6割方当たっていたが、当たっていたことを今日まで誰も確かめていなかった。

## 3. 何を変えるか（stat_arb と同一の作法）
両ファイルとも「選別層」だけを差し替える。**損益エンジン・ノブの意味・出力スキーマは不変。**

各兵（trend_follow.py / mean_reversion.py）に対して:
1. `_build_from_screen()` を追加し `data/circulation/soldier_screen.json` を読む。
   採用銘柄と `measured_strength`（=clamp(期間外シャープ,0,1)×勝率）を選別の唯一の根拠にする。
2. 手書き `TF_INSTRUMENTS` / `MR_INSTRUMENTS` は `LEGACY_*` へ退役（検算用の死蔵・選別にも損益にも不使用）。
3. **選別ファイルが無いときは黙って手書きへ戻さず 0器**（fail-closed＝再発防止・stat_arb と同じ）。
4. `_held_ids` は `measured_strength` と既存ノブ（CONFIRM_MIN / Z_ENTRY）を突き合わせる形へ。
   ノブの名前・意味は変えない（会長が読める指標のまま）。
5. selftest は**銘柄名でなく性質**を検査（採用は全部screen由来／手書き混入ゼロ／point-in-time=True）。
6. 損益は既に実バー＝**エンジンのコードは一行も触らない**。
7. バックアップを取ってから着工（stat_arb 同様 `*.bak_YYYYMMDD_measured_selection`）。可逆。

差し替え後の期待held: トレンド=BTC(1)／戻り取り=8器（§2の通り）。
現行の手書きheldは理由つきで自然に入れ替わる。

## 4. 正直な留保（隠さない）
- コストの元は**FXプロップ口座の実測**（片道0.272bps・スパイク×2.75・×5まで検証）。
  **株ETFは実コストがより高い**＝この採用リストは「机上のコスト」で通っている。
- 戻り取りは建玉回数が多く**コスト前提に弱い**（コストが上がると真っ先に効く）。
- BTCトレンドは期間外シャープ0.35＝**強くはない**（生存はするが薄い）。
- G0関門を初回実行後に追加した（VIX/SHV の偽陽性排除）。**候補を減らす方向のみ**＝基準の緩和ではない。

## 5. 安全境界（不変）
- **paper のみ・金ゼロ・adoption 0・live_gate LOCKED・プロップ(g4_)非接触。**
- この起案の着工は**選別層の差し替えのみ**＝ライブ経路・鍵・実弾には一切触れない。
- 鍵は回さない。実弾・購入・二重ロック解錠は会長の手のみ（不変）。

## 6. 段取り（(c)コスト実測差替を捨てずに織り込む）
- **第1段（この起案・会長GO後に着工可）**: 選別層を実測へ差し替え→selftest PASS→
  **翌朝の実循環で held が実測どおりに入れ替わるのを実見**。ここまで全て paper・adoption 0。
- **第2段（別の会長GO・後日）**: ライブを一切考える前に、**株ETFのコストを本番口座で実測差替**し
  採用リストを再算出。＝会長の選択肢(c)を「捨てる」のでなく**ライブ前の必須ゲート**として下流に置く。
  第1段は(c)を待たずに進められる（paper だから）。ライブは(c)通過が絶対条件。

## 7. 完了の定義
「差し替えた」ではなく、**差し替え後の実循環で held が実測どおりに入れ替わるのを実見**したこと。

## 8. 会長への上申
第1段（選別層の差し替え・paper・金ゼロ）への着工GOを求める。GOが出れば、
バックアップ→差し替え→selftest→翌朝実循環の実見、まで自律で回して実見報告する。
GOが出るまで器には一行も触れない。
