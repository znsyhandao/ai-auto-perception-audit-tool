"""
AISleepGen发布审核脚本
"""

import requests
import json

def run_audit():
    """运行审核"""
    print("AISleepGen Release Audit")
    print("=" * 60)
    
    # 配置
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    service_url = "http://localhost:8010"
    
    print("1. Running mathematical audit...")
    
    audit_data = {
        "skill_id": skill_id,
        "skill_path": skill_path,
        "audit_types": ["maclaurin", "taylor", "fourier", "matrix", "proof"],
        "mathematical_depth": 5
    }
    
    try:
        response = requests.post(f"{service_url}/audit", json=audit_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            score = result.get("overall_mathematical_score", 0)
            certificates = result.get("mathematical_certificates", [])
            
            print(f"   Score: {score}")
            print(f"   Certificates: {len(certificates)}")
            
            # 检查要求
            score_ok = score >= 75.0
            certs_ok = len(certificates) >= 3
            
            if score_ok and certs_ok:
                print("   Mathematical audit: PASS")
                return True
            else:
                print(f"   Mathematical audit: FAIL")
                print(f"     Score >= 75: {score_ok}")
                print(f"     Certificates >= 3: {certs_ok}")
                return False
        else:
            print(f"   Audit failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   Audit error: {e}")
        return False

def main():
    """主函数"""
    if run_audit():
        print("\n" + "=" * 60)
        print("AUDIT PASSED")
        print("AISleepGen is ready for release.")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("AUDIT FAILED")
        print("AISleepGen needs fixes.")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
