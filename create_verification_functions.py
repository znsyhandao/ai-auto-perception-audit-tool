"""
创建验证麦克劳林检测的测试函数
"""

import os
from pathlib import Path
import json

def create_verification_skills():
    """创建验证技能"""
    print("CREATING VERIFICATION FUNCTIONS FOR MACLAURIN DETECTION")
    print("=" * 70)
    
    test_dir = Path("D:/openclaw/test_maclaurin_verification")
    
    # 清理旧目录
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True)
    
    print(f"Test directory: {test_dir}")
    
    # 创建测试技能
    test_skills = [
        {
            "name": "fully_analytic",
            "description": "完全解析函数 - 应得高分",
            "functions": [
                "def exponential(x): return 1 + x + x**2/2 + x**3/6",
                "def sine_function(x): return x - x**3/6 + x**5/120",
                "def cosine_function(x): return 1 - x**2/2 + x**4/24",
                "def polynomial(x): return 1 + 2*x + 3*x**2 + 4*x**3"
            ],
            "expected_confidence": "high (0.850+)",
            "expected_validity": "valid"
        },
        {
            "name": "not_analytic_at_zero", 
            "description": "在0点不解析的函数 - 应得低分",
            "functions": [
                "def absolute_value(x): return abs(x)",
                "def piecewise_function(x): return x if x >= 0 else -x",
                "def conditional_exp(x): return math.exp(x) if x > 0 else 1",
                "def max_function(x): return max(x, 0)"
            ],
            "expected_confidence": "low (0.500-)", 
            "expected_validity": "questionable"
        },
        {
            "name": "special_functions",
            "description": "特殊函数（对数、平方根） - 中等分数",
            "functions": [
                "def logarithm_approx(x): return x - x**2/2 + x**3/3",
                "def square_root_approx(x): return 1 + x/2 - x**2/8",
                "def tangent_approx(x): return x + x**3/3 + 2*x**5/15",
                "def rational_function(x): return (1 + x/2) / (1 - x/2)"
            ],
            "expected_confidence": "medium (0.600-0.800)",
            "expected_validity": "valid"
        },
        {
            "name": "numerically_unstable",
            "description": "数值不稳定函数 - 应检测稳定性问题",
            "functions": [
                "def unstable_subtraction(x): return (1 - math.cos(x)) / x**2",
                "def catastrophic_cancellation(x): return math.exp(x) - 1 - x",
                "def ill_conditioned(x): return (x**3 - 3*x**2 + 3*x - 1) / (x - 1)**3",
                "def alternating_series(x): return x - x**3/6 + x**5/120 - x**7/5040"
            ],
            "expected_confidence": "medium-low (0.500-0.700)",
            "expected_validity": "questionable"
        }
    ]
    
    print("\n1. Creating test skills with known mathematical properties:")
    print("-" * 50)
    
    created_skills = []
    
    for skill in test_skills:
        skill_dir = test_dir / skill["name"]
        skill_dir.mkdir()
        
        # 创建skill.py
        skill_content = f'''"""
{skill["description"]}
Expected: {skill["expected_confidence"]} confidence, {skill["expected_validity"]} validity
"""

import math

{chr(10).join(skill["functions"])}

def main():
    """Test main function"""
    test_value = 0.5
    results = {{
        "exponential": exponential(test_value),
        "sine": sine_function(test_value),
        "cosine": cosine_function(test_value),
        "polynomial": polynomial(test_value)
    }}
    return results

if __name__ == "__main__":
    print(main())
'''
        
        skill_file = skill_dir / "skill.py"
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(skill_content)
        
        # 创建config.yaml
        config_content = f'''skill_id: test_maclaurin_{skill["name"]}
version: 1.0.0
description: {skill["description"]}
expected_confidence: {skill["expected_confidence"]}
expected_validity: {skill["expected_validity"]}
'''
        
        config_file = skill_dir / "config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        created_skills.append({
            "name": skill["name"],
            "path": str(skill_dir),
            "description": skill["description"],
            "expected_confidence": skill["expected_confidence"],
            "expected_validity": skill["expected_validity"],
            "function_count": len(skill["functions"])
        })
        
        print(f"\n{skill['name']}:")
        print(f"  Description: {skill['description']}")
        print(f"  Expected: {skill['expected_confidence']}, {skill['expected_validity']}")
        print(f"  Functions: {len(skill['functions'])}")
        print(f"  Path: {skill_dir}")
    
    print(f"\n2. Created {len(created_skills)} test skills")
    
    # 创建验证计划
    verification_plan = {
        "verification_time": "2026-03-31T13:25:00Z",
        "purpose": "Verify true Maclaurin detection process",
        "hypothesis": "Maclaurin measures mathematical suitability for series expansion, not code quality",
        "test_cases": created_skills,
        "verification_steps": [
            "Run Maclaurin audit on each test skill",
            "Compare actual results with expected",
            "Validate detection of: analyticity, convergence, stability",
            "Confirm algorithm follows true mathematical process"
        ],
        "expected_outcomes": {
            "fully_analytic": "High confidence (0.850+), valid",
            "not_analytic_at_zero": "Low confidence (0.500-), questionable",
            "special_functions": "Medium confidence (0.600-0.800), valid",
            "numerically_unstable": "Medium-low confidence (0.500-0.700), questionable"
        }
    }
    
    plan_file = test_dir / "verification_plan.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(verification_plan, f, indent=2, ensure_ascii=False)
    
    print(f"\nVerification plan saved: {plan_file}")
    
    print(f"\n3. Next steps:")
    print("   a. Run Maclaurin audit on each test skill")
    print("   b. Compare actual vs expected results")
    print("   c. Validate true detection process")
    print("   d. Based on results, plan real optimization")
    
    return test_dir, created_skills, verification_plan

def main():
    """主函数"""
    print("MACLAURIN DETECTION VERIFICATION SETUP")
    print("=" * 70)
    
    print("\nScientific verification approach:")
    print("1. Create test cases with KNOWN mathematical properties")
    print("2. Run Maclaurin audit to see algorithm response")
    print("3. Compare actual results with expected")
    print("4. Validate true understanding of detection process")
    
    test_dir, created_skills, verification_plan = create_verification_skills()
    
    print(f"\n" + "=" * 70)
    print("VERIFICATION TEST CASES CREATED")
    print("=" * 70)
    
    print(f"\nTest directory: {test_dir}")
    print(f"Total test skills: {len(created_skills)}")
    
    print(f"\nVerification will test:")
    print("• Does Maclaurin detect analyticity at x=0?")
    print("• Does it measure convergence radius?")
    print("• Does it assess numerical stability?")
    print("• Does it follow true mathematical process?")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)