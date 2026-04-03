"""
分析其他数学审核类型的表现
"""

import requests
import json
import time
from pathlib import Path

def run_complete_audit():
    """运行完整数学审核"""
    print("ANALYZING OTHER MATHEMATICAL AUDIT TYPES")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v2.1_transparent_release"
    
    # 检查服务
    print("1. Checking mathematical audit service...")
    try:
        response = requests.get('http://localhost:8010/health', timeout=5)
        if response.status_code == 200:
            print("   Service healthy")
        else:
            print(f"   Service not healthy: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"   Service not reachable: {e}")
        return None
    
    # 运行完整审核（所有类型）
    audit_data = {
        'skill_id': 'aisleepgen_v2.1_other_audits',
        'skill_path': skill_path,
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 3
    }
    
    print(f"\n2. Running complete mathematical audit...")
    print(f"   Target: {skill_path}")
    print(f"   Audit types: maclaurin, taylor, fourier, matrix, proof")
    
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
            
            # 提取总体结果
            overall_score = result.get('overall_mathematical_score', 0)
            certificates = result.get('mathematical_certificates', [])
            
            print(f"Overall mathematical score: {overall_score:.2f}/100")
            print(f"Mathematical certificates: {len(certificates)}")
            
            # 分析每个审核类型
            print(f"\n4. Individual audit type analysis:")
            print("-" * 50)
            
            audit_results = {}
            
            for cert in certificates:
                theorem = cert.get('theorem', '')
                confidence = cert.get('confidence', 0)
                validity = cert.get('validity', 'unknown')
                
                # 确定审核类型
                audit_type = 'unknown'
                if 'maclaurin' in theorem.lower():
                    audit_type = 'maclaurin'
                elif 'taylor' in theorem.lower():
                    audit_type = 'taylor'
                elif 'fourier' in theorem.lower():
                    audit_type = 'fourier'
                elif 'matrix' in theorem.lower():
                    audit_type = 'matrix'
                elif 'proof' in theorem.lower():
                    audit_type = 'proof'
                
                audit_results[audit_type] = {
                    'confidence': confidence,
                    'validity': validity,
                    'theorem': theorem
                }
                
                print(f"{audit_type:10} | Confidence: {confidence:.3f} | Validity: {validity:12} | {theorem[:40]}...")
            
            print(f"\n5. Comparison with matrix results:")
            print("-" * 50)
            
            matrix_conf = audit_results.get('matrix', {}).get('confidence', 0)
            
            print(f"Matrix confidence (baseline): {matrix_conf:.3f}")
            print(f"\nOther audit types vs matrix:")
            
            for audit_type, data in audit_results.items():
                if audit_type != 'matrix':
                    conf = data['confidence']
                    diff = conf - matrix_conf
                    print(f"  {audit_type:10}: {conf:.3f} ({diff:+.3f} difference)")
            
            # 识别优化机会
            print(f"\n6. Optimization opportunities:")
            print("-" * 50)
            
            opportunities = []
            
            for audit_type, data in audit_results.items():
                if audit_type != 'matrix':
                    conf = data['confidence']
                    validity = data['validity']
                    
                    if conf < 0.800:
                        opportunities.append({
                            'type': audit_type,
                            'current': conf,
                            'target': 0.850,
                            'gap': 0.850 - conf,
                            'priority': 'high' if conf < 0.700 else 'medium'
                        })
                    elif validity != 'valid':
                        opportunities.append({
                            'type': audit_type,
                            'issue': f'validity: {validity}',
                            'priority': 'medium'
                        })
            
            if opportunities:
                print(f"Found {len(opportunities)} optimization opportunities:")
                for opp in opportunities:
                    if 'current' in opp:
                        print(f"  {opp['type']:10}: {opp['current']:.3f} → 0.850 (gap: {opp['gap']:.3f}) - {opp['priority']} priority")
                    else:
                        print(f"  {opp['type']:10}: {opp['issue']} - {opp['priority']} priority")
            else:
                print("All audit types performing well!")
            
            # 保存结果
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            result_file = f"other_audit_types_analysis_{timestamp}.json"
            
            analysis = {
                "analysis_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "skill_version": "v2.1_transparent_release",
                "overall_score": overall_score,
                "audit_time": audit_time,
                "audit_results": audit_results,
                "matrix_baseline": matrix_conf,
                "optimization_opportunities": opportunities,
                "recommendations": []
            }
            
            # 生成建议
            if matrix_conf == 0.700:
                analysis["recommendations"].append({
                    "type": "strategy",
                    "content": "Matrix algorithm shows baseline behavior (0.700). Focus optimization on other audit types.",
                    "priority": "high"
                })
            
            for opp in opportunities:
                if opp.get('priority') == 'high':
                    analysis["recommendations"].append({
                        "type": "optimization",
                        "audit_type": opp['type'],
                        "content": f"Optimize {opp['type']} from {opp['current']:.3f} to 0.850+",
                        "priority": "high"
                    })
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            print(f"\nAnalysis saved: {result_file}")
            
            return analysis
            
        else:
            print(f"   ERROR: Audit failed with HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ERROR running audit: {e}")
        return None

def analyze_algorithm_formulas():
    """分析其他审核类型的算法公式"""
    print(f"\n7. Understanding other audit type algorithms:")
    print("-" * 50)
    
    formulas = {
        'maclaurin': {
            'formula': 'confidence = convergence_rate',
            'detects': 'Code complexity and convergence patterns',
            'optimization': 'Improve code structure and algorithm efficiency'
        },
        'taylor': {
            'formula': 'confidence = 1.0 - (total_complexity × 0.1)',
            'detects': 'Algorithm complexity and performance',
            'optimization': 'Simplify algorithms, reduce complexity'
        },
        'fourier': {
            'formula': 'confidence = 0.7 + (pattern_diversity × 0.05)',
            'detects': 'Code pattern diversity and structure',
            'optimization': 'Increase code pattern diversity'
        },
        'proof': {
            'formula': 'confidence = overall_confidence',
            'detects': 'Mathematical correctness and proof validity',
            'optimization': 'Improve code correctness and documentation'
        }
    }
    
    print("Algorithm formulas and what they detect:")
    for audit_type, info in formulas.items():
        print(f"\n{audit_type.upper():10}")
        print(f"  Formula: {info['formula']}")
        print(f"  Detects: {info['detects']}")
        print(f"  Optimization: {info['optimization']}")
    
    return formulas

def main():
    """主函数"""
    print("ANALYSIS OF OTHER MATHEMATICAL AUDIT TYPES")
    print("=" * 70)
    
    print("\nBased on 'Understanding over passing' principle:")
    print("1. First understand current performance")
    print("2. Identify optimization opportunities")
    print("3. Focus on responsive audit types")
    
    analysis = run_complete_audit()
    formulas = analyze_algorithm_formulas()
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE - READY FOR TARGETED OPTIMIZATION")
    print("=" * 70)
    
    if analysis:
        print(f"\nKey findings:")
        print(f"- Overall score: {analysis['overall_score']:.2f}/100")
        print(f"- Matrix baseline: {analysis['matrix_baseline']:.3f}")
        
        opportunities = analysis.get('optimization_opportunities', [])
        if opportunities:
            print(f"- Optimization opportunities: {len(opportunities)}")
            for opp in opportunities[:3]:  # 只显示前3个
                if 'current' in opp:
                    print(f"  • {opp['type']}: {opp['current']:.3f} → 0.850")
        
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print(f"\nRecommendations:")
            for rec in recommendations:
                print(f"  [{rec['priority'].upper()}] {rec['content']}")
    
    print(f"\nNext steps:")
    print("1. Based on analysis, select highest priority audit type")
    print("2. Apply 'understanding over passing' principle")
    print("3. Design targeted optimization strategy")
    print("4. Implement and verify improvements")
    
    return analysis is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)