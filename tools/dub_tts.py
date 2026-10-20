"""한국어 대본 -> Supertonic 3 합성 -> 원래 클립 길이·자리·음량에 맞춘 PCM(게임 샘플레이트)
  python tools/dub_tts.py ts|com      -> dub/wav/<set>/<번호>.npy (이어하기 지원), dub/tts_<set>.jsonl 기록
대본: dub/ko/<set>_*.tsv (번호<TAB>한국어|KEEP), 원본 정보: dub/asr_<set>.jsonl
"""
import os, sys, re, json, glob, hashlib
import numpy as np
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(__file__))
import voice
from loudness import lufs, master

ROOT = voice.ROOT
DUB = voice.DUB
RATE = voice.RATE                     # 게임 재생 샘플레이트 (VOICE_RATE 환경변수)
VOICE = {'ts': 'M2', 'com': 'M4'}      # 팀 무전 엔지니어, 해설 캐스터
NATURAL = {'M1': 5.4, 'M2': 5.6, 'M3': 6.6, 'M4': 5.7, 'M5': 5.3}
SPEED_MIN, SPEED_MAX, STRETCH_MAX = 0.85, 1.6, 1.3

def syllables(s):
    return len(re.findall('[가-힣]', s))

def tts_text(s):
    s = re.sub(r'[^가-힣 .,!?]', ' ', s.replace('…', ', '))
    s = re.sub(r'\s+', ' ', s).strip()
    return s or '.'

def trim(x, margin):
    env = np.abs(x) > max(300.0, np.abs(x).max() * 0.02)
    idx = np.nonzero(env)[0]
    if len(idx) == 0: return x
    return x[max(0, idx[0] - margin):idx[-1] + margin]

def wsola(x, speed, win=720, tol=180):
    hop = win // 2; w = np.hanning(win); n_out = int(len(x) / speed)
    xp = np.concatenate([np.zeros(tol + win), x, np.zeros(tol + 2 * win)])
    base = tol + win; y = np.zeros(n_out + win); ws = np.zeros(n_out + win); prev = base
    for m in range(0, n_out, hop):
        ideal = base + int(m * speed)
        if m == 0: pos = ideal
        else:
            target = xp[prev + hop:prev + hop + win]; seg = xp[ideal - tol:ideal + tol + win]
            pos = ideal - tol + int(np.argmax(np.correlate(seg, target, 'valid')))
        y[m:m + win] += xp[pos:pos + win] * w; ws[m:m + win] += w; prev = pos
    return (y / np.maximum(ws, 1e-3))[:n_out]

class Voices:
    def __init__(self):
        from huggingface_hub import hf_hub_download
        from supertonic import TTS
        path = os.path.dirname(hf_hub_download('Supertone/supertonic-3', 'config.json', local_files_only=True))
        self.tts = TTS(model='supertonic-3', model_dir=path, auto_download=False)
        self.cache = {}
    def say(self, text, name, speed, seed):
        if name not in self.cache: self.cache[name] = self.tts.get_voice_style(name)
        np.random.seed(seed)
        wav, _ = self.tts.synthesize(text, voice_style=self.cache[name], lang='ko', speed=speed)
        x = resample_poly(wav.squeeze().astype(np.float64) * 32767, RATE, 44100)
        return trim(x, int(0.01 * RATE))

def load_script(key):
    out = {}
    for fn in sorted(glob.glob(os.path.join(DUB, 'ko', key + '_*.tsv'))):
        for l in open(fn, encoding='utf-8').read().splitlines():
            if '\t' in l:
                i, s = l.split('\t', 1); out[int(i)] = s.strip()
    return out

def synth(v, vname, ko, orig_pcm, seed):
    o = orig_pcm.astype(np.float64)
    target = lufs(o, RATE)
    limit = len(o)                                  # 원래 길이 이하 (자리 크기 = 원본 바이트)
    speech = trim(o, 0)
    goal = max(0.3, len(speech) / RATE)
    text = tts_text(ko)
    speed = float(np.clip(syllables(text) / NATURAL[vname] / goal, SPEED_MIN, SPEED_MAX))
    x = v.say(text, vname, speed, seed)
    for _ in range(3):
        if len(x) <= limit: break
        k = len(x) / limit
        if k <= STRETCH_MAX: x = wsola(x, k * 1.005)[:limit]; break
        speed = min(1.9, speed * k / 1.1); x = v.say(text, vname, speed, seed)
    if len(x) > limit: x = wsola(x, len(x) / limit * 1.005)[:limit]
    y = master(x, RATE, target) if np.isfinite(target) else x
    return np.clip(y, -32768, 32767).astype(np.int16), speed

def main(key):
    asr = {r['i']: r for r in map(json.loads, open(os.path.join(DUB, 'asr_%s.jsonl' % key), encoding='utf-8'))}
    script = load_script(key)
    outdir = os.path.join(DUB, 'wav', key); os.makedirs(outdir, exist_ok=True)
    log = os.path.join(DUB, 'tts_%s.jsonl' % key)
    done = {}
    if os.path.exists(log):
        for l in open(log, encoding='utf-8'): r = json.loads(l); done[r['i']] = r['ko']
    v = Voices(); vname = VOICE[key]
    wadf = open(os.path.join(voice.AUD, voice.SETS[key][1] + '.WAD'), 'rb')
    with open(log, 'a', encoding='utf-8') as fo:
        for i, ko in sorted(script.items()):
            if ko == 'KEEP' or done.get(i) == ko or i not in asr: continue
            r = asr[i]
            o = voice.clip(key, r['off'], r['size'], wadf)
            seed = int(hashlib.md5(('%s%d' % (key, i)).encode()).hexdigest()[:8], 16) % 100000
            y, speed = synth(v, vname, ko, o, seed)
            np.save(os.path.join(outdir, '%d.npy' % i), y)
            fo.write(json.dumps({'i': i, 'ko': ko, 'speed': round(speed, 2), 'len': len(y), 'orig': len(o)}, ensure_ascii=False) + '\n'); fo.flush()

if __name__ == '__main__':
    main(sys.argv[1])
