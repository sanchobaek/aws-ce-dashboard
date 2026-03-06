# AWS Dashboard - 당일 전체 리전 비용 표시

이 디렉토리의 `aws_dashboard.py`는 당일(오늘) AWS 비용을 **모든 리전** 단위로 조회하여 HTML 대시보드로 출력한다.

## 핵심 동작 규칙

- **기준일 기본값: 오늘 (today)**
  `--date` 인자가 없으면 `date.today()`를 기준일로 사용한다. (어제가 아님)

- **모든 리전 표시**
  비용이 발생한 리전을 전부 표시한다. 상위 N개로 제한하지 않는다.

- **리전 정렬 기준**
  비용 내림차순 정렬. 동일 비용이면 리전 코드 알파벳 순.

## 프로필 목록

```
account 1
account 2
account 3
```

## 출력 파일

- HTML: `/tmp/aws_dashboard_all.html`
- 생성 후 `open` 명령으로 브라우저 자동 오픈

## 스크립트 수정 시 주의사항

- `get_daily_by_region()` 함수에서 리전 필터링 로직(`[:3]` 등) 추가 금지
- 기준일 기본값을 `timedelta(days=1)`(어제)로 변경 금지
- 환율 API 실패 시 기본값 1,450 KRW/USD 유지
