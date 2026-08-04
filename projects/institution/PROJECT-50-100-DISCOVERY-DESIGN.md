---
doc_id: AURELIAN-EXPANSION-FRONTIER-DESIGN-v2
tags: [institution, design, discovery, frontier, project50, project100, north-star, approved]
type: design-proposal
rank: 設計裁可済み（Stage 0固定・Stage 1着工）
created: 2026-08-04
updated: 2026-08-04
status: approved — chairman GO, Stage 0 fixed, Stage 1 underway
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: 会長＋ChatGPTアドバイザー「Profit Source Expansion × High Return Frontier / Project 50→100」
constraint: 実装はpaper・金ゼロ・既存無改変・自動Live化なし・自動採用なし・KPI化なし・プロップ非接触。North Star思想はStage 0で設計上の固定目的として扱う（憲章v2刻印はStage 5）。
---

> **会長裁可（2026-08-04）**: 本設計を裁可。ただし(1)North Starを攻めの方向へ固定（下記）、(2)North Star思想はStage 0で設計上の固定目的とし、CHARTER v2正式改定はStage 5（実装検証後）へ後置、(3)Discoveryを縮小解釈しない（未知Cell/Hybrid/未知Source/Cross-Source＋現在分類名すら持たない利益構造まで対象）、(4)Frontierは単なるリスク分析器でなく機関能力を外側へ拡張する測定エンジン。Stage 0→Stage 1着工GO。Live化・資金移動・Leverage変更・未知Edge自動採用は禁止。

# Aurelian 拡張設計 — Discovery Engine × Return/Risk Frontier

> 統括CEO AUREL による最適設計案。実装は会長承認後。既存9循環・憲章・源泉は破壊せず、**発見エンジン**と**限界測定エンジン**を追加・接続する。

## Stage 0: North Star（設計上の固定目的・会長裁可 2026-08-04）
> **「生存制約を絶対条件として、資本の複利成長と利益生成能力を積極的に最大化し、そのReturn/Risk Frontierを自己進化によって継続的に外側へ拡張する。」**

この一文が本設計以降の全モジュールの上位目的として固定される（機械可読な階層は下記・憲章v2刻印はStage 5）。
- **HARD CONSTRAINT（絶対条件・違反不可）**: 破産回避＝床(-8/-12/-15%)・Kill Switch・出金権限なしキー。生存は目的でなく全行動の前提。
- **OBJECTIVE（積極的に最大化）**: 資本の複利成長能力と利益生成能力(Profit-Generation Capacity)。守りへ収束させない。制約の内側で**攻めて**能力を伸ばす。
- **EVOLUTION（能力そのものを増やす）**: 未知Edge/未知Cell/Hybrid Cell/未知Source/Cross-Source構造、さらに**現在分類名すら持たない利益構造**を発見し、Return/Risk Frontierを外側へ押し広げる。
- **MOONSHOT（非KPI）**: Project50→100は到達を強制する必達目標ではなく、Frontier拡張の到達可能性を測る研究命題。

重要（会長明示）: Aurelianを「破綻しないが利益能力の低い機関」へ収束させない。生存は極めて重要だが最終目的ではない。生存を絶対条件に固定した上で、能力の限界を更新し続ける。

## 中心思想（この設計の背骨）
現状のAurelianは「与えられた武器を磨く」機械（write_back収束／source_family淘汰／reserve留保／evolve加速）。
不足は2つ:（1）**未知の武器を市場から発見する能力**（2）**自機の利益生成能力の限界を測り押し広げる能力**。
本設計は、生存を**絶対制約**に固定したまま、この2能力を⑨自己進化の「第2ギア」として増設し、North Star OBJECTIVE（能力の積極的最大化）を機械で追える形にする。
**10本目のループは作らない。⑨自己進化に「収束(既存)＋拡張(新設)」の二臓器を持たせる。**

---

## 成果物1〜3: Proposal A（Profit Source Expansion）の接続構造

### 配置場所
G4 Research & Intelligence（感覚器・学習器＝「未来を作る」）の**実体化**。現状G4はworldmodelしか無く未実装に近い。ここに **Discovery Engine** を新設する。

