#!/usr/bin/env python3
"""AWS Dashboard - 당일 비용 전체 리전 HTML 대시보드 생성"""

import os
import boto3
import requests
import argparse
import subprocess
from datetime import date, timedelta, datetime
from botocore.exceptions import ClientError, NoCredentialsError

_profiles_env = os.environ.get("AWS_COST_PROFILES", "")
if not _profiles_env:
    raise SystemExit("환경변수 AWS_COST_PROFILES가 설정되지 않았습니다.\n예: export AWS_COST_PROFILES=profile1,profile2,profile3")
PROFILES = [p.strip() for p in _profiles_env.split(",") if p.strip()]

REGION_KR = {
    "ap-northeast-2": "서울",
    "ap-northeast-3": "오사카",
    "ap-northeast-1": "도쿄",
    "ap-south-1": "뭄바이",
    "us-east-1": "버지니아",
    "us-east-2": "오하이오",
    "us-west-1": "캘리포니아",
    "us-west-2": "오레곤",
    "eu-west-1": "아일랜드",
    "eu-central-1": "프랑크푸르트",
    "ap-southeast-1": "싱가포르",
    "ap-southeast-2": "시드니",
    "ca-central-1": "캐나다",
    "eu-north-1": "스톡홀름",
    "eu-west-2": "런던",
    "eu-west-3": "파리",
    "sa-east-1": "상파울루",
    "NoRegion": "글로벌",
}


def get_exchange_rate():
    try:
        resp = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": "USD", "to": "KRW"},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()["rates"]["KRW"]
    except Exception:
        return 1450.0


def to_krw(usd, rate):
    return int(usd * rate)


def get_daily_total(ce, d_start, d_end):
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": d_start, "End": d_end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
    )
    results = resp["ResultsByTime"]
    if not results:
        return 0.0
    return float(results[0]["Total"]["UnblendedCost"]["Amount"])


def get_daily_by_region(ce, d_start, d_end):
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": d_start, "End": d_end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}],
    )
    results = resp["ResultsByTime"]
    if not results:
        return {}
    region_costs = {}
    for group in results[0].get("Groups", []):
        region_code = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if amount > 0:
            region_costs[region_code] = amount
    return region_costs


def fetch_profile_data(profile, rate, days):
    result = {"profile": profile, "days": [], "error": None}
    try:
        session = boto3.Session(profile_name=profile)
        ce = session.client("ce", region_name="us-east-1")
        for day in days:
            d_start = day.strftime("%Y-%m-%d")
            d_end = (day + timedelta(days=1)).strftime("%Y-%m-%d")
            total_krw = to_krw(get_daily_total(ce, d_start, d_end), rate)
            region_costs = get_daily_by_region(ce, d_start, d_end)
            # 비용 발생 리전만 표시 (KRW 0원 제외, 상위 N개 제한 없음)
            all_regions = sorted(
                [(REGION_KR.get(k, k), to_krw(v, rate)) for k, v in region_costs.items() if to_krw(v, rate) > 0],
                key=lambda x: -x[1],
            )
            result["days"].append({
                "date": day,
                "total_krw": total_krw,
                "all_regions": all_regions,
            })
    except NoCredentialsError:
        result["error"] = "자격증명 없음"
    except ClientError as e:
        result["error"] = e.response["Error"]["Code"]
    except Exception as e:
        result["error"] = str(e)
    return result


