import re,sys
d=open(sys.argv[1],'rb').read();pat=sys.argv[2] if len(sys.argv)>2 else '.'
for m in re.finditer(rb'[\x20-\x7e]{6,}',d):
    s=m.group().decode()
    if re.search(pat,s,re.I): print(hex(m.start()),s)
