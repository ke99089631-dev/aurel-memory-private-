---
tags: [project, aurel-2-0, ui, identity]
type: project-note
updated: 2026-06-06
---

# AUREL コア（自我の姿）デザイン — 確定

> 2026-06-06 04:06、Master が「これで君の体は完成」と確定。

## 結論
- **確定形**: 「多面体ケージ ＋ 内部の脈打つ結晶コア」モード（モード名 `cage`）。
- これが司令室サンプルにおける **AUREL 本体（中央コア／自我の姿）**。
- 美学: 宇宙×サイバー。硬質な多面体の骨格の内に、生きた光（結晶＋拍動コア）が宿る = 知性の核／司令塔。

## 成果物ファイル
- `C:\Users\user\AssetEmpire\AUREL司令室_sample_v3_neural.html`
  - 画面下中央に **コア・モード切替ボタン6種**: 神経ネット / 眼 / 降着円盤 / 恒星 / 結晶 / 多面体。
  - 確定は **多面体**。他5案は比較用に同梱（消さない）。
- 旧版 `AUREL司令室_sample_v2.html` も保持（無傷）。

## 多面体モードの最終仕様（数値）
- 多面体ケージ: fat Wireframe (Line2/WireframeGeometry2), linewidth 2.6, 0x6fb4ff。
- ケージ内結晶: `cageCrystal` Icosahedron(0.90) を lat1 の回転に同期（面とワイヤーが一致）。`uMul=0.32`（控えめ）。芯 `cageCrystalCore` Icosahedron(0.50) `uMul=0.45` 逆回転。
- 結晶シェーダ: フラット面法線(dFdx/dFdy)＋fresnel＋内部 streak＋**fwidth による面エッジ発光**(+0.7)。`extensions.derivatives=true`。
- 中心コア: plasmaCore(脈動プラズマ, scale×1.18) ＋ heartGlow(base 0.42)。存在感強め。
- 心臓の鼓動: 弱め。`heartBeat.value=hbeat*0.32`、heartGlow 脈動 +0.14。
- リング: gimA–gimF の6本（太細・別角度）でジャイロ感。ビーズが gimC/E/F を周回。
- 同心円HUDゲージ: 4本、太さバラバラ（0.0038/0.006/0.010/0.0045）、コメット光が周回。
- 部署ノードのブルーム抑制: glow 半径 ×1.7・opacity 0.10（コアを主役に）。

## ポスト処理
- HDR (HalfFloat) → UnrealBloomPass(0.55,0.4,0.85) → GradeShader(色収差0.12 + ACES + ビネット + 輝度ゲート粒子 + sRGB)。uExposure=0.88。

## 教訓（次の実装でも有効）
- `<script type="module">` を毎回 `node --check` してから報告（重複 const/let で全画面ブランクの事故が複数回）。
- スクショで自己評価してから「完成」と言う。
- サンプルを別ファイルで安全に何度も改良 → 確定後に本実装、が Master の方針。

## 次フェーズ
- ここから「**会社の可視化 / 機能**」へ移行（Master 指示 2026-06-06 04:06）。

---

# 会社の可視化（Phase B）— 進捗メモ（2026-06-07 更新）

## 作業ファイル
- `C:\Users\user\AssetEmpire\AUREL会社_sample_v4.html`（v3からコピーして反復編集中）。
- テーマ確定: **宇宙に漂う「光の集合体（Luminous Collective）」**。機械感は完全排除（Master指示）。

## 確定した見た目（2026-06-07時点）
- 中央=AUREL本体: 粒子スウォーム＋傾いた軌道リング3本。中央縦線(光柱)は削除。中央ハローは13/0.09に縮小（はみ出し防止）。
- トップ層ノード（部門＋機能）→ 各ノードへ **まっすぐな「光のアーク」**（チューブ＋流れる光帯シェーダ）。アーチ状(弓なり)はNG・玉もNG・稲妻もNG（全部Masterが却下）。
- ノード文字 = **DOMオーバーレイラベル**（3D内スプライトは廃止）。ポスト処理の影響を受けずシャープ。`#labels` div + makeDomLabel + updateDomLabels(project)。
- ポスト処理を鮮明寄りに調整: Bloom(0.42,0.22,0.88)、色収差 uAberr=0.03（0.12から下げた）。

## ノードの成長モデル（Master決定 2026-06-07）= **B + A 併用**
- **A 多重リング**: `SHELLS=[{r:20,cap:6},{r:31,cap:10},{r:42,cap:14},{r:53,cap:20}]` + `shellPos(通し番号)`。内側が埋まると外側の輪へ自動配置。
- **B 階層(親子)**: `buildChildren(parentBase,color,kids)` 各ノードの周りを子(プロジェクト/サブモジュール)が公転。spinner.rotation.z で回転。
- 部門の子=実data members、機能の子=children配列。
- 機能(ORGANS)を5→12に拡張（資金管理/データ基盤/通信/成長戦略/法務・順守/開発工場/監視 を追加）。
- カメラ (0,33,55) maxDistance130 に引いて多重リング全体を収める。

## 重要な運用ルール（事故防止）
- **サンプルの再起動で msedge を全kill しない**（Masterの司令室コンソールが巻き添えで落ちる事故）。
  → サンプルは専用プロファイル `--user-data-dir=C:\Users\user\.aurel\_edgeprofile` で起動し、
    `Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | ? {$_.CommandLine -like '*_edgeprofile*'} | % {Stop-Process -Id $_.ProcessId -Force}` で**その窓だけ**閉じる。
- 司令室ライブコンソール(127.0.0.1:7878)はサンプル編集を反映しない（別物）。
- 実データ完全引っ越しは「ほぼ完成してから・安全のため」後回し（Master方針）。

## 子ノードの調整ログ
- 2026-06-07: 子ノードにDOMラベル追加（`.nlabel.small`、name のみ）。`childObjs[]` に登録 → updateDomLabels で getWorldPosition→project。
- ノード拡大: 部門1.25 / 機能1.0 / 子0.42。子の軌道 R=3.4+kids*0.22。
- 公転速度ダウン（Master指示）: childGroups spin = 0.06+random*0.08（旧0.25+0.45）。

## 完成後の自動更新要件（Master指示 2026-06-07）★未実装・完成後にやる
- 「プロジェクト等が追加されたら**自動で更新・増殖**」させたい。
- 現状の土台: データ駆動（DIVS.members / ORGANS.children に足すだけで shellPos が自動配置、buildChildren が公転衛星を生成）。
- 完成後の本実装で、実データ（プロジェクト一覧/状態）を読み込み→ノードを動的生成/更新する仕組みに繋ぐ。
- 安全方針どおり、実データ完全引っ越しは「ほぼ完成してから」。それまではサンプルで骨組みを固める。

