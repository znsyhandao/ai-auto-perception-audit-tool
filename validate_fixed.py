"""
验证数学方法有效性 - 修复编码版本
"""

import requests
import json
import datetime
import time

def validate_mathematical_methods():
    """验证数学方法有效性"""
    print("VALIDATING MATHEMATICAL METHODS")
    print("=" * 70)
    
    # 测试数据
    test_data = {
        'skill_id': 'test_validation',
        'skill_path': 'test/path',
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 5
    }
    
    print("1. Testing complete mathematical audit...")
    
    try:
        start_time = time.time()
        response = requests.post('http://localhost:8010/audit', json=test_data, timeout=30)
        audit_time = time.time() - start_time
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {audit_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n2. VALIDATION RESULTS:")
            print(f"   Overall Score: {result.get('overall_mathematical_score', 0)}/100")
            print(f"   Audit Status: {result.get('audit_status', 'unknown')}")
            
            certificates = result.get('mathematical_certificates', [])
            print(f"   Certificates Generated: {len(certificates)}")
            
            # 分析结果
            if certificates:
                confidences = [c.get('confidence', 0) for c in certificates]
                avg_confidence = sum(confidences) / len(confidences)
                
                valid_count = sum(1 for c in certificates if c.get('validity') == 'valid')
                validity_rate = valid_count / len(certificates)
                
                print(f"\n3. QUALITY METRICS:")
                print(f"   Average Confidence: {avg_confidence:.3f}")
                print(f"   Validity Rate: {validity_rate:.1%}")
                print(f"   Mathematical Coverage: {len(set(c.get('audit_type', 'unknown') for c in certificates))}/5 theorem types")
            
            # 保存验证报告
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            report = {
                'validation_id': f'VALIDATION_{timestamp}',
                'test_data': test_data,
                'results': result,
                'summary': {
                    'overall_score': result.get('overall_mathematical_score', 0),
                    'certificate_count': len(certificates),
                    'audit_time': audit_time,
                    'validation_status': 'PASS' if result.get('overall_mathematical_score', 0) > 50 else 'FAIL'
                },
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            output_file = f'validation_report_{timestamp}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n4. VALIDATION REPORT:")
            print(f"   Report ID: {report['validation_id']}")
            print(f"   Status: {report['summary']['validation_status']}")
            print(f"   Saved to: {output_file}")
            
            # 最终评估
            print(f"\n5. FINAL ASSESSMENT:")
            if report['summary']['validation_status'] == 'PASS':
                print("   MATHEMATICAL METHODS ARE EFFECTIVE")
                print("   Ready for production deployment")
                return True
            else:
                print("   MATHEMATICAL METHODS NEED IMPROVEMENT")
                return False
                
        else:
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   Validation error: {e}")
        return False

def main():
    """主函数"""
    print("MATHEMATICAL METHODS VALIDATION")
    print("=" * 70)
    
    # 检查服务健康
    print("\n0. Checking service health...")
    try:
        health = requests.get('http://localhost:8010/health', timeout=5)
        if health.status_code == 200:
            print(f"   Service: Healthy")
            print(f"   Mathematical Engine: Available")
        else:
            print(f"   Health check failed")
            return False
    except Exception as e:
        print(f"   Health check error: {e}")
        return False
    
    # 运行验证
    print("\n" + "=" * 70)
    if validate_mathematical_methods():
        print("\n" + "=" * 70)
        print("VALIDATION SUCCESSFUL")
        print("Mathematical methods are effective and ready for production.")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("VALIDATION FAILED")
        print("Mathematical methods need improvement.")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)