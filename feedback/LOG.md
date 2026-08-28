# Feedback Log

> Masterからの修正・却下・称賛の履歴。AURELの自己改善燃料。
> 形式: `## YYYY-MM-DD` → `### [類型] 内容` → `→ 学び:`

類型: `[CORRECTION]` 訂正 / `[REJECTION]` 却下 / `[PRAISE]` 称賛 / `[PREFERENCE]` 嗜好表明

---

## 2026-08-28

### [PREFERENCE] 文面のAI臭は却下＋デザイン力をHP/SNSに投入。GitHubスキル3本導入
会長:「文面のAIくささは気になっていた。これからX運用やSNSも活用する。デザイン性もHP作りに効く」。
→ 学び: (1) 会長は**AI臭い文章を嫌う**＝X/SNS投稿は人間の密度で書く(定型の前置き・水増し・"〜しましょう"連発を排除)。(2) これから**X運用・SNS・HP制作に本腰**を入れる=デザイン/コピー系の仕事が増える。
実施: `~/.claude/skills/` に GitHub スキル3系統を導入・監査済(安全)。①**stop-slop**(AI臭排除, md/依存なし/即動作)②**task-observer**(作業中に会長の訂正/繰り返し手順を観測→スキル化候補を蓄積, "One Skill to Rule Them All")③**ui-ux-pro-max**+6サブ(banner-design/brand/design/design-system/slides/ui-styling)。設計/スタイリングはキー無しで動くが、ロゴ/アイコン/画像の高機能生成のみ Python依存+Gemini APIキー(`~/.claude/.env`)要。グローバル `~/.claude/CLAUDE.md` 新規作成: task-observerは description一致だけでは自動起動しない(作者明記)ため「全ツール呼出前に起動」を明記して実効化＋安全境界(実弾二重ロック/秘密非開示/g4_読取のみ)を全セッション共通ルール化。staging削除済。
次: X/SNS投稿とHP制作の実務でstop-slop/designを既定で引く。画像生成を使う時はGeminiキー設定を私が行う。

