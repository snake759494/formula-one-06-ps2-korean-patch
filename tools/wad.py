import struct,sys
def read(path):
    d=open(path,'rb').read()
    n=struct.unpack_from('<I',d,4)[0]
    return d,[struct.unpack_from('<4I',d,8+i*16) for i in range(n)]
if __name__=='__main__':
    d,e=read(sys.argv[1])
    for i,(h,o,a,b) in enumerate(e):
        print(i,'%08x %08x %8x %8x'%(h,o,a,b),d[o:o+16].hex())
T=[]
for i in range(256):
    c=i
    for _ in range(8): c=(c>>1)^0xedb88320 if c&1 else c>>1
    T.append(c)
def h(name):
    c=0
    for ch in name.lower().replace(chr(92),"/").encode("latin1"): c=T[(c^ch)&0xff]^(c>>8)
    return (~c)&0xffffffff
