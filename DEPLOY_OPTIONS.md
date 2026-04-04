# 배포 옵션 선택

## 옵션 1️⃣: GitHub → EC2 (권장)

**필요한 것:**
- GitHub 계정 & 저장소 URL
- AWS EC2 인스턴스 (t3.micro 이상)

**단계:**
```bash
# 1. GitHub에 저장소 생성
# https://github.com/new → "market-dashboard"

# 2. 로컬에서 푸시
git remote add origin https://github.com/YOUR_USERNAME/market-dashboard.git
git branch -M main
git push -u origin main

# 3. EC2 접속
ssh -i your-key.pem ubuntu@EC2_IP

# 4. 배포
git clone https://github.com/YOUR_USERNAME/market-dashboard.git
cd market-dashboard
chmod +x deploy.sh
./deploy.sh
```

---

## 옵션 2️⃣: 로컬 테스트 먼저 (추천)

**현재 환경에서 Streamlit 앱 테스트:**

```bash
cd C:\Users\Kim.HJ\Desktop\market-dashboard
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

브라우저: http://localhost:8501

---

## 옵션 3️⃣: Docker 배포 (간단)

**EC2에서:**
```bash
git clone https://github.com/YOUR_USERNAME/market-dashboard.git
cd market-dashboard
sudo docker-compose up -d
# 접속: http://EC2_IP:8501
```

---

## 선택 후 알려주세요!

1. **GitHub URL** (예: https://github.com/kim-hj/market-dashboard)
2. **EC2 IP** (또는 "인스턴스 없음" → 생성 가이드 제공)
3. **선호하는 배포 옵션** (GitHub, Local, Docker)

