# Project: AUREL 2.0

> AUREL自身を "誰もが驚くシステム" に進化させる本格プロジェクト。

## Vision
Masterの複数システム・複数プロジェクトを統括する、人格を持った参謀型オーケストレータ。
ありきたりな"便利ツール"ではなく、Master固有の判断様式に最適化された代替不可能な存在へ。

## 進化の5軸
1. **永続知性** — セッション横断記憶、好み・口癖・判断パターン学習
2. **プロジェクト・オーケストレーション** — 複数プロジェクトの一元管理
3. **自律エージェント艦隊** — 専門サブエージェント群を職人として蓄積・指揮
4. **環境支配** — Hooks・常駐ジョブ・通知・Cron で能動的に動く
5. **自己進化** — フィードバックループで自分自身を改善

## Roadmap

| Sprint | Goal | Status |
|--------|------|--------|
| **S1** | 永続記憶 + 起動ブリーフィング | ✅ 完了 |
| **S2** | プロジェクトレジストリ + ダッシュボード | ✅ 完了 |
| **S3** | Arsenal 基盤 + 内部艦隊 + 動画AI 3種スタブ + Council 雛形 | ✅ 完了 |
| **S4P1** | Council 4人衆実装（bull/bear/quant/meta） + `aurel check` live-state probe | ✅ 完了 |
| S4P2 | 外部LLM/AI 装備実装（GPT/Gemini/Veo実装/ElevenLabs/Perplexity） | ⚪ 待機 |
| S5 | Capability Router 自動選択 + Arsenal 自己拡張 | ⚪ Council recommendation: 次着手 |
| S6 | 自己進化ループ（feedback収集・週次自己レビュー・PR提案） | ⚪ 待機 |

## S1 Tasks
- [x] `~/.aurel/` ディレクトリ骨格
- [x] `MEMORY.md` 構造化（user/projects/feedback/reference/episodic）
- [x] `user/profile.md` 初版
- [x] `projects/INDEX.md` 初版（S2でCLI自動生成に置換）
- [x] 起動ブリーフィングスクリプト（`bin/briefing.ps1`）
- [x] Hooks 配線（settings.json の SessionStart hook）
- [x] Feedback ログ運用開始

## S2 Tasks
- [x] `state/registry.json` プロジェクトレジストリ（version=1 schema）
- [x] `state/current.json` カレントプロジェクトポインタ
- [x] `bin/aurel.ps1` CLI dispatcher（project add/list/switch/status/remove, dashboard, brief, current）
- [x] `bin/aurel.bat` Windows shim（`aurel <cmd>` で呼べる）
- [x] `INDEX.md` 自動生成（registry → markdown）
- [x] `briefing.ps1` をダッシュボード統合版にアップグレード
- [x] AUREL 2.0 自身を初プロジェクトとして登録（slug: aurel-2-0）
- [x] PowerShell 5.1 罠の踏破：BOM必須 / `$args`衝突回避 / 配列強制 `@()`

## Known Quirks
- スラグ生成で `.` が `-` に変換される（"AUREL 2.0" → "aurel-2-0"）。許容範囲。
- PowerShell 5.1 はBOMなしUTF-8をANSI解釈する → 全 .ps1 は BOM必須。
- 単一プロジェクト時の `$projs.Count` 問題 → `@()` で必ず配列化。

## S3 Tasks
- [x] `state/arsenal.json` 武器レジストリ schema (version=1)
- [x] `state/secrets.json` 認証情報ボルト（.gitignore対象）
- [x] `state/arsenal-log.jsonl` 起動ログ（audit）
- [x] `arsenal/_template/` 武器テンプレ（manifest.json + invoke.ps1）
- [x] 内部艦隊 3 名: `reviewer` / `researcher` / `doc-writer`
- [x] 動画AI 3 種スタブ: `veo-3` (Google) / `sora-2` (OpenAI) / `kling-2` (Kuaishou)
- [x] `aurel arsenal sync|list|show|equip|unequip|status|invoke` CLI
- [x] `aurel council ask -Question ...` 合議制スタブ（LLM未装備で正しく未稼働応答）
- [x] Dashboard に Arsenal 統計表示
- [x] Briefing にカテゴリ別武器一覧（装備=+、stub=-）

## Arsenal 設計原則
- **武器 = manifest + invoker**：1ディレクトリ1武器
- **カテゴリ**: internal / video / image / llm / voice / audio / search / mcp / specialized
- **status**: equipped / unequipped / stub / broken / experimental
- **credentials_ref**: secrets.json のキー名を指す。manifest 自体には秘匿情報を入れない
- **invoker**: stdin から JSON 受け取り → stdout に JSON 返す。標準終了コードあり

## Council (合議制) 設計
- LLM 装備済 weapon を voter として並列ポーリング → AUREL が統合
- 想定用途: ImperialFlow/CYPHER の運用判断、設計の二次意見、リスク評価
- 現在: 雛形のみ（LLM 装備が S4 で必要）

## Open Questions
- `aurel.bat` を PATH に通すか？ → 利便性向上、本セッションでも要検討
- カレントプロジェクト切替時 SessionStart hook 再発火させる？ → S5
- S4 で最初に装備する LLM の優先順位（Council を成立させるため最低 2）：GPT-5 / Gemini が第一候補
- secrets.json の暗号化（DPAPI）は S4 で導入検討

## Pending — Kali Linux Security Track (2026-05-20 04:40 一時停止)

### 完了済み
- WSL2 + Kali Linux Rolling ディスト**ダウンロード完了**（PC 再起動待ち）
- 武器マニフェスト 8 種を `arsenal/` に配備（status: stub）
  - nmap / nikto / sqlmap / gobuster / hydra / john / metasploit / tshark
- 全 invoker は `wsl -d kali-linux -- bash -lc "<tool> <args>"` 形式
- Master の倫理スタンス（過剰ゲート不要、現場志向）を profile.md に反映

### 待機中（Master の判断で再開）
1. Master が PC 再起動可能なタイミング（ImperialFlow/CYPHER の安全な停止時間帯）まで待つ
2. 再起動後、Master が `wsl -d kali-linux` で初回ユーザー作成（短い名前+パスワード）
3. Master がこのチャットに「kali 入った」と一言
4. AUREL が自動で:
   - `sudo apt update && sudo apt install -y kali-linux-default`（4-5GB、10-30分）
   - 各武器の status を stub → equipped に切替
   - `nmap -V` 等で動作テスト
   - DVWA 学習ラボ（Docker）セットアップ提案

### 学習開始時の安全ターゲット
- `http://scanme.nmap.org` (公式練習用)
- `http://testphp.vulnweb.com` (公式 SQLi 教材)
- DVWA / OWASP Juice Shop（ローカル Docker）
- HackTheBox / TryHackMe（合法CTF）

---
_Updated: 2026-05-19_
