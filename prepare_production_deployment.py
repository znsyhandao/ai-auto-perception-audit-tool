"""
生产部署准备 - 并行执行
"""

import os
import json
import datetime
from pathlib import Path

def create_docker_config():
    """创建Docker配置"""
    print("1. Creating Docker configuration...")
    
    dockerfile_content = """# Mathematical Audit Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY microservices/mathematical-audit-service/requirements-service.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-service.txt

# 复制应用代码
COPY microservices/mathematical-audit-service/ /app/

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8010

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8010/health', timeout=2)"

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
"""
    
    docker_compose_content = """# Mathematical Audit Service Docker Compose
version: '3.8'

services:
  mathematical-audit-service:
    build:
      context: .
      dockerfile: Dockerfile.mathematical
    ports:
      - "8010:8010"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8010/health', timeout=2)"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    networks:
      - audit-network

networks:
  audit-network:
    driver: bridge
"""
    
    # 保存文件
    with open('Dockerfile.mathematical', 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    with open('docker-compose.mathematical.yml', 'w', encoding='utf-8') as f:
        f.write(docker_compose_content)
    
    print("   Created: Dockerfile.mathematical")
    print("   Created: docker-compose.mathematical.yml")
    return True

def create_deployment_scripts():
    """创建部署脚本"""
    print("\n2. Creating deployment scripts...")
    
    # Windows部署脚本
    deploy_windows = """@echo off
REM Mathematical Audit Service Deployment Script (Windows)
echo ========================================
echo MATHEMATICAL AUDIT SERVICE DEPLOYMENT
echo ========================================

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    exit /b 1
)

REM 构建镜像
echo Building Docker image...
docker build -f Dockerfile.mathematical -t mathematical-audit-service:latest .

if errorlevel 1 (
    echo ERROR: Docker build failed
    exit /b 1
)

REM 停止现有容器
echo Stopping existing containers...
docker-compose -f docker-compose.mathematical.yml down

REM 启动服务
echo Starting mathematical audit service...
docker-compose -f docker-compose.mathematical.yml up -d

REM 等待服务启动
echo Waiting for service to start...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo Checking service health...
curl -s http://localhost:8010/health >nul
if errorlevel 1 (
    echo ERROR: Service health check failed
    exit /b 1
)

echo ========================================
echo DEPLOYMENT SUCCESSFUL!
echo Service is running on: http://localhost:8010
echo Health check: http://localhost:8010/health
echo API docs: http://localhost:8010/docs
echo ========================================
"""
    
    # Linux部署脚本
    deploy_linux = """#!/bin/bash
# Mathematical Audit Service Deployment Script (Linux)
echo "========================================"
echo "MATHEMATICAL AUDIT SERVICE DEPLOYMENT"
echo "========================================"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker: sudo apt-get install docker.io"
    exit 1
fi

# 构建镜像
echo "Building Docker image..."
docker build -f Dockerfile.mathematical -t mathematical-audit-service:latest .

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed"
    exit 1
fi

# 停止现有容器
echo "Stopping existing containers..."
docker-compose -f docker-compose.mathematical.yml down

# 启动服务
echo "Starting mathematical audit service..."
docker-compose -f docker-compose.mathematical.yml up -d

# 等待服务启动
echo "Waiting for service to start..."
sleep 10

# 检查服务状态
echo "Checking service health..."
if curl -s http://localhost:8010/health > /dev/null; then
    echo "========================================"
    echo "DEPLOYMENT SUCCESSFUL!"
    echo "Service is running on: http://localhost:8010"
    echo "Health check: http://localhost:8010/health"
    echo "API docs: http://localhost:8010/docs"
    echo "========================================"
else
    echo "ERROR: Service health check failed"
    exit 1
fi
"""
    
    # 保存脚本
    with open('deploy_mathematical_windows.bat', 'w', encoding='utf-8') as f:
        f.write(deploy_windows)
    
    with open('deploy_mathematical_linux.sh', 'w', encoding='utf-8', newline='\n') as f:
        f.write(deploy_linux)
    
    # 使Linux脚本可执行
    os.chmod('deploy_mathematical_linux.sh', 0o755)
    
    print("   Created: deploy_mathematical_windows.bat")
    print("   Created: deploy_mathematical_linux.sh")
    return True

def create_monitoring_config():
    """创建监控配置"""
    print("\n3. Creating monitoring configuration...")
    
    prometheus_config = """# Prometheus configuration for Mathematical Audit Service
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'mathematical-audit-service'
    static_configs:
      - targets: ['mathematical-audit-service:8010']
    metrics_path: '/metrics'
    scrape_interval: 30s
"""
    
    grafana_dashboard = {
        "dashboard": {
            "title": "Mathematical Audit Service Dashboard",
            "panels": [
                {
                    "title": "Service Health",
                    "type": "stat",
                    "targets": [{"expr": "up{job='mathematical-audit-service'}"}]
                },
                {
                    "title": "Request Rate",
                    "type": "graph", 
                    "targets": [{"expr": "rate(http_requests_total[5m])"}]
                },
                {
                    "title": "Response Time",
                    "type": "graph",
                    "targets": [{"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"}]
                }
            ]
        }
    }
    
    # 保存配置
    with open('prometheus.mathematical.yml', 'w', encoding='utf-8') as f:
        f.write(prometheus_config)
    
    with open('grafana_dashboard_mathematical.json', 'w', encoding='utf-8') as f:
        json.dump(grafana_dashboard, f, indent=2)
    
    print("   Created: prometheus.mathematical.yml")
    print("   Created: grafana_dashboard_mathematical.json")
    return True

def create_documentation():
    """创建文档"""
    print("\n4. Creating documentation...")
    
    readme_content = """# Mathematical Audit Service

基于数学定理的AI引擎审核服务，使用麦克劳林级数、泰勒级数、傅里叶变换等数学方法进行代码审核。

## Features

- **数学定理驱动**: 麦克劳林级数、泰勒级数、傅里叶变换、矩阵分解、数学证明
- **完整证书系统**: 每个审核结果都有数学证书
- **生产就绪**: Docker容器化，健康检查，监控集成
- **REST API**: OpenAPI文档，标准化接口

## Quick Start

### Using Docker Compose

```bash
# 启动服务
docker-compose -f docker-compose.mathematical.yml up -d

# 检查服务状态
curl http://localhost:8010/health
```

### Manual Deployment

```bash
# 构建镜像
docker build -f Dockerfile.mathematical -t mathematical-audit-service:latest .

# 运行容器
docker run -p 8010:8010 mathematical-audit-service:latest
```

## API Documentation

服务启动后访问: http://localhost:8010/docs

### Endpoints

- `GET /health` - 健康检查
- `POST /audit` - 运行数学审核
  ```json
  {
    "skill_id": "your-skill-id",
    "skill_path": "/path/to/skill",
    "audit_types": ["maclaurin", "taylor", "fourier", "matrix", "proof"],
    "mathematical_depth": 5
  }
  ```

## Mathematical Methods

### 1. Maclaurin Series Analysis
- **定理**: f(x) = Σ [f^(n)(0) * x^n / n!]
- **应用**: 代码复杂度特征工程
- **输出**: 级数展开，收敛率，近似值

### 2. Taylor Series Complexity
- **定理**: T(n) = Σ [T^(k)(a) * (n-a)^k / k!]
- **应用**: 算法性能分析
- **输出**: 复杂度项，大O表示法

### 3. Fourier Transform Pattern
- **定理**: F(ω) = ∫ f(t) * e^(-iωt) dt
- **应用**: 代码结构模式识别
- **输出**: 频率分量，主导模式

### 4. Matrix Decomposition
- **定理**: A = U * Σ * V^T (SVD)
- **应用**: 模块依赖分析
- **输出**: 特征值，依赖密度，矩阵秩

### 5. Mathematical Proof
- **定理**: P₁ ∧ P₂ ∧ ... ∧ Pₙ → Q
- **应用**: 代码属性验证
- **输出**: 证明步骤，置信度，有效性

## Monitoring

### Prometheus Metrics
- `http_requests_total` - 总请求数
- `http_request_duration_seconds` - 请求耗时
- `mathematical_audit_score` - 审核分数
- `certificate_confidence` - 证书置信度

### Health Checks
- 服务状态: `GET /health`
- 数学引擎状态: 包含在健康检查响应中
- 自动重启: Docker restart策略

## Configuration

### Environment Variables
- `LOG_LEVEL` - 日志级别 (INFO, DEBUG, WARNING, ERROR)
- `PORT` - 服务端口 (默认: 8010)
- `MATHEMATICAL_DEPTH` - 数学分析深度 (默认: 5)

### Volume Mounts
- `/app/logs` - 日志目录
- `/app/certificates` - 证书存储 (可选)

## Development

### Local Development
```bash
# 安装依赖
pip install -r microservices/mathematical-audit-service/requirements-service.txt

# 启动服务
cd microservices/mathematical-audit-service
python -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

### Testing
```bash
# 运行测试
python test_mathematical_service.py

# 验证数学方法
python validate_mathematical_methods.py
```

## Production Deployment

### Requirements
- Docker 20.10+
- Docker Compose 2.0+
- 1GB RAM minimum
- 2GB disk space

### Deployment Steps
1. 复制部署文件到服务器
2. 运行部署脚本: `./deploy_mathematical_linux.sh`
3. 验证部署: `curl http://localhost:8010/health`
4. 配置监控 (可选)

## Troubleshooting

### Common Issues

1. **服务无法启动**
   - 检查Docker是否运行: `docker ps`
   - 检查端口占用: `netstat -tulpn | grep 8010`
   - 查看日志: `docker logs mathematical-audit-service`

2. **健康检查失败**
   - 检查数学引擎加载: 查看服务日志
   - 验证依赖安装: 确保所有Python包已安装
   - 检查文件权限: 确保服务有读写权限

3. **审核失败**
   - 检查输入数据格式
   - 验证技能路径是否存在
   - 查看审核器错误日志

### Logs
日志位置: `/app/logs/mathematical_audit.log`
日志级别: 通过`LOG_LEVEL`环境变量配置

## License

MIT License

## Support

- 文档: 查看本README
- 问题: 创建GitHub Issue
- 邮件: support@example.com
"""
    
    api_docs = {
        "openapi": "3.0.0",
        "info": {
            "title": "Mathematical Audit Service API",
            "version": "4.0.0",
            "description": "基于数学定理的代码审核服务"
        },
        "paths": {
            "/health": {
                "get": {
                    "summary": "健康检查",
                    "responses": {
                        "200": {
                            "description": "服务健康",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "service": {"type": "string"},
                                            "version": {"type": "string"},
                                            "mathematical_engine": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/audit": {
                "post": {
                    "summary": "运行数学审核",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "skill_id": {"type": "string"},
                                        "skill_path": {"type": "string"},
                                        "audit_types": {"type": "array", "items": {"type": "string"}},
                                        "mathematical_depth": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "审核成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "overall_mathematical_score": {"type": "number"},
                                            "mathematical_certificates": {"type": "array"},
                                            "audit_time": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # 保存文档
    with open('README_MATHEMATICAL_SERVICE.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    with open('api_docs_mathematical.json', 'w', encoding='utf-8') as f:
        json.dump(api_docs, f, indent=2)
    
    print("   Created: README_MATHEMATICAL_SERVICE.md")
    print("   Created: api_docs_mathematical.json")
    return True

def create_production_checklist():
    """创建生产检查清单"""
    print("\n5. Creating production checklist...")
    
    checklist = {
        "checklist_id": f"PRODUCTION_CHECKLIST_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.datetime.now().isoformat(),
        "checks": [
            {
                "category": "Infrastructure",
                "items": [
                    {"item": "Docker installed and running", "status": "pending", "required": True},
                    {"item": "Port 8010 available", "status": "pending", "required": True},
                    {"item": "Minimum 1GB RAM available", "status": "pending", "required": True},
                    {"item": "Network connectivity", "status": "pending", "required": True}
                ]
            },
            {
                "category": "Service",
                "items": [
                    {"item": "Service starts successfully", "status": "pending", "required": True},
                    {"item": "Health check passes", "status": "pending", "required": True},
                    {"item": "Mathematical engine loads", "status": "pending", "required": True},
                    {"item": "API endpoints respond", "status": "pending", "required": True}
                ]
            },
            {
                "category": "Functionality",
                "items": [
                    {"item": "Maclaurin analysis works", "status": "pending", "required": True},
                    {"item": "Taylor analysis works", "status": "pending", "required": True},
                    {"item": "Fourier analysis works", "status": "pending", "