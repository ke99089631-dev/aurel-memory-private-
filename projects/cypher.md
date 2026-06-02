---
tags: [project/cypher, L4, defi, liquidation, mev, base, active]
type: project
created: 2026-05-19
---

# Project: CYPHER

> AI 思想で設計された L4 第2号。単一目的の DeFi 清算ハンター。
> 並走相手: [[imperialflow]] / 司令: [[Identity/AUREL]]、Master [[Identity/Master]]

## Vision
Base チェーン上の Aave V3 / Morpho の清算ボーナス（5-10%）を、
Balancer フラッシュローン + atomic 実行で刈り取る MEV searcher。
[[imperialflow]] の「多軸統合の美」に対し、「単一ニッチの速度」を体現する対比設計。

## Status (Phase 2a v2 **LIVE**, 2026-06-01 AM4:12)
- ✅ **Aave event listener LIVE** — `eth_subscribe("logs")` で Aave V3 Pool の LiquidationCall を即時購読中
- ✅ **QuickNode WSS** 経由（publicnode / 公式 base.org は不可と判明）
- ✅ skip-list 機構稼働：他 bot が清算した user は 120 秒間 hunt 除外
- ⚠ pending tx 観察は Base architecture（中央集権 sequencer）の制約で不可と確定 → 設計 pivot 完了

### Phase 2a v1 → v2 pivot 経緯
- v1: `newPendingTransactions` で全 pending tx をサンプリング解析を試行
- publicnode WSS: subscribe 自体は成功するが pending tx を 1 件も流さず（30秒タイムアウト）
- Base 公式 wss://mainnet.base.org: 接続自体できず（5 retry exhaust）
- QuickNode WSS: subscribe 成功するが Base は sequencer 内部に pending を閉じてるため event ゼロ
- → **Base は構造的に公開 mempool を持たない**と判明
- v2: `eth_subscribe("logs")` で確定済 Aave 事象を即時取得する方式に pivot
- 全 RPC で universal 動作、false positive ゼロ、~2 秒遅延だが skip-list 用途に十分

## Status (Phase 1f **LIVE 稼働開始**, 2026-05-31 AM6:31)
- ✅ **DRY_RUN=false** / network=BASE MAINNET / dry_run=False で確認済
- ✅ EXECUTOR initialized: address=0x3D42daBE3F7B... / DRY_RUN=NO / contract=0x27c0d36CD0b3...
- ✅ `min_profit_usd` 閾値 $10 → **$3** に緩和（小型機会も拾う）
- ✅ AssetResolver primed (15 reserves), 全 systems online
- ⏸ 実発射待ち：liquidatable position 出現 + net profit ≥ $3 + gas ≤ 0.1 gwei
- 5/31 朝の市場：30 danger zone、2 件 liquidatable（旧 $10 閾値で却下、新 $3 でも -$0.10 は弾く）
- 次に大型清算が出れば **CYPHER 史上初の LIVE tx** が発火する


- ✅ **CypherLiquidator デプロイ済**: `0x27c0d36CD0b3A67d521a144E9aA28832EE9d48f5`
- ✅ **owner**: `0x3D42daBE3F7Bec9735c08fff57bFb26c328C42fd` (Imperial_MEV wallet, ImperialFlow と共有)
- ✅ Sanity check pass: owner() / BALANCER_VAULT() / AAVE_POOL() / AERODROME_ROUTER() 全部期待値返す
- ✅ EXECUTOR_PRIVATE_KEY / EXECUTOR_ADDRESS / EXECUTOR_CONTRACT_ADDRESS 全て `.env` に装填済
- ⚠ **DRY_RUN=true のまま** — Master の最終判断待ち
- 残課題：DRY_RUN=false 切替 + CYPHER 再起動で初の LIVE 実行可能化

