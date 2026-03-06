#!/bin/bash
# 세션 종료 시 대시보드 PNG를 저장
# AWS_COST_SAVE_DIR 환경변수로 저장 경로 지정 (미설정 시 저장 안 함)
SRC="/tmp/aws_cost_dashboard.png"

if [ -z "$AWS_COST_SAVE_DIR" ]; then
  exit 0
fi

if [ -f "$SRC" ]; then
  mkdir -p "$AWS_COST_SAVE_DIR"
  cp "$SRC" "$AWS_COST_SAVE_DIR/aws_dashboard_$(date +%Y%m%d_%H%M%S).png"
fi