### 新規モジュール（すべて paper・単一書き手・追加のみ・.discovery系接尾）
| モジュール | 役割 | 出力 | 5点契約の帰還⑤ |
|---|---|---|---|
| `discovery.py` | 未知現象の観測・仮説生成。研究空間=price/vol/options/carry/arb/macro/news/event/time/cross-market。大胆に生成 | `discovery.json`（候補仮説＋出自provenance） | 検証結果が次の探索の重み付けへ戻る |
| `hypothesis_ledger.py` | 仮説の知的資本。各仮説にID(例H-327)・指紋fingerprint・状態(active/failed/promoted)・失敗理由タグ | `hypothesis_ledger.json` | 新候補が過去仮説と構造類似かを照合して戻す |
| `validation.py` | 決定的検証ガントレット（LLM非経由=憲章第7条）。統計→反証→コスト→OOS→Paper→既存Edge比較 | 候補ごとの合否＋等級 | 却下も知識化してledgerへ戻す |

### 発見4段階の着地先（LEVEL A/B/C/D）＋非縮小スコープ（会長明示）
- **LEVEL A 未知Cell** → 既存源泉に新soldier枠（source_familyにstatus:slot追加）
- **LEVEL B Hybrid Cell** → 複数源泉サーフェス(*.json)を関数合成する細胞。hybridフラグ付きsoldier
- **LEVEL C 未知Source** → source_familyに**新源泉**を建てる提案（macro/eventと同じ建て方）
- **LEVEL D Cross-Source Structure** → 関係そのもののEdge。structure細胞orメタ源泉。macro_causalのcausal_mapが種
- **LEVEL X 未分類利益構造** → **現在の8-family地図にも4段階分類にも名前が無い利益構造**。Discoveryはこれを「分類不能ゆえ探索対象外」としない。名前が無い＝未踏という理由で優先的に記録する（ledgerに space="uncharted" として残し、後に分類名を与える）。Discoveryは既存戦略の候補生成器ではなく、**未踏の利益構造まで射程に入れる発見器**である。

### 発見と実弾化の分離（絶対）
discoveryは**discovery.json/hypothesis_ledgerにしか書けない**。source_familyへ自動注入しない。
候補→正式採用は既存の`proposals.py`統治（AUREL提案→会長二重ロック enable+arm_code='CHAIRMAN-GO'）を通る。
採用paper細胞→liveは`live_gate`（引き金未実装）を通る。＝「自由に考える能力」と「自由に金を動かす権限」は**構造的に分離**（既存分離を再利用）。

---

## 成果物4: 責任分界
| 主体 | 権限 | 成功判定 |
|---|---|---|
| AI社員（細胞） | 自分のpaper血を回し健康報告 | 持続勝率＋PnL＋非隔離 |
| Research（discovery/validation） | 仮説を大胆に生成・検証・失敗を知識化 | 有効候補の産出＋失敗の構造知識化 |
| Council（council.py拡張） | 候補バッチを審査する6人目の票 or レビュー1パス | 候補の優先度判断の的中 |
| AUREL | 設計判断（Cell/Hybrid/Source判定）・統合設計・会長へ提案 | 循環9/9・盲点ゼロ・良候補の昇格設計 |
| 会長 | 正式採用の最終承認（二重ロック）／live別GO | 機関の方向の最終決定 |

**大胆な研究／厳格な実弾**の非対称を、権限で担保する。

---

## 成果物5: Proposal B（High Return Frontier）の配置
新規 `frontier.py`（測定・研究モジュール＝日々の配分ドライバではない）。
**Frontierは単なるリスク分析器ではない（会長明示）**。機関能力そのものを外側へ拡張するための測定エンジンであり、「今どこに壁があるか」を測って⑨拡張ループへ研究要求を出す起点になる。
機関全体のpaper能力を読み、要求Return帯[10,20,30,50,75,100,150]%で
DD/Tail/ES/必要Leverage/Source集中/Edge数/相関/Capacity/Liquidity/破綻確率がどう変わるかを模擬。
出力`frontier.json`= Aurelian自身のReturn/Risk Frontier ＋（a）壁の位置（b）最も資本効率の良い通常火力帯（c）Project50/100の実現可能性クラス（d）壁の診断（Edge不足/相関/Capacityのどれが律速か）→discoveryへの研究要求種。

### 高Return 3分類（CLASS A/B/C）
- **A STRUCTURAL**（複数独立Edge・強Edge・良配分で構造的に残る）＝最重要
- **B REGIME**（特定環境のみ火力成立。「今月は複数SourceでEdgeが同時に厚い」と認識する研究へ発展）
- **C ARTIFICIAL**（過剰Leverage/Hidden Tail/Overfit/Leakage/コスト無視/過剰集中/一撃破綻）＝**ガントレットで自動棄却**
frontierは**経路を推奨しない・測定と分類のみ**。実Leverageは一切触らない（禁止事項）。

---