### Phase 1e 実施詳細（2026-05-31 AM6:13 → 6:15）
- 当初 wallet rotation 検討 → Master 「気にしない」判断 → ただし MetaMask 鍵忘れ騒動
- 真相判明：Master が見てた MetaMask "Imperial_MEV" は IF MEV wallet (`0x3D42...42fd`, $36.92)、CYPHER 用 (`0xBBC9...AA61`) は別物で空
- 戦略変更：IF MEV wallet を CYPHER でも使い回す（IF MEV は PAUSED で nonce 衝突なし）
- AUREL が IF .env から MEV_PRIVATE_KEY を読出し → アドレス導出で `0x3D42...42fd` と integrity 確認 → CYPHER .env に転記
- `EXECUTOR_ADDRESS` を `0xBBC9...AA61` → `0x3D42daBE3F7Bec9735c08fff57bFb26c328C42fd` に更新
- Hardhat deploy 実行：JSON-RPC parse error で見かけ上 fail、しかし nonce 0→1 / balance 0.01824→0.01823 ETH で **実 tx は成功**判明
- 決定論的 contract address 計算（`keccak(rlp([deployer, 0]))[12:]`）→ `0x27c0d36CD0b3A67d521a144E9aA28832EE9d48f5`
- on-chain bytecode 4,550 bytes 存在確認、`owner()` view call で `0x3D42...42fd` 返却確認
- gas 実費 約 $0.02

### 直近観察（5/31 朝の市場変化）
- danger zone 12 → **30** に倍増
- 初の liquidatable 検出（2 件、$-0.10 net、$10 閾値で却下）
- マーケットが動き始めた、Phase 1e タイミングとして良い
- Base mainnet 接続、**DRY_RUN モードで read-only 観察中**
- 743-800 unique Aave V3 借り手を把握、HF を **5-6 秒で全 indexing**（Multicall3）
- 新ブロック毎に danger zone 14-15 名を **2-3 秒粒度で re-check**
- ダッシュボード稼働: http://127.0.0.1:8090（サイバーパンク UI）
- **Phase 1c**: Solidity 契約 `CypherLiquidator.sol` + Hardhat scaffold + Python calldata builder 完成
  - Balancer flash (0% premium) → Aave liq → Aerodrome swap → Balancer 返済 → owner sweep
  - `npx hardhat compile` 成功（solc 0.8.24, viaIR + optimizer runs=1000）
  - smoke test **5/5 通過**（owner/vault/onlyOwner ガード検証済）
- **Phase 1c+**: indexer/simulator 拡張で plan が LIVE 実行可能な状態に
  - 新規 `asset_resolver.py`: Aave V3 PoolDataProvider を Multicall3 で叩き、user 毎の最大 collateral / 最大 debt を `(asset address, wei量, symbol)` で確定
  - `Position` dataclass 拡張: `collateral_amount_wei` / `debt_amount_wei` / `collateral_symbol` / `debt_symbol` / `resolved_at` / `fully_resolved` プロパティ追加
  - `LiquidationPlan` 拡張: `coll_asset` / `debt_asset` / `debt_amount_wei` / `swap_route` / `min_profit_wei`
  - `simulator.build_aerodrome_route()`: ヒューリスティック（両 stable → 1-hop stable / 片方 WETH → 1-hop volatile / それ以外 → via-WETH 2-hop）
  - `main.py:_hunt_loop` を `index → resolve → simulate → execute` の 4 段に改修
  - 起動時に reserves を事前キャッシュ（TTL 1h）
  - py_compile 全 OK、import + route 構築のロジック単体テスト通過
- **Phase 1d (mainnet-fork integration test) ✅ PASS** — 2026-05-25
  - fork at block 46,366,653（cbBTC/USDC unhealthy user HF=0.9941）
  - 全 atomic 経路成功：Balancer flash → Aave liq → Aerodrome swap → repay → owner sweep
  - 実 profit $0.29 USDC が owner に着金、contract balance 0（leakage なし）
  - **gas 実測 657,800**（Base 0.05 gwei → 約 $0.10/tx → $1000+ debt なら gas/profit 比は十分有利）
  - 使用 archive RPC: IF の QuickNode endpoint を一時借用（CYPHER の publicnode は state pruning で fork 不可）

