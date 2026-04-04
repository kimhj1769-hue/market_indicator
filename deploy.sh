#!/bin/bash
# EC2 Docker 기반 배포 스크립트

set -e

echo "=== Market Dashboard Docker EC2 배포 시작 ==="

REPO_URL="${1:-https://github.com/YOUR_USERNAME/market-dashboard.git}"
APP_DIR="/home/ec2-user/apps/market-dashboard"

# 1. 시스템 업데이트
echo "[1] 시스템 패키지 업데이트..."
sudo yum update -y  # Amazon Linux 2 기준

# 2. Docker 설치
echo "[2] Docker 설치..."
sudo yum install -y docker git
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

echo "⚠️  Docker 그룹에 추가됨. 새 터미널에서 재로그인하거나 아래 명령 실행:"
echo "    newgrp docker"

# 3. 앱 디렉토리 설정
echo "[3] 앱 디렉토리 설정..."
mkdir -p ~/apps
cd ~/apps

if [ -d "market-dashboard" ]; then
    echo "기존 코드 업데이트..."
    cd market-dashboard
    git pull origin main
else
    echo "코드 클론..."
    git clone "$REPO_URL" market-dashboard
    cd market-dashboard
fi

# 4. Docker 이미지 빌드
echo "[4] Docker 이미지 빌드..."
docker build -t market-dashboard:latest .

# 5. 기존 컨테이너 중지 (있으면)
echo "[5] 기존 컨테이너 정리..."
docker stop market-dashboard 2>/dev/null || true
docker rm market-dashboard 2>/dev/null || true

# 6. Docker 컨테이너 실행
echo "[6] Docker 컨테이너 시작..."
docker run -d \
  --name market-dashboard \
  -p 8501:8501 \
  --restart=unless-stopped \
  -e PYTHONUNBUFFERED=1 \
  -e TZ=Asia/Seoul \
  market-dashboard:latest

# 7. Systemd 서비스 파일 생성 (컨테이너 자동 재시작)
echo "[7] Systemd 서비스 설정..."
sudo tee /etc/systemd/system/streamlit-dashboard.service > /dev/null <<EOF
[Unit]
Description=Market Dashboard Streamlit Container
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker start market-dashboard
RemainAfterExit=yes
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable streamlit-dashboard

# 8. 방화벽 설정
echo "[8] 보안 그룹 설정..."
echo "⚠️  AWS 보안 그룹에서 8501 포트 인바운드를 수동으로 열어야 합니다."
echo "    AWS 콘솔 → EC2 → 보안 그룹 → 인바운드 규칙 → 8501 추가"

# 9. 배포 완료
echo ""
echo "=== 배포 완료 ==="
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "접속 URL: http://$PUBLIC_IP:8501"
echo ""
echo "컨테이너 상태: docker ps -a | grep market-dashboard"
echo "로그 보기: docker logs -f market-dashboard"
echo "컨테이너 재시작: docker restart market-dashboard"
