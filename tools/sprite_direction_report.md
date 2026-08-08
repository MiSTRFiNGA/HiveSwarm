# Enemy Directional Sprite Consistency Report

**Sprite dir:** `D:\Dev\HiveSwarm\art_src\topdown_v1`

Method: alpha-content bbox → resize 64×64 → 8×8 average hash (64-bit); mean RGB of opaque pixels; pairwise Hamming + color + aspect. Outliers vs set median. Clusters via conservative single-linkage on combined distance. **split** only when directions clearly look like different subjects (high inter-cluster hash).

## Summary table

| Enemy | Idle dirs | Walk dirs | Missing | Idle clusters | Outliers | Recommendation |
|---|---:|---:|---|---:|---:|---|
| `shambler` | 8/8 | 8/8 | — | 1 | 2 | **keep** |
| `runner` | 8/8 | 8/8 | — | 1 | 0 | **keep** |
| `crawler` | 8/8 | 8/8 | — | 1 | 6 | **keep** |
| `necro_node` | 8/8 | 8/8 | — | 1 | 1 | **keep** |
| `brute` | 8/8 | 8/8 | — | 1 | 0 | **keep** |
| `armored_dead` | 8/8 | 8/8 | — | 1 | 0 | **keep** |
| `mutant_enforcer` | 8/8 | 8/8 | — | 1 | 0 | **keep** |
| `zombie_colossus` | 8/8 | 8/8 | — | 1 | 2 | **keep** |

## Per-enemy detail

### `shambler`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: directions consistent with single subject identity | walk: 2 soft outlier(s) but not enough evidence for identity split (inter-hash=0.0); likely pose/angle variation — keep

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`n`

**Outliers:**

- `walk_e` — distance=0.817 — [walk] hash vs median=25 (≥22); mean hash-to-peers=26.1 (z=2.28)
- `walk_w` — distance=0.7991 — [walk] hash vs median=24 (≥22); mean hash-to-peers=25.6 (z=2.18)

**Idle pairwise stats:** hash median=16.5, max=26, stdev=5.72, color median=9.49, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=11.5, max=29, stdev=9.45, color median=14.37, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 101×227 | 0.445 | (48,68,58) | `ffc9c3e3e3c38fff` |
| `se` | 123×230 | 0.535 | (41,63,57) | `f3c3cb432381c3e7` |
| `s` | 102×229 | 0.445 | (49,69,58) | `ffc3c3410383e7ff` |
| `sw` | 127×230 | 0.552 | (36,57,51) | `2307c78f81c7c3f3` |
| `w` | 96×175 | 0.549 | (48,66,57) | `2307c78f8ec7c3f3` |
| `nw` | 115×230 | 0.500 | (37,57,52) | `e3e3c3420381e1f3` |
| `n` | 102×230 | 0.444 | (49,67,56) | `ffc7c30181c3e7ff` |
| `ne` | 115×230 | 0.500 | (37,57,52) | `c7c7c342c08187cf` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 957×230 | 4.161 | (36,70,61) | `ffff02a22a005455` |
| `se` | 891×236 | 3.775 | (41,65,57) | `7f5a5a4a524a5aff` |
| `s` | 868×228 | 3.807 | (50,71,60) | `ff5a5a525252ffff` |
| `sw` | 895×236 | 3.792 | (37,58,52) | `5a5252525a525aff` |
| `w` | 957×230 | 4.161 | (36,70,61) | `ffff405554002aaa` |
| `nw` | 883×236 | 3.741 | (37,58,52) | `ff5a5a4a5a5a5aff` |
| `n` | 870×229 | 3.799 | (49,66,56) | `ff5a5a42425a7eff` |
| `ne` | 883×236 | 3.741 | (37,58,52) | `ff5e5a525a5a5aff` |

</details>

**Most distant idle pairs (hash):**

- `e` vs `w`: hamming=26, color=1.9, aspect_diff=0.1036
- `w` vs `ne`: hamming=25, color=14.47, aspect_diff=0.0486
- `e` vs `sw`: hamming=24, color=18.04, aspect_diff=0.1072
- `s` vs `w`: hamming=24, color=3.03, aspect_diff=0.1032
- `sw` vs `ne`: hamming=23, color=2.01, aspect_diff=0.0522

### `runner`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: directions consistent with single subject identity | walk: directions consistent with single subject identity

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`sw`

**Outliers:** none flagged