- **Phase 1d-fix ✅** — 2026-05-26 AM0
  - `CypherLiquidator.sol` に `if (collAsset != debtAsset)` ガード追加（same-asset 時の Aerodrome swap-self を回避）
  - 副次的に `minProfitWei` を最終 balance check に組み込み、same-asset path でも profit floor 強制
  - **再 compile + smoke test 5/5 OK + 成功 regression test OK**

- **Phase 1d-polish ✅** — 2026-05-26 AM0:30（simulator の "電卓レベル" → "実 on-chain データ" 化）
  - `asset_resolver.py` 拡張：`getReserveConfigurationData` を Multicall でキャッシュ
    → 15 reserves 全ての decimals / LTV / liquidationThreshold / liquidationBonus 取得済
    → WETH/USDC/USDbC/DAI/EURC/GHO=5%、wstETH=6%、cbETH/weETH/cbBTC/ezETH/tBTC=7.5%、LBTC=8.5%、AAVE=10%
  - `aerodrome_quoter.py` 新設：`getAmountsOut` ラッパー
    → 実 pool の出力量を eth_call で取得、ETH 価格・spot rate・実 swap 量を取得可能
  - `simulator.py` の 3 つの hardcoded を実データに置換：
    | 項目 | 旧 | 新 |
    |---|---|---|
    | bonus | 0.05 固定 | `reserve[symbol]` per-asset |
    | slippage | 0.003 固定 | Aerodrome 2-quote (tiny vs actual) |
    | gas | $0.10 固定 | `live(gas_price × 657800 × ETH_price)` |
    - source タグ付きで失敗時はフォールバック明示
  - 検証：$1000 cbBTC/USDC で bonus 7.5% / slip 0.15% / gas $0.008 → net $36.70（計算合致）
  - 検証：$10000 WETH/USDC で bonus 5.0% / slip 0.42% / gas $0.008 → net $239.32
  - smoke test 5/5 維持、py_compile 全 OK

### Phase 1d テスト結果マトリクス
| シナリオ | fork block | user / pair | HF | 結果 |
|---|---|---|---|---|
| 異種資産 success | 46,366,653 | 0x8D03 cbBTC/USDC | 0.9941 | ✅ profit $0.29、gas 657,800 |
| 異種資産 healthy refuse | 46,390,341 | 0x8730 USDC/WETH | 1.0015 | ✅ graceful revert: Aave `HealthFactorNotBelowThreshold()` |
| 同一資産（修正後） | 46,366,666 | 0x5088 WETH/WETH | 0.9999 | ⚠ Aave 内部別エラー `0xb629b0e4`（swap-self は回避済、Aave-level 別ガード） |
| Smoke (access ctrl) | n/a | n/a | n/a | ✅ 5/5（owner / vault / rescue ガード）|

### 解決した selector mystery
- `0x930bb771` = **Aave V3 `HealthFactorNotBelowThreshold()`**（最初は我々の UnprofitableSwap だと誤推測していた）
- `0xb629b0e4` = 未特定（Aave V3 同一資産清算で出る）。我々の swap-skip 修正は意図通り動作、Aave-level の別制約に当たっている

### 修正された KNOWN_SELECTORS テーブル（fork_test.js）
- NotOwner() = 0x30cd7471（正）
- NotVault() = 0x62df0545（前回 0xf2d2823a と誤記）
- UnprofitableSwap(uint256,uint256) = 0x24d0319e（前回 0x930bb771 と誤記）
- LIVE 実行のために残るのは：(1) wallet rotation（Master 判断で**スキップ**）、(2) mainnet deploy
- 並走相手 [[imperialflow]] と 2026-12 末に PnL 比較予定

## Roadmap

