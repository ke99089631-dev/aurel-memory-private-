# DATA_MAP — この環境で実際に触れるデータの地図（v1・2026-11-05 研究レーン cycle3）

> 補遺B2の最重要成果物。研究レーンが育てる。各領域に【実験可 / 読むだけ / 要取得 / 未調査】を付す。
> 「関連しそう」でなく「予測に使えるか実験できるか」で分類する。v1 はファイル棚卸し（scripts/c3_inventory.py・MT5 未接続）。

## 1. 金 XAUUSD 価格（1次データ）
- 金 M5 OHLC 2010-01〜2026-06: 【実験可】AssetEmpire `empire/research/wall_to_wall/m5_loader.py`。tick 無し・板無し。全読込 ≈19 s。**多年 scan は 1138 s** → 1 サイクル内禁止（キャッシュを使う）。短期間（数週）の scan は推定 10〜20 s で可。
- 直近 5000 本（2026-10-08〜11-03）: 【実験可】data/refute_api_bars_probe.json（serve_chart /api/data の読取り保存）。
- 現値/板: 【読むだけ】MT5 tick は現値のみ。オーダーフロー・板・建玉: **無い**（読むだけ・検証不能）。

## 2. 我々の実験の素（scan キャッシュ・AUREL_RESEARCH/data）
- `refute_c4_scan_paths_2010_2026.json`: 【実験可】再加速 closed **19404 本**（2010-01〜2026-06）。entry_time/year/jh/wall_kind/side/risk/b/R/exit/hold/x0/open_gap/mfe0・mae0・mfe1・mae1/mae_bar0・mfe_bar0/atr。
- `c1_reaccel_paths_2010_2026.json`: 【実験可】同 19404 本の bar 別 mfe/mae/cl 配列（**48 本で切断**）。
- `refute_c2_fullpaths.npz`: 【実験可】同 19404 本の決着までの全足 hiR/loR/clR（870650 足・切断なし）＋ off 索引。建値/トレール/時間切れ系の再シミュに最適（数秒）。
- 注意（反証レーンの確定事項）: scan 全体 θ≈0・gross 平均R −0.055。SL/TP は FEED_TOL 分不利に記帳され終値クローズは記帳されない → SL/TP 以外の出口は s≥0.10 USD を課すか R*=R+ft で公正化（findings 11-04 20:25／23:30）。

## 3. 台帳（前向き紙・本番エンジンの出力）— live フォルダ直下・読むだけ
- `setup_ledger.jsonl`: 【実験可】7852 行（setup 444＋update 7408）。**最終状態は update 行（target=id）を setup 行に上書きして復元する**（setup 行の nested dict は作成時スナップショット）。再加速 closed **305 本**（2026-09-15〜11-04、TP150/SL154/TIME1、全時間帯・jh7-12 は 90 本）。各本に mfe_R/mae_R/hold_bars/exit_reason/entry/sl/tp/entry_time。chase closed 86。setup 行に spread_pt/slip_pt/slip_src/sl_slip_pt/tp_fill_ok（**R が slip 込みか未確認**・要 setup_engine 読取り）。
- `setup_ledger_15m.jsonl`: 【実験可・小】178 行、closed 37。
- `demo_exec_ledger.jsonl`: 【読むだけ・n 小】23 行（live 約定 11・observe 11・close 1）。実デモの fill_price/retcode あり＝将来の滑り実測の種。
- `paper_ledger.jsonl` 23／`paper_ledger_v3.jsonl` 71（旧版・features 付き）: 【読むだけ】定義が現行と違う。
- `pinbar_ledger.jsonl`（pin 2・closed 1）／`tf_ledger.jsonl` 4／`touch2sb_ledger.jsonl` 9: 【読むだけ・n≤9】実験不能。
- `setup_ledger.bak_*`: 旧スナップショット（重複・使わない）。
- fert_reaccel_stop_ledger.jsonl: live 直下に**存在しない**（CHARTER 記載と不一致・所在未確認）。

## 4. 執行コスト
- `spread_log.jsonl`: 【実験可・新規】**94496 行** ts/jst_hour/spread_pt/bid（M5 相当の連続記録）。`spread_log_15m.jsonl` 4993 行。→ スプレッドの時間帯・曜日・ボラ依存、net R の時間構造、「スプレッド÷平均R」が検証できる。期間・欠測は未集計（次サイクル）。
- 滑り: 【要取得→demo_exec_ledger が種】実約定 11 本では統計不能。紙の仮定 0.56 USD/risk（≈0.08〜0.12R/本）を使う。

## 5. MT5 読取（27972608 Live／他端末デモ）
- 【未調査】読める銘柄一覧・履歴可否・粒度。XAUUSD+ の現値/M5 は読めている実績。**接続は read-only・最小限**（symbols_get / copy_rates のみ、発注関数は呼ばない）。次サイクル以降に 1 回だけ probe し本節を埋める。
- AssetEmpire `empire/strategies/trackA_us100_sleeve.py` に copy_rates 利用あり → US100 系の履歴は読める可能性（未確認）。

## 6. 公開マクロ／他資産（ドル指数・米金利・VIX・他商品）
- 【要取得・未調査】Web で取れるか、粒度（日次か）・遅延・再現性。金 M5 と結合するには日次でも「前日値で条件づけ」なら look-ahead なしに使える。優先度: 中（DIRECTIVE タスク3）。取得元候補は次サイクルで調査し、取れたら CSV を AUREL_RESEARCH/data に保存して【実験可】へ。

## 7. 無いもの（読むだけ・検証不能と明記）
- オプション建玉時系列・板・オーダーフロー・クロスアセット tick・COT の高頻度版。該当する仮説は文献調査で終え「データX が必要」と記録する。

## 原則
- 「要取得」は、取得元・コスト・優先度・何の仮説を解くかをセットで記す。
- データが無い領域は正直に「読むだけ（検証不能）」と印をつけ、無理に実験した体を作らない。
- 1 サイクル内で多年 scan・全足 path 再構築を新規に走らせない（既存キャッシュ §2 を使う）。