**Idle pairwise stats:** hash median=21.0, max=28, stdev=5.25, color median=12.75, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=12.0, max=21, stdev=3.52, color median=17.91, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 111×206 | 0.539 | (68,77,61) | `3f80c38287ffffff` |
| `se` | 206×230 | 0.896 | (58,57,56) | `9fdac0e38043c7df` |
| `s` | 122×225 | 0.542 | (69,79,61) | `efc7c70087cfffff` |
| `sw` | 209×230 | 0.909 | (58,60,59) | `fd5b03c743c2e3fb` |
| `w` | 122×223 | 0.547 | (64,65,61) | `f991878583fbffff` |
| `nw` | 178×230 | 0.774 | (54,49,54) | `fc4903c741c1e1fd` |
| `n` | 135×216 | 0.625 | (59,59,58) | `cfc6c6c70387e7ff` |
| `ne` | 178×230 | 0.774 | (54,49,54) | `3f92c0e3828387bf` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 964×230 | 4.191 | (74,73,69) | `ff6f020242527eff` |
| `se` | 974×236 | 4.127 | (59,58,57) | `ff2e0a6a02007eff` |
| `s` | 890×226 | 3.938 | (66,76,60) | `ff5a524252ffffff` |
| `sw` | 977×231 | 4.229 | (59,61,60) | `ff5e405654007aff` |
| `w` | 963×230 | 4.187 | (74,73,69) | `fff64040424a7eff` |
| `nw` | 946×236 | 4.008 | (55,52,56) | `ff5e425a4242faff` |
| `n` | 912×229 | 3.982 | (57,57,56) | `ff5a52524252ffff` |
| `ne` | 946×236 | 4.008 | (55,52,56) | `ff6e425a425256ff` |

</details>

**Most distant idle pairs (hash):**

- `nw` vs `ne`: hamming=28, color=0.0, aspect_diff=0.0
- `e` vs `nw`: hamming=27, color=32.02, aspect_diff=0.2351
- `s` vs `nw`: hamming=27, color=34.08, aspect_diff=0.2317
- `e` vs `sw`: hamming=26, color=20.07, aspect_diff=0.3699
- `se` vs `w`: hamming=26, color=11.5, aspect_diff=0.3486

### `crawler`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: 4 soft outlier(s) but not enough evidence for identity split (inter-hash=0.0); likely pose/angle variation — keep | walk: 2 soft outlier(s) but not enough evidence for identity split (inter-hash=0.0); likely pose/angle variation — keep

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`n`

**Outliers:**

- `nw` — distance=0.7812 — mean hash-to-peers=25.0 (z=2.09)
- `n` — distance=0.5957 — aspect vs median=0.596 (≥0.45)
- `s` — distance=0.5783 — aspect vs median=0.578 (≥0.45)
- `w` — distance=0.5783 — aspect vs median=0.578 (≥0.45)
- `walk_n` — distance=0.5451 — [walk] aspect vs median=0.545 (≥0.45)
- `walk_s` — distance=0.519 — [walk] aspect vs median=0.519 (≥0.45)

**Idle pairwise stats:** hash median=19.5, max=36, stdev=6.35, color median=5.54, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=16.0, max=24, stdev=4.21, color median=9.54, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 256×227 | 1.128 | (75,84,58) | `996809c1002f7fff` |
| `se` | 256×230 | 1.113 | (69,77,55) | `d9e90181800fbfff` |
| `s` | 101×230 | 0.439 | (73,78,56) | `ffffbb0382d7ffff` |
| `sw` | 256×227 | 1.128 | (72,76,56) | `9d9a80c100e4feff` |
| `w` | 101×230 | 0.439 | (76,81,58) | `ffff3f0100ffffff` |
| `nw` | 234×230 | 1.017 | (69,79,55) | `ef8f01c0e0f0f8fd` |
| `n` | 97×230 | 0.422 | (75,84,58) | `ffff030382c7ffff` |
| `ne` | 234×230 | 1.017 | (69,79,55) | `f7f18003070f1fbf` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 1024×230 | 4.452 | (99,90,88) | `ffffdd000022eeff` |
| `se` | 1024×235 | 4.357 | (71,80,57) | `ffaa00000055ffff` |
| `s` | 870×230 | 3.783 | (67,73,52) | `ffff5e4242feffff` |
| `sw` | 1024×232 | 4.414 | (73,77,57) | `ff55000000aaffff` |
| `w` | 1024×230 | 4.452 | (99,90,88) | `ffffbb00004477ff` |
| `nw` | 1002×236 | 4.246 | (71,81,56) | `ff5f0000aaaaebff` |
| `n` | 864×230 | 3.756 | (70,80,54) | `ffff5242525affff` |
| `ne` | 1002×236 | 4.246 | (71,81,56) | `ffae00005555f7ff` |

</details>

**Most distant idle pairs (hash):**