| Phase | Goal | Status |
|---|---|---|
| 0 | skeleton + dashboard | ✅ |
| 1a | Aave Borrow listener + mainnet 観察 | ✅ |
| 1b | Multicall3 + per-block re-check（**200x 高速化**） | ✅ |
| 1c | Solidity 契約（Balancer flash + Aave liq + Aerodrome swap atomic） | ✅ 基盤 |
| 1c+ | indexer/simulator 拡張：per-asset 内訳特定 + route 構築 | ✅ 2026-05-20 |
| 1d | mainnet-fork integration test（実 Balancer/Aave/Aerodrome 相手に dry-run） | ✅ 2026-05-25 |
| 1d-fix | `coll == debt` エッジケース対応（swap スキップガード追加） | ✅ 2026-05-26 |
| 1e | mainnet deploy（Imperial_MEV wallet 流用、$0.02 gas）| ✅ 2026-05-31 AM6:15 |
| 1f | DRY_RUN=false 切替 + 初 LIVE tx 観察 | ✅ 起動 2026-05-31 AM6:31 |
| 1g | 初の LIVE 発射観察（liquidatable + 採算条件揃い待ち）| ⏳ 自然発生待ち |
| 2a | Aave event listener（logs subscription、skip-list 機構）| ✅ 2026-06-01 AM4:12 |
| 2b | dedicated RPC（mempool 諦め、 latency 改善目的）| ⏭ 1-2週間 LIVE データ後判断 |
| 2c | MEV-Boost bundle 提出 | ⏭ Phase 2b 後 |
| 2+ | mempool listener 復活、Morpho 統合、MEV-Boost bundle 提出 | 計画 |

## モジュール構成
### Python
| File | Role |
|---|---|
| `main.py` | オーケストレータ |
| `config.py` | pydantic 設定（`executor_contract_address` 追加 in 1c） |
| `borrow_event_listener.py` | Aave V3 Borrow イベント polling |
| `liquidation_indexer.py` | Multicall3 で全 user HF 取得 |
| `simulator.py` | 清算 atomic シミュレーション（Phase 0: 概算式） |
| `executor.py` | tx 送信（**1c で LIVE 経路実装**：estimate_gas → sign → send → receipt） |
| `calldata_builder.py` | **NEW 1c**: CypherLiquidator 契約への calldata エンコーダ + Aerodrome route helper |
| `contract_abi.py` | **NEW 1c**: CypherLiquidator の最小 ABI 定義 |
| `asset_resolver.py` | **1c+ → 1d-polish 拡張**: Aave V3 reserves + per-user 内訳 + **per-reserve config（bonus/decimals/LTV/threshold）** Multicall |
| `aerodrome_quoter.py` | **NEW 1d-polish**: Aerodrome Router `getAmountsOut` ラッパー（実 pool から spot/actual quote）|
| `test_helpers/find_recent_liquidation.py` | **NEW 1d**: Aave V3 LiquidationCall ログ検索（fork test seed 探索） |
| `test_helpers/check_hf_batch.py` | **NEW 1d**: 候補 user の fork block HF を archive RPC で一括確認 |
| `test_helpers/check_sameasset_hf.py` | **NEW 1d**: 同一資産候補の HF 確認 |
| `test_helpers/verify_bonus_fetch.py` | **NEW 1d-polish**: 全 reserves の bonus/decimals 一覧検証 |
| `test_helpers/verify_aerodrome_quote.py` | **NEW 1d-polish**: 各 pair の Aerodrome quote 動作確認 |
| `test_helpers/verify_simulator_real.py` | **NEW 1d-polish**: simulator end-to-end real-data test |
| `scripts/fork_test.js` | **NEW 1d**: mainnet-fork で contract integration test |
| `mempool_listener.py` | Base mempool WSS 購読 |
| `telegram_bot.py` | 通知 |
| `dashboard.py` | aiohttp 内蔵 web server |

### Solidity / Hardhat (**Phase 1c**)
| File | Role |
|---|---|
| `contracts/CypherLiquidator.sol` | Balancer flash + Aave liq + Aerodrome swap atomic（owner-only / vault-only ガード、Rescue 関数付き） |
| `contracts/interfaces/IBalancerVault.sol` | Vault.flashLoan + IFlashLoanRecipient |
| `contracts/interfaces/IAavePool.sol` | liquidationCall + getUserAccountData |
| `contracts/interfaces/IAerodromeRouter.sol` | swapExactTokensForTokens + Route 型 |
| `contracts/interfaces/IERC20.sol` | minimal ERC20 |
| `hardhat.config.js` | Hardhat v2.28 + toolbox 6.1（base / baseSepolia / mainnet-fork） |
| `scripts/deploy.js` | デプロイスクリプト（owner = deployer 確定） |
| `test/CypherLiquidator.smoke.js` | アクセス制御＆定数の smoke test |
| `package.json` | npm scripts: compile / test / deploy:sepolia / deploy:base / verify |