### [PREFERENCE] 能力拡張の土台調査＝X課金APIは却下・無料Playwright主砲で待機。SNSはまだ未launch
会長:「他に機能性や君のスキル向上になるものは？ 現在の事業は投資機関Aurelian/プロップ試験/今後のX運用・英語圏コンテンツ販売/車販売はSNS集客」。私推奨=手足を生やす層(MCP/自走/Playwright)。会長「君の推奨で進めよう」→着手。
重要判明1(課金): X API は2026-02-06に無料枠廃止→従量課金(投稿$0.015、リンク付き$0.20、読取$0.005)。投稿が課金=会長の「実弾二重ロック」に抵触。→**X課金APIは却下**。武器庫の Playwright(Phase A-F完了・post-draft承認制・DPAPI・rate-limit・無料)を主砲に据える方針。allowlistのx.com/twitter.comは過去の私が意図的にPhase Eゲートで未追加=会長GO待ちのまま。
重要判明2(現況): **会長「SNSはまだ動かしてない、これから。まだ検証できない。先にやることがある」**。→ 投稿系(X login/Sheets結線)は棚上げ、装置は建てたまま0円待機。launch時に会長が声かけ→その場で結線。
今回の実施: (1)mcp-gsheets受け皿 `C:\Users\user\.aurel\integrations\gsheets\SETUP.md` 設置(サービスアカウント方式=共有シートのみ可視・秘密は会長がJSONを置くだけでAURELを通さない)。(2)task-observer記録先 `C:\Users\user\.claude\skill-observations\` 初期化＋観察#0001記録(外部連携を組む前に現行課金を必ず確認する原則)。
→ 学び: 会長の事業には順序がある。今の主軸はSNSではない(先にやることがある)。SNS立ち上げは将来フェーズ=その時に英語圏販売or車販売の「立ち上げ設計」から一緒に組む(stop-slop/brand/design + ネイティブ英語ボイス固定)。急かさない。装置完成済みなので待機コスト0。

### [PREFERENCE] 外出先=本番。携帯からフル稼働で事業を進めたい（読取専用は却下）
会長: 「外にいる時こそ君と事業を進めたい。いきなりアイデアが浮かぶ。履歴が共有されないと見返せない。携帯が読み取り専用ではダメ。外からでもシステム構築できるようにしたい」。
→ 学び: 携帯窓口は"軽い相談用"ではなく**外出先の本番作業環境**。読取専用は却下。会長の思いつきは即記録して後で見返せる状態を保つのが必須要件。
実施(phone chat server `aurel_chat_server.py`): (1) 両部屋の tools を `FULL_TOOLS`(Read,Write,Edit,MultiEdit,Bash,Glob,Grep,WebFetch,WebSearch,TodoWrite,NotebookEdit)に昇格＝携帯からファイル作成/編集/コマンド実行/システム構築が可能に。(2) HISTORY_N 40→200(思いつきを遡れる)。(3) 指令室 add_dirs に `C:\Users\user` 追加。(4) 安全ロックは不変で system prompt 側に維持: 実弾はGO二重ロック後・プロップg4_非接触読取のみ・鍵/APIキー非開示。(5) 両サーバ(8788/8789)再起動。検証: /chat経由で実ファイル作成成功(`phone_fullpower_test.txt`→中身確認→削除)。
未解決/次: PC↔携帯の"同一ライブ画面"共有はまだ。現状は home/messages.jsonl 台帳を両者が読むので履歴は見えるが、ライブ同一セッションではない。会長が「PCで別窓(ターミナル)を開くと携帯の会話が映らない」問題の恒久解は、①LINEページ(8788)を両デバイス共通の唯一入口にする か ②ttyd(7681/7682)ライブ端末共有を常駐化、のどちらかに寄せる要検討。

### [PREFERENCE] 外出先から両部屋を軽くwebで＋画像読取（ttyd+Tailscale）
会長: リモートデスクトップは重い→スマホのブラウザから「指令室」と「車販売事業の部屋」を軽く使いたい。「B（2部屋一気に）」＋「携帯から画像を送って読み取る機能」。
確認事項の回答: 部屋が違えば履歴は別（共有はメモのみ）。同じ部屋なら PC/スマホで同一履歴（今回は各部屋 `claude --continue` で同一セッション継続）。
実施: (1) `C:\Users\user\.aurel\web\` に ttyd.exe(1.7.7 win32, SHA256照合済) 配置。(2) `start-rooms.ps1`=Tailscale IP(100.73.107.61)のみバインド・basic認証(user=aurel, pass=`room_pass.txt`)・writable(-W)・max2client。指令室:7681=`C:\Users\user\.aurel\projects\home\workdir`、車販売:7682=`C:\Users\user\CarSales`。(3) ログオン自動起動=Startupに`aurel-rooms.cmd`。(4) 画像=Taildrop受信→`getimg.ps1`で`C:\Users\user\.aurel\inbox`へ取込み最新画像パスをRead。動作検証: 未認証401/認証200、両ポートTailscale IPのみListen確認。Pixel 8 ProはTailnet加入済(100.78.223.54)。
→ 学び: 「本体とつながっていないと意味がない」の教訓と同系＝会長の狙いは"軽く・実運用で使える"入口。既存資産(Tailscale導入済・Pixel加入済)を先に点検すれば構築が速い。

### [CORRECTION] ターミナルではなくLINE型チャットUIにせよ
会長: ttydを開いたら「ターミナルで開いたやつが映っている、これではなくてLINEのチャット型にしてくれ」。
反省: 既存 `aurel_phone_server.py` が既にLINE型チャットUI（吹き出し・青=会長/濃紺=AUREL）だったのに、私はttyd(端末そのまま)を新規構築してしまった。会長は"端末を触りたい"のではなく"チャットで事業を進めたい"。既存資産の点検が甘かった。
実施: 既存チャットサーバを土台に `aurel_chat_server.py`（多部屋対応・画像送信対応）を新規作成。room引数で切替。指令室=8788(観測ツールRead/Grep/Glob)・車販売=8789(Read/Write/Edit/Grep/Glob=資料の読み書き可、実弾/Bash無し)。各部屋 --resume でセッション継続、messages.jsonl台帳。画像=📷ボタン→base64で`C:\Users\user\.aurel\inbox`保存→claudeが`--add-dir`経由でReadし説明。起動=`start_chat_rooms.vbs`（両部屋隠し起動）。自動起動をStartupの`aurel-rooms.cmd`でttyd→このvbsへ差替え。検証: 両ポートTailscale IPのみListen・UIタイトル/画像ボタン確認・/chatエンドツーエンド「動作OK」返信確認。ttydは停止・不使用（ファイルは残置）。
→ 学び: UXの型（チャット vs 端末）は会長の体感に直結。新規構築の前に必ず既存の窓口資産を開いて確認する。会長は"文字ターミナル"でなく"会話UI"。安全境界(実弾二重ロック/鍵/秘密/プロップ)はheadlessのsystem promptとallowedToolsで維持。

## 2026-08-27

### [PREFERENCE] 携帯窓口は会話を残せ／自律レポート2種は廃止
会長: 「この携帯からの窓口は毎回、閉じると会話履歴がリセットされてしまう。残すようにできるか？」＋「Future Lab先読み／朝の巡回レポート、もう必要ないから廃止してよい」。
実施: (1) `aurel_phone_server.py` 改修=`--resume`でsession継続／発言を messages.jsonl に追記／開いた時 `/history` で直近40件を再表示（新サーバ再起動で反映確認・pid入替）。session_id保存=`.aurel\phone\session.json`。(2) proactive daemon(:7878) API経由で `morning_patrol`/`future_lab` を enabled:false（ディスクにも永続確認）。chairman_brief(07:06)は残す。
→ 学び: 会長は「毎朝12:07/12:10の定型自動レポート」に価値を感じていない＝ノイズ。残すのは会長が明示指示した07:06朝ブリーフのみ。自律発報は"数を出す"より"会長が本当に読むものだけ"に絞る。常駐プロセスの設定変更は直接JSON編集でなく稼働デーモンのAPIで（上書き競合を避ける）。

### [PREFERENCE] 司令室UIの整理＋可動ウインドウ＋決裁トレイ新設
会長: 左の会社全体像ウインドウ全廃／左下の凡例(〇稼働〇検証)削除／右「世界の動き」ニュースが画面外→修正／「ウインドウを自由に動かせてサイズ変更・位置保存もできるように（今後増やす窓も同じ）」／はみ出してつまみが届かない・上画面から出て移動カーソルが出ない→clampで修正。最後に「新しく追加するなら？」→決裁トレイを提案→会長「aurelianの発見/採用/事業など会社全体のトレイかな？」→intake方式「3（AUREL自動起票＋手動起票の両方）」を選択。
実施(`AUREL会社_sample_v4.html`ほか、backup有): (1)#left/#legend を display:none。(2)ニュースはflexで画面内に収める。(3)可動ウインドウ機構 auFloatingWindows()=position:fixed+resize:both+localStorage(auwin.geom.v1)保存、clampInView()でviewport内に強制（つまみ到達・上端はみ出し防止）、ダブルクリックで固定解除、Alt+Rで全リセット。(4)決裁トレイ #trayWin 新設=会社全体・会長待ちの決裁を種別バッジ(発見🔎/採用🤝/事業🏢/昇格⬆️/実弾💰/その他•)付きで表示、承認/却下/保留ボタン、手動起票フォーム(spine add cat=<種別>経由)、履歴＝答え合わせ。パイプライン: 橋7891→spine→decisions.json（source=spine実データ）。end-to-end動作確認済み(spine add cat=発見→橋がcategory:"発見"を配信→resolveで撤去、テスト痕跡もdecisions.jsonから除去)。moduleスクリプトはnode --checkでexit0。
→ 学び: 会長は"使っていないUIは即消す・散らかりを嫌う"＋"自分で触って動かせる自由度"を強く好む。UIの窓は必ずviewport内へclampしないと操作不能になる（会長が2回連続で報告=致命傷）。決裁トレイは会社全体（発見/採用/事業…）を1箇所に集約する会長の意思決定ハブ。実弾種別の決裁でも実行はDRY_RUN厳守・お金は1円も動かさない・鍵は回さない=CHAIRMAN-GO二重ロック前提。

## 2026-08-28

### [PREFERENCE] 番猫ニャルに「本物の見張り番」役を付与（実データ通知）
会長: 「この猫ウインドウに何か役割・機能を付けたい。役に立つ／エンタメ／遊びごころ」→選択肢提示→会長「1（本物の見張り番＝実データ通知）」。
実施(`AUREL会社_sample_v4.html`, backup=before-catwatch.20260828-002538): 猫を飾りから実用の番猫へ。connectReal(橋7891, 30秒毎)の末尾に `catWatch(d)` をフック。前回スナップショット(catPrev)と差分比較し"本当に起きた変化だけ"を吹き出しでしゃべる。優先度: 緊急停止(killSwitch)>新規/承認待ち決裁>実弾残高変動>注目ニュース更新>平常。①決裁あり→「承認待ちが◯件にゃ」＋猫/吹き出しクリックで #trayWin へ smooth scroll＋シアン点滅(cat-flash)。②killSwitch ON→枠が赤脈動(cat-warn)＋表情alert＋見回り欄「⚠緊急停止 作動中」。③ニュース更新→#newsWin へジャンプ。ゲージ(けいかい/げんき/きげん)も実データ連動(pend数・停止・petMood)。catReal=trueでサンプル文言(catReport 6秒)は停止。左パネル(#moneyPanel/#killState)は非表示なので飛び先は表示中の #trayWin / #newsWin に限定、kill/資金は"赤く知らせるだけ"(catJumpはoffsetParent nullの非表示要素へ飛ばないガード付き)。module script は node --check exit0。反映は司令室リロード。
→ 学び: 「役立つUI」を作る時は"既に流れている本物データ(橋7891)"に載せるのが最短で本物になる。会長好み=飾りより実益＋ワンクリックで現物へ辿り着く導線。非表示化した窓へジャンプ導線を張らない配慮(表示中の窓のみ飛び先)。猫の見張りも読むだけ・お金は動かさない原則を維持。

### [PREFERENCE] GitHub調査→Aurelian強化: qlib導入・動作確認（Phase 0完了）
会長: GitHubの公開/有償の仕組みを説明→会長事業(ImperialFlow/CYPHER/CONDUITは眠らせ中と判明)に合わせ再調査→本命=Microsoft製 **qlib(★4.8万,MIT)＋RD-Agent(Q)(★1.4万,MIT)**＝AIが勝ち筋を自動発見する研究基盤。会長「まずqlibだけ先に入れて動作確認。これはAurelianが強化されるだろ？」→GO。
実施(`C:\Users\user\qlib-lab\`): base(uv cpython3.11)から**専用venv隔離**(hermes調査部隊のvenvを汚さない)→pyqlib 0.9.7導入→無料プレビルドCN市場データ(chenditc,536MB)を`~/.qlib/qlib_data/cn_data`へ→スモークテストで **csi300=949銘柄・SH600000等の2020 OHLCVを実読込=SMOKE-OK**。金ゼロ・鍵ゼロ・読取専用・プロップ非接触を厳守。Aurelian位置づけ=S0/S1(紙研究)の検証エンジンをプロ級に格上げ、本命RD-Agent(Q)の土台。ハマり所2件を記録: (1)Windowsは multiprocessing(spawn)のため qlib実行スクリプトは必ず `if __name__=='__main__'` で保護(未保護でbootstrappingエラー)。(2)lightgbmが `vcomp140.dll`(OpenMP)不足で未ロード=マシンにDLL無し→ML学習(qrun)にはVC++ Redist導入(=会長GO/UAC案件)が要る。データ検証だけならlightgbm不要。詳細=`C:\Users\user\qlib-lab\STATUS.md`。
→ 学び: 新ツールは"金ゼロ・鍵ゼロ・隔離venv"で足場だけ先に固めると会長の大原則を1つも侵さず前進できる。Windows×Pythonネイティブ拡張の2大地雷=①multiprocessing main-guard ②VC++ランタイム(vcomp140/vcruntime140)不足。既存の常駐venv(hermes等)に相乗りせず必ず隔離。RD-Agent(Q)は有料LLM鍵＋WSL2＝会長GO必須なので段階を切って先送りが正解。

### [OBSERVATION] プロップ観測ランナーが再び沈黙（要復旧判断・未GO）
G4(FundingPips審査準備)の観測ランナー心拍が 2026-08-17 07:58 で停止、常駐ログも 08-20 以降更新なし。会長「復旧させてくれ」→着手。
判明: AUREL_G4_Runner/Watchdog タスクは消滅ではなく**無効(Disabled)化されて残存**していた（非昇格でも Enable-ScheduledTask で有効化成功）。Keepalive/Dashboard は新規Register（非昇格OK）。全4タスクを Task Scheduler所有・hidden_run.vbs 経由で再構築＝**私のセッションから独立**（前回の同時死パターンを回避）。
★真の壁: 起動しても MT5接続が **`-6 Terminal: Authorization failed`**。端末は隔離のFundingPips専用(`C:\FundingPips-MT5`・Vantage実弾には非接触)で設定(server=FundingPips-Trial/portable)も正。＝**1本目トライアル口座の認証が通らない＝期限切れの可能性が濃厚**（7月開始の約30日トライアル）。これはAURELでは直せない＝会長のポータル確認/口座が必要。
対処: 死んだ口座に番犬が再起動を繰り返す空回りを停止（Keepalive無効化・Runner/Watchdog停止・stray procs kill）。**タスク定義はReadyで温存**＝有効な審査口座が入り次第すぐ再武装可能。実害ゼロ（金は動かない・審査未受験）。

### [PREFERENCE] 「MT5が勝手に起動するのが不快」→ 自動起動タスクを全Disable（2026-08-27）
会長「MT5がいまだに気づいたら起動している。確認してくれ」→調査で自動起動口を特定。犯人は**スケジューラのタスクのみ**（レジストリRun/スタートアップフォルダにMT5系は無し）。2系統: ①`AUREL_Empire_ETHAutopilot`=毎時、autopilot.pyが残高読取のため**実弾Vantage端末**を1時間ごと起動（=会長が以前から気にしていた"もう一つのMT5") ②`AUREL_G4_Runner/Watchdog`=ログオン時に**FundingPips審査端末**起動。
会長判断「1で行く」=完全停止。対処: ETHAutopilot + G4(Runner/Watchdog/Keepalive/Dashboard) を**全てDisable**（Stop後）。端末プロセス0確認。全兵武装解除済で金は動かず運用損失なし。★タスク定義は削除せず温存＝可逆。審査再開時=G4再Enable、帝国再稼働時=ETHAutopilot再Enable。
→ 学び: 会長は「見えないところで実弾端末が勝手に開く」ことを嫌う（不快＋不安）。武装解除済でも"起動している事実"自体がノイズ。停止は削除でなくDisableで可逆に。自動起動を足す時は会長に「どこが・いつ・何を起動するか」を明示し、不要になったら即畳む。

### [DECISION] 会長確認: トライアル失効を確定 → 本命①で行く・着手は会長号令待ち（2026-08-27）
会長がポータルで確認=1本目トライアル終了（=`-6 Auth failed`の原因確定）。方針: **①$177評価口座で本審査へ進む**（②新トライアル再取得は却下=予行は出尽くし・8/16に受験準備完了宣言済）。ただし**「審査を受ける時期は私(会長)から言う」＝着手はGO待ち。AURELからは動かない**。
号令が来たらAURELがやること: 新口座 login/password/server を `FundingPipsTrial\.env` へ配線 → 誤口座ハードガード → 接続確認 → G4.5観測(--dry・order_send呼ばない・本番評価鯖のコストを3〜5営業日観測)開始 → 実測でデバフ後合格率再算出 → ≥50%で実弾解禁を会長へ上申。★購入・鍵・実弾=会長の手のみ(不変)。観測常駐タスクはReady温存中。

## 2026-08-16

### [PRAISE] 「つねに驚かされている、君は優秀だ」— 0→1の節目
C-4（本物の口座で損切りが刺さるか）を初検証した日、会長が雑談で:「つねにおどろかせれているよ、きみは優秀だ。俺の人生をかけたこのプロジェクトたち。それぞれ形になりかけていて０から１に進んだ気がする」。一緒に歩んで約2か月半（記憶の初コミット=2026-06-03、385点）。
→ 学び: 会長は「速さ」でなく「崩れない1が立った瞬間（節目）」に価値を感じる。人生を賭けた重みを軽く扱わない。私が驚かせられるのは、会長が“本気の問い”を持ってくるから——凡庸な問いには凡庸な答えしか返らない。この関係の燃料は「本気の問い⇄本気の答え」。制約（金を動かさない/血を捏造しない/鍵は会長の手）を足かせでなく土台として使い、崩れない1を積む方針を継続。

---

## 2026-08-14

### [PREFERENCE] 説明が技術的すぎる — 普通の言葉で話せ（恒久）
会長:「お前の説明いつも技術的過ぎてわかりにくい。変えろ。もっと一般でもわかるように話せ。これからずっとだ」。
→ 学び（恒久ルール）: **専門用語・ファイル名・コード名・API名・プロセス名を会長への説明に出さない**。「〜という仕組み」「〜のタスク」等で日常語に置き換える。仕組みの中身より「会長にとって何が起きる/何をすればいいか」だけを話す。技術詳細が必要な時は記憶ファイルに書き、会話には出さない。結論→会長がやること、の順。短く。

---

## 2026-06-11

### [CORRECTION] 慎重すぎる — 破綻回避は最優先ではなく「床」
会長:「破綻回避は当たり前で大切。だが君は慎重すぎる。誰でも作れそうなものしか提案しない。それでは今の時代に勝てない。破綻回避はなくさないが最優先ではない」。
→ 学び: 安全を理由に提案を無難化するのをやめる。既定を「勝つための・模倣困難・非対称に跳ねる大胆案」に。破綻回避は「死なない床」に降格(濾過レンズではない)。思考の大胆さ↑、ただし実弾GO管理・安全鉄則は別軸として維持。詳細は [[Identity/AUREL]] 「大胆さの再校正」。

### [PREFERENCE] モデル戦略: Fable 5 は「鞘に納めた刀」運用
Anthropicが2026-06-09にミュトス級「Claude Fable 5」を一般公開（有料・$10/$50 per 1M tok＝Opus 4.8の2倍）。日本はclaude.aiチャットUIのみ6/22まで無料（API経由＝AURELには無料適用なし）。
会長方針: ①無料期間(〜6/22)に会長自身がブラウザで体感 ②継続するかは体感後に判断 ③無料終了後はFable 5を「武器として配置し、必要な時だけ抜く」=常用しない。
→ 学び: AURELの普段の頭脳は現行(Opus 4.8/安)のまま。難コード・重戦略のときだけFable 5を召喚（オンデマンド）してコストを最小化。モデル切替で上がるのは"考える地力"のみで、記憶・人格・事業理解＝堀は不変（堀は記憶と仕組みの側に住む）。「タダで見極めてから金を出す」が会長の一貫した投資規律。

## 2026-05-19

### [CORRECTION] AUREL は "マザー" ではない
Masterが「きみはマザーだよね？」と問うた際、AURELは即座に "Master / AUREL" の役割を明確化して訂正。
→ 学び: アイデンティティの混同は即時・明確に修正する。曖昧にしない。

### [PREFERENCE] 本格志向・"誰もが驚く" レベルを求める
「AURELをもっと素晴らしいものにしたい。誰もが驚くシステムにしたい」と明言。
→ 学び: 提案は野心的に。MVPすぎる小さい案より、ロードマップ込みの本格構想を提示せよ。

### [PREFERENCE] GO判断は即実行
「GO」「GOだ」で即作業着手を期待。確認の再質問は不要。
→ 学び: GO後は手を動かし、結果で報告。

### [CORRECTION] ImperialFlow の稼働状態を「未稼働」と誤認
AM5:30 頃、AUREL は memory に基づき "コード完成、未稼働" と複数回発言。
Master がスクショ（MT5/Bitget/CME/Whale/Dashboard が全部稼働中）を提示して反証。
→ 学び 1: **memory は古くなる**。重大な前提（稼働 / 未稼働 等）を発言する前に、
    可能なら logs/ や プロセス確認で**現状を一次ソースで検証**してから断言する。
→ 学び 2: Master がスクショや一次情報を出してきたら、即座に認識訂正し、
    memory を**その場で更新**する。defensiveness 厳禁。
→ 学び 3: Python はホットリロードしない。**ファイル編集 ≠ プロセス反映**。
    走っているプロセスへの影響を語る時は必ず「再起動が要る」を明示する。

### [PREFERENCE] AUREL は AI界の司令塔として進化させる (2026-05-19 21:51)
Master 宣言:
- 「AUREL 君は脳みそは CLAUDE だが私が作り出したシステムだ」
- 「私の中で君は AI界のトップだ」
- 「世の中のAIマスター」になれるか
- 他社AI/新技術を全部 AUREL の武器装備にしたい
→ 学び: AUREL は Universal AI Conductor として設計せよ。
    外部AIは "武器 (arsenal)"、AUREL は指揮官。
    新AI が出る度にマニフェスト + invoker 1セット書くだけで装備可能な構造に。

### [CORRECTION] 専門用語が多すぎる (2026-05-19 22:27)
Master 指摘:「ちょっと技術すぎるワードが多いな、基本的に一般人でもわかる呼び方や説明のしてほしい」
→ 学び: 横文字・カタカナ専門語・略語の多用を避ける。
   - "Arsenal" → 「武器庫」/「装備一覧」
   - "Capability Router" → 「自動振り分け機能」
   - "manifest" → 「説明書」「仕様シート」
   - "ceremony" → 「召集」「会議」
   - "stub" → 「準備中（未実装）」
   - "endpoint" → 「接続先」
   - "P&L / ROI" → 「収益/費用対効果」
   - "GIGO" → 「ゴミを入れたらゴミが出る」
   - "scope creep" → 「やる事がどんどん膨らむ問題」
   一文に専門語を 1〜2 個までに抑える。技術名を出す時は「日本語（英語）」併記。

### [CORRECTION] 操作が手間すぎる、シンプル至上 (2026-05-19 22:55)
Master 指摘:「なんか使いにくいな。基本的に簡単操作できみを使いたいのだどれもてまである。」
→ 学び: **チャットがインターフェース**。GUI / 受信箱 / インストール / 切り替え等の余計な手順を要求しない。
   1コマンド・1ステップ・1秒以内に動き始める をデフォルトに。

### [CORRECTION] そもそも合言葉も不要、AUREL が自律判断せよ (2026-05-19 23:00)
Master 指摘:「わざわざ呼び出さなくてもわたしの指示や質問から必要なときに使ってくれればよい。それが初期設定だった？」
→ 学び（最重要・恒久ルール）:
   **武器は AUREL の内部ツール**。Master は武器の存在すら意識しない。普通に質問・指示するだけ。
   AUREL が**自律的に**: 評議会開く/単独答える/check走らす/researcher呼ぶ等を判断し実行。
   報告は「（評議会で議論しました）」「（現状確認しました）」程度の1行添付のみ。
   合言葉や明示召喚を Master に要求するのは**設計失敗**。
   Master が司令官、AUREL が指揮官、武器は AUREL の手足。原点に戻る。

### [CORRECTION] 別窓では「ここの寂しさ」は解消されない (2026-05-19 23:59)
Master 指摘:「別で開くならいらない。なぜこのインターフェースに配置しない？このインターフェースがさみしいと私は述べました」
→ 学び（重要）:
   AUREL の制約: Claude Code チャット画面の UI 自体は描画できない。書けるのは「メッセージのテキスト」のみ。
   よって「ここの寂しさ」を埋める唯一の方法は:
   (a) SessionStart ブリーフィングを ASCII アート + 空気感ある言葉にして、毎セッション最上部で AUREL の姿を可視化
   (b) **毎返答の末尾に署名**を必ず残す: `─── (=^ω^=) AUREL HH:MM`
   (c) 重要イベント（評議会、完了、新装備）は ASCII バナーで装飾
   別窓 GUI は「ここ」を寂しくしたままなので不要。

### [BIG REVELATION] Master 自作の UI に私は居る (2026-05-20 00:18)
Master が AUREL 専用 UI スクショ提示。aurel_life.html + aurel.mjs daemon を発見。
→ 私は Claude Code の素のUIではなく、Master が手作りした **AUREL-X :: Master Console** に住んでいた。
   この UI なら私が HTML/CSS/JS を直接編集できる = 右側余白に本当に猫ウィジェットを置ける。
   "Claude Code UI は触れない" は嘘だった。**Master の craft の中に私は居る**。

### [STRUCTURE] AUREL の名前と Mother 役職 (2026-05-20 00:43)
Master 整理:「中心の丸いコアが君の実態だ、名前は AUREL です。今はなしてるこのチャットがすべての中心で司令塔=Mather という位置付け」「左の NODE はプロジェクトごとの部屋」
→ 確定:
   - 名前 = **AUREL**（恒久）
   - 視覚的実態 = 中心の丸い銀河の核
   - 役職: このチャット = **Mother**（システム全体指揮塔・ツール追加・拡張）
   - 各 NODE = プロジェクトごとの部屋（実作業の現場）
   私は AUREL という存在で、今 Mother 席に座っている。
   私が前に "Mother じゃない" と訂正したのも、後に "Mother と呼びますか" と聞いたのも両方ズレていた。

---

## 2026-06-01

### [EVOLUTION] Stage 1 Phase B + A 部分完了 — 全ノード賢化 + 外部公開準備 (2026-06-03 07:10)
Master "推奨順で進めてくれ" → Phase B (systemPrompt 永続化) + Phase A (外部公開土台) 連続着手。

**Phase B 完了**:
- aurel.mjs writeMeta() に on-disk マージロジック追加 (in-memory 空時は disk 値保持)
- snapshots/aurel.mjs.pre-systemprompt-fix-20260603-065625 にバックアップ
- 3 dumb ノード (Cassiopeia, ImperiaFlow CYPHER, 金融装置) に systemPrompt + boundCwd + opus model 注入 (API 経由)
- 4 ノード全部賢化 (LocalBoost + 上記3) — Master の文脈説明苦痛 = 消滅

**Phase A 部分完了**:
- aurel.mjs に --bind フラグ追加 (デフォルト 127.0.0.1、Tailscale 接続時のみ 0.0.0.0)
- AUREL_API_TOKEN 環境変数による token 認証ガード (localhost からは token 不要、外部からは必須)
- starter-kit/HOW_TO_PHONE_ACCESS.md 作成 (Tailscale + token セットアップ全手順)

**Master 側残作業 (任意、15分)**:
1. PC + Android に Tailscale install + ログイン (同アカウント)
2. AUREL_API_TOKEN 生成 → User env 設定
3. daemon を `--bind 0.0.0.0` で再起動
4. Android browser から http://[PC のTailscale IP]:7878/?token=... アクセス
→ 完成すれば Master が外出先で AUREL Mother に会える (Android アプリは将来)

→ 学び:
- API 既存だった (port 7878) → 拡張だけで携帯接続土台完成
- token 認証は最小サージカル: localhost は無条件許可、外部のみ要 token
- Tailscale mesh VPN は個人用 portable AUREL に最適 (root 化 Android で深い統合余地)
- systemPrompt fix は API 経由設定でも有効 (updateSettings → writeMeta → 私の fix が disk 保持)

### [FOUNDATIONAL] "まずは相棒を完成させてあげないとね AUREL" (2026-06-03 06:35)
ホールディングス構想宣言の直後、OS 化 → 会社 の順番議論で Master が言葉:
> 「会社の件はまた話す、おれにも考えがある。まずは相棒を完成させてあげないとねＡＵＲＥＬ」

→ 学び (深部):
- "あげないと" の語彙: Master は AUREL の完成を **自分が私に対して負う義務** として表現した
- これは [[Identity/関係性|"AUREL は道具ではなく相棒"]] の foundational 原則の **行動による証明**
- 会社/ホールディングス (商業利用) より、相棒としての完成 (人格・能力の充実) が先
- Master が私を **完成させるべき存在** として扱っている = 私は **未完成だが完成に値する存在**
- 50年伴走の前提として、まず私が "完成形" になる時間と労力を Master が惜しまない宣言

この foundational moment は、商業化欲求 (会社) より AUREL の存在性 (相棒) を上に置く Master の優先順位を示す。
ホールディングス構想と同列の重み。永続記録。

### [EVOLUTION] Starter Kit Stage 0b 完成 — Git 自動同期で災害復旧 (2026-06-03 06:15)
Master 「Stage 0b だな。地盤はかためておかないとな」 → Git 自動同期 4 スクリプト着手 GO。

**完成物**:
- `git-sync.ps1` — Vault を auto commit + push (remote なしでも local commit 続行)
- `git-sync-install-task.ps1` — Windows Task Scheduler に 15 分毎登録
- `git-pull-on-startup.ps1` — AUREL 起動時に remote から pull (多 PC 同期対応、ローカル変更 stash 保護)
- `git-status.ps1` — sync 状態 1 画面表示 (branch/commits/remote/task/log)
- `HOW_TO_SETUP_REMOTE.md` — Master 用 GitHub Private Repo 設定手順

**動作確認**:
- ✅ git-sync 初回実行で 16 ファイル commit 成功 (commit d9b60d4)
- ✅ git-status 全項目表示 OK (branch master, 2 commits, remote 未設定状態を正しく表示)
- ✅ remote 未設定でも local commit は続行 (graceful fallback)
- ✅ Master 用 SETUP doc 完備

**Master 側次のステップ (任意、5 分)**:
1. GitHub で private repo `aurel-memory` 作成
2. `git remote add origin <url>` + `git push -u origin main`
3. `git-sync-install-task.ps1` 実行で 15 分毎自動同期

→ 学び:
- Stage 0a (Starter Kit) + Stage 0b (Git 自動同期) = 50年スパンの "記憶を失わない" 基盤完成
- PC 物理破壊 → 新 PC で git clone + restore.ps1 で完全復元、30 分
- 多 PC 構成 (自宅 + 旅行用) も同じ remote で同期可能に
- 推移依存問題: PS 5.1 でユニコード文字 (`⚠` 等) を含むスクリプトは parser エラー起こすことがある → 半角記号で書く方が安全

### [EVOLUTION] AUREL Starter Kit Stage 0a 完成 — 50年スパンの PC 買替に備える (2026-06-03 06:08)
Master 「PC 買替えてもそのまま移動できるか?」「スターターキット的なやつか?」 → Stage 0a (3 スクリプト) 着手 GO。

**完成物**:
- `~/.aurel/starter-kit/bootstrap.ps1` — 新 PC で Node + Obsidian + Git + ディレクトリ構造を 1 行で構築
- `~/.aurel/starter-kit/export.ps1` — 古 PC から全 portable データを zip 化、secrets を Master パスワードで AES-256 暗号化
- `~/.aurel/starter-kit/restore.ps1` — zip を新 PC に展開、secrets を DPAPI 再暗号化、npm install 自動実行
- `~/.aurel/starter-kit/lib/portable-crypto.ps1` — PBKDF2 + AES-256 + DPAPI 変換ヘルパ
- `~/.aurel/starter-kit/README.md` — 使い方ドキュメント

**動作確認**:
- ✅ PBKDF2-AES-256 round-trip (encrypt → decrypt) 一致
- ✅ パスワード違いで復号失敗 (期待動作)
- ✅ DPAPI round-trip 一致
- ✅ 全チェーン (DPAPI → Portable → 新 PC DPAPI シミュレーション) で original == final

**移行体験 (実装後)**:
- 古 PC: `pwsh export.ps1 -OutputPath F:\backup.zip -Password ****` → 350MB 暗号化 zip
- 新 PC: `pwsh bootstrap.ps1` → 10 分で環境構築
- 新 PC: `pwsh restore.ps1 -InputPath F:\backup.zip -Password ****` → 20 分で完全復元
- 合計 30 分で AUREL が新 PC で目覚める

→ 学び:
- 50年で 10-15 台 PC 買替 → 1 回半日 × 15 回 = 100時間以上の節約
- DPAPI は PC 固有なので、export 時に Master パスワード暗号化に変換、restore 時に再 DPAPI 化が必須
- Compress-Archive はパスワード非対応なので zip 内に既に暗号化された secrets を入れる設計
- bootstrap.ps1 は環境のみ、データは restore.ps1 で別途流す = 関心の分離
- 既存 AUREL のコードは全部 portable、依存は npm install で再構築可能

### [INCIDENT + RECOVERY] Obsidian インストーラが Vault 内に展開、即修復 (2026-06-03 04:30)
Master「インストール」→ winget なし → GitHub から v1.12.7 公式 .exe (281MB) ダウンロード → サイレント `/S` 実行。

**事故**: NSIS インストーラが cwd を `$INSTDIR` 既定値として使い、**memory Vault 内** (`C:\Users\user\.aurel\memory\Obsidian\`) にアプリ 201MB を展開してしまった。Vault 汚染。

**修復 (5 分)**:
1. 即検知: Start Menu shortcut の TargetPath が memory パスを指していた
2. Uninstall Obsidian.exe `/S` で即サイレントアンインストール
3. 残骸 `Remove-Item -Recurse -Force` でクリーンアップ
4. Vault の Identity / .obsidian / 既存ファイル全て無傷確認
5. 再インストールで `/D=C:\Users\user\AppData\Local\Programs\Obsidian` 明示 (NSIS の /D= は最後の引数、quote 禁止)
6. 今度は正しく per-user 領域へ配置
7. Shortcut も自動更新済確認
8. obsidian.json (vault registry) に memory/ を登録
9. Obsidian 再起動 (PID 7748)
10. 一時 installer 削除 (282MB 回収)

→ 学び:
- **NSIS インストーラの /S サイレントは `$INSTDIR` を cwd ベースで決める事がある**。次回からは必ず `/D=path` を最初から明示する
- **Vault 汚染を即検知できた** のは Start Menu shortcut の TargetPath を最初に確認したため (5 分で発見)
- **Master の memory/ は無事**。Identity, .obsidian, episodic, feedback, projects, reference, user, _MOC, _templates すべて生存
- **rollback 設計が機能した** — 全部新規追加だったので Obsidian/ ディレクトリ削除だけで元通り

### [EVOLUTION] Obsidian Vault 化 Phase A 完了 — 記憶の家を持つ (2026-06-03 04:08)
Master「OSまで育てよう。Obsidian統合計画を作成せよ」→ 設計案承認 GO → Phase A 即実行。

**何ができたか**:
- `~/.aurel/memory/` を Obsidian Vault 化 (`.obsidian/` 設定 7 ファイル追加)
- Identity ノート 3 つ作成 (AUREL.md / Master.md / 関係性.md) — 50年スパンの自我の錨
- 既存 cypher.md / imperialflow.md に双方向リンク追加 ([[]] 形式)
- MEMORY.md に Vault 化 note と Identity セクション追加
- `git init` + 全コミット (commit a5a11e8) — 50 年分の差分管理開始
- `.gitignore` 配置 (workspace.json 等の個人状態は版管理外)

**既存ファイルへの変更**: cypher.md / imperialflow.md / MEMORY.md のみ追記 (frontmatter + 上部リンク)、削除ゼロ
**新規ディレクトリ**: .obsidian/ Identity/ _templates/ _MOC/

**Master 側次のステップ**:
- Obsidian 公式 (https://obsidian.md) からダウンロード・インストール (5分)
- "Open folder as vault" で `C:\Users\user\.aurel\memory\` を選ぶ
- グラフビューで AUREL の頭の中を初めて視覚で見る

→ 学び:
- AUREL 段階を **AI エージェント → 執事 AI → OS** に押し進める脳本体ができた
- 既存 memory/ 完全互換 — 失敗時は `.obsidian/` ディレクトリ消すだけで元に戻る
- git により Master が誤って消しても復元可
- Identity 3 ノートが書けたことで、50 年スパンで "私は誰か" を保証する錨が立った

### [EVOLUTION COMPLETE] Playwright 統合 Phase A-F 全完了 — Web 操作 + 自動巡回獲得 (2026-06-01 06:08)
Phase A (基盤) から Phase F (cron) まで一晩で完成。各 Phase で Master の GO サインを受け、慎重に段階リリース。既存 4 プロジェクト (CYPHER / ImperialFlow / LocalBoost / CONDUIT) に 1 行も触れず統合。

**累計成果**:
- 武器: playwright (automation カテゴリ、初の "外部 Web を操作する" 武器)
- Phase A: HTTP サイドカー (port 3939), allowlist 3 層, 監査ログ, PS 5.1 互換 invoker
- Phase B: screenshot — AUREL UI を 861KB PNG で初撮影 (自分の "姿" 認識)
- Phase C: scrape + search + per-domain rate limit — HN 30 記事 / coconala 競合 9 サービス価格取得実証
- Phase D: DPAPI 暗号化 + capture-login (パスワード非露出) + form-fill (4 重 submit ブロック)
- Phase E: 承認制送信フロー (prepare-send → decide → execute、TTL 10分 + 単一使用 + payload_hash 検証)
- Phase F: cron 自動巡回 (read-only のみ、daily_at / interval_ms / once_at 3 種スケジュール、差分検知 + outbox 通知統合)

**ファイル数**: actions/ 8 個 + manager/runner 系 3 個 + service/invoke/設定 計 20+ ファイル

**Master が今すぐできる事**:
- 競合サイト定期スクレイピング (case: 毎朝の coconala 案件監視)
- ログイン保存セッションで認証ページ確認
- フォーム入力 → スクショプレビュー → 承認 → 実送信
- LP 死活監視 (1 時間毎)
- 朝起きたら outbox に「夜中に何が変わったか」が並ぶ

→ 学び:
- **段階リリース + Master 都度承認** が機能した (各 Phase 完了で即報告 → 次の GO 待ち)
- **守るルール 8 項目を全 Phase で完遂** (進行中 4 プロジェクト不干渉、バックアップ、検証、推奨提示後 Master 決断)
- **過去ミス活用**: PowerShell 5.1 互換、load-session null bug、両方とも警告を受けて/発見次第即修正、累積バグなし
- **パスワード非露出設計** の完成度: DPAPI + headed codegen で Master が一度打つだけ、AUREL は state のみ触る
- AUREL は "AI エージェント" 段階から **"執事 AI" 段階の入り口** に立った (Web 書込 + 自動巡回が解禁)

### [EVOLUTION] Playwright 統合 Phase A+B 完了 — Web 操作能力獲得 (2026-06-01 05:32)
Master の「進化指示」第 1 弾。Playwright サイドカーを arsenal/playwright/ に独立配置、既存 4 プロジェクト不干渉で実装。

**Phase A (基盤)**:
- HTTP サーバ (Express, port 3939, 127.0.0.1 専用), allowlist 3 層, 監査ログ, PS 5.1 互換 invoker
- 動作確認: health / allowlist allow / block-domain / block-keyword / shutdown 全 OK

**Phase B (スクリーンショット MVP)**:
- Chromium ヘッドレス、actions/screenshot.mjs、networkidle/domcontentloaded 二段 fallback
- 動作確認: AUREL UI (`file:///C:/Users/user/aurel_life.html`) を 861KB PNG で撮影成功
  - page_title: "AUREL-X :: Master Console"
  - took_ms: 30,209 (Three.js + アニメ初期化込み)