## 成果物6: 中央級研究にしつつ通常運用を歪ませない構造
- frontierは**読取専用の測定**。capital.py（日々の配分）にもevolved_configs（本番ノブ）にも書かない。
- 通常運用の血流（auto_writeback cadence）とは**別レーン**。frontier/discoveryはcadence末尾で回し、失敗は非致命（既存4c系と同じ隔離）。
- Project50/100は**必達KPIにしない**（憲章に明記する案＝成果物12）。研究命題であり続ける。

## 成果物7: 2つのProposalを循環させる（⑨の第2ギア）
```
frontier: 壁を X% で発見 → 「なぜX%が壁か」診断（Edge不足/相関/Capacity）
   → discoveryへ研究要求（欠損を狙え）→ 未知Edge探索 → ガントレット → 候補
   → AUREL設計 → 会長承認 → source_familyへ採用 → frontier再測定 → 壁が動く → 再研究
```
**Frontier＝壁を発見するエンジン／Discovery＝壁を突破する武器を発明するエンジン**。相互接続。

## 成果物8: 既存9循環との接続（10本目を作らない）
拡張は既存ループに乗る:
- ①情報＝discoveryの感覚（macro_read/event proximityを種に）
- ④知識＝hypothesis_ledger（仮説の知的資本）
- ⑤失敗＝失敗仮説の知識化（immuneが銘柄を隔離するのに対し、ledgerは**仮説**を記憶）
- ⑨自己進化＝**収束(evolve既存)＋拡張(frontier↔discovery新設)**の二臓器
closed_loops=9/9 不変。⑨が高いギアを一段持つだけ。

## 成果物9: Macro / News・Event を未知Edge探索へ使う
- macro_causalのcausal_map/macro_read → **LEVEL D Cross-Source構造の種**（原油↔株↔金利↔為替の未知の遅行関係）
- event_drivenのproximity/surprise → **LEVEL B Hybrid種**（price×event, vol×event の条件付き偏り）
- ＝macro/eventは利益源泉であると同時にdiscoveryの**感覚フィード**。①情報をさらに太らせる。

## 成果物10: Research/Evolutionから残す/拡張する
- **残す**: write_back収束（ミクロ）・reserve20%留保・evolve収束速度・source_family淘汰・proposals盲点統治・immune隔離（実証済で安全）
- **拡張**: discovery/validation/hypothesis_ledger（新武器の発見）＋frontier（限界の測定）
- reserve予算は今後**2用途**に分岐: 収束速度(既存)＋discovery計算予算(新)。evolutionが2ギア化。

## 成果物11・16: Growth/Survival/Evolution/Diversification 評価
新規 `scorecard.py`（or digest拡張）。4軸を**別々に測定・単一月利へ潰さない**:
- **GROWTH**: paper equityの増分
- **SURVIVAL**: 背負ったRisk（max DD・床への近さ・ES）
- **EVOLUTION**: 利益生成能力そのもの（frontierの効率火力帯の時間推移・Edge数・discovery throughput）
- **DIVERSIFICATION**: 源泉/Cell/Regime/相関構造の多様性
North Starの目的関数がこれを読む: survival=絶対ゲート → 内側でGrowth×Evolutionを最大化、Diversification健全性を制約に。

## 成果物12: North Star — 会長裁可済み文言（2026-08-04固定）
**方式: 新設の競合North Star文書は作らず、既存憲章を改定(v2)して正式な目的関数条項を追加する。ただし正式刻印はStage 5。Stage 0では設計上の固定目的として本文書に据える。**
理由: CHARTER-HIERARCHYで最上位は憲章。別立てNorth Starは「どちらが最高規範か」の曖昧化を生む。憲章第1条は既に種（リスク調整後Return＋規模＋永続進化）を持つ。これを**精密な階層的(lexicographic)目的関数**へ昇華し、攻めの条項を足す。

### 固定North Star（会長裁可・Stage 0）
> **「生存制約を絶対条件として、資本の複利成長と利益生成能力を積極的に最大化し、そのReturn/Risk Frontierを自己進化によって継続的に外側へ拡張する。」**

### 機械可読な階層（憲章 第1条-2 として刻む案・Stage 5で正式改定）
> **絶対制約（HARD・違反不可）**: 生存＝床(-8/-12/-15%)・キルスイッチ・出金権限なしを決して破らない。生存は目的でなく全行動の前提。
> **目的（OBJECTIVE・制約の内側で積極的に最大化）**: 資本の複利成長能力と**利益生成能力(Profit-Generation Capacity)**の継続的拡大。守りへ収束させない。
> **進化（EVOLUTION）**: 未知Edge/Cell/Hybrid/Source/Cross-Source＋未分類利益構造の発見で、Return/Risk Frontierを外側へ押し広げ、能力そのものを増やす。
> Capacityは Growth・Survival・Evolution・Diversification の合成で測り、Frontierが測定・Discovery/Expansionが更新する。
> **明示的非目標（MOONSHOT非KPI）**: 単月/単年リターンの最大化、Project50/100の必達KPI化。

