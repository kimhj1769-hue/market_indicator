# Market Dashboard EC2 배포 계획

## 목표
Streamlit 금융 대시보드를 AWS EC2에 배포하여 24/7 온라인 접속 가능하게 구성.

---

## Phase 1: 준비 (완료)
- [x] 배포 스크립트 생성 (`deploy.sh`)
- [x] Streamlit 설정 최적화 (`.streamlit/config.toml`)
- [x] 배포 가이드 작성 (`EC2_DEPLOY.md`, `QUICK_START.md`)
- [x] 프로젝트 문서화 (`CLAUDE.md`)

---

## Phase 2: AWS 설정 (TODO)

### 2.1 EC2 인스턴스 생성
- [ ] AWS 계정 생성 및 로그인
- [ ] EC2 대시보드에서 "인스턴스 시작"
- [ ] 인스턴스 사양:
  - AMI: Ubuntu 22.04 LTS
  - 타입: t3.micro (프리티어) 또는 t3.small
  - 스토리지: 30GB
- [ ] 키 페어 다운로드 (`.pem` 파일)
- [ ] 인스턴스 실행 및 IP 주소 확인

### 2.2 보안 그룹 설정
- [ ] SSH (22번): 관리자 IP만 허용
- [ ] HTTP (80번): 모든 IP 허용
- [ ] HTTPS (443번): 모든 IP 허용
- [ ] Streamlit (8501번): 모든 IP 허용

---

## Phase 3: GitHub 준비 (TODO)

### 3.1 저장소 생성
- [ ] GitHub 계정으로 새 저장소 생성 (`market-dashboard`)
- [ ] 로컬에서 커밋 및 푸시:
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  git remote add origin https://github.com/USERNAME/market-dashboard.git
  git push -u origin main
  ```

### 3.2 deploy.sh 수정
- [ ] `deploy.sh`에서 `<YOUR_REPO_URL>` 수정
- [ ] 예: `https://github.com/USERNAME/market-dashboard.git`

---

## Phase 4: EC2 배포 (TODO)

### 4.1 SSH 접속
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 4.2 배포 실행
```bash
# 코드 클론
git clone https://github.com/USERNAME/market-dashboard.git
cd market-dashboard

# 배포 스크립트 실행
chmod +x deploy.sh
./deploy.sh
```

### 4.3 배포 완료 확인
- [ ] 서비스 상태 확인: `sudo systemctl status streamlit-dashboard`
- [ ] 로그 확인: `sudo journalctl -u streamlit-dashboard -f`
- [ ] 브라우저에서 `http://YOUR_EC2_IP:8501` 접속

---

## Phase 5: 추가 설정 (선택사항)

### 5.1 도메인 연결 (DNS)
- [ ] Route 53 또는 외부 DNS에서 EC2 IP로 A 레코드 지정
- [ ] 도메인: `your-domain.com` → EC2 IP

### 5.2 Nginx Reverse Proxy (HTTPS 필요 시)
- [ ] Nginx 설치 및 설정
- [ ] EC2_DEPLOY.md의 "Nginx Reverse Proxy" 섹션 참고
- [ ] SSL 인증서 자동 갱신 설정

### 5.3 Let's Encrypt SSL 인증서
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 5.4 모니터링 (선택)
- [ ] CloudWatch 알람 설정 (CPU, 메모리)
- [ ] EC2 인스턴스 메트릭 모니터링

---

## Phase 6: 유지보수

### 정기 작업
- [ ] 주 1회: 로그 확인 및 에러 확인
- [ ] 월 1회: 시스템 업데이트 (`sudo apt update && sudo apt upgrade`)
- [ ] 필요 시: 코드 수정 후 배포

### 코드 업데이트 프로세스
```bash
# 로컬에서 수정
git add .
git commit -m "Fix: ..."
git push origin main

# EC2에서 적용
cd ~/apps/market-dashboard
git pull origin main
sudo systemctl restart streamlit-dashboard
```

---

## 예상 비용 (AWS)

| 항목 | 금액 |
|------|------|
| EC2 t3.micro (750시간/월) | 무료 (프리티어) |
| EC2 t3.small (추가) | $0.0208/시간 (~$15/월) |
| 트래픽 (첫 1GB) | 무료 |
| 데이터 전송 (초과) | $0.12/GB |
| 탄력적 IP | 무료 (사용 중) |

---

## 트러블슈팅

### 포트 8501 연결 불가
```bash
# 방화벽 확인
sudo ufw status
# 포트 오픈
sudo ufw allow 8501/tcp
# 보안 그룹 설정 (AWS 콘솔)
```

### 서비스 실행 안됨
```bash
# 로그 확인
sudo journalctl -u streamlit-dashboard -f
# 수동 실행 테스트
cd ~/apps/market-dashboard
source venv/bin/activate
streamlit run Home.py
```

### 메모리 부족
```bash
# 인스턴스 타입 업그레이드
# AWS 콘솔 → 인스턴스 중지 → 인스턴스 타입 변경 → 재시작
```

### API 오류
- yfinance 또는 외부 API 문제 확인
- `utils.py`의 예외 처리 추가
- 캐시 재설정: Home.py의 `clear_cache()` 호출

---

## 완료 후 체크리스트

- [ ] EC2 인스턴스 실행 중
- [ ] Systemd 서비스 자동 시작 설정됨
- [ ] 브라우저에서 대시보드 접속 가능
- [ ] 로그에 에러 없음
- [ ] GitHub에 코드 백업됨
- [ ] 도메인 연결됨 (선택)
- [ ] HTTPS 설정됨 (선택)

---

## 예상 소요 시간

| Phase | 시간 |
|-------|------|
| 1. 준비 | 1시간 (완료) |
| 2. AWS 설정 | 30분 |
| 3. GitHub 준비 | 15분 |
| 4. EC2 배포 | 10분 |
| 5. 추가 설정 | 1시간 (선택) |
| **총계** | **2.5시간** |

