# 매뉴얼 실제렌더검수
root / RUNNING. Browser API를통한실제렌더,단순정적파일검사와구분.
- local127.0.0.1:8088 Python정적서버. 연결은로컬이며외부CDN/스크립트에의존하지않음. OS네트워크전체차단검사는아직실행하지않음.
- 01 최초렌더실행설명Node22+불일치발견→본인4매뉴얼및02담당에CMD-01정합화전달. Node22.12+/npm10+,stop요청뒤프로세스종료확인후DB중지로수정·독립검토중.
- D-MAN02-01: 02의7개표wrapper에명명region/tabindex/focus표시누락발견. 작성자contract_ai수정후root재검증예정.
- 01데스크톱8/8,02데스크톱7/7,03데스크톱10/10 로컬이미지자연크기로드확인. lazy속성의초기미로드는오류로처리하지않고해당앵커방문후검사.
- 01·03모바일390×844 문서375px,표role region/tabindex0·ArrowRight scrollLeft40확인. 01→02다른매뉴얼상대링크실제이동성공.
- 캡처는execute/designReview/manuals/evidence. 실제200%는사용자나중진행응답에따라미실행,viewport변경으로대체하지않음.

## 5개 렌더 관측
- desktop1440×900: 01/02/03/04/05 문서너비1425px, 목차앵커와로컬이미지각8/7/10/10/12장전체로드확인. 상대링크01→02이동성공.
- mobile390×844: 문서너비모두375px로전체가로넘침없음. 01/03/04/05의표region너비309/scrollWidth580,키보드ArrowRight로scrollLeft40·초점확인. 02는현재폭303px에줄바꿈되어표내부넘침없음(left0/max0),명명region초점outline3px확인.
- D-MAN02-01 수정후7개명명region/tabindex0와실제focus-visible정상. 해당표폭에가로넘침이없으므로ArrowRight이동거리가0인것을실패로보지않음. 모바일문서사진7/7다시로드확인.
- 원시관측 mobile-dom.json, 각PNG는designReview/manuals/evidence. 독립시각검수contract_data에게요청.
- CMD-01 변경후04/05 최신Node22.12/npm10문구확인. 01/03최종갱신과키보드건너뛰기후속검증예정.

## 수정본 확인
- 01/03/04/05 D-MAN-H01 수정: 실제 computed rgb(225,237,239), 배경#173c48 대비9.886:1. 각 desktop1440-header-fixed.png 저장.
- 5개 manual Tab→Enter→Tab으로 main의첫서비스링크에초점이동. 02는#start,그외#content. final-dom.json.
- 5개 mobile390-table-identifier-fixed.png: 문서375px, ID code white-space:nowrap, 표초점확인. 02의303px 표도ID중간분할없음.
- README.md·docs/09-validation.md·integration-concept-03/actual-ai.json의로컬HTTP200/본문반환확인. 다만내장Browser의.md링크클릭은화면이동/다운로드이벤트가없어이브라우저의Markdown뷰어동작은확인하지못함. 파일자체는로컬편집기에서열수있음. HTML매뉴얼간상대이동은실제PASS.
- 네트워크전체차단실험은실행하지않았음. 문서와이미지는모두로컬,외부CDN/스크립트없음. 200%사용자나중진행으로NOT_RUN유지.
