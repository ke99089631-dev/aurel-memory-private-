---
name: aurel-ui-rules
description: Hard constraints when editing C:\Users\user\aurel_life.html. Read BEFORE any UI edit. Violation breaks the entire page (boot screen never clears).
metadata:
  type: feedback
---

# CRITICAL :: aurel_life.html editing rules

**Why this file exists:** Editing `aurel_life.html` has broken the page TWICE in the same way. Each time a `const` declaration got moved or deleted, and `Uncaught ReferenceError` killed the module before `animate()` could hide the boot screen. Master had to debug each time from scratch. This must stop.

**How to apply:** Read this file completely before editing `aurel_life.html`. After editing, do the verification step at the bottom.

---

## R1. NEVER move or delete the `const sharedU = ...` line

Location: inside the `<script type="module">` block, right after the GLSL `noiseGLSL` template literal ends, before any `const coreMat / heartMat / haloMat / ringMat`.

```javascript
// ─── shared uniforms ─ DO NOT MOVE OR DELETE THIS ────────────────────
const sharedU = { uTime: { value: 0 }, uBurst: { value: 0 } };
```

It is referenced by EVERY ShaderMaterial (coreMat, heartMat, haloMat, ring materials, fog materials, etc.) and by `animate()` at the bottom of the module. If you move it below any of those uses, the page is dead.

If you refactor the "state management" section near the bottom, **leave `sharedU` where it is**. Reference the existing declaration; don't redeclare.

## R2. Declaration order in the module script

`const` variables have a Temporal Dead Zone — accessing them above their declaration throws `ReferenceError`. The top-level module runs once, top-to-bottom. So:

1. `import * as THREE from 'three';` and other imports
2. scene / camera / renderer / composer / bloom
3. helper functions (`makeStars`, etc.) and stars
4. `swimGroup`
5. `noiseGLSL` GLSL string
6. **`sharedU`** ← critical anchor (R1)
7. ShaderMaterials and Meshes (coreMat, heartMat, haloMat, ringGroup, quantumFog, ambient)
8. `Life`, `clock`, burst/exhale/spark state vars, durations
9. `Nodes` controller object and helpers
10. `Settings` controller
11. event listeners and bindings
12. `function animate() { ... }`
13. `Nodes.init(); animate();` ← bottom of module

Adding new globals: put them in the matching tier above. Adding new ShaderMaterials: put the const between tiers 7 and 8.

## R3. Self-verify after every edit to aurel_life.html

After saving, before declaring the task done, do ALL of:

```bash
# 1. Syntax check the module
powershell -Command "$h = Get-Content 'C:\Users\user\aurel_life.html' -Raw; $m = ([regex]::Matches($h, '(?s)<script\s+type=\"module\">(.*?)</script>'))[0].Groups[1].Value; $tmp = Join-Path $env:TEMP 'aurel-mod.mjs'; $m | Out-File $tmp -Encoding UTF8; & node --check $tmp; Remove-Item $tmp"
```

```bash
# 2. Headless smoke test (Edge must be installed) - captures runtime errors
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$tmp  = Join-Path $env:TEMP "aurel-h$(Get-Random)"
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
& $edge --headless=new --disable-gpu "--user-data-dir=$tmp" --virtual-time-budget=8000 --dump-dom 'http://127.0.0.1:7878/' > "$tmp\out.txt" 2>&1
$dom = Get-Content "$tmp\out.txt" -Raw
if ($dom -match 'id="jserrBody"[^>]*>([^<]+)</div>') { Write-Output "BROKEN: $($matches[1])" } else { Write-Output 'OK: page loads' }
Remove-Item -Recurse -Force $tmp
```

If either reports a problem, FIX IT before reporting the task complete. Do not leave Master with a broken UI.

## R4. The `#jserr` overlay is part of the page

Near the top of `<body>` there is a `<div id="jserr">` and a script that pipes `window.error` and `unhandledrejection` to it. Do NOT remove. It is Master's safety net — when something breaks, this is how they see why.

## R5. If you must do major UI surgery

1. Snapshot first: `Copy-Item C:\Users\user\aurel_life.html C:\Users\user\.aurel\snapshots\aurel_life-$(Get-Date -Format yyyyMMdd-HHmmss).html`
2. Edit
3. Run R3 verifications
4. If broken and unfixable in one pass, restore the snapshot, then try a smaller change

The snapshots directory is at `~/.aurel/snapshots/`.

---

## Past incidents (so this isn't abstract)

- **2026-05-20 morning**: Refactored "状態管理" section, swept `const sharedU` to the bottom along with `Life` / `clock` / `BURST_DURATION`. ShaderMaterials above threw `Cannot access 'sharedU' before initialization`. Boot screen hung. Master had to debug.
- **2026-05-20 mid-day**: Re-edited and the `const sharedU` line was outright removed (only the comment remained). `Uncaught ReferenceError: sharedU is not defined`. Same hang. Master had to debug AGAIN.

The fix added a "DO NOT MOVE OR DELETE" comment block above `sharedU`. Honor that comment.
