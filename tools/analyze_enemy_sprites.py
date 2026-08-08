#!/usr/bin/env python3
"""
Analyze HiVE SWARM enemy directional sprites for cross-direction consistency.

For each enemy stem, loads idle/walk direction PNGs, computes content metrics
(alpha bbox, size, mean RGB, average hash), pairwise distances, outlier flags,
and identity clusters. Writes JSON + Markdown reports.

Does NOT delete or modify any sprite files.
"""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from PIL import Image
import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SPRITE_DIR = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
OUT_JSON = Path(r"D:\Dev\HiveSwarm\tools\sprite_direction_report.json")
OUT_MD = Path(r"D:\Dev\HiveSwarm\tools\sprite_direction_report.md")

ENEMY_STEMS = [
    "shambler",
    "runner",
    "crawler",
    "necro_node",
    "brute",
    "armored_dead",
    "mutant_enforcer",
    "zombie_colossus",
]

DIRECTIONS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]

# Average-hash size (content region resized to this before hashing)
HASH_SIZE = 8  # 8x8 bits = 64-bit aHash (normalized content is 64x64 first)

# Thresholds (conservative: only flag clear subject mismatches, not angle diffs)
# Hamming distance on 64-bit aHash: max 64
HASH_OUTLIER_Z = 2.0          # z-score of median pairwise hash dist to median
HASH_HARD_OUTLIER = 22        # absolute hamming vs set median hash (high = different subject)
COLOR_HARD_OUTLIER = 55.0     # Euclidean mean-RGB distance vs set median color
ASPECT_HARD_OUTLIER = 0.45    # |aspect_a - aspect_b| absolute

# Clustering: agglomerative on combined distance; split only if clusters diverge hard
CLUSTER_HASH_LINK = 18        # max hamming within same identity cluster (median-link-ish)
CLUSTER_COMBINED_SPLIT = 0.55 # normalized combined distance threshold for new cluster

# Recommendation policy
# "split" only when ≥2 substantial clusters with high inter-cluster hash distance
SPLIT_MIN_CLUSTER_SIZE = 2
SPLIT_INTER_HASH_MIN = 20


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

@dataclass
class SpriteMetrics:
    path: str
    dir_key: str          # e.g. "e", "walk_ne", "base", "walk_base"
    set_name: str         # "idle" | "walk" | "base"
    width: int
    height: int
    bbox: tuple[int, int, int, int] | None  # left, top, right, bottom (exclusive)
    content_w: int
    content_h: int
    aspect: float         # content_w / content_h (1.0 if empty)
    opaque_count: int
    mean_rgb: tuple[float, float, float]
    ahash: int            # 64-bit average hash of content region


