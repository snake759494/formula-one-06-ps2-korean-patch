import os
# 드라이버·팀 데이터베이스 한글 표기
# 드라이버: id -> (이름, 성, 짧은 표기, 표시용 성, 출생지)
DRIVERS = {
    'falonso': ('페르난도', '알론소', 'F. 알론소', '알론소', '스페인 오비에도'),
    'gfisichella': ('잔카를로', '피지켈라', 'G. 피지켈라', '피지켈라', '이탈리아 로마'),
    'kraikkonen': ('키미', '라이코넨', 'K. 라이코넨', '라이코넨', '핀란드 에스포'),
    'jmontoya': ('후안 파블로', '몬토야', 'J. 몬토야', '몬토야', '콜롬비아 보고타'),
    'mschumacher': ('미하엘', '슈마허', 'M. 슈마허', 'M 슈마허', '독일 휘르트헤르뮐하임'),
    'fmassa': ('펠리페', '마사', 'F. 마사', '마사', '브라질 상파울루'),
    'rschumacher': ('랄프', '슈마허', 'R. 슈마허', 'R 슈마허', '독일 휘르트헤르뮐하임'),
    'jtrulli': ('야르노', '트룰리', 'J. 트룰리', '트룰리', '이탈리아 페스카라'),
    'mwebber': ('마크', '웨버', 'M. 웨버', '웨버', '호주 퀸비언'),
    'nrosberg': ('니코', '로즈버그', 'N. 로즈버그', '로즈버그', '독일 비스바덴'),
    'rbarrichello': ('루벤스', '바리첼로', 'R. 바리첼로', '바리첼로', '브라질 상파울루'),
    'jbutton': ('젠슨', '버튼', 'J. 버튼', '버튼', '영국 프롬'),
    'dcoulthard': ('데이비드', '쿨사드', 'D. 쿨사드', '쿨사드', '스코틀랜드 트윈홈'),
    'cklien': ('크리스티안', '클린', 'C. 클린', '클린', '오스트리아 호에넴스'),
    'nheidfeld': ('닉', '하이드펠트', 'N. 하이드펠트', '하이드펠트', '독일 묀헨글라트바흐'),
    'jvilleneuve': ('자크', '빌뇌브', 'J. 빌뇌브', '빌뇌브', '캐나다 생장쉬르리슐리외'),
    'tmonteiro': ('티아구', '몬테이루', 'T. 몬테이루', '몬테이루', '포르투갈 포르투'),
    'calbers': ('크리스티얀', '알버스', 'C. 알버스', '알버스', '네덜란드 아인트호번'),
    'vliuzzi': ('비탄토니오', '리우치', 'V. 리우치', '리우치', '이탈리아 로코로톤도'),
    'sspeed': ('스콧', '스피드', 'S. 스피드', '스피드', '미국 만티카'),
    'tsato': ('타쿠마', '사토', 'T. 사토', '사토', '일본 도쿄'),
    'yide': ('유지', '이데', 'Y. 이데', '이데', '일본 사이타마'),
}
for k in range(1, 7):
    DRIVERS['classic%d' % k] = DRIVERS['mschumacher']

# 팀: id -> (정식 이름, 짧은 이름, 엔진/차량 표기, 본거지)
TEAMS = {
    'Renault': ('르노 F1 팀', '르노', '르노', '영국 엔스톤'),
    'McLaren': ('맥라렌 메르세데스', '맥라렌', '맥라렌 메르세데스', '영국 워킹'),
    'Ferrari': ('스쿠데리아 페라리', '페라리', '페라리', '이탈리아 마라넬로'),
    'Toyota': ('파나소닉 토요타 레이싱', '토요타', '토요타', '독일 쾰른'),
    'Williams': ('윌리엄스 F1 팀', '윌리엄스', '윌리엄스 코스워스', '영국 그로브'),
    'Honda': ('혼다 레이싱 F1 팀', '혼다', '혼다', '영국 브래클리'),
    'RedBull': ('레드불 레이싱', '레드불', 'RBR 페라리', '영국 밀턴킨스'),
    'BMW': ('BMW 자우버 F1 팀', 'BMW 자우버', '자우버 BMW', '스위스 힌빌'),
    'Midland': ('MF1 레이싱', 'MF1', 'MF1 토요타', '영국 실버스톤'),
    'ToroRosso': ('스쿠데리아 토로 로소', '토로 로소', 'STR 코스워스', '영국 밀턴킨스'),
    'SuperAguri': ('슈퍼 아구리 F1 팀', '슈퍼 아구리', '아구리 혼다', '영국 브래클리'),
    'Lotus72e': ('로터스 72E', '로터스 72E', '로터스 72E', None),
    'CooperClimax': ('쿠퍼 클라이맥스', '쿠퍼 클라이맥스', '쿠퍼 클라이맥스', None),
    'Lotus49c': ('로터스 49C', '로터스 49C', '로터스 49C', None),
    'WilliamsFW18': ('윌리엄스 FW18', '윌리엄스 FW18', '윌리엄스 FW18', None),
    'WilliamsFW06': ('윌리엄스 FW06', '윌리엄스 FW06', '윌리엄스 FW06', None),
    'Alfa158': ('알파 로메오 158', '알파 로메오 158', '알파 로메오 158', None),
    'online': ('온라인', '온라인', '온라인', '이탈리아 마라넬로'),
    'Safety': ('세이프티 팀', '세이프티 팀', '세이프티 팀', None),
    'Studio': ('F1 06 콘셉트', 'F1 06 콘셉트', 'F1 06 콘셉트', '영국 브래클리'),
}
COUNTRY = {'Britain': '영국', 'France': '프랑스', 'Monaco': '모나코', 'Belgium': '벨기에', 'Australia': '호주',
           'Argentina': '아르헨티나', 'South Africa': '남아공', 'USA': '미국', 'Bahrain': '바레인'}

