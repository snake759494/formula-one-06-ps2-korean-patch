import struct,sys
def walk(f,lba,size,path=''):
    f.seek(lba*2048);d=f.read(size);p=0;out=[]
    while p<len(d):
        n=d[p]
        if n==0: p=(p//2048+1)*2048;continue
        l,s=struct.unpack_from('<I',d,p+2)[0],struct.unpack_from('<I',d,p+10)[0]
        fl=d[p+25];nm=d[p+33:p+33+d[p+32]].decode('latin1').split(';')[0]
        if nm not in('\x00','\x01'):
            full=path+'/'+nm
            if fl&2: out+=walk(f,l,s,full)
            else: out.append((full,l,s,lba*2048+p))
        p+=n
    return out
def records(f):
    f.seek(16*2048);pvd=f.read(2048)
    return walk(f,struct.unpack_from('<I',pvd,158)[0],struct.unpack_from('<I',pvd,166)[0])
if __name__=='__main__':
    for r in sorted(records(open(sys.argv[1],'rb')),key=lambda x:x[1]): print(*r)
