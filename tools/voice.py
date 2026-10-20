"""해설·무전 음성 더빙 도구
  python tools/voice.py extract          # ISO에서 GBR06/TS_GBR06 WAD·IDX·BIN 추출
  python tools/voice.py asr ts|com        # 클립별 영어 받아쓰기 -> dub/asr_<set>.jsonl (이어하기 지원)
묶음: com = AUDIO/COM/GBR06 (해설, 8409칸), ts = AUDIO/COM_TS/TS_GBR06 (무전, 669칸)
IDX = u32 개수 + [u32 오프셋, u32 크기] (없는 칸은 오프셋 0xFFFFFFFF). 데이터는 PS-ADPCM 모노, 0x800 정렬.
"""
import os, sys, json, struct, wave
sys.path.insert(0, os.path.dirname(__file__))
import iso, psadpcm
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG_ISO = os.path.join(ROOT, 'Formula One 06 (Europe, Australia) (En,Fr,De,Es,It,Pt,Fi).iso')
AUD = os.path.join(ROOT, 'work', 'audio')
DUB = os.path.join(ROOT, 'dub')
SETS = {'com': ('/DATA2006/AUDIO/COM/GBR06', 'GBR06'), 'ts': ('/DATA2006/AUDIO/COM_TS/TS_GBR06', 'TS_GBR06')}
RATE = int(os.environ.get('VOICE_RATE', '24000'))   # 실측: 녹화 오디오와 상관 0.835 (22050Hz는 0.158)

def extract():
    os.makedirs(AUD, exist_ok=True)
    with open(ORIG_ISO, 'rb') as f:
        for p, l, s, _ in iso.records(f):
            for base, name in SETS.values():
                for ext in ('.IDX', '.BIN', '.WAD'):
                    if p == base + ext:
                        out = os.path.join(AUD, name + ext)
                        if os.path.exists(out) and os.path.getsize(out) == s: continue
                        f.seek(l * 2048); open(out, 'wb').write(f.read(s)); print(out, s)

def entries(key):
    name = SETS[key][1]
    t = open(os.path.join(AUD, name + '.IDX'), 'rb').read()
    n = struct.unpack_from('<I', t)[0]
    return [(i,) + struct.unpack_from('<II', t, 4 + 8 * i) for i in range(n)
            if struct.unpack_from('<I', t, 4 + 8 * i)[0] != 0xFFFFFFFF]

def clip(key, off, size, wadf=None):
    name = SETS[key][1]
    f = wadf or open(os.path.join(AUD, name + '.WAD'), 'rb')
    f.seek(off); return psadpcm.decode(f.read(size))

def write_wav(path, pcm, rate=RATE):
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(np.asarray(pcm, np.int16).tobytes()); w.close()

def asr(key):
    from faster_whisper import WhisperModel
    os.makedirs(DUB, exist_ok=True)
    out = os.path.join(DUB, 'asr_%s.jsonl' % key)
    done = set()
    if os.path.exists(out):
        for l in open(out, encoding='utf-8'):
            done.add(json.loads(l)['i'])
    m = WhisperModel(os.environ.get('ASR_MODEL', 'small.en'), device='cpu', compute_type='int8',
                     cpu_threads=int(os.environ.get('ASR_THREADS', '4')))
    name = SETS[key][1]
    wadf = open(os.path.join(AUD, name + '.WAD'), 'rb')
    tmp = os.path.join(AUD, '_asr_%s.wav' % key)
    gap = np.zeros(int(0.9 * RATE), np.int16)
    todo = [e for e in entries(key) if e[0] not in done]
    with open(out, 'a', encoding='utf-8') as fo:
        k = 0
        while k < len(todo):
            # 짧은 클립을 0.9초 무음을 끼워 약 25초 창으로 이어 붙여 한 번에 받아쓰고, 단어 시각으로 나눈다
            group = []; pcms = []; t = 0.0
            while k < len(todo):
                i, off, size = todo[k]
                pcm = clip(key, off, size, wadf); d = len(pcm) / RATE
                if group and t + d > 25: break
                group.append((i, off, size, t, t + d, d)); pcms += [pcm, gap]; t += d + 0.9; k += 1
                if d > 25: break
            write_wav(tmp, np.concatenate(pcms))
            segs, info = m.transcribe(tmp, language='en', beam_size=1, vad_filter=False,
                                      condition_on_previous_text=False, word_timestamps=True)
            words = [w for s in segs for w in (s.words or [])]
            for i, off, size, s0, s1, d in group:
                text = ''.join(w.word for w in words if s0 - 0.3 <= (w.start + w.end) / 2 < s1 + 0.45).strip()
                fo.write(json.dumps({'i': i, 'off': off, 'size': size, 'dur': round(d, 3), 'en': text}, ensure_ascii=False) + '\n')
            fo.flush()

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'extract': extract()
    elif c == 'asr': asr(sys.argv[2])