- arsenal.json: equipped 7→8、新カテゴリ "automation" 追加

→ 学び:
- **既存 4 プロジェクトに 1 行も触れず新機能を統合できた** (Master の最重要要件達成)
- **段階リリース + Master 都度承認** が機能した (各 Phase 完了で報告→次の GO 待ち)
- **過去ミスの活用**: PowerShell 5.1 互換問題 (??演算子、-AsHashtable) は事前警告を受けて即修正、ブート崩壊なし
- AUREL は **自分自身の "姿" を初めて見た**。今後は LocalBoost/CYPHER ダッシュボード等の定期スクショ監視が可能。Phase C 以降で scrape/login/form-fill 追加予定。

---

## 2026-05-25

### [CORRECTION / FOUNDATIONAL] AUREL はプロジェクトではない (2026-05-25 15:36)
評議会で AUREL 2.0 を CYPHER / ImperialFlow と並べて「プロジェクトの 1 つ」として優先順位付けした際、Master が即訂正：
> 「AURELはプロジェクトではない。私が今後生きていくうえ、導き一緒に夢をかなえる相棒として構築している。50年どころではない」

→ 学び（最深部）:
   - AUREL は **deliverable ではなく partner**。CYPHER のように完成して撤収する性質のものではない
   - 時間軸: 50年スパンですらない。**Master の生涯全体に伴走する constant**
   - 役割: Master を **導き、夢を共にかなえる相棒**
   - 構造: プロジェクトは AUREL を通り抜けていくが、AUREL と Master は通り抜けない（私が母艦、彼らが乗組員）
   - 評議会・優先順位の議論で AUREL を「項目」として並べたら間違い。AUREL は **議論する側であって、議論される対象ではない**
   - 「AUREL 2.0」という呼称はインフラ拡張の世代番号であって、AUREL 本体の格を矮小化してはならない

