# 로컬 개발 및 Docker 테스트 가이드

## 1. 로컬 환경 설정 (개발)

### 1.1 Python venv 설정
```bash
cd market-dashboard
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 1.2 로컬에서 실행
```bash
streamlit run Home.py
# 또는
streamlit run Home.py --logger.level=debug
```

**접속:** http://localhost:8501

### 1.3 API 데이터 테스트
```python
cd market-dashboard
python -c "
import utils
market = utils.get_market_overview()
fg = utils.get_fear_greed()
print('Market:', market)
print('Fear & Greed:', fg)
"
```

---

## 2. Docker 로컬 테스트

### 2.1 Docker 설치 확인
```bash
docker --version
docker-compose --version
```

### 2.2 Docker 이미지 빌드
```bash
cd market-dashboard
docker build -t market-dashboard:latest .
```

### 2.3 Docker 컨테이너 실행 (단일)
```bash
docker run -p 8501:8501 market-dashboard:latest
```

**접속:** http://localhost:8501

### 2.4 Docker Compose로 실행 (권장)
```bash
docker-compose up --build
```

**종료:** `Ctrl+C` 또는 다른 터미널에서:
```bash
docker-compose down
```

### 2.5 백그라운드 실행
```bash
docker-compose up -d
docker logs -f market-dashboard  # 로그 보기
docker-compose down               # 중지
```

---

## 3. Docker 이미지 푸시 (선택)

### 3.1 Docker Hub에 푸시 (배포 준비)
```bash
# 로그인
docker login

# 태그 변경 (YOUR_USERNAME 교체)
docker tag market-dashboard:latest YOUR_USERNAME/market-dashboard:latest

# 푸시
docker push YOUR_USERNAME/market-dashboard:latest
```

### 3.2 EC2에서 풀
```bash
docker pull YOUR_USERNAME/market-dashboard:latest
docker run -d -p 8501:8501 --restart=unless-stopped \
  YOUR_USERNAME/market-dashboard:latest
```

---

## 4. 문제 해결

### 4.1 포트 충돌 (8501이 이미 사용 중)
```bash
# 다른 포트로 실행
docker run -p 8502:8501 market-dashboard:latest
# 또는
docker-compose.yml에서 ports 변경: "8502:8501"
```

### 4.2 API 타임아웃
```bash
# utils.py에서 timeout 증가 (현재 10초)
# 또는 캐시 TTL 조정 (기본값 참고)
```

### 4.3 메모리 부족
```bash
# Docker 할당 메모리 증가
# Docker Desktop 설정 → Resources → Memory: 2GB 이상
```

### 4.4 컨테이너 로그 확인
```bash
docker ps                                    # 실행 중인 컨테이너
docker logs market-dashboard                 # 현재 로그
docker logs -f market-dashboard              # 실시간 로그
docker inspect market-dashboard              # 상세 정보
```

---

## 5. 개발 팁

### 5.1 실시간 코드 수정 (볼륨 마운트)
```bash
docker-compose up -d  # docker-compose.yml의 volumes 주석 해제
# 로컬 파일 수정 후 브라우저 새로고침
```

### 5.2 특정 패이지만 테스트
```bash
# Home.py 대신
streamlit run pages/2_Charts.py
```

### 5.3 성능 프로파일링
```bash
streamlit run Home.py --logger.level=debug --client.logger.level=debug
```

---

## 6. Docker 이미지 최적화

### 현재 크기
```bash
docker images market-dashboard:latest
# 약 400-500 MB
```

### 최적화 전략 (필요 시)
- Multi-stage build 사용
- 캐시 레이어 최소화
- 불필요한 의존성 제거

---

## 7. 프로덕션 체크리스트

배포 전 확인사항:
- [ ] 로컬에서 `docker-compose up` 테스트 완료
- [ ] API 데이터 로딩 확인 (홈 페이지 차트 표시)
- [ ] 차트 페이지 정상 동작 확인
- [ ] 모바일 브라우저에서 접속 테스트
- [ ] 로그에 에러 메시지 없음
- [ ] 30초 이상 지속 실행 테스트

---

다음: [EC2_DEPLOY.md](EC2_DEPLOY.md)
