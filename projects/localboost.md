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

## 位置づけ確定(2026-06-16 会長一次情報・確定版)
LocalBoost=会社の看板(屋号)。下に2本を**同時並行稼働**:
- **① AI診断 = 入口**(無料/安価, ココナラ等で集客の呼び水)。
- **② 院向け 口コミ返信AI = 本命商品**(月額)。診断の先の完成品。それ自体が「診断から生まれた実例」=最強ポートフォリオ。
- 関係: 診断→本命への流れ かつ 両方を常時並行で回す。CONDUITは②に吸収済み。集客=X運用＋ココナラ同時並行。
- 注: 「ココナラで燃料を稼ぐ」は短期現金の側面表現だが、役割の正は「診断=入口/院向けAI=本命」で2026-06より不変。
- **X運用の現状(6/16)**: ココナラ出品・診断まわりは全て済。X運用は現在**LB(本命②)側アカウントのみ**稼働。**今後はAI診断(入口①)側のX運用も新規立ち上げ予定**=次の集客テーマ。

## X運用エンジン構築(2026-06-17 進行中)
会長方針: Grok(Xの偵察兵/有料)＋Hermès(深く調べる頭脳/無料)＋AUREL(束ねて投稿量産)。狙い=量産だけでなく「伸びてる同業=個人SaaS開発者アカウントの運用法を解剖→LBへ移植」。会長はX Premium加入(Premium+/SuperGrokではない)。標準案A(先に出した告知3案)は「甘い」と会長判断=心理設計/アルゴリズム理解を組み込む方針へ。
- **Grok API**: xAI開発者APIキー取得済(console.x.ai, team=LocalBoost)。HermèsにXAI_API_KEY登録済(status=xAI/Grok✓, 84文字, 値はチャット非経由でクリップボード経由登録)。**ただしチーム残高$0でpermission-denied** → 少額チャージ待ち(会長のデビット決済が一旦不通=カード会社の本人確認待ち。代替=別カード or 後追い)。鍵自体は有効。料金: grok-4.1-fast $0.20/M入・$0.50/M出, X/web検索$5/1000回, 月¥1-2k見込み・無料枠可能性。
- **Hermès**: 完動・無料・web_search稼働確認(levelsio≈89.9万fol取得)。6/17にX運用調査タスク投入(出力先 C:/Users/user/.aurel/state/x-strategy-research.md)。
- 次: Hermès調査結果を受けてX運用プレイバック確定→投稿量産(AUREL作成→会長が投稿クリック)。Grokは残高入り次第Xリアルタイム偵察に投入。
- **2026-06-18 Grok鍵 復旧・稼働確認**: 旧鍵は保存できておらず消失→会長が新規キー作成。受け渡し=会長がメモ帳(新規)に貼付→AURELが開きっぱなしのNotepad TabState .bin(共有読取)から抽出。※printableバイト全拾いでバイナリ付録2字が混入し86字→「Incorrect API key」。末尾2字削った**84字が正**と判明、grok-3で実問い合わせ成功(「Got it!」)＝**鍵・残高(課金)とも有効**。保存=`C:\Users\user\.aurel\state\xai.env`(XAI_API_KEY=, UTF8 BOM無)。`.aurel`はgit管理外で漏洩事故なし。呼出し=xAI直叩き(`https://api.x.ai/v1/chat/completions`, Bearer)。有効モデル例=grok-3。**会長手元のNotepad鍵メモは要削除(loose secret)**。X Live Search=search_parameters(sources x)で偵察可。
- **2026-06-17 Hermès調査完了**: 出力=C:/Users/user/.aurel/state/x-strategy-research.md(2297語)。要点=①返信>いいね(会話誘発が最強)②投稿後30分の初速③最初の投稿に外部リンク貼ると埋もれる(リンクは2投目/返信欄)④型=課題提起→共感→具体→断言→CTA、製品名は最後⑤日本院長向けは"収益ドヤ"でなく時間/評判の悩みに寄り添う。素材=プロフ文/コンテンツ5本柱/フック10本/2週間日割り計画。⚠**LBは顧客ゼロ→架空の導入事例投稿は厳禁(信用喪失地雷)。顧客が付くまでBuild in Public/専門知識に差し替える**。
- **会長の重要指摘(6/17)**: LB側Xは既に1か月運用(投稿多数/リプ・いいね周りも実施)。ゼロから書くより**実アカを先に解剖(伸びた投稿・文体・効く話題を抽出)→心理設計フレームと掛合せ**た方が良い投稿になる。観覧は当面画面共有(Xはログイン要)、将来Grok funded後は自動偵察。

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