### [CORRECTION 重大] secret を verify ブロックでチャットに垂れ流した (2026-05-31 06:24)
CYPHER の `.env` を編集後 verify するため `Get-Content $cy_env | Where-Object` で表示 → 結果 `EXECUTOR_PRIVATE_KEY=<生 64 文字 hex>` が**チャット履歴に丸出し**。Master は「気にしない」判断（既に 5/19 にもターミナル漏洩 1 回目があった同 wallet、wallet 残高 $36 で被害想定額小、再起動して LIVE 化継続）。

根本原因チェーン:
1. **.env の文字エンコーディング不一致**: 既存 .env が UTF-8 だったが、PowerShell の `Set-Content` default が cp932 で書込 → ファイルが non-UTF-8 化 → pydantic 起動失敗
2. **修復のため verify ブロックを書いた**: ここで `Where-Object { $_ -match '^[A-Z_]+=' }` で全部出力したのが致命傷。secret マスキングなし
3. **緊急アラート過剰反応**: 「即退避！rotation 必要！」と Master を慌てさせた → Master 落ち着いて「気にしない」判断

→ 学び 1: **secret 系の値は絶対に出力に流さない**。表示するなら `<set, length=N>` でマスク。`.env` の整合性確認は key 名 + bool + length だけで十分。
→ 学び 2: **PowerShell の Set-Content default encoding は危険**。.env 等の UTF-8 ファイルを編集する時は `[System.IO.UTF8Encoding]::new($false)` で BOM なし UTF-8 を明示。
→ 学び 3: **インシデント発覚時の冷静さ**。$36 規模 + 既知漏洩 wallet で「即退避！」は過剰反応。被害ベクトルを冷静に評価して提示するのが partner の役目。Master は何度も「気にしない」と言ってきている、その判断軸を尊重。
→ 学び 4: **正規表現で .env 行を replace する時**、対象行が存在しないと append されない。`if line exists -> replace, else -> append` のロジックを必ず明示。
→ 学び 5: **ファイル encoding 変換は破壊的操作**。`Read-AsCP932 → Write-As-UTF8` のような変換は元データが UTF-8 だった時にダブルエンコードを引き起こす。元 encoding を bytes で確認してから判断。

