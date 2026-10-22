# Formula One 06 (PS2, 유럽판) 비공식 한글패치

PS2 유럽판 **Formula One 06 (SCES-53950)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·영어 원문·번역 대본·음성은 포함하지 않습니다.

## 적용 방법
1. 아래 해시와 일치하는 **원본 `.iso`** 를 준비합니다. (CSO·CHD 등으로 변환한 이미지에는 적용할 수 없습니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Formula One 06 (Europe, Australia) (En,Fr,De,Es,It,Pt,Fi).iso'`
2. xdeltaUI 같은 도구로 원본에 `Formula_One_06_PS2_KO_v1.2.xdelta` 를 적용합니다.
   - 명령줄: `xdelta3 -d -s "Formula One 06 (Europe, Australia) (En,Fr,De,Es,It,Pt,Fi).iso" Formula_One_06_PS2_KO_v1.2.xdelta "Formula One 06 (Europe, Australia) (Korean).iso"`
3. 만들어진 ISO를 PCSX2 또는 실기(DVD5 용량)에서 실행합니다. 처음 언어 선택에서 **한국어**(원래 ENGLISH 자리)를 고르면 한국어가 나옵니다.

| 항목 | 값 |
| --- | --- |
| 원본 ISO 크기 | 4,418,568,192 바이트 |
| 원본 ISO MD5 | `b72851d1d58528775fa48a36923d8bb5` |
| 원본 ISO SHA-256 | `8d90a2b496ed8148a1e591728c4ccd9f4ebac1150cf377d5f3384d14211f54ef` |
| xdelta SHA-256 | `769e6c4a8ed253e1d6998d0bfcdfff1bfb901aacc41f74323961ea77d18b9d04` |
| 결과 ISO 크기 | 4,684,978,176 바이트 |
| 결과 ISO SHA-256 | `2bd28216b15dd75530105d42c1ac2a72ed7e72a104eb584280f0dc6d72e0e4a6` |

## 한글화 내용
- 화면 텍스트 전체: 메뉴·도움말·옵션·대화 상자·레이스 화면, 커리어 이메일과 F1 뉴스 기사(텍스트 3,940줄)
- 서킷 이름, 화면 텍스트 속 드라이버·팀·차량 이름, 언어 선택의 'ENGLISH' → '한국어'
- 글꼴: 게임 글꼴 8종에 한글 추가 (최대 875자, 나눔스퀘어네오 Regular/Bold, 아주 작은 글씨만 갈무리). 모든 글꼴 텍스처 512×512 이하
- **한국어 음성 더빙**: 레이스 해설·엔지니어 무전·튜토리얼 8,392개, 테스트 세션 무전 668개 클립을 한국어 합성 음성으로 교체
- 화면비 16:9는 게임 옵션의 **화면 비율 → 와이드스크린(16:9)** 으로 설정하고, 에뮬레이터 화면비도 16:9로 맞추면 됩니다.

## AI 음성 고지
한국어 음성은 **Supertonic 3(Supertone) 모델에 내장된 화자**(해설 M4, 무전 M2)로 합성했습니다. 원작 해설자·성우의 목소리를 복제·학습하지 않았습니다. 번역은 기계 번역 서비스를 쓰지 않고 작성했으며, 해설은 이름·순위 조각을 원작 구조(영어 어순)대로 이어 붙이므로 어색한 곳이 있을 수 있습니다.

## 그대로 둔 것
- 퀵 레이스 선택 칸·그리드·순위표의 드라이버·팀 이름: 이 데이터에 한글을 넣으면 퀵 레이스 로딩이 멈춰 영문으로 둡니다.
- 효과음·엔진음, 동영상, 로고, 법적 고지 등 그림으로 된 영문 문구

## 검증 범위
PCSX2에서 언어 선택, 타이틀, 프로필 생성·메모리 카드 저장, 메인 메뉴, 옵션, 퀵 레이스 설정, 출발 그리드, 퀵 레이스 시작(로딩·그리드)·레이스 출발 해설·무전 재생, 그랑프리 위크엔드 시작·금요일 연습 주행 화면·세션 관전(관중석 구간 초당 50프레임)을 확인했습니다. 실기와 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/DUBBING.md](docs/DUBBING.md) — 해설·무전 더빙 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