def _debut(s):
    for en, ko in COUNTRY.items():
        if s.startswith(en + ' '): return ko + s[len(en):]
    return s

SHORTER = {   # 원문 길이를 넘을 때 쓰는 짧은 후보
    '파나소닉 토요타 레이싱': '토요타 레이싱', '스쿠데리아 토로 로소': '토로 로소', '맥라렌 메르세데스': '맥라렌',
    '혼다 레이싱 F1 팀': '혼다 F1 팀', '슈퍼 아구리 F1 팀': '슈퍼 아구리', 'BMW 자우버 F1 팀': 'BMW 자우버',
    '스쿠데리아 페라리': '페라리', '윌리엄스 코스워스': '윌리엄스', '알파 로메오 158': '알파 158',
    '쿠퍼 클라이맥스': '쿠퍼', 'F1 06 콘셉트': 'F1 06',
}

def _fit(new, old, alts=()):
    """게임이 고정 크기 버퍼에 복사하므로 원문 바이트 길이를 넘지 않게 한다."""
    lim = len(old.encode('utf-8'))
    for c in (new,) + tuple(alts) + ((SHORTER[new],) if new in SHORTER else ()):
        if c and len(c.encode('utf-8')) <= lim: return c
    return old

SAFE_DRV = {3, 5}      # 표시 전용(짧은 표기, 표시용 성). 이름·성은 내부 키로 쓰여 바꾸면 레이스 로딩이 멈춘다
SAFE_TEAM = {1, 2}

def convert(ss):
    orig = list(ss)
    _convert(ss)
    drv = any(x.startswith('drivers/') for x in orig)
    safe = SAFE_DRV if drv else SAFE_TEAM
    for i, (o, n) in enumerate(zip(orig, ss)):
        if i not in safe: ss[i] = o; continue
        if o != n:
            alts = []
            if drv and i == 3 and ' ' in n: alts = [n.split(' ', 1)[1]]                    # 'F. 알론소' -> '알론소'
            if i in (6, 9) and ' ' in n: alts = [n.split(' ')[-1]]                         # '스페인 오비에도' -> '오비에도'
            ss[i] = _fit(n, o, alts) if os.environ.get("NAMES_FIT") else n
    return ss

def _convert(ss):
    path = next((x for x in ss if x.startswith(('drivers/', 'teams/'))), '')
    if path.startswith('drivers/'):
        d = DRIVERS.get(ss[0])
        if d:
            ss[1], ss[2], ss[3], ss[5] = d[0], d[1], d[2], d[3]
            if len(ss) > 9 and ss[9] not in ('-',): ss[9] = d[4]
            if len(ss) > 10: ss[10] = _debut(ss[10])
            if ss[0] == 'cklien' and ss[-1] == 'Klein': ss[-1] = '클린'
        elif ss[0] == 'playerdriver':
            ss[8] = '스페인'
        elif ss[0] == 'scdriver':
            ss[1], ss[2], ss[3], ss[5] = 'SC', '드라이버', 'SC 드라이버', 'SC 드라이버'
    elif path.startswith('teams/'):
        t = TEAMS.get(ss[0])
        if t:
            ss[1], ss[2], ss[3] = t[0], t[1], t[2]
            if t[3] and len(ss) > 6: ss[6] = t[3]
            for i in (7, 8):
                if len(ss) > i: ss[i] = _debut(ss[i])
            ss[:] = [('* 스튜어트 시절 성적 포함.' if x == '* Results scored under Stewart.' else x) for x in ss]
    return ss
