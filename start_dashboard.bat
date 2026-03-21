@echo off
chcp 65001 > nul
title Market Dashboard

cd /d "C:\Users\Kim.HJ\Desktop\market-dashboard"

echo ============================================
echo   📊 Market Dashboard 시작 중...
echo ============================================
echo.
echo  브라우저가 자동으로 열립니다.
echo  핸드폰에서도 접속하려면:
echo  같은 WiFi에서 http://[PC IP]:8501 접속
echo.

call venv\Scripts\activate
streamlit run Home.py --server.port 8501 --server.address 0.0.0.0

pause
