# AWS Cost Dashboard Plugin

AWS 멀티 계정 비용을 조회하여 HTML 대시보드로 시각화하는 Claude Code 플러그인.

## 기능

- 여러 AWS 계정 비용 조회 (USD → KRW 자동 환산)
- HTML 대시보드 생성 + 브라우저 자동 오픈
- 세션 종료 시 PNG 자동 저장 (선택)

## 설치

```bash
npx skills add github:<your-username>/aws-cost-dashboard
```

## 설정

`~/.claude/settings.json`의 `env` 섹션에 아래 항목을 추가하세요:

```json
{
  "env": {
    "AWS_COST_PROFILES": "profile1,profile2,profile3",
    "AWS_COST_SAVE_DIR": "/path/to/save/screenshots"
  }
}
```

| 환경변수 | 필수 | 설명 |
|----------|------|------|
| `AWS_COST_PROFILES` | 필수 | 조회할 AWS 프로파일 목록 (쉼표 구분). `~/.aws/credentials`의 `[프로파일명]`과 일치해야 함 |
| `AWS_COST_SAVE_DIR` | 선택 | 세션 종료 시 대시보드 PNG를 저장할 폴더. 미설정 시 저장하지 않음 |

## 사용법

```
/aws-cost-dashboard          # 어제 기준
/aws-cost-dashboard 03.05    # 특정 날짜 기준
```

## 사전 요구사항

- Python 3 + `boto3`, `requests` 설치 (`pip install boto3 requests`)
- `~/.aws/credentials`에 프로파일 설정
- 각 계정의 IAM에 `ce:GetCostAndUsage` 권한 필요
- PNG 저장을 위해 Google Chrome 설치 필요
