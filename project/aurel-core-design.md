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

## 猫＝3D実装に切替（2026-06-07 確定）★現行
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
