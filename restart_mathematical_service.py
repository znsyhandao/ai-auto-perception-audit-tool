"""
重启数学审核服务进行最终验证
"""

import subprocess
import time
import requests
from pathlib import Path

def restart_mathematical_service():
    """重启数学审核服务"""
    print("RESTARTING MATHEMATICAL AUDIT SERVICE")
    print("=" * 70)
    
    service_dir = Path("D:/OpenClaw_TestingFramework/microservices/mathematical-audit-service")
    main_file = service_dir / "main.py"
    
    if not main_file.exists():
        print(f"ERROR: Service file not found: {main_file}")
        return False
    
    print(f"1. Service directory: {service_dir}")
    print(f"2. Main file: {main_file}")
    
    # 使用端口8040（之前的端口）
    port = 8040
    
    print(f"3. Starting service on port {port}...")
    
    try:
        # 启动服务（后台运行）
        cmd = f'cd "{service_dir}" && python main.py --port {port}'
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   Service process started (PID: {process.pid})")
        
        # 等待服务启动
        print(f"4. Waiting for service to start...")
        time.sleep(5)
        
        # 检查服务健康
        print(f"5. Checking service health...")
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f'http://localhost:{port}/health', timeout=2)
                if response.status_code == 200:
                    print(f"   Service healthy on port {port}")
                    print(f"   Health response: {response.json()}")
                    
                    # 检查审核端点
                    print(f"6. Testing audit endpoint...")
                    test_data = {
                        'skill_id': 'test_service',
                        'skill_path': 'test',
                        'audit_types': ['matrix']
                    }
                    
                    test_response = requests.post(
                        f'http://localhost:{port}/audit',
                        json=test_data,
                        timeout=10
                    )
                    
                    if test_response.status_code == 200:
                        print(f"   Audit endpoint working")
                        return True
                    else:
                        print(f"   Audit endpoint test failed: HTTP {test_response.status_code}")
                        break
                
            except requests.exceptions.RequestException as e:
                if i < max_retries - 1:
                    print(f"   Attempt {i+1}/{max_retries}: Waiting...")
                    time.sleep(2)
                else:
                    print(f"   Service not responding after {max_retries} attempts")
                    print(f"   Error: {e}")
                    return False
        
        return False
        
    except Exception as e:
        print(f"ERROR starting service: {e}")
        return False

def run_v2_audit():
    """运行v2.0实际审核"""
    print(f"\n7. RUNNING ACTUAL AUDIT ON v2.0_targeted")
    print("-" * 50)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v2.0_targeted"
    
    audit_data = {
        'skill_id': 'aisleepgen_v2.0_targeted',
        'skill_path': skill_path,
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 5
    }
    
    try:
        print(f"   Target: {skill_path}")
        print(f"   Sending audit request...")
        
        start_time = time.time()
        response = requests.post(
            'http://localhost:8040/audit',
            json=audit_data,
            timeout=60
        )
        audit_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   Audit completed in {audit_time:.2f}s")
            print(f"   Overall Mathematical Score: {result.get('overall_mathematical_score', 0)}/100")
            
            certificates = result.get('mathematical_certificates', [])
            print(f"   Mathematical Certificates: {len(certificates)}")
            
            # 查找矩阵分解证书
            matrix_cert = None
            for cert in certificates:
                if "matrix" in cert.get("theorem", "").lower():
                    matrix_cert = cert
                    break
            
            if matrix_cert:
                matrix_conf = matrix_cert.get("confidence", 0)
                matrix_valid = matrix_cert.get("validity", "unknown")
                
                print(f"\n   Matrix Decomposition Result:")
                print(f"     Confidence: {matrix_conf:.3f}")
                print(f"     Validity: {matrix_valid}")
                
                # 与v1.0.9比较
                v1_matrix_conf = 0.700
                improvement = matrix_conf - v1_matrix_conf
                
                print(f"\n   Comparison with v1.0.9:")
                print(f"     v1.0.9 confidence: {v1_matrix_conf:.3f}")
                print(f"     v2.0 confidence: {matrix_conf:.3f}")
                print(f"     Improvement: {improvement:+.3f}")
                
                target = 0.850
                if matrix_conf >= target:
                    print(f"     ✅ TARGET ACHIEVED: ≥{target}")
                else:
                    print(f"     ⚠️ Target not reached: {matrix_conf:.3f}/{target}")
            
            # 保存结果
            import json
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            result_file = f"v2_actual_audit_result_{timestamp}.json"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n   Audit result saved: {result_file}")
            
            return result
            
        else:
            print(f"   ERROR: Audit failed with HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ERROR running audit: {e}")
        return None

def main():
    """主重启函数"""
    print("MATHEMATICAL AUDIT SERVICE RESTART & v2.0 VERIFICATION")
    print("=" * 70)
    
    # 1. 重启服务
    service_restarted = restart_mathematical_service()
    
    if not service_restarted:
        print(f"\n" + "=" * 70)
        print("SERVICE RESTART FAILED - USING PREDICTED RESULTS")
        print("=" * 70)
        return False
    
    # 2. 运行v2.0审核
    print(f"\n" + "=" * 70)
    audit_result = run_v2_audit()
    
    print(f"\n" + "=" * 70)
    if audit_result:
        print("ACTUAL AUDIT COMPLETE - RESULTS AVAILABLE")
    else:
        print("AUDIT FAILED - USING PREDICTED RESULTS")
    
    print("=" * 70)
    
    return audit_result is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)