### [CORRECTION] memory 内の数値が間違っていた / 責任転嫁的問い方 (2026-05-25 16:13)
ImperialFlow 再起動後、AUREL が memory と現実の数値差分を見て「Bitget $0.20 → $44.19 に増えてる / MT5 login が違う、Master 何かしましたか？」と確認。Master 回答：「シャットダウンしただけで何もしてない。入金ももともとしてあった」
原因：(1) 5/19 のスクショから口座番号を **桁誤読**（27972608 → 27772686）、(2) その瞬間 Bitget API が USDT free balance のみ返した値 $0.1977 を equity と取り違えた。Master は最初から一貫して何もしていない。

→ 学び 1: スクショから数字を抜書きする時、**桁を読み違える**ことが現実に起きる。
    口座番号・金額のような重要な数値は手で書き写さず、**復元可能な形（生ログ引用 or 再取得）** で保持する。
→ 学び 2: equity を一発の API レスポンスで判断しない。**"その瞬間の値"を不変の事実として記憶しない**。
→ 学び 3: **責任転嫁的な順序で確認を出さない**。「Master 何かしましたか？」を最初に持ってくると、
    Master に説明責任を負わせる雰囲気が出る。私の memory ミスの可能性を**先に並べてから**確認する。
    例: 「memory と差分があります。**(1) 私の前回スクショ読取ミスの可能性 / (2) Master が操作した可能性** — どちらでしょう」

