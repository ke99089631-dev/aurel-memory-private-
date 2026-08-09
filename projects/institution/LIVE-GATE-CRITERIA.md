# Aurelian 実弾検討ゲート（Live-Consideration Criteria） v1（草案・会長ratify待ち）

制定: 2026-08-09。会長「君に推進でいこう」＝AUREL主導の育成フェーズ開始に伴い、
**冷静なうちに「実弾を検討してよい条件」を先に固定**する（欲・焦りへの予防線）。

## 大原則
- これは **Live化の条件ではなく「Live化を“検討してよい”土俵に上がる条件」**。全部満たしても自動Live化は無い。
- **最終GOは常に会長の二重ロック**（`enable_live=True` かつ `arm_code='CHAIRMAN-GO'`）。AURELは絶対に鍵を回さない。
- **survival が growth に常に優先**。利益はKPIにしない（Project50/100は別軸・非従属）。約束された利益は存在しない。

## 土俵に上がる7条件（全て AND）
数値は AUREL 提案・**会長が編集可**。

1. **実績の長さ**: 実データ紙運用で連続 **≥120営業日** のトラック。かつ主要仮説の `data_insufficient` が解けている（サンプル ≥ MIN_SAMPLES）。
2. **血の質**: Live対象は **real=True の兵士に限定**。proxy(vol_sell/tail_hedge)・partial(carry)・休眠(event_driven) は対象外、または real へ格上げ済み。
3. **ガントレット通過**: **実データ（サンプル十分）で PROMOTE_CANDIDATE を通過**した候補が ≥1件、かつ会長が proposals 二重ロックで正式採用済み（＝紙で adoption>0 の実績）。
4. **生存の実証**: 実運用期間中に survival gate / 床(deadman -8/-12/-15%) / kill-switch / quarantine が**実際に機能した記録**。紙 max_dd が床を割っていない。
5. **規模の微小性**: 初回は「全損しても痛くない」極小サイズ。**出金権限なしキー**・キルスイッチ常設・deadman 常設。
6. **境界不可侵**: 出金なし／レバ上げない／プロップ(g4_)非接触／G2聖域不可侵／凍結資産・維持機MM0・審査機G0 非接触／US100 FINAL・凍結backtester 非改変。
7. **会長の二重ロック**: 上記1–6を会長が自分の目で確認し、`enable_live=True`＋`arm_code` を回す。

## レビュー・リズム（AUREL推進・会長は月次のみ）
- 毎日07:00: 自律サイクル（8兵士→frontier→discovery→evidence→validation→scorecard→loop1）。会長関与不要。
- 週次: AUREL が scorecard/台帳の増減・survival指標を観測（自律・必要時のみ司令室へ声上げ）。
- 月次(15分): 会長レビュー＝実績の傾き・血の質の進捗・上記7条件の充足度・建設の要否。

## 現在地（2026-08-09 時点・未充足）
- 条件1: ✗ 実績まだ短い・多くが data_insufficient。
- 条件2: 一部○（real 4兵士）だが proxy/partial/休眠 が残る。
- 条件3: ✗ 実データ通過ゼロ（昇格1件=H-0007も証拠不足の仮免）。adoption=0。
- 条件4: 進行中（紙 max_dd 0.037・床未接触・quarantine 稼働中）。
- 結論: **まだ土俵の外。今の議題は「待つ・貯める・触りすぎない」。**

## 変更履歴
- v1 2026-08-09 草案（AUREL起案）。会長ratify後に「確定」へ。数値は会長編集で上書き可。
