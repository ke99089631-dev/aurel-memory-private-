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
