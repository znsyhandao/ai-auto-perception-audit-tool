"""
启动数学审核服务并测试AISleepGen
"""

import subprocess
import time
import requests
import json
from datetime import datetime

def start_mathematical_service():
    """启动数学审核服务"""
    print("=" * 70)
    print("STARTING MATHEMATICAL AUDIT SERVICE v4.0")
    print("=" * 70)
    
    service_dir = "microservices/mathematical-audit-service"
    
    print(f"1. Starting service on port 8008...")
    
    try:
        # 在新控制台启动服务
        process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008", "--reload"],
            cwd=service_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"   Service started with PID: {process.pid}")
        print(f"   Waiting for service to initialize...")
        
        time.sleep(8)
        
        # 测试服务健康
        print(f"2. Testing service health...")
        
        try:
            response = requests.get("http://localhost:8008/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Mathematical Engine: {data.get('mathematical_engine', 'unknown')}")
                print(f"   Available Audits: {data.get('available_audits', [])}")
                print(f"   ✅ Service is healthy!")
            else:
                print(f"   ❌ Service not healthy: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Service test failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error starting service: {str(e)}")
        return False

def test_aisleepgen_mathematical_audit():
    """测试AISleepGen数学审核"""
    print()
    print("3. Testing AISleepGen mathematical audit...")
    
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    print(f"   Skill: {skill_id}")
    print(f"   Path: {skill_path}")
    print(f"   Starting complete mathematical audit...")
    
    try:
        response = requests.post(
            "http://localhost:8008/audit",
            json={
                "skill_id": skill_id,
                "skill_path": skill_path,
                "audit_types": ["maclaurin", "taylor", "fourier", "matrix", "proof"],
                "mathematical_depth": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"   ✅ Audit completed successfully!")
            print(f"   Overall Mathematical Score: {data.get('overall_mathematical_score', 0)}/100")
            print(f"   Audit Time: {data.get('audit_time', 0)} seconds")
            
            # 显示详细结果
            audit_results = data.get("audit_results", {})
            print()
            print("   Detailed Results:")
            print("   " + "-" * 40)
            
            for audit_type, result in audit_results.items():
                score = result.get("score", 0)
                analysis_type = result.get("analysis_type", "unknown")
                print(f"   {analysis_type.upper():25} Score: {score:5}/100")
            
            # 显示数学证书
            certificates = data.get("mathematical_certificates", [])
            print()
            print(f"   Mathematical Certificates: {len(certificates)}")
            for cert in certificates[:3]:  # 显示前3个证书
                cert_type = cert.get("certificate_type", "unknown")
                cert_id = cert.get("certificate_id", "unknown")
                print(f"   • {cert_type}: {cert_id}")
            
            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AISleepGen_Mathematical_Audit_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print()
            print(f"   📄 Full report saved: {filename}")
            
            return data
            
        else:
            print(f"   ❌ Audit failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Audit error: {str(e)}")
        return None

def main():
    """主函数"""
    print("MATHEMATICAL AUDIT FRAMEWORK v4.0 - AISleepGen Test")
    print("=" * 70)
    
    # 启动服务
    if not start_mathematical_service():
        print("Failed to start mathematical service")
        return
    
    # 测试审核
    result = test_aisleepgen_mathematical_audit()
    
    print()
    print("=" * 70)
    
    if result:
        overall_score = result.get("overall_mathematical_score", 0)
        
        if overall_score >= 80:
            print("🎉 EXCELLENT! AISleepGen passed mathematical audit with high score!")
            print("   Ready for production release with mathematical certification.")
        elif overall_score >= 70:
            print("✅ GOOD! AISleepGen passed mathematical audit.")
            print("   Ready for production release.")
        elif overall_score >= 60:
            print("⚠️  FAIR! AISleepGen passed with some improvements needed.")
            print("   Can be released with improvements recommended.")
        else:
            print("❌ NEEDS IMPROVEMENT! Mathematical audit score is low.")
            print("   Requires significant improvements before release.")
        
        print()
        print(f"Overall Mathematical Score: {overall_score}/100")
        print(f"Mathematical Certificates: {len(result.get('mathematical_certificates', []))}")
        
    else:
        print("❌ Mathematical audit test failed.")
        print("   Please check service logs and try again.")
    
    print("=" * 70)
    print()
    print("Note: Mathematical service is running on port 8008.")
    print("Keep this window open to maintain the service.")

if __name__ == "__main__":
    main()