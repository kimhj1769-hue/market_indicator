# 🚀 Market Dashboard → EC2 Docker 배포 — 최종 요약

## ✅ 완료된 작업

### Phase 1: 로컬 API 문제 해결
- ✅ API 데이터 로딩 테스트 완료 (Yahoo Finance, alternative.me 정상 작동)
- ✅ Market data (BTC, NASDAQ, S&P500, VIX, DOW) 실시간 수집 확인
- ✅ Fear & Greed Index 30일 히스토리 수집 확인

### Phase 2: Docker 이미지 생성
- ✅ **Dockerfile** 생성 (Python 3.11-slim, Streamlit 서버 설정)
- ✅ **.dockerignore** 생성 (불필요 파일 제외)
- ✅ **docker-compose.yml** 생성 (로컬/EC2 공용, 헬스체크 포함)
- ✅ **requirements.txt** 버전 고정 (재현성 보장)

### Phase 3: EC2 배포 구성
- ✅ **deploy.sh** 업데이트 (Docker 기반 배포 스크립트)
- ✅ **LOCAL_DEV.md** 작성 (로컬 개발 및 Docker 테스트 가이드)
- ✅ **EC2_DEPLOY_GUIDE.md** 작성 (상세 EC2 배포 가이드)

---

## 📁 생성된 파일 목록

| 파일 | 목적 | 상태 |
|------|------|------|
| `Dockerfile` | Docker 이미지 빌드 정의 | ✅ |
| `.dockerignore` | Docker 빌드에서 제외할 파일 | ✅ |
| `docker-compose.yml` | 로컬/EC2 배포 오케스트레이션 | ✅ |
| `requirements.txt` | Python 의존성 (버전 고정) | ✅ |
| `deploy.sh` | EC2 자동 배포 스크립트 | ✅ |
| `LOCAL_DEV.md` | 로컬 개발 가이드 | ✅ |
| `EC2_DEPLOY_GUIDE.md` | EC2 배포 상세 가이드 | ✅ |
| `DEPLOYMENT_SUMMARY.md` | 이 파일 | ✅ |

---

## 🎯 사용자 액션 플랜

### Step 1: 로컬 테스트 (15분)
```bash
cd market-dashboard

# venv 설정 (이미 있으면 스킵)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Streamlit 실행
streamlit run Home.py
# http://localhost:8501 접속 → 차트 확인
```

### Step 2: Docker 로컬 테스트 (10분)
```bash
cd market-dashboard

# Docker 이미지 빌드
docker build -t market-dashboard:latest .

# docker-compose로 실행 (권장)
docker-compose up --build
# http://localhost:8501 접속 → 차트 확인

# 중지
docker-compose down
```

### Step 3: EC2 배포 (20분)
#### 3.1 EC2 인스턴스 준비 (AWS 콘솔)
- **이미지:** Amazon Linux 2 (권장) 또는 Ubuntu
- **유형:** t2.micro (프리티어) 이상
- **스토리지:** 8GB 이상
- **보안 그룹:**
  - SSH (22): 내 IP
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
  - 사용자 정의 TCP (8501): 0.0.0.0/0

#### 3.2 GitHub 리포지토리 설정 (선택)
```bash
# 1. GitHub에 푸시 (로컬)
git add .
git commit -m "feat: Docker 배포 설정 추가"
git push origin main

# 2. GitHub 리포지토리 URL 복사
# https://github.com/YOUR_USERNAME/market-dashboard.git
```

#### 3.3 배포 스크립트 실행 (EC2)
```bash
# SSH 로그인
ssh -i /path/to/your-key.pem ec2-user@<PUBLIC_IP>

# 또는 AWS Systems Manager Session Manager 사용

# 배포 스크립트 실행
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/market-dashboard/main/deploy.sh | \
  bash -s "https://github.com/YOUR_USERNAME/market-dashboard.git"

# 또는 수동 실행
git clone https://github.com/YOUR_USERNAME/market-dashboard.git
cd market-dashboard
chmod +x deploy.sh
./deploy.sh
```

#### 3.4 보안 그룹 설정 (AWS 콘솔)
- 인바운드 규칙 추가:
  - TCP 8501, 소스: 0.0.0.0/0 (모두 허용) 또는 특정 IP

#### 3.5 접속 테스트
```bash
# 브라우저에서
http://<EC2_PUBLIC_IP>:8501

# 또는 터미널에서
curl -I http://<EC2_PUBLIC_IP>:8501
```

---

## 🔍 검증 체크리스트

### 로컬 테스트
- [ ] `streamlit run Home.py` 실행 OK
- [ ] http://localhost:8501 접속 OK
- [ ] 주요 지수 카드 데이터 표시 OK
- [ ] Fear & Greed 게이지 표시 OK
- [ ] 1개월 차트 로드 OK

