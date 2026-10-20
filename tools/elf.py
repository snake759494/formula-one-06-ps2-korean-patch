import struct,capstone,sys
D=open('work/orig/SCES_539.50','rb').read()
ph=struct.unpack_from('<I',D,0x1c)[0];n=struct.unpack_from('<H',D,0x2c)[0]
segs=[]
for i in range(n):
    t,off,va,pa,fs,ms=struct.unpack_from('<6I',D,ph+i*32)
    if t==1: segs.append((va,off,fs))
def v2o(v):
    for va,off,fs in segs:
        if va<=v<va+fs: return v-va+off
def o2v(o):
    for va,off,fs in segs:
        if off<=o<off+fs: return o-off+va
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS64+capstone.CS_MODE_LITTLE_ENDIAN)
def dis(v,cnt=60):
    o=v2o(v);out=[]
    for k in range(cnt):
        w=D[o+4*k:o+4*k+4]
        ins=list(md.disasm(w,v+4*k))
        out.append('%08x: %s'%(v+4*k,(ins[0].mnemonic+' '+ins[0].op_str) if ins else w.hex()))
    return '\n'.join(out)
def xrefs(target):
    """find lui/addiu pairs referencing target address"""
    hi=(target+0x8000)>>16;lo=(target-(hi<<16))&0xffff;res=[]
    for va,off,fs in segs:
        for k in range(0,fs-4,4):
            w=struct.unpack_from('<I',D,off+k)[0]
            if (w>>26)==0xf and (w&0xffff)==hi:
                rt=(w>>16)&31
                for j in range(1,12):
                    w2=struct.unpack_from('<I',D,off+k+4*j)[0]
                    if (w2&0xffff)==lo and ((w2>>21)&31)==rt: res.append(va+k);break
    return res
if __name__=='__main__':
    if sys.argv[1]=='d': print(dis(int(sys.argv[2],16),int(sys.argv[3]) if len(sys.argv)>3 else 60))
    elif sys.argv[1]=='x': print([hex(x) for x in xrefs(o2v(int(sys.argv[2],16)))])
    elif sys.argv[1]=='s': print(segs)
