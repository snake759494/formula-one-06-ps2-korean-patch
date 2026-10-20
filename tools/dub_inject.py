"""합성한 한국어 음성(dub/wav/<set>/<번호>.npy)을 PS-ADPCM으로 인코딩해 원래 자리에 넣는다.
WAD·IDX 파일 크기는 그대로(제자리 교체) -> 한글 ISO 안의 원래 위치에 직접 쓴다.
  python tools/dub_inject.py            (빌드 후 실행; build.py 가 자동 호출)
"""
import os, sys, glob, struct
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import voice, psadpcm, iso

def patched(key):
    name = voice.SETS[key][1]
    wad = bytearray(open(os.path.join(voice.AUD, name + '.WAD'), 'rb').read())
    idx = bytearray(open(os.path.join(voice.AUD, name + '.IDX'), 'rb').read())
    n = 0
    for i, off, size in voice.entries(key):
        p = os.path.join(voice.DUB, 'wav', key, '%d.npy' % i)
        if not os.path.exists(p): continue
        b = psadpcm.encode(np.load(p))
        if len(b) > size: b = b[:size - size % 16]; b = b[:-16] + bytes([b[-16], 1]) + b[-14:]
        wad[off:off + size] = b + bytes(size - len(b))
        struct.pack_into('<I', idx, 4 + 8 * i + 4, len(b))
        n += 1
    return wad, idx, n

def inject(iso_path):
    voice.extract()                      # 원본 음성 WAD·IDX가 없으면 원본 ISO에서 추출
    with open(iso_path, 'r+b') as f:
        recs = {p: (l, s) for p, l, s, _ in iso.records(f)}
        for key, (base, name) in voice.SETS.items():
            wad, idx, n = patched(key)
            for ext, data in (('.WAD', wad), ('.IDX', idx)):
                l, s = recs[base + ext]
                assert len(data) == s, (base, ext)
                f.seek(l * 2048); f.write(data)
            print('dub', key, n, 'clips')

if __name__ == '__main__':
    inject(sys.argv[1] if len(sys.argv) > 1 else os.path.join(voice.ROOT, 'Formula One 06 (Europe, Australia) (Korean).iso'))
