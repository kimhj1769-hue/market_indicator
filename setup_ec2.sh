#!/bin/bash
# AWS EC2 인스턴스 생성 스크립트 (AWS CLI 필요)

set -e

echo "=== AWS EC2 인스턴스 생성 ==="
echo ""
echo "필수 사항:"
echo "1. AWS 계정 & IAM 권한"
echo "2. AWS CLI 설치: https://aws.amazon.com/cli/"
echo "3. AWS 자격증명 설정: aws configure"
echo ""

# AWS CLI 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되지 않았습니다."
    echo "설치: https://aws.amazon.com/cli/ 또는 choco install awscli"
    exit 1
fi

echo "AWS CLI 버전:"
aws --version

# AWS 계정 정보 확인
echo ""
echo "AWS 계정 확인 중..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS 계정: $ACCOUNT_ID"

# 인스턴스 파라미터
INSTANCE_TYPE="t3.micro"
KEY_NAME="market-indicator-key"
SECURITY_GROUP="market-indicator-sg"
INSTANCE_NAME="market-indicator"
REGION="us-east-1"

echo ""
echo "인스턴스 설정:"
echo "  - 타입: $INSTANCE_TYPE (프리티어 대상)"
echo "  - 키 페어: $KEY_NAME"
echo "  - 보안그룹: $SECURITY_GROUP"
echo "  - 리전: $REGION"
echo ""

read -p "진행하시겠습니까? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ 취소됨"
    exit 0
fi

# 1. 키 페어 생성
echo ""
echo "🔑 키 페어 생성 중..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION 2>/dev/null; then
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > "${KEY_NAME}.pem"
    chmod 400 "${KEY_NAME}.pem"
    echo "✅ 키 페어 생성: ${KEY_NAME}.pem (현재 디렉토리)"
else
    echo "⚠️ 키 페어 이미 존재"
fi

# 2. 보안 그룹 생성
echo ""
echo "🔒 보안 그룹 생성 중..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "")

if [ "$SG_ID" = "" ] || [ "$SG_ID" = "None" ]; then
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP \
        --description "Market Dashboard Security Group" \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    echo "✅ 보안 그룹 생성: $SG_ID"

    # 인바운드 규칙 추가
    echo "  규칙 추가 중..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp --port 22 --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null && echo "    - SSH (22)"

    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp --port 80 --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null && echo "    - HTTP (80)"

    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp --port 443 --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null && echo "    - HTTPS (443)"

    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp --port 8501 --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null && echo "    - Streamlit (8501)"
else
    echo "⚠️ 보안 그룹 이미 존재: $SG_ID"
fi

# 3. EC2 인스턴스 생성
echo ""
echo "🚀 EC2 인스턴스 생성 중 (1-2분 소요)..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

if [ -z "$INSTANCE_ID" ]; then
    echo "❌ 인스턴스 생성 실패"
    exit 1
fi

echo "✅ 인스턴스 생성: $INSTANCE_ID"

# 4. IP 주소 할당 대기
echo ""
echo "⏳ Public IP 할당 대기 중..."
sleep 10

PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

if [ "$PUBLIC_IP" = "None" ] || [ -z "$PUBLIC_IP" ]; then
    echo "⏳ IP 할당 중... (최대 1분)"
    for i in {1..12}; do
        sleep 5
        PUBLIC_IP=$(aws ec2 describe-instances \
            --instance-ids $INSTANCE_ID \
            --region $REGION \
            --query 'Reservations[0].Instances[0].PublicIpAddress' \
            --output text)
        if [ "$PUBLIC_IP" != "None" ] && [ ! -z "$PUBLIC_IP" ]; then
            break
        fi
    done
fi

echo "✅ Public IP: $PUBLIC_IP"

# 최종 정보
echo ""
echo "=========================================="
echo "✅ EC2 인스턴스 준비 완료!"
echo "=========================================="
echo ""
echo "인스턴스 정보:"
echo "  ID: $INSTANCE_ID"
echo "  Public IP: $PUBLIC_IP"
echo "  키 파일: ${KEY_NAME}.pem"
echo ""
echo "접속 방법:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo ""
echo "배포:"
echo "  git clone https://github.com/kimhj1769-hue/market_indicator.git"
echo "  cd market-indicator"
echo "  chmod +x deploy.sh"
echo "  ./deploy.sh"
echo ""
echo "접속 주소:"
echo "  http://${PUBLIC_IP}:8501"
echo ""

# IP 저장
echo "$PUBLIC_IP" > ec2_ip.txt
echo "IP 저장됨: ec2_ip.txt"
