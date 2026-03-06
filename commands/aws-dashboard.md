---
description: "AWS 비용 대시보드 생성 (전체 리전, 0원 제외)"
argument-hint: "[날짜 MM.DD] (미입력시 오늘 기준)"
---

# AWS Dashboard (전체 리전)

이 커맨드가 호출되면 아래 절차를 따른다.

## 날짜 결정

1. 사용자가 날짜를 명시한 경우 (예: "03.01", "3월 1일", "2026-03-01") → 해당 날짜 사용
2. 날짜를 명시하지 않은 경우 → 기본값(오늘, today)으로 바로 실행

## 실행 명령

날짜를 명시한 경우:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/aws_dashboard.py --date YYYY-MM-DD
```

날짜 미지정 (오늘 기준):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/aws_dashboard.py
```

## 출력

- HTML 파일 `/tmp/aws_dashboard_all.html` 생성 후 브라우저 자동 오픈
- 테이블: 계정명 | D-2 | D-1 | 기준일★ | 모든 리전 (기준일)
- 기준일 컬럼 파란색 강조
- 비용이 발생한 리전만 표시 (KRW 0원 리전 제외)

## aws-cost-dashboard와의 차이점

| 항목 | /aws-cost-dashboard | /aws-dashboard |
|------|---------------------|----------------|
| 기본 기준일 | 어제 | 오늘 |
| 리전 표시 | 상위 3개 | 비용 발생 전체 리전 |
| 0원 리전 | 포함 | 제외 |

## 오류 대응

| 오류 | 원인 | 조치 |
|------|------|------|
| NoCredentialsError | ~/.aws/credentials에 프로필 없음 | 프로필명 확인 |
| AccessDenied | Cost Explorer 권한 없음 | IAM 정책에 ce:GetCostAndUsage 추가 필요 |
| 당일 데이터 0원 | Cost Explorer 집계 지연 (최대 24시간) | 정상 현상, 어제 날짜로 확인 권장 |
