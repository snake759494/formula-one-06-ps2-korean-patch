# Formula One 06 (PAL) 한글 패치 빌드
#   python tools/build.py            -> work/out/*.WAD 생성 + 한글 ISO 갱신
import os, sys, struct, shutil, glob, re
sys.path.insert(0, os.path.dirname(__file__))
import wad, lzss, blf, bft, kfont, iso, udf, dbnames, names_db
from export_text import unesc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ORIG_ISO = 'Formula One 06 (Europe, Australia) (En,Fr,De,Es,It,Pt,Fi).iso'
OUT_ISO = 'Formula One 06 (Europe, Australia) (Korean).iso'
SEC = 2048

ENGLISH_BLF = ['5361ae57', 'e73b4e14', '366ae106', 'e90d5167']   # sys / main(2017) / main(2803) / career
FONTS = ['eurostyleSmallPx', 'eurostyleMediumPx', 'eurostyleLargePx', 'fruitigerTiny', 'fruitigerMedium',
         'fruitigerLarge', 'Small', 'tv2004_frb']
WADS = ['STARTUP', 'F12006', 'CAREER2']

# 한국어 문장에서 폰트에 없는 기호 정규화
NORM = {'…': '...', '·': '.', '～': '~', '‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-',
        ' ': ' ', '「': '"', '」': '"', '『': '"', '』': '"', '×': 'x', '→': '->', '％': '%'}

def load_translation():
    en = {}
    for line in open('translation/en.tsv', encoding='utf-8').read().splitlines():
        i, s = line.split('\t', 1); en[i] = unesc(s)
    ko = {}
    for fn in sorted(glob.glob('translation/ko/ko_*.tsv')):
        if '.part' in fn: continue
        for line in open(fn, encoding='utf-8').read().splitlines():
            if not line.strip(): continue
            i, s = line.split('\t', 1)
            s = unesc(s)
            for a, b in NORM.items(): s = s.replace(a, b)
            ko[i] = s
    tr = {}
    for i, s in en.items():
        if i in ko: tr[s] = ko[i]
    return tr

def read_entry(d, ent):
    return lzss.get(d, ent)

def wad_patch(src, repl, dst):
    """repl: hash -> bytes. 바뀐 항목은 WAD 끝에 비압축으로 덧붙인다."""
    d = bytearray(open(src, 'rb').read())
    n = struct.unpack_from('<I', d, 4)[0]
    for i in range(n):
        h, o, a, b = struct.unpack_from('<4I', d, 8 + i * 16)
        if h in repl:
            data = repl[h]
            while len(d) % 0x40: d.append(0)
            off = len(d); d += data
            struct.pack_into('<4I', d, 8 + i * 16, h, off, len(data), len(data))
    while len(d) % SEC: d.append(0)
    open(dst, 'wb').write(d)

def prepare():
    """원본 ISO 에서 WAD 를 꺼내고 영어 텍스트·폰트를 풀어 둔다(없을 때만)."""
    if not os.path.exists('work/orig/DATA2006/F12006.WAD'):
        with open(ORIG_ISO, 'rb') as f:
            for p, l, s, _ in iso.records(f):
                if p.startswith('/DATA2006/') and p[10:-4] in WADS:
                    os.makedirs('work/orig/DATA2006', exist_ok=True)
                    f.seek(l * SEC); open('work/orig' + p, 'wb').write(f.read(s))
    os.makedirs('work/blf', exist_ok=True); os.makedirs('work/font', exist_ok=True)
    d, e = wad.read('work/orig/DATA2006/F12006.WAD'); m = {x[0]: x for x in e}
    for name in ENGLISH_BLF:
        if not os.path.exists('work/blf/%s.blf' % name):
            open('work/blf/%s.blf' % name, 'wb').write(lzss.get(d, m[int(name, 16)]))
    for fn in FONTS:
        p = 'work/font/F12006_%s.bft' % fn
        if not os.path.exists(p): open(p, 'wb').write(lzss.get(d, m[wad.h('Fonts/%s.bft' % fn)]))

