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
