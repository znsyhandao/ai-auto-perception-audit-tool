@echo off
echo ==========================================
echo 企业级审核框架部署脚本 (Windows)
echo ==========================================

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装
    echo 请先安装Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose未安装
    echo 请先安装Docker Compose
    pause
    exit /b 1
)

echo ✓ Docker和Docker Compose已安装

REM 检查环境文件
if not exist ".env" (
    echo 创建环境配置文件...
    copy .env.example .env
    echo ✓ 环境配置文件已创建
    echo 请编辑 .env 文件配置您的设置
)

REM 构建和启动服务
echo 构建Docker镜像...
docker-compose build

echo 启动服务...
docker-compose up -d

echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 检查服务状态...
set services=api-gateway validator security performance compliance reporting monitoring deep-analysis

for %%s in (%services%) do (
    docker-compose ps | findstr "%%s.*Up" >nul
    if errorlevel 1 (
        echo   ✗ %%s: 未运行
    ) else (
        echo   ✓ %%s: 运行中
    )
)

echo.
echo ==========================================
echo 部署完成！
echo ==========================================
echo.
echo 服务访问地址:
echo   API网关:      http://localhost:8000
echo   验证服务:     http://localhost:8001
echo   安全服务:     http://localhost:8002
echo   性能服务:     http://localhost:8003
echo   合规服务:     http://localhost:8004
echo   报告服务:     http://localhost:8005
echo   监控服务:     http://localhost:8006
echo   深度分析服务: http://localhost:8007
echo.
echo API文档:
echo   Swagger UI:   http://localhost:8000/docs
echo   ReDoc:        http://localhost:8000/redoc
echo.
echo 管理命令:
echo   查看日志:     docker-compose logs -f
echo   停止服务:     docker-compose down
echo   重启服务:     docker-compose restart
echo   更新服务:     docker-compose pull ^&^& docker-compose up -d
echo.
echo 默认API密钥: demo_key
echo ==========================================
pause