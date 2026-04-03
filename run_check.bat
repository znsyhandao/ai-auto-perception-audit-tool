@echo off
chcp 65001 >nul
echo ============================================================
echo 🔍 增强版安全检查 - 基于AISkinX经验
echo ============================================================
echo 检查目录: %1
echo ============================================================

REM 检查Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 没有找到Python，请安装Python 3.7+
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo.

REM 运行安全检查
python enhanced_security_scanner.py "%1"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 🎉 安全检查完成，所有检查通过！
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ❌ 安全检查失败，需要修复问题！
    echo ============================================================
)

pause