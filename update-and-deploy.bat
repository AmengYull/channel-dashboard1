@echo off
chcp 65001 >nul
echo ==========================================
echo   渠道数据看板 - 更新并部署
echo ==========================================
echo.

REM 检查 Git 是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Git，请先安装 Git
    pause
    exit /b 1
)

REM 生成数据
echo [1/4] 正在生成数据文件...
python generate_js.py
if errorlevel 1 (
    echo [错误] 数据生成失败
    pause
    exit /b 1
)
echo [完成] 数据生成成功
echo.

REM 添加更改
echo [2/4] 正在添加文件到 Git...
git add data.js
git add 渠道数据.xlsx
git add 拓展线索.xlsx
git add *.html
echo [完成] 文件已添加
echo.

REM 提交更改
echo [3/4] 正在提交更改...
set TIMESTAMP=%date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,8%
git commit -m "Update data - %TIMESTAMP%"
if errorlevel 1 (
    echo [提示] 没有需要提交的更改，或提交失败
    pause
    exit /b 1
)
echo [完成] 提交成功
echo.

REM 推送到远程
echo [4/4] 正在推送到 GitHub...
git push origin main
if errorlevel 1 (
    echo [错误] 推送失败，请检查网络连接和仓库配置
    pause
    exit /b 1
)
echo [完成] 推送成功
echo.

echo ==========================================
echo   部署已触发！
echo   GitHub Actions 将自动构建并部署
echo   请访问 GitHub 查看部署状态
echo ==========================================
pause
