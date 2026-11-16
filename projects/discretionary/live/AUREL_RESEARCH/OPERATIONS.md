# AUREL_RESEARCH 運転設定(レーンは読まない・人間/AUREL用)

## 2026-11-16 会長GO「1と2を実行」— Fable上限対策
背景: 直近14日で研究+反証レーン=Fable消費の約75%(475M tok・1日16回)。11-11上限到達→11-12〜15の4日間レーン即失敗・会長チャットも停止。

| レーン | 旧 | 新 |
|---|---|---|
| AUREL_ResearchLane(run_research.cmd) | 毎日3時間ごと(8回/日・土日も) | **平日のみ 00:30/06:30/12:30/18:30**(4回/日)・モデルは既定(Fable)のまま |
| AUREL_ResearchRefute(run_refute.cmd) | 毎日3時間ごと(8回/日・土日も) | **平日のみ 03:30/09:30/15:30/21:30**(4回/日)・**`--model claude-opus-5`** |

- 週の実行回数 112→40。見込み: レーンのFable消費 約34M/日→約10M/日。
- 反証をOpus 5にした理由: 反証は「同じ検定を別の切り口で壊す」機械的な仕事でモデル差が出にくい。研究(発想側)はFable維持。
- タスク定義はXMLで差し替え(MultipleInstances=IgnoreNew等の設定は維持)。旧XML=`C:\Users\user\.aurel\tmp\task_Research*_20261116.xml`、旧cmd=`run_refute.cmd.bak_20261116`。
- 戻し方: `schtasks /Create /TN <name> /XML <旧XML> /F` と bak を戻す。
- 効果測定: 翌日以降 `~/.claude/projects` の会話記録からモデル別トークンを集計(2026-11-16 episodic に集計スクリプトの要点)。
