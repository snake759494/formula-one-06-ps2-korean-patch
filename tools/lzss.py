# F1 06 WAD LZSS: MSB-first bit flags. 1 -> 8-bit literal, 0 -> 13-bit absolute window pos + 4-bit (len-3).
# window 0x2000, write position starts at 1.
def decompress(src, size):
    out = bytearray(); win = bytearray(0x2000); wp = 1
    pos = 0; mask = 0; cur = 0
    def bits(n):
        nonlocal pos, mask, cur
        v = 0
        for _ in range(n):
            if mask == 0:
                cur = src[pos]; pos += 1; mask = 0x80
            v = (v << 1) | (1 if cur & mask else 0)
            mask >>= 1
        return v
    while len(out) < size:
        if bits(1):
            b = bits(8); out.append(b); win[wp] = b; wp = (wp + 1) & 0x1fff
        else:
            off = bits(13); ln = bits(4) + 3
            for i in range(ln):
                if len(out) >= size: break
                b = win[(off + i) & 0x1fff]; out.append(b); win[wp] = b; wp = (wp + 1) & 0x1fff
    return bytes(out)

def get(d, ent):
    h, o, a, b = ent
    return d[o:o + b] if a == b else decompress(d[o:o + b], a)
