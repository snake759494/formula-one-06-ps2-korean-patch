import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from iso import records
iso=sys.argv[1];f=open(iso,'rb')
for p,l,s,_ in records(f):
    if any(p.endswith(x) for x in sys.argv[2:]):
        f.seek(l*2048);o='work/orig'+p;os.makedirs(os.path.dirname(o),exist_ok=True);open(o,'wb').write(f.read(s));print(o)
