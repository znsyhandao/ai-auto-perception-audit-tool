"""
为企业级框架添加安全与生产特性
"""

import os
import json
from pathlib import Path

def add_security_features():
    """为所有服务添加安全特性"""
    print("ADDING SECURITY & PRODUCTION FEATURES")
    print("=" * 60)
    
    # 1. 创建环境配置文件
    print("\n[1] Creating environment configuration...")
    
    env_config = """# 企业级审核框架 - 环境配置
# 生产环境配置模板

# API配置
API_VERSION=3.1.0
API_HOST=0.0.0.0
API_PORT=8000

# 服务端口配置
VALIDATOR_PORT=8001
SECURITY_PORT=8002
PERFORMANCE_PORT=8003
COMPLIANCE_PORT=8004
REPORTING_PORT=8005
MONITORING_PORT=8006
DEEP_ANALYSIS_PORT=8007

# 安全配置
API_KEY_REQUIRED=true
DEFAULT_API_KEY=enterprise_audit_2026
RATE_LIMIT_PER_MINUTE=100
ENABLE_AUDIT_LOGGING=true
LOG_LEVEL=INFO

# 数据库配置 (生产环境使用)
# DATABASE_URL=postgresql://user:password@localhost:5432/audit_db
# REDIS_URL=redis://localhost:6379/0

# 使用内存存储 (开发环境)
USE_MEMORY_STORE=true

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
ALERT_EMAIL=admin@example.com

# 部署配置
DEPLOYMENT_ENV=production
MAX_WORKERS=4
TIMEOUT_SECONDS=30
"""
    
    env_file = Path(".env.example")
    env_file.write_text(env_config, encoding="utf-8")
    print(f"  Created: {env_file}")
    
    # 2. 创建API密钥管理文件
    print("\n[2] Creating API key management...")
    
    api_keys_config = {
        "api_keys": {
            "demo_key": {
                "name": "Demo API Key",
                "rate_limit": 100,
                "permissions": ["read", "analyze"],
                "created": "2026-03-30",
                "expires": "2026-12-31"
            },
            "enterprise_key": {
                "name": "Enterprise API Key",
                "rate_limit": 1000,
                "permissions": ["read", "analyze", "admin"],
                "created": "2026-03-30",
                "expires": "2027-03-30"
            }
        },
        "security": {
            "require_api_key": True,
            "rate_limiting_enabled": True,
            "audit_logging_enabled": True,
            "cors_allowed_origins": ["http://localhost:3000", "http://localhost:8000"]
        }
    }
    
    api_keys_file = Path("api_keys_config.json")
    api_keys_file.write_text(json.dumps(api_keys_config, indent=2), encoding="utf-8")
    print(f"  Created: {api_keys_file}")
    
    # 3. 为每个服务添加安全中间件
    print("\n[3] Adding security middleware to services...")
    
    security_middleware = '''"""
安全中间件 - API密钥验证和速率限制
"""

import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# API密钥验证
class APIKeyValidator:
    def __init__(self):
        self.api_keys = {
            "demo_key": {"rate_limit": 100, "used": 0, "last_reset": time.time()},
            "enterprise_key": {"rate_limit": 1000, "used": 0, "last_reset": time.time()}
        }
        self.rate_limit_window = 60  # 1分钟
    
    def verify_api_key(self, api_key: Optional[str] = None) -> bool:
        """验证API密钥"""
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")
        
        if api_key not in self.api_keys:
            raise HTTPException(status_code=403, detail="Invalid API key")
        
        # 检查速率限制
        key_info = self.api_keys[api_key]
        current_time = time.time()
        
        # 重置计数器（如果超过时间窗口）
        if current_time - key_info["last_reset"] > self.rate_limit_window:
            key_info["used"] = 0
            key_info["last_reset"] = current_time
        
        if key_info["used"] >= key_info["rate_limit"]:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        key_info["used"] += 1
        return True
    
    def get_api_key_info(self, api_key: str) -> Dict:
        """获取API密钥信息"""
        return self.api_keys.get(api_key, {})

# 审计日志
class AuditLogger:
    def __init__(self):
        self.logs = []
    
    def log_request(self, request: Request, api_key: Optional[str] = None, user_agent: Optional[str] = None):
        """记录请求日志"""
        log_entry = {
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "api_key_used": api_key is not None,
            "user_agent": user_agent or request.headers.get("user-agent", "unknown")
        }
        self.logs.append(log_entry)
        
        # 保持日志大小
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        return self.logs[-limit:]

# 配置安全中间件
def setup_security_middleware(app: FastAPI):
    """设置安全中间件"""
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 可信主机
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "::1"]
    )
    
    # 创建验证器和日志器实例
    api_validator = APIKeyValidator()
    audit_logger = AuditLogger()
    
    # 中间件：记录所有请求
    @app.middleware("http")
    async def audit_middleware(request: Request, call_next):
        # 记录请求
        api_key = request.headers.get("x-api-key")
        user_agent = request.headers.get("user-agent")
        audit_logger.log_request(request, api_key, user_agent)
        
        # 验证API密钥（如果需要）
        if request.url.path not in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            try:
                api_validator.verify_api_key(api_key)
            except HTTPException:
                # 公开端点不需要API密钥
                if not request.url.path.startswith("/public/"):
                    raise
        
        response = await call_next(request)
        return response
    
    # 添加依赖项
    app.state.api_validator = api_validator
    app.state.audit_logger = audit_logger
    
    return app

# 依赖项
def get_api_validator(request: Request):
    """获取API验证器"""
    return request.app.state.api_validator

def get_audit_logger(request: Request):
    """获取审计日志器"""
    return request.app.state.audit_logger
'''
    
    security_file = Path("security_middleware.py")
    security_file.write_text(security_middleware, encoding="utf-8")
    print(f"  Created: {security_file}")
    
    # 4. 创建生产部署配置
    print("\n[4] Creating production deployment configuration...")
    
    docker_compose = '''version: '3.8'

services:
  # API网关
  api-gateway:
    build: ./microservices/api-gateway
    ports:
      - "8000:8000"
    environment:
      - VALIDATOR_SERVICE_URL=http://validator:8001
      - SECURITY_SERVICE_URL=http://security:8002
      - PERFORMANCE_SERVICE_URL=http://performance:8003
      - COMPLIANCE_SERVICE_URL=http://compliance:8004
      - REPORTING_SERVICE_URL=http://reporting:8005
      - MONITORING_SERVICE_URL=http://monitoring:8006
      - DEEP_ANALYSIS_SERVICE_URL=http://deep-analysis:8007
    depends_on:
      - validator
      - security
      - performance
      - compliance
      - reporting
      - monitoring
      - deep-analysis
    networks:
      - audit-network

  # 验证服务
  validator:
    build: ./microservices/validator-service
    ports:
      - "8001:8001"
    environment:
      - PORT=8001
      - USE_MEMORY_STORE=true
    networks:
      - audit-network

  # 安全服务
  security:
    build: ./microservices/security-service
    ports:
      - "8002:8002"
    environment:
      - PORT=8002
      - USE_MEMORY_STORE=true
    networks:
      - audit-network

  # 性能服务
  performance:
    build: ./microservices/performance-service
    ports:
      - "8003:8003"
    environment:
      - PORT=8003
      - USE_MEMORY_STORE=true
    networks:
      - audit-network

  # 合规服务
  compliance:
    build: ./microservices/compliance-service
    ports:
      - "8004:8004"
    environment:
      - PORT=8004
      - USE_MEMORY_STORE=true
    networks:
      - audit-network

  # 报告服务
  reporting:
    build: ./microservices/reporting-service
    ports:
      - "8005:8005"
    environment:
      - PORT=8005
      - USE_MEMORY_STORE=true
    networks:
      - audit-network

  # 监控服务
  monitoring:
    build: ./microservices/monitoring-service
    ports:
      - "8006:8006"
    environment:
      - PORT=8006
      - USE_MEMORY_STORE=true
    networks:
      - audit-network

  # 深度分析服务
  deep-analysis:
    build: ./microservices/deep-analysis-service
    ports:
      - "8007:8007"
    environment:
      - PORT=8007
      - USE_MEMORY_STORE=true
    networks:
      - audit-network

  # PostgreSQL数据库 (生产环境)
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: audit_db
  #     POSTGRES_USER: audit_user
  #     POSTGRES_PASSWORD: audit_password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"
  #   networks:
  #     - audit-network

  # Redis缓存 (生产环境)
  # redis:
  #   image: redis:7-alpine
  #   ports:
  #     - "6379:6379"
  #   networks:
  #     - audit-network

networks:
  audit-network:
    driver: bridge

volumes:
  postgres_data:
'''
    
    compose_file = Path("docker-compose.yml")
    compose_file.write_text(docker_compose, encoding="utf-8")
    print(f"  Created: {compose_file}")
    
    # 5. 创建一键部署脚本
    print("\n[5] Creating one-click deployment script...")
    
    deploy_script = '''#!/bin/bash
# 企业级审核框架 - 一键部署脚本

set -e

echo "=========================================="
echo "企业级审核框架部署脚本"
echo "=========================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装"
    echo "请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装"
    echo "请先安装Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker和Docker Compose已安装"

# 检查环境文件
if [ ! -f ".env" ]; then
    echo "创建环境配置文件..."
    cp .env.example .env
    echo "✓ 环境配置文件已创建"
    echo "请编辑 .env 文件配置您的设置"
fi

# 构建和启动服务
echo "构建Docker镜像..."
docker-compose build

echo "启动服务..."
docker-compose up -d

echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
services=("api-gateway" "validator" "security" "performance" "compliance" "reporting" "monitoring" "deep-analysis")

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "${service}.*Up"; then
        echo "  ✓ ${service}: 运行中"
    else
        echo "  ✗ ${service}: 未运行"
    fi
done

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "服务访问地址:"
echo "  API网关:      http://localhost:8000"
echo "  验证服务:     http://localhost:8001"
echo "  安全服务:     http://localhost:8002"
echo "  性能服务:     http://localhost:8003"
echo "  合规服务:     http://localhost:8004"
echo "  报告服务:     http://localhost:8005"
echo "  监控服务:     http://localhost:8006"
echo "  深度分析服务: http://localhost:8007"
echo ""
echo "API文档:"
echo "  Swagger UI:   http://localhost:8000/docs"
echo "  ReDoc:        http://localhost:8000/redoc"
echo ""
echo "管理命令:"
echo "  查看日志:     docker-compose logs -f"
echo "  停止服务:     docker-compose down"
echo "  重启服务:     docker-compose restart"
echo "  更新服务:     docker-compose pull && docker-compose up -d"
echo ""
echo "默认API密钥: demo_key"
echo "=========================================="
'''
    
    deploy_file = Path("deploy.sh")
    deploy_file.write_text(deploy_script, encoding="utf-8")
    
    # Windows批处理版本
    deploy_bat = '''@echo off
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
'''
    
    deploy_bat_file = Path("deploy.bat")
    deploy_bat_file.write_text(deploy_bat, encoding="utf-8")
    print(f"  Created: {deploy_file