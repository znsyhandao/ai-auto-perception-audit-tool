"""
审核模块化版本的AISleepGen
"""

import requests
import json
import time

def audit_modular_aisleepgen():
    """审核模块化版本"""
    print("AUDITING MODULAR AISLEEPGEN v1.0.8")
    print("=" * 70)
    
    # 模块化版本路径
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.8_modular"
    
    print(f"\n1. Target: AISleepGen v1.0.8 (Modular)")
    print(f"   Path: {skill_path}")
    
    # 运行完整数学审核
    print(f"\n2. Running mathematical audit on modular version...")
    
    audit_data = {
        'skill_id': 'aisleepgen_v1.0.8_modular',
        'skill_path': skill_path,
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 5
    }
    
    try:
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
            
            # 分析证书
            if certificates:
                print(f"\n3. Mathematical Certificate Analysis:")
                
                for i, cert in enumerate(certificates, 1):
                    theorem = cert.get('theorem', 'Unknown')
                    confidence = cert.get('confidence', 0)
                    validity = cert.get('validity', 'unknown')
                    
                    print(f"   {i}. {theorem}")
                    print(f"      Confidence: {confidence:.3f}")
                    print(f"      Validity: {validity}")
                
                # 计算指标
                confidences = [c.get('confidence', 0) for c in certificates]
                avg_confidence = sum(confidences) / len(confidences)
                
                valid_count = sum(1 for c in certificates if c.get('validity') == 'valid')
                validity_rate = valid_count / len(certificates)
                
                print(f"\n   Summary Metrics:")
                print(f"   Average Confidence: {avg_confidence:.3f}")
                print(f"   Validity Rate: {validity_rate:.1%}")
                print(f"   Coverage: {len(set(c.get('audit_type', 'unknown') for c in certificates))}/5 theorem types")
            
            # 保存报告
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            report = {
                'audit_id': f'AISLEEPGEN_MODULAR_AUDIT_{timestamp}',
                'skill': {
                    'id': 'aisleepgen_v1.0.8',
                    'name': 'AISleepGen Modular Version',
                    'version': '1.0.8_modular',
                    'path': skill_path
                },
                'audit': {
                    'types': audit_data['audit_types'],
                    'depth': audit_data['mathematical_depth'],
                    'time_seconds': audit_time
                },
                'results': result,
                'summary': {
                    'overall_score': result.get('overall_mathematical_score', 0),
                    'certificate_count': len(certificates),
                    'audit_time': audit_time,
                    'release_ready': result.get('overall_mathematical_score', 0) >= 70,
                    'improvement_from_v1.0.7': 'to_be_calculated'
                },
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            report_file = f'aisleepgen_modular_audit_{timestamp}.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n4. Audit Report:")
            print(f"   Report ID: {report['audit_id']}")
            print(f"   Saved to: {report_file}")
            
            # 发布建议
            print(f"\n5. RELEASE RECOMMENDATION:")
            score = report['summary']['overall_score']
            
            if score >= 70:
                print(f"   ✅ RECOMMENDED FOR RELEASE")
                print(f"   Mathematical score: {score}/100 (≥70)")
                print(f"   Certificates: {report['summary']['certificate_count']}/5")
                
                # 检查矩阵分解改进
                matrix_cert = next((c for c in certificates if 'matrix' in str(c).lower()), None)
                if matrix_cert:
                    matrix_conf = matrix_cert.get('confidence', 0)
                    print(f"   Matrix decomposition confidence: {matrix_conf:.3f} (previously: 0.700)")
                    if matrix_conf > 0.700:
                        print(f"   ✅ Matrix decomposition IMPROVED after modularization")
            else:
                print(f"   ⚠️ NOT READY FOR RELEASE")
                print(f"   Mathematical score: {score}/100 (<70)")
            
            return report['summary']['release_ready']
            
        else:
            print(f"   ERROR: Audit failed with HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def compare_with_previous():
    """与之前版本比较"""
    print(f"\n6. Comparison with v1.0.7_fixed:")
    
    # 之前的审核结果
    previous_score = 79.95
    previous_certs = 4
    previous_matrix_conf = 0.700
    
    print(f"   v1.0.7_fixed: Score={previous_score}, Certs={previous_certs}, Matrix={previous_matrix_conf}")
    print(f"   v1.0.8_modular: Waiting for audit results...")
    
    return True

def main():
    """主函数"""
    print("MODULAR AISLEEPGEN MATHEMATICAL AUDIT")
    print("=" * 70)
    
    # 检查数学服务
    print("\n0. Checking mathematical audit service...")
    try:
        response = requests.get('http://localhost:8040/health', timeout=5)
        if response.status_code == 200:
            print(f"   Service: Healthy")
        else:
            print(f"   ERROR: Service not healthy")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # 运行审核
    print("\n" + "=" * 70)
    release_ready = audit_modular_aisleepgen()
    
    # 比较
    compare_with_previous()
    
    print("\n" + "=" * 70)
    if release_ready:
        print("CONCLUSION: Modular v1.0.8 is READY FOR RELEASE")
        print("Matrix decomposition should show improvement after modularization.")
    else:
        print("CONCLUSION: Modular v1.0.8 NEEDS FURTHER WORK")
        print("Check mathematical audit results for details.")
    
    print("=" * 70)
    return release_ready

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)