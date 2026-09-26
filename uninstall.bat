@echo off
chcp 65001 >nul
title 校园网自动登录 - 卸载

echo ============================================================
echo           校园网自动登录程序 - 卸载
echo ============================================================
echo.

:: 删除任务计划程序任务
echo [1/3] 删除开机自动登录任务...
schtasks /query /tn CampusNetworkAutoLogin >nul 2>&1
if not errorlevel 1 (
    schtasks /delete /tn CampusNetworkAutoLogin /f
    echo [✓] 任务已删除
) else (
    echo [i] 任务不存在，跳过
)

:: 删除生成的文件
echo.
echo [2/3] 清理生成的文件...
if exist start_login.bat del start_login.bat
if exist start_login_silent.vbs del start_login_silent.vbs
echo [✓] 文件已清理

:: 删除日志文件
echo.
echo [3/3] 清理日志文件...
if exist campus_network.log (
    set /p delete_log="是否删除日志文件? (y/n): "
    if /i "%delete_log%"=="y" (
        del campus_network.log
        echo [✓] 日志已删除
    ) else (
        echo [i] 保留日志文件
    )
)

echo.
echo ============================================================
echo                    卸载完成！
echo ============================================================
echo.
echo 注意: 配置文件 config.json 已保留
echo 如需完全删除，请手动删除项目文件夹
echo.
pause
