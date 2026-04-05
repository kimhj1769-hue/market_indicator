# Market Dashboard EC2 배포 가이드

## 1. AWS EC2 인스턴스 생성

### 인스턴스 사양
- **AMI**: Ubuntu 22.04 LTS
- **인스턴스 타입**: t3.micro (프리티어) 또는 t3.small (추천)
- **스토리지**: 30GB

### 보안 그룹 설정
포트 개방:
- SSH: 22번 (관리자 IP만)
- HTTP: 80번 (전체)
- HTTPS: 443번 (전체)
- Streamlit: 8501번 (전체)

---

## 2. 로컬에서 Git 설정

```bash
# GitHub 저장소 만들기 (또는 기존 저장소 사용)
cd C:\Users\Kim.HJ\Desktop\market-indicator
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/market_indicator.git
git push -u origin main
```

---

## 3. EC2 인스턴스에 접속 및 배포

### SSH 접속
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 배포 스크립트 실행
```bash
# 코드 클론
cd ~
git clone https://github.com/YOUR_USERNAME/market_indicator.git
cd market-indicator

# 배포 스크립트 실행 권한 설정
chmod +x deploy.sh

# 배포 시작
./deploy.sh
```

**주의**: `deploy.sh`에서 `<YOUR_REPO_URL>`을 자신의 GitHub 저장소 URL로 변경하세요.

---

## 4. 수동 배포 (스크립트 없을 때)

```bash
# 1. Python 설치
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip git

# 2. 앱 디렉토리 생성
mkdir -p ~/apps/market-indicator
cd ~/apps/market-indicator

# 3. 코드 클론 (또는 pull)
git clone <YOUR_REPO_URL> .

# 4. 가상환경 설정
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. 방화벽 설정
sudo ufw allow 8501/tcp

# 6. 앱 실행 (테스트)
streamlit run Home.py --server.port 8501 --server.address 0.0.0.0
```

---

## 5. 백그라운드 실행 (Systemd)

### 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/streamlit-dashboard.service
```

**다음 내용 입력:**
```ini
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

[Install]
WantedBy=multi-user.target
```

### 서비스 시작
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit-dashboard
sudo systemctl start streamlit-dashboard

# 상태 확인
sudo systemctl status streamlit-dashboard

# 로그 보기
sudo journalctl -u streamlit-dashboard -f
```

---

## 6. Nginx Reverse Proxy (선택사항)

HTTPS 및 커스텀 도메인 사용 시:

### Nginx 설치 및 설정
```bash
sudo apt-get install -y nginx

sudo nano /etc/nginx/sites-available/market-indicator
```

**설정 내용:**
```nginx
upstream streamlit {
    server localhost:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 200M;

    location / {
        proxy_pass http://streamlit;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;

        # WebSocket 설정
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Nginx 활성화
```bash
sudo ln -s /etc/nginx/sites-available/market-indicator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 7. HTTPS 설정 (Let's Encrypt)

```bash
sudo apt-get install -y certbot python3-certbot-nginx

sudo certbot --nginx -d your-domain.com
```

---

## 8. 접속 확인

브라우저에서 다음 주소로 접속:

```
http://your-ec2-public-ip:8501
```

또는 도메인 설정 후:

```
https://your-domain.com
```

---

## 9. 문제 해결

### 포트 8501 확인
```bash
sudo netstat -tlnp | grep 8501
```

### 로그 확인
```bash
sudo journalctl -u streamlit-dashboard -n 50 -f
```

### 메모리 부족 에러
```bash
# t3.micro가 부족하면 t3.small로 업그레이드
```

### 백그라운드 프로세스 수동 종료
```bash
sudo systemctl stop streamlit-dashboard
```

---

## 10. 코드 업데이트

```bash
cd ~/apps/market-indicator
git pull origin main
sudo systemctl restart streamlit-dashboard
```

---

## 핵심 포인트

✅ **자동 재시작**: Systemd로 앱이 자동 실행 및 재시작
✅ **항상 켜짐**: EC2 실행 중 24/7 접속 가능
✅ **로그 추적**: `journalctl`로 실시간 모니터링
✅ **쉬운 업데이트**: `git pull` 후 서비스 재시작

