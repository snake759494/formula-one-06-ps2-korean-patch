"""멈춤 테스트: PCSX2(백그라운드)로 시나리오를 돌리고 단계마다 화면을 찍는다.
  python tools/smoke.py <iso> <시나리오...>      결과: work/smoke/<시나리오>_<단계>.png, 멈춤 판정 출력
시나리오 시작점은 메인 메뉴('레이스' 선택). 처음 한 번 새 프로필을 만든 상태저장(work/smoke/main.p2s)을 쓴다.
멈춤 판정: 마지막 단계 뒤 8초 간격 두 화면이 (로딩 아이콘 영역 제외) 같고, 다음 키 입력에도 바뀌지 않으면 FREEZE.
"""
import os, sys, time, glob, shutil, io
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import emu

R = emu.R; OUT = os.path.join(R, 'work', 'smoke'); os.makedirs(OUT, exist_ok=True)
SS = os.path.join(emu.EMU, 'sstates')

# 메인 메뉴: 레이스 / 화면 분할 / 옵션 / 프로필 / 부가 요소
# 레이스 메뉴: 퀵 레이스 / 타임 트라이얼 / 그랑프리 위크엔드 / 월드 챔피언십 / 커리어
SCEN = {   # 시작점: 레이스 메뉴(퀵 레이스 선택). 메인 메뉴 항목은 I(뒤로)로 나간 뒤
    'quick_driver': 'K w8 s D w1 ' + 'RT w3 ' * 22 + 's U w1 K w150 s',
    'quick_team':   'K w8 D w0.5 D w1 ' + 'RT w3 ' * 11 + 's U w0.5 U w1 K w150 s',
    'quick_circuit':'K w8 D w0.5 D w0.5 D w1 ' + 'RT w3 ' * 18 + 's U w0.5 U w0.5 U w1 K w150 s',
    'timetrial':    'D w0.5 K w8 s D w1 RT w3 RT w3 RT w3 s U w1 K w150 s',
    'grandprix':    'D w0.5 D w0.5 K w8 s D w0.5 D w1 RT w3 RT w3 RT w3 s U w0.5 K w160 s K w20 s',
    'championship': 'D w0.5 D w0.5 D w0.5 K w8 s D w1 RT w3 RT w3 RT w3 s U w1 K w10 s K w10 s K w160 s',
    'career':       'D w0.5 D w0.5 D w0.5 D w0.5 K w10 s K w10 s K w10 s K w20 s',
    'splitscreen':  'I w4 D w0.5 K w8 s K w8 s K w8 s K w150 s',
    'options':      'I w4 D w0.5 D w0.5 K w6 s K w5 s I w3 D w0.5 K w5 s I w3 D w0.5 K w5 s I w3 I w3 s',
    'profile':      'I w4 D w0.5 D w0.5 D w0.5 K w6 s K w5 s I w3 I w3 s',
    'extras':       'I w4 D w0.5 D w0.5 D w0.5 D w0.5 K w6 s K w6 s I w3 D w0.5 K w6 s I w3 I w3 s',
}

def shot():
    old = set(glob.glob(os.path.join(SS, '*.p2s')))
    t0 = time.time()
    emu.pine(bytes([9, 9]))
    for _ in range(200):
        ps = glob.glob(os.path.join(SS, '*.p2s'))
        p = max(ps, key=os.path.getmtime) if ps else None
        if p and os.path.getmtime(p) > t0 - 1: time.sleep(1.2); break
        time.sleep(0.1)
    return Image.open(io.BytesIO(emu.member(p, 'Screenshot.png'))).convert('RGB'), p

def same(a, b):
    x = np.asarray(a.resize((160, 120)), float); y = np.asarray(b.resize((160, 120)), float)
    x[:16, :24] = 0; y[:16, :24] = 0                      # 로딩 아이콘
    return np.abs(x - y).mean() < 1.0

def wait_boot(iso, first):
    emu.stop(); time.sleep(2)
    emu.launch(iso)
    for _ in range(60):
        time.sleep(5)
        try:
            img, _ = shot()
        except Exception:
            continue
        a = np.asarray(img.resize((320, 240)), int)
        red = ((a[..., 0] > 180) & (a[..., 1] < 90) & (a[..., 2] < 90)).sum()
        if red > 20: return True                           # 언어 선택 화살표
    return False

def is_main(img):
    a = np.asarray(img.resize((640, 480)), int)
    title = a[66:92, 10:220]                                 # 제목 줄: 메인 메뉴는 제목 글자가 없다
    bright = (title.min(-1) > 200).sum()
    arrow = a[140:170, 15:50]
    red = ((arrow[..., 0] > 180) & (arrow[..., 1] < 90)).sum()
    return bright < 15 and red > 15

REF = os.path.join(R, 'work', 'smoke_ref_race.png')      # '레이스' 메뉴(퀵 레이스 선택) 기준 화면

def is_race_menu(img):
    ref = Image.open(REF).convert('RGB')
    x = np.asarray(img.resize((160, 120)), float)[10:60, :70]; y = np.asarray(ref.resize((160, 120)), float)[10:60, :70]
    return np.abs(x - y).mean() < 12

def make_main(iso):
    """새 프로필을 만들고 '레이스' 메뉴에 도착한 상태를 저장(빌드마다 새로 만든다: 다른 빌드의 상태저장은 쓸 수 없음)"""
    for attempt in range(3):
        shutil.rmtree(os.path.join(emu.EMU, 'memcards'), ignore_errors=True)
        assert wait_boot(iso, True), 'boot'
        for k in 'U w0.5 U w0.5 U w0.6 K w45 RET w6 RET w9 D w0.4 D w0.4 D w0.4 D w0.6 K w5 K w14'.split():
            time.sleep(float(k[1:])) if k[0] == 'w' else emu.key(k)
        for _ in range(5):
            img, p = shot()
            if is_race_menu(img):
                img.save(os.path.join(OUT, '_main.png')); shutil.copy(p, os.path.join(OUT, 'main.p2s')); return
            emu.key('K'); time.sleep(10)
    raise RuntimeError('레이스 메뉴에 도착하지 못함')

def run(iso, name):
    st = os.path.join(SS, 'SCES-53950 (AD31CF2A).01.p2s')
    shutil.copy(os.path.join(OUT, 'main.p2s'), st)
    emu.pine(bytes([0xa, 1])); time.sleep(4)
    n = 0
    for k in SCEN[name].split():
        if k == 's':
            img, _ = shot(); img.save(os.path.join(OUT, '%s_%d.png' % (name, n))); n += 1
        elif k[0] == 'w' and k[1:].replace('.', '').isdigit():
            time.sleep(float(k[1:]))
        else:
            emu.key(k)
    a, _ = shot(); time.sleep(8); b, _ = shot()
    frozen = same(a, b)
    if frozen:
        emu.key('K'); time.sleep(6); c, _ = shot(); frozen = same(b, c)
    b.save(os.path.join(OUT, '%s_end.png' % name))
    print('%-14s %s' % (name, 'FREEZE?' if frozen else 'ok'), flush=True)
    return not frozen

if __name__ == '__main__':
    iso = sys.argv[1]; names = sys.argv[2:] or list(SCEN)
    for f in glob.glob(os.path.join(OUT, '*_*.png')): os.remove(f)
    make_main(iso)
    res = {}
    for nm in names:
        res[nm] = run(iso, nm)
    emu.stop()
    print('RESULT', res)
