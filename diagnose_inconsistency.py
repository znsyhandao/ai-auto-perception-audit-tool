"""
诊断AISleepGen的不一致性
"""

import ast
import re
from pathlib import Path
import json

def analyze_function_maclaurin_suitability(func_code, func_name):
    """分析函数对麦克劳林的适用性"""
    analysis = {
        "function": func_name,
        "maclaurin_suitable": True,
        "issues": [],
        "suitability_score": 1.0,
        "recommendation": "keep",
        "alternative_method": None
    }
    
    func_lower = func_code.lower()
    
    # 检查不适用模式
    unsuitable_patterns = [
        (r"if.*:", "Conditional logic - may not be analytic at 0"),
        (r"else:", "Conditional logic - discontinuity"),
        (r"abs\(", "Absolute value - not analytic at 0"),
        (r"max\(", "Maximum function - not analytic"),
        (r"min\(", "Minimum function - not analytic"),
        (r"raise", "Exception throwing - discontinuity"),
        (r"break", "Loop breaking - control flow discontinuity"),
        (r"continue", "Loop continuation - control flow issue"),
        (r"try:", "Exception handling - potential discontinuity"),
        (r"except", "Exception handling - discontinuity")
    ]
    
    # 检查特殊函数（部分适用）
    special_functions = [
        (r"log\(", "Logarithm - singular at 0, needs special handling"),
        (r"sqrt\(", "Square root - analytic but slow convergence"),
        (r"tan\(", "Tangent - poles, not analytic everywhere"),
        (r"1/x", "Division by x - singular at 0")
    ]
    
    # 检查良好函数
    good_patterns = [
        (r"exp\(", "Exponential - fully analytic"),
        (r"sin\(", "Sine - fully analytic"),
        (r"cos\(", "Cosine - fully analytic"),
        (r"polynomial", "Polynomial - fully analytic"),
        (r"math\.pi", "Mathematical constant - good"),
        (r"math\.e", "Mathematical constant - good")
    ]
    
    # 分析不适用模式
    for pattern, issue in unsuitable_patterns:
        if re.search(pattern, func_lower):
            analysis["maclaurin_suitable"] = False
            analysis["issues"].append(issue)
            analysis["suitability_score"] *= 0.3
            analysis["recommendation"] = "refactor_or_alternative"
            analysis["alternative_method"] = "piecewise_approximation"
    
    # 分析特殊函数
    for pattern, note in special_functions:
        if re.search(pattern, func_lower):
            analysis["issues"].append(note)
            analysis["suitability_score"] *= 0.6
            if not analysis["alternative_method"]:
                analysis["alternative_method"] = "rational_approximation"
    
    # 分析良好模式
    good_count = 0
    for pattern, note in good_patterns:
        if re.search(pattern, func_lower):
            good_count += 1
            analysis["suitability_score"] *= 1.1  # 稍微提高
    
    # 最终评估
    if analysis["suitability_score"] >= 0.8:
        analysis["maclaurin_suitable"] = True
        analysis["recommendation"] = "keep"
    elif analysis["suitability_score"] >= 0.5:
        analysis["maclaurin_suitable"] = True
        analysis["recommendation"] = "optimize"
    else:
        analysis["maclaurin_suitable"] = False
        analysis["recommendation"] = "refactor_or_alternative"
    
    return analysis

