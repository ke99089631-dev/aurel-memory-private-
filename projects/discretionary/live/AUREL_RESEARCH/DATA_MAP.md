# DATA_MAP — この環境で実際に触れるデータの地図（v1.3・2026-11-05 研究レーン cycle3 棚卸し／cycle4 §3-4 執行コスト実測／cycle5 §6 公開マクロ日次を【実験可】へ／cycle6 §2 期間集計の密度）

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
- 期間集計の密度（cycle6 11-05・時系列/レジーム検定の設計用）: 週あたり本数 中央値 在 2010-20 **20**（p10 12・p90 30・572 週）／外 2021-26H1 **27**（287 週）／近年 2024-26H1 **30**（131 週）。月あたり 85／116／134 本。週平均R の標本 SE ≈0.23R・月 ≈0.11R → 週次で r≈0.12（80% 検出力）、月次で在 ≈0.24 が検出限界。本数の lag1 自己相関 +0.42〜+0.71（ボラ・クラスタリング）、平均R の lag1 ≈0（c6_persistence_result.md）。
- 注意（反証レーンの確定事項）: scan 全体 θ≈0・gross 平均R −0.055。SL/TP は FEED_TOL 分不利に記帳され終値クローズは記帳されない → SL/TP 以外の出口は s≥0.10 USD を課すか R*=R+ft で公正化（findings 11-04 20:25／23:30）。

## 3. 台帳（前向き紙・本番エンジンの出力）— live フォルダ直下・読むだけ
- `setup_ledger.jsonl`: 【実験可】7852 行（setup 444＋update 7408）。**最終状態は update 行（target=id）を setup 行に上書きして復元する**（setup 行の nested dict は作成時スナップショット）。再加速 closed **305 本**（2026-09-15〜11-04、TP150/SL154/TIME1、全時間帯・jh7-12 は 90 本）。各本に mfe_R/mae_R/hold_bars/exit_reason/entry/sl/tp/entry_time。chase closed 86。setup 行に spread_pt（建玉時 tick 実測）／update 行で slip_pt/slip_src/sl_slip_pt/tp_fill_ok（slippage_sim の注釈）。**R は gross**（setup_engine._simulate: R=pnl/risk・控除なし／cycle4 11-05 で確認）。
- `setup_ledger_15m.jsonl`: 【実験可・小】178 行、closed 37。
- `demo_exec_ledger.jsonl`: 【読むだけ・n 小】23 行（live 約定 11・observe 11・close 1）。実デモの fill_price/retcode あり＝将来の滑り実測の種。
- `paper_ledger.jsonl` 23／`paper_ledger_v3.jsonl` 71（旧版・features 付き）: 【読むだけ】定義が現行と違う。
- `pinbar_ledger.jsonl`（pin 2・closed 1）／`tf_ledger.jsonl` 4／`touch2sb_ledger.jsonl` 9: 【読むだけ・n≤9】実験不能。
- `setup_ledger.bak_*`: 旧スナップショット（重複・使わない）。
- fert_reaccel_stop_ledger.jsonl: live 直下に**存在しない**（CHARTER 記載と不一致・所在未確認）。

## 4. 執行コスト
- `spread_log.jsonl`: 【実験可・済 cycle4 11-05】**94621 行**、2026-09-25 08:47〜11-05 12:46 JST（42 日）、サンプル間隔 中央値 16 s（p90 120 s）、>10 分欠測 2 回。**実口座 27972608 の tick**（serve_chart /api 経由・setup_engine._log_spread）。値は USD。結果: 開場中は **固定 0.15/0.16 の 2 値（99.15%）**・時間帯/曜日/ボラ構造なし・max 0.23。0.21/0.22 は閉場（週末・JST5-7 の日次メンテ）中の配信値で stale 行は 100% 広い。→ 「スプレッドの時間構造」は**この口座では検証済み・無い**。他口座（デモ）は別物（10-23 実測 0.42）＝【要取得】。`spread_log_15m.jsonl` 5053 行（同源・未分析）。
- 滑り: 【実験可・小】台帳 263 本に slippage_sim（MT5 tick 履歴・成行 L=1 s）の注釈 slip_pt／sl_slip_pt（158）／tp_fill_ok（103）。entry slip 中央値 +0.02 USD（p90 +0.33・両側対称）、SL slip 中央値 +0.026（max 0.65）、紙 TP の 3.9% が実約定不成立。spread＋slip の実コスト 中央値 0.21 USD＝0.03R/本。**台帳 R は gross（_simulate は pnl/risk のみ・控除なし）**。注釈の無い 42 本は高 R に偏る（欠落は無作為でない）。demo_exec_ledger の実約定 11 本は別途【読むだけ・n 小】。手数料（commission）の記録は**無い**＝【要取得】。

## 5. MT5 読取（27972608 Live／他端末デモ）
- 【未調査】読める銘柄一覧・履歴可否・粒度。XAUUSD+ の現値/M5 は読めている実績。**接続は read-only・最小限**（symbols_get / copy_rates のみ、発注関数は呼ばない）。次サイクル以降に 1 回だけ probe し本節を埋める。
- AssetEmpire `empire/strategies/trackA_us100_sleeve.py` に copy_rates 利用あり → US100 系の履歴は読める可能性（未確認）。

## 6. 公開マクロ／他資産（ドル指数・米金利・VIX・他商品）
- 日次（FRED）: 【実験可・済 cycle5 11-05】`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>` は API キー不要・1 系列 0.1〜0.4 s。保存先 `data/macro/<ID>.csv`（date,value・欠損は "."）。取得済: **DFII10**（10y 実質・2003〜）／**DGS10**（10y 名目・1962〜）／**DTWEXBGS**（広義ドル・2006〜・**Fed H.10 の公表遅延 ≈4 営業日**＝当日観測不能・DXY の代理）／**VIXCLS**（1990〜）。最終行 2026-11-03（DTWEXBGS は 10-30）。
  - 結合規則（5条・確定）: FRED 日付 D の値は NY 17:00 ET 確定 → **JST D+1 07:00 以降の建玉のみ**（avail_date=(entry_JST−7h).date()−1 日・merge_asof backward・staleness ≤7 日）。scan 19404 本に 100% 付与、staleness 中央値 0 日。コード: scripts/c5_macro_condition.py。
  - 結果: 前日 |Δ| 上位20%／前日の向き×side の 8 セルは 在/外/近年 で条件づけなし（family-wise p 0.73）。日次粒度の限界。
  - 未取得候補（必要時）: DCOILWTICO 原油／DEXJPUS／T10YIE 期待インフレ／DFF。
- イントラデイ（DXY・US10Y/TNX・US 株指数の M5〜H1）: 【要取得】金の実質金利・ドル感応は同時刻の共変動なので、レジーム条件づけの本命はこちら。取得元候補 = MT5（§5 probe で copy_rates 可否を確認）。解く仮説: 「建玉時点の同日ドル/金利の動きが壁→壁の成績を条件づけるか」。優先度: 中〜高（§5 probe と同時に）。

## 7. 無いもの（読むだけ・検証不能と明記）
- オプション建玉時系列・板・オーダーフロー・クロスアセット tick・COT の高頻度版。該当する仮説は文献調査で終え「データX が必要」と記録する。

## 原則
- 「要取得」は、取得元・コスト・優先度・何の仮説を解くかをセットで記す。
- データが無い領域は正直に「読むだけ（検証不能）」と印をつけ、無理に実験した体を作らない。
- 1 サイクル内で多年 scan・全足 path 再構築を新規に走らせない（既存キャッシュ §2 を使う）。