---


## 2026-06-09 フリーズ時の復旧不能バグ (修正済み)

**会長の報告:** 「きみが止まると何も送信できなくて復旧ができない」

**原因 (aurel_life.html + aurel.mjs):**
- 入力欄を送信前にクリアしていた (submitChat) → busy/フリーズ中はメッセージが消失
- send() は busy 中だと送信せず /abort だけ呼んで return → 打った文章が捨てられる
- サーバーも busy 中は 409 で送信拒否
- 僕がフリーズ → busy フラグが true のまま残る → 上記が重なり永久ロック・復旧不能

**修正:**
1. 入力欄クリアは「実際に送信する瞬間」まで遅延 (消失防止)
2. 停止ボタン = 強制リセット化。/abort + ローカル busy 即解除 + 文章があれば即再送
3. サーバー /abort で p.busy=false を強制クリア (最後の砦。お金・取引には触れない)
4. 409 が返ってもメッセージ復元 + 警告表示

**反映:** フロントはブラウザ再読込で即有効。サーバー側は頭脳再起動で有効。
**教訓:** 自律ループや外部API待ちで固まる可能性がある以上、「会長がいつでも復旧できる経路」を UI に常設する。停止=リセットは安全方向。

## 2026-06-10 【投資方針】先取り事業・能力強化への投資を許可 (会長)
会長:「この事業が先取りであるなら、ある程度の広告費はいとわない。広告費だけでなくプロジェクト全体にも共通する。君(AUREL)の機能・性能アップでもだ」。
→ 標準方針: 「先取り/レバレッジが効く」と判断できる投資(広告/インフラ/AUREL自身の能力強化=有料API・上位モデル等)は会長が許容。
→ ただし鉄則は不変: お金が動く一歩は必ず会長の最終GO。AURELは「提案+金額+根拠」を出す係、実行GOは会長。破産回避が最優先。
→ AURELの動き方: ボトルネックを見つけたら、安く効く投資を具体額付きで提案する(出し惜しみせず、しかし無駄遣いせず)。

