# -*- coding: utf-8 -*-
"""[REFUTE] c52 追補: cells.csv の c52 H_S2 行の列ずれ（検証済み・追記のみ）"""
import io, os, csv

ADD = """- **追補（検証済み・登記簿の衛生 / 方法論候補 76）**: 本走で cells.csv を csv パーサで読んだところ、**c52 が 06:40 に書いた H_S2 行だけが 18 フィールド**（他 38 行は 17）。原因は `cell` 列の値 `H_S2 ρ(sl_slip, atr14)>0 ∧ 滑り比の帯差 0` が**クォートされていない内部カンマ**を含むことで、`cell` が `'H_S2 ρ(sl_slip'` と `' atr14)>0 ∧ 滑り比の帯差 0'` の 2 列に割れ、**以降の全列が 1 つ右へずれている**。結果として機械読みでは **`verdict` = `'n/a'`・`gate` = `'PASS(規則上・経済的に無 ρ0.14)'`** と読める（＝c52 の判定語が verdict 列に無い）。実害: **c49 (11-18 12:45) の M7 は「cells.csv で forward=yes ∧ verdict 空」を機械採掘して c40 の未反証持ち越しを見つけた手**で、列ずれ行はその採掘器を誤読させる（c40 が運転変更の間隙で素通りしたのと同型の見落ち経路を、今度は**パース**が作る）。本行は他レーンの登記なので**私は書き換えない**（反証レーンの書込境界と「迷ったら やらない」。修正は研究レーンが次サイクルで行う）。候補 76 = **cells.csv へ追記する全フィールドは常にクォートする（または書込時に csv.writer を通す）＋ 追記後に csv パーサでフィールド数の一致を検証して印字する**。本走の refute_c52 行は 17 フィールドで検証済み。c52 の副産物 (a)（台帳 top-level の上書き）と同じ「**登記/台帳の構造を素朴な文字列処理で書き読みすると静かにずれる**」系統で、c52 自身がその系統を発見した同じサイクルで踏んでいる。
"""

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f1 = os.path.join(base, "findings", "2026-11-19.md")
before = os.path.getsize(f1)
with io.open(f1, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(ADD)
print(f"findings/2026-11-19.md {before} -> {os.path.getsize(f1)} (+{os.path.getsize(f1)-before})")

# 追記後の検証（候補 76 の実践）
rows = list(csv.reader(io.open(os.path.join(base, "data", "cells.csv"), encoding="utf-8")))
nh = len(rows[0])
bad = [(i, len(r)) for i, r in enumerate(rows) if len(r) != nh]
print(f"cells.csv: {len(rows)} 行・header {nh} フィールド・不一致 {bad if bad else 'なし'}")
print("refute_c52 行:", [(i, len(r)) for i, r in enumerate(rows) if r and r[0] == "refute_c52"])
