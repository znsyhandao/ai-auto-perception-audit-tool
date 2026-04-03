"""
识别不适用函数并开始重构
"""

import json
from pathlib import Path

def load_diagnosis_results():
    """加载诊断结果"""
    diagnosis_file = "aisleepgen_inconsistency_diagnosis.json"
    
    if Path(diagnosis_file).exists():
        with open(diagnosis_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def identify_unsuitable_functions():
    """识别不适用函数"""
    print("IDENTIFYING UNSUITABLE FUNCTIONS FOR REFACTORING")
    print("=" * 70)
    
    diagnosis = load_diagnosis_results()
    
    if not diagnosis:
        print("ERROR: Diagnosis results not found")
        return None
    
    print(f"\nBased on diagnosis:")
    print(f"- Total functions: {diagnosis['diagnosis_results']['total_functions']}")
    print(f"- Suitable: {diagnosis['diagnosis_results']['suitable_functions']}")
    print(f"- Unsuitable: {diagnosis['diagnosis_results']['unsuitable_functions']}")
    print(f"- Consistency: {diagnosis['diagnosis_results']['consistency_score']*100:.1f}%")
    
    print(f"\n1. Listing {diagnosis['diagnosis_results']['unsuitable_functions']} unsuitable functions:")
    print("-" * 50)
    
    unsuitable_functions = []
    
    for func_analysis in diagnosis["diagnosis_results"]["function_analyses"]:
        if not func_analysis.get("maclaurin_suitable", True):
            unsuitable_functions.append(func_analysis)
    
    # 按文件分组
    functions_by_file = {}
    
    for func in unsuitable_functions:
        file_path = func["file"]
        if file_path not in functions_by_file:
            functions_by_file[file_path] = []
        functions_by_file[file_path].append(func)
    
    print(f"\nUnsuitable functions by file:")
    
    for file_path, functions in functions_by_file.items():
        print(f"\n{file_path}:")
        for func in functions:
            print(f"  • {func['function']}")
            if func.get("issues"):
                for issue in func["issues"][:2]:  # 只显示前2个问题
                    print(f"    - {issue}")
            if func.get("alternative_method"):
                print(f"    Alternative: {func['alternative_method']}")
    
    print(f"\n2. Refactoring strategy for each function type:")
    print("-" * 50)
    
    strategies = {
        "Conditional logic functions": {
            "problem": "if/else statements may create discontinuities",
            "solution": "Replace with smooth mathematical functions",
            "example": "abs(x) → sqrt(x² + ε) where ε is small",
            "priority": "high"
        },
        "Exception handling functions": {
            "problem": "try/except/raise create control flow discontinuities",
            "solution": "Use mathematical error handling or precondition checks",
            "example": "if x == 0: raise → if abs(x) < ε: use_limit",
            "priority": "high"
        },
        "Absolute value functions": {
            "problem": "abs(x) is not analytic at x=0",
            "solution": "Use smooth approximation",
            "example": "abs(x) → sqrt(x² + ε²)",
            "priority": "medium"
        },
        "Maximum/minimum functions": {
            "problem": "max/min create discontinuities",
            "solution": "Use smooth maximum/minimum",
            "example": "max(a,b) → (a+b+sqrt((a-b)²+ε²))/2",
            "priority": "medium"
        }
    }
    
    for strategy_name, strategy in strategies.items():
        print(f"\n{strategy_name} [{strategy['priority'].upper()}]:")
        print(f"  Problem: {strategy['problem']}")
        print(f"  Solution: {strategy['solution']}")
        print(f"  Example: {strategy['example']}")
    
    print(f"\n3. Implementation approach:")
    print("-" * 50)
    
    approach = """
PHASED REFACTORING APPROACH:

Phase 1A: Quick wins (30 minutes)
• Identify functions with simple conditional logic
• Replace with smooth mathematical equivalents
• Test each change immediately

Phase 1B: Complex refactoring (45 minutes)
• Handle exception-based functions
• Implement mathematical error handling
• Create utility functions for common patterns

Phase 1C: Verification (15 minutes)
• Test refactored functions individually
• Ensure mathematical correctness
• Document changes made

TOTAL: 1.5 hours for 12 functions (~7.5 minutes per function)
"""
    
    print(approach)
    
    print(f"\n4. Creating refactoring plan...")
    
    refactoring_plan = {
        "plan_time": "2026-03-31T14:00:00Z",
        "target": f"Refactor {len(unsuitable_functions)} unsuitable functions",
        "goal": "Make functions Maclaurin-suitable or use clear alternatives",
        "phases": [
            {
                "phase": "Phase 1A: Quick conditional logic fixes",
                "duration": "30 minutes",
                "target_functions": [f for f in unsuitable_functions if "Conditional logic" in str(f.get("issues", []))],
                "approach": "Replace if/else with smooth functions"
            },
            {
                "phase": "Phase 1B: Exception handling refactoring",
                "duration": "45 minutes",
                "target_functions": [f for f in unsuitable_functions if "Exception" in str(f.get("issues", []))],
                "approach": "Implement mathematical error handling"
            },
            {
                "phase": "Phase 1C: Verification and documentation",
                "duration": "15 minutes",
                "tasks": [
                    "Test each refactored function",
                    "Verify mathematical properties",
                    "Document changes and reasoning"
                ]
            }
        ],
        "success_criteria": [
            "All 12 functions are either Maclaurin-suitable or use clear alternatives",
            "Consistency improves from 65.7% to >85%",
            "Ready for Phase 2 optimization"
        ]
    }
    
    plan_file = "unsuitable_functions_refactoring_plan.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(refactoring_plan, f, indent=2, ensure_ascii=False)
    
    print(f"Refactoring plan saved: {plan_file}")
    
    print(f"\n5. Ready to begin Phase 1A: Quick conditional logic fixes")
    print(f"Starting with {len([f for f in unsuitable_functions if 'Conditional logic' in str(f.get('issues', []))])} functions")
    
    return unsuitable_functions, refactoring_plan

def main():
    """主函数"""
    print("UNSUITABLE FUNCTIONS IDENTIFICATION AND REFACTORING PLAN")
    print("=" * 70)
    
    print("\nGoal: Refactor 12 unsuitable functions to achieve consistency")
    print("Target: questionable → valid validity")
    
    unsuitable_functions, refactoring_plan = identify_unsuitable_functions()
    
    print(f"\n" + "=" * 70)
    print("READY TO BEGIN REFACTORING")
    print("=" * 70)
    
    print(f"\nSummary:")
    print(f"- Unsuitable functions identified: {len(unsuitable_functions)}")
    print(f"- Primary issues: Conditional logic, Exception handling")
    print(f"- Refactoring time: 1.5 hours")
    print(f"- Expected outcome: Consistency 65.7% → >85%")
    
    print(f"\nNext: Begin Phase 1A - Quick conditional logic fixes")
    print(f"Time: Now (14:00) to 14:30")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)