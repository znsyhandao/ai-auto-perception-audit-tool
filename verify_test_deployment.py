"""
验证测试环境部署
"""

import requests
import json

def verify_test_deployment():
    """验证测试环境部署"""
    print("VERIFYING TEST ENVIRONMENT DEPLOYMENT")
    print("=" * 70)
    
    base_url = "http://localhost:8030"
    
    # 1. 健康检查
    print("\n1. Health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
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
    
    # 2. 完整数学审核测试
    print("\n2. Full mathematical audit test...")
    test_data = {
        'skill_id': 'test-deployment',
        'skill_path': 'test/path',
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 5
    }
    
    try:
        response = requests.post(f"{base_url}/audit", json=test_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   SUCCESS! Audit completed.")
            print(f"   Overall Score: {result.get('overall_mathematical_score', 0)}")
            print(f"   Certificates: {len(result.get('mathematical_certificates', []))}")
            print(f"   Audit Time: {result.get('audit_time', 0)}s")
            
            # 分析证书
            certificates = result.get('mathematical_certificates', [])
            if certificates:
                print(f"\n3. Certificate analysis:")
                confidences = [c.get('confidence', 0) for c in certificates]
                avg_confidence = sum(confidences) / len(confidences)
                
                valid_count = sum(1 for c in certificates if c.get('validity') == 'valid')
                validity_rate = valid_count / len(certificates)
                
                print(f"   Average Confidence: {avg_confidence:.3f}")
                print(f"   Validity Rate: {validity_rate:.1%}")
                print(f"   Coverage: {len(set(c.get('audit_type', 'unknown') for c in certificates))}/5 theorem types")
            
            print("   PASS")
            return True
        else:
            print(f"   FAIL: HTTP {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def main():
    """主函数"""
    print("TEST ENVIRONMENT VERIFICATION")
    print("=" * 70)
    
    if verify_test_deployment():
        print("\n" + "=" * 70)
        print("VERIFICATION SUCCESSFUL")
        print("Mathematical audit service is running in test environment.")
        print("\nAccess points:")
        print("  Health check: http://localhost:8030/health")
        print("  API docs:     http://localhost:8030/docs")
        print("  Test audit:   POST http://localhost:8030/audit")
        print("\nPhase A completed. Ready for Phase B.")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("VERIFICATION FAILED")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)