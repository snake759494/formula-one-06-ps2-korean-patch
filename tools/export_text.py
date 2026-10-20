# 영어 문자열을 번역용 TSV(translation/en.tsv)로 내보낸다. 줄바꿈 CRLF -> \n, 탭 -> \t
import sys, re, os
sys.path.insert(0, os.path.dirname(__file__))
import blf

SETS = [('5361ae57', 'sys'), ('366ae106', 'main'), ('e73b4e14', 'main'), ('e90d5167', 'career')]

def esc(s):
    return s.replace('\\', '\\\\').replace('\r\n', '\\n').replace('\t', '\\t')

def unesc(s):
    out = []; i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            n = s[i + 1]
            out.append({'n': '\r\n', 't': '\t', '\\': '\\'}.get(n, '\\' + n)); i += 2
        else:
            out.append(c); i += 1
    return ''.join(out)

def skip(s):
    return (not re.search('[A-Za-z]', s)) or re.fullmatch(r'Medius\w+', s) is not None

def collect():
    order = []; seen = set()
    for f, tag in SETS:
        for k, h, s in blf.parse(open('work/blf/%s.blf' % f, 'rb').read()):
            if s not in seen:
                seen.add(s); order.append((tag, s))
    rows = []
    for i, (tag, s) in enumerate(order):
        if skip(s): continue
        rows.append(('%s%04d' % (tag[0], i), tag, s))
    return rows

if __name__ == '__main__':
    rows = collect()
    with open('translation/en.tsv', 'w', encoding='utf-8', newline='\n') as f:
        for i, t, s in rows:
            f.write('%s\t%s\n' % (i, esc(s)))
    for t in ['sys', 'main', 'career']:
        print(t, sum(1 for r in rows if r[1] == t), sum(len(r[2]) for r in rows if r[1] == t))
