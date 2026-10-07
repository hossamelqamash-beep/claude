"""Synthesised soundtrack for the IMPACT motion piece (numpy only).
Ambient pad + soft pulse + whooshes/hits synced to the visual cues.
Usage: python3 soundtrack.py out.wav
"""
import sys, wave
import numpy as np

SR = 44100
DUR = 90.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
mix = np.zeros((N, 2))


def note(f):  # midi -> Hz
    return 440.0 * 2 ** ((f - 69) / 12)


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(sig), 0] += sig * gain * l
    mix[i:i + len(sig), 1] += sig * gain * r


def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


# ---------- Pad: warm detuned chords ----------
# D major world: Dmaj9 - Bm9 - Gmaj9 - A6sus, 6 s per chord
chords = [
    [50, 57, 61, 64, 66], [47, 54, 57, 61, 62], [43, 50, 54, 57, 62], [45, 52, 57, 59, 64],
]
pad = np.zeros(N)
CH = 6.0
k = 0
st = 0.0
while st < DUR:
    ch = chords[k % 4]
    n = int((CH + 2.5) * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for m in ch:
        f = note(m)
        for det in (-0.08, 0.0, 0.08):
            ff = f * 2 ** (det / 12)
            ph = rng.random() * 6.28
            # soft "filtered saw": a few decaying harmonics
            for h in range(1, 6):
                s += np.sin(2 * np.pi * ff * h * tt + ph * h) / (h ** 1.6)
    s *= env_adsr(n, 2.0, 2.5) / 12
    i = int(st * SR)
    seg = s[: N - i]
    pad[i:i + len(seg)] += seg
    st += CH
    k += 1
pad = lowpass(pad, 1400)
# slow swell automation: quiet open, lift, dip at the "pace slows" intro, warm closing
auto = np.interp(t, [0, 4, 8, 20, 22, 32, 50, 64, 74, 75.8, 77, 85, 88, 90],
                 [0, .5, .7, .75, .55, .8, .9, .9, .55, 1, .8, .9, .8, 0])
pad *= auto
mix[:, 0] += pad * 0.55
mix[:, 1] += np.roll(pad, 300) * 0.55  # tiny haas widening

# ---------- Sub-bass following chord roots ----------
bass = np.zeros(N)
for j in range(int(DUR / CH) + 1):
    root = chords[j % 4][0] - 12
    n = int(CH * SR)
    tt = np.arange(n) / SR
    b = np.sin(2 * np.pi * note(root) * tt) * env_adsr(n, 0.4, 1.0)
    i = int(j * CH * SR)
    seg = b[: N - i]
    bass[i:i + len(seg)] += seg
bass *= np.interp(t, [0, 8, 9, 20, 23, 32, 33, 74, 75.8, 77, 86, 90], [0, 0, .5, .5, .2, .2, .6, .6, .9, .4, .4, 0])
mix += (bass * 0.35)[:, None]

# ---------- Pulse: soft kick + hat, 100 BPM ----------
BPM = 100
beat = 60 / BPM


def kick():
    n = int(0.45 * SR)
    tt = np.arange(n) / SR
    f = 45 + 90 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)


def hat():
    n = int(0.08 * SR)
    x = rng.standard_normal(n)
    x = x - lowpass(x, 7000)
    return x * np.exp(-np.arange(n) / SR * 60)


K, Hh = kick(), hat()
sections = [(8.0, 19.9, 0.5), (32.0, 47.4, 0.7), (50.0, 73.8, 0.7)]
for a, b, g in sections:
    bt = a
    i = 0
    while bt < b:
        ramp = min(1, (bt - a) / 3)
        add(K, bt, 0, 0.55 * g * ramp)
        add(Hh, bt + beat / 2, 0.3, 0.12 * g * ramp)
        if i % 4 == 3:
            add(Hh, bt + beat * 0.75, -0.3, 0.07 * g * ramp)
        bt += beat
        i += 1

# ---------- Plucks: gentle arpeggio in the "what we do" section ----------
def pluck(f, dur=0.9):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (4 + 3 * h)) / h for h in range(1, 5))
    return s * env_adsr(n, 0.004, 0.2)


arp = [74, 78, 81, 85, 83, 81, 78, 76]
j = 0
bt = 32.0
while bt < 73.5:
    if not (47.4 < bt < 50.0):
        ch = chords[int(bt / CH) % 4]
        m = ch[j % len(ch)] + 24
        add(pluck(note(m)), bt, 0.5 * np.sin(j), 0.05)
    bt += beat / 2
    j += 1

# ---------- FX: whooshes and hits on visual cues ----------
def whoosh(dur, up=True):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    tt = np.linspace(0, 1, n)
    # time-varying brightness via crossfade of two filtered versions
    lo, hi = lowpass(x, 600), lowpass(x, 5000)
    shape = tt ** 2 if up else (1 - tt) ** 2
    s = lo * (1 - shape) + hi * shape
    amp = (tt ** 2.2) if up else (1 - tt) ** 1.5
    return s * amp


def boom():
    n = int(2.8 * SR)
    tt = np.arange(n) / SR
    f = 38 + 70 * np.exp(-tt * 12)
    b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 1.6)
    noise = lowpass(rng.standard_normal(n), 2500) * np.exp(-tt * 9) * 0.4
    return b + noise


def shimmer(dur=3.0, base=86):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for i, m in enumerate([base, base + 4, base + 7, base + 11, base + 14]):
        s += np.sin(2 * np.pi * note(m) * tt + i) * np.exp(-tt * 1.4) * (tt > i * 0.06)
    return s * env_adsr(n, 0.01, 0.8)


hits = [5.45, 20.4, 47.6, 54.2, 75.8, 83.9]
for h in hits:
    add(whoosh(1.2, True), h - 1.2, 0, 0.18)
    add(boom(), h, 0, 0.55)
for w in [7.6, 16.15, 35.8, 50.0, 64.0, 85.45]:  # transitions
    add(whoosh(0.9, True), w - 0.6, -0.4, 0.12)
    add(whoosh(1.2, False), w + 0.3, 0.4, 0.08)
for s_ in [20.6, 75.9, 86.0]:
    add(shimmer(3.5), s_, 0, 0.06)
add(shimmer(4.0, 81), 87.0, 0, 0.05)

# ---------- Reverb (FFT convolution with a synthetic IR) ----------
irn = int(2.6 * SR)
irt = np.arange(irn) / SR
ir = np.stack([rng.standard_normal(irn), rng.standard_normal(irn)], 1) * np.exp(-irt * 2.4)[:, None]
ir = np.stack([lowpass(ir[:, 0], 6000), lowpass(ir[:, 1], 6000)], 1)
ir /= np.sqrt((ir ** 2).sum(0))
L = N + irn
size = 1 << int(np.ceil(np.log2(L)))
wet = np.zeros((N, 2))
for c in range(2):
    wet[:, c] = np.fft.irfft(np.fft.rfft(mix[:, c], size) * np.fft.rfft(ir[:, c], size), size)[:N]
out = mix * 0.8 + wet * 0.35

# master: fade, gentle soft-clip, normalise to -1 dBFS
fade = np.clip(np.minimum(t / 0.5, (DUR - t) / 2.5), 0, 1)
out *= fade[:, None]
out = np.tanh(out / np.abs(out).max() * 1.4)
out *= 0.89 / np.abs(out).max()

pcm = (out * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('ok')
