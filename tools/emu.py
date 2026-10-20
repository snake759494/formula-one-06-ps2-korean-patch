"""테스트 전용: 작업 폴더의 포터블 PCSX2 를 백그라운드(최소화·비활성)로 실행하고
창 메시지(PostMessage)로 키 입력, PINE 상태 저장으로 화면 획득. 사용자 PC 조작을 방해하지 않는다.
  python tools/emu.py launch <iso>
  python tools/emu.py keys K K w2 RET ...   (K=X, L=O, I=△, J=□, RET=START, U/D/LF/RT=방향, wN=대기 N초)
  python tools/emu.py snap <tag>            -> work/shot_<tag>.png
  python tools/emu.py stop
"""
import subprocess, sys, os, time, glob, zipfile, struct, ctypes, socket
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMU = os.path.join(R, 'work', 'emu'); PIDF = os.path.join(EMU, 'emu.pid')
PORT = 28235
u = ctypes.windll.user32
u.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
VK = dict(K=0x4B, L=0x4C, I=0x49, J=0x4A, RET=0x0D, BS=0x08, U=0x26, D=0x28, LF=0x25, RT=0x27, Q=0x51, E=0x45,
          N1=0x31, N3=0x33, W=0x57, A=0x41, S=0x53, DD=0x44, SPACE=0x20, TAB=0x09, F10=0x79)

def windows(pid):
    hs = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(h, l):
        pp = ctypes.c_ulong(); u.GetWindowThreadProcessId(ctypes.c_void_p(h), ctypes.byref(pp))
        if pp.value == pid and u.IsWindowVisible(ctypes.c_void_p(h)): hs.append(h)
        return True
    u.EnumWindows(cb, 0)
    return hs

def all_children(h):
    out = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(c, l):
        out.append(c); return True
    u.EnumChildWindows(ctypes.c_void_p(h), cb, 0)
    return out

def pid():
    return int(open(PIDF).read().strip()) if os.path.exists(PIDF) else None

def launch(iso):
    si = subprocess.STARTUPINFO(); si.dwFlags = 1; si.wShowWindow = 7   # SW_SHOWMINNOACTIVE
    args = [os.path.join(EMU, 'pcsx2-qt.exe'), '-batch', '-nogui', '--', os.path.abspath(iso)]
    p = subprocess.Popen(args, cwd=EMU, startupinfo=si)
    open(PIDF, 'w').write(str(p.pid)); print('pid', p.pid)
    for _ in range(150):
        hs = windows(p.pid)
        if hs:
            time.sleep(1.0)
            for h in windows(p.pid): u.ShowWindow(ctypes.c_void_p(h), 7)
            return
        time.sleep(0.2)

def stop():
    p = pid()
    if p: subprocess.run(['taskkill', '/F', '/PID', str(p)], capture_output=True)
    if os.path.exists(PIDF): os.remove(PIDF)

def key(name, ms=120):
    vk = VK[name]
    sc = u.MapVirtualKeyW(vk, 0)
    ext = 1 << 24 if vk in (0x25, 0x26, 0x27, 0x28) else 0
    targets = []
    for h in windows(pid()):
        targets += [h] + all_children(h)
    for h in targets:
        u.PostMessageW(h, 0x100, vk, 1 | (sc << 16) | ext)
    time.sleep(ms / 1000)
    for h in targets:
        u.PostMessageW(h, 0x101, vk, 1 | (sc << 16) | ext | 0xC0000000)
    time.sleep(0.25)

def pine(payload):
    s = socket.create_connection(('127.0.0.1', PORT), timeout=20)
    s.sendall(struct.pack('<I', len(payload) + 4) + payload)
    b = b''
    while len(b) < 4: b += s.recv(4 - len(b))
    n = struct.unpack('<I', b)[0]; body = b''
    while len(body) < n - 4: body += s.recv(n - 4 - len(body))
    s.close(); return body

def member(p, name):
    with zipfile.ZipFile(p) as z:
        i = z.getinfo(name)
        if i.compress_type in (0, 8): return z.read(name)
    import zstandard
    with open(p, 'rb') as f:
        f.seek(i.header_offset); h = f.read(30); n, e = struct.unpack_from('<HH', h, 26); f.seek(n + e, 1)
        raw = f.read(i.compress_size)
    return zstandard.ZstdDecompressor().decompress(raw, max_output_size=i.file_size)

def latest():
    ps = glob.glob(os.path.join(EMU, 'sstates', '*.p2s'))
    return max(ps, key=os.path.getmtime) if ps else None

def snap(tag, slot=9, ram=False):
    old = latest(); t = os.path.getmtime(old) if old else 0
    pine(struct.pack('<BB', 9, slot))
    p = None
    for _ in range(300):
        p = latest()
        if p and os.path.getmtime(p) > t: time.sleep(1.5); break
        time.sleep(0.1)
    out = os.path.join(R, 'work', 'shot_%s.png' % tag)
    open(out, 'wb').write(member(p, 'Screenshot.png'))
    if ram: open(os.path.join(R, 'work', 'ram_%s.bin' % tag), 'wb').write(member(p, 'eeMemory.bin'))
    print(out)

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'launch': launch(sys.argv[2])
    elif c == 'stop': stop()
    elif c == 'snap': snap(sys.argv[2], ram='--ram' in sys.argv)
    elif c == 'keys':
        for k in sys.argv[2:]:
            if k.startswith('w'): time.sleep(float(k[1:]))
            else: key(k)
    elif c == 'load': print(pine(struct.pack('<BB', 0xa, int(sys.argv[2]))))
