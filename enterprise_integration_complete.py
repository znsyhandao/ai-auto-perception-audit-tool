"""
企业级框架集成 - 完整配置
"""

import os
import json
from pathlib import Path

def create_integration_files():
    """创建集成文件"""
    print("CREATING ENTERPRISE INTEGRATION FILES")
    print("=" * 70)
    
    # 1. 创建服务发现配置
    print("\n1. Creating service discovery configuration...")
    
    discovery_config = {
        "services": {
            "mathematical-audit-service": {
                "name": "Mathematical Audit Service",
                "description": "Mathematical theorem-based code audit with AI engine",
                "version": "4.0.0",
                "port": 8010,
                "protocol": "http",
                "health_endpoint": "/health",
                "api_endpoint": "/audit",
                "documentation": "/docs",
                "mathematical_capabilities": [
                    {
                        "method": "maclaurin_series",
                        "description": "Code complexity analysis using Maclaurin series expansion",
                        "theorem": "f(x) = Σ [f^(n)(0) * x^n / n!]"
                    },
                    {
                        "method": "taylor_series",
                        "description": "Algorithm performance analysis using Taylor series",
                        "theorem": "T(n) = Σ [T^(k)(a) * (n-a)^k / k!]"
                    },
                    {
                        "method": "fourier_transform",
                        "description": "Code structure pattern recognition",
                        "theorem": "F(ω) = ∫ f(t) * e^(-iωt) dt"
                    },
                    {
                        "method": "matrix_decomposition",
                        "description": "Module dependency analysis",
                        "theorem": "A = U * Σ * V^T (SVD)"
                    },
                    {
                        "method": "mathematical_proof",
                        "description": "Code property verification",
                        "theorem": "P₁ ∧ P₂ ∧ ... ∧ Pₙ → Q"
                    }
                ],
                "certificate_system": {
                    "enabled": True,
                    "certificate_types": 5,
                    "confidence_scoring": True,
                    "validity_verification": True
                }
            }
        },
        "integration_status": "ready",
        "integration_date": "2026-03-31",
        "gateway_endpoints": {
            "mathematical_health": "/api/v1/mathematical/health",
            "mathematical_audit": "/api/v1/mathematical/audit",
            "mathematical_docs": "/api/v1/mathematical/docs"
        }
    }
    
    config_dir = Path("enterprise_integration")
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "service_discovery.json", 'w', encoding='utf-8') as f:
        json.dump(discovery_config, f, indent=2)
    
    print("   Created: enterprise_integration/service_discovery.json")
    
    # 2. 创建API网关路由配置
    print("\n2. Creating API gateway routing configuration...")
    
    gateway_routes = """# Mathematical Audit Service Routes for API Gateway

# Health check endpoint
- path: /api/v1/mathematical/health
  target: http://mathematical-audit-service:8010/health
  methods: [GET]
  description: "Mathematical audit service health status"
  timeout: 5000
  retries: 3

# Mathematical audit endpoint
- path: /api/v1/mathematical/audit
  target: http://mathematical-audit-service:8010/audit
  methods: [POST]
  description: "Run mathematical theorem-based code audit"
  timeout: 30000
  retries: 2
  request_transform:
    add_headers:
      X-Mathematical-Service: "true"
      X-Audit-Type: "mathematical"

# API documentation endpoint
- path: /api/v1/mathematical/docs
  target: http://mathematical-audit-service:8010/docs
  methods: [GET]
  description: "Mathematical audit API documentation"
  timeout: 10000

# Combined audit endpoint (with mathematical integration)
- path: /api/v1/audit/complete
  target: http://validator-service:8001/audit/complete
  methods: [POST]
  description: "Complete audit including mathematical analysis"
  timeout: 60000
  pipeline:
    - security-service:8002/audit
    - mathematical-audit-service:8010/audit
    - performance-service:8003/audit
    - reporting-service:8005/generate
"""
    
    with open(config_dir / "gateway_routes.yaml", 'w', encoding='utf-8') as f:
        f.write(gateway_routes)
    
    print("   Created: enterprise_integration/gateway_routes.yaml")
    
    # 3. 创建Docker Compose集成
    print("\n3. Creating Docker Compose integration...")
    
    docker_compose = """version: '3.8'

services:
  # Mathematical Audit Service
  mathematical-audit-service:
    build:
      context: ./microservices/mathematical-audit-service
      dockerfile: Dockerfile
    image: mathematical-audit:4.0.0
    container_name: mathematical-audit-service
    ports:
      - "8010:8010"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
      - SERVICE_NAME=mathematical-audit
      - SERVICE_VERSION=4.0.0
    volumes:
      - ./logs/mathematical:/app/logs
      - ./certificates:/app/certificates
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8010/health', timeout=2)"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    networks:
      - enterprise-audit-network

  # API Gateway (with mathematical routes)
  api-gateway:
    build:
      context: ./microservices/api-gateway-enhanced
      dockerfile: Dockerfile
    image: api-gateway:latest
    container_name: api-gateway
    ports:
      - "8080:8080"
    depends_on:
      mathematical-audit-service:
        condition: service_healthy
    environment:
      - NODE_ENV=production
      - MATHEMATICAL_SERVICE_URL=http://mathematical-audit-service:8010
    volumes:
      - ./enterprise_integration/gateway_routes.yaml:/app/config/routes.yaml:ro
    restart: unless-stopped
    networks:
      - enterprise-audit-network

networks:
  enterprise-audit-network:
    driver: bridge
    name: enterprise-audit-network
"""
    
    with open(config_dir / "docker-compose.integration.yml", 'w', encoding='utf-8') as f:
        f.write(docker_compose)
    
    print("   Created: enterprise_integration/docker-compose.integration.yml")
    
    # 4. 创建集成测试
    print("\n4. Creating integration tests...")
    
    integration_test = '''"""
企业级框架集成测试 - 数学审核服务
"""

import requests
import json
import time

class MathematicalServiceIntegrationTest:
    """数学服务集成测试类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8010"
        self.gateway_url = "http://localhost:8080"
    
    def test_direct_service(self):
        """测试直接服务访问"""
        print("1. Testing direct service access...")
        
        endpoints = [
            ("Health check", f"{self.base_url}/health", "GET"),
            ("API documentation", f"{self.base_url}/docs", "GET")
        ]
        
        for name, url, method in endpoints:
            print(f"   Testing {name}...")
            try:
                if method == "GET":
                    response = requests.get(url, timeout=5)
                else:
                    response = requests.post(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"     PASS: HTTP 200")
                else:
                    print(f"     FAIL: HTTP {response.status_code}")
                    return False
            except Exception as e:
                print(f"     ERROR: {e}")
                return False
        
        return True
    
    def test_mathematical_audit(self):
        """测试数学审核功能"""
        print("\\n2. Testing mathematical audit functionality...")
        
        test_cases = [
            {
                "name": "Maclaurin analysis only",
                "data": {
                    "skill_id": "test-maclaurin",
                    "skill_path": "test/path",
                    "audit_types": ["maclaurin"],
                    "mathematical_depth": 3
                }
            },
            {
                "name": "Full mathematical audit",
                "data": {
                    "skill_id": "test-full",
                    "skill_path": "test/path",
                    "audit_types": ["maclaurin", "taylor", "fourier", "matrix", "proof"],
                    "mathematical_depth": 5
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}...")
            
            try:
                response = requests.post(
                    f"{self.base_url}/audit",
                    json=test_case["data"],
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    score = result.get("overall_mathematical_score", 0)
                    certs = len(result.get("mathematical_certificates", []))
                    
                    print(f"     PASS: Score={score}, Certificates={certs}")
                else:
                    print(f"     FAIL: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"     ERROR: {e}")
                return False
        
        return True
    
    def test_certificate_system(self):
        """测试证书系统"""
        print("\\n3. Testing certificate system...")
        
        try:
            response = requests.post(
                f"{self.base_url}/audit",
                json={
                    "skill_id": "cert-test",
                    "skill_path": "test/path",
                    "audit_types": ["maclaurin", "proof"],
                    "mathematical_depth": 4
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                certificates = result.get("mathematical_certificates", [])
                
                if certificates:
                    print(f"   Certificates generated: {len(certificates)}")
                    
                    # 检查证书质量
                    valid_certs = [c for c in certificates if c.get("validity") == "valid"]
                    avg_confidence = sum(c.get("confidence", 0) for c in certificates) / len(certificates)
                    
                    print(f"   Valid certificates: {len(valid_certs)}/{len(certificates)}")
                    print(f"   Average confidence: {avg_confidence:.3f}")
                    
                    if len(valid_certs) > 0 and avg_confidence > 0.5:
                        print("   PASS: Certificate system working")
                        return True
                    else:
                        print("   FAIL: Certificate quality too low")
                        return False
                else:
                    print("   FAIL: No certificates generated")
                    return False
            else:
                print(f"   FAIL: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("ENTERPRISE INTEGRATION TEST - MATHEMATICAL AUDIT SERVICE")
        print("=" * 70)
        
        tests = [
            ("Direct service access", self.test_direct_service),
            ("Mathematical audit functionality", self.test_mathematical_audit),
            ("Certificate system", self.test_certificate_system)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\\n{test_name}...")
            if test_func():
                print("  PASS")
                results.append(True)
            else:
                print("  FAIL")
                results.append(False)
        
        passed = sum(results)
        total = len(results)
        
        print(f"\\nTest results: {passed}/{total} passed")
        
        if passed == total:
            print("\\n" + "=" * 70)
            print("INTEGRATION TEST PASSED")
            print("Mathematical audit service is ready for enterprise use.")
            print("=" * 70)
            return True
        else:
            print("\\n" + "=" * 70)
            print("INTEGRATION TEST FAILED")
            print("=" * 70)
            return False

def main():
    """主测试函数"""
    tester = MathematicalServiceIntegrationTest()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
'''
    
    with open(config_dir / "integration_test.py", 'w', encoding='utf-8') as f:
        f.write(integration_test)
    
    print("   Created: enterprise_integration/integration_test.py")
    
    # 5. 创建部署脚本
    print("\n5. Creating deployment script...")
    
    deploy_script = '''@echo off
REM Enterprise Integration Deployment Script
echo ========================================
echo ENTERPRISE INTEGRATION DEPLOYMENT
echo Mathematical Audit Service
echo ========================================

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found
    echo Please install Docker Desktop
    exit /b 1
)

REM Build mathematical audit service
echo Building Mathematical Audit Service...
docker build -t mathematical-audit:4.0.0 -f microservices/mathematical-audit-service/Dockerfile microservices/mathematical-audit-service

if errorlevel 1 (
    echo ERROR: Docker build failed
    exit /b 1
)

REM Build API gateway
echo Building API Gateway...
docker build -t api-gateway:latest -f microservices/api-gateway-enhanced/Dockerfile microservices/api-gateway-enhanced

if errorlevel 1 (
    echo ERROR: Gateway build failed
    exit /b 1
)

REM Stop existing containers
echo Stopping existing containers...
docker-compose -f enterprise_integration/docker-compose.integration.yml down

REM Start services
echo Starting enterprise services...
docker-compose -f enterprise_integration/docker-compose.integration.yml up -d

REM Wait for services to start
echo Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check service health
echo Checking mathematical service health...
curl -s http://localhost:8010/health >nul
if errorlevel 1 (
    echo ERROR: Mathematical service health check failed
    exit /b 1
)

echo Checking API gateway...
curl -s http://localhost:8080/api/v1/mathematical/health >nul
if errorlevel 1 (
    echo ERROR: Gateway health check failed
    exit /b 1
)

echo ========================================
echo DEPLOYMENT SUCCESSFUL!
echo ========================================
echo Services:
echo   Mathematical Audit: http://localhost:8010
echo   API Gateway:        http://localhost:8080
echo ========================================
echo Test endpoints:
echo   Direct health:      http://localhost:8010/health
echo   Gateway health:     http://localhost:8080/api/v1/mathematical/health
echo   API docs:           http://localhost:8010/docs
echo ========================================
'''
    
    with open(config_dir / "deploy_enterprise.bat", 'w', encoding='utf-8') as f:
        f.write(deploy_script)
    
    print("   Created: enterprise_integration/deploy_enterprise.bat")
    
    # 6. 创建集成报告
    print("\n6. Creating integration report...")
    
    integration_report = {
        "integration_id": f"INTEGRATION_{int(time.time())}",
        "service": "mathematical-audit-service",
        "version": "4.0.0",
        "integration_date": "2026-03-31",
        "status": "ready",
        "components_integrated": [
            "Service discovery configuration",
            "API gateway routing",
            "Docker Compose deployment",
            "Integration tests",
            "Deployment scripts"
        ],
        "endpoints": {
            "direct_service": "http://localhost:8010",
            "api_gateway": "http://localhost:8080",
            "health_check": "http://localhost:8010/health",
            "gateway_health": "http://localhost:8080/api/v1/mathematical/health"
        },
        "mathematical_capabilities": [
            "maclaurin_series",
            "taylor_series",
            "fourier_transform",
            "matrix_decomposition",
            "mathematical_proof"
        ],
        "certificate_system": {
            "enabled": True,
            "certificate_types": 5,
            "confidence_scoring": True,
            "validity_verification": True
        },
        "next_steps": [
            "Run integration tests: python enterprise_integration/integration_test.py",
            "Deploy to test environment: enterprise_integration/deploy_enterprise.bat",
            "Monitor service health and performance",
            "Extend integration with other enterprise services"
        ]
    }
    
    with open(config_dir / "integration_report.json", 'w', encoding='utf-8') as f:
        json.dump(integration_report, f, indent=2)
    
    print("   Created: enterprise_integration/integration_report.json")
    
    print("\n" + "=" * 70)
    print("ENTERPRISE INTEGRATION FILES CREATED SUCCESSFULLY")
    print("=" * 70)
    print("\nFiles created in 'enterprise_integration/' directory:")
    print("  - service_discovery.json