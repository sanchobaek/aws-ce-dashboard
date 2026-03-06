---
description: "AWS 비용 대시보드 생성 및 브라우저로 오픈"
argument-hint: "[날짜 MM.DD] (미입력시 어제 기준)"
---

# AWS Cost Dashboard

이 커맨드가 호출되면 아래 절차를 따른다.

## 날짜 결정

1. 사용자가 날짜를 명시한 경우 (예: "03.01", "3월 1일", "2026-03-01") → 해당 날짜 사용
2. 날짜를 명시하지 않은 경우 → 기본값(어제)으로 바로 실행

## 실행 명령

날짜를 명시한 경우:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/aws_cost_dashboard.py --date YYYY-MM-DD
```

날짜 미지정 (어제 기준):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/aws_cost_dashboard.py
```

## 출력

- HTML 파일 `/tmp/aws_cost_dashboard.html` 생성 후 브라우저 자동 오픈
- 테이블: 계정명 | D-2 | D-1 | 기준일★ | 주요 리전
- 기준일 컬럼 파란색 강조

## 환경변수 설정 (settings.json → env)

| 변수 | 설명 | 예시 |
|------|------|------|
| `AWS_COST_PROFILES` | 조회할 AWS 프로파일 목록 (쉼표 구분) | `"profile1,profile2"` |
| `AWS_COST_SAVE_DIR` | 세션 종료 시 PNG 저장 경로 (미설정 시 저장 안 함) | `"/Users/me/aws_billing"` |

## 오류 대응

| 오류 | 원인 | 조치 |
|------|------|------|
| NoCredentialsError | ~/.aws/credentials에 프로필 없음 | 프로필명 확인 |
| AccessDenied | Cost Explorer 권한 없음 | IAM 정책에 ce:GetCostAndUsage 추가 필요 |
