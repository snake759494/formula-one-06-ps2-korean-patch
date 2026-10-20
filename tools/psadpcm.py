# PS-ADPCM(VAG) 디코드/인코드 (모노, 16바이트 프레임 = 28샘플), numba 가속
import numpy as np
from numba import njit

F0 = np.array([0, 60, 115, 98, 122], np.int64)
F1 = np.array([0, 0, -52, -55, -60], np.int64)

@njit(cache=True)
def _decode(d, out):
    h1 = 0; h2 = 0; n = 0
    for p in range(0, len(d) - 15, 16):
        sh = d[p] & 15; fl = d[p] >> 4
        if fl > 4: fl = 4
        f0 = F0[fl]; f1 = F1[fl]
        for i in range(14):
            b = d[p + 2 + i]
            for k in range(2):
                nib = (b >> (4 * k)) & 15
                s = nib - 16 if nib >= 8 else nib
                v = ((s << 12) >> sh) + ((h1 * f0 + h2 * f1 + 32) >> 6)
                if v > 32767: v = 32767
                if v < -32768: v = -32768
                out[n] = v; n += 1; h2 = h1; h1 = v
    return n

def decode(data):
    d = np.frombuffer(data, np.uint8).astype(np.int64)
    out = np.zeros(len(d) // 16 * 28, np.int64)
    n = _decode(d, out)
    return out[:n].astype(np.int16)

@njit(cache=True)
def _encode(x, out):
    h1 = 0; h2 = 0
    nf = len(x) // 28
    nibs = np.zeros(28, np.int64); best = np.zeros(28, np.int64)
    for f in range(nf):
        berr = -1; bfl = 0; bsh = 0; bh1 = 0; bh2 = 0
        for fl in range(5):
            f0 = F0[fl]; f1 = F1[fl]
            for sh in range(13):
                a1 = h1; a2 = h2; err = 0
                ok = True
                for i in range(28):
                    v = x[f * 28 + i]
                    pred = (a1 * f0 + a2 * f1 + 32) >> 6
                    q = ((v - pred) << sh)
                    q = (q + (2048 if q >= 0 else -2048)) // 4096
                    if q > 7: q = 7
                    if q < -8: q = -8
                    r = ((q << 12) >> sh) + pred
                    if r > 32767: r = 32767
                    if r < -32768: r = -32768
                    e = r - v; err += e * e
                    nibs[i] = q & 15; a2 = a1; a1 = r
                    if berr >= 0 and err >= berr:
                        ok = False; break
                if ok and (berr < 0 or err < berr):
                    berr = err; bfl = fl; bsh = sh; bh1 = a1; bh2 = a2
                    for i in range(28): best[i] = nibs[i]
        h1 = bh1; h2 = bh2
        o = f * 16
        out[o] = (bfl << 4) | bsh
        out[o + 1] = 1 if f == nf - 1 else 0         # 마지막 프레임 = 종료 플래그
        for i in range(14):
            out[o + 2 + i] = best[2 * i] | (best[2 * i + 1] << 4)

def encode(pcm):
    """int16 PCM -> PS-ADPCM bytes (마지막 프레임에 종료 플래그 1)"""
    x = np.asarray(pcm, np.int64)
    x = np.concatenate([x, np.zeros((-len(x)) % 28, np.int64)])
    if len(x) == 0: x = np.zeros(28, np.int64)
    out = np.zeros(len(x) // 28 * 16, np.int64)
    _encode(x, out)
    return out.astype(np.uint8).tobytes()
