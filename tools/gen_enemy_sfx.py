"""Synthesize per-enemy attack/die SFX as MP3 via ffmpeg."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from gen_weapon_sfx import OUT, SR, env, to_mp3, write_wav

RNG = np.random.default_rng(20260818)


def noise(n, seed_off=0):
    return RNG.standard_normal(n)


def tone(n, hz):
    t = np.arange(n) / SR
    return np.sin(2 * math.pi * hz * t)


def growl(n, hz, decay=10):
    t = np.arange(n) / SR
    wob = hz * (1 + 0.08 * np.sin(2 * math.pi * 6 * t))
    phase = 2 * math.pi * np.cumsum(wob) / SR
    return 0.55 * np.sin(phase) * np.exp(-t * decay)


def wet(n, bright=0.2):
    x = noise(n)
    for win in (7, 13, 21):
        x = np.convolve(x, np.ones(win) / win, mode="same")
    return x * (0.35 + bright)


def clicky(n, gap=0.03, amp=0.7):
    out = np.zeros(n)
    i = 0
    step = max(8, int(gap * SR))
    while i < n:
        span = min(90, n - i)
        out[i : i + span] += noise(span) * amp * np.linspace(1, 0, span)
        i += step
    return out


def make(attack, die):
    return {"attack": attack, "die": die}


def shambler():
    n = int(SR * 0.28)
    return make(
        (growl(n, 110, 7) + wet(n, 0.12) * 0.4) * env(n, 0.01, 0.08),
        (growl(int(SR * 0.42), 70, 5) + wet(int(SR * 0.42), 0.08) * 0.5) * env(int(SR * 0.42), 0.02, 0.14),
    )


def slime():
    n = int(SR * 0.24)
    t = np.arange(n) / SR
    squelch = 0.4 * np.sin(2 * math.pi * (90 + 70 * t) * t) + wet(n, 0.35) * 0.55
    popn = int(SR * 0.36)
    pop = wet(popn, 0.5) * 0.7 + 0.25 * tone(popn, 140)
    return make(squelch * env(n, 0.008, 0.09), pop * env(popn, 0.004, 0.12))


def runner():
    n = int(SR * 0.16)
    t = np.arange(n) / SR
    screech = 0.35 * np.sin(2 * math.pi * (1400 + 600 * t) * t)
    return make(
        (screech + noise(n) * 0.12) * env(n, 0.002, 0.05),
        (growl(int(SR * 0.22), 260, 14) + noise(int(SR * 0.22)) * 0.2) * env(int(SR * 0.22), 0.002, 0.08),
    )


def node():
    n = int(SR * 0.2)
    t = np.arange(n) / SR
    drip = 0.3 * np.sin(2 * math.pi * (180 + 40 * np.sin(2 * math.pi * 9 * t)) * t)
    return make(
        (drip + wet(n, 0.2) * 0.35) * env(n, 0.01, 0.07),
        (wet(int(SR * 0.3), 0.4) * 0.6 + 0.2 * tone(int(SR * 0.3), 90)) * env(int(SR * 0.3), 0.01, 0.12),
    )


def crawler():
    n = int(SR * 0.18)
    return make(
        clicky(n, 0.022, 0.8) * env(n, 0.001, 0.05),
        (clicky(int(SR * 0.26), 0.018, 0.9) + growl(int(SR * 0.26), 180, 12) * 0.3) * env(int(SR * 0.26), 0.002, 0.08),
    )


def psychoid():
    n = int(SR * 0.26)
    t = np.arange(n) / SR
    warp = 0.32 * np.sin(2 * math.pi * (420 + 380 * np.sin(2 * math.pi * 7 * t)) * t)
    return make(
        (warp + noise(n) * 0.08) * env(n, 0.01, 0.08),
        (0.4 * np.sin(2 * math.pi * (280 - 160 * np.arange(int(SR * 0.4)) / SR) * np.arange(int(SR * 0.4)) / SR))
        * env(int(SR * 0.4), 0.02, 0.14),
    )


def necro():
    n = int(SR * 0.34)
    t = np.arange(n) / SR
    drone = 0.35 * np.sin(2 * math.pi * 48 * t) + 0.2 * np.sin(2 * math.pi * 96 * t)
    return make(
        (drone + wet(n, 0.1) * 0.25) * env(n, 0.03, 0.1),
        (growl(int(SR * 0.5), 42, 3) + wet(int(SR * 0.5), 0.15) * 0.3)
        * env(int(SR * 0.5), 0.04, 0.16),
    )


def biomorph():
    n = int(SR * 0.15)
    t = np.arange(n) / SR
    chirp = 0.4 * np.sin(2 * math.pi * (700 + 900 * t) * t)
    return make(
        (chirp + noise(n) * 0.08) * env(n, 0.002, 0.05),
        (0.35 * np.sin(2 * math.pi * (500 - 300 * np.arange(int(SR * 0.22)) / SR) * np.arange(int(SR * 0.22)) / SR))
        * env(int(SR * 0.22), 0.002, 0.08),
    )


def brute():
    n = int(SR * 0.3)
    return make(
        (growl(n, 72, 6) + wet(n, 0.05) * 0.3) * env(n, 0.01, 0.1),
        (0.6 * tone(int(SR * 0.45), 48) * np.exp(-np.arange(int(SR * 0.45)) / SR * 5) + wet(int(SR * 0.45), 0.08) * 0.35)
        * env(int(SR * 0.45), 0.015, 0.16),
    )


def cyber():
    n = int(SR * 0.18)
    t = np.arange(n) / SR
    zap = 0.35 * np.sin(2 * math.pi * 1800 * t) + 0.2 * np.sin(2 * math.pi * 3600 * t)
    return make(
        (zap + noise(n) * 0.14 * np.exp(-t * 20)) * env(n, 0.001, 0.05),
        (0.3 * np.sin(2 * math.pi * (900 - 700 * np.arange(int(SR * 0.32)) / SR) * np.arange(int(SR * 0.32)) / SR)
         + noise(int(SR * 0.32)) * 0.2)
        * env(int(SR * 0.32), 0.002, 0.1),
    )


def armored():
    n = int(SR * 0.22)
    scrape = clicky(n, 0.04, 0.45) + growl(n, 95, 8) * 0.45
    return make(
        scrape * env(n, 0.006, 0.07),
        (growl(int(SR * 0.38), 60, 5) + clicky(int(SR * 0.38), 0.05, 0.35)) * env(int(SR * 0.38), 0.01, 0.13),
    )


def mutant():
    n = int(SR * 0.26)
    return make(
        (growl(n, 140, 8) + 0.2 * tone(n, 420)) * env(n, 0.008, 0.08),
        (growl(int(SR * 0.4), 90, 5) + wet(int(SR * 0.4), 0.1) * 0.3) * env(int(SR * 0.4), 0.01, 0.14),
    )


def colossus():
    n = int(SR * 0.4)
    boom = wet(n, 0.05)
    for win in (31, 61):
        boom = np.convolve(boom, np.ones(win) / win, mode="same")
    return make(
        (0.55 * tone(n, 40) * np.exp(-np.arange(n) / SR * 4) + boom * 0.5) * env(n, 0.02, 0.14),
        (0.65 * tone(int(SR * 0.62), 32) * np.exp(-np.arange(int(SR * 0.62)) / SR * 3) + wet(int(SR * 0.62), 0.04) * 0.4)
        * env(int(SR * 0.62), 0.03, 0.2),
    )


def praetorian():
    n = int(SR * 0.3)
    t = np.arange(n) / SR
    roar = growl(n, 160, 6) + 0.18 * np.sin(2 * math.pi * 700 * t)
    return make(
        roar * env(n, 0.01, 0.09),
        (growl(int(SR * 0.48), 100, 4) + 0.2 * tone(int(SR * 0.48), 220)) * env(int(SR * 0.48), 0.02, 0.16),
    )


JOBS = {
    "shambler": shambler,
    "slime": slime,
    "runner": runner,
    "node": node,
    "crawler": crawler,
    "psychoid": psychoid,
    "necro": necro,
    "biomorph": biomorph,
    "brute": brute,
    "cyber": cyber,
    "armored": armored,
    "mutant": mutant,
    "colossus": colossus,
    "praetorian": praetorian,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, fn in JOBS.items():
        pair = fn()
        for kind, samples in pair.items():
            name = f"{stem}_{kind}"
            wav = OUT / f"{name}.wav"
            mp3 = OUT / f"{name}.mp3"
            write_wav(wav, np.clip(samples, -1, 1))
            to_mp3(wav, mp3)
            print("ok", mp3.name, mp3.stat().st_size)


if __name__ == "__main__":
    main()