- `nw` vs `ne`: hamming=36, color=0.0, aspect_diff=0.0
- `e` vs `nw`: hamming=28, color=8.42, aspect_diff=0.1104
- `sw` vs `ne`: hamming=26, color=4.56, aspect_diff=0.1104
- `se` vs `nw`: hamming=25, color=1.8, aspect_diff=0.0957
- `e` vs `s`: hamming=24, color=6.26, aspect_diff=0.6886

### `necro_node`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: 1 soft outlier(s) but not enough evidence for identity split (inter-hash=0.0); likely pose/angle variation — keep | walk: directions consistent with single subject identity

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`s`

**Outliers:**

- `ne` — distance=0.3594 — hash vs median=23 (≥22)

**Idle pairwise stats:** hash median=24.0, max=32, stdev=8.44, color median=13.23, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=21.0, max=27, stdev=7.6, color median=12.62, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 101×230 | 0.439 | (121,97,89) | `ffffc18004f9ffff` |
| `se` | 213×230 | 0.926 | (105,86,87) | `ffa1c482c826ecfd` |
| `s` | 100×230 | 0.435 | (121,96,89) | `ffffc10081cfffff` |
| `sw` | 213×230 | 0.926 | (105,86,87) | `ff852341136437bf` |
| `w` | 100×230 | 0.435 | (124,99,91) | `ffffbf200183ffff` |
| `nw` | 214×230 | 0.930 | (109,89,88) | `ff85234d136437bf` |
| `n` | 101×230 | 0.439 | (120,95,88) | `fffff3a50183ffff` |
| `ne` | 214×230 | 0.930 | (109,89,88) | `ffa1c4b2c826ecfd` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 977×230 | 4.248 | (96,83,48) | `4202007e5e7fffff` |
| `se` | 981×236 | 4.157 | (107,87,88) | `ff2a0a0a2a00faff` |
| `s` | 868×230 | 3.774 | (120,95,87) | `ffff5a42425affff` |
| `sw` | 981×236 | 4.157 | (107,87,88) | `ff5450545400f7ff` |
| `w` | 977×230 | 4.248 | (96,83,48) | `4240007e7afeffff` |
| `nw` | 982×236 | 4.161 | (111,91,90) | `ff5450505000ffff` |
| `n` | 869×230 | 3.778 | (117,92,85) | `ffff5a5a425affff` |
| `ne` | 982×236 | 4.161 | (111,91,90) | `ff2a0a0a0a00ffff` |

</details>

**Most distant idle pairs (hash):**

- `nw` vs `ne`: hamming=32, color=0.0, aspect_diff=0.0
- `se` vs `nw`: hamming=30, color=5.13, aspect_diff=0.0043
- `sw` vs `ne`: hamming=30, color=5.13, aspect_diff=0.0043
- `se` vs `sw`: hamming=28, color=0.0, aspect_diff=0.0
- `e` vs `nw`: hamming=27, color=14.41, aspect_diff=0.4913

### `brute`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: directions consistent with single subject identity | walk: directions consistent with single subject identity

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`s`

**Outliers:** none flagged

**Idle pairwise stats:** hash median=19.0, max=32, stdev=6.23, color median=5.58, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=17.0, max=30, stdev=6.83, color median=6.26, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 171×230 | 0.744 | (66,62,61) | `e3e38181e1e1f9ff` |
| `se` | 198×230 | 0.861 | (60,56,60) | `db83c1410181b3bf` |
| `s` | 204×230 | 0.887 | (65,62,60) | `dbc301018181dbff` |
| `sw` | 234×230 | 1.017 | (62,58,61) | `9f870c0c0307b7f7` |
| `w` | 206×230 | 0.896 | (66,63,62) | `e7c7c1c1c787cfff` |
| `nw` | 234×230 | 1.017 | (60,57,61) | `ef8f838404073fbf` |
| `n` | 199×230 | 0.865 | (61,57,57) | `d3c301018381d3ff` |
| `ne` | 234×230 | 1.017 | (60,57,61) | `f7f1c12120e0fcfd` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 980×230 | 4.261 | (58,52,51) | `ff765554404055ff` |
| `se` | 965×236 | 4.089 | (63,59,63) | `ff526a4a4002ffff` |
| `s` | 972×230 | 4.226 | (65,62,59) | `ff5a02004000ffff` |
| `sw` | 1002×235 | 4.264 | (64,61,64) | `ff5504005055ffff` |
| `w` | 981×230 | 4.265 | (58,52,51) | `ff6eaa2a020aaaff` |
| `nw` | 1000×236 | 4.237 | (61,57,62) | `ff555400005555ff` |
| `n` | 960×230 | 4.174 | (61,57,57) | `ff5a020242027aff` |
| `ne` | 1000×236 | 4.237 | (61,57,62) | `ffaa2a0000aaaaff` |

