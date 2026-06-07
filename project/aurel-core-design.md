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

## 却下された案（再提案しないこと）
- 機械的ステーション(箱hull/トラス/平面ディスク+スポーク) / 中央の光柱 / 中央→ノードの玉 / アーチ状の弧 / 電光(稲妻) / 中心から出る放射線 / 背景の薄いドット。
