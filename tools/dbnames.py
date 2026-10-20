# 드라이버·팀 데이터베이스(STARTUP/F12006 0x873A829C) 문자열 교체
# 레코드 = [헤더(u32들, 문자열 오프셋 목록 포함, -1로 끝)] [u32 블록크기] [NUL로 끝나는 문자열들]
# 문자열을 바꾸면 블록을 다시 만들고, 헤더의 오프셋(이전 문자열 시작값)을 새 시작값으로 고친다.
import struct, re

def blocks(t):
    """('drivers/'|'teams/') 경로를 가진 문자열 블록들: (헤더시작, 크기필드위치, 블록시작, 블록끝)"""
    out = []
    for m in re.finditer(rb'\x00(drivers|teams)/[^\x00]+\x00', t):
        path = m.start() + 1
        for q in range(path, max(0, path - 600), -1):
            n = struct.unpack_from('<I', t, q - 4)[0]
            if 4 < n < 600 and q + n > path and t[q + n - 1] == 0 and (q == 4 or t[q - 5] in (0, 0xff) or True):
                if all(t[q + i] != 0 or True for i in range(1)):
                    # 블록 안 문자열이 모두 정상 UTF-8인지 확인
                    try:
                        t[q:q + n].decode('utf-8'); out.append((q - 4, q, q + n)); break
                    except UnicodeDecodeError:
                        pass
    return out

def strings(t, q, end):
    s = t[q:end].split(b'\x00')[:-1]
    starts = []; p = 0
    for x in s: starts.append(p); p += len(x) + 1
    return [x.decode('utf-8') for x in s], starts

def rebuild(t, fn):
    """fn(문자열 목록) -> 새 목록 (드라이버/팀 블록마다 호출)"""
    bl = blocks(t)
    out = bytearray(); prev = 0
    for szpos, q, end in bl:
        head = bytearray(t[prev:szpos])
        ss, starts = strings(t, q, end)
        new = fn(list(ss))
        nb = b''.join(x.encode('utf-8') + b'\x00' for x in new)
        nstarts = []; p = 0
        for x in new: nstarts.append(p); p += len(x.encode('utf-8')) + 1
        mp = {o: n for o, n in zip(starts, nstarts) if o}
        # 이 레코드 헤더 범위: 직전 블록 끝 ~ 크기필드. -1 이전의 u32 중 문자열 시작값이면 교체
        hstart = 0
        ff = head.rfind(b'\xff\xff\xff\xff')
        lim = ff if ff >= 0 else len(head)
        # 오프셋 목록은 -1 바로 앞에 연속으로 놓인다: 뒤에서부터 거꾸로 읽어 문자열 시작값인 동안만 교체
        k = lim - 4
        while k >= 0:
            v = struct.unpack_from('<I', head, k)[0]
            if v in mp: struct.pack_into('<I', head, k, mp[v]); k -= 4
            else: break
        out += head + struct.pack('<I', len(nb)) + nb
        prev = end
    out += t[prev:]
    return bytes(out)
