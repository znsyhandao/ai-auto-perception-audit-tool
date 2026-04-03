"""
验证v2.0优化效果
"""

import json
from pathlib import Path

def compare_dependency_metrics():
    """比较优化前后的依赖指标"""
    print("VERIFYING v2.0 OPTIMIZATION EFFECTIVENESS")
    print("=" * 70)
    
    # 读取优化前的分析报告
    v1_report_file = "enhanced_dependency_analysis.json"
    if not Path(v1_report_file).exists():
        print(f"ERROR: v1 analysis report not found: {v1_report_file}")
        return False
    
    with open(v1_report_file, 'r', encoding='utf-8') as f:
        v1_report = json.load(f)
    
    print(f"\n1. v1.0.9_optimized (优化前) 依赖指标:")
    v1_metrics = v1_report.get("metrics", {})
    
    print(f"   Total dependencies: {v1_metrics.get('total_dependencies', 0)}")
    print(f"   Module count: {v1_metrics.get('module_count', 0)}")
    print(f"   Weighted density: {v1_metrics.get('weighted_density', 0):.4f}")
    print(f"   Estimated confidence: {v1_metrics.get('estimated_confidence', 0):.3f}")
    print(f"   Current audit confidence: {v1_metrics.get('current_audit_confidence', 0):.3f}")
    
    print(f"\n   Dependency type breakdown:")
    for dep_type, count in v1_metrics.get('dependency_types', {}).items():
        weight = v1_metrics.get('weighted_dependencies', {}).get(dep_type, 0)
        print(f"     {dep_type}: {count} deps, weight: {weight:.1f}")
    
    # 分析优化后的版本
    print(f"\n2. Analyzing v2.0_targeted (优化后)...")
    
    # 重新运行增强分析（简化版）
    from enhanced_dependency_analyzer import EnhancedDependencyAnalyzer
    
    v2_path = "D:/openclaw/releases/AISleepGen/v2.0_targeted"
    analyzer = EnhancedDependencyAnalyzer(v2_path)
    
    print(f"   Analyzing optimized version...")
    dependencies = analyzer.analyze_skill()
    v2_metrics = analyzer.calculate_metrics()
    
    print(f"\n3. v2.0_targeted (优化后) 依赖指标:")
    print(f"   Total dependencies: {v2_metrics.get('total_dependencies', 0)}")
    print(f"   Module count: {v2_metrics.get('module_count', 0)}")
    print(f"   Weighted density: {v2_metrics.get('weighted_density', 0):.4f}")
    print(f"   Estimated confidence: {v2_metrics.get('estimated_confidence', 0):.3f}")
    
    print(f"\n   Dependency type breakdown:")
    for dep_type, count in v2_metrics.get('dependency_types', {}).items():
        weight = v2_metrics.get('weighted_dependencies', {}).get(dep_type, 0)
        print(f"     {dep_type}: {count} deps, weight: {weight:.1f}")
    
    # 比较结果
    print(f"\n4. COMPARISON RESULTS:")
    
    total_deps_diff = v2_metrics.get('total_dependencies', 0) - v1_metrics.get('total_dependencies', 0)
    total_deps_pct = (total_deps_diff / v1_metrics.get('total_dependencies', 1)) * 100 if v1_metrics.get('total_dependencies', 0) > 0 else 0
    
    density_diff = v2_metrics.get('weighted_density', 0) - v1_metrics.get('weighted_density', 0)
    density_pct = (density_diff / v1_metrics.get('weighted_density', 1)) * 100 if v1_metrics.get('weighted_density', 0) > 0 else 0
    
    confidence_diff = v2_metrics.get('estimated_confidence', 0) - v1_metrics.get('estimated_confidence', 0)
    
    print(f"   Total dependencies: {total_deps_diff:+.0f} ({total_deps_pct:+.1f}%)")
    print(f"   Weighted density: {density_diff:+.4f} ({density_pct:+.1f}%)")
    print(f"   Estimated confidence: {confidence_diff:+.3f}")
    
    # 按类型比较
    print(f"\n5. Dependency type changes:")
    
    v1_types = v1_metrics.get('dependency_types', {})
    v2_types = v2_metrics.get('dependency_types', {})
    
    all_types = set(list(v1_types.keys()) + list(v2_types.keys()))
    
    for dep_type in sorted(all_types):
        v1_count = v1_types.get(dep_type, 0)
        v2_count = v2_types.get(dep_type, 0)
        
        if v1_count != v2_count:
            diff = v2_count - v1_count
            pct = (diff / v1_count * 100) if v1_count > 0 else 100
            print(f"   {dep_type}: {v1_count} -> {v2_count} ({diff:+.0f}, {pct:+.1f}%)")
    
    # 保存比较报告
    comparison = {
        "comparison_time": "2026-03-31T10:04:00Z",
        "versions": {
            "v1.0.9_optimized": {
                "path": "D:/openclaw/releases/AISleepGen/v1.0.9_optimized",
                "metrics": v1_metrics
            },
            "v2.0_targeted": {
                "path": "D:/openclaw/releases/AISleepGen/v2.0_targeted",
                "metrics": v2_metrics
            }
        },
        "differences": {
            "total_dependencies": {
                "v1": v1_metrics.get('total_dependencies', 0),
                "v2": v2_metrics.get('total_dependencies', 0),
                "difference": total_deps_diff,
                "percentage": total_deps_pct
            },
            "weighted_density": {
                "v1": v1_metrics.get('weighted_density', 0),
                "v2": v2_metrics.get('weighted_density', 0),
                "difference": density_diff,
                "percentage": density_pct
            },
            "estimated_confidence": {
                "v1": v1_metrics.get('estimated_confidence', 0),
                "v2": v2_metrics.get('estimated_confidence', 0),
                "difference": confidence_diff
            }
        },
        "optimization_effectiveness": {
            "import_statement_reduction": v1_types.get('import_statement', 0) - v2_types.get('import_statement', 0),
            "class_inheritance_reduction": v1_types.get('class_inheritance', 0) - v2_types.get('class_inheritance', 0),
            "attribute_access_reduction": v1_types.get('attribute_access', 0) - v2_types.get('attribute_access', 0),
            "method_call_reduction": v1_types.get('method_call', 0) - v2_types.get('method_call', 0)
        },
        "principles_validation": "基于理解的优化验证 - 先理解依赖检测，再针对性优化"
    }
    
    report_file = "v2_optimization_comparison.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"\n6. Comparison report saved: {report_file}")
    
    # 初步结论
    print(f"\n7. PRELIMINARY CONCLUSION:")
    
    if total_deps_diff < 0:
        print(f"   SUCCESS: Total dependencies reduced by {-total_deps_diff}")
    else:
        print(f"   WARNING: Total dependencies increased by {total_deps_diff}")
    
    if density_diff < 0:
        print(f"   SUCCESS: Weighted density reduced by {-density_diff:.4f}")
    else:
        print(f"   WARNING: Weighted density increased by {density_diff:.4f}")
    
    if confidence_diff > 0:
        print(f"   SUCCESS: Estimated confidence increased by {confidence_diff:.3f}")
        print(f"   Expected matrix confidence improvement: {confidence_diff * 0.4:.3f}")
    else:
        print(f"   WARNING: Estimated confidence decreased by {-confidence_diff:.3f}")
    
    print(f"\n8. Next: Run mathematical audit for final verification")
    
    return True

def main():
    """主验证函数"""
    print("v2.0 OPTIMIZATION VERIFICATION - DEPENDENCY METRICS")
    print("=" * 70)
    
    success = compare_dependency_metrics()
    
    print(f"\n" + "=" * 70)
    if success:
        print("VERIFICATION COMPLETE - READY FOR MATHEMATICAL AUDIT")
    else:
        print("VERIFICATION FAILED - CHECK ERRORS")
    
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)