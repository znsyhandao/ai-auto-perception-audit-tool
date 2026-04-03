#!/usr/bin/env pwsh
<#
企业级审核框架 - 生产环境部署脚本
版本: 3.1.0
#>

# 错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$Magenta = "Magenta"

function Write-Color {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Color "[✓] $Message" $Green
}

function Write-Info {
    param([string]$Message)
    Write-Color "[i] $Message" $Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Color "[!] $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Color "[✗] $Message" $Red
}

function Write-Step {
    param([int]$Step, [string]$Title)
    Write-Host ""
    Write-Color "=" * 70 $Magenta
    Write-Color "步骤 $Step : $Title" $Magenta
    Write-Color "=" * 70 $Magenta
    Write-Host ""
}

# 主函数
function Main {
    Write-Color "================================================================" $Cyan
    Write-Color "    企业级审核框架 v3.1.0 - 生产环境部署" $Cyan
    Write-Color "================================================================" $Cyan
    Write-Host ""
    
    # 检查Docker
    Write-Step 1 "检查Docker环境"
    try {
        $dockerVersion = docker --version
        Write-Success "Docker已安装: $dockerVersion"
        
        $dockerComposeVersion = docker-compose --version
        Write-Success "Docker Compose已安装: $dockerComposeVersion"
    } catch {
        Write-Error "Docker未安装或未运行"
        Write-Info "请先安装Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    }
    
    # 检查端口占用
    Write-Step 2 "检查端口占用"
    $ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 3000)
    $occupiedPorts = @()
    
    foreach ($port in $ports) {
        $result = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        if ($result.TcpTestSucceeded) {
            $occupiedPorts += $port
            Write-Warning "端口 $port 已被占用"
        } else {
            Write-Success "端口 $port 可用"
        }
    }
    
    if ($occupiedPorts.Count -gt 0) {
        Write-Warning "以下端口已被占用: $($occupiedPorts -join ', ')"
        $choice = Read-Host "是否继续? (y/n)"
        if ($choice -ne 'y') {
            exit 1
        }
    }
    
    # 创建数据目录
    Write-Step 3 "创建数据目录"
    $dataDirs = @("data/skills", "data/reports", "data/analysis", "logs", "config", "security-config")
    
    foreach ($dir in $dataDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "创建目录: $dir"
        } else {
            Write-Info "目录已存在: $dir"
        }
    }
    
    # 生成环境文件
    Write-Step 4 "配置环境变量"
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
        if (Test-Path ".env") {
            Write-Success "已创建 .env 文件"
            Write-Info "请编辑 .env 文件配置环境变量"
        } else {
            Write-Warning "未找到 .env.example 文件"
        }
    } else {
        Write-Info ".env 文件已存在"
    }
    
    # 构建Docker镜像
    Write-Step 5 "构建Docker镜像"
    Write-Info "开始构建微服务镜像..."
    
    try {
        docker-compose build
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker镜像构建成功"
        } else {
            Write-Error "Docker镜像构建失败"
            exit 1
        }
    } catch {
        Write-Error "构建过程中出错: $_"
        exit 1
    }
    
    # 启动服务
    Write-Step 6 "启动企业级框架"
    Write-Info "启动所有微服务..."
    
    try {
        docker-compose up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Success "服务启动成功"
        } else {
            Write-Error "服务启动失败"
            exit 1
        }
    } catch {
        Write-Error "启动过程中出错: $_"
        exit 1
    }
    
    # 等待服务就绪
    Write-Step 7 "等待服务就绪"
    Write-Info "等待服务启动完成..."
    
    Start-Sleep -Seconds 10
    
    # 检查服务状态
    Write-Step 8 "验证服务状态"
    $services = @(
        @{Name="API网关"; Port=8000; Path="/"},
        @{Name="验证服务"; Port=8001; Path="/health"},
        @{Name="安全服务"; Port=8002; Path="/health"},
        @{Name="性能服务"; Port=8003; Path="/health"},
        @{Name="合规服务"; Port=8004; Path="/health"},
        @{Name="报告服务"; Port=8005; Path="/health"},
        @{Name="监控服务"; Port=8006; Path="/health"},
        @{Name="深度分析服务"; Port=8007; Path="/health"},
        @{Name="Web管理界面"; Port=3000; Path="/"}
    )
    
    $healthyServices = 0
    foreach ($service in $services) {
        $url = "http://localhost:$($service.Port)$($service.Path)"
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "$($service.Name) (端口 $($service.Port)): 健康"
                $healthyServices++
            } else {
                Write-Warning "$($service.Name) (端口 $($service.Port)): 状态 $($response.StatusCode)"
            }
        } catch {
            Write-Warning "$($service.Name) (端口 $($service.Port)): 不可达"
        }
    }
    
    # 部署完成
    Write-Step 9 "部署完成"
    Write-Color "================================================================" $Green
    Write-Color "    企业级审核框架部署完成!" $Green
    Write-Color "================================================================" $Green
    Write-Host ""
    
    Write-Color "服务状态: $healthyServices/$($services.Count) 个服务健康" $Cyan
    Write-Host ""
    
    Write-Color "访问地址:" $Cyan
    Write-Color "  Web管理界面: http://localhost:3000" $Cyan
    Write-Color "  API网关: http://localhost:8000" $Cyan
    Write-Color "  API文档: http://localhost:8000/docs" $Cyan
    Write-Host ""
    
    Write-Color "管理命令:" $Cyan
    Write-Color "  查看日志: docker-compose logs -f" $Cyan
    Write-Color "  停止服务: docker-compose down" $Cyan
    Write-Color "  重启服务: docker-compose restart" $Cyan
    Write-Color "  查看状态: docker-compose ps" $Cyan
    Write-Host ""
    
    Write-Color "下一步:" $Cyan
    Write-Color "  1. 访问Web管理界面配置系统" $Cyan
    Write-Color "  2. 生成API密钥用于生产环境" $Cyan
    Write-Color "  3. 配置SSL证书(生产环境)" $Cyan
    Write-Color "  4. 设置备份和监控" $Cyan
    Write-Host ""
    
    Write-Color "企业级审核框架 v3.1.0 已就绪!" $Green
}

# 执行主函数
try {
    Main
} catch {
    Write-Error "部署过程中出错: $_"
    exit 1
}