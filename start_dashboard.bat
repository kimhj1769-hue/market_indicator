@echo off
chcp 65001 > nul
title Market Dashboard

cd /d "C:\Users\Kim.HJ\Desktop\market-dashboard"

echo ============================================
echo   Market Dashboard 시작 중...
echo ============================================
echo.
echo  잠시 후 브라우저가 자동으로 열립니다.
echo  핸드폰: 같은 WiFi에서 http://192.168.45.125:8501
echo.

venv\Scripts\streamlit.exe run Home.py --server.port 8501 --server.address 0.0.0.0

pause
