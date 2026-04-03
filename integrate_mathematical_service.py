"""
集成数学审核服务到企业级框架 - 简化版本
"""

import os
import json
from pathlib import Path

def main():
    """主集成函数"""
    print("INTEGRATING MATHEMATICAL AUDIT SERVICE")
    print("=" * 70)
    
    print("\n1. Checking enterprise framework structure...")
    
    # 检查微服务目录
    microservices_dir = Path("microservices")
    if not microservices_dir.exists():
        print("   ERROR: microservices directory not found")
        return False
    
    print(f"   Found {len(list(microservices_dir.iterdir()))} microservices")
    
    # 检查数学服务是否存在
    math_service_dir = microservices_dir / "mathematical-audit-service"
    if not math_service_dir.exists():
        print("   ERROR: mathematical-audit-service not found")
        return False
    
    print("   Mathematical audit service found")
    
    print("\n2. Creating integration configuration...")
    
    # 创建服务注册表
    registry_dir = microservices_dir / "config"
    registry_dir.mkdir(exist_ok=True)
    
    registry = {
        "mathematical-audit-service": {
            "name": "Mathematical Audit Service",
            "version": "4.0.0",
            "port": 8010,
            "endpoints": {
                "health": "/health",
                "audit": "/audit",
                "docs": "/docs"
            },
            "mathematical_methods": [
                "maclaurin_series",
                "taylor_series",
                "fourier_transform",
                "matrix_decomposition",
                "mathematical_proof"
            ]
        }
    }
    
    registry_file = registry_dir / "mathematical-service.json"
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"   Created service registry: {registry_file}")
    
    print("\n3. Creating Docker Compose integration...")
    
    # 创建docker-compose集成片段
    compose_snippet = """
  # Mathematical Audit Service
  mathematical-audit-service:
    build: ./microservices/mathematical-audit-service
    ports:
      - "8010:8010"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8010/health', timeout=2)"]
      interval: 30s
      timeout: 3s
      retries: 3
    networks:
      - audit-network
"""
    
    compose_file = Path("docker-compose.mathematical-integration.yml")
    with open(compose_file, 'w', encoding='utf-8') as f:
        f.write(f"""version: '3.8'

services:{compose_snippet}

networks:
  audit-network:
    driver: bridge
""")
    
    print(f"   Created Docker Compose config: {compose_file}")
    
    print("\n4. Creating integration test...")
    
    test_content = '''"""
数学服务集成测试
"""

import requests

def test_mathematical_service():
    """测试数学服务集成"""
    print("Testing Mathematical Service Integration")
    print("=" * 60)
    
    # 直接测试数学服务
    print("1. Direct service test...")
    try:
        response = requests.get("http://localhost:8010/health", timeout=5)
        if response.status_code == 200:
            print(f"   Service healthy: {response.json().get('status')}")
            print("   PASS")
        else:
            print(f"   FAIL: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # 测试数学审核
    print("\\n2. Mathematical audit test...")
    test_data = {
        "skill_id": "integration-test",
        "skill_path": "test/path",
        "audit_types": ["maclaurin", "t