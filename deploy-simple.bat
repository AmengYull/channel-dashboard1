@echo off
chcp 65001 >nul
echo ==========================================
echo   渠道数据看板 - 快速部署到 Vercel
echo ==========================================
echo.

REM 检查 Vercel CLI
call npx vercel --version >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 Vercel CLI...
    call npm install -g vercel
)

REM 生成数据
echo [1/2] 正在生成数据文件...
python generate_js.py
if errorlevel 1 (
    echo [错误] 数据生成失败
    pause
    exit /b 1
)
echo [完成] 数据生成成功
echo.

REM 部署到 Vercel
echo [2/2] 正在部署到 Vercel...
echo 首次部署需要登录 Vercel 账号
call npx vercel --prod
echo.

echo ==========================================
echo   部署完成！
echo   请查看上方输出的访问链接
echo ==========================================
pause