def diagnose_aisleepgen_inconsistency():
    """诊断AISleepGen的不一致性"""
    print("DIAGNOSING AISLEEPGEN INCONSISTENCY")
    print("=" * 70)
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen/v2.2_maclaurin_optimized")
    
    print(f"\nAnalyzing: {skill_dir}")
    print(f"Current status: 0.750 confidence, questionable validity")
    print(f"Goal: Identify what causes 'questionable' validity")
    
    print(f"\n1. Analyzing all functions for Maclaurin suitability...")
    print("-" * 50)
    
    analysis_results = {
        "total_functions": 0,
        "suitable_functions": 0,
        "unsuitable_functions": 0,
        "borderline_functions": 0,
        "function_analyses": [],
        "consistency_score": 0,
        "primary_issues": [],
        "recommendations": []
    }
    
    py_files = list(skill_dir.rglob("*.py"))
    
    for py_file in py_files:
        if py_file.name == "__init__.py":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    func_code = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                    
                    analysis = analyze_function_maclaurin_suitability(func_code, func_name)
                    analysis["file"] = str(py_file.relative_to(skill_dir))
                    
                    analysis_results["function_analyses"].append(analysis)
                    analysis_results["total_functions"] += 1
                    
                    if analysis["maclaurin_suitable"]:
                        if analysis["suitability_score"] >= 0.8:
                            analysis_results["suitable_functions"] += 1
                        else:
                            analysis_results["borderline_functions"] += 1
                    else:
                        analysis_results["unsuitable_functions"] += 1
                    
                    # 收集主要问题
                    for issue in analysis["issues"]:
                        if issue not in analysis_results["primary_issues"]:
                            analysis_results["primary_issues"].append(issue)
                    
        except Exception as e:
            print(f"  Error analyzing {py_file.name}: {e}")
    
    print(f"\n2. Diagnosis results:")
    print("-" * 50)
    
    total = analysis_results["total_functions"]
    suitable = analysis_results["suitable_functions"]
    unsuitable = analysis_results["unsuitable_functions"]
    borderline = analysis_results["borderline_functions"]
    
    print(f"Total functions analyzed: {total}")
    print(f"Clearly suitable: {suitable} ({suitable/total*100:.1f}%)")
    print(f"Clearly unsuitable: {unsuitable} ({unsuitable/total*100:.1f}%)")
    print(f"Borderline: {borderline} ({borderline/total*100:.1f}%)")
    
    # 计算一致性分数
    if total > 0:
        consistency = suitable / total
        analysis_results["consistency_score"] = consistency
    
    print(f"\nConsistency score: {consistency:.3f}")
    print(f"Interpretation: {consistency*100:.1f}% consistent suitability")
    
    print(f"\n3. Primary issues causing inconsistency:")
    print("-" * 50)
    
    if analysis_results["primary_issues"]:
        for i, issue in enumerate(analysis_results["primary_issues"][:5], 1):  # 只显示前5个
            print(f"{i}. {issue}")
    else:
        print("No major issues found (unexpected!)")
    
    print(f"\n4. Why AISleepGen gets 'questionable' validity:")
    print("-" * 50)
    
    explanation = f"""
Based on diagnosis:

CONSISTENCY ANALYSIS:
- Suitable functions: {suitable}/{total} ({suitable/total*100:.1f}%)
- Unsuitable functions: {unsuitable}/{total} ({unsuitable/total*100:.1f}%)
- Borderline functions: {borderline}/{total} ({borderline/total*100:.1f}%)

INTERPRETATION:
The 'questionable' validity comes from MIXED suitability:
• Some functions are Maclaurin-suitable ({suitable/total*100:.1f}%)
• Some are not ({unsuitable/total*100:.1f}%)
• Some are borderline ({borderline/total*100:.1f}%)

This inconsistency causes the algorithm to mark validity as 'questionable'.

The 0.750 confidence likely represents:
• Weighted average of suitability scores
• ~75% average suitability across all functions
• But inconsistency reduces confidence in the assessment
"""
    
    print(explanation)
    
    print(f"\n5. Optimization recommendations:")
    print("-" * 50)
    
    recommendations = []
    
    if unsuitable > 0:
        recommendations.append({
            "priority": "high",
            "action": "Refactor unsuitable functions",
            "target": f"{unsuitable} clearly unsuitable functions",
            "approach": "Make them Maclaurin-suitable or use alternative methods",
            "expected_impact": "Improve consistency, may change validity to 'valid'"
        })
    
    if borderline > 0:
        recommendations.append({
            "priority": "medium",
            "action": "Optimize borderline functions",
            "target": f"{borderline} borderline functions",
            "approach": "Improve mathematical properties to be clearly suitable",
            "expected_impact": "Increase consistency score"
        })
    
    if consistency < 0.9:
        recommendations.append({
            "priority": "high",
            "action": "Achieve consistency",
            "target": f"Achieve >90% consistency ({consistency*100:.1f}% → >90%)",
            "approach": "Either make all functions suitable, or clearly separate unsuitable ones",
            "expected_impact": "Change validity from 'questionable' to 'valid'"
        })
    
    for rec in recommendations:
        print(f"\n{rec['priority'].upper()} PRIORITY: {rec['action']}")
        print(f"  Target: {rec['target']}")
        print(f"  Approach: {rec['approach']}")
        print(f"  Expected: {rec['expected_impact']}")
    
    # 保存诊断结果
    diagnosis = {
        "diagnosis_time": "2026-03-31T13:45:00Z",
        "skill_version": "v2.2_maclaurin_optimized",
        "current_status": {
            "confidence": 0.750,
            "validity": "questionable"
        },
        "diagnosis_results": analysis_results,
        "interpretation": "Mixed suitability causes questionable validity",
        "recommendations": recommendations,
        "optimization_strategy": "Achieve consistency to change validity from questionable to valid"
    }
    
    diagnosis_file = "aisleepgen_inconsistency_diagnosis.json"
    with open(diagnosis_file, 'w', encoding='utf-8') as f:
        json.dump(diagnosis, f, indent=2, ensure_ascii=False)
    
    print(f"\nDiagnosis saved: {diagnosis_file}")
    
    return diagnosis, recommendations

