"""Synthesize short weapon SFX as WAV then encode MP3 via ffmpeg."""
from __future__ import annotations

import math
import struct
import subprocess
import wave
from pathlib import Path

import numpy as np

OUT = Path(r"D:\Dev\HiveSwarm\assets\SFX")
SR = 44100


def write_wav(path: Path, samples: np.ndarray) -> None:
    samples = np.clip(samples, -1, 1)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def to_mp3(wav: Path, mp3: Path) -> None:
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-qscale:a", "4", str(mp3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    wav.unlink(missing_ok=True)


def env(n, a=0.01, r=0.08):
    e = np.ones(n, dtype=np.float64)
    na, nr = int(SR * a), int(SR * r)
    if na > 0:
        e[:na] = np.linspace(0, 1, na)
    if nr > 0:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pulse_fire(n=int(SR * 0.14)):
    t = np.arange(n) / SR
    tone = 0.45 * np.sin(2 * math.pi * 880 * t) + 0.25 * np.sin(2 * math.pi * 1760 * t)
    click = np.random.randn(n) * 0.18
    click *= np.exp(-t * 40)
    return (tone + click) * env(n, 0.002, 0.06)


def seeker_fire(n=int(SR * 0.28)):
    t = np.arange(n) / SR
    freq = 420 + 900 * t
    phase = 2 * math.pi * np.cumsum(freq) / SR
    whoosh = 0.35 * np.sin(phase) + 0.2 * np.random.randn(n) * np.exp(-t * 6)
    return whoosh * env(n, 0.02, 0.1)


def flame_loop(n=int(SR * 1.2)):
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    # crude lowpass
    for _ in range(3):
        noise = np.convolve(noise, np.ones(9) / 9, mode="same")
    rumble = 0.22 * np.sin(2 * math.pi * 70 * t) + 0.12 * np.sin(2 * math.pi * 110 * t)
    hiss = noise * (0.35 + 0.1 * np.sin(2 * math.pi * 8 * t))
    return np.tanh(rumble + hiss) * 0.85


def beam_fire(n=int(SR * 0.16)):
    t = np.arange(n) / SR
    zap = 0.4 * np.sin(2 * math.pi * 2100 * t) + 0.2 * np.sin(2 * math.pi * 4200 * t)
    noise = np.random.randn(n) * 0.15 * np.exp(-t * 18)
    return (zap + noise) * env(n, 0.001, 0.07)


def chain_fire(n=int(SR * 0.22)):
    t = np.arange(n) / SR
    crack = np.zeros(n)
    for k in (0.0, 0.035, 0.07):
        i = int(k * SR)
        if i < n:
            crack[i : i + 80] += np.random.randn(min(80, n - i)) * (1.2 - k * 8)
    buzz = 0.2 * np.sin(2 * math.pi * 1600 * t) * np.exp(-t * 12)
    return np.clip(crack * 0.35 + buzz, -1, 1) * env(n, 0.001, 0.08)


def nova_fire(n=int(SR * 0.32)):
    t = np.arange(n) / SR
    boom = np.random.randn(n)
    for win in (21, 41):
        boom = np.convolve(boom, np.ones(win) / win, mode="same")
    thump = 0.55 * np.sin(2 * math.pi * 55 * t) * np.exp(-t * 8)
    return np.tanh(thump + boom * 0.55) * env(n, 0.004, 0.12)


def poison_fire(n=int(SR * 0.2)):
    t = np.arange(n) / SR
    squirt = 0.3 * np.sin(2 * math.pi * (240 + 80 * np.sin(2 * math.pi * 14 * t)) * t)
    fizz = np.random.randn(n) * 0.12 * np.exp(-t * 7)
    return (squirt + fizz) * env(n, 0.01, 0.08)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = {
        "pulse_fire": pulse_fire,
        "seeker_fire": seeker_fire,
        "flame_loop": flame_loop,
        "beam_fire": beam_fire,
        "chain_fire": chain_fire,
        "nova_fire": nova_fire,
        "poison_fire": poison_fire,
    }
    for name, fn in jobs.items():
        wav = OUT / f"{name}.wav"
        mp3 = OUT / f"{name}.mp3"
        write_wav(wav, fn())
        to_mp3(wav, mp3)
        print("ok", mp3.name, mp3.stat().st_size)


if __name__ == "__main__":
    main()
