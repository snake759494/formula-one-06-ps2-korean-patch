# F1 06 .blf localisation file: serialized red-black tree (hash -> pool offset) + UTF-8 string pool.
# header 9 u32: [n][n][2][n+1][root][-1][n+1][0][0], then n*4 bytes (unused), then (n+2) nodes of 40 bytes,
# node: [hash][stroff][color][?][idx][left][right][parent][flag][pad]. pool starts right after nodes;
# string = pool[stroff:] up to NUL.
import struct

def layout(d):
    n = struct.unpack_from('<I', d)[0]
    nodes = 0x24 + n * 4
    pool = nodes + (n + 2) * 40
    return n, nodes, pool

def parse(d):
    n, nodes, pool = layout(d)
    out = []
    for k in range(n + 2):
        p = nodes + k * 40
        h, off, _, _, idx = struct.unpack_from('<IIIiI', d, p)
        if idx != k or off == 0 and k < 2: continue
        e = d.index(b'\0', pool + off)
        out.append((k, h, d[pool + off:e].decode('utf-8')))
    return out

def rebuild(d, texts):
    """texts: dict hash -> new str. Rewrites pool (dedup) and node offsets."""
    n, nodes, pool = layout(d)
    d = bytearray(d)
    head = bytes(d[pool:pool + 4])            # keep leading junk so offsets stay >= 1
    newpool = bytearray(head); seen = {}
    for k in range(n + 2):
        p = nodes + k * 40
        h, off, _, _, idx = struct.unpack_from('<IIIiI', d, p)
        if idx != k: continue
        e = d.index(b'\0', pool + off)
        s = texts.get(h)
        b = s.encode('utf-8') if s is not None else bytes(d[pool + off:e])
        if b not in seen:
            seen[b] = len(newpool); newpool += b + b'\0'
        struct.pack_into('<I', d, p + 4, seen[b])
    return bytes(d[:pool]) + bytes(newpool)
