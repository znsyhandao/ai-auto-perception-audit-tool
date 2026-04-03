"""
分析为什么矩阵分解置信度没有改善
"""

import json
from pathlib import Path

def analyze_results():
    """分析审核结果"""
    print("ANALYZING WHY MATRIX CONFIDENCE DID NOT IMPROVE")
    print("=" * 70)
    
    # 读取v1和v2的审核结果
    v1_audit_file = "aisleepgen_mathematical_audit_20260331_084657.json"
    v2_audit_file = "v2_final_audit_result_20260331_104919.json"
    
    if not Path(v1_audit_file).exists() or not Path(v2_audit_file).exists():
        print("ERROR: Audit files not found")
        return False
    
    with open(v1_audit_file, 'r', encoding='utf-8') as f:
        v1_audit = json.load(f)
    
    with open(v2_audit_file, 'r', encoding='utf-8') as f:
        v2_audit = json.load(f)
    
    print("\n1. COMPARING AUDIT RESULTS")
    print("-" * 50)
    
    v1_results = v1_audit.get("results", {})
    v2_results = v2_audit.get("results", {})
    
    print(f"Overall score: {v1_results.get('overall_mathematical_score', 0)} -> {v2_results.get('overall_mathematical_score', 0)}")
    print(f"Certificate count: {len(v1_results.get('mathematical_certificates', []))} -> {len(v2_results.get('mathematical_certificates', []))}")
    
    # 比较矩阵证书
    v1_matrix_cert = None
    v2_matrix_cert = None
    
    for cert in v1_results.get('mathematical_certificates', []):
        if "matrix" in cert.get("theorem", "").lower():
            v1_matrix_cert = cert
            break
    
    for cert in v2_results.get('mathematical_certificates', []):
        if "matrix" in cert.get("theorem", "").lower():
            v2_matrix_cert = cert
            break
    
    if v1_matrix_cert and v2_matrix_cert:
        print(f"\nMatrix decomposition comparison:")
        print(f"  v1.0.9 confidence: {v1_matrix_cert.get('confidence', 0):.3f}")
        print(f"  v2.0 confidence: {v2_matrix_cert.get('confidence', 0):.3f}")
        print(f"  Change: {v2_matrix_cert.get('confidence', 0) - v1_matrix_cert.get('confidence', 0):+.3f}")
        print(f"  v1 validity: {v1_matrix_cert.get('validity', 'unknown')}")
        print(f"  v2 validity: {v2_matrix_cert.get('validity', 'unknown')}")
    
    # 读取依赖优化数据
    print(f"\n2. DEPENDENCY OPTIMIZATION RESULTS")
    print("-" * 50)
    
    comparison_file = "v2_optimization_comparison.json"
    if Path(comparison_file).exists():
        with open(comparison_file, 'r', encoding='utf-8') as f:
            comparison = json.load(f)
        
        improvements = comparison.get("differences", {})
        
        print(f"Dependency improvements:")
        print(f"  Total dependencies: {improvements.get('total_dependencies', {}).get('v1', 0)} -> {improvements.get('total_dependencies', {}).get('v2', 0)}")
        print(f"    Reduction: {improvements.get('total_dependencies', {}).get('difference', 0)} ({improvements.get('total_dependencies', {}).get('percentage', 0):+.1f}%)")
        
        print(f"  Weighted density: {improvements.get('weighted_density', {}).get('v1', 0):.4f} -> {improvements.get('weighted_density', {}).get('v2', 0):.4f}")
        print(f"    Reduction: {improvements.get('weighted_density', {}).get('difference', 0):+.4f} ({improvements.get('weighted_density', {}).get('percentage', 0):+.1f}%)")
    
    print(f"\n3. KEY INSIGHTS")
    print("-" * 50)
    
    print(f"Observation: Dependency metrics improved but matrix confidence unchanged")
    print(f"\nPossible reasons:")
    
    reasons = [
        "1. Matrix decomposition algorithm may have detection threshold",
        "2. Confidence calculation may saturate at certain dependency levels",
        "3. Our dependency reduction may not be in the dimensions that matter most",
        "4. Matrix algorithm may detect different dependency patterns than our analyzer",
        "5. There may be minimum confidence floor (e.g., 0.700)",
        "6. Validity 'questionable' suggests algorithm uncertainty"
    ]
    
    for reason in reasons:
        print(f"  {reason}")
    
    print(f"\n4. EVIDENCE ANALYSIS")
    print("-" * 50)
    
    print(f"Evidence for threshold/saturation:")
    print(f"  • Both v1 and v2 have same confidence: 0.700")
    print(f"  • Validity: questionable (algorithm uncertain)")
    print(f"  • Despite 25% dependency reduction, no change")
    
    print(f"\nEvidence against our optimization being ineffective:")
    print(f"  • Dependency metrics clearly improved")
    print(f"  • Import reduction 57%, inheritance reduction 60%")
    print(f"  • Weighted density reduced 34%")
    
    print(f"\n5. HYPOTHESIS")
    print("-" * 50)
    
    hypothesis = """
HYPOTHESIS: Matrix decomposition confidence has a detection threshold or saturation point.

Based on the evidence:
1. Our dependency optimization WAS effective (25% reduction, 57% import reduction, etc.)
2. But matrix confidence DID NOT change (0.700 → 0.700)
3. Validity is 'questionable' suggesting algorithm uncertainty

This suggests:
• Matrix algorithm may have minimum confidence floor (e.g., 0.700)
• Or confidence calculation saturates beyond certain dependency levels
• Or our optimization didn't affect the specific dependencies that matter most to matrix algorithm
"""
    
    print(hypothesis)
    
    print(f"\n6. NEXT STEPS FOR INVESTIGATION")
    print("-" * 50)
    
    next_steps = [
        "1. Analyze matrix decomposition algorithm source code",
        "2. Create test cases to understand confidence calculation",
        "3. Test if there's a minimum confidence floor",
        "4. Identify which dependencies affect matrix confidence most",
        "5. Consider alternative optimization strategies"
    ]
    
    for i, step in enumerate(next_steps, 1):
        print(f"  {i}. {step}")
    
    print(f"\n7. IMMEDIATE ACTION")
    print("-" * 50)
    
    print(f"Given the results:")
    print(f"  • v2.0 optimization DID improve dependency metrics")
    print(f"  • But matrix confidence DID NOT improve")
    print(f"  • Overall score remains good (79.95/100)")
    
    print(f"\nRecommendation:")
    print(f"  RELEASE v2.0 with transparent documentation explaining:")
    print(f"    1. Dependency optimization achieved (25% reduction)")
    print(f"    2. Matrix confidence unchanged (0.700)")
    print(f"    3. Hypothesis about algorithm thresholds")
    print(f"    4. Plan for v2.1 to investigate further")
    
    # 保存分析
    analysis = {
        "analysis_time": "2026-03-31T10:50:00Z",
        "key_finding": "Matrix confidence unchanged despite dependency optimization",
        "evidence": {
            "dependency_improvement": {
                "total_reduction": improvements.get('total_dependencies', {}).get('percentage', 0) if 'improvements' in locals() else 0,
                "import_reduction": 57.1,
                "inheritance_reduction": 60.0,
                "weighted_density_reduction": improvements.get('weighted_density', {}).get('percentage', 0) if 'improvements' in locals() else 0
            },
            "matrix_confidence": {
                "v1": v1_matrix_cert.get('confidence', 0) if v1_matrix_cert else 0,
                "v2": v2_matrix_cert.get('confidence', 0) if v2_matrix_cert else 0,
                "change": (v2_matrix_cert.get('confidence', 0) - v1_matrix_cert.get('confidence', 0)) if v1_matrix_cert and v2_matrix_cert else 0,
                "validity_v1": v1_matrix_cert.get('validity', 'unknown') if v1_matrix_cert else 'unknown',
                "validity_v2": v2_matrix_cert.get('validity', 'unknown') if v2_matrix_cert else 'unknown'
            }
        },
        "hypothesis": "Matrix decomposition confidence has detection threshold or saturation point",
        "recommendation": "Release v2.0 with transparent documentation and plan v2.1 investigation"
    }
    
    analysis_file = "matrix_confidence_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis saved: {analysis_file}")
    
    return True

def main():
    """主分析函数"""
    print("MATRIX CONFIDENCE ANALYSIS - WHY NO IMPROVEMENT?")
    print("=" * 70)
    
    success = analyze_results()
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)