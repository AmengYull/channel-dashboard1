@echo off
REM === 渠道数据看板 一键启动脚本 ===
REM 启动两个服务：
REM   1) Python http.server on port 8081  (static files)
REM   2) Flask proxy.py on port 8082 (AI API proxy)

set BASE_DIR=%~dp0
set PYTHON_EXE=python

echo ===================================================
echo  渠道数据看板 — 启动脚本
echo ===================================================
echo.

REM ---- Step 1: Check if 渠道数据.xlsx exists ----
if not exist "%BASE_DIR%\渠道数据.xlsx" (
    echo [警告] 找不到 渠道数据.xlsx，data.js 可能无法重新生成
)

REM ---- Step 2: Re-generate data.js (optional) ----
echo [1/4] 重新生成 data.js ...
"%PYTHON_EXE%" "%BASE_DIR%\generate_js.py"
if errorlevel 1 (
    echo   [警告] generate_js.py 运行失败，将使用已有 data.js
) else (
    echo   [OK] data.js 已重新生成
)
echo.

REM ---- Step 3: Start http.server (port 8081) in new window ----
echo [2/4] 启动静态文件服务（port 8081)...
start "看板-静态服务" /D "%BASE_DIR%" "%PYTHON_EXE%" -m http.server 8081
timeout /t 2 /nobreak >nul
echo   [OK] 静态服务已启动： http://localhost:8081/dashboard.html
echo.

REM ---- Step 4: Check if Flask dependencies are installed ----
echo [3/4] 检查 Flask 依赖...
"%PYTHON_EXE%" -c "import flask, flask_cors, requests; print('OK')" 2>nul
if errorlevel 1 (
    echo   [安装] flask, flask-cors, requests 未安装，正在安装...
    "%PYTHON_VEN_PIP%" install flask flask-cors requests -q
if errorlevel 1 (
    echo   [重试] 尝试使用 python -m pip...
    "%PYTHON_VEN_V%" -m pip install flask flask-cors requests -q
)
    echo   [OK] 依赖已安装
) else (
    echo   [OK] Flask 依赖已安装
)
echo.

REM ---- Step 5: Start Flask proxy (port 8082) in new window ----
echo [4/4] 启动 AI 分析代理服务（port 8082)...
start "看板-AI代理" /D "%BASE_DIR%" "%PYTHON_VENV%" proxy.py
timeout /t 2 /nobreak >nul
echo   [OK] AI 代理已启动： http://localhost:8082/api/health
echo.

REM ---- Step 6: Open browser ----
echo ===================================================
echo  所有服务已启动！
echo  - 看板地址：<A href="http://localhost:8081/dashboard.html">http://localhost:8081/dashboard.html</A>
echo  - AI 代理： http://localhost:8082/api/health
echo.
echo  提示：关闭这两个窗口即可停止服务
echo ===================================================
echo.
start http://localhost:8081/dashboard.html
echo 浏览器已打开，如果没有自动打开请手动访问上述地址。
echo.
pause
