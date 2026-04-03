@echo off
REM 企业级审核框架 - 简单部署脚本 (Windows批处理)
REM 生成时间: 2026-03-30

echo ==========================================
echo    企业级审核框架 v3.0 - 部署脚本
echo    Enterprise Audit Framework v3.0
echo ==========================================
echo.

REM 检查Docker
echo [CHECK] 检查Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop for Windows
    echo 下载地址: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo [OK] Docker已安装

REM 检查Docker Compose
echo [CHECK] 检查Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose未安装
    echo Docker Desktop通常包含Docker Compose
    pause
    exit /b 1
)
echo [OK] Docker Compose已安装

REM 创建数据目录
echo [DIR] 创建数据目录...
if not exist data mkdir data
cd data
mkdir mongodb 2>nul
mkdir redis 2>nul
mkdir timescaledb 2>nul
mkdir neo4j 2>nul
mkdir prometheus 2>nul
mkdir grafana 2>nul
mkdir rabbitmq 2>nul
cd ..
echo [OK] 数据目录创建完成

REM 启动服务
echo [SERVICE] 启动企业级审核框架服务...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] 启动服务失败
    pause
    exit /b 1
)
echo [OK] 服务启动命令已发送

REM 等待服务启动
echo [WAIT] 等待服务启动 (15秒)...
timeout /t 15 /nobreak >nul

REM 检查服务状态
echo [STATUS] 检查服务状态...
docker-compose ps

echo.
echo ==========================================
echo [SUCCESS] 部署完成！
echo ==========================================
echo.

echo 访问以下服务：
echo   API网关: http://localhost:8000
echo   监控面板: http://localhost:3000 ^(admin/enterprise123^)
echo   Prometheus: http://localhost:9090
echo   RabbitMQ管理: http://localhost:15672 ^(admin/enterprise123^)
echo.

echo 微服务端点：
echo   验证服务: http://localhost:8001
echo   安全服务: http://localhost:8002
echo   性能服务: http://localhost:8003
echo   合规服务: http://localhost:8004
echo   报告服务: http://localhost:8005
echo.

echo 使用以下命令管理服务：
echo   查看日志: docker-compose logs -f
echo   重启服务: docker-compose restart
echo   停止服务: docker-compose down
echo.

echo 测试企业级框架：
echo   python test_enterprise_framework.py
echo.

echo ==========================================
pause