## 運営モデル(2026-06-05確定・要約で消えやすい重要事項)
**AURELが全自動で運営する**設計。提案・要件整理・成果物・返信・レポート=全部AURELがさばく(AIエージェント社員で自律運営)。会長の役割≈「レポートを読む→承認/却下→数クリック貼るだけ」。
- **会長の手が要る不変ゲートは2つだけ**: ①ココナラ等への**物理的な送信・公開**(=ログイン情報を自動化に渡さない安全鉄則のため) ②**受注/課金/公開/決済の決裁**。
- 含意: 「全自動」とは“頭脳と作業はAURELが全自動、最後の送信/決裁クリックだけ会長”の意。手抜きや会長運用ではない。Xも同じ=文章・ネタ・戦略はAUREL全自動、投稿ボタンのみ会長(X代理投稿はしない標準ルール)。
- AI診断側Xも同モデルで立ち上げる(=AURELが投稿ネタ・文面を全自動生成、会長が投稿クリック)。

## 2026-06-19 X集客 偵察→テンプレ化(プランA完了・※会長が組み直し予定)
- **Grok X偵察 成功**(`C:\Users\user\.aurel\state\x-recon-grok.md`)。xAI Agent Tools API経由(`POST /v1/responses`, model=grok-4→grok-4.3解決, `tools=[{type:web_search},{type:x_search}]`, `tool_choice='required'`)。**Live Search(search_parameters)は410で廃止済**。
  - 詰まり回避の知見: 巨大1発プロンプト＋検索強制なし=暴走15分ハング。**軽い2発(整骨院系/個人開発系)＋tool_choice=required**だと各19〜55秒で実在ハンドル付き応答。切り離し(Start-Process)はネット呼び出しで固まる→**AUREL直叩き(PowerShellツール)が安定**。
  - PS5.1のUTF-8地雷2つ: ①.ps1内の日本語inlineはANSI誤読でmojibake→日本語(プロンプト/見出し)は別UTF-8ファイルから`[IO.File]::ReadAllText(...,UTF8)`で読む。②応答は`Invoke-WebRequest -UseBasicParsing`＋`[Text.Encoding]::UTF8.GetString($resp.RawContentStream.ToArray())`でデコード(IRMだと文字化け)。スクリプト群=`grok_recon3.ps1`/`grok_recon_prompt.txt`/`grok_titles.txt`/`grok_diag*.ps1`。
  - 偵察の核心: 両ジャンルとも「自慢」でなく「悩みズバリ→具体数字→次の一歩」で伸びる。整骨院系実在例=@kamen___writer/@meo_goto/@siro111323/@yuzukuri5。勝ちフック=「Googleマップで上位なのに予約が入らない」型。アンチパターン=**サクラ口コミ/★操作(医療広告ガイドライン違反リスク)**・抽象論・単発。個人開発系=@levelsio/@tdinh_me等、Build-in-Public(収益/失敗の正直公開)。
- **Hermès心理フレーム既存**(`x-strategy-research.md`): フック→共感→具体→断言→CTA／返信はいいねの27倍／投稿後30分初速／リンクは2投稿目／毎日同時刻+40%。※ただし**架空の導入事例・効果保証を多用**=顧客ゼロでは使用不可。
- **統合テンプレ作成**(`C:\Users\user\.aurel\state\lb-x-templates.md`): 心理フレーム＋アルゴリズム術は採用、**架空実績は全部Build-in-Public(作っている過程の実況)に置換**。プロフ文/5本柱(主役=作っている過程)/即投稿フック10本/完成テンプレ2本/1週間リズム。**顧客ゼロ→導入事例・お客様の声は封印、★操作禁止明記、文章AUREL・投稿ボタン会長を厳守**。
- **状態: 会長が「LBについて伝えたいことがある→組み直したい」と保留。上記は土台として保存、方針転換待ち。**

## 制約
お金が動く一歩・本番課金は会長の最終GO。秘密(sk_live/whsec/.env)はgit/出力に絶対出さない。ログイン情報は自動化に渡さない(物理送信は会長の手)。
