# EC2 Docker 배포 상세 가이드

## 📋 전제 조건

- AWS EC2 인스턴스 (Amazon Linux 2 또는 Ubuntu)
- 인스턴스 크기: t2.micro (프리티어) 이상 권장
- 인스턴스 스토리지: 5GB 이상
- IAM 권한: EC2 인스턴스 생성/관리

---

## 🔧 Step 1: EC2 인스턴스 준비

### 1.1 인스턴스 생성
1. AWS 콘솔 → EC2 → 인스턴스 시작
2. **이미지 선택:**
   - Amazon Linux 2 (권장, 무료)
   - 또는 Ubuntu Server 22.04 LTS
3. **인스턴스 유형:** t2.micro (프리티어) 또는 t2.small
4. **스토리지:** 최소 8GB
5. **보안 그룹:**
   - SSH (22): 내 IP만 (0.0.0.0/0 권장 안 함)
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - 사용자 지정 TCP (8501): 0.0.0.0/0 (또는 특정 IP)

### 1.2 탄력적 IP 할당 (선택)
```bash
# 인스턴스 공인 IP가 변경되지 않도록
# 콘솔 → 탄력적 IP → 주소 할당 → 인스턴스 연결
```

---

## 🚀 Step 2: 배포 스크립트 실행

### 2.1 SSH로 인스턴스 접속
```bash
# 터미널/PowerShell
ssh -i /path/to/your-key.pem ec2-user@<PUBLIC_IP>
# 또는
ssh -i /path/to/your-key.pem ubuntu@<PUBLIC_IP>  # Ubuntu의 경우
```

### 2.2 배포 스크립트 다운로드 및 실행
```bash
# 옵션 1: 리포지토리에서 직접 실행
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/market-dashboard/main/deploy.sh | bash -s "https://github.com/YOUR_USERNAME/market-dashboard.git"

# 옵션 2: 수동으로 다운로드
git clone https://github.com/YOUR_USERNAME/market-dashboard.git
cd market-dashboard
chmod +x deploy.sh
./deploy.sh "https://github.com/YOUR_USERNAME/market-dashboard.git"
```

### 2.3 스크립트 완료 후
```bash
# Docker 그룹에 추가됨 — 새 터미널에서 로그인하거나
newgrp docker

# 접속 URL 확인
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "http://$PUBLIC_IP:8501"
```

---

## 🔐 Step 3: 보안 그룹 설정

AWS 콘솔에서 (스크립트에서 완료되지 않음):

1. **EC2 → 보안 그룹**
2. **인바운드 규칙 편집**
3. **규칙 추가:**
   | 프로토콜 | 포트 | 소스 | 설명 |
   |---------|------|------|------|
   | TCP | 22 | 내 IP | SSH |
   | TCP | 8501 | 0.0.0.0/0 | Streamlit (모두 허용) |
   | TCP | 8501 | xxx.xxx.xxx.xxx/32 | 특정 IP만 |

4. **저장**

---

## 🧪 Step 4: 배포 검증

### 4.1 컨테이너 상태 확인
```bash
docker ps -a | grep market-dashboard
docker logs -f market-dashboard
```

### 4.2 브라우저 접속 테스트
```
http://<PUBLIC_IP>:8501
```

예상 화면:
- 📊 Market Dashboard 헤더
- 주요 지수 카드 (BTC, NASDAQ, S&P500 등)
- Fear & Greed Index 게이지
- 차트 및 데이터

### 4.3 API 데이터 확인
1. 주요 지수 카드에 현재가가 표시되나?
2. Fear & Greed 게이지에 값이 있나?
3. 차트가 로드되나?

모두 "예"면 ✅ 배포 성공!

---

## 📊 Step 5: 모니터링

### 5.1 실시간 로그 모니터링
```bash
docker logs -f market-dashboard
# 또는
sudo journalctl -u streamlit-dashboard -f
```

### 5.2 컨테이너 헬스 확인
```bash
docker inspect market-dashboard | grep -A 10 '"Health"'
```

### 5.3 성능 모니터링
```bash
docker stats market-dashboard
```

**정상 상태:**
- STATUS: Up (with health status: healthy)
- CPU: < 20%
- 메모리: 100-300 MB

### 5.4 EC2 인스턴스 CPU/메모리 (CloudWatch)
```bash
# AWS 콘솔 → CloudWatch → 인스턴스 메트릭
# CPU: < 30%, 메모리 사용: < 70%
```

---

## 🔄 Step 6: 자동 재시작 설정

### 6.1 Systemd 서비스 확인
```bash
sudo systemctl status streamlit-dashboard
sudo systemctl enable streamlit-dashboard
```

### 6.2 EC2 인스턴스 재부팅 후 자동 시작
```bash
# 테스트: 인스턴스 재부팅
sudo reboot

# 재부팅 후 (2-3분 대기)
ssh -i /path/to/your-key.pem ec2-user@<PUBLIC_IP>
docker ps | grep market-dashboard
# 컨테이너가 자동으로 시작되어야 함
```

