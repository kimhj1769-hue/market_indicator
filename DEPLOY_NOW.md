# 🚀 시작하기 - 배포 완전 가이드

## 1️⃣ GitHub 저장소 생성 (5분)

### Windows PowerShell에서:

```powershell
# GitHub CLI 설치 확인
gh --version

# 또는 설치
winget install gh

# 로그인
gh auth login

# 저장소 생성 및 푸시
cd C:\Users\Kim.HJ\Desktop\market-dashboard
git remote add origin https://github.com/YOUR_USERNAME/market-dashboard.git
git branch -M main
git push -u origin main
```

**결과:**
- ✅ GitHub에 `market-dashboard` 저장소 생성됨
- ✅ 로컬 코드 푸시 완료
- 📝 저장소 URL: `https://github.com/YOUR_USERNAME/market-dashboard.git`

---

## 2️⃣ AWS EC2 인스턴스 생성 (10분)

### 옵션 A: AWS CLI 자동화 (권장)

```powershell
# AWS CLI 설치
winget install aws-cli

# AWS 자격증명 설정
aws configure
# Access Key ID, Secret Access Key, Region(us-east-1) 입력

# EC2 인스턴스 자동 생성
cd C:\Users\Kim.HJ\Desktop\market-dashboard
bash setup_ec2.sh

# 결과:
# - market-dashboard-key.pem (저장됨)
# - ec2_ip.txt (IP 주소 저장됨)
```

### 옵션 B: AWS 콘솔 수동 생성

1. https://console.aws.amazon.com/ec2/
2. **인스턴스 시작** 클릭
3. **Ubuntu 22.04 LTS** 선택
4. **t3.micro** (프리티어)
5. **키 페어**: 새로 생성 → `market-dashboard-key.pem` 저장
6. **보안 그룹**: 다음 포트 오픈
   - 22 (SSH)
   - 80 (HTTP)
   - 443 (HTTPS)
   - 8501 (Streamlit)
7. **시작** → Public IP 복사

**결과:**
- ✅ EC2 인스턴스 실행 중
- 📝 Public IP: `X.X.X.X` (복사해두기)

---

## 3️⃣ 앱 배포 (2분)

### SSH로 EC2 접속

```bash
# PowerShell에서
ssh -i C:\Users\Kim.HJ\Desktop\market-dashboard\market-dashboard-key.pem ubuntu@YOUR_EC2_IP

# 또는 ec2_ip.txt에서 IP 자동 읽기
$IP = Get-Content C:\Users\Kim.HJ\Desktop\market-dashboard\ec2_ip.txt
ssh -i C:\Users\Kim.HJ\Desktop\market-dashboard\market-dashboard-key.pem ubuntu@$IP
```

### EC2에서 배포 실행

```bash
# 1. 코드 클론
git clone https://github.com/YOUR_USERNAME/market-dashboard.git
cd market-dashboard

# 2. 배포 자동 실행
chmod +x deploy.sh
./deploy.sh

# 3. 완료 대기 (1-2분)
# ✅ "배포 완료" 메시지 나올 때까지

# 4. 서비스 상태 확인
sudo systemctl status streamlit-dashboard
```

---

## 4️⃣ 대시보드 접속

### 브라우저에서

```
http://YOUR_EC2_IP:8501
```

예: `http://54.123.45.67:8501`

---

## ✅ 최종 체크리스트

- [ ] GitHub CLI 설치
- [ ] GitHub 저장소 생성 (코드 푸시)
- [ ] AWS 계정 활성화
- [ ] AWS CLI 설치 & 자격증명 설정
- [ ] EC2 인스턴스 생성 (Ubuntu 22.04, t3.micro)
- [ ] 보안 그룹에서 8501 포트 오픈
- [ ] SSH로 접속 확인
- [ ] `./deploy.sh` 실행
- [ ] Systemd 서비스 시작 확인
- [ ] 브라우저에서 접속 테스트

---

## 🛠️ 문제 해결

### SSH 접속 안됨
```bash
# 키 권한 확인 (Windows)
icacls "market-dashboard-key.pem" /inheritance:r

# SSH 포트 확인
aws ec2 describe-security-groups --group-ids sg-xxx
```

### 앱 실행 안됨
```bash
# EC2에서
sudo journalctl -u streamlit-dashboard -f
```

### 방화벽 설정 확인
```bash
# EC2에서
sudo ufw status
sudo ufw allow 8501
```

---

## 📞 지원

질문이 있으면 EC2_DEPLOY.md를 참고하세요.

- **SSH 문제**: EC2_DEPLOY.md § "EC2 인스턴스에 접속"
- **배포 실패**: EC2_DEPLOY.md § "문제 해결"
- **앱 업데이트**: EC2_DEPLOY.md § "코드 업데이트"

