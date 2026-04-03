# 企业级审核框架部署脚本 (PowerShell版本)
# 生成时间: 2026-03-30

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   企业级审核框架 v3.0 - 部署脚本" -ForegroundColor Yellow
Write-Host "   Enterprise Audit Framework v3.0" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker
Write-Host "[CHECK] 检查Docker..." -ForegroundColor Gray
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker未安装，请先安装Docker" -ForegroundColor Red
    exit 1
}

# 检查Docker Compose
Write-Host "[CHECK] 检查Docker Compose..." -ForegroundColor Gray
try {
    $composeVersion = docker-compose --version
    Write-Host "[OK] Docker Compose已安装: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker Compose未安装，请先安装Docker Compose" -ForegroundColor Red
    exit 1
}

# 创建数据目录
Write-Host "[DIR] 创建数据目录..." -ForegroundColor Gray
$dataDirs = @("mongodb", "redis", "timescaledb", "neo4j", "prometheus", "grafana", "rabbitmq")
foreach ($dir in $dataDirs) {
    $fullPath = Join-Path "data" $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  [+] 创建目录: $fullPath" -ForegroundColor DarkGray
    }
}

# 启动服务
Write-Host "[SERVICE] 启动企业级审核框架服务..." -ForegroundColor Gray
try {
    docker-compose up -d
    Write-Host "[OK] 服务启动命令已发送" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] 启动服务失败: $_" -ForegroundColor Red
    exit 1
}

# 等待服务启动
Write-Host "[WAIT] 等待服务启动 (10秒)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "[STATUS] 检查服务状态..." -ForegroundColor Gray
try {
    docker-compose ps
} catch {
    Write-Host "[WARNING] 无法获取服务状态: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] 部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "访问以下服务：" -ForegroundColor White
Write-Host "  API网关: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  监控面板: http://localhost:3000 (admin/enterprise123)" -ForegroundColor Cyan
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "  RabbitMQ管理: http://localhost:15672 (admin/enterprise123)" -ForegroundColor Cyan
Write-Host ""

Write-Host "微服务端点：" -ForegroundColor White
Write-Host "  验证服务: http://localhost:8001" -ForegroundColor DarkCyan
Write-Host "  安全服务: http://localhost:8002" -ForegroundColor DarkCyan
Write-Host "  性能服务: http://localhost:8003" -ForegroundColor DarkCyan
Write-Host "  合规服务: http://localhost:8004" -ForegroundColor DarkCyan
Write-Host "  报告服务: http://localhost:8005" -ForegroundColor DarkCyan
Write-Host ""

Write-Host "使用以下命令管理服务：" -ForegroundColor White
Write-Host "  查看日志: docker-compose logs -f" -ForegroundColor Gray
Write-Host "  重启服务: docker-compose restart" -ForegroundColor Gray
Write-Host "  停止服务: docker-compose down" -ForegroundColor Gray
Write-Host ""

Write-Host "测试企业级框架：" -ForegroundColor White
Write-Host "  python test_enterprise_framework.py" -ForegroundColor Gray
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan