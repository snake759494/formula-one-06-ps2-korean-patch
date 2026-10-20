# 한글 글리프를 .bft 폰트에 추가한다 (텍스처 확장 + 셸프 패킹)
import os, struct, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import bft

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTF = {
    'neo_l': os.path.join(ROOT, 'NanumSquareNeo-aLt.ttf'),
    'neo_r': os.path.join(ROOT, 'NanumSquareNeo-bRg.ttf'),
    'neo_b': os.path.join(ROOT, 'NanumSquareNeo-cBd.ttf'),
    'neo_eb': os.path.join(ROOT, 'NanumSquareNeo-dEb.ttf'),
    'neo_h': os.path.join(ROOT, 'NanumSquareNeo-eHv.ttf'),
    'gm11': os.path.join(ROOT, 'tools', 'fonts', 'Galmuri11.ttf'),
    'gm11b': os.path.join(ROOT, 'tools', 'fonts', 'Galmuri11-Bold.ttf'),
    'gm9': os.path.join(ROOT, 'tools', 'fonts', 'Galmuri9.ttf'),
}

# 폰트별 설정: ttf, 한글 글자 크기(px, 정사각 상자), 셀 안 상단 여백(top), 기울임(shear), 자간 여유
CONF = {
    'eurostyleLargePx':  dict(ttf='neo_b',  size=19, top=2, shear=0, gap=1, boost=1.15),
    'eurostyleMediumPx': dict(ttf='neo_b',  size=15, top=2, shear=0, gap=1, boost=1.15),
    'eurostyleSmallPx':  dict(ttf='neo_b',  size=13, top=1, shear=0, gap=1),
    'fruitigerLarge':    dict(ttf='neo_r',  size=16, top=3, shear=0, gap=1, boost=1.1),
    'fruitigerMedium':   dict(ttf='neo_b',  size=12, top=2, shear=0, gap=1, boost=1.15),
    'fruitigerTiny':     dict(ttf='gm9',    size=10, top=0, shear=0, gap=1, pixel=True, maxw=256),
    'Small':             dict(ttf='gm11',   size=11, top=2, shear=0, gap=1, pixel=True, maxw=256),
    'tv2004_frb':        dict(ttf='neo_b',  size=14, top=3, shear=0, gap=1, boost=1.1),
}

def palette_alpha(f):
    c = f.clut
    i = c.find(bytes.fromhex('0800000002000000520000000000000000'))
    p = c.find(bytes.fromhex('0480000000000008'), i) + 8
    return [c[p + 4 * k + 3] for k in range(16)]

def alpha_to_index(alphas):
    """0..255 -> palette index with nearest alpha (alpha scale 0..0x80)."""
    a = np.array(alphas, float)
    lut = np.zeros(256, np.uint8)
    zero = [k for k in range(16) if alphas[k] == 0][0]
    for v in range(256):
        t = v / 255 * 0x80
        if v < 8: lut[v] = zero; continue
        lut[v] = int(np.argmin(np.abs(a - t) + (a == 0) * 1000))
    return lut

def render(ch, conf):
    """returns float alpha array (h, w) where h = top+size+1 (cell-top aligned)."""
    size = conf['size']; top = conf['top']
    pad = 4
    S = size + pad * 2
    # 원래 크기에서 FreeType 힌팅으로 렌더링(선명), 픽셀 폰트는 그대로
    font = ImageFont.truetype(TTF[conf['ttf']], conf.get('pt', size))
    im = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), '한', font=font)          # 기준 상자(모든 글자 공통 위치)
    gh = bb[3] - bb[1]; gw = bb[2] - bb[0]
    ox = round((S - gw) / 2 - bb[0]); oy = round((S - gh) / 2 - bb[1])
    d.text((ox, oy), ch, font=font, fill=255)
    a = np.asarray(im, float).copy()
    if conf['shear']:
        # 이탤릭: 행마다 정수 픽셀 이동(보간 없음)
        sh = conf['shear']; out = np.zeros_like(a)
        for y in range(S):
            k = int(round(sh * (S / 2 - y)))
            if k > 0: out[y, k:] = a[y, :-k]
            elif k < 0: out[y, :k] = a[y, -k:]
            else: out[y] = a[y]
        a = out
    if not conf.get('pixel') and conf['ttf'][:2] != 'gm':
        # 대비 곡선: 반투명 가장자리를 줄여 선명하게(굵기는 유지)
        lo, hi = conf.get('curve', (0.33, 0.55))
        a = np.clip((a / 255 - lo) / (hi - lo), 0, 1) * 255
    # 잉크가 들어갈 정사각 상자(size x size)를 잘라낸다
    c0 = pad
    box = a[c0:c0 + size, c0 - 1:c0 + size + 1] if conf['shear'] else a[c0:c0 + size, c0:c0 + size]
    out = np.zeros((top + size + 1, box.shape[1]), float)
    out[top:top + size] = box
    return out

