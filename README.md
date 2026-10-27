# 세계 디지털헬스케어 현황판

(주)사이넥스 헬스케어혁신연구소의 글로벌 디지털헬스케어 동향 모니터링 화면.

- 주요 17개국과 EU의 뉴스(최근 14일)와 전시·행사(향후 90일)를 세계지도 위에 보여준다.
- 카테고리: 기업·서비스 / 정책·규제 / 투자·M&A / 전시·행사
- 중요도: 즉시 확인 / 주의 / 참고
- 지도의 낮·밤은 조회하는 시각의 실제 해 위치를 따른다.
- 데이터는 `data/news.json` 하나이며, 매일 07:00 KST 예약 작업이 [UPDATE_GUIDE.md](UPDATE_GUIDE.md)대로 갱신한다.

## 구성
- `index.html` — 화면 전체(D3, TopoJSON은 cdnjs에서 불러옴)
- `data/news.json` — 뉴스·행사·오늘의 브리핑
- `data/countries-110m.json` — Natural Earth 1:110m 국경 (world-atlas 2.0.2)
- `fonts/PretendardVariable.woff2` — Pretendard 1.3.9 (SIL OFL)
- `scripts/merge_news.py` — 새 항목 병합·정리