### Docker 로컬 테스트
- [ ] `docker build` 성공 (이미지 크기 ~400-500MB)
- [ ] `docker-compose up` 실행 OK
- [ ] http://localhost:8501 접속 OK
- [ ] 컨테이너 정상 실행 (`docker ps`)
- [ ] `docker-compose down` 정상 중지

### EC2 배포 테스트
- [ ] SSH 로그인 성공
- [ ] 배포 스크립트 실행 완료 (3-5분)
- [ ] Docker 컨테이너 실행 중 (`docker ps`)
- [ ] http://<PUBLIC_IP>:8501 접속 OK
- [ ] 차트 및 데이터 로드 OK
- [ ] 인스턴스 재부팅 후 자동 재시작 확인

---

## 📊 예상 구조

```
로컬 개발 (Windows/Mac/Linux)
  ↓
venv + streamlit run
  ↓
Docker 이미지 테스트 (로컬)
  ↓
Docker Hub (선택)
  ↓
EC2 인스턴스
  ↓
Docker 컨테이너 + Systemd
  ↓
24/7 자동 실행
```

---

## 🔧 배포 후 유지보수

### 주간
```bash
# 로그 확인
docker logs -f market-dashboard

# 상태 확인
docker ps -a | grep market-dashboard

# 헬스 확인
docker inspect market-dashboard | grep Health
```

### 월간
```bash
# 코드 업데이트
cd ~/apps/market-dashboard
git pull origin main
docker build -t market-dashboard:latest .
docker restart market-dashboard

# 패키지 업데이트
docker build --no-cache -t market-dashboard:latest .
```

### 반기
```bash
# Python 버전 업그레이드
# Dockerfile에서 python:3.11-slim → python:3.12-slim
docker build -t market-dashboard:latest .
```

---

## 💡 팁

### 로컬에서 빠른 반복 개발
```bash
# docker-compose.yml의 volumes 주석 해제
volumes:
  - ./:/app

docker-compose up
# 로컬 파일 수정 → 브라우저 새로고침 → 즉시 반영
```

### EC2에서 Docker 이미지 크기 절약
```bash
# 빌드 후
docker image prune -a  # 사용하지 않는 이미지 삭제
docker builder prune   # 빌드 캐시 정리
```

### 모바일에서 접속
```bash
# EC2 인스턴스 공인 IP
http://EC2_PUBLIC_IP:8501

# 또는 탄력적 IP로 고정
http://ELASTIC_IP:8501
```

---

## 🚨 주의사항

### 보안
- ⚠️ **8501 포트 공개:** 필요시 특정 IP만 허용
- ⚠️ **SSH 키 관리:** 안전한 위치에 보관
- ⚠️ **IAM 권한:** 최소 권한 원칙 준수

### 비용
- 📊 **EC2:** t2.micro 프리티어 (12개월) 또는 월 $7-9
- 📊 **탄력적 IP:** 미사용 시 월 $0.32 (사용 중 무료)
- 📊 **EBS:** 8GB = 월 $0.77 (gp3)

### 성능
- ⚠️ **t2.nano:** CPU 버스트 제한 (트래픽 낮으면 OK)
- ⚠️ **메모리:** 1GB로 충분 (Streamlit + yfinance)
- ⚠️ **API 타임아웃:** utils.py에서 10초 설정 (필요시 조정)

---

## 📞 문제 해결

### "컨테이너가 시작되지 않음"
```bash
docker logs market-dashboard
# 로그 확인 후 문제 해결
# 대부분 API 타임아웃 또는 의존성 문제
```

### "API 데이터가 로드되지 않음"
```bash
# EC2에서 외부 접속 테스트
curl -I https://api.alternative.me/fng/?limit=1

# 결과: 200 OK이면 정상
# 결과: 오류면 보안 그룹 아웃바운드 확인
```

### "높은 CPU 사용률"
```bash
docker stats market-dashboard

# 메모리 누수가 없으면 정상
# (Streamlit 특성상 주기적으로 데이터 갱신)

# 해결: 컨테이너 재시작
docker restart market-dashboard
```

---

## 📚 참고 문서

- [LOCAL_DEV.md](LOCAL_DEV.md) — 로컬 개발 가이드
- [EC2_DEPLOY_GUIDE.md](EC2_DEPLOY_GUIDE.md) — EC2 배포 상세 가이드
- [CLAUDE.md](CLAUDE.md) — 프로젝트 개요

---

## ✅ 최종 확인

배포 완료 후:
1. http://<EC2_PUBLIC_IP>:8501 접속
2. 📊 Market Dashboard 헤더 확인
3. 주요 지수 카드 데이터 확인
4. Fear & Greed 게이지 확인
5. 차트 로드 확인

모두 OK → **배포 성공** 🎉

---

**업데이트:** 2026-04-04
**버전:** 1.0
**상태:** 배포 준비 완료 ✅
