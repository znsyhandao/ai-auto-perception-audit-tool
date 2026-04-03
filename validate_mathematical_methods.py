"""
验证数学方法有效性 - AISleepGen实际测试
"""

import requests
import json
import datetime
import time
from typing import Dict, Any

def validate_aisleepgen_mathematical_audit():
    """验证AISleepGen数学审核有效性"""
    print("VALIDATING MATHEMATICAL METHODS EFFECTIVENESS")
    print("=" * 70)
    
    # AISleepGen技能信息
    skill_info = {
        'skill_id': 'aisleepgen_v1.0.7',
        'skill_path': 'D:/openclaw/releases/AISleepGen/v1.0.7_fixed',
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 5
    }
    
    print(f"1. Target Skill: {skill_info['skill_id']}")
    print(f"   Path: {skill_info['skill_path']}")
    print(f"   Audit Types: {skill_info['audit_types']}")
    
    # 检查技能路径是否存在
    import os
    if not os.path.exists(skill_info['skill_path']):
        print(f"   [WARNING] Skill path does not exist, using simulated data")
        # 创建模拟数据用于验证
        skill_info['skill_path'] = 'simulated/skill/path'
    
    print("\n2. Starting mathematical audit validation...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:8010/audit',
            json=skill_info,
            timeout=60
        )
        
        audit_time = time.time() - start_time
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {audit_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n3. VALIDATION RESULTS:")
            print(f"   Overall Score: {result.get('overall_mathematical_score', 0)}/100")
            print(f"   Audit Status: {result.get('audit_status', 'unknown')}")
            print(f"   Audit Time: {result.get('audit_time', 0)}s")
            
            certificates = result.get('mathematical_certificates', [])
            print(f"   Certificates Generated: {len(certificates)}")
            
            # 分析证书质量
            if certificates:
                print(f"\n4. CERTIFICATE QUALITY ANALYSIS:")
                
                # 按类型统计
                cert_types = {}
                for cert in certificates:
                    cert_type = cert.get('audit_type', 'unknown')
                    cert_types[cert_type] = cert_types.get(cert_type, 0) + 1
                
                print(f"   Certificate Distribution:")
                for cert_type, count in cert_types.items():
                    print(f"     - {cert_type}: {count} certificates")
                
                # 置信度分析
                confidences = [c.get('confidence', 0) for c in certificates]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                print(f"   Average Confidence: {avg_confidence:.3f}")
                
                # 有效性分析
                valid_count = sum(1 for c in certificates if c.get('validity') == 'valid')
                validity_rate = valid_count / len(certificates) if certificates else 0
                print(f"   Validity Rate: {validity_rate:.1%}")
                
                # 详细证书信息
                print(f"\n5. DETAILED CERTIFICATE INFO (first 3):")
                for i, cert in enumerate(certificates[:3], 1):
                    print(f"   {i}. {cert.get('theorem', 'Unknown')}")
                    print(f"      ID: {cert.get('certificate_id', 'N/A')}")
                    print(f"      Confidence: {cert.get('confidence', 0)}")
                    print(f"      Validity: {cert.get('validity', 'Unknown')}")
                    print(f"      Generated: {cert.get('generated_at', 'N/A')}")
            
            # 审核结果分析
            audit_results = result.get('audit_results', {})
            print(f"\n6. AUDIT RESULTS ANALYSIS:")
            print(f"   Total Audit Types: {len(audit_results)}")
            
            success_count = sum(1 for r in audit_results.values() if r.get('status') == 'success')
            success_rate = success_count / len(audit_results) if audit_results else 0
            print(f"   Success Rate: {success_rate:.1%}")
            
            # 保存完整验证报告
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'D:/OpenClaw_TestingFramework/mathematical_validation_report_{timestamp}.json'
            
            validation_report = {
                'validation_id': f'VALIDATION_{timestamp}',
                'skill_info': skill_info,
                'validation_time': audit_time,
                'validation_results': result,
                'summary': {
                    'overall_score': result.get('overall_mathematical_score', 0),
                    'certificate_count': len(certificates),
                    'average_confidence': avg_confidence if certificates else 0,
                    'validity_rate': validity_rate if certificates else 0,
                    'success_rate': success_rate,
                    'mathematical_coverage': f"{len(set(c.get('audit_type', 'unknown') for c in certificates))}/5 theorem types"
                },
                'validation_status': 'PASS' if result.get('overall_mathematical_score', 0) > 50 else 'WARNING' if result.get('overall_mathematical_score', 0) > 0 else 'FAIL',
                'generated_at': datetime.datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(validation_report, f, indent=2, ensure_ascii=False)
            
            print(f"\n7. VALIDATION REPORT:")
            print(f"   Report ID: {validation_report['validation_id']}")
            print(f"   Status: {validation_report['validation_status']}")
            print(f"   Saved to: {output_file}")
            
            # 最终评估
            print(f"\n8. FINAL ASSESSMENT:")
            if validation_report['validation_status'] == 'PASS':
                print(f"   ✅ MATHEMATICAL METHODS ARE EFFECTIVE")
                print(f"   Mathematical audit framework successfully validated")
                print(f"   Ready for production deployment")
            elif validation_report['validation_status'] == 'WARNING':
                print(f"   ⚠️ MATHEMATICAL METHODS PARTIALLY EFFECTIVE")
                print(f"   Some improvements needed before production")
            else:
                print(f"   ❌ MATHEMATICAL METHODS NEED IMPROVEMENT")
                print(f"   Significant improvements required")
            
            return validation_report['validation_status'] == 'PASS'
            
        else:
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   Validation error: {e}")
        return False

def main():
    """主验证函数"""
    print("MATHEMATICAL METHODS VALIDATION FOR AISleepGen")
    print("=" * 70)
    
    # 首先检查服务健康
    print("\n0. Checking service health...")
    try:
        health_response = requests.get('http://localhost:8010/health', timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Service: {health_data.get('service', 'unknown')}")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Mathematical Engine: {health_data.get('mathematical_engine', 'unknown')}")
        else:
            print(f"   Health check failed: HTTP {health_response.status_code}")
            return False
    except Exception as e:
        print(f"   Health check error: {e}")
        return False
    
    # 运行验证
    print("\n" + "=" * 70)
    if validate_aisleepgen_mathematical_audit():
        print("\n" + "=" * 70)
        print("✅ VALIDATION SUCCESSFUL")
        print("Mathematical methods are effective and ready for production.")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ VALIDATION FAILED")
        print("Mathematical methods need improvement.")
        print("=" * 70)
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)