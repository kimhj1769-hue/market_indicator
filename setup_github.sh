#!/bin/bash
# GitHub 저장소 생성 및 푸시 스크립트

set -e

echo "=== GitHub 저장소 설정 ==="
echo ""
echo "GitHub CLI(gh)를 사용합니다."
echo "GitHub CLI 설치: https://cli.github.com/"
echo ""

# GitHub 로그인 확인
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI가 설치되지 않았습니다."
    echo "설치: https://cli.github.com/ 또는 winget install gh"
    exit 1
fi

echo "GitHub CLI 버전:"
gh --version

echo ""
read -p "GitHub 사용자명을 입력하세요 (예: kim-hj): " USERNAME

if [ -z "$USERNAME" ]; then
    echo "❌ 사용자명이 비어있습니다."
    exit 1
fi

REPO_NAME="market-dashboard"
REPO_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo ""
echo "📝 저장소 생성 중: ${REPO_URL}"
gh repo create ${REPO_NAME} --public --source=. --remote=origin --push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ GitHub 저장소 생성 완료!"
    echo ""
    echo "저장소 URL: ${REPO_URL}"
    echo ""
    echo "다음 명령어로 EC2에서 클론할 수 있습니다:"
    echo "git clone ${REPO_URL}"
else
    echo "❌ 저장소 생성 실패"
    exit 1
fi