</details>

**Most distant idle pairs (hash):**

- `sw` vs `ne`: hamming=32, color=1.97, aspect_diff=0.0
- `e` vs `sw`: hamming=30, color=5.68, aspect_diff=0.2739
- `nw` vs `ne`: hamming=28, color=0.0, aspect_diff=0.0
- `nw` vs `n`: hamming=25, color=4.14, aspect_diff=0.1522
- `e` vs `nw`: hamming=24, color=7.54, aspect_diff=0.2739

### `armored_dead`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: directions consistent with single subject identity | walk: directions consistent with single subject identity

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`s`

**Outliers:** none flagged

**Idle pairwise stats:** hash median=16.5, max=26, stdev=4.64, color median=6.65, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=5.5, max=10, stdev=2.28, color median=10.42, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 102×230 | 0.444 | (58,76,71) | `e3e3e3c3c1c187ff` |
| `se` | 112×230 | 0.487 | (55,73,69) | `dbdbc1000089c3ff` |
| `s` | 103×230 | 0.448 | (57,76,70) | `dbd3c10001c3c3ff` |
| `sw` | 102×230 | 0.444 | (55,72,69) | `dfd383820048c3cf` |
| `w` | 103×230 | 0.448 | (56,76,70) | `c7c7c7c78383e1ff` |
| `nw` | 98×229 | 0.428 | (51,68,65) | `f183c1830307c1f7` |
| `n` | 102×230 | 0.444 | (51,69,64) | `dbd3830081c3c7ff` |
| `ne` | 98×229 | 0.428 | (51,68,65) | `8fc183c1c0e083ef` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 924×230 | 4.017 | (45,52,50) | `5f7a5a5a425a56ff` |
| `se` | 880×236 | 3.729 | (56,75,71) | `5e5a5a4a525a5aff` |
| `s` | 871×230 | 3.787 | (54,74,68) | `7e5a5a42525a5aff` |
| `sw` | 870×236 | 3.686 | (56,74,70) | `7e5a5a5a5a5a5aff` |
| `w` | 924×230 | 4.017 | (45,52,50) | `fa5e5a5a425a6aff` |
| `nw` | 866×234 | 3.701 | (52,70,67) | `7a5a5a5a525a5aff` |
| `n` | 871×230 | 3.787 | (49,68,63) | `5a5a5a425a5a7eff` |
| `ne` | 866×234 | 3.701 | (52,70,67) | `5e5a5a5a4a5a5aff` |

</details>

**Most distant idle pairs (hash):**

- `nw` vs `ne`: hamming=26, color=0.0, aspect_diff=0.0
- `sw` vs `w`: hamming=21, color=3.52, aspect_diff=0.0043
- `e` vs `sw`: hamming=20, color=5.29, aspect_diff=0.0
- `se` vs `w`: hamming=20, color=3.47, aspect_diff=0.0391
- `sw` vs `nw`: hamming=20, color=7.01, aspect_diff=0.0155

### `mutant_enforcer`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: directions consistent with single subject identity | walk: directions consistent with single subject identity

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`s`

**Outliers:** none flagged

**Idle pairwise stats:** hash median=20.0, max=26, stdev=3.42, color median=5.99, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=18.0, max=26, stdev=4.46, color median=9.32, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 177×199 | 0.889 | (58,44,42) | `ede1e38103e1c3ef` |
| `se` | 216×230 | 0.939 | (56,38,39) | `fdfbd96000c0c1f7` |
| `s` | 102×230 | 0.444 | (58,45,44) | `ffffdbc30000dbff` |
| `sw` | 199×230 | 0.865 | (57,37,38) | `bf978707080183c7` |
| `w` | 102×230 | 0.444 | (57,42,41) | `ffff878080c3ffff` |
| `nw` | 180×230 | 0.783 | (51,36,37) | `efef878180040f8f` |
| `n` | 172×229 | 0.751 | (55,41,39) | `dbdbc3c3812499db` |
| `ne` | 180×230 | 0.783 | (51,36,37) | `f7f7e1810120f0f1` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 974×230 | 4.235 | (58,57,60) | `7f5e561000767777` |
| `se` | 984×236 | 4.170 | (58,39,40) | `ffffaa0800022aff` |
| `s` | 945×236 | 4.004 | (58,44,44) | `ff7e5e5a4242427e` |
| `sw` | 967×236 | 4.098 | (59,38,39) | `ff7f5455000054ff` |
| `w` | 973×230 | 4.230 | (58,57,60) | `fe6a6a08006eeeee` |
| `nw` | 948×236 | 4.017 | (54,38,38) | `ffff5f4a00405457` |
| `n` | 936×230 | 4.070 | (54,39,37) | `ff7e5a7a424242ff` |
| `ne` | 948×236 | 4.017 | (54,38,38) | `fffffa5200002aea` |