---

## 📝 Step 7: 로그 관리

### 7.1 Docker 로그 용량 제한 (선택)
```bash
# /etc/docker/daemon.json 수정
sudo vi /etc/docker/daemon.json
```

추가:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

재시작:
```bash
sudo systemctl restart docker
```

### 7.2 정기적 로그 확인
```bash
# 주간 1회 확인
docker logs market-dashboard | tail -50
```

---

## ❌ 문제 해결

### 7.1 컨테이너가 시작되지 않음
```bash
# 1. 로그 확인
docker logs market-dashboard

# 2. 이미지 재빌드
docker build -t market-dashboard:latest .

# 3. 컨테이너 제거 후 재시작
docker stop market-dashboard
docker rm market-dashboard
docker run -d -p 8501:8501 --restart=unless-stopped \
  -e PYTHONUNBUFFERED=1 market-dashboard:latest
```

### 7.2 API 데이터가 로드되지 않음
```bash
# 1. 인스턴스에서 외부 네트워크 접속 테스트
curl -I https://api.alternative.me/fng/?limit=1

# 2. 보안 그룹 확인 (아웃바운드 HTTPS 허용)
# AWS 콘솔 → 보안 그룹 → 아웃바운드 규칙 (기본값: 모두 허용)

# 3. DNS 확인
nslookup api.alternative.me
```

### 7.3 높은 CPU 사용률
```bash
# 1. 스트림릿 프로세스 확인
docker top market-dashboard

# 2. Python 메모리 누수 확인
docker stats market-dashboard

# 3. 컨테이너 재시작
docker restart market-dashboard
```

### 7.4 Streamlit이 계속 재시작됨
```bash
# 세션 상태 파일 삭제
docker exec market-dashboard rm -rf /tmp/*streamlit*
docker restart market-dashboard
```

---

## 💰 비용 관리

### 8.1 EC2 비용 최적화
- **t2.micro:** 프리티어 (12개월), 이후 월 $7-9
- **t2.nano:** 더 저렴 (월 $3-4), 트래픽 낮으면 충분
- **t3.micro:** 더 효율적 (월 $5-6)

### 8.2 탄력적 IP 비용
- 미사용 탄력적 IP: 월 $0.32/개
- 연결된 탄력적 IP: 무료
- **권장:** 필요시에만 할당, 사용하지 않으면 해제

### 8.3 EBS 비용
- gp3 (기본): 월 $0.096/GB (8GB = 월 $0.77)

---

## 🛠️ Step 8: 코드 업데이트 배포

### 8.1 새 코드 푸시 및 자동 배포
```bash
# 로컬에서
git add .
git commit -m "feature: xxx"
git push origin main

# EC2에서
cd ~/apps/market-dashboard
git pull origin main
docker build -t market-dashboard:latest .
docker restart market-dashboard
```

### 8.2 Docker Hub를 통한 자동 배포 (선택)
```bash
# 로컬에서
docker tag market-dashboard:latest YOUR_USERNAME/market-dashboard:v1.0
docker push YOUR_USERNAME/market-dashboard:v1.0

# EC2에서
docker pull YOUR_USERNAME/market-dashboard:v1.0
docker run -d -p 8501:8501 --name market-dashboard \
  --restart=unless-stopped YOUR_USERNAME/market-dashboard:v1.0
```

---

## 📅 정기 유지보수

### 9.1 주간 체크리스트
- [ ] 대시보드 접속 확인
- [ ] API 데이터 로드 상태 확인
- [ ] 에러 로그 확인 (`docker logs market-dashboard`)
- [ ] 컨테이너 상태 확인 (`docker ps`)

### 9.2 월간 체크리스트
- [ ] 패키지 업데이트 확인
- [ ] 보안 그룹 설정 검토
- [ ] 이미지 재빌드 (최신 패키지)
- [ ] 비용 확인 (AWS 청구)

### 9.3 반기 체크리스트
- [ ] Python 버전 업데이트 (3.11.x → 3.12.x)
- [ ] 의존성 보안 감사
- [ ] 스트림릿 메이저 업데이트 검토

---

## ✅ 최종 체크리스트

배포 완료 후 확인:
- [ ] EC2 인스턴스 실행 중
- [ ] 탄력적 IP 할당 (선택)
- [ ] 보안 그룹 설정 (SSH, HTTP/HTTPS, 8501)
- [ ] Streamlit 컨테이너 실행 중
- [ ] http://<PUBLIC_IP>:8501 접속 가능
- [ ] 차트/데이터 정상 로드
- [ ] Systemd 서비스 자동 시작 설정
- [ ] 로그 모니터링 확인
- [ ] 30분 이상 연속 실행 테스트

---

## 📞 추가 도움말

- Streamlit 공식 문서: https://docs.streamlit.io
- AWS EC2 문서: https://docs.aws.amazon.com/ec2
- Docker 문서: https://docs.docker.com

---

**배포 완료!** 🎉 문제가 발생하면 로그를 확인하고 문제 해결 섹션을 참고하세요.