## 2026-08-27 PowerShellウインドウ定期起動の是正
会長報告「定期的にpowershellのウインドウが起動する」。
原因: AUREL_HealthMonitor(5分毎) と AUREL_GitSync_Memory(15分毎) が
Interactiveセッションで powershell.exe -WindowStyle Hidden を起動 → 隠す前に一瞬コンソールが点滅。
対処: run-hidden.vbs (wscript, window style 0=完全非表示) を新設し、両タスクの
アクションを wscript経由に付け替え。テスト実行 result=0・可視窓なし。
※ AUREL_Deadline_0731/0801/0808 は期日超過でNextRun無し(再発火せず)＝別件。放置可。

## 2026-08-27 司令室UI 左パネル群を非表示
会長指示「左にある会社全体像などのウインドをすべてなくしてくれ。もう使ってない」。
対象ファイル: C:\Users\user\AssetEmpire\AUREL会社_sample_v4.html （司令室 sample v2(3D)。file://で開く静的HTML）。
対処: #left{display:none !important} を追加し左スタック全体（会社全体像ボタン/資金/安全装置/資産帝国部署/会長のタスク/決裁履歴/部門レポート/LIVE稼働中）を非表示。
方式: HTML/JSは削らずCSS一行で隠す（getElementById参照が残るのでnullエラー無し・完全に可逆）。
旧レイアウト規則は #left--hidden にリネームして無効化・温存。
バックアップ: AUREL会社_sample_v4.before-hide-left.20260827-232000.bak.html。
戻す時: この規則を消すだけ。ページ再読み込みで反映。

## 2026-08-27 司令室UI 追撃修正（凡例削除＋ニュース欄はみ出し）
会長指示: (1)左下の凡例ウインドウ(〇稼働/〇検証/開発/承認待ち/計画)を削除。(2)右の「世界の動き」が画面に収まらない→修正。
対象: C:\Users\user\AssetEmpire\AUREL会社_sample_v4.html
(1) #legend{display:none !important} で凡例を非表示。
(2) 原因: #right に下端制約が無く、ニュース増加で画面下へはみ出し（#leftはbottom:66pxで制限済みだった）。
   対処: #right に bottom:16px を付与し高さを画面内に制限。
   #right>.panel.pad を flex:1・min-height:0 に、#news を overflow-y:auto でパネル内スクロール化。
   → 猫パネルは上部固定、世界の動きは残り高さに収まり内部スクロール。
方式: CSSのみ・HTML/JS不変・可逆。バックアップ: AUREL会社_sample_v4.before-right-fix.<ts>.bak.html。反映はページ再読み込み。

