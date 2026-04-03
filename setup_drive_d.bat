@echo off
echo ========================================
echo    OpenClaw测试框架 - D盘设置工具
echo ========================================
echo.

REM 检查D盘是否存在
if not exist D:\ (
    echo ❌ D盘不存在！
    echo 请确保D盘已正确连接。
    pause
    exit /b 1
)

REM 检查备份目录
if not exist "D:\OpenClaw_TestingFramework\" (
    echo ❌ 测试框架目录不存在: D:\OpenClaw_TestingFramework\
    echo 请先复制测试框架文件到D盘。
    pause
    exit /b 1
)

echo ✅ D盘测试框架目录存在

REM 恢复测试框架到OpenClaw工作空间
echo.
echo 🔧 恢复测试框架到OpenClaw工作空间...
python "D:\OpenClaw_TestingFramework\restore_testing_framework.py"

if %errorlevel% neq 0 (
    echo ❌ 恢复失败！
    pause
    exit /b 1
)

echo ✅ 测试框架恢复成功

REM 设置自动加载
echo.
echo 🔧 设置自动加载...
python "D:\OpenClaw_TestingFramework\auto_load_testing.py"

echo.
echo ========================================
echo           设置完成！
echo ========================================
echo.
echo 📁 备份位置: D:\OpenClaw_TestingFramework\
echo 🔧 恢复脚本: restore_testing_framework.py
echo 🚀 自动加载: auto_load_testing.py
echo 📚 文档指南: BACKUP_AND_RESTORE_GUIDE.md
echo.
echo 💡 使用建议:
echo   1. 每次重新安装OpenClaw后运行此脚本
echo   2. 或直接运行恢复脚本: python restore_testing_framework.py
echo   3. 查看完整指南: BACKUP_AND_RESTORE_GUIDE.md
echo.
pause