# 企业级审核框架 - 启动所有服务脚本
# 启动6个微服务：验证(8001)、安全(8002)、性能(8003)、合规(8004)、报告(8005)、监控(8006)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  企业级审核框架 - 启动所有服务" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
Write-Host "[1] 检查Python环境..." -ForegroundColor Yellow
$pythonVersion = python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Python未安装或不在PATH中" -ForegroundColor Red
    exit 1
}
Write-Host "Python版本: $pythonVersion" -ForegroundColor Green

# 检查FastAPI和Uvicorn
Write-Host "[2] 检查依赖..." -ForegroundColor Yellow
try {
    python -c "import fastapi; import uvicorn; print('FastAPI和Uvicorn已安装')"
} catch {
    Write-Host "警告: FastAPI或Uvicorn未安装，尝试安装..." -ForegroundColor Yellow
    pip install fastapi uvicorn
}

Write-Host ""
Write-Host "[3] 启动6个微服务..." -ForegroundColor Yellow
Write-Host ""

# 服务配置
$services = @(
    @{Name="验证服务"; Port=8001; Path="microservices\validator-service"; File="main_fixed.py"},
    @{Name="安全服务"; Port=8002; Path="microservices\security-service"; File="main_fixed.py"},
    @{Name="性能服务"; Port=8003; Path="microservices\performance-service"; File="main.py"},
    @{Name="合规服务"; Port=8004; Path="microservices\compliance-service"; File="main.py"},
    @{Name="报告服务"; Port=8005; Path="microservices\reporting-service"; File="main.py"},
    @{Name="监控服务"; Port=8006; Path="microservices\monitoring-service"; File="main.py"}
)

# 启动每个服务
foreach ($service in $services) {
    $serviceName = $service.Name
    $port = $service.Port
    $path = $service.Path
    $file = $service.File
    
    Write-Host "启动 $serviceName (端口: $port)..." -ForegroundColor White
    
    # 检查服务文件是否存在
    $fullPath = Join-Path $path $file
    if (-not (Test-Path $fullPath)) {
        Write-Host "  错误: 服务文件不存在: $fullPath" -ForegroundColor Red
        continue
    }
    
    # 在新的PowerShell窗口中启动服务
    $command = "cd '$PSScriptRoot\$path'; uvicorn main:app --host 0.0.0.0 --port $port --reload"
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command -WindowStyle Normal
    
    Write-Host "  $serviceName 已启动 (等待5秒)..." -ForegroundColor Green
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "[4] 验证服务状态..." -ForegroundColor Yellow

# 等待所有服务启动
Write-Host "等待服务完全启动 (15秒)..." -ForegroundColor White
Start-Sleep -Seconds 15

# 检查每个服务
$allHealthy = $true
foreach ($service in $services) {
    $serviceName = $service.Name
    $port = $service.Port
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/health" -TimeoutSec 5
        if ($response.status -eq "healthy") {
            Write-Host "  $serviceName (端口: $port): 健康 ✅" -ForegroundColor Green
        } else {
            Write-Host "  $serviceName (端口: $port): 不健康 ❌" -ForegroundColor Red
            $allHealthy = $false
        }
    } catch {
        Write-Host "  $serviceName (端口: $port): 不可达 ❌" -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
if ($allHealthy) {
    Write-Host "✅ 所有6个服务已成功启动！" -ForegroundColor Green
} else {
    Write-Host "⚠️  部分服务启动失败，请检查日志" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "服务端点:" -ForegroundColor Cyan
Write-Host "  验证服务: http://localhost:8001" -ForegroundColor White
Write-Host "  安全服务: http://localhost:8002" -ForegroundColor White
Write-Host "  性能服务: http://localhost:8003" -ForegroundColor White
Write-Host "  合规服务: http://localhost:8004" -ForegroundColor White
Write-Host "  报告服务: http://localhost:8005" -ForegroundColor White
Write-Host "  监控服务: http://localhost:8006" -ForegroundColor White

Write-Host ""
Write-Host "监控面板: http://localhost:8006/status" -ForegroundColor Cyan
Write-Host "完整审核示例: python .\run_full_audit.py" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 打开监控面板
Write-Host ""
$openDashboard = Read-Host "是否打开监控面板? (y/n)"
if ($openDashboard -eq "y" -or $openDashboard -eq "Y") {
    Start-Process "http://localhost:8006/status"
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")