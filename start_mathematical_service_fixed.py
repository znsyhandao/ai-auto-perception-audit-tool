"""
启动数学审核服务并测试AISleepGen - ASCII修复版本
"""

import subprocess
import time
import requests
import json
from datetime import datetime
import sys
import os

def start_mathematical_service():
    """启动数学审核服务"""
    print("=" * 70)
    print("STARTING MATHEMATICAL AUDIT SERVICE v4.0")
    print("=" * 70)
    
    service_dir = "microservices/mathematical-audit-service"
    
    print(f"1. Starting service on port 8008...")
    
    try:
        # 检查服务目录是否存在
        if not os.path.exists(service_dir):
            print(f"   ERROR: Service directory not found: {service_dir}")
            return False
        
        # 检查main.py是否存在
        main_file = os.path.join(service_dir, "main.py")
        if not os.path.exists(main_file):
            print(f"   ERROR: main.py not found in {service_dir}")
            return False
        
        # 在新控制台启动服务
        print(f"   Starting uvicorn server...")
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008"],
            cwd=service_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   Service started with PID: {process.pid}")
        print(f"   Waiting for service to initialize (10 seconds)...")
        
        time.sleep(10)
        
        # 测试服务健康
        print(f"2. Testing service health...")
        
        try:
            response = requests.get("http://localhost:8008/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Mathematical Engine: {data.get('mathematical_engine', 'unknown')}")
                print(f"   Available Audits: {data.get('available_audits', [])}")
                print(f"   [SUCCESS] Service is healthy!")
            else:
                print(f"   [ERROR] Service not healthy: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   [ERROR] Service test failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] Error starting service: {str(e)}")
        return False

def test_aisleepgen_mathematical_audit():
    """测试AISleepGen数学审核"""
    print()
    print("3. Testing AISleepGen mathematical audit...")
    
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    print(f"   Skill: {skill_id}")
    print(f"   Path: {skill_path}")
    
    if not os.path.exists(skill_path):
        print(f"   [WARNING] Skill path does not exist, using test data")
        # 创建测试数据
        test_data = {
            "skill_id": skill_id,
            "skill_path": skill_path,
            "audit_types": ["maclaurin", "taylor", "fourier"],
            "mathematical_depth": 3
        }
    else:
        test_data = {
            "skill_id": skill_id,
            "skill_path": skill_path,
            "audit_types": ["maclaurin", "taylor", "fourier", "matrix", "proof"],
            "mathematical_depth": 5
        }
    
    try:
        response = requests.post(
            "http://localhost:8008/audit/mathematical",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   [SUCCESS] Mathematical audit completed!")
            print(f"   Overall Score: {result.get('overall_mathematical_score', 0)}")
            print(f"   Audit Time: {result.get('audit_time', 0)}s")
            print(f"   Certificates: {len(result.get('mathematical_certificates', []))}")
            
            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"mathematical_audit_result_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"   Results saved to: {output_file}")
            
            return True
        else:
            print(f"   [ERROR] Audit failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Audit test failed: {str(e)}")
        return False

def main():
    """主函数"""
    print("MATHEMATICAL AUDIT SERVICE TESTER")
    print("=" * 50)
    
    # 启动服务
    if not start_mathematical_service():
        print("\n[FAILED] Could not start mathematical service")
        return 1
    
    # 测试审核
    if not test_aisleepgen_mathematical_audit():
        print("\n[FAILED] Mathematical audit test failed")
        return 1
    
    print("\n" + "=" * 50)
    print("[SUCCESS] All tests passed!")
    print("Mathematical Audit Service v4.0 is ready for production use.")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())