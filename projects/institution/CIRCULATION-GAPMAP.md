---
doc_id: AURELIAN-CIRCULATION-GAPMAP-v1
tags: [institution, circulation, gap-analysis, loop-level, build-step0]
type: circulation-gap-map
rank: STEP0 成果（循環の断裂地図・構築の起点）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: CIRCULATION-ARCHITECTURE.md（最上位設計思想）
principle: 完成度は「箱があるか」でなく「帰還ループ⑤が閉じて回っているか」で測る
---

# 循環の断裂地図（Circulation Gap Map）— STEP 0

> **測り方の転換**: これまでは「箱（部署）があるか」で完成度を測った。本書は「**循環が一周して戻り、次の判断を変えているか**」で測る。
> **記号**: ●=閉じて回っている / ◐=片方向は流れるが帰還が無い/手動 / ○=流れていない（断裂）。
> **原則**: 帰還(⑤)が無いループは「静止画」。ここを閉じることが構築の本体。

---

## 9循環の現状（帰還ループが閉じているか）

| # | 循環 | 経路 | 現状 | 断裂点（⑤が無い/手動の箇所） |
|---|---|---|---|---|
| ① | 情報 | 世界→Research→Executive→Business→結果→Audit→Research | **●（本番自律・最小）** | 【2026-07-30】worldmodel.py＋run_info.py で①を閉じた。観測所(observatory.regime)がマクロCSV(SPY/VIX/GLD/DXY/TLT/BTC・読取専用)から今日の地合いを決定的分類＝世界理解→本物のpaper帳簿で機関の直近体調→(地合い×自分の成績)を専用Ledgerへ記録＝自前の実証地図が育つ→荒れ地合い(高ボラ/リスクオフ)＋出血中なら選別フロアを上げる守り。実データ検証：今日raw=crisis/確定=range・vol+0.36・本の直近pnl -0.066/勝率0.31→stance=defensive→判断 long→flat 反転・連鎖OK。本番反映は単一書き手write_backに世界フロアを免疫フロアとmaxで統合(ETHUSD 0.005→0.009 commit)。ただし“明確に勝つ”銘柄は免除＝危機に強い金XAUUSDを一律引き上げで手枷にしない。日次カデンツで自動。【更新⑦】手書きの金免除を、地合い別の銘柄親和性**学習**へ置換（worldmodel.symbol_affinity）＝自前記録の(地合い×銘柄)から「危機で金は強い」等を経験から判定し免除は加法的(clearly_healthy or learned_favorable)。記録が閾値未満なら unknown＝既存規則に委譲で今日の挙動は不変。残：全部門共有の能動読取 |
| ② | 利益 | 利益→Capital→再配分→Business→利益→留保→研究投資 | **●（paper自律・金ゼロ）** | 【2026-07-30】capital.py＋run_capital.py で②をpaper/助言で閉じた。本物paper帳簿の実現損益(生涯sum_pnl・読取専用)→単一化したpaper資本口座で各兵の取り分を増減(equity=1+損益)→equity比例で資本ウェイトを再配分(下限0.05/上限0.40で暴走・餓死を防ぐ・monotone)→⑤免疫の隔離兵は最小ウェイトへ(資本が免疫に従う)。実データ検証：勝ち頭XAUUSD@0.339・隔離BTC/GBPは0.047へ縮小・等分0.2から資本が0.31動いた・同帳簿で冪等・台帳連鎖OK。日次カデンツ(auto_writeback step5c)で自動更新＋共有神経へbroadcast＋digestに②表示。**助言＋paper台帳のみ＝本番evolved_configsも実弾も非接触**。実弾(本物の資金移動)は最後・会長二重ロックGO後。残：利益の留保→研究投資への分岐 |
| ③ | 資本 | 資本→Allocator→各事業→運用→利益→資本増加→再配分 | ○ | 資本台帳が単一化されていない。複数枠の資本が一箇所に集約→再配分される血流が無い |
| ④ | 知識 | 成功→Research→Knowledge Ledger→全部門共有→次世代戦略 | **●（本番自律）** | 【2026-07-30】機構→実データ読取→本番書き戻し→**日次自動カデンツ**まで到達。自分のpaper戦績→本番evolved_configs.jsonへ毎朝07:00自動帰還（AUREL_Circulation_WriteBack）。専用Ledger連鎖OK。残：全部門共有（他Groupが読む）は次増分 |
| ⑤ | 失敗 | 事故→Risk→Audit→分析→知識化→Research→改善→Technology→Business | **●（本番自律・自己治癒付）** | 【2026-07-30 v2】immune.py を強化。①急性検知＋自己治癒：判定を寿命累計→直近K=10取引へ＝“今の体調”で診る。回復すれば隔離が自動で解ける。隠れ出血のBTCUSD(寿命では健全に見えるが直近-0.096)を新規隔離＝隔離5件へ。②口座レベル応答：歴史的25%DDは抗体(記憶)に留め、発火は現在状態(def_level/def_dd_trailing)で判断。現在は回復済のため account_defense は正しく非発火(過剰防御しない)。発火時フロア0.008を全ソルジャーへ課す配線を write_back に統合(単調・引上げのみ)。BTCUSD 0.01→0.02 を本番commit(GBPUSD 0.02維持)。日次カデンツで④慢性＋⑤急性を自動同時適用。残：検死の因果分析深化・全部門共有 |
| ⑥ | AI | Research AI→Strategy AI→Risk AI→Execution AI→Audit AI→AUREL→Chairman→Research AI | ◐ | Arsenal/Council/Hermes/ai_soldier/Gemini は個別に在るが、AI同士が結果を渡し合い学習し合う環が繋がっていない。councilはオンデマンド |
| ⑦ | 技術 | 問題→Technology→改善→実装→Business→結果→Technology | ◐ | health-monitor/自動起動など運用の自動修復は●。だが「Businessの問題→自動で改善要求→実装→結果検証」の開発ループは手動 |
| ⑧ | 人材(AI社員) | 新AI→教育→評価→専門化→昇格→統括AI→後進育成 | ○ | AI社員の名簿・権限・評価・昇格の定義が無い。エージェントは在るが組織化・育成の環が未 |
| ⑨ | 自己進化 | 経験→知識→改善→再設計→実行→新経験→さらに知識 | **●（本番自律・単軸）** | 【2026-07-30】④と同じ配管で本番paperを日次自律運転（結果→設定→次の行動が毎日変わる・冪等収束）。まだ単一ノブ(momentum_confirm_min)・単軸だが、生命体として毎日1拍を自律で打ち続ける状態に到達。総合化（多軸・全Group連動）は今後 |

