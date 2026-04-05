#!/bin/bash
# EC2 Systemd 기반 배포 스크립트 (market-indicator)

set -e

echo "=== Market Indicator EC2 배포 시작 ==="

REPO_URL="${1:-https://github.com/kimhj1769-hue/market_indicator.git}"
APP_DIR="/home/ubuntu/apps/market-indicator"

# 1. 시스템 업데이트
echo "[1] 시스템 패키지 업데이트..."
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip git

# 2. 앱 디렉토리 설정
echo "[2] 앱 디렉토리 설정..."
mkdir -p ~/apps
cd ~/apps

if [ -d "market-indicator" ]; then
    echo "기존 코드 업데이트..."
    cd market-indicator
    git pull origin main
else
    echo "코드 클론..."
    git clone "$REPO_URL" market-indicator
    cd market-indicator
fi

# 3. 가상환경 설정
echo "[3] Python 가상환경 설정..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Systemd 서비스 파일 생성
echo "[4] Systemd 서비스 파일 생성..."
sudo tee /etc/systemd/system/streamlit-dashboard.service > /dev/null <<'EOF'
[Unit]
Description=Streamlit Market Indicator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/apps/market-indicator
ExecStart=/home/ubuntu/apps/market-indicator/venv/bin/streamlit run Home.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

# 5. 서비스 시작
echo "[5] 서비스 시작..."
sudo systemctl daemon-reload
sudo systemctl enable streamlit-dashboard
sudo systemctl start streamlit-dashboard

# 6. 포트 방화벽 설정
echo "[6] 포트 방화벽 설정..."
sudo ufw allow 8501/tcp 2>/dev/null || echo "UFW 설정 건너뜀"

# 7. 배포 완료
echo ""
echo "=== 배포 완료 ==="
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "✓ 접속 URL: http://$PUBLIC_IP:8501"
echo ""
echo "서비스 상태: sudo systemctl status streamlit-dashboard"
echo "실시간 로그: sudo journalctl -u streamlit-dashboard -f"
echo "서비스 재시작: sudo systemctl restart streamlit-dashboard"
