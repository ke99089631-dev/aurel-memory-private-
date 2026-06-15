
## ★悪い癖の是正 (2026-06-12 会長指摘・最重要)
- 悪い癖=「研究スクリプトを empire/research/ に作って終わり。指令室(UI)に反映せず放置」。これをやめろ。
- 指令室の左右ウインドウは飾りではない。作った機能は必ず指令室に映して初めて『仕事完了』。
- 資産帝国は『部署』。部署として分けて可視化すること(他部署と区別できる形)。
- 今後の鉄則: 機能を作る=指令室への配線+可視化まで含めて1セット。作りっぱなし禁止。

## ★UI反映先の取り違え是正 (2026-06-14 会長指摘・重要)
- ミス: 資産帝国 部署パネルを「マスターコンソール」(aurel_life.html / port7878 / aurel.mjs配信)に足した。会長が実際に使うのは別物。
- 正しい本物=「AUREL 司令室」= C:\Users\user\AssetEmpire\AUREL会社_sample_v4.html / port7891 / company-bridge.mjs配信。会社ビジュアル(部署・お金・決裁・部門レポート)はすべてココ。
- 鉄則: 会社/部署の可視化は必ず「司令室(7891 company-bridge)」へ。aurel_life.html(7878 Master Console)は開発用の仮窓。データ配線は company-bridge.mjs の /api/company に足し、HTMLは connectReal() で描画する流儀。
- 配線方式の真実の出所: empire/data/empire_status.json (emit_empire_status.py生成・読取専用) → company-bridge.mjs getAssetEmpire()→ /api/company.assetEmpire → 司令室の #empirePanel。

## ★会長のメイン操作面=司令室(7891)で確定 (2026-06-14)
- 会長「基本的にマスターコンソールつかわない。今はこの司令室がメインで使用する」。今後の表示・チャット・可視化は全て司令室(7891)前提で考える。Master Console(7878)は基本使わない。
- チャットの真実: 司令室のチャットも aurel.mjs(7878) の home部屋に SSE接続(discoverBrain→/api/projects/home/stream)。=Master Consoleと同じ私・同じ記憶・同じ会話。返事はhome部屋に保存され両窓に映る(片方に閉じ込められない)。
- 会長が司令室で私と話す手順: 右上(または該当)の「モード」ボタンで観測モード→チャットモードに切替→ロード履歴に直近24件が出る→下のチャット欄で送信→返事はその場でストリーム表示。
- 鉄則: 新機能・報告の可視化は司令室に出す。会長が司令室チャットを使えているか不安なら、その動線(モード切替→送信→返事表示)も合わせて点検する。