def generate_html(data_rows, days, target_date, rate):
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]

    date_headers = ""
    for day in days:
        label = f"{day.month}/{day.day} ({weekdays[day.weekday()]})"
        is_target = day == target_date
        style = ' class="target-col"' if is_target else ""
        marker = " ★" if is_target else ""
        date_headers += f"<th{style}>{label}{marker}</th>\n"

    rows_html = ""
    totals = [0] * len(days)

    for row in data_rows:
        short_name = row["profile"].replace("sancho-", "")
        if row["error"]:
            cells = f'<td colspan="{len(days)}" class="error">{row["error"]}</td>'
            region_cell = "-"
        else:
            cells = ""
            for i, day_data in enumerate(row["days"]):
                totals[i] += day_data["total_krw"]
                cls = ' class="target-col"' if day_data["date"] == target_date else ""
                cells += f'<td{cls}>{day_data["total_krw"]:,}원</td>\n'

            # 기준일의 모든 리전 표시
            all_regions = row["days"][-1]["all_regions"]
            if all_regions:
                region_lines = "".join(
                    f'<div class="region-item">'
                    f'<span class="region-name">{r}</span>'
                    f'<span class="region-cost">{v:,}원</span>'
                    f'</div>'
                    for r, v in all_regions
                )
                region_cell = region_lines
            else:
                region_cell = "-"

        rows_html += f"""<tr>
            <td class="account-name">{short_name}</td>
            {cells}
            <td class="region-cell">{region_cell}</td>
        </tr>"""

    total_cells = ""
    for i, total in enumerate(totals):
        cls = ' class="target-col"' if days[i] == target_date else ""
        total_cells += f"<td{cls}>{total:,}원</td>\n"

    rows_html += f"""<tr class="total-row">
        <td>합계</td>
        {total_cells}
        <td>-</td>
    </tr>"""

    generated_at = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AWS 비용 대시보드 (전체 리전)</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
    background: #f0f4f8;
    color: #2d3748;
    padding: 48px 32px;
  }}
  .container {{
    max-width: 1100px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    padding: 48px;
  }}
  h1 {{ font-size: 22px; font-weight: 700; margin-bottom: 6px; }}
  .meta {{
    color: #718096;
    font-size: 13px;
    margin-bottom: 36px;
    display: flex;
    gap: 16px;
  }}
  .meta span {{ display: flex; align-items: center; gap: 4px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{
    text-align: left;
    padding: 14px 18px;
    border-bottom: 2px solid #2d3748;
    font-size: 13px;
    color: #4a5568;
    white-space: nowrap;
  }}
  td {{
    padding: 14px 18px;
    border-bottom: 1px solid #edf2f7;
    font-size: 14px;
    vertical-align: top;
  }}
  tr:not(.total-row):hover td {{ background: #f7fafc; }}
  .account-name {{ font-weight: 700; white-space: nowrap; }}
  .target-col {{ background: #ebf4ff; font-weight: 700; }}
  th.target-col {{ background: #ebf4ff; color: #2b6cb0; }}
  .total-row td {{
    font-weight: 700;
    background: #f7fafc;
    border-top: 2px solid #2d3748;
    border-bottom: none;
  }}
  .total-row td.target-col {{ background: #dbeafe; }}
  .region-cell {{ min-width: 220px; }}
  .region-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding: 2px 0;
    font-size: 13px;
    line-height: 1.7;
  }}
  .region-name {{ color: #4a5568; }}
  .region-cost {{ color: #2d3748; font-weight: 500; white-space: nowrap; }}
  .error {{ color: #e53e3e; font-size: 13px; }}
  .badge {{
    display: inline-block;
    background: #ebf4ff;
    color: #2b6cb0;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 99px;
    margin-left: 8px;
    vertical-align: middle;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>AWS 비용 대시보드 <span class="badge">전체 리전</span></h1>
  <div class="meta">
    <span>기준일: {target_date.strftime('%Y년 %m월 %d일')} ★</span>
    <span>환율: 1 USD = {rate:,.0f} KRW</span>
    <span>생성: {generated_at}</span>
  </div>
  <table>
    <thead>
      <tr>
        <th>계정명</th>
        {date_headers}
        <th>모든 리전 (기준일)</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="기준 날짜 YYYY-MM-DD (기본값: 오늘)")
    args = parser.parse_args()

    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        target_date = date.today()  # 기본값: 오늘 (당일)

    print(f"AWS 대시보드 생성 중... (기준일: {target_date.strftime('%m.%d')} ★, 전체 리전)")
    rate = get_exchange_rate()
    print(f"환율: 1 USD = {rate:,.0f} KRW")

    days = [target_date - timedelta(days=i) for i in range(2, -1, -1)]

    data_rows = []
    for profile in PROFILES:
        print(f"  {profile} 조회 중...")
        data_rows.append(fetch_profile_data(profile, rate, days))

    html = generate_html(data_rows, days, target_date, rate)

    output_path = "/tmp/aws_dashboard_all.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n대시보드 생성 완료 → {output_path}")
    subprocess.run(["open", output_path])


if __name__ == "__main__":
    main()
