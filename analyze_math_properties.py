"""
分析数学属性以进行轻度优化
"""

import re
from pathlib import Path
import json

def analyze_mathematical_properties():
    """分析数学属性"""
    print("ANALYZING MATHEMATICAL PROPERTIES FOR OPTIMIZATION")
    print("=" * 70)
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen/v2.3_consistency_optimized")
    
    print(f"\nAnalyzing: {skill_dir}")
    print("Looking for mathematical properties that can be optimized")
    
    # 数学属性分析
    property_patterns = [
        {
            "pattern": r"exp\(",
            "property": "exponential_function",
            "quality": "excellent",
            "optimization": "none_needed"
        },
        {
            "pattern": r"sin\(",
            "property": "trigonometric_function", 
            "quality": "excellent",
            "optimization": "none_needed"
        },
        {
            "pattern": r"cos\(",
            "property": "trigonometric_function",
            "quality": "excellent", 
            "optimization": "none_needed"
        },
        {
            "pattern": r"log\(",
            "property": "logarithmic_function",
            "quality": "good",
            "optimization": "improve_near_zero"
        },
        {
            "pattern": r"sqrt\(",
            "property": "square_root",
            "quality": "good",
            "optimization": "improve_convergence"
        },
        {
            "pattern": r"\*\* 0.5",
            "property": "power_half",
            "quality": "good",
            "optimization": "use_sqrt_instead"
        },
        {
            "pattern": r"1/",
            "property": "division",
            "quality": "medium",
            "optimization": "improve_numerical_stability"
        },
        {
            "pattern": r"x\*\*2",
            "property": "quadratic",
            "quality": "excellent",
            "optimization": "none_needed"
        }
    ]
    
    analysis_results = {
        "total_functions": 0,
        "property_counts": {},
        "optimization_opportunities": [],
        "files_analyzed": 0
    }
    
    py_files = list(skill_dir.rglob("*.py"))
    
    for py_file in py_files:
        if py_file.name == "__init__.py":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_properties = []
            
            for prop_info in property_patterns:
                pattern = prop_info["pattern"]
                matches = re.findall(pattern, content)
                
                if matches:
                    count = len(matches)
                    file_properties.append({
                        "property": prop_info["property"],
                        "count": count,
                        "quality": prop_info["quality"],
                        "optimization": prop_info["optimization"]
                    })
                    
                    # 更新总计数
                    if prop_info["property"] not in analysis_results["property_counts"]:
                        analysis_results["property_counts"][prop_info["property"]] = 0
                    analysis_results["property_counts"][prop_info["property"]] += count
            
            if file_properties:
                # 识别优化机会
                for prop in file_properties:
                    if prop["optimization"] != "none_needed":
                        analysis_results["optimization_opportunities"].append({
                            "file": str(py_file.relative_to(skill_dir)),
                            "property": prop["property"],
                            "count": prop["count"],
                            "optimization": prop["optimization"],
                            "quality": prop["quality"]
                        })
                
                analysis_results["files_analyzed"] += 1
                
        except Exception as e:
            print(f"  Error analyzing {py_file.name}: {e}")
    
    print(f"\n1. Mathematical properties found:")
    print("-" * 50)
    
    total_properties = sum(analysis_results["property_counts"].values())
    
    for prop, count in analysis_results["property_counts"].items():
        percentage = count / total_properties * 100 if total_properties > 0 else 0
        print(f"  {prop}: {count} occurrences ({percentage:.1f}%)")
    
    print(f"\n2. Optimization opportunities:")
    print("-" * 50)
    
    if analysis_results["optimization_opportunities"]:
        # 按优化类型分组
        optimizations_by_type = {}
        
        for opp in analysis_results["optimization_opportunities"]:
            opt_type = opp["optimization"]
            if opt_type not in optimizations_by_type:
                optimizations_by_type[opt_type] = []
            optimizations_by_type[opt_type].append(opp)
        
        for opt_type, opportunities in optimizations_by_type.items():
            print(f"\n{opt_type}:")
            for opp in opportunities[:3]:  # 只显示前3个
                print(f"  • {opp['file']}: {opp['property']} ({opp['count']}x)")
            if len(opportunities) > 3:
                print(f"    ... and {len(opportunities)-3} more")
    else:
        print("No optimization opportunities found (excellent!)")
    
    print(f"\n3. Recommended optimizations:")
    print("-" * 50)
    
    recommendations = []
    
    # 基于分析的建议
    if "improve_near_zero" in optimizations_by_type:
        recommendations.append({
            "priority": "high",
            "action": "Improve logarithmic functions near zero",
            "approach": "Use log1p(x) for log(1+x) near zero",
            "files": [opp["file"] for opp in optimizations_by_type["improve_near_zero"][:2]],
            "expected_impact": "Better numerical stability, may improve confidence"
        })
    
    if "improve_convergence" in optimizations_by_type:
        recommendations.append({
            "priority": "medium",
            "action": "Improve square root convergence",
            "approach": "Use optimized sqrt approximations",
            "files": [opp["file"] for opp in optimizations_by_type["improve_convergence"][:2]],
            "expected_impact": "Faster convergence, better numerical properties"
        })
    
    if "improve_numerical_stability" in optimizations_by_type:
        recommendations.append({
            "priority": "medium",
            "action": "Improve division numerical stability",
            "approach": "Add small epsilon to denominators",
            "files": [opp["file"] for opp in optimizations_by_type["improve_numerical_stability"][:2]],
            "expected_impact": "Avoid division by zero, improve stability"
        })
    
    if not recommendations:
        recommendations.append({
            "priority": "low",
            "action": "General mathematical cleanup",
            "approach": "Minor improvements to existing functions",
            "files": ["Select 2-3 files with most mathematical operations"],
            "expected_impact": "Slight confidence improvement (0.750 → 0.760-0.780)"
        })
    
    for rec in recommendations:
        print(f"\n{rec['priority'].upper()} PRIORITY: {rec['action']}")
        print(f"  Approach: {rec['approach']}")
        print(f"  Files: {', '.join(rec['files'][:2])}")
        if len(rec['files']) > 2:
            print(f"    ... and {len(rec['files'])-2} more")
        print(f"  Expected: {rec['expected_impact']}")
    
    print(f"\n4. Implementation plan (45 minutes):")
    print("-" * 50)
    
    plan = """
PHASE 2A: QUICK MATHEMATICAL OPTIMIZATIONS (45 MINUTES)

15:17-15:30 (13 min): Analyze specific functions
• Identify 3-5 key functions with optimization potential
• Focus on logarithmic and division operations

15:30-15:50 (20 min): Implement optimizations
• Apply log1p() for log(1+x) patterns
• Add epsilon to denominators for stability
• Minor mathematical improvements

15:50-16:02 (12 min): Test and verify
• Test each optimized function
• Ensure mathematical correctness
• Prepare for final audit

TOTAL: 45 minutes
EXPECTED: Confidence 0.750 → 0.760-0.780
"""
    
    print(plan)
    
    # 保存分析
    analysis = {
        "analysis_time": "2026-03-31T15:20:00Z",
        "skill_version": "v2.3_consistency_optimized",
        "current_confidence": 0.750,
        "current_validity": "valid",
        "analysis_results": analysis_results,
        "recommendations": recommendations,
        "implementation_plan": "45 minutes of targeted mathematical optimizations"
    }
    
    with open("math_properties_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis saved: math_properties_analysis.json")
    
    return analysis, recommendations

def main():
    """主分析函数"""
    print("MATHEMATICAL PROPERTIES ANALYSIS FOR LIGHT OPTIMIZATION")
    print("=" * 70)
    
    print("\nGoal: Identify quick mathematical improvements")
    print("Target: Confidence 0.750 → 0.760-0.780 (small improvement)")
    
    analysis, recommendations = analyze_mathematical_properties()
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE - READY FOR OPTIMIZATION")
    print("=" * 70)
    
    total_props = sum(analysis["analysis_results"]["property_counts"].values())
    opp_count = len(analysis["analysis_results"]["optimization_opportunities"])
    
    print(f"\nSummary:")
    print(f"- Total mathematical operations: {total_props}")
    print(f"- Optimization opportunities: {opp_count}")
    print(f"- Recommendations: {len(recommendations)}")
    
    print(f"\nReady to begin Phase 2A: Quick mathematical optimizations")
    print(f"Time: 15:20-16:05 (45 minutes)")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)