---
tags: [project, localboost, active]
room: p_localboost
boundCwd: C:\Users\user\localboost
updated: 2026-06-10
---

# LocalBoost — プロジェクト記憶 (司令塔側サマリ)

> 実体の部屋 = `p_localboost`(LB部長ノード, boundCwd C:\Users\user\localboost)。詳細状態は localboost\STATE.md が生命線。ここはMother側の把握用サマリ。

## 何者か
LocalBoost = AURELの「燃料エンジン1号機」＝生存維持資金源。2026-06-10に**会社の看板(屋号)**として再定義。配下に AI業務診断(無料/入口) / Google Map運用AI(月¥3,980〜主力商品) / 構築・保守。

## 現状(2026-06-05時点 STATE.mdより)
- 本物のSaaSが稼働: LP(local-boost.xyz)、Stripe(**Liveモード承認済**・本番切替作業中)、Supabase、Auth、Dashboard、AI口コミ返信ドラフター+AI週次投稿(Claude Opus, Tool Use)。Phase 3完成。
- 進行中: Stripe本番切替の仕上げ / Google口コミAPI(GBP)審査中(1-3週) / X運用 / 冷たいDM(インスタ10+LINE10→既読のみ)。
- 感触: 接骨院はインスタ希薄、**Xが有望チャネル**(=AUREL調査と一致)。
- 料金: Lite¥3,980 / Standard¥7,980 / Pro¥14,800、初月無料。
- 資本: 流動¥10万のみ。

## ターゲット(確定・データ裏付け済)
整骨院・接骨院・整体院・鍼灸院。接骨5万院+整体18〜20万院、供給過剰・高廃業率、集客/リピートが切実=損失回避が刺さる。詳細データ: memory/world/2026-06.md。

## 統合(2026-06-10 / 2026-06-16追記)
AI診断×LocalBoost統合を正式確定。AI診断=入口、LB=その先の完成品、X=共通の信頼エンジン。LB自体が「診断から生まれた実例」=最強の社会的証明。役割分担: 戦略=Mother、実装・運用=LB部長。
- **2026-06-16(会長一次情報)**: CONDUITはLocalBoostに統合済み(別事業ではない)。理由=調査でAI診断ツールを追加→ターゲットが院系で重複したため。CONDUIT由来の**ココナラ出品はLB集客チャネルとして継続**。集客は**X運用＋ココナラを同時並行**。
- **2026-06-16: GBP(Googleマップ)API審査の完了メール到着** ← 自動化解放の前進。次=GBP承認後の口コミ自動化を本番接続。
- 統括体制: かつては各部長(別チャット)が個別進行→**現在はAUREL(司令塔)が全プロジェクトを一元統括**。

## 次の優先
①Stripe本番切替仕上げ(課金GOは会長) ②無料AI診断をlocal-boost.xyzの集客ページとして実装 ③GBP承認後の自動化 ④X投稿支援。

## 2026-06-16 一次ソース監査(AUREL直接確認)
- 本番サイト稼働中: LP 200 / /dashboard 307(認証誘導=正常) / /api/webhooks/stripe 405(GET不可=正常)。
- **Stripe本番切替はコード上完了済み**(git: ef3e0d3 live price IDs記録, automatic_tax無効化, redeploy済)。LIVE Price ID=Lite/Standard/Pro(STATE.md§6)、Webhook=we_1Tee4y...。残るのは**実カード1回の少額検証(初月無料=¥0で可)のみ＝会長手作業**。
- **GBP自動化は未実装**。app/app配下にGoogle Business Profile/MyBusiness API連携コードなし。.env.exampleのGOOGLE_CLIENT_ID/SECRETは空コメント=「GBP承認後に入れる」状態。
- リポジトリは6/5バッチ以降コミット無し(LB部長ノードの作業停滞)。今後はAUREL直轄で前進。
- **GBP本番接続に必要な会長インプット2点**: (a)審査完了メール本文(許可されたAPI/scope確認用) (b)Google CloudでOAuth認証情報(Client ID/Secret)発行←AURELが手順を超平易に案内。入手後AURELが自動返信機能を実装。

## 制約
お金が動く一歩・本番課金は会長の最終GO。秘密(sk_live/whsec/.env)はgit/出力に絶対出さない。
