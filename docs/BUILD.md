# 직접 빌드하기

번역 대본·합성 음성은 저장소에 없으므로, 아래는 같은 과정을 처음부터 다시 하는 순서입니다.

## 준비
- Python 3.12 이상, `pip install -r requirements.txt`
- 작업 폴더에 원본 ISO `Formula One 06 (Europe, Australia) (En,Fr,De,Es,It,Pt,Fi).iso`
- 작업 폴더에 `NanumSquareNeo-bRg.ttf`, `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`, `tools/fonts/` 에 `Galmuri9.ttf`, `Galmuri11.ttf`, `Galmuri11-Bold.ttf`
- Supertonic 3 모델: `huggingface-cli download Supertone/supertonic-3`

## 순서
1. 화면 텍스트: `python tools/export_text.py` → `translation/en.tsv` 를 번역해 `translation/ko/ko_*.tsv`(`번호<TAB>한국어`)로 저장, `python tools/check_tr.py` 로 변수·줄바꿈 검사.
2. 음성: `python tools/voice.py extract` → `python tools/voice.py asr ts` / `asr com` → `dub/ko/<묶음>_*.tsv` 번역 → `python tools/dub_tts.py ts` / `com`.
3. 빌드: `python tools/build.py` — 텍스트·글꼴·WAD를 만들고 한글 ISO를 갱신한 뒤 더빙을 제자리에 넣습니다.
4. 차분: `xdelta3 -e -s "원본.iso" "Formula One 06 (Europe, Australia) (Korean).iso" 패치.xdelta`

`tools/emu.py` 는 PCSX2를 최소화·비활성 창으로 띄워 창 메시지로 키를 보내고 PINE 상태 저장으로 화면을 얻는 테스트 도구입니다.
