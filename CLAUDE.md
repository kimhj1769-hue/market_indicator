# Market Dashboard 프로젝트

Streamlit 기반 금융 시장 대시보드. EC2에서 24/7 실행.

---

## 폴더 구조

```
market-dashboard/
├── Home.py              # 메인 페이지 (메트릭, 차트)
├── utils.py             # 데이터 수집 함수 (yfinance, API)
├── requirements.txt     # Python 패키지
├── deploy.sh            # EC2 자동 배포 스크립트
├── EC2_DEPLOY.md        # 상세 배포 가이드
├── QUICK_START.md       # 빠른 시작 가이드
├── .streamlit/
│   └── config.toml      # Streamlit 서버 설정 (포트 8501)
├── pages/               # 다중 페이지 앱
└── venv/                # Python 가상환경
```

---

## 환경

- **Python**: 3.11+
- **Streamlit**: 1.32.0+
- **배포**: AWS EC2 Ubuntu 22.04 LTS
- **서비스 관리**: Systemd
- **포트**: 8501 (Streamlit 기본)

---

## 필수 설정

### 로컬 실행
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

### EC2 배포
```bash
./deploy.sh              # 자동 배포 (권장)
# 또는 EC2_DEPLOY.md 참고하여 수동 배포
```

---

## 핵심 파일 설명

### Home.py
- 메인 대시보드 페이지
- 시장 개요, Fear & Greed 지수, 차트 표시
- CSS 커스터마이징 (다크테마)

### utils.py
- `get_market_overview()` - 시장 데이터 수집
- `get_fear_greed()` - 공포/탐욕 지수
- `get_chart_data()` - 차트용 데이터
- `clear_cache()` - 캐시 초기화

### .streamlit/config.toml
- 포트 8501로 설정
- 헤드리스 모드 활성화 (EC2용)
- CORS/CSRF 보호 활성화

---

## 배포 체크리스트

- [ ] GitHub 저장소 생성 및 코드 업로드
- [ ] AWS EC2 인스턴스 생성 (Ubuntu 22.04)
- [ ] 보안 그룹에서 포트 8501 오픈
- [ ] `deploy.sh`에서 repo URL 수정
- [ ] EC2 접속 후 `./deploy.sh` 실행
- [ ] Systemd 서비스 자동 실행 확인
- [ ] 브라우저에서 접속 테스트

---

## 서비스 관리

```bash
# 상태 확인
sudo systemctl status streamlit-dashboard

# 실시간 로그
sudo journalctl -u streamlit-dashboard -f

# 재시작
sudo systemctl restart streamlit-dashboard

# 중지
sudo systemctl stop streamlit-dashboard
```

---

## 필수 규칙 (MUST FOLLOW)

- EC2 배포 시 항상 Systemd 서비스 사용 (수동 실행 금지)
- GitHub에 민감한 정보(API 키) 올리지 않기 (`.env` 사용 또는 AWS Secrets Manager)
- Streamlit 포트 8501은 고정 (config.toml에 명시)
- 코드 수정 후 자동 재로드 확인
- 로그로 에러 추적 가능하도록 유지

---

## 커스텀 스킬

| 스킬 | 설명 |
|------|------|
| `/ec2-deploy` | EC2 배포 자동화 스크립트 생성 및 실행 |
| `/streamlit-config` | Streamlit 설정 최적화 (포트, CORS 등) |
| `/systemd-service` | Systemd 서비스 파일 자동 생성 |
| `/check-deployment` | EC2 배포 상태 확인 |

---

## 표준 작업 순서

### 초기 배포
1. GitHub 저장소 생성 및 코드 푸시
2. EC2 인스턴스 생성
3. `./deploy.sh` 실행
4. 서비스 상태 확인
5. 브라우저 접속 테스트

### 코드 수정 후 배포
1. 로컬에서 테스트
2. Git 커밋 및 푸시
3. EC2에서 `git pull`
4. `sudo systemctl restart streamlit-dashboard`

### 문제 해결
1. 로그 확인: `sudo journalctl -u streamlit-dashboard -f`
2. 서비스 상태: `sudo systemctl status streamlit-dashboard`
3. 포트 확인: `sudo netstat -tlnp | grep 8501`

