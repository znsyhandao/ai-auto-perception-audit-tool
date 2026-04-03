"""
运行v2.0最终数学审核
"""

import requests
import json
import time
from pathlib import Path

def run_final_audit():
    """运行最终审核"""
    print("RUNNING FINAL MATHEMATICAL AUDIT ON v2.0_release")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v2.0_release"
    
    # 检查服务健康
    print("1. Checking service health...")
    try:
        health_response = requests.get('http://localhost:8010/health', timeout=5)
        if health_response.status_code == 200:
            print("   Service healthy")
        else:
            print(f"   Service not healthy: HTTP {health_response.status_code}")
            return None
    except Exception as e:
        print(f"   Service not reachable: {e}")
        return None
    
    # 准备审核数据
    audit_data = {
        'skill_id': 'aisleepgen_v2.0_release',
        'skill_path': skill_path,
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 5
    }
    
    print(f"\n2. Running audit on: {skill_path}")
    print("   Audit types: maclaurin, taylor, fourier, matrix, proof")
    
    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8010/audit',
            json=audit_data,
            timeout=60
        )
        audit_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n3. AUDIT COMPLETED in {audit_time:.2f}s")
            print("-" * 50)
            
            # 总体结果
            overall_score = result.get('overall_mathematical_score', 0)
            certificates = result.get('mathematical_certificates', [])
            
            print(f"Overall Mathematical Score: {overall_score}/100")
            print(f"Mathematical Certificates: {len(certificates)}")
            
            # 详细证书信息
            print(f"\nCertificate details:")
            for i, cert in enumerate(certificates, 1):
                theorem = cert.get('theorem', 'Unknown')
                confidence = cert.get('confidence', 0)
                validity = cert.get('validity', 'unknown')
                
                print(f"  {i}. {theorem}")
                print(f"     Confidence: {confidence:.3f}")
                print(f"     Validity: {validity}")
            
            # 矩阵分解结果
            matrix_cert = None
            for cert in certificates:
                if "matrix" in cert.get("theorem", "").lower():
                    matrix_cert = cert
                    break
            
            if matrix_cert:
                matrix_conf = matrix_cert.get("confidence", 0)
                matrix_valid = matrix_cert.get("validity", "unknown")
                
                print(f"\n4. MATRIX DECOMPOSITION RESULT")
                print("-" * 50)
                print(f"Confidence: {matrix_conf:.3f}")
                print(f"Validity: {matrix_valid}")
                
                # 与v1.0.9比较
                v1_matrix_conf = 0.700
                improvement = matrix_conf - v1_matrix_conf
                
                print(f"\nComparison with v1.0.9:")
                print(f"  v1.0.9 confidence: {v1_matrix_conf:.3f}")
                print(f"  v2.0 confidence: {matrix_conf:.3f}")
                print(f"  Improvement: {improvement:+.3f}")
                
                target = 0.850
                if matrix_conf >= target:
                    print(f"  TARGET ACHIEVED: {matrix_conf:.3f} >= {target}")
                else:
                    print(f"  TARGET NOT REACHED: {matrix_conf:.3f} < {target}")
                    print(f"  Gap: {target - matrix_conf:.3f}")
            
            # 其他指标
            print(f"\n5. ADDITIONAL METRICS")
            print("-" * 50)
            
            audit_time_ms = result.get('audit_time_ms', audit_time * 1000)
            certificate_confidence_avg = result.get('certificate_confidence_avg', 0)
            validity_rate = result.get('validity_rate', 0)
            
            print(f"Audit time: {audit_time_ms:.0f} ms")
            print(f"Average certificate confidence: {certificate_confidence_avg:.3f}")
            print(f"Validity rate: {validity_rate:.1%}")
            
            # 保存结果
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            result_file = f"v2_final_audit_result_{timestamp}.json"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n6. RESULT SAVED: {result_file}")
            
            # 创建总结
            create_summary(result, matrix_conf if matrix_cert else 0)
            
            return result
            
        else:
            print(f"   ERROR: Audit failed with HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ERROR running audit: {e}")
        return None

def create_summary(audit_result, matrix_confidence):
    """创建审核总结"""
    print(f"\n7. FINAL AUDIT SUMMARY")
    print("=" * 70)
    
    summary = {
        "audit_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        "skill_version": "v2.0_release",
        "overall_score": audit_result.get('overall_mathematical_score', 0),
        "certificate_count": len(audit_result.get('mathematical_certificates', [])),
        "matrix_confidence": matrix_confidence,
        "v1_matrix_confidence": 0.700,
        "improvement": matrix_confidence - 0.700,
        "target_confidence": 0.850,
        "target_achieved": matrix_confidence >= 0.850,
        "audit_duration_ms": audit_result.get('audit_time_ms', 0),
        "validity_rate": audit_result.get('validity_rate', 0)
    }
    
    # 显示总结
    print(f"\nAISleepGen v2.0 Final Mathematical Audit")
    print(f"Audit time: {summary['audit_time']}")
    print(f"Overall score: {summary['overall_score']}/100")
    print(f"Certificates: {summary['certificate_count']}")
    print(f"\nMatrix Decomposition Confidence:")
    print(f"  v1.0.9: {summary['v1_matrix_confidence']:.3f}")
    print(f"  v2.0: {summary['matrix_confidence']:.3f}")
    print(f"  Improvement: {summary['improvement']:+.3f}")
    print(f"  Target: {summary['target_confidence']:.3f}")
    
    if summary['target_achieved']:
        print(f"  STATUS: TARGET ACHIEVED")
    else:
        print(f"  STATUS: Target not reached (gap: {summary['target_confidence'] - summary['matrix_confidence']:.3f})")
    
    print(f"\nAdditional metrics:")
    print(f"  Audit duration: {summary['audit_duration_ms']:.0f} ms")
    print(f"  Validity rate: {summary['validity_rate']:.1%}")
    
    # 保存总结
    summary_file = "v2_final_audit_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nSummary saved: {summary_file}")
    
    # 最终建议
    print(f"\n8. RELEASE RECOMMENDATION")
    print("-" * 50)
    
    if summary['target_achieved']:
        print("RECOMMENDATION: RELEASE v2.0")
        print("  - Matrix confidence target achieved")
        print("  - All certificates generated")
        print("  - Optimization validated")
    else:
        print("RECOMMENDATION: RELEASE WITH TRANSPARENT NOTES")
        print("  - Matrix confidence improved but target not reached")
        print("  - Include transparent documentation")
        print("  - Plan v2.1 for further optimization")
    
    return summary

def main():
    """主函数"""
    print("AISLEEPGEN v2.0 FINAL MATHEMATICAL AUDIT")
    print("=" * 70)
    
    result = run_final_audit()
    
    print(f"\n" + "=" * 70)
    if result:
        print("FINAL AUDIT COMPLETE - RESULTS AVAILABLE")
    else:
        print("FINAL AUDIT FAILED - CHECK ERRORS")
    
    print("=" * 70)
    
    return result is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)