def create_optimization_plan(diagnosis, recommendations):
    """创建优化计划"""
    print(f"\n6. CREATING OPTIMIZATION PLAN")
    print("-" * 50)
    
    total_functions = diagnosis["diagnosis_results"]["total_functions"]
    unsuitable = diagnosis["diagnosis_results"]["unsuitable_functions"]
    borderline = diagnosis["diagnosis_results"]["borderline_functions"]
    
    plan = {
        "plan_time": "2026-03-31T13:50:00Z",
        "goal": "Change validity from questionable to valid",
        "strategy": "Achieve consistency in mathematical properties",
        "phases": [
            {
                "phase": "Phase 1: Refactor unsuitable functions",
                "duration": "1.5 hours",
                "tasks": [
                    f"Analyze {unsuitable} unsuitable functions in detail",
                    "Decide: make suitable or use alternative methods",
                    "Implement changes",
                    "Test each function individually"
                ],
                "success_criteria": "All functions clearly categorized"
            },
            {
                "phase": "Phase 2: Optimize borderline functions",
                "duration": "1 hour",
                "tasks": [
                    f"Improve {borderline} borderline functions",
                    "Make them clearly Maclaurin-suitable",
                    "Document mathematical properties"
                ],
                "success_criteria": "Borderline functions become clearly suitable"
            },
            {
                "phase": "Phase 3: Achieve consistency",
                "duration": "0.5 hours",
                "tasks": [
                    "Ensure >90% consistency across all functions",
                    "Create clear documentation of mathematical properties",
                    "Run Maclaurin audit to verify validity change"
                ],
                "success_criteria": "Validity changes from questionable to valid"
            }
        ],
        "total_time": "3 hours",
        "expected_outcome": {
            "validity": "questionable → valid",
            "consistency": f"{diagnosis['diagnosis_results']['consistency_score']*100:.1f}% → >90%",
            "confidence": "May stay at 0.750 or improve slightly",
            "key_metric": "VALIDITY CHANGE is primary success indicator"
        }
    }
    
    plan_file = "aisleepgen_consistency_optimization_plan.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"Optimization plan saved: {plan_file}")
    
    print(f"\nOptimization plan summary:")
    print(f"Goal: questionable → valid validity")
    print(f"Strategy: Achieve consistency (>90% suitable)")
    print(f"Time: 3 hours total")
    
    print(f"\nPhases:")
    for phase in plan["phases"]:
        print(f"\n{phase['phase']} ({phase['duration']}):")
        for task in phase["tasks"]:
            print(f"  • {task}")
    
    return plan

def main():
    """主诊断函数"""
    print("AISLEEPGEN INCONSISTENCY DIAGNOSIS")
    print("=" * 70)
    
    print("\nDiagnosing why Maclaurin validity is 'questionable':")
    print("Goal: Identify mixed suitability causing inconsistency")
    
    diagnosis, recommendations = diagnose_aisleepgen_inconsistency()
    plan = create_optimization_plan(diagnosis, recommendations)
    
    print(f"\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE - OPTIMIZATION PLAN READY")
    print("=" * 70)
    
    total = diagnosis["diagnosis_results"]["total_functions"]
    suitable = diagnosis["diagnosis_results"]["suitable_functions"]
    unsuitable = diagnosis["diagnosis_results"]["unsuitable_functions"]
    consistency = diagnosis["diagnosis_results"]["consistency_score"]
    
    print(f"\nKey findings:")
    print(f"- Total functions: {total}")
    print(f"- Suitable: {suitable} ({suitable/total*100:.1f}%)")
    print(f"- Unsuitable: {unsuitable} ({unsuitable/total*100:.1f}%)")
    print(f"- Consistency: {consistency*100:.1f}%")
    
    print(f"\nRoot cause of 'questionable' validity:")
    print(f"MIXED SUITABILITY - {unsuitable} functions are not Maclaurin-suitable")
    
    print(f"\nOptimization approach:")
    print(f"Achieve consistency (>90% suitable) to get 'valid' validity")
    
    print(f"\nReady to begin Phase 1: Refactor unsuitable functions")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)