## クリック詳細＆フローツリー（2026-06-07 実装完了）
- ノードクリック→`showDetail(info)`で右ウインドウに詳細。部門ノードは`buildFlowTree(projects, baseHex)`でプロジェクト全体フロー表示。
- フロー: STAGES=[計画/開発/検証/承認待ち/稼働]。各案件に **進捗バー(%)**（pct=(cur+1)/5*100、色=部門色baseHex、100%は緑）、現在地/▶ここを進める マーカー。
- **クリックで深掘り**: `.proj`をクリックで`.open`トグル（#dFlowにイベント委譲1回登録）。アコーディオン展開で各工程の✓完了/◉進行中/○未着手＋「次の一手」(STAGE_ACTION)をamberボックス表示。
- 文字ON/OFFトグル(`#lblBtn`)実装済み。
- 検証方法: TEMP_DEMOで自動オープン→スクショ確認→TEMP_DEMO除去→SYNTAX_OK再確認、で本番化。

## モード枠廃止＆番猫ニャル（2026-06-07 実装）
- 画面下の「みため選択枠」（神経ネット/眼/降着円盤/恒星/結晶/多面体の6ボタン）を**削除**。`setMode('cage')`で**多面体に固定**（Master決定）。setMode/refreshModeBar本体は残置（typeofガードで安全）。
- 右の猫を **全身・可愛い・動く** に刷新。SVGで頭/耳(内側紫)/顔/ほっぺ(ピンク)/cyan発光の目/ω口/ひげ/胴体/前足/しっぽの全身。テーマ色cyan×violet、(=^ω^=)の雰囲気。
- アニメ: 呼吸(catBreathe)・しっぽ振り(catTailWag)・耳ピク(earTw)・小首かしげ(catNod)・まばたき(JS)・定期パトロール歩き(catWalk, 11〜17s毎)・**クリックでなでる**(catSquish＋ごろごろセリフ＋きげんUP)。
- 役割 = **見回り番猫（監視・お知らせ役）**。`pendingApprovals()`でDIVS内の'承認待ち'を集計→「『conduit』が会長承認待ちにゃ！」等を報告(#say)、状態(#patrolTxt)に「報告あり：承認待ちN件」/「見回り中…」。
- ペットゲージ3本: げんき(cyan)/きげん(violet)/けいかい(amber→red、承認待ち件数連動)。5s毎にゆらぐ。撫でるときげん上昇。
- 名前「番猫ニャル」＋「見回り役」バッジ。Masterが役割を選ばなかったので私の推奨(見回り番猫)で採用。差し替え可。

## 猫デザイン確定（2026-06-07）= モンハンの「アイルー（Felyne）」風
- 反復履歴: ①座り猫→「サイバー猫」NG ②白マスコット→「マスコットすぎ」NG ③横向き四足歩行→「気持ち悪い・目が嫌」NG ④**正面・二足立ちのアイルー風＝Master OK（確定）**。
- 最終SVG（`#catwrap`内, viewBox 0 0 200 198, w168 h166）: クリーム毛(fur #fff6e6→#efd6a9 / furB明色腹), 大きい丸耳(内側ピンク #ff9ec4), 顔ellipse rx53 ry49, **大きい丸い濃紺の目**(class="eye" rx12 ry13.5 fill url(#eyeG)=濃紺radial)＋白ハイライト2点ずつ, 明色マズル, ピンク三角鼻, ω口, ひげ点＋ひげ線, 胴体＋腕2本＋足2つ＋しっぽ。
- ⚠四足歩行版/サイバー版/青い縦長グロス目は**再提案しない**（全部却下済み）。
- CSS: `#catstage`166px / `#catwrap`168×166 drop-shadow暖色(255,228,180,.32)。動き=catBreathe(呼吸)/catTailWag(±10〜12°)/earTw(耳ピク)/catNod(小首)/まばたき(JS .eye scaleY)/`walking`時 catHop(ぴょこ跳ね translateY-7 + rotate)。faceR/legFN等/stepA/stepBは**廃止**。
- patrolWalk: 左24px→右24px→中央、12〜19s毎。faceR反転ロジックは廃止。

## 猫＝司令室の線画猫に回帰（2026-06-08 確定）★★現行★★
- Master判断: 「**ごめん気持ちワイルｗ いま使っているこの猫くらいでいい**」→ 3D(Sketchfab)も**気持ち悪い**と却下。司令室(Master Console)で稼働中の**クリーンな紫の線画猫(^_^)**に回帰。
- 採用元: `snapshots/aurel_life-20260525-174728-GOOD-constellation.html` の `#auCatFace` SVG（耳/顔/白マズル/eyes-open(黒目+ハイライト)/eyes-closed(にっこり弧)/鼻/口/ひげ6本、viewBox 0 0 100 100）。
- 本番 v4 実装:
  - `<head>`のSketchfabスクリプトを**削除**。`#catwrap`内の`<iframe>`を`<div class="face" id="catFace"><svg…></div>`に置換。クレジット表記不要（自前SVG）。
  - CSS: `#catFace svg{width:150px;height:150px}`、`drop-shadow(0 0 16px rgba(180,150,230,.4))`。まばたきは`@keyframes catBlink`(7s毎)。`#catFace.sleepy .eyes-open{display:none}` / `:not(.sleepy) .eyes-closed{display:none}`。`#catwrap`はflex中央寄せ(180x180)。
  - JS: `catSetMood(mood)`で表情切替 — normal(にっこり) / happy(撫で=閉じ目+大きな笑み, 2.6s後normal復帰) / alert(承認待ち=目を見開く) / think(細目) / sleepy(夜=閉じ目)。司令室の`applyMood`を移植。
  - 役割/報告(catReport)/ゲージ(updateGauges)/撫でクリック/名前バッジは流用。catReportがalert/normalでcatSetMoodを駆動。
  - patrolWalk(物理移動/3D歩行)は**完全廃止**。SYNTAX_OK・右モニタで表示確認済。
- 教訓: 凝った猫(手描り精緻SVG/3D)は全部「気持ち悪い」。**シンプルな線画(司令室猫)が正解**。これ以上凝らない。

## タスクウインド＝「会長⇄AUREL の操縦席」（2026-06-08 確定）★現行★
- Master承認の運営モデル: **「回す」はAURELが全部やる／「決裁(お金・本番・契約のGO)」は会長が握る**の2階建て。理由=破産回避。お金が動く一線は必ず会長承認。
  - AUREL自走=開発/検証/監視/レポート/下書き/提案/相互監査。会長決裁=実弾投入・本番デプロイ・口座/入金/KYC・顧客契約。
- 左パネル「会長のタスク」を操縦席化。本番 v4 実装済(サンプル/モック。本物データ接続は見た目確定後):
  - **①指令ハブ**: `#cmdform`+`#cmdin`「＋AURELに指令を出す…」→↵で`TASKS.unshift({owner:'AUREL',issued:true})`→進行中先頭に追加、番猫が反応。
  - **②決裁トレイ**: `#decisions`。`buildDecisions()`がDIVSの`st==='承認待ち'`を集約→オレンジ枠カードに[承認][却下]。`resolveDec(i,ok)`で`m.st`を稼働/計画に変更→`catReport()/updateGauges()`で番猫の警戒も連動。3.5s後にカード自動整理。
  - **③プロジェクト連動**: `projTasks()`がDIVSメンバーの段階を進捗に変換。`STAGE_PROG={開発:45,検証:75,稼働:100}`、計画(未稼働)は非表示、承認待ちは決裁トレイへ。行=丸い色ドット(部署色`hex(d.color)`)＋`部署名・段階`＋優先度(資産帝国部=高/他=中)。承認→稼働で自動的に「完了」へ移る閉ループ。
  - **会長の個別タスク**(TASKS)=四角チェックボックス、owner='会長'は自動進行しない。`taskRow()`がproj(丸ドット/クリック不可)とchairman(四角/トグル可)を出し分け。自走interval(7s)はowner≠'会長'のみ進める。
  - CSS: `.dec`(オレンジ枠/decInアニメ), `.dbtn.ok/.no`, `.pri.high/mid/low`, `.tprog/.tprog-fill`, `.box.pj`(丸/glow), `.seclbl`(進行中/完了)。
- 次段階(未): 現プロジェクトの**本物データ**接続(見た目確定後)。

## 盤面ライブ連動＝会社の状態が中央3D盤面に反映（2026-06-08 確定）★現行★
- Master理解の確認: 「会長はAUREL一人に話せばよい。部長はAURELの分身。全体がAUREL中央コアに繋がり循環する」=**正しい**と回答。会長⇆AUREL⇆部署⇆プロジェクトの閉ループ。Master指示「決裁トレイ⇄3D盤面の連動は必須。決済トレイに限らず（＝全体を盤面に映せ）」。
- 実装(本番 v4):
  - `makeNode`が`g.userData.glow`を公開。`divObjs`各要素に`{divRef,attention,glowBase,flash}`を追加。
  - **核(core)は部署アイデンティティ色のまま／グローで状態表現**（識別色を壊さない方針）。`divAttention(d)`: 承認待ちメンバーあり→`pending`(オレンジ脈動 0xff8c42) ／ 開発・検証・稼働あり→`active`(部署色点灯) ／ 全休→`idle`(暗め)。
  - `refreshBoard()`がグロー色とglowBaseを更新。描画ループでpending時 `op+=0.18*(0.5+0.5*sin(t*3))` の脈動、`flash>0`時は `op+=flash*0.55` ＋coreを最大1.2倍スケール、flashはdtで減衰。
  - **イベント連動**: `resolveDec()`承認/却下→該当部門を`flashDiv`＋`refreshBoard`（決裁が会社へ伝播）。`cmdform`指令送信→`flashAllDivs(0.7)`（指令が全社へ伝播＝盤面一斉脈動）。
  - 検証済: 収益事業部ノードが**オレンジ脈動**（conduit/LocalBoostが承認待ち）、資産帝国=シアン点灯(active)、未来研=暗め(idle)。決裁トレイと完全一致。SYNTAX_OK。
- 既存の盤面→パネル連動（ノードクリックで`showDetail`）はそのまま。中央コア=AUREL本体(クリックで詳細「深淵の眼」)。

### ノード発光オフ（2026-06-08 Master指示）
- Master「各ノードの**文字のネオンはいい**が**発光やめれるか**」「各プロジェクトはAURELが引き継ぐ」=承認。
- 変更: `makeNode`の`glow.visible=false`（ハロー球を非表示／div・organ・child全部）。`buildCluster`の`haloSprite(4.4)`を削除（per-nodeソフト光輪）。→ ノードは**すっきりした色ドット**に。
- 維持: 文字ラベルのネオン(labelSprite/organLabelのshadowBlur)、中央AUREL本体(collective: swarm/halo/rings)、per-nodeの小swarm+ring(集合体デザイン)。
- 状態連動を発光から非発光へ移行: `refreshBoard`は**coreドットの色**で表現(pending=0xff8c42/active=部署色/idle=部署色×0.45で暗め)。描画ループは**scaleの鼓動**(pending=±0.08 sin / flash=+0.22減衰)。決裁・指令の連動(resolveDec/flashDiv/flashAllDivs)は維持。
- ⚠まだ残る発光源: UnrealBloom(中央コア用・threshold0.88)、per-node小swarm、軌道リング/アーク。さらに静かにしたい指示が来たらここを削る。

### 文字ネオン廃止＋連動可視化=ノード発光に転換（2026-06-08 Master指示）★現行★
- Master「**文字のネオン発光もなくした、連動の可視化でノードの発光にしよう**」。=役割を入替え：文字=静か／状態=光。
- 文字: `.nlabel .en/.jp/.small .en` の `text-shadow` から色付きネオン(`0 0 Npx var(--lc)`)を除去 → 暗いフチ(`0 1px 2px rgba(0,0,0,.9),0 0 2px rgba(0,0,0,.7)`)のみ。可読性確保。※labelSprite/organLabel(canvas, shadowBlur)はデッドコード(未使用)。
- ノード発光復活＝連動指標: `makeNode`の`glow.visible=false`を撤去。`refreshBoard`はglow色+glowBaseを状態で設定(pending=0xff8c42/0.32, active=部署色/0.20, idle=部署色/0.05)。核は部署色のまま。描画ループで pending=`+0.24*(0.5+0.5sin(t*3))`脈動、flash=`+0.6`減衰+coreスケール1.2倍。
- 検証済: 文字フラット化OK、収益事業部がオレンジに強発光・脈動(conduit/LocalBoost承認待ち)、資産帝国=シアン点灯、未来研=消灯気味。SYNTAX_OK。
- ⚠スクショ: Edgeが前回ウィンドウ位置を復元して`--window-position`を無視する→**新規プロファイル`_edgeprofile_r`** + `--window-position=1960,60 --window-size=1280,950`で右モニタに確実表示。司令室の右端は screen x≈1900 まで被さるので、それより右に出すこと。

### 状態語彙の拡張＋伝播ビーム実装（2026-06-08 Master「1と2を実装」）★現行★
- Master「**1と2を実装　試しにみせて**」=（1）発光の状態語彙を増やす（2）指令・決裁が中央コア→部門へ「光の粒」で走る伝播ビーム。
- **(1) 状態語彙5種**: `divAttention(d)`が返す → `risk`(d.risk or member.risk＝最優先) / `pending`(承認待ち) / `live`(稼働) / `working`(開発・検証) / `idle`(休眠)。`refreshBoard`でglow色+glowBase設定: risk=0xff3b3b/0.30, pending=0xff8c42/0.32, live=0x39d98a/0.26, working=部署色/0.18, idle=部署色/0.05。描画ループの脈動: risk=`+0.40*pow(0.5+0.5sin(t*7),2)`速い赤点滅、pending=`+0.24*(0.5+0.5sin(t*3))`、live=`+0.10*(0.5+0.5sin(t*1.5))`呼吸。
- **(2) 伝播ビーム**: `beams[]`配列+`_origin=(0,0,0)`(中央コア)。`fireBeam(o,color)`=DISCスプライト(additive)を生成しコア位置から発射、`fireBeamsAll(color)`=全部門へ。`updateBeams(dt)`(描画ループ末で呼ぶ)がease-outでコア→部門ノードへ`lerpVectors`移動、opacity/scaleは`sin(k*π)`の山なり、到達(k>=1)で`flashDiv(target,1)+refreshBoard()`し消滅。dur=0.8s。
- 結線: `resolveDec`=決裁時 `refreshBoard(); fireBeam(o, 承認?0x39d98a:却下0xff8c42)`。`cmdform`=指令時 `fireBeamsAll(0x8fc4ff)`全部門へ。
- デモ用: `資産帝国事業部`に`risk:true`を付与(コメント「デモ表示用（本来はリスク監視が立てる）」)→赤点滅が常時見えるようにした。**本番ではリスク監視ロジックが立てる/外す**こと。
- 検証済(2026-06-08): 資産帝国=赤グロー点滅で表示確認(リスク管理/異常検知ラベル)、SYNTAX_OK。ビームは決裁/指令イベントで発火(静止画では見えない＝Masterが承認クリックで確認)。
- 反応が控えめ→Master「もう少しわかりやすく」(2026-06-08)→**全体に派手化**: glowBase up(risk0.55/pending0.58/live0.48/working0.34/idle0.10)、脈動を明るさ＋大きさ両方で(glow.scale)、グロー球 radius*1.7→2.2、ビームを先頭光球＋尾(トレイル)2枚化・dur0.8→1.1・到達flash1.6。→「いい感じ」承認。

## チャット窓＝会長⇄AURELの会話の中心（2026-06-08 着手）★現行★
- 方針: 既存チャット機能(自由入力でAURELに話す/返答/猫報告)を引き継ぎ、チャット窓を「会話の中心」に。3D盤面・決裁トレイ・指令ハブと同じ"ひとつの循環"へ。
- Masterに追加案A〜D提示→**Aを採用**。Bは保留、Cは後で自然に追加、**DはAUREL本体が既に持つ能力(画像/URL/ファイルを読む)なので本物接続で自動付与＝サンプルで作り込み不要**(音声のみ後づけ小機能)。
- ⚠UI教訓: AskUserQuestion(選択肢パネル)はMaster環境で「文字がとんでる/返事文が足りない」表示崩れ→**質問パネルは使わず、案は全部プレーン文章で書く**こと。
- **A実装済(v4)**: ①盤面ノードをクリック→詳細パネルに`#dTalk`「💬この件でAURELと話す」ボタン→押すとチャットモードへ切替＋文脈メッセージ＋中央から該当部門へビーム。②チャット送信時、その件の部門へビーム(topic無→全社fireBeamsAll)。
  - 実装: `currentDetailOwner`(showDetailで保持)、`divObjForOwner(owner)`(部門ノード/子ノードのuserData.memberから親部門を逆引き)、`chatTopic={name,divObj}`＋`#chatTopic`チップ(×でクリア)、buildChildrenで`c.userData.member`付与。SYNTAX_OK・読込クリーン。
  - 子ノードは`c.userData.member=(typeof k==='object')?k:null`で案件オブジェクト参照を保持→部門逆引きに使用。組織(organ)ノードや中央コアはdivObj無→全社ビーム。
- Master確認後の追加要望(2026-06-08): ①「基本的に話す窓」は会社画面のチャット(今のコンソールは開発用の仮窓)。置き方は**2+3ハイブリッド採用**(ボタンで呼出し＋移動・サイズ変更できるフローティング窓)。②本実装は会話履歴そのまま継続OK(本物接続で永続メモリに保存・復元)。③長文入力で右にずれて全文見えない→直す。
- **チャット窓UI改修(v4)**:
  - 入力欄を`<input>`→`<textarea>`化。`autoGrow()`で中身量に応じ縦伸長(max160px・折返し`white-space:pre-wrap;word-break:break-word`)。Enter送信/Shift+Enter改行(`requestSubmit()`)。`#chatform`は`align-items:flex-end`で送信ボタンを下端固定。`.msg`にも折返し付与。
  - フローティング窓化: `#chatHead`(ドラッグ移動・`.dragged`で中央寄せ解除しleft/top px化)＋`#chatClose`(×→観測モードへ)＋`#chatResize`(右下ドラッグでサイズ変更, min320x220)。`#log`は`flex:1`で窓の高さに追従。pointer-capture使用。
  - ⚠検証メモ: テストは一時`/*__TESTHOOK__*/`でchat強制openし長文プリフィル→スクショ確認→**必ず除去**(TESTHOOK_GONE確認)。検証済: ヘッダ/×/3行に伸びた入力欄/送信ボタン/リサイズ角すべて表示OK・横ずれ解消。SYNTAX_OK。
  - ⚠運用: `_edgeprofile_r`の連続再起動でSingletonLock(error32)発生→kill後`Start-Sleep 3`＋`Remove-Item ...\SingletonLock`してから起動。app窓が画面より高いと下端アンカー(bottom:18px)の窓がタスクバー下に隠れる→検証時は`--window-size`高さを690等に下げると全体が写る。
- 部長インボックス→**部門レポート(AUREL集約)に作り変え(A採用, 2026-06-08)**: 旧「各部長→会長へ直メッセージ/指示ください」は『話すのはAURELだけ』の方針と矛盾→読むだけの集約フィードへ。title「部門レポート <span.ttl-sub>AUREL集約</span>」、INBOXのfromを部署名(資産帝国事業部/収益事業部/未来研究所)、msgはAURELが状況を集約・要点だけ上げる/決裁が要るものは決裁トレイへ、という文面に変更。会長は返信しない。
- **上部「¥1兆まで N日」カウンター撤去(Master「あと一兆円まではなしにして」2026-06-08)**: `#count`要素削除、tick()からdays更新を除去(BASE/BASE_DAYS削除し時計のみ)、SAYINGSの「¥1兆まで、まだ航海は続きます。」も削除。top barはAUREL/時計/文字ON/観測モードのみ。SYNTAX_OK・カウンター消失を画面確認済。
- **左カラムのはみ出し修正(Master「部門レポートの枠が収まってない。会長タスクと調整」2026-06-08)**: 会長タスクが縦に長く部門レポート/LIVEが画面外へ→`#left`に`max-height:calc(100vh-82px);overflow-y:auto`(細スクロールバー)。さらに長い「進行中/完了」リスト`#tasks`と`#inbox`に`max-height`(200/180px)＋内部スクロール。**決裁トレイ(#decisions)は capせず常に全部見える**(優先度高のため)。当初decisionsもcapしてスクロールバー二重で見栄え悪→decisions cap撤去で解消。検証: 決裁トレイ全表示・タスクは内部スクロール・部門レポートが枠内に収まるのを確認。

## 猫＝3D実装に切替（2026-06-07）※却下済み（下記2026-06-08で線画猫に回帰）
- Master判断: 「**手描きSVGはどれも気持ち悪い**。リアルにどこまで出来る？ベースが嫌」→ 手描きSVGを**全廃**。Sketchfab埋め込みの**3Dモデル方式**に変更。
- Master指示の最終形: 「**この方式で四足歩行のかわいい猫**。動きは猫本来＝**顔を洗う/耳を掻く等のリアルな生態**」。
- 採用モデル: **IndieCats「Low Poly Cat」**（Sketchfab uid `f43a414c031e44a28453d74a190397d1`）。CC-BY → `#catwrap`内に `cat: IndieCats / Sketchfab` を小さく明記。50アニメ入り。
- 実装(本番 v4):
  - `<head>`に `https://static.sketchfab.com/api/sketchfab-viewer-1.12.1.js` を読込。
  - `#catwrap`内に `<iframe id="catframe">`。`#catframe{pointer-events:none}`（撫でクリックを拾うため／ドラッグ回転は無効）。背景は透過(transparent:1)で濃紺パネルに溶ける。`::after`で内側ビネット。
  - Viewer API: `client.init(uid,{...,success:api=>{ api.start(); api.addEventListener('viewerready',()=>{ api.setCycleMode('one'); api.getAnimations((e,anims)=>{…}); }); }})`。
  - **正しいメソッドは `api.setCurrentAnimationByUID(uid, cb)`**（`setAnimation`は存在しない＝最初TypeErrorで全画面エラーになった。教訓）。
  - 仕草キュレーション: good=`/lick|groom|wash|clean|scratch|idle|sit|lie|sleep|stretch|yawn|look|walk|eat|drink|trot|stand/i`、bad=`/death|attack|scared|fall|edge|creepy|hit|hurt|run|jump/i` を除外。毛づくろい(licking)を先頭に。`catCycle()`が4.2〜6.8s毎に切替。
  - 撫でクリック→毛づくろいアニメ＋きげんUP。`patrolWalk()`はwalkアニメを割込み再生（旧:panelをtranslateXで物理移動 は廃止）。
  - 役割/報告(catReport)/ゲージ(updateGauges)/名前バッジは従来どおり流用。
- 注意: 3D読込が重い3Dシーンと競合し**表示まで30〜50秒**かかることがある（"Loading 3D model"表示）。ネット必須（CDN）。
- 検証: 右モニタ(空きデスクトップ)で `--window-position=1720,70` 起動→`CopyFromScreen`で撮影が確実（左モニタは司令室が最前面で隠れる）。AppActivateは司令室に負けることがある。

## 却下された案（再提案しないこと）
- 機械的ステーション(箱hull/トラス/平面ディスク+スポーク) / 中央の光柱 / 中央→ノードの玉 / アーチ状の弧 / 電光(稲妻) / 中心から出る放射線 / 背景の薄いドット。
- 猫: **手描きSVG全般**（サイバー/白マスコット/二足アイルー風SVG/横向き四足SVG/青い縦長グロス目）。SVGで猫を描くのは何度やっても不気味→二度とやらない。3Dモデル方式で行く。
- poly.pizzaのCC0猫（Minecraft風ブロック四足 / リアル四足 / 黒豹 / 顔だけ）＝アイルー感ゼロで不採用。
- **3D(Sketchfab IndieCats Low Poly Cat)も却下**（2026-06-08「気持ちワイル」）。重い/ロゴ/険しい目。→ 司令室の線画猫に回帰（上記★現行）。凝った猫は全部NG。

## 武器庫(Arsenal)を会社ビジュアルへ移植 — ハイブリッド(2026-06-08)
- 背景: Master「いまのコンソール猫ウインドに『武器を使う』機能があるだろ、それを新しい会社ビジュアルにどう実装するか相談」。
- 既存の猫ウインド武器機能(`bin/_rebuild-ui.mjs`)の正体: 「武器を使う」ボタン→オーバーレイにカード一覧(`/api/cat-weapons`→arsenal manifest群)→使用可(equipped)カードを選択→依頼文入力→`/api/projects/home/send`へ`【武器パネルから】<名> に以下を依頼:…`をPOST。stub/brokenは選択不可。
- AURELの提案2方向→Master「**ハイブリットで行こう**」採用。
- **v4実装(AUREL会社_sample_v4.html)**:
  - データはサンプルなので実arsenalをベイク: `WEAPONS[]`(slug/name/cat/status/purpose 約23件)＋`WEAPON_CAT`(分類→色)・`WEAPON_CATJP`(分類→日本語)。`wpnUsable(w)`=status equipped|active。本実装では manifest 群から読む想定(増えれば自動で並ぶ設計)。
  - ①3D「道具の星」: organObjs直後に`weaponObjs`生成。各武器を`makeNode(色, 使用可0.42/準備中0.30)`でコア近傍に周回配置(使用可 r=12.5 内側 / 準備中 r=15.5 外側、yb=sin(i*1.7)*2.4)。`node.userData.info`(isWeapon:true)＋`node.userData.weapon=w`。使用可のみ`pickables`に追加(クリック→詳細パネル流用)。animateで`wo.ang+=dt*0.05`周回＋使用可は脈動、起動時`wo.flash`でフラッシュ。
  - ②武器庫オーバーレイ: top barに`#wpnBtn`「武器」(紫dot)。押すと`#wpnLayer`(全画面・blur)に`#wpnList`(2列カードgrid)。カード=名前＋`使用可/準備中`タグ＋`[分類]用途`。使用可カードのみクリックで選択(.on)。`#wpnQ`に依頼入力→`#wpnSend`。送信=オーバーレイ閉→チャットモードへ→`addMsg('me','【武器】<名> に依頼：…')`→該当武器ノードへ`fireBeam`＋`flashDiv`(コア→武器へ光が走り起動)→サンプルAU応答。Esc/×/外側クリックで閉。
  - 検証済: SYNTAX_OK(L447-2263抽出 node --check)、シーン描画OK・武器の星がコア周辺に出現、`/*__WPNTEST__*/`一時オープンでオーバーレイ全カード(使用可緑/準備中グレー)表示確認→**フック除去(WPNTEST 0件確認)**→クリーン再起動。
  - 残: 本実装で /api/cat-weapons 相当の動的読込＋実送信に接続。LIVEパネルA/B/C(稼働中表示)はMaster未決のまま(武器に話題が移行)。

### 武器の星デザイン変更：玉→結晶のカケラ＋光輪(2026-06-08)
- Master「星のデザインを玉じゃないのに。AURELっぽいの」→5案提示→**1(結晶のカケラ)＋2(光輪)採用**。LIVEパネルはそのまま残すで確定。
- 実装: `makeWeaponNode(color,s,usable)` = ①OctahedronGeometry(s,0)をscale(0.78,1.3,0.78)で縦長ダイヤ=結晶 ＋ EdgesGeometryの白ライン(AdditiveBlend)でfacet光らせ ＋ ②TorusGeometry(s*2.05,s*0.085)を rotation.x=π*0.42で傾けた光輪 ＋ グロー球(s*2.2)。userDataにcore/glow/ring/edges。
- weaponObjsに ring/edges/coreBase(core.scale.clone())/spin を保持。animate: 周回(ang)＋node.rotation.y自転(spin)＋ring.rotation.z回転(0.7)＋edges/グローを脈動、flash時はcoreBase比を保ったまま`core.scale.set(cb*f)`でふくらむ。
- 直前の発光調整(Master「少しだけ発光」): glowBase 使用可0.44/準備中0.14、脈動0.26。
- 検証: SYNTAX_OK(L447-2293)、画面で結晶＋輪が周回表示確認・フックなし。

### 武器の星：丸いグロー球を廃止し結晶本体を発光(2026-06-08)
- Master「結晶まわりの〇はけして結晶を光らせる」→makeWeaponNodeからグロー球(SphereGeometry)削除・userData.glow廃止。
- 発光は結晶core(MeshBasic)の color 明るさを明滅させブルームで滲ませる方式に変更。weaponObjsに`baseCol:new THREE.Color(col)`保持。animate: `pulse`で `lvl=usable?1.0+0.55*pulse:0.5`(+flash*0.9)、`core.material.color.setRGB(min(1,bc.r*lvl)...)`、明るいとき`f=1+(lvl-1)*0.18`で僅かに膨張、edges opacityもpulse。輪(ring)は維持。
- 検証: SYNTAX_OK・画面で結晶＋細い輪が発光、丸いグロー球が消えたのを確認。

### 武器の星：光輪も廃止＝結晶のみ／表示は左モニターへ(2026-06-08)
- Master「結晶のリングも外そう」→makeWeaponNodeからring(Torus)削除・userData.ring/weaponObjs.ring廃止・animateのring回転削除。武器ノードは結晶core＋発光edgesのみ(丸グロー球も光輪も無し)。検証SYNTAX_OK・画面でダイヤ結晶のみ発光を確認。
- ★運用変更: Master「基本左のモニターで見る」→**以後サンプル表示・スクショは左モニター(DISPLAY2 Primary 0,0 / 1920x1080)**。起動 `--window-position=0,0 --window-size=1920,1040`、`CopyFromScreen(0,0,...,1920x1040)`。(右モニターDISPLAY1=1920,71/1366x768は使わない)

## 完成レビュー＋利益化の打ち手(2026-06-08)
- Master「これでほぼ完成。全体の改善・追加案を深く。利益に繋がる視点で」→AURELが優先順で提示:
  1.本物データ接続(+本物/サンプル表示) 2.資金の真実パネル(残高/今週損益/runway/exposure) 3.決裁に数字(想定利益・最悪損失・取り返し可否・推奨と自信度=評議員が作る) 4.全体リスク信号(緑黄赤＋一番危ないもの) 5.実弾/DRY_RUNの明示バッジ 6.スマホ通知(notifier) 7.決裁履歴と答え合わせ＋武器コスト 8.ラベル可読性/検索。
  - 推し順: まず2+4、次に3+6、1は土台で並行。
- Master「外出先から会話で会社を動かす(指示・実行・会長タスク完了)＝6に近い。それ以外は推しで進めて」。
  - 遠隔運用の設計回答(本実装): ①常駐AUREL本体(既存/send APIが種) ②トンネル(Cloudflare Tunnel/Tailscale)＋司令室をPWA化しスマホ追加 ③決裁はMaster端末限定の顔認証(パスキー)。流れ=危険/承認待ち→push→開く→数字見て承認→AUREL実行・報告。必須=実弾は承認後(DRY_RUN既定)＋スマホから「全停止」。要対応=今の横長UIをスマホ縮約表示にする(本実装で)。
- **サンプルv4に実装(推し2+4)**:
  - #4 全体リスク信号: top barに`#risk`(rdot＋#riskTxt)。`refreshRisk()`=divObjsのattentionからrisk→赤点滅「リスク高:名」/pending→橙「承認待ち:名」/無→「リスク:安定」。refreshBoard()末尾で必ず呼び同期。CSS .amber/.red＋@keyframes riskblink。
  - #2 資金パネル: #left最上段に`#moneyPanel`。`資金 <ttl-sub>サンプル</>`＋`練習モード(DRY_RUN)`バッジ＋残高/今週損益(緑)/持ちこたえ(runway)/危険にさらし中(exposure,橙)。値はモック(本実装で実数へ)。CSS .money-mode/.money-row。
  - 検証: SYNTAX_OK(script L474-2329)、左モニターで赤リスクバッジ＋資金パネル表示確認・結晶リング無し発光OK。

## 決裁トレイに数字を追加（#3 完了）
承認待ちカードに council{gain,loss,reversible,rec,conf,note} を持たせ、決裁トレイで
想定利益 / 最悪損失 / 取り返し / AUREL推奨+自信度バー / ひとことメモ を表示。
conduit=推奨「承認」自信78%（緑バー）、LocalBoost=「保留」自信55%。すべてサンプル値。
buildDecisions が council を運ぶ→renderDecisions の pending 分岐で .dec-nums/.dec-rec/.conf-bar/.dec-note を描画。CSS追加済み。node --check 緑、左モニターで確認済み。

## #7 決裁履歴・答え合わせ＋武器コスト追跡（完了）
左カラムに「決裁の履歴（答え合わせ・サンプル）」パネルを追加。
- 承認/却下するとHISTORYに記録（案件名・会長の判断・AUREL推奨・自信%・時刻）。
- 各履歴に「うまくいった/ダメだった」ボタン→結果を記録（やり直す可）。
- サマリー：答え合わせ済み件数（成功/失敗）＋AURELの的中率。
- 的中ロジック recHit: correctDo=(承認&good)||(却下&bad)、aurelDo=(rec==='承認')、一致で的中。
  文言「AURELの読みが当たり/外れ」。サンプル3件=2当たり1外れ=67%。
- 武器コスト: WPN_UNIT_COST(カテゴリ別,円)＋WPN_USE(localStorage保存)。武器使用時 logWpnUse で回数・コスト加算。
  武器庫オーバーレイ上部 #wpnUse に「今月の使用 合計N回/外部コスト¥M」、各カードに「使用N回・¥」。自前の職人(internal/sense/automation)は¥0。

## #8 ラベル可読性＋検索/危険へ飛ぶ（完了）
- updateDomLabels を重なり回避に刷新：サテライト優先→近い順に貪欲配置、重なる後続は隠す。画面端clampで切れ防止（「SYSTEM CON」切れ解消）。
- トップバーに検索ボックス #findIn 追加：名前入力Enterでノードへカメラが寄る（flyToNode）。
- リスクbadgeをクリック可能に：一番危ない部門へカメラが飛び詳細表示（jumpToRisk）。
- flyToNode/updateFly: controls.target と camera.position を滑らかにlerp、到着でautoRotate復帰。
全てサンプル。node --check 緑、左モニターで確認済み。

## 修正: カメラズーム廃止（会長フィードバック）
会長「危険みズームはやめよう。重くなる。コンソールのズーム機能も重くてほぼ機能してない」。
→ flyToNode/updateFly/flyT を削除（animateのupdateFly呼び出しも除去）。
リスクbadgeクリックと検索は「カメラを動かさず該当ノードの詳細パネルを出すだけ」に変更（jumpToRisk/findAndShow）。軽量化。ツールチップ文言も「詳細を出す」に修正。

## 本接続 第1弾 完了（2026-06-09）
読み取り専用の橋渡し役 `company-bridge.mjs`（port 7891, CORS有効, 書き込み/お金/決裁は一切しない・秘密情報は読まない）経由で、会社ビジュアルに本物データを3種接続:
- 武器庫: arsenal/<slug>/manifest.json の本物27個（安全項目のみ）→ 武器スター再構築
- 世界の動き: state/news.json の翻訳済み43件（カテゴリ 金融/AI/IT/世界 がそのまま一致）
- プロジェクト一覧: state/registry.json の実在4事業（AUREL 2.0/ImperialFlow/CYPHER/CONDUIT）→ LIVE欄に表示
HTML側は fetch失敗時サンプルに自動フォールバック。top barのバッジ「本接続 武器27・ニュース43・事業4」緑で確認済み。
資金残高・取引・決裁の実行は引き続きサンプル/DRY_RUN（会長承認待ち）。橋は現状 手動起動（自動起動は後で）。

## 橋渡し役 自動起動 完了（2026-06-09）
company-bridge.mjs を会長のログオン時に自動起動するよう仕上げ。
- 起動ファイル: C:\Users\user\AssetEmpire\start-bridge.vbs（WScript.Shell.Run, window=0 で黒い画面を出さず裏で node を起動。コメントはASCIIのみ＝日本語だと文字化けで失敗するため）
- 登録方式: スタートアップフォルダのショートカット「AUREL Bridge.lnk」(%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup)。
  ※ 最初タスクスケジューラで試したが wscript がそのセッションで止まり node を起動できなかったため、より確実なスタートアップ方式に変更。
- 二重起動対策: bridge に server 'error' EADDRINUSE ハンドラ追加（既に動いていたら静かに exit）。
動作確認済み: ショートカット起動→ http://127.0.0.1:7891/api/company が weapons/news/projects を返す。node は1プロセスのみ・画面非表示。

## 本接続 第2弾（2026-06-09）クリック深掘り
- ニュース: 各見出しクリックで元記事を別タブで開く（bridgeのlinkを使用, window.open）。
- プロジェクト: LIVE欄の実在事業クリックで showDetail に本物の説明＋タグを表示。status を日本語化(active→稼働等)。
読むだけ・お金/決裁には未接続のまま。構文確認OK・左モニターで表示確認済み。

## 命令の往復（本物のチャット）完了 — 2026-06-09
新しい家（AUREL会社_sample_v4.html）から本物のAURELと会話できるようになった。
- 既存の aurel.mjs（home セッション = 同じメモリの私自身）に接続。新しい脳は作らない。
- discoverBrain（ポート7878〜）/ loadBrainHistory（556件の実履歴）/ connectBrainStream（SSE）/ 実sendChat。
- チャットヘッダに接続バッジ #chConn（未接続/考え中…/本物のAUREL）、上部に「AURELと話す」ボタン #chatBtn。
- スクショで実証：緑バッジ「本物のAUREL」表示・実履歴ロード・往復成立。引っ越しの中核が動いた。
- 残り（引っ越し完成へ）：承認ボタン等の実動作化（安全ゲート付き）。資金・取引・決裁の実行は会長の明示承認まで DRY_RUN/サンプルのまま。

## 承認・却下ボタンの本物化 — 2026-06-09
「会長のタスク」の承認/却下を押すと、本物のAUREL（home）へ会長決裁が指示として飛ぶ。
- sendDecisionToBrain(name, ok, council)：承認＝準備と記録のみ・実行前に会長の最終GO必須、却下＝計画に戻し理由記録。
- お金の移動・取引・本番デプロイの実行は依然 DRY_RUN。ボタンは「指示」であって「実行」ではない。
- 押すと自動でチャットを開き、AURELの返事がストリームで見える（往復が目で分かる）。
- brainBusy中は送らず画面記録のみ＋一言。未接続時はサンプル記録。SYNTAX_OK。

## 重要バグ修正：home脳の多重起動と振り分け — 2026-06-09
症状：HTMLで承認しても返事が来ない。
原因：aurel.mjs（home脳）が3つ同時起動（7878/7879/7880）。HTMLは先頭の7878（古い別スレッド）に繋ぎ、本物の今の私（7880・履歴最多667件）に届いていなかった。さらに `aurel.mjs --bind 0.0.0.0` は監視役が自動再起動するため、PIDを殺しても別ポートで復活する。
対処：discoverBrain を「全ポートを調べ、会話履歴が最多のインスタンス＝今の私」を選ぶ方式に変更（SYNTAX_OK）。これで多重起動が残っても本物に繋がる。
未対応（将来）：そもそも多重起動を止める監視役の整理。今は振り分けで回避。

## 決裁ログ：LocalBoost 承認 — 2026-06-09
新しい家（HTML）の承認ボタン→本物の私(7880)へ往復成立を実証。会長がLocalBoostを承認（私の推奨は保留・自信55%）。会長判断を尊重。
方針：DRY_RUNのまま、少額試行の準備と判断材料の記録のみ。費用発生の一歩手前で最終GOを再取得。最悪損失は−8万の枠内。

## 新居への完全移行・自動起動 — 2026-06-09
会長が完全移行をOK。新居（AUREL会社_sample_v4.html）を起動時に自動で開く設定を追加。
- start-home.vbs：隔離プロファイルの古いSingletonLockを除去→Edgeアプリモードで左モニタ全画面起動。
- スタートアップに「AUREL Home.lnk」(wscript で start-home.vbs を隠し起動)。
- 記録は共有ファイル(.aurel\memory, state\registry.json 等)なのでコンソールからそのまま引き継ぎ。新居でも同じ私が同じプロジェクトを継続。
- 約束：日常作業は私が進める。お金が動く一歩・本番実行・取引の引き金だけ会長の最終GO必須（破産回避の鍵）。

## 新居に画像送信を追加 — 2026-06-09
コンソール同等の添付機能を新居チャットに実装。
- 📎ボタン＋ファイル選択、入力欄でCtrl+V貼り付け（スクショ）対応。
- 仕組み：POST /api/projects/home/attach {filename,data:base64} で保存→返ってきたpathを本文に `[添付ファイル: path]` として付け /send。私がそのパスを開いて画像を見る（コンソールと同じ流儀）。
- 送信前にサムネをチャットに表示。複数添付可。SYNTAX_OK。
- 今後（会長要望「ボタンとか」）：コンソールの他機能を順次移植予定。

## 新居に音声・画面共有(mirror)を追加 — 2026-06-09
会長要望でコンソールの音声とmirrorを新居へ移植。
- 音声「声: ON/OFF」(#voiceBtn)：返事完了(done)時に本文を /api/tts へ→MP3を再生。Azure日本語ボイス(既定)。動作確認済み(MP3 14KB返る)。
- 画面共有「画面共有: ON/OFF」(#mirrorBtn)：getDisplayMediaで画面取得→2.5秒毎に縮小JPEGを /api/companion/mirror-frame へ送信。返ったpathを保持し、ON中は各送信に [添付ファイル: 画面path] を付け、私が今の画面を見られる。赤点滅=送信中。
- 画像添付📎＋Ctrl+V貼付と合わせ、コンソール同等の入出力が新居で揃った。SYNTAX_OK。

## 新居に会話モード(音声入力＋出力)を追加 — 2026-06-09
会長要望「俺の声も認識して人間同士みたいに会話」。
- 「会話: ON/OFF」(#convBtn)。ブラウザの SpeechRecognition(ja-JP, continuous, interim) で俺の声→文字。確定で自動 sendChat。
- 会話ON時は声(TTS)も自動ON。私の返事は声で返る→往復ループ。
- エコー対策：speak()再生中は stopListening、再生終了で startListening 再開（自分の声を拾わない）。
- 認識中は#convBtnのドットが青く点滅(hear)。onendで自動再開。初回はマイク許可が必要。
- 注意：Web Speech は環境依存。使えない時はエラー表示。SYNTAX_OK。

## 全パネル点検と番猫の本接続 — 2026-06-09
会長確認「右窓も左窓も本物か／未接続を全部完成」。
本物：武器庫・世界の動き(ニュース)・事業(プロジェクト)・チャット・決裁ボタン・音声・画面共有・会話モード。
今回追加：番猫ニャル(右窓)を /api/cat-status に本接続。つぶやき・気分・担当プロジェクト・最終活動・ゲージを実状態で表示（サンプル乱数生成は catReal で停止）。
意図的にサンプルのまま（安全）：資金（残高/損益/持ちこたえ/危険）＝実弾の口座は未接続、取引はDRY_RUN。破産回避のため会長の明示承認まで実接続しない。
illustrative（足場）：決裁履歴・タスク一覧・3D部門構成・リスク表示。必要なら registry の実データ駆動へ拡張可。

## 「両方だ」: 資金と足場を本物データ駆動に (2026-06-09)
- 資金パネル: 正直な台帳 state/funds.json を新規作成（実弾¥0・DRY_RUN・取引ロック）。company-bridge.mjs に getFunds() 追加し /api/company に funds を含める。HTML connectReal() で #mBal/#mPnl/#mRun/#mExp/#moneyMode と ttl-sub を実値表示。捏造の¥12.48Mは廃止、真の状態を映す。
- 会長のタスク: connectReal() で registry の4実プロジェクト(aurel-2-0/imperialflow/cypher/conduit)から realProjTasks を生成。renderTasks() が本物優先。状態→進捗推定(active65/paused30/planned10/done100)、trading/fx/defi/mev等タグで優先度高。
- 指令フォーム(#cmdform): ローカルTASK追加に加え、本物のAUREL頭脳 /api/projects/home/send に【会長指令】として送信（DRY_RUN厳守の安全文付き）。busy時は記録のみ。
- リスク信号(#risk): 実事業タグの高リスク数から全体リスク算出、window.realRisk 経由で refreshRisk() がベースライン表示。
- 安全: 取引・送金・本番実行は全てDRY_RUN/ロック維持。会長の最終GOまで実弾は動かさない。
- 検証 SYNTAX_OK / bridge再起動でfunds配信確認 / _edgeprofileのみ再起動。