> **要約**: **●（閉じて回っている循環）は 5つに到達**＝①情報・②利益(paper)・④知識・⑤失敗（免疫）・⑨自己進化（2026-07-30、本番paperで日次自律・GO/AUREL推進済）。運用自動修復の⑦技術も部分●。G5/G1帰還は助言レベルで流れ始めた(能動読取)。⑥AIは「片方向は流れるが戻りが無い/手動」。③資本・⑧人材は流れていない。**「箱の完成度」でなく「●になった循環の数」で測る＝現在 5/9 が自律で呼吸（①②④⑤⑨は同じ日次カデンツで拍動）。**
>
> **【2026-07-30 更新⑨】②利益循環をpaperで閉じた＝●が5/9へ（AUREL推進・検証PASS）**: 地図でずっと○だった②を、実弾を使わず paper/助言で一周させた。血流の実体＝各兵が稼いだ/溶かしたpaper利益が、その銘柄の“資本の取り分”を変える。capital.py＋run_capital.py：本物paper帳簿の生涯実現損益(読取専用)→単一化paper資本口座(equity=1+損益)→equity比例で資本ウェイト再配分(下限0.05/上限0.40・monotone)→⑤免疫の隔離兵は最小へ(資本が免疫に従う)。検証(run_capital PASS)：XAUUSD@0.339(勝ち頭)・BTC/GBP@0.047(隔離で縮小)・等分0.2から資本0.31移動・冪等(同帳簿→同ウェイト)・台帳連鎖OK。auto_writeback step5cで日次自動＋共有神経へbroadcast＋digestに②表示(closed_loops=5)。**助言＋paper資本台帳のみ＝本番evolved_configsも実弾も一切非接触**（実弾は最後・会長二重ロックGO後）。＝生命体の血の再配分が金ゼロで回り始めた。残：利益の留保→研究投資分岐・③資本台帳の統合。
>
> **【2026-07-30 更新⑧】全部門共有を閉じた＝他Groupの“能動読取”（AUREL推進・検証PASS）**: 公開(更新⑥)は片方向だった＝血は流れたが、他の臓器が自分から取りに来て反応するまで共有は閉じない。その最後の一歩を実装。`subscribe.py`＋`run_subscribe.py` を新設。(1)`broadcast()`＝循環の心拍(digest)を**既存の共有神経 SignalBus** へ1メッセージとして流す（ファイルだけでなく本物の神経幹線に乗る）。(2)他Group購読者が**各自のカーソルで**新しい心拍だけを pull し自分の観点で反応：**G5 Risk/Audit**＝地合い×隔離×口座防御→警戒度(calm/elevated/high)、**G1 Executive**＝閉ループ数×構え×本の体調→資本姿勢(expand/hold/defend)。(3)反応は **助言(advisory)のみ**＝本番 evolved_configs は一切書かない（単一書き手 write_back を侵さない）。実データ検証(run_subscribe PASS)：心拍を流す→G5=high(隔離5＋守り)・G1=defend(守り＋本が出血)＝各自が姿勢を変える→同じ心拍の再消化は n_new=0/無反応＝**冪等**（重複助言なし）・専用台帳連鎖OK。`auto_writeback` に step5b(broadcast＋consume_all)を追加＝毎朝カデンツ後、心拍を共有神経へ流し他Groupが自動で読み姿勢更新。paperのみ・金ゼロ・専用バス/台帳・live/プロップ/維持機/審査機非接触・既存資産無改変。＝**地図の共通の「残」だった全部門共有が閉じた**（公開→能動読取→他Groupの姿勢変化まで一周）。
>
> **【2026-07-30 更新⑦】①の借金返済＝地合い別の銘柄親和性“学習”（AUREL推進・検証PASS）**: 「危機に強い金XAUUSDを守りの一律引き上げから外す」免除を、これまで手書き(clearly_healthy)で持っていた。この技術的負債を **自前記録から学ぶ親和性** へ置換。`worldmodel.py` に regime_symbol_memory()（過去 world_update の(地合い×銘柄)集計）＋ symbol_affinity()（この地合いでこの銘柄は実証的に有利か favorable/unfavorable/unknown）を追加。記録様式は `record_belief()` へ一本化し **銘柄別 symbols フィールド** を毎日追記＝地合い×銘柄の実証が貯まる。`write_back` の免除を **加法的**(exempt = clearly_healthy **or** learned_favorable)に改修＝単調安全・退行なし。合成多日検証(`test_affinity.py`)：危機5日で金→favorable(+0.05/日)・BTC→unfavorable(-0.04/日)・記録n<5は unknown・別地合い range も unknown・専用DB連鎖OK。**正直に**：本番記録はまだ n=1〜2/地合い（paper帳簿に取引日付が無く遡及不可）＝学習は今日から前向きに貯まる。ゆえに **今日の書き戻しは意図的に不変**（DRY再確認：symbols_changed=0・金は clearly_healthy で免除・ETHは床0.009維持）。日次カデンツ `auto_writeback` に**同日ガード付き記録**を追加＝毎朝1回、地合い×成績を世界モデルへ追記し親和性が育つ。残：全部門共有の能動読取。
>
> **【2026-07-30 更新⑥】全部門共有の第一歩＝循環ダイジェスト公開（AUREL推進・検証PASS）**: 4本の●(①④⑤⑨)の判断が専用台帳とevolved_configsに埋もれ他Group・会長から読めない「全ループ共通の残」を解消。`digest.py`＋`run_digest.py` で生きた読取専用ソース(worldmodel/immune/evolved_configs/Ledger検証)から現在状態を束ね、単一共有ファイル `data/circulation/circulation_digest.json` へ公開(単一書き手=digest)。目玉＝**『どのソルジャーを誰が決めたか』表**(BTC/GBP←⑤免疫・ETH←①情報・EUR←④知識・XAU←base)。`auto_writeback` に digest.publish() を追加＝毎朝カデンツ後に共有面が自動更新。会長command画面 `aurelian_command.html` に「循環-呼吸している帰還ループ」カードを**追加描画**(institution_state.json の新規 circulation ブロックを読む・既存カード無改変)。＝閉じたループが初めて組織全体(会長含む)へ届いた。残：他Group側の**能動読取(自動購読)**。
>
> **【2026-07-30 更新⑤】①情報ループを閉じた（AUREL推進・検証PASS）**: 当初「①はpaper cycleが世界モデルを読んでいない＝砂上」と判明（run_trading_cycleにregime参照ゼロ・observatoryはg4/プロップ側のみ＝触れない）。そこで **circulation内に世界モデル信念記録を新設**（`worldmodel.py`＋`run_info.py`）。観測所でマクロCSVから今日の地合いを決定的分類（世界理解）→本物paper帳簿で機関の直近体調→(地合い×成績)を専用Ledgerへ記録し**自前の実証地図が育つ**→荒れ地合い＋出血で選別フロアを上げる守り。今日 raw=crisis/vol+0.36・本の直近pnl-0.066→stance=defensive→判断 long→flat 反転（day1で●）。本番は単一書き手write_backに世界フロアを免疫フロアと**max**で統合（最も守りを採る）・ETHUSD 0.005→0.009 commit・**明確に勝つ金XAUUSDは免除**（危機に強い銘柄を手枷にしない）・台帳seq3鎖OK・--restore復元可。①④⑤⑨が同一日次カデンツで拍動。残：地合い別の銘柄親和性の学習・全部門共有。
> → **箱で見た完成度（G6:75%等）は“静止画としての完成度”。循環で見ると、まだ一周も自動で回っていない。** これが本当の現在地。
>
> **【2026-07-30 更新①】最初の心拍（機構）**: ④知識/⑨自己進化の**最小形を実装し、隔離環境で1周を閉じることを実証**（`empire/circulation/loop1.py`・`run_loop1.py`）。paper結果→学習(閾値1.0→1.2)→次の判断が long→flat に反転→`loop_closed` を専用Ledgerに記録・ハッシュ連鎖検証OK。
>
> **【2026-07-30 更新②】実データ接続（読取専用）**: `run_ingest.py`＋`result_source.py` を追加し、**機関の本物のpaper帳簿**(paper_book.json/paper_book_4h.json)を【読むだけ】で読み、実測勝率で循環を一周。結果=19銘柄ingested・17銘柄が学習で変異（勝率0.5以上のETH/XAUは正しくhold）・専用Ledger連鎖検証OK。**本番 evolved_configs.json は無改変（circulation内のシャドウ設定で学習）／live・プロップ非接触**。behavior_changed=0＝負け銘柄は既にflatで判断反転が観測されなかった（プローブ設計上の理由・正直に記載）。
>
> **【2026-07-30 更新③】本番へ物理的に閉じた（会長GO済・検証PASS）**: `write_back.py` を追加し、機関自身のpaper戦績(paper_book.json・読取専用)の学習を、本番が読む `data/evolved_configs.json` の単調安全ノブ `momentum_confirm_min` へ反映。負けている3銘柄のみ選別を厳格化(0.005→0.007)、勝ち・中立は据え置き。**次の実trading cycleがこの値を実際に読む＝『自分の結果→学習→次の行動が変わる』帰還が本番で1周閉じた**。安全=既定DRY/`--commit`必須/変化上限+0.002/範囲[0.001,0.02]/バックアップ＋1コマンド復元(`--restore`)/専用Ledger記録(連鎖OK)/live・プロップ・維持機・審査機非接触・金ゼロ。
>
> **重要発見（正直に）**: 既存 `evolution_cycle.py`（週次稼働中）は**2年バックテストCSVを再最適化するだけ**で、6週連続「採用変更0件＝静止画」。**自分のpaper戦績を一度も見ていなかった**。本地図が言う「帰還が無い」の実体はこれ。今回、初めて「**自分の結果→本番設定**」の帰還を通した。
>
> **【2026-07-30 更新④】カデンツ自動化＝運用●（会長GO済・検証PASS）**: `auto_writeback.py`＋`run_circulation_writeback.bat`＋Windowsタスク `AUREL_Circulation_WriteBack`（毎日07:00 JST・日次paperサイクル06:30直後・Ready）で**無人運転化**。毎朝、機関自身のpaper戦績→本番設定へ自動帰還＝**ループが毎日1周、自律で閉じる**。
> - **冪等化**: `write_back` を加算式→**目標収束式**（目標=BASE-GAIN*(win-0.5)・1回最大STEP・中立帯据置）に改修。純関数で収束証明＝win0.25→0.010で停止(天井0.02へ暴走せず)／win0.5不動／win0.75→0.001で停止。**同じ戦績を毎日読んでも累積punishしない**。
> - **無人安全弁**: キルスイッチ（`data/circulation/DISABLE_AUTOWRITE` を置けば即停止・検証済）＋クールダウン20h（検証済）＋毎回バックアップ＋台帳＋`--restore`復元。初回ライブ実行で losers 0.007→0.009・台帳seq39鎖OK・独立確認済。paperのみ・金ゼロ・live/プロップ/維持機/審査機非接触。
>
> **現況の正直な位置づけ**: **“機構●・実データ読取●・本番書き戻し●・運用（連続自動）●”**＝**④知識/⑨自己進化ループが本番paperで自律的に回り続ける状態に到達（初の●循環）**。残：全部門共有（他Groupがこの帰還を読む）／`evolution_cycle.py`自体をpaper戦績連動へ／実弾はT10で別GO。