## 残課題
- ✅ `executor.py` の実 calldata 組立 → Phase 1c **完了**
- ✅ indexer/simulator 拡張（per-asset 内訳 + Aerodrome route）→ Phase 1c+ **完了**
- ✅ **mainnet-fork integration test** (Phase 1d) → 2026-05-25 SUCCESS
- ~~**wallet rotation**~~：Master 判断でスキップ（既存 hot wallet を継続使用）。**運用上の措置**：profit が出る度に owner wallet からメイン保管 wallet に sweep する習慣を徹底
- ✅ **`coll == debt` エッジケース** (1d-fix): 完了。Aerodrome swap-self は回避できたが、Aave 内部の `0xb629b0e4` で同一資産清算自体は別ガードに阻まれる → 同一資産は実機会から除外する方針に
- ✅ **`0x930bb771` 正体特定**: Aave V3 `HealthFactorNotBelowThreshold()`（healthy user で正しく拒否されていた）
- ✅ **失敗パス検証**: healthy user → Aave が拒否、contract balance 0、no leakage 確認済
- ⏭ **`0xb629b0e4` 正体未特定**: 優先度低（同一資産清算は除外方針なので追跡不要）
- **mainnet deploy** (Phase 1e): Master 承認後、`cli.js run scripts/deploy.js --network base`
  - 事前: `.env` の `EXECUTOR_PRIVATE_KEY` を装填（現在空欄）
  - 事前: その wallet に Base mainnet ETH ~$5-10 入金
- `BASE_WS_URL` 未設定で mempool listener 停止中（任意修正）
- public RPC のレイテンシ 600-1700ms → 本格運用時は dedicated RPC 必須（ImperialFlow の QuickNode 借用は fork test の一時利用のみ）

## 安全設計
- `DRY_RUN=true` デフォルト（tx 送信せず、ログのみ）
- `USE_TESTNET=true/false` で testnet/mainnet 切替（現在 mainnet）
- `MAX_GAS_GWEI=0.1` で abort 閾値
- 専用 hot wallet 使用（メイン保管 wallet と物理分離）

## Paths
- コード: `C:\Users\user\cypher\`
- 設定: `C:\Users\user\cypher\.env`
- ログ: `C:\Users\user\cypher\logs\cypher.log`
- ダッシュボード: http://127.0.0.1:8090

## 起動コマンド
```powershell
# Python ボット
cd C:\Users\user\cypher
.\venv\Scripts\Activate.ps1
python main.py

# Solidity 開発（Phase 1c）
cd C:\Users\user\cypher
& 'C:\Program Files\nodejs\node.exe' '.\node_modules\hardhat\internal\cli\cli.js' compile
& 'C:\Program Files\nodejs\node.exe' '.\node_modules\hardhat\internal\cli\cli.js' test
# ↑ npx hardhat は HHE22 で失敗するため、cli.js を直接叩く
# deploy:
#   ... cli.js run scripts/deploy.js --network baseSepolia
#   ... cli.js run scripts/deploy.js --network base   (wallet rotation 後)
```

## ターゲットプロトコル
| Protocol | Status |
|---|---|
| Aave V3 (Base) | ✅ MONITORING |
| Morpho Blue | ⏸ Phase 1 |
| Compound V3 | ⏸ Phase 2 |
| Balancer V2 (Flash Loan) | ✅ READY |
| Aerodrome (DEX) | ✅ READY |
| Uniswap V3 | ⏸ Phase 1 |
| MEV-Boost Bundle | ⏸ Phase 4 |
| Flashbots Protect | ⏸ Phase 4 |

---
_Updated: 2026-05-19_