def content_bbox(img: Image.Image, alpha_thresh: int = 16) -> tuple[int, int, int, int] | None:
    """Return (L, T, R, B) exclusive content bbox from alpha, or None if empty."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    arr = np.asarray(img)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > alpha_thresh)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def mean_opaque_rgb(img: Image.Image, alpha_thresh: int = 16) -> tuple[tuple[float, float, float], int]:
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    arr = np.asarray(img).astype(np.float64)
    mask = arr[:, :, 3] > alpha_thresh
    n = int(mask.sum())
    if n == 0:
        return (0.0, 0.0, 0.0), 0
    rgb = arr[:, :, :3][mask]
    return (float(rgb[:, 0].mean()), float(rgb[:, 1].mean()), float(rgb[:, 2].mean())), n


def average_hash_content(img: Image.Image, bbox: tuple[int, int, int, int] | None) -> int:
    """
    Perceptual average hash of content region:
    crop to alpha bbox -> resize to 64x64 -> grayscale -> 8x8 mean binary hash.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    if bbox is None:
        # solid empty hash
        return 0
    crop = img.crop(bbox)
    # Composite on neutral mid-gray so transparent doesn't bias white/black
    bg = Image.new("RGBA", crop.size, (128, 128, 128, 255))
    comp = Image.alpha_composite(bg, crop).convert("L")
    # Normalize geometry first
    big = comp.resize((64, 64), Image.Resampling.LANCZOS)
    small = big.resize((HASH_SIZE, HASH_SIZE), Image.Resampling.LANCZOS)
    pixels = list(small.get_flattened_data()) if hasattr(small, "get_flattened_data") else list(small.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for i, p in enumerate(pixels):
        if p >= avg:
            bits |= 1 << i
    return bits


def hamming64(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def color_dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def load_metrics(path: Path, dir_key: str, set_name: str) -> SpriteMetrics | None:
    if not path.is_file():
        return None
    try:
        with Image.open(path) as im:
            im = im.convert("RGBA")
            w, h = im.size
            bb = content_bbox(im)
            mean_rgb, opaque = mean_opaque_rgb(im)
            ah = average_hash_content(im, bb)
            if bb is None:
                cw, ch, aspect = 0, 0, 1.0
            else:
                cw = bb[2] - bb[0]
                ch = bb[3] - bb[1]
                aspect = (cw / ch) if ch > 0 else 1.0
            return SpriteMetrics(
                path=str(path),
                dir_key=dir_key,
                set_name=set_name,
                width=w,
                height=h,
                bbox=bb,
                content_w=cw,
                content_h=ch,
                aspect=aspect,
                opaque_count=opaque,
                mean_rgb=mean_rgb,
                ahash=ah,
            )
    except Exception as e:
        print(f"  WARN: failed to load {path}: {e}")
        return None


# ---------------------------------------------------------------------------
# Pairwise / outlier / cluster
# ---------------------------------------------------------------------------

def pairwise_stats(metrics: list[SpriteMetrics]) -> dict[str, Any]:
    """Build distance matrices and summary stats for a set of direction sprites."""
    n = len(metrics)
    keys = [m.dir_key for m in metrics]
    hash_mat = [[0] * n for _ in range(n)]
    color_mat = [[0.0] * n for _ in range(n)]
    aspect_mat = [[0.0] * n for _ in range(n)]
    pairs: list[dict[str, Any]] = []

    for i in range(n):
        for j in range(i + 1, n):
            hd = hamming64(metrics[i].ahash, metrics[j].ahash)
            cd = color_dist(metrics[i].mean_rgb, metrics[j].mean_rgb)
            ad = abs(metrics[i].aspect - metrics[j].aspect)
            hash_mat[i][j] = hash_mat[j][i] = hd
            color_mat[i][j] = color_mat[j][i] = cd
            aspect_mat[i][j] = aspect_mat[j][i] = ad
            pairs.append(
                {
                    "a": keys[i],
                    "b": keys[j],
                    "hash_hamming": hd,
                    "color_dist": round(cd, 2),
                    "aspect_diff": round(ad, 4),
                }
            )

    hash_vals = [p["hash_hamming"] for p in pairs]
    color_vals = [p["color_dist"] for p in pairs]
    aspect_vals = [p["aspect_diff"] for p in pairs]

    def safe_median(xs: list) -> float:
        return float(statistics.median(xs)) if xs else 0.0

    def safe_stdev(xs: list) -> float:
        return float(statistics.pstdev(xs)) if len(xs) > 1 else 0.0

    return {
        "keys": keys,
        "hash_mat": hash_mat,
        "color_mat": color_mat,
        "aspect_mat": aspect_mat,
        "pairs": sorted(pairs, key=lambda p: -p["hash_hamming"]),
        "hash_median": safe_median(hash_vals),
        "hash_stdev": safe_stdev(hash_vals),
        "hash_max": max(hash_vals) if hash_vals else 0,
        "color_median": safe_median(color_vals),
        "color_stdev": safe_stdev(color_vals),
        "aspect_median": safe_median(aspect_vals),
    }


def median_hash(metrics: list[SpriteMetrics]) -> int:
    """Bit-wise majority vote hash as robust 'median' identity fingerprint."""
    if not metrics:
        return 0
    bits = [0] * 64
    for m in metrics:
        for b in range(64):
            if (m.ahash >> b) & 1:
                bits[b] += 1
    half = len(metrics) / 2.0
    out = 0
    for b in range(64):
        if bits[b] >= half:
            out |= 1 << b
    return out


def median_color(metrics: list[SpriteMetrics]) -> tuple[float, float, float]:
    if not metrics:
        return (0.0, 0.0, 0.0)
    return (
        float(statistics.median([m.mean_rgb[0] for m in metrics])),
        float(statistics.median([m.mean_rgb[1] for m in metrics])),
        float(statistics.median([m.mean_rgb[2] for m in metrics])),
    )


def find_outliers(metrics: list[SpriteMetrics], stats: dict[str, Any]) -> list[dict[str, Any]]:
    """Flag directions that diverge from the set median (likely wrong subject/pose style)."""
    if len(metrics) < 3:
        return []

    med_h = median_hash(metrics)
    med_c = median_color(metrics)
    med_aspect = float(statistics.median([m.aspect for m in metrics]))

    # Per-sprite mean hash distance to all others
    keys = stats["keys"]
    hash_mat = stats["hash_mat"]
    mean_hash_to_others: dict[str, float] = {}
    for i, k in enumerate(keys):
        others = [hash_mat[i][j] for j in range(len(keys)) if j != i]
        mean_hash_to_others[k] = sum(others) / len(others) if others else 0.0

    vals = list(mean_hash_to_others.values())
    med_mean = float(statistics.median(vals))
    std_mean = float(statistics.pstdev(vals)) if len(vals) > 1 else 0.0

    outliers: list[dict[str, Any]] = []
    for m in metrics:
        reasons: list[str] = []
        dist_hash = hamming64(m.ahash, med_h)
        dist_color = color_dist(m.mean_rgb, med_c)
        dist_aspect = abs(m.aspect - med_aspect)
        mean_to_peers = mean_hash_to_others[m.dir_key]

        z = (mean_to_peers - med_mean) / std_mean if std_mean > 1e-6 else 0.0

        score = 0.0
        if dist_hash >= HASH_HARD_OUTLIER:
            reasons.append(f"hash vs median={dist_hash} (≥{HASH_HARD_OUTLIER})")
            score = max(score, dist_hash / 64.0)
        if z >= HASH_OUTLIER_Z and mean_to_peers > stats["hash_median"] + 4:
            reasons.append(f"mean hash-to-peers={mean_to_peers:.1f} (z={z:.2f})")
            score = max(score, min(1.0, mean_to_peers / 32.0))
        if dist_color >= COLOR_HARD_OUTLIER:
            reasons.append(f"color vs median={dist_color:.1f} (≥{COLOR_HARD_OUTLIER})")
            score = max(score, min(1.0, dist_color / 100.0))
        if dist_aspect >= ASPECT_HARD_OUTLIER:
            reasons.append(f"aspect vs median={dist_aspect:.3f} (≥{ASPECT_HARD_OUTLIER})")
            score = max(score, min(1.0, dist_aspect))

        # Empty / nearly empty content
        if m.opaque_count < 50:
            reasons.append(f"nearly empty opaque_count={m.opaque_count}")
            score = max(score, 0.9)

        if reasons:
            outliers.append(
                {
                    "dir": m.dir_key,
                    "reason": "; ".join(reasons),
                    "distance": round(score, 4),
                    "hash_vs_median": dist_hash,
                    "color_vs_median": round(dist_color, 2),
                    "aspect_vs_median": round(dist_aspect, 4),
                    "mean_hash_to_peers": round(mean_to_peers, 2),
                }
            )

    outliers.sort(key=lambda o: -o["distance"])
    return outliers


def combined_distance(i: int, j: int, stats: dict[str, Any]) -> float:
    """Normalized combined distance in [0, ~1+]."""
    hd = stats["hash_mat"][i][j] / 64.0
    cd = min(1.0, stats["color_mat"][i][j] / 80.0)
    ad = min(1.0, stats["aspect_mat"][i][j] / 0.6)
    # Hash dominates identity; color secondary; aspect weak
    return 0.65 * hd + 0.25 * cd + 0.10 * ad


def cluster_directions(metrics: list[SpriteMetrics], stats: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Single-linkage agglomerative clustering on combined distance.
    Conservative: only forms separate clusters when link distance is high
    (different character identity, not mere facing).
    """
    n = len(metrics)
    if n == 0:
        return []
    if n == 1:
        return [{"id": "A", "dirs": [metrics[0].dir_key], "representative": metrics[0].dir_key}]

    # Union-find
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Edges sorted by combined distance
    edges: list[tuple[float, int, int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            cd = combined_distance(i, j, stats)
            hd = stats["hash_mat"][i][j]
            edges.append((cd, hd, i, j))
    edges.sort(key=lambda e: e[0])

    for cd, hd, i, j in edges:
        # Merge only if both combined and absolute hash are within identity band
        if cd <= CLUSTER_COMBINED_SPLIT and hd <= CLUSTER_HASH_LINK + 6:
            union(i, j)

    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    # Label clusters A, B, C... by size desc then first dir name
    ordered = sorted(
        groups.values(),
        key=lambda idxs: (-len(idxs), metrics[min(idxs)].dir_key),
    )

    clusters: list[dict[str, Any]] = []
    for ci, idxs in enumerate(ordered):
        cid = chr(ord("A") + ci) if ci < 26 else f"C{ci}"
        dirs = [metrics[i].dir_key for i in sorted(idxs, key=lambda i: DIRECTIONS.index(metrics[i].dir_key) if metrics[i].dir_key in DIRECTIONS else 99)]
        # Representative: closest to cluster median hash
        sub = [metrics[i] for i in idxs]
        mh = median_hash(sub)
        rep_i = min(idxs, key=lambda i: hamming64(metrics[i].ahash, mh))
        # Intra hash stats
        intra = []
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                intra.append(stats["hash_mat"][idxs[a]][idxs[b]])
        clusters.append(
            {
                "id": cid,
                "dirs": dirs,
                "representative": metrics[rep_i].dir_key,
                "size": len(dirs),
                "intra_hash_median": float(statistics.median(intra)) if intra else 0.0,
            }
        )
    return clusters


def inter_cluster_hash(metrics: list[SpriteMetrics], clusters: list[dict[str, Any]], stats: dict[str, Any]) -> float:
    """Median pairwise hash distance between different clusters (0 if single cluster)."""
    key_to_i = {m.dir_key: i for i, m in enumerate(metrics)}
    if len(clusters) < 2:
        return 0.0
    dists: list[int] = []
    for a in range(len(clusters)):
        for b in range(a + 1, len(clusters)):
            for da in clusters[a]["dirs"]:
                for db in clusters[b]["dirs"]:
                    dists.append(stats["hash_mat"][key_to_i[da]][key_to_i[db]])
    return float(statistics.median(dists)) if dists else 0.0


def recommend(
    metrics: list[SpriteMetrics],
    clusters: list[dict[str, Any]],
    outliers: list[dict[str, Any]],
    missing: list[str],
    stats: dict[str, Any],
) -> tuple[str, dict[str, Any] | None, str]:
    """
    Conservative recommendation:
    - fill_missing if any of 8 dirs missing
    - split only when ≥2 clusters of size≥2 with high inter-cluster hash
      OR one large primary + small variant cluster that is clearly different subject
    - else keep
    """
    notes: list[str] = []

    if missing:
        notes.append(f"missing directions: {', '.join(missing)}")

    inter = inter_cluster_hash(metrics, clusters, stats)
    substantial = [c for c in clusters if c["size"] >= SPLIT_MIN_CLUSTER_SIZE]
    singleton_outliers = [c for c in clusters if c["size"] == 1]

    # Strong split: multiple multi-member clusters with high inter hash
    if len(substantial) >= 2 and inter >= SPLIT_INTER_HASH_MIN:
        primary = max(substantial, key=lambda c: c["size"])
        variants = [c for c in substantial if c["id"] != primary["id"]]
        # Prefer largest non-primary as the alt variant group
        variant = max(variants, key=lambda c: c["size"])
        proposal = {
            "primary_dirs": primary["dirs"],
            "variant_dirs": variant["dirs"],
            "variant_name_suffix": "_alt",
            "inter_cluster_hash_median": round(inter, 2),
            "note": "Multiple multi-dir clusters with high hash separation — likely different subjects mixed in one stem.",
        }
        # Include singleton outliers in variant if they are closer to variant? keep simple
        notes.append(
            f"SPLIT: {len(clusters)} identity clusters, inter-hash median={inter:.1f}"
        )
        return "split", proposal, "; ".join(notes)

    # Soft split: primary cluster + 1+ singleton/small clusters that are hard outliers
    hard_outlier_dirs = {
        o["dir"]
        for o in outliers
        if o.get("hash_vs_median", 0) >= HASH_HARD_OUTLIER
        or o.get("distance", 0) >= 0.5
    }
    if (
        len(clusters) >= 2
        and hard_outlier_dirs
        and inter >= SPLIT_INTER_HASH_MIN
        and any(c["size"] >= 3 for c in clusters)
    ):
        primary = max(clusters, key=lambda c: c["size"])
        variant_dirs = []
        for c in clusters:
            if c["id"] == primary["id"]:
                continue
            variant_dirs.extend(c["dirs"])
        # Only split if variant set is non-trivial and clearly different
        if len(variant_dirs) >= 2 and inter >= SPLIT_INTER_HASH_MIN:
            proposal = {
                "primary_dirs": primary["dirs"],
                "variant_dirs": variant_dirs,
                "variant_name_suffix": "_alt",
                "inter_cluster_hash_median": round(inter, 2),
                "note": "Primary identity plus secondary group with high hash distance.",
            }
            notes.append(
                f"SPLIT: primary={primary['dirs']} vs variant={variant_dirs}, inter-hash={inter:.1f}"
            )
            return "split", proposal, "; ".join(notes)

    if missing:
        notes.append("recommend generating or mirroring missing facings")
        return "fill_missing", None, "; ".join(notes)

    if outliers:
        notes.append(
            f"{len(outliers)} soft outlier(s) but not enough evidence for identity split "
            f"(inter-hash={inter:.1f}); likely pose/angle variation — keep"
        )
    else:
        notes.append("directions consistent with single subject identity")

    if singleton_outliers and inter > 0:
        notes.append(
            f"singleton cluster(s) {[c['dirs'][0] for c in singleton_outliers]} — review manually, not auto-splitting"
        )

    return "keep", None, "; ".join(notes)


# ---------------------------------------------------------------------------
# Per-enemy analysis
# ---------------------------------------------------------------------------

def discover_files(stem: str) -> dict[str, Any]:
    """Map expected names to paths; record presence."""
    base = SPRITE_DIR / f"{stem}.png"
    walk_base = SPRITE_DIR / f"{stem}_walk.png"
    idle: dict[str, Path] = {}
    walk: dict[str, Path] = {}
    for d in DIRECTIONS:
        p = SPRITE_DIR / f"{stem}_{d}.png"
        if p.is_file():
            idle[d] = p
        pw = SPRITE_DIR / f"{stem}_walk_{d}.png"
        if pw.is_file():
            walk[d] = pw
    return {
        "base": base if base.is_file() else None,
        "walk_base": walk_base if walk_base.is_file() else None,
        "idle": idle,
        "walk": walk,
        "missing_idle": [d for d in DIRECTIONS if d not in idle],
        "missing_walk": [d for d in DIRECTIONS if d not in walk],
    }


def analyze_set(
    label: str,
    path_map: dict[str, Path],
    missing: list[str],
) -> dict[str, Any]:
    metrics: list[SpriteMetrics] = []
    for d in DIRECTIONS:
        if d not in path_map:
            continue
        m = load_metrics(path_map[d], d, label)
        if m:
            metrics.append(m)

    if not metrics:
        return {
            "dirs_present": [],
            "dirs_missing": missing,
            "per_dir": {},
            "outliers": [],
            "clusters": [],
            "pairwise_top": [],
            "stats_summary": {},
            "recommendation": "fill_missing" if missing else "keep",
            "split_proposal": None,
            "notes": "no direction sprites found",
        }

    stats = pairwise_stats(metrics)
    outliers = find_outliers(metrics, stats)
    clusters = cluster_directions(metrics, stats)
    rec, proposal, notes = recommend(metrics, clusters, outliers, missing, stats)

    per_dir = {}
    for m in metrics:
        per_dir[m.dir_key] = {
            "file": Path(m.path).name,
            "canvas": [m.width, m.height],
            "bbox": list(m.bbox) if m.bbox else None,
            "content_size": [m.content_w, m.content_h],
            "aspect": round(m.aspect, 4),
            "opaque_count": m.opaque_count,
            "mean_rgb": [round(c, 2) for c in m.mean_rgb],
            "ahash_hex": f"{m.ahash:016x}",
        }

    return {
        "dirs_present": [m.dir_key for m in metrics],
        "dirs_missing": missing,
        "per_dir": per_dir,
        "outliers": outliers,
        "clusters": [
            {
                "id": c["id"],
                "dirs": c["dirs"],
                "representative": c["representative"],
            }
            for c in clusters
        ],
        "clusters_detail": clusters,
        "pairwise_top": stats["pairs"][:12],
        "stats_summary": {
            "hash_median": round(stats["hash_median"], 2),
            "hash_stdev": round(stats["hash_stdev"], 2),
            "hash_max": stats["hash_max"],
            "color_median": round(stats["color_median"], 2),
            "aspect_median": round(stats["aspect_median"], 4),
            "inter_cluster_hash_median": round(
                inter_cluster_hash(metrics, clusters, stats), 2
            ),
        },
        "recommendation": rec,
        "split_proposal": proposal,
        "notes": notes,
    }


def analyze_enemy(stem: str) -> dict[str, Any]:
    print(f"Analyzing {stem}...")
    files = discover_files(stem)

    idle_result = analyze_set("idle", files["idle"], files["missing_idle"])
    walk_result = analyze_set("walk", files["walk"], files["missing_walk"])

    # Base / walk base metrics (informational)
    base_info = None
    if files["base"]:
        bm = load_metrics(files["base"], "base", "base")
        if bm:
            base_info = {
                "file": Path(bm.path).name,
                "content_size": [bm.content_w, bm.content_h],
                "mean_rgb": [round(c, 2) for c in bm.mean_rgb],
                "ahash_hex": f"{bm.ahash:016x}",
            }
    walk_base_info = None
    if files["walk_base"]:
        wm = load_metrics(files["walk_base"], "walk_base", "base")
        if wm:
            walk_base_info = {
                "file": Path(wm.path).name,
                "content_size": [wm.content_w, wm.content_h],
                "mean_rgb": [round(c, 2) for c in wm.mean_rgb],
                "ahash_hex": f"{wm.ahash:016x}",
            }

    # Top-level recommendation: idle is identity authority; walk can escalate fill_missing
    idle_rec = idle_result["recommendation"]
    walk_rec = walk_result["recommendation"]

    if idle_rec == "split":
        top_rec = "split"
        top_proposal = idle_result["split_proposal"]
    elif walk_rec == "split" and idle_rec != "split":
        # Walk-only split is weaker signal; only promote if idle also multi-cluster soft
        if len(idle_result["clusters"]) >= 2 and idle_result["stats_summary"].get(
            "inter_cluster_hash_median", 0
        ) >= SPLIT_INTER_HASH_MIN * 0.85:
            top_rec = "split"
            top_proposal = walk_result["split_proposal"]
        else:
            top_rec = idle_rec if idle_rec != "keep" else (
                "fill_missing" if walk_rec == "fill_missing" else "keep"
            )
            top_proposal = None
    elif idle_rec == "fill_missing" or walk_rec == "fill_missing":
        top_rec = "fill_missing"
        top_proposal = None
    else:
        top_rec = "keep"
        top_proposal = None

    # dirs_present: idle direction keys (primary report surface)
    dirs_present = idle_result["dirs_present"]
    # outliers: primarily idle; annotate walk outliers separately
    outliers = list(idle_result["outliers"])
    for o in walk_result["outliers"]:
        outliers.append(
            {
                "dir": f"walk_{o['dir']}",
                "reason": f"[walk] {o['reason']}",
                "distance": o["distance"],
            }
        )

    clusters = idle_result["clusters"]

    missing_all = []
    if files["missing_idle"]:
        missing_all.extend(files["missing_idle"])
    if files["missing_walk"]:
        missing_all.extend([f"walk_{d}" for d in files["missing_walk"]])
    if files["base"] is None:
        missing_all.append("base")
    if files["walk_base"] is None:
        missing_all.append("walk_base")

    return {
        "dirs_present": dirs_present,
        "walk_dirs_present": walk_result["dirs_present"],
        "missing": missing_all,
        "has_base": files["base"] is not None,
        "has_walk_base": files["walk_base"] is not None,
        "base": base_info,
        "walk_base": walk_base_info,
        "outliers": outliers,
        "clusters": clusters,
        "recommendation": top_rec,
        "split_proposal": top_proposal,
        "idle": idle_result,
        "walk": walk_result,
        "notes": f"idle: {idle_result['notes']} | walk: {walk_result['notes']}",
    }


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def write_json(report: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    # Strip heavy detail for cleaner top-level; keep full idle/walk inside
    slim = {
        "sprite_dir": str(SPRITE_DIR),
        "hash_method": "average-hash 8x8 of alpha-bbox content resized to 64x64, composited on mid-gray",
        "thresholds": {
            "HASH_HARD_OUTLIER": HASH_HARD_OUTLIER,
            "COLOR_HARD_OUTLIER": COLOR_HARD_OUTLIER,
            "ASPECT_HARD_OUTLIER": ASPECT_HARD_OUTLIER,
            "CLUSTER_COMBINED_SPLIT": CLUSTER_COMBINED_SPLIT,
            "CLUSTER_HASH_LINK": CLUSTER_HASH_LINK,
            "SPLIT_INTER_HASH_MIN": SPLIT_INTER_HASH_MIN,
        },
        "enemies": {},
    }
    for stem, data in report["enemies"].items():
        slim["enemies"][stem] = {
            "dirs_present": data["dirs_present"],
            "walk_dirs_present": data["walk_dirs_present"],
            "missing": data["missing"],
            "has_base": data["has_base"],
            "has_walk_base": data["has_walk_base"],
            "outliers": data["outliers"],
            "clusters": data["clusters"],
            "recommendation": data["recommendation"],
            "split_proposal": data["split_proposal"],
            "notes": data["notes"],
            "idle_stats": data["idle"].get("stats_summary", {}),
            "walk_stats": data["walk"].get("stats_summary", {}),
            "idle_per_dir": data["idle"].get("per_dir", {}),
            "walk_per_dir": data["walk"].get("per_dir", {}),
            "idle_pairwise_top": data["idle"].get("pairwise_top", []),
            "walk_pairwise_top": data["walk"].get("pairwise_top", []),
        }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(slim, f, indent=2)
    print(f"Wrote {OUT_JSON}")


def write_markdown(report: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Enemy Directional Sprite Consistency Report")
    lines.append("")
    lines.append(f"**Sprite dir:** `{SPRITE_DIR}`")
    lines.append("")
    lines.append(
        "Method: alpha-content bbox → resize 64×64 → 8×8 average hash (64-bit); "
        "mean RGB of opaque pixels; pairwise Hamming + color + aspect. "
        "Outliers vs set median. Clusters via conservative single-linkage on combined distance. "
        "**split** only when directions clearly look like different subjects (high inter-cluster hash)."
    )
    lines.append("")
    lines.append("## Summary table")
    lines.append("")
    lines.append(
        "| Enemy | Idle dirs | Walk dirs | Missing | Idle clusters | Outliers | Recommendation |"
    )
    lines.append("|---|---:|---:|---|---:|---:|---|")

    for stem in ENEMY_STEMS:
        d = report["enemies"][stem]
        miss = ", ".join(d["missing"]) if d["missing"] else "—"
        n_out = len(d["outliers"])
        lines.append(
            f"| `{stem}` | {len(d['dirs_present'])}/8 | {len(d['walk_dirs_present'])}/8 | "
            f"{miss} | {len(d['clusters'])} | {n_out} | **{d['recommendation']}** |"
        )

    lines.append("")
    lines.append("## Per-enemy detail")
    lines.append("")

    for stem in ENEMY_STEMS:
        d = report["enemies"][stem]
        lines.append(f"### `{stem}`")
        lines.append("")
        lines.append(f"- **Recommendation:** `{d['recommendation']}`")
        lines.append(f"- **Idle dirs present:** {', '.join(d['dirs_present']) or 'none'}")
        lines.append(f"- **Walk dirs present:** {', '.join(d['walk_dirs_present']) or 'none'}")
        if d["missing"]:
            lines.append(f"- **Missing:** {', '.join(d['missing'])}")
        lines.append(f"- **Base:** {'yes' if d['has_base'] else 'NO'} · **Walk base:** {'yes' if d['has_walk_base'] else 'NO'}")
        lines.append(f"- **Notes:** {d['notes']}")
        lines.append("")

        # Clusters
        lines.append("**Identity clusters (idle):**")
        lines.append("")
        for c in d["clusters"]:
            lines.append(
                f"- Cluster **{c['id']}**: dirs=`{c['dirs']}` · representative=`{c['representative']}`"
            )
        if not d["clusters"]:
            lines.append("- _(none)_")
        lines.append("")

        if d["split_proposal"]:
            sp = d["split_proposal"]
            lines.append("**Split proposal:**")
            lines.append("")
            lines.append(f"- Primary dirs: `{sp.get('primary_dirs')}`")
            lines.append(f"- Variant dirs: `{sp.get('variant_dirs')}`")
            lines.append(f"- Variant suffix: `{sp.get('variant_name_suffix')}`")
            if sp.get("note"):
                lines.append(f"- Note: {sp['note']}")
            lines.append("")

        # Outliers
        if d["outliers"]:
            lines.append("**Outliers:**")
            lines.append("")
            for o in d["outliers"]:
                lines.append(
                    f"- `{o['dir']}` — distance={o.get('distance')} — {o.get('reason')}"
                )
            lines.append("")
        else:
            lines.append("**Outliers:** none flagged")
            lines.append("")

        # Stats
        ist = d["idle"].get("stats_summary", {})
        wst = d["walk"].get("stats_summary", {})
        lines.append("**Idle pairwise stats:** "
                     f"hash median={ist.get('hash_median')}, max={ist.get('hash_max')}, "
                     f"stdev={ist.get('hash_stdev')}, color median={ist.get('color_median')}, "
                     f"inter-cluster hash={ist.get('inter_cluster_hash_median')}")
        lines.append("")
        lines.append("**Walk pairwise stats:** "
                     f"hash median={wst.get('hash_median')}, max={wst.get('hash_max')}, "
                     f"stdev={wst.get('hash_stdev')}, color median={wst.get('color_median')}, "
                     f"inter-cluster hash={wst.get('inter_cluster_hash_median')}")
        lines.append("")

        # Per-dir table idle
        lines.append("<details><summary>Idle per-direction metrics</summary>")
        lines.append("")
        lines.append("| Dir | Content | Aspect | Mean RGB | aHash |")
        lines.append("|---|---|---:|---|---|")
        for dk in DIRECTIONS:
            pd = d["idle"].get("per_dir", {}).get(dk)
            if not pd:
                lines.append(f"| `{dk}` | MISSING | | | |")
                continue
            rgb = pd["mean_rgb"]
            lines.append(
                f"| `{dk}` | {pd['content_size'][0]}×{pd['content_size'][1]} | "
                f"{pd['aspect']:.3f} | ({rgb[0]:.0f},{rgb[1]:.0f},{rgb[2]:.0f}) | `{pd['ahash_hex']}` |"
            )
        lines.append("")
        lines.append("</details>")
        lines.append("")

        lines.append("<details><summary>Walk per-direction metrics</summary>")
        lines.append("")
        lines.append("| Dir | Content | Aspect | Mean RGB | aHash |")
        lines.append("|---|---|---:|---|---|")
        for dk in DIRECTIONS:
            pd = d["walk"].get("per_dir", {}).get(dk)
            if not pd:
                lines.append(f"| `{dk}` | MISSING | | | |")
                continue
            rgb = pd["mean_rgb"]
            lines.append(
                f"| `{dk}` | {pd['content_size'][0]}×{pd['content_size'][1]} | "
                f"{pd['aspect']:.3f} | ({rgb[0]:.0f},{rgb[1]:.0f},{rgb[2]:.0f}) | `{pd['ahash_hex']}` |"
            )
        lines.append("")
        lines.append("</details>")
        lines.append("")

        # Top distant pairs
        top = d["idle"].get("pairwise_top", [])[:5]
        if top:
            lines.append("**Most distant idle pairs (hash):**")
            lines.append("")
            for p in top:
                lines.append(
                    f"- `{p['a']}` vs `{p['b']}`: hamming={p['hash_hamming']}, "
                    f"color={p['color_dist']}, aspect_diff={p['aspect_diff']}"
                )
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Interpretation guide")
    lines.append("")
    lines.append(
        "- **keep** — directions look like one creature under different facings; "
        "hash distances are in the normal pose/angle range."
    )
    lines.append(
        "- **fill_missing** — one or more of the 8 idle/walk facings (or base) are absent."
    )
    lines.append(
        "- **split** — two or more identity groups with high inter-cluster average-hash distance "
        "(conservative threshold); consider promoting a subset to a new enemy stem with `_alt` suffix."
    )
    lines.append(
        "- Facing-only differences (mirrors, foreshortening) typically stay under the split threshold."
    )
    lines.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {OUT_MD}")


def main() -> int:
    report: dict[str, Any] = {"enemies": {}}
    for stem in ENEMY_STEMS:
        report["enemies"][stem] = analyze_enemy(stem)

    write_json(report)
    write_markdown(report)

    # Console summary
    print("\n=== SUMMARY ===")
    for stem in ENEMY_STEMS:
        d = report["enemies"][stem]
        print(
            f"  {stem:20s}  rec={d['recommendation']:12s}  "
            f"idle={len(d['dirs_present'])}/8  walk={len(d['walk_dirs_present'])}/8  "
            f"clusters={len(d['clusters'])}  outliers={len(d['outliers'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
