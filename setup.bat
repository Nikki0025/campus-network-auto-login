@echo off
chcp 65001 >nul
title 校园网自动登录 - 安装向导

echo ============================================================
echo           校园网自动登录程序 - 安装向导
echo ============================================================
echo.

:: 检查Python是否安装
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [✓] Python环境正常

:: 安装依赖
echo.
echo [2/4] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [✓] 依赖安装完成

:: 测试登录
echo.
echo [3/4] 测试登录功能...
echo 请确保已连接校园网
set /p test_choice="是否现在测试登录? (y/n): "
if /i "%test_choice%"=="y" (
    python main.py
)

:: 设置开机自启
echo.
echo [4/4] 设置开机自动登录...
set /p setup_choice="是否设置开机自动登录? (y/n): "
if /i "%setup_choice%"=="y" (
    python scheduler.py
)

echo.
echo ============================================================
echo                    安装完成！
echo ============================================================
echo.
echo 使用方法:
echo   1. 手动登录: python main.py
echo   2. 设置开机自启: python scheduler.py
echo   3. 查看日志: type campus_network.log
echo.
echo 配置文件: config.json (首次运行自动生成)
echo.
pause
