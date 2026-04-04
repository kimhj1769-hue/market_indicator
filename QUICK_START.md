# 빠른 시작 가이드 (EC2 배포)

## 📋 사전 준비
1. AWS 계정 생성 및 로그인
2. GitHub 저장소 생성 (코드 업로드용)
3. EC2 인스턴스 생성 (Ubuntu 22.04 LTS, t3.micro 이상)

---

## 🚀 3단계 배포

### Step 1: GitHub에 코드 업로드
```bash
cd C:\Users\Kim.HJ\Desktop\market-dashboard
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/market-dashboard.git
git push -u origin main
```

### Step 2: EC2 접속
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Step 3: 배포 실행
```bash
git clone https://github.com/YOUR_USERNAME/market-dashboard.git
cd market-dashboard

# deploy.sh에서 <YOUR_REPO_URL> 수정
nano deploy.sh  # 또는 사용자 계정명 등 수정

chmod +x deploy.sh
./deploy.sh
```

---

## 🌐 접속
배포 완료 후 브라우저에서:

```
http://YOUR_EC2_IP:8501
```

---

## 📊 서비스 관리

```bash
# 상태 확인
sudo systemctl status streamlit-dashboard

# 로그 보기
sudo journalctl -u streamlit-dashboard -f

# 재시작
sudo systemctl restart streamlit-dashboard

# 중지
sudo systemctl stop streamlit-dashboard
```

---

## 📝 코드 업데이트
```bash
cd ~/apps/market-dashboard
git pull origin main
sudo systemctl restart streamlit-dashboard
```

---

## 🆘 문제 해결

| 증상 | 해결 방법 |
|------|----------|
| 포트 8501 연결 불가 | `sudo ufw allow 8501/tcp` |
| 서비스 실행 안됨 | `sudo journalctl -u streamlit-dashboard -f` 로그 확인 |
| 메모리 부족 | EC2 인스턴스 타입을 t3.small로 업그레이드 |

---

## 📖 자세한 가이드
`EC2_DEPLOY.md` 파일 참고 (Nginx, HTTPS, 도메인 등)

