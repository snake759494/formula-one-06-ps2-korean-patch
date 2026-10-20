import re,glob,collections
en=dict(l.split('\t',1) for l in open('translation/en.tsv',encoding='utf-8').read().splitlines())
ko={}
for fn in sorted(glob.glob('translation/ko/ko_*.tsv')):
    for l in open(fn,encoding='utf-8').read().splitlines():
        if l.strip(): i,s=l.split('\t',1); ko[i]=s
print('en',len(en),'ko',len(ko),'missing',len(set(en)-set(ko)),'extra',len(set(ko)-set(en)))
P=re.compile(r'<[^<>]{1,20}>|%[-\d.]*[a-z%]')
bad=0
for i,s in en.items():
    k=ko.get(i)
    if k is None: continue
    if collections.Counter(P.findall(s))!=collections.Counter(P.findall(k)) or s.count('\n')!=k.count('\n'):
        bad+=1;print(i,s[:80],'|',k[:80])
print('bad',bad)
