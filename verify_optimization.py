"""
验证深度优化效果 - 运行数学审核
"""

import requests
import json
import time

def audit_optimized_version():
    """审核优化后的版本"""
    print("AUDITING OPTIMIZED AISLEEPGEN v1.0.9")
    print("=" * 70)
    
    # 优化版本路径
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.9_optimized"
    
    print(f"\n1. Target: AISleepGen v1.0.9 (Optimized)")
    print(f"   Path: {skill_path}")
    print(f"   Key improvements: 15 modules, interfaces, dependency injection")
    
    # 运行完整数学审核
    print(f"\n2. Running mathematical audit on optimized version...")
    
    audit_data = {
        'skill_id': 'aisleepgen_v1.0.9_optimized',
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
                
                matrix_cert = None
                for i, cert in enumerate(certificates, 1):
                    theorem = cert.get('theorem', 'Unknown')
                    confidence = cert.get('confidence', 0)
                    validity = cert.get('validity', 'unknown')
                    
                    print(f"   {i}. {theorem}")
                    print(f"      Confidence: {confidence:.3f}")
                    print(f"      Validity: {validity}")
                    
                    if 'matrix' in theorem.lower():
                        matrix_cert = cert
                
                # 计算指标
                confidences = [c.get('confidence', 0) for c in certificates]
                avg_confidence = sum(confidences) / len(confidences)
                
                valid_count = sum(1 for c in certificates if c.get('validity') == 'valid')
                validity_rate = valid_count / len(certificates)
                
                print(f"\n   Summary Metrics:")
                print(f"   Average Confidence: {avg_confidence:.3f}")
                print(f"   Validity Rate: {validity_rate:.1%}")
                
                # 特别关注矩阵分解
                if matrix_cert:
                    matrix_conf = matrix_cert.get('confidence', 0)
                    matrix_valid = matrix_cert.get('validity', 'unknown')
                    
                    print(f"\n   Matrix Decomposition Analysis:")
                    print(f"   Confidence: {matrix_conf:.3f}")
                    print(f"   Validity: {matrix_valid}")
                    
                    # 与之前版本比较
                    previous_matrix_conf = 0.700
                    improvement = matrix_conf - previous_matrix_conf
                    
                    print(f"   Previous version: {previous_matrix_conf:.3f}")
                    print(f"   Improvement: {improvement:+.3f}")
                    
                    if improvement > 0:
                        print(f"   ✅ MATRIX DECOMPOSITION IMPROVED!")
                        if matrix_conf >= 0.850:
                            print(f"   🎉 TARGET ACHIEVED: ≥0.850!")
                        else:
                            print(f"   📈 Progress: {matrix_conf:.3f}/0.850")
                    else:
                        print(f"   ⚠️ No improvement in matrix decomposition")
            
            # 保存报告
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            report = {
                'audit_id': f'AISLEEPGEN_OPTIMIZED_AUDIT_{timestamp}',
                'skill': {
                    'id': 'aisleepgen_v1.0.9',
                    'name': 'AISleepGen Optimized Version',
                    'version': '1.0.9_optimized',
                    'path': skill_path,
                    'module_count': 15,
                    'optimizations': [
                        'interface_modules',
                        'dependency_injection',
                        'hierarchical_structure',
                        'small_focused_modules'
                    ]
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
                    'matrix_decomposition_confidence': matrix_cert.get('confidence', 0) if matrix_cert else 0,
                    'matrix_decomposition_validity': matrix_cert.get('validity', 'unknown') if matrix_cert else 'unknown'
                },
                'comparison': {
                    'v1.0.7_fixed': {
                        'overall_score': 79.95,
                        'matrix_confidence': 0.700,
                        'module_count': 1
                    },
                    'v1.0.8_modular': {
                        'overall_score': 79.95,
                        'matrix_confidence': 0.700,
                        'module_count': 4
                    },
                    'v1.0.9_optimized': {
                        'overall_score': result.get('overall_mathematical_score', 0),
                        'matrix_confidence': matrix_cert.get('confidence', 0) if matrix_cert else 0,
                        'module_count': 15
                    }
                },
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            report_file = f'aisleepgen_optimized_audit_{timestamp}.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n4. Audit Report:")
            print(f"   Report ID: {report['audit_id']}")
            print(f"   Saved to: {report_file}")
            
            # 发布建议
            print(f"\n5. RELEASE DECISION:")
            score = report['summary']['overall_score']
            matrix_conf = report['summary']['matrix_decomposition_confidence']
            
            release_criteria = [
                score >= 70,
                matrix_conf >= 0.850,
                report['summary']['certificate_count'] >= 3
            ]
            
            criteria_met = sum(release_criteria)
            
            print(f"   Release Criteria:")
            print(f"   1. Overall score ≥ 70: {score}/100 {'✅' if score >= 70 else '❌'}")
            print(f"   2. Matrix confidence ≥ 0.850: {matrix_conf:.3f} {'✅' if matrix_conf >= 0.850 else '❌'}")
            print(f"   3. Certificates ≥ 3: {report['summary']['certificate_count']} {'✅' if report['summary']['certificate_count'] >= 3 else '❌'}")
            
            if all(release_criteria):
                print(f"\n   🎉 ALL CRITERIA MET - READY FOR RELEASE!")
                print(f"   Optimization successful: Matrix confidence improved to {matrix_conf:.3f}")
            elif criteria_met >= 2:
                print(f"\n   ⚠️ PARTIAL SUCCESS - Consider release with notes")
                print(f"   {criteria_met}/3 criteria met")
            else:
                print(f"\n   ❌ OPTIMIZATION NEEDED - Do not release yet")
                print(f"   Only {criteria_met}/3 criteria met")
            
            return all(release_criteria)
            
        else:
            print(f"   ERROR: Audit failed with HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def compare_all_versions():
    """比较所有版本"""
    print(f"\n6. VERSION COMPARISON:")
    print(f"   {'Version':<20} {'Score':<10} {'Matrix':<10} {'Modules':<10}")
    print(f"   {'-'*20} {'-'*10} {'-'*10} {'-'*10}")
    print(f"   v1.0.7_fixed       79.95      0.700      1")
    print(f"   v1.0.8_modular     79.95      0.700      4")
    print(f"   v1.0.9_optimized   Waiting for audit results...")
    
    return True

def main():
    """主函数"""
    print("OPTIMIZED AISLEEPGEN MATHEMATICAL AUDIT")
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
    release_ready = audit_optimized_version()
    
    # 比较
    compare_all_versions()
    
    print("\n" + "=" * 70)
    if release_ready:
        print("CONCLUSION: OPTIMIZATION SUCCESSFUL!")
        print("Matrix decomposition confidence improved to ≥0.850")
        print("v1.0.9_optimized is READY FOR RELEASE")
    else:
        print("CONCLUSION: OPTIMIZATION PARTIAL SUCCESS")
        print("Matrix decomposition may need further work")
        print("Check audit results for details")
    
    print("=" * 70)
    return release_ready

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)