---

## 7 Group 5点契約 × 現状の帰還可否

各Groupを「受・判・産・渡・帰」で見て、⑤帰還が実装/自動化されているか。

| Group | ①受 | ②判 | ③産 | ④渡 | ⑤帰還 | 帰還の現状 |
|---|---|---|---|---|---|---|
| G1 Executive | 全部門 | 方針決定 | 命令 | 全部門 | **一部●(助言)** | 【更新⑧】循環の心拍を共有神経から能動読取し資本姿勢(expand/hold/defend)を自動更新＝助言レベルの帰還が流れ始めた。命令への昇格は今後 |
| G2 Core | 全状態/イベント | （運ぶ） | 配信/保存 | 各部門 | **要** | Ledger保存は●。だが全部門が同一背骨に読み書きする統一が未（state分散） |
| G3 Business | 仮説/戦略/資本 | 参加/資本量 | 利益/損失/経験/データ | Capital/Risk/Audit/Research | **一部●(paper)** | 【更新⑨】利益→Capital→再配分の血流をpaperで自動化(capital.py)＝paper利益が資本ウェイトを毎日動かす。経験→Researchの自動帰還は今後。実弾は最後 |
| G4 Research | 世界+全結果 | 仮説/新戦略 | 提案/戦略/期待値 | Exec/Business/Capital/Risk/Tech | **要** | 結果を読んで学習し戻す環が未。昇格パイプライン未確立 |
| G5 Risk/Audit | 全口座/注文/ログ | 危険/停止判断 | 監査/事故分析/改善要求 | Exec/Research/Tech/Capital/Business | **一部●(助言)** | 【更新⑧】循環の心拍を能動読取し警戒度(calm/elevated/high)を自動更新＝助言レベルの帰還。⑤免疫の自動隔離は既に●。自動違反検知の全面化は今後 |
| G6 Technology | 改善要求/障害 | 実装/修正/復旧 | システム/監視/自動化 | 全部門 | **一部●** | 運用の自動復旧は閉じている。開発改善ループは手動 |
| G7 Chairman Nav | 全機関状態 | 長期構想/最終判断 | 最終命令 | Executive | **要** | 中央司令画面は写しフォールバック。状態が会長へ“ライブで”届く帰還が未 |