＝「守るだけにしない・生存を絶対条件に固定した上で能力の限界を積極的に更新し続ける」を機械可読な羅針盤にする。

## 成果物13: 建築順序（Stage・会長修正版 2026-08-04）
- **Stage 0（固定済み）**: North Star思想・階層的目的関数を**設計原則として固定**（憲章の正式改定はStage 5へ後置。実装検証前でも設計上の目的として全モジュールが従う）。本設計文書v2に刻印。← **完了**
- **Stage 1（着工）**: hypothesis_ledger＋discovery骨格（研究空間=既存サーフェスのみ・新データ無し）＋validationガントレット。全て自前JSONのみ書込・cadence末尾・読取専用・**採用経路まだ無し**。
- **Stage 2**: frontier.py測定（paper能力を読みfrontier.json＋Project50実現可能性＋A/B/C分類）。純測定＝能力拡張の測定エンジン。
- **Stage 3**: frontier→discovery研究要求の接続（⑨第2ギア拡張ループ）。全paper/助言・採用はproposals→会長のまま。
- **Stage 4**: scorecard（Growth/Survival/Evolution/Diversification 4軸）＋dashboardパネル。
- **Stage 5**: **整合性監査 → CHARTER v2刻印**。Stage 0で固定したNorth Star思想を、実装検証済みの状態で正式に憲章へ改定（会長裁可）。
- **Stage 6+（会長ゲート）**: discovery用の実データ接続 → Project50 → Project100 → （遥か後・別GO）live。

## 成果物14: 現実機と最終構想の差分
| 能力 | 現状 | 最終構想 |
|---|---|---|
| 既存戦略の改善 | ●（write_back/evolve/source_family） | 維持 |
| 未知Edge発見 | ✕ | ●（discovery/validation） |
| 失敗の構造記憶 | △（immuneは銘柄隔離のみ・仮説記憶なし） | ●（hypothesis_ledger） |
| 能力限界の測定 | ✕ | ●（frontier / Return-Risk Frontier） |
| 高Return 3分類 | ✕ | ●（A/B/C・C自動棄却） |
| 4軸評価 | △（digestは9/9中心・P&L非測定） | ●（scorecard: G/S/E/D） |
| North Star目的関数 | △（言葉のみ・機械可読でない） | ●（憲章v2 目的関数） |
| 発見↔限界の循環 | ✕ | ●（⑨第2ギア） |

## 成果物15: 実装前に会長判断が要る事項
1. North Star文言／憲章v2改定の承認（成果物12）
2. G4 Discovery Engineを実体subsystemとして新設する承認
3. reserve予算の2分岐（収束速度 vs discovery計算予算）承認
4. 採用統治（discovery候補→proposals→二重ロック）の承認
5. 「拡張は⑨に乗る・10本目は作らない」方針の確認（or 明示的な10本目を望むか）
6. discovery実データ接続の優先度（eventは既にdata_gated）
7. Project50/100を研究専用・非KPIとする憲章明記の承認
8. PSR×Tail乖離を別トラック（CCI-1）として扱う承認（成果物18）

---

## 成果物18: PSR×Tail 乖離（Charter Compliance Issue CCI-1・別扱い）
- 憲章第1条/第10条/INSTITUTIONAL-CORE:95 = **PSR×テール補正で配分・生PnL禁止**
- 実装 capital.py = **生涯実現PnL比例**（免疫隔離＋床）
- 今回は**修正しない**。分離して後日検討: 乖離理由／PSR正式定義／Tail penalty定義／サンプル不足時の扱い／移行影響。
- 接点: frontierのCapacity測定はPSR×テール補正の「本物度」で行うのが正しく、Class-C棄却はまさにtail penalty。frontier研究の中でPSR/tail式を綺麗に定義でき、後日capital.pyへback-port可能（今は触らない）。

## 禁止事項（今回）
Live化しない／資金移動しない／Leverage上げない／既存戦略勝手に変更しない／既存憲章勝手に書換えない／9循環破壊しない／会長承認なしに新戦略正式採用しない／Unknown Edge自動Live化しない／Project50/100を必達KPIにしない／プロップ非接触。

## 改定
- v1（2026-08-04）: 会長＋アドバイザー指示書に対するAUREL最適設計案 初版（提案・実装未着手）。