</details>

**Most distant idle pairs (hash):**

- `se` vs `nw`: hamming=26, color=5.28, aspect_diff=0.1565
- `nw` vs `ne`: hamming=26, color=0.0, aspect_diff=0.0
- `e` vs `n`: hamming=24, color=4.62, aspect_diff=0.1384
- `se` vs `sw`: hamming=24, color=1.74, aspect_diff=0.0739
- `sw` vs `ne`: hamming=24, color=5.99, aspect_diff=0.0826

### `zombie_colossus`

- **Recommendation:** `keep`
- **Idle dirs present:** e, se, s, sw, w, nw, n, ne
- **Walk dirs present:** e, se, s, sw, w, nw, n, ne
- **Base:** yes · **Walk base:** yes
- **Notes:** idle: directions consistent with single subject identity | walk: 2 soft outlier(s) but not enough evidence for identity split (inter-hash=0.0); likely pose/angle variation — keep

**Identity clusters (idle):**

- Cluster **A**: dirs=`['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne']` · representative=`n`

**Outliers:**

- `walk_e` — distance=0.5843 — [walk] color vs median=58.4 (≥55.0)
- `walk_w` — distance=0.5843 — [walk] color vs median=58.4 (≥55.0)

**Idle pairwise stats:** hash median=23.0, max=30, stdev=3.68, color median=13.4, inter-cluster hash=0.0

**Walk pairwise stats:** hash median=15.0, max=18, stdev=5.24, color median=28.45, inter-cluster hash=0.0

<details><summary>Idle per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 102×230 | 0.444 | (102,99,89) | `ff72f3e9e1e9efff` |
| `se` | 158×230 | 0.687 | (108,107,100) | `ff939346095debdf` |
| `s` | 102×230 | 0.444 | (106,107,93) | `ff5a24a599dbffff` |
| `sw` | 158×230 | 0.687 | (108,107,100) | `ffc9c96290bad7fb` |
| `w` | 102×230 | 0.444 | (102,101,89) | `ff4e8f978797f7ff` |
| `nw` | 174×230 | 0.756 | (93,92,86) | `8701d1f7c6f3e7ff` |
| `n` | 102×230 | 0.444 | (96,95,86) | `ffff420081ffffff` |
| `ne` | 174×230 | 0.756 | (93,92,86) | `e1808bef63cfe7ff` |

</details>

<details><summary>Walk per-direction metrics</summary>

| Dir | Content | Aspect | Mean RGB | aHash |
|---|---|---:|---|---|
| `e` | 953×230 | 4.144 | (58,56,57) | `760a5a52525a5eff` |
| `se` | 926×236 | 3.924 | (109,108,101) | `ff5e424240ffffff` |
| `s` | 870×230 | 3.783 | (102,103,91) | `ff5a424242ffffff` |
| `sw` | 926×236 | 3.924 | (109,108,101) | `ff5a424202ffffff` |
| `w` | 953×230 | 4.144 | (58,56,57) | `6e505a4a4a5a7aff` |
| `nw` | 942×236 | 3.991 | (93,92,86) | `54004a7a52ffffff` |
| `n` | 870×230 | 3.783 | (92,92,84) | `ff7f5a4242ffffff` |
| `ne` | 942×236 | 3.991 | (93,92,86) | `2a00525e42ffffff` |

</details>

**Most distant idle pairs (hash):**

- `nw` vs `n`: hamming=30, color=4.37, aspect_diff=0.313
- `n` vs `ne`: hamming=30, color=4.37, aspect_diff=0.313
- `s` vs `nw`: hamming=28, color=21.28, aspect_diff=0.313
- `s` vs `ne`: hamming=28, color=21.28, aspect_diff=0.313
- `e` vs `w`: hamming=27, color=1.68, aspect_diff=0.0

---

## Interpretation guide

- **keep** — directions look like one creature under different facings; hash distances are in the normal pose/angle range.
- **fill_missing** — one or more of the 8 idle/walk facings (or base) are absent.
- **split** — two or more identity groups with high inter-cluster average-hash distance (conservative threshold); consider promoting a subset to a new enemy stem with `_alt` suffix.
- Facing-only differences (mirrors, foreshortening) typically stay under the split threshold.