def main():
    prepare()
    os.makedirs('work/out', exist_ok=True)
    tr = load_translation()
    print('translations', len(tr))
    # 0) 한글 코드 재배정: 레이스 쪽 텍스트 코드가 U+2200 위 문자를 그리지 못하고(빈칸), 드라이버 DB에 넣으면
    #    레이스 로딩이 멈춘다. 쓰이는 한글을 대소문자가 없는 낮은 영역(2바이트 UTF-8)에 차례로 배정한다.
    d, e = wad.read('work/orig/DATA2006/STARTUP.WAD'); m = {x[0]: x for x in e}
    rawdb = lzss.get(d, m[0x873A829C])
    db_ko = dbnames.rebuild(rawdb, names_db.convert)
    used = set(''.join(tr.values())) | set('한국어')
    for bl in dbnames.blocks(db_ko):
        used |= set(db_ko[bl[1]:bl[2]].decode('utf-8'))
    hangul = sorted(c for c in used if 0xAC00 <= ord(c) <= 0xD7A3)
    if os.environ.get('LIMIT_HANGUL'): hangul = hangul[:int(os.environ['LIMIT_HANGUL'])]
    slots = list(range(0x250, 0x370)) + list(range(0x590, 0x800))
    assert len(hangul) <= len(slots), len(hangul)
    cmap = {c: chr(slots[i]) for i, c in enumerate(hangul)}
    def enc(s):
        return ''.join(cmap.get(ch, ch) for ch in s)
    # 레이스 쪽에서도 쓰는 글꼴(ui=True)에는 메뉴·시스템 텍스트(m·s 번호)와 드라이버·팀 이름 글자만 넣는다
    ui = set('한국어')
    for fn_ in glob.glob('translation/ko/ko_*.tsv'):
        for l in open(fn_, encoding='utf-8').read().splitlines():
            if '	' in l and l[0] in 'ms': ui |= set(l.split('	', 1)[1])
    for bl in dbnames.blocks(db_ko):
        ui |= set(db_ko[bl[1]:bl[2]].decode('utf-8'))
    ui_chars = [c for c in hangul if c in ui]
    print('hangul chars', len(hangul), 'mapped to U+%04X..U+%04X' % (slots[0], slots[len(hangul) - 1]))
    # 1) 텍스트
    newblf = {}
    miss = 0
    for name in ENGLISH_BLF:
        raw = open('work/blf/%s.blf' % name, 'rb').read()
        texts = {}
        for k, h, s_ in blf.parse(raw):
            if s_ in tr:
                texts[h] = enc(tr[s_])
            elif re.search('[A-Za-z]', s_) and not s_.startswith('Medius'):
                miss += 1
        newblf[int(name, 16)] = blf.rebuild(raw, texts)
    print('untranslated', miss)
    # 드라이버·팀 데이터베이스(짧은 표기·표시용 성·팀 이름)
    newdb = dbnames.rebuild(rawdb, lambda ss: [enc(x) for x in names_db.convert(ss)])
    # 2) 폰트
    newfont = {}
    for fn in FONTS:
        raw = open('work/font/F12006_%s.bft' % fn, 'rb').read()
        f = bft.parse(raw)
        other = sorted(c for c in used if ord(c) > 0x7e and not (0xAC00 <= ord(c) <= 0xD7A3) and ord(c) not in f.glyphs)
        if other: print('  missing glyphs in', fn, other)
        full = os.environ.get('FULL_FONTS')
        chars = ui_chars if kfont.CONF[fn].get('ui') else hangul
        kfont.add_hangul(f, fn, chars if not full or fn in full.split(',') else chars[:1], codes=cmap)
        newfont[wad.h('Fonts/%s.bft' % fn)] = bft.build(f)
        kfont.preview(f, 'work/out/font_%s.png' % fn)
        print('  font', fn, f.W, f.H, len(newfont[wad.h('Fonts/%s.bft' % fn)]))
    repl = dict(newblf); repl.update(newfont)
    # 드라이버·팀 DB에 한글을 넣으면 퀵 레이스 로딩이 멈춘다(v1.1 제보). DB_KO=1 일 때만 적용
    if os.environ.get('DB_KO'): repl[0x873A829C] = newdb
    # 언어 선택 메뉴 스크립트: ENGLISH -> 한국어 (u8 형식 4, u32 길이(NUL 포함), 문자열)
    old = b'\x04\x08\x00\x00\x00ENGLISH\x00'
    ko = enc('한국어 ').encode('utf-8')    # 길이 고정(7바이트): 재배정한 한글은 2바이트 -> '한국어 '
    new = b'\x04' + struct.pack('<I', len(ko) + 1) + ko + b'\x00'
    for w in ('STARTUP', 'F12006'):
        d, e = wad.read('work/orig/DATA2006/%s.WAD' % w)
        for x in e:
            if x[0] in repl or x[2] > 300000: continue
            t = lzss.get(d, x)
            if old in t and b'mMenuTextItems' in t:
                repl[x[0]] = t.replace(old, new); print('  lang menu', w, hex(x[0]))
    mode = os.environ.get('TESTMODE', '')
    if mode:   # 원인 분리용: raw=원본 그대로 비압축, fontrt=폰트만 무변경 재구성, textonly=텍스트만
        repl = {}
        for name in ENGLISH_BLF:
            raw = open('work/blf/%s.blf' % name, 'rb').read()
            repl[int(name, 16)] = raw if mode == 'raw' else newblf[int(name, 16)] if mode == 'textonly' else raw
        for fn in FONTS:
            raw = open('work/font/F12006_%s.bft' % fn, 'rb').read()
            k = wad.h('Fonts/%s.bft' % fn)
            if mode == 'raw': repl[k] = raw
            elif mode == 'fontrt': repl[k] = bft.build(bft.parse(raw))
        print('TESTMODE', mode, len(repl))
    # 3) WAD
    for w in WADS:
        wad_patch('work/orig/DATA2006/%s.WAD' % w, repl, 'work/out/%s.WAD' % w)
        print('wad', w, os.path.getsize('work/out/%s.WAD' % w))
    # 4) ISO
    build_iso()
    # 5) 한국어 음성(해설·무전) 제자리 교체
    import dub_inject
    dub_inject.inject(OUT_ISO)

