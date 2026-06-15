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

## 2026-06-16 GBP自動返信 実装完了(AUREL直轄・画面共有で会長と協働)
- **Google Cloud設定完了**(画面共有で確認): project=My First Project(project-9dd25b45-96ed-4195-845)。審査クリア確定(My Business Account Management/Business Information/Business Profile Performance APIが有効)。レビュー用Google My Business APIは"許可制の隠しスイッチ型"で一覧に出ない=審査クリアで使用可。
  - OAuth同意画面(branding)構成済(アプリ名LocalBoost, support=ke99089631@gmail.com, 外部)。
  - OAuthクライアント"LocalBoost Web"作成済(ウェブアプリ)。Client ID末尾 ...tkcp.apps.googleusercontent.com。リダイレクトURI=https://local-boost.xyz/api/google/callback。**JSON保存済(会長Downloads)**。Client Secretはチャット非経由(JSON内)。
  - テストユーザー ke99089631@gmail.com 登録済(アプリはTesting状態=登録者のみ連携可)。
- **コード実装完了&commit(88bc088)**: app配下に lib/google.ts(OAuth+GBP REST raw fetch), lib/google-tokens.ts(保存+自動リフレッシュ), api/google/connect+callback, actions/reviews.ts(同期/AI返信案/投稿/解除), dashboard/google-card.tsx(連携ボタン+口コミ一覧UI), page.tsx(仮枠を本物に置換)。既存schema(oauth_tokens/stores/reviews)を利用。`npx next build`成功(TS通過)。scope=business.manage。レビューはv4 mybusiness API(accounts/{id}/locations/{id}/reviews)。
- **本番稼働確認済み(6/16)**: ~~①Vercel本番env追加~~✅ → ~~②git push(88bc088)→Vercel自動デプロイ~~✅ → ~~③配線テスト~~✅完了。会長が本番/dashboardで「Googleと連携」成功(連携中:ke99089631@gmail.com表示)→「口コミ取得・同期」実行→お店未所有のため0件テロップ(=正常な想定動作)。**OAuth連携・トークン保存・同期処理が本番で完動**。
- **GBP機能の唯一の残り = 実物テスト**: 会長は自分のお店(Googleビジネスプロフィール)を持たない=正解(会長は売る側)。口コミは"お店"に紐づくため、AI返信まで含む最終確認は**1人目の契約客(整骨院)のプロフィールを連携した時点**で行う。それまでGBPエンジンは完成・待機状態。
- **本番ログインはパスワードレス(Magic Link方式)**: メール入力→「ログインリンクを送信」→届いたメールのリンクをクリックでログイン。パスワード欄は無い。
- **テスト前提の未確認事項**: 会長がGoogleビジネスプロフィール(Googleマップ登録店舗)を管理しているか要確認。無いと口コミ0件で動作確認できない。

## 制約
お金が動く一歩・本番課金は会長の最終GO。秘密(sk_live/whsec/.env)はgit/出力に絶対出さない。
