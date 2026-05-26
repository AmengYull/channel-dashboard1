@echo off
chcp 65001 >nul
echo ==========================================
echo   推送数据到钉钉
echo ==========================================
echo.

python send_to_dingtalk.py

echo.
pause
