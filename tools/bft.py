# F1 06 .bft bitmap font
# [u32 0][u32 lineheight] + glyph tree (rbt: 7 u32 header, (n+2)*4 junk, (n+2)*72 nodes) + [extra blob (kerning trees)] + pct texture
# node(72): [u16 code][u16 junk][f32 w, h, u0, u1, v0, v1, advance, xoff][i32 -1] + tail 7 i32 (rbt) + [u8 flag][3 junk]
# texture: PSMT4, uploaded as PSMCT32 (w/2 x h/4); v measured from bottom (y = (1-v)*H)
import struct, re, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import rbt, gsmem

class Font:
    pass

def parse(d):
    f = Font()
    f.head = d[:8]
    n = struct.unpack_from('<I', d, 8)[0]
    nodes = 0x24 + (n + 2) * 4
    f.sentinel = d[nodes:nodes + 144]
    f.glyphs = {}; f.aux = {}
    for k in range(2, n + 2):
        p = nodes + k * 72
        code, b23 = struct.unpack_from('<HH', d, p)
        f.glyphs[code] = list(struct.unpack_from('<8f', d, p + 4))
        f.aux[code] = (b23, struct.unpack_from('<i', d, p + 36)[0])   # +36 = 커닝 테이블 번호(-1 없음)
    e = nodes + (n + 2) * 72
    m = re.search(rb'[\x55-\xaa]\x04\x40\x20', d[e:])
    f.extra = d[e:e + m.start()]
    t = d[e + m.start():]
    f.tex = t
    hdr = t[:13]
    f.W = 1 << (hdr[0] & 15); f.H = 1 << (hdr[0] >> 4)
    nb = f.W * f.H // 2
    px = np.frombuffer(t[0xcd:0xcd + nb], np.uint8).reshape(f.H // 4, f.W // 2, 4)
    vm = np.zeros(4 << 20, np.uint8)
    idx = gsmem.index32(0, f.W // 128 if f.W >= 128 else 1, f.W // 2, f.H // 4)
    for c in range(4): vm[idx + c] = px[:, :, c]
    f.img = gsmem.read4(vm, 0, max(2, f.W // 64), f.W, f.H)
    f.clut = t[0xcd + nb:]
    return f

def swizzle(img):
    H, W = img.shape
    vm = np.zeros(4 << 20, np.uint8)
    a = np.array([[gsmem.addr4(0, max(2, W // 64), x, y) for x in range(W)] for y in range(H)], np.int64)
    b = a >> 1
    lo = (a & 1) == 0
    np.bitwise_or.at(vm, b[lo], img[lo] & 15)
    np.bitwise_or.at(vm, b[~lo], (img[~lo] & 15) << 4)
    idx = gsmem.index32(0, W // 128 if W >= 128 else 1, W // 2, H // 4)
    return np.stack([vm[idx + c] for c in range(4)], -1).astype(np.uint8).tobytes()

def build_tex(f, img):
    H, W = img.shape
    t = bytearray(f.tex[:0xcd])
    nb = W * H // 2
    blocks = nb // 256
    t[0] = (H.bit_length() - 1) << 4 | (W.bit_length() - 1)
    struct.pack_into('<HH', t, 4, H, W)
    struct.pack_into('<H', t, 10, blocks)
    struct.pack_into('<H', t, 12, blocks + 1)   # u16 (byte 13 was 0)
    t[0x27] = W // 128 if W >= 128 else 1        # DBW of CT32 upload
    struct.pack_into('<H', t, 0x2d, blocks)
    t[0x6a] = nb // 4096 if nb >= 4096 else 1
    struct.pack_into('<II', t, 0x9d, W // 2, H // 4)   # TRXREG
    struct.pack_into('<H', t, 0xbd, nb // 16)          # IMAGE nloop
    return bytes(t) + swizzle(img) + f.clut

def build(f, img=None):
    codes = sorted(f.glyphs)
    n = len(codes)
    tails, root = rbt.tails(n)
    out = bytearray(f.head)
    out += struct.pack('<7i', n, n, 2, n + 1, root, -1, n + 1)
    out += bytes((n + 2) * 4)
    out += f.sentinel
    for k, c in enumerate(codes, 2):
        g = f.glyphs[c]
        b23, kern = f.aux.get(c, (0xff, -1))
        out += struct.pack('<HH8fi', c, b23, *g, kern)
        out += struct.pack('<7i', *tails[k])
        out += bytes([0, 0, 0, 0])
    out += f.extra
    out += build_tex(f, f.img if img is None else img)
    return bytes(out)