PAL = {   # 원본 폰트 팔레트의 알파값(인덱스 0~15)
    'eurostyleSmallPx':  [0, 0, 0, 0x43, 0x6a, 0x1b, 0x58, 0x2f, 0x7a, 0x0a, 0x4c, 0x24, 0x61, 0x38, 0x12, 0x72],
    'eurostyleMediumPx': [0, 0, 0, 0x43, 0x19, 0x6d, 0x59, 0x2e, 0x7a, 0x09, 0x4e, 0x38, 0x64, 0x24, 0x11, 0x74],
    'eurostyleLargePx':  [0, 0, 0, 0x45, 0x1c, 0x6e, 0x31, 0x5b, 0x0a, 0x7b, 0x27, 0x3c, 0x65, 0x50, 0x11, 0x75],
    'fruitigerLarge':    [0, 0, 0, 0x41, 0x6c, 0x18, 0x58, 0x2b, 0x7a, 0x09, 0x36, 0x62, 0x4c, 0x21, 0x75, 0x10],
    'fruitigerMedium':   [0, 0, 0, 0x3d, 0x68, 0x17, 0x54, 0x78, 0x29, 0x08, 0x5f, 0x47, 0x20, 0x33, 0x80, 0x6f],
    'fruitigerTiny':     [0, 0, 0x56, 0x35, 0x63, 0x14, 0x4c, 0x74, 0x24, 0x07, 0x00, 0x43, 0x6d, 0x7d, 0x2e, 0x1b],
}
FAMILY = {n: ['eurostyleMediumPx', 'eurostyleLargePx'] for n in ('eurostyleMediumPx', 'eurostyleLargePx')}   # 실측: 이 둘은 CLUT 공유
FAMILY.update({n: ['fruitigerLarge', 'fruitigerMedium', 'fruitigerTiny'] for n in ('fruitigerLarge', 'fruitigerMedium')})   # 그리드 화면 실측

def robust_lut(name):
    pals = np.array([PAL[m] for m in FAMILY[name]], float)
    lo, hi = pals.min(0), pals.max(0)
    ok = [k for k in range(16) if hi[k] - lo[k] <= 0x12]          # 계열 전체에서 값이 거의 같은 인덱스
    mid = (lo + hi) / 2
    top = max(mid[k] for k in ok)
    lut = np.zeros(256, np.uint8)
    for v in range(256):
        t = v / 255 * top
        lut[v] = min(ok, key=lambda k: abs(mid[k] - t))
    return lut

def canonical_palette(f):
    """폰트마다 뒤섞인 팔레트를 '인덱스 순 = 투명도 순' 공통 팔레트로 통일하고 픽셀을 재매핑."""
    c = bytearray(f.clut)
    i = c.find(bytes.fromhex('0800000002000000520000000000000000'))
    p = c.find(bytes.fromhex('0480000000000008'), i) + 8
    old = [c[p + 4 * k + 3] for k in range(16)]
    rgb = bytes(c[p + 4 * 15:p + 4 * 15 + 3]) if old[15] else b'\xff\xff\xff'
    for k in range(16):
        if old[k]: rgb = bytes(c[p + 4 * k:p + 4 * k + 3]); break
    new = [0] + [round(k * 0x80 / 15) for k in range(1, 16)]
    remap = np.array([int(np.argmin([abs(n - o) for n in new])) for o in old], np.uint8)
    f.img = remap[f.img]
    for k in range(16):
        c[p + 4 * k:p + 4 * k + 4] = (rgb if k else b'\0\0\0') + bytes([new[k]])
    f.clut = bytes(c)

def add_hangul(f, name, chars):
    conf = CONF[name]
    # 게임은 같은 계열 폰트끼리 CLUT 하나를 공유한다 → 계열 내 모든 팔레트에서 같은 투명도가 나오는 인덱스만 사용
    lut = robust_lut(name) if name in FAMILY else alpha_to_index(palette_alpha(f))
    zero = lut[0]
    glyphs = []
    tid = os.environ.get('FONTID')
    for ch in chars:
        a = render(str(list(CONF).index(name)) if tid else ch, conf)
        g = lut[np.clip(a, 0, 255).astype(np.uint8)]
        glyphs.append((ord(ch), g))
    # 원본 사용 영역
    used_h = 0
    for c, g in f.glyphs.items():
        y0 = round((1 - g[5]) * f.H); used_h = max(used_h, y0 + int(g[1]))
    gh = glyphs[0][1].shape[0]; gw = glyphs[0][1].shape[1]
    MAXW = conf.get('maxw', int(os.environ.get('FONT_MAXW', '512')))

    def slots(W, H):
        """빈 칸 좌표: 원본 글리프 영역 오른쪽(가능하면) → 그 아래 전체 폭"""
        out = []
        if W > f.W:
            y = 0
            while y + gh <= used_h:
                x = f.W + 1
                while x + gw < W: out.append((x, y)); x += gw + 1
                y += gh + 1
        y = used_h + 1
        while y + gh <= H:
            x = 1
            while x + gw < W: out.append((x, y)); x += gw + 1
            y += gh + 1
        return out

    W, H = max(f.W, 256), f.H
    while len(slots(W, H)) < len(glyphs):
        if W < MAXW and W <= H: W *= 2
        else: H *= 2
        assert H <= 1024, (name, W, H)
    pos = slots(W, H)
    img = np.full((H, W), zero, np.uint8)
    img[:f.H, :f.W] = f.img
    adv = conf['size'] + conf['gap']
    for (code, g), (x, y) in zip(glyphs, pos):
        img[y:y + gh, x:x + gw] = g
        h, w = g.shape
        xoff = -1 if conf['shear'] else 0
        f.glyphs[code] = [float(w), float(h), x / W, (x + w) / W, 1 - (y + h) / H, 1 - y / H, float(adv), float(xoff)]

    # 기존 글리프 UV 재계산 (텍스처 크기 변경)
    if (W, H) != (f.W, f.H):
        for code, g in f.glyphs.items():
            if code >= 0xAC00 and code <= 0xD7A3: continue
            g[2] *= f.W / W; g[3] *= f.W / W
            y0 = (1 - g[5]) * f.H; y1 = (1 - g[4]) * f.H
            g[5] = 1 - y0 / H; g[4] = 1 - y1 / H
    f.W, f.H, f.img = W, H, img
    return f

def preview(f, path):
    Image.fromarray((f.img.astype(np.uint16) * 17).clip(0, 255).astype(np.uint8)).save(path)