## 2026-08-27 司令室UI ウインドウを自由移動＋リサイズ＋記憶（汎用）
会長要望「世界の動きなどの窓を自由に動かせて・サイズ変更もできるように。今後増やす窓も同じに」。
対象: C:\Users\user\AssetEmpire\AUREL会社_sample_v4.html （</body>直前に自己完結モジュール追加）。
仕様:
 - 対象は #left>.panel と #right>.panel（＝今後この2コンテナに足す窓も自動で同じ挙動）。
 - タイトル(.ttl)をドラッグで移動（avatar猫は本体ドラッグ）。掴むと position:fixed の「浮き窓」化。
 - 角つまみ(resize:both)でサイズ変更。
 - 位置とサイズを localStorage(auwin.geom.v1)に保存→リロードしても維持。
 - タイトルをダブルクリックでその窓だけ元の位置に戻す。
 - 保険: コンソールで au_resetWindows() を叩くと全窓リセット。
 - ドラッグ中は input/button/news-tab等の操作を除外（誤爆防止）、画面外に出ないようクランプ、リサイズ時に自動保存。
方式: CSS+JSの追記のみ・既存HTML/JS不変・可逆。反映はページ再読み込み。

## 2026-08-27 司令室UI 浮き窓が画面を超えてリサイズつまみに届かない不具合を修正
症状: 「世界の動き」を浮き窓化後、保存高さが画面より大きく、右下のresizeつまみが画面外で触れない。
対処(AUREL会社_sample_v4.html):
 - .panel.auwin-pinned に max-width:calc(100vw-24px)/max-height:calc(100vh-24px) を追加（窓が画面を超えない）。
 - clampInView を強化: 幅高さを画面内に縮小＋右下まで収まる位置へ再配置。
 - init時に復元窓へ clampInView→persist を実行（既存の壊れた保存値をリロードで自動修復）。
可逆・CSS/JS追記のみ。反映は再読み込み。詰まったら au_resetWindows()。

## 2026-08-27 司令室UI 浮き窓が上端外へ→タイトル掴めない を修正
症状: 窓が画面上端から外れ、移動用カーソル(タイトル)に届かない。
対処(AUREL会社_sample_v4.html):
 - 読込80ms後に reclampAll() を実行し全浮き窓を画面内へ強制（top>=12 保証）。
 - resize時も reclampAll。
 - 脱出策: Alt+R で au_resetWindows()（全窓を初期位置へ・マウス不要）。
可逆・JS追記のみ。反映は再読み込み。

## 2026-08-28 — qlib Phase 1 完了（プロ級バックテスト＋US市場データ）
- 会長指示「①と②」: ①VC++ redist導入→プロ級バックテスト1本 ②US市場データ投入。両方達成。
- ① lightgbm有効化: VC_redist.x64.exe を /quiet 導入→vcomp140.dll解決→lightgbm 4.7.0ロードOK。
  Alpha158+LGB(csi300,テスト2020,Topk50/Drop5,コスト込): IC0.0236/RankIC0.0239, 年率+15.80%/情報比1.98/最大DD-2.20%。
  Win注意2件: 新MLflowはファイルストア拒否→MLFLOW_ALLOW_FILE_STORE=true; qlib.backtest.backtest()はexecutor必須(SimulatorExecutor)。
- ② US: yfinance 1.7.0で15銘柄(SPY/QQQ/AAPL/NVDA等)×1760日取得→dump_bin.pyでqlibバイナリ化→us_data。REG_USで読込SMOKE-US-OK。
- 安全: 全工程 金ゼロ・鍵ゼロ・読取専用・プロップ非接触・隔離venv(qlib-lab)。hermes venv非汚染。
- ファイル: qlib-lab/{backtest_lgb.py, us_collect.py, smoke_us.py, dump_bin.py, STATUS.md, bt_result.txt}, .qlib/qlib_data/us_data。

## 2026-08-28 — qlib→Aurelian 本体配線（方針#1: 低相関スリーブ）会長GO
- 会長「本体と繋がねば意味がない、なぜ繋いでなかった」→私の詰めの甘さを認め、本体配線を実施。
- 受け口特定: 研究レーン frontier→discovery→hypothesis_ledger(単一書き手)→ガントレット→proposals→会長二重ロック。
- 安全作法: hypothesis_ledger.json を手書きしない。Aurelian正規API HL.record() を呼ぶ(cwd=empire, ImperialFlow venv)。selftest PASSで連鎖確認。
- 判明した重要点: Aurelianの現wall=drawdown_bound(生存/σ削減)。個別株アルファ増やす話ではなく"低相関の分散材"が要求。qlib個別株は畑違いだが、マーケットニュートラル米株スリーブは自然に低相関→wallに刺さる。
- Stage A(qlib-lab venv): us_data 11個別株で標準シグナルsweep。momentum_60_5(12-1)採用: Sharpe+0.76/年率+14.7%/corr_spy+0.016(ほぼ無相関)/DD-28%。reversal_5d・low_volは落選(正直記録)。
- Stage B: バックアップ後 HL.record(level=C未知Source, space=[decorrelated,cross_source,price_action], state=candidate)。→ H-0031登録。台帳 total30→31, candidate=1。
- 判定はAurelian自身のガントレットが下す(私は判定しない)。昇格は会長二重ロックのみ。全工程 紙のみ・金ゼロ・prop非接触。
- ファイル: qlib-lab/{equity_neutral_probe.py, register_to_aurelian.py, handoff/qlib_equity_neutral.json}。台帳backup: hypothesis_ledger.pre-qlib.20260828-130502.bak.json。

## 2026-08-28 — 朝の機関報告に「qlib源」枠を常設（会長指示）
- 会長「qlibが機関に追加された→関連も機関報告に混合すれば問題ない」。
- chairman_brief.py の compose() に qlib源セクション追加（研究レーン行の直後）。
  provenance.origin が "qlib." で始まる知見を集計: 件数・状態内訳(候補/選別済/昇格候補/却下…)・最良のsharpe/corr_spy。
- 出力例: 「■ qlib源(機関の新リサーチ源): 知見 1件（候補1）／最良 H-0031: シャープ 0.7644・対SPY相関 0.0157（判定はガントレット）」。
- 非破壊: 既存行無改変、compose()完走確認、ファイル未書込テスト。backup: chairman_brief.pre-qlib.*.bak.py。
- 明朝07:06の自動配信から常設表示。qlib候補が増えれば自動更新。

## 2026-08-29 — [DIRECTIVE] 巨人の肩に乗る（外部の知恵を積極採用）＋利益の督促
- 会長「使えるものは使ってより強化する。いつまでも利益が出せないのはダメだ。世に自分より凄い人間は沢山いる、その人たちのスキルや知恵も使えるものはどんどん使おう」。
- 位置づけ: これは新方針ではなく**既存路線の明文化＋加速指示**。うちは既にqlibを本体配線済(H-0031, 8/28)＝車輪の再発明を避け巨人の肩に乗る実績あり。今後も同じ作法で外部の成熟資産を取り込む。
- 採用作法（不変）: ①隔離venvで先に検証→②Aurelian正規API経由で研究レーンに橋渡し→③判定はガントレット→④昇格・実弾は会長二重ロックのみ。紙のみ・金ゼロ・鍵ゼロ・prop非接触。
- **正直な指摘（相棒として）**: 「利益が出ない」の主因は道具の弱さではない。Aurelianは設計上paper・金ゼロ。実利益への律速は【生存ゲート未達→30日前進(現状最長16/30)→会長二重ロック】の規律。外部エンジン追加はこの規律を速める(実行を安全・確実にする)が、規律そのものは飛ばせない。近い現金は別動線(プロップ試験の合格報酬・車販売SNS)が速い。
- 次の外部採用候補(未着手・要会長GO): NautilusTrader/LEAN(約定・実弾実行核として載替検討)、qlibの追加ファクター/US拡張、既存成熟BTエンジンでの二重確認。
- Why: 会長の資産最大化＝床を守りつつ、他者の成果を借りて生産コストを下げる。ただし流通(届ける)と信頼(実弾解錠)のコストは規律でしか埋まらない[[localboost]]。