def build_iso():
    orig_size = os.path.getsize(ORIG_ISO)
    nsec = orig_size // SEC
    meta = 4096                                   # 앞부분(디렉터리·UDF 메타) 섹터 수
    if not os.path.exists(OUT_ISO):
        print('copy iso ...'); shutil.copyfile(ORIG_ISO, OUT_ISO)
    with open(ORIG_ISO, 'rb') as fo, open(OUT_ISO, 'r+b') as f:
        f.truncate(orig_size)
        fo.seek(0); f.seek(0); f.write(fo.read(meta * SEC))
        recs = {p: (l, s, r) for p, l, s, r in iso.records(fo)}
        u = udf.UDF(f)
        pos = nsec
        for w in WADS:
            path = '/DATA2006/%s.WAD' % w
            data = open('work/out/%s.WAD' % w, 'rb').read()
            f.seek(pos * SEC); f.write(data)
            l, s, r = recs[path]
            f.seek(r + 2); f.write(struct.pack('<I', pos) + struct.pack('>I', pos))
            f.seek(r + 10); f.write(struct.pack('<I', len(data)) + struct.pack('>I', len(data)))
            u.set_file(path, pos, len(data))
            print('  %s -> LBA %d size %d' % (path, pos, len(data)))
            pos += len(data) // SEC
        total = pos + 1                             # 마지막 섹터 = UDF 앵커
        f.seek(total * SEC - 1); f.write(b'\0')
        # PVD volume space size
        f.seek(16 * SEC + 80); f.write(struct.pack('<I', total) + struct.pack('>I', total))
        u.grow(total)
    print('iso', OUT_ISO, os.path.getsize(OUT_ISO) / 1e9, 'GB', total, 'sectors')

if __name__ == '__main__':
    main()
