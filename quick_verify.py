"""
快速验证测试环境
"""

import requests
import time

def quick_verify():
    """快速验证"""
    print("QUICK VERIFICATION - TEST ENVIRONMENT")
    print("=" * 60)
    
    # 等待服务完全启动
    print("Waiting for service to fully start...")
    time.sleep(2)
    
    # 1. 健康检查
    print("\n1. Health check...")
    try:
        response = requests.get("http://localhost:8040/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Mathematical Engine: {data.get('mathematical_engine', 'unknown')}")
            print("   PASS")
        else:
            print(f"   FAIL: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # 2. 快速审核测试
    print("\n2. Quick audit test...")
    test_data = {
        'skill_id': 'quick-test',
        'skill_path': 'test/path',
        'audit_types': ['maclaurin'],
        'mathematical_depth': 3
    }
    
    try:
        start_time = time.time()
        response = requests.post("http://localhost:8040/audit", json=test_data, timeout=10)
        audit_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS! Audit completed in {audit_time:.2f}s")
            print(f"   Score: {result.get('overall_mathematical_score', 0)}")
            print("   PASS")
            return True
        else:
            print(f"   FAIL: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def main():
    """主函数"""
    print("TEST ENVIRONMENT DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    if quick_verify():
        print("\n" + "=" * 60)
        print("VERIFICATION SUCCESSFUL")
        print("Service is running on: http://localhost:8040")
        print("Phase A completed. Ready for Phase B.")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("VERIFICATION FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)