---

## 構築の焦点（どのループから閉じるか）

循環で見た現在地から、**閉じる順序**を導く：

1. **G2 Coreを単一背骨にする**（②③④⑤⑥全部がここを通る）＝血管敷設。すべての循環の前提。
2. **④知識ループ＋①情報ループを最初に閉じる**＝paper・金ゼロ・既存research/evolution資産で組める最小の“呼吸”。Business(paper結果)→Ledger/Knowledge→Research→改善→Business。
3. **⑤失敗ループを閉じる**＝免疫。事故→自動分析→知識化→改善。ETH衝突検知の実績を自動化の型にする。
4. 以降 ⑥AI・⑧人材・②③資本 を順に閉じ、最後に⑨自己進化が総合ループとして実体化。

> **実弾（②利益・③資本の実データ活性化）は最後。** それまでは全ループをpaper/dryで閉じ、生命体として一周させることが目標。

---

## この地図の使い方（今後の判断基準）
- 新しい設計・追加は、必ず「**どのループのどの帰還(⑤)を閉じるためか**」を宣言してから着手する。
- 完成度レビューは箱の数でなく「●になった循環の数」で報告する。
- プロップは循環対象外（機関側の帰還を張らない）。本地図に含めない。

## 改定
- v1（2026-07-30）: STEP0成果として初版。9循環の断裂地図・7Group帰還可否・閉じる順序を定義。
