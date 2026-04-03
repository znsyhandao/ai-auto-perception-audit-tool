"""
运行麦克劳林验证测试
"""

import requests
import json
import time
from pathlib import Path

def run_maclaurin_audit(skill_name, skill_path):
    """运行麦克劳林审核"""
    print(f"\nAuditing {skill_name}...")
    print(f"Path: {skill_path}")
    
    # 检查服务
    try:
        health = requests.get('http://localhost:8010/health', timeout=5)
        if health.status_code != 200:
            print(f"  Service not healthy: HTTP {health.status_code}")
            return None
    except Exception as e:
        print(f"  Service error: {e}")
        return None
    
    # 运行麦克劳林审核
    audit_data = {
        'skill_id': f'test_maclaurin_{skill_name}',
        'skill_path': skill_path,
        'audit_types': ['maclaurin'],
        'mathematical_depth': 3
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8010/audit',
            json=audit_data,
            timeout=30
        )
        audit_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # 提取麦克劳林结果
            certificates = result.get('mathematical_certificates', [])
            
            maclaurin_cert = None
            for cert in certificates:
                if "maclaurin" in cert.get("theorem", "").lower():
                    maclaurin_cert = cert
                    break
            
            if maclaurin_cert:
                confidence = maclaurin_cert.get("confidence", 0)
                validity = maclaurin_cert.get("validity", "unknown")
                
                print(f"  Result: confidence={confidence:.3f}, validity={validity}")
                print(f"  Audit time: {audit_time:.2f}s")
                
                return {
                    'skill': skill_name,
                    'confidence': confidence,
                    'validity': validity,
                    'audit_time': audit_time,
                    'certificate': maclaurin_cert
                }
            else:
                print(f"  ERROR: Maclaurin certificate not found")
                return None
        else:
            print(f"  ERROR: Audit failed with HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def load_verification_plan():
    """加载验证计划"""
    plan_file = Path("D:/openclaw/test_maclaurin_verification/verification_plan.json")
    
    if plan_file.exists():
        with open(plan_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def main():
    """主验证函数"""
    print("RUNNING MACLAURIN DETECTION VERIFICATION")
    print("=" * 70)
    
    print("\nTesting hypothesis:")
    print("Maclaurin measures MATHEMATICAL SUITABILITY for series expansion")
    print("Not code quality or structure")
    
    # 加载验证计划
    plan = load_verification_plan()
    
    if not plan:
        print("ERROR: Verification plan not found")
        return False
    
    test_cases = plan.get("test_cases", [])
    expected_outcomes = plan.get("expected_outcomes", {})
    
    print(f"\n1. Running audits on {len(test_cases)} test skills...")
    print("-" * 50)
    
    audit_results = []
    
    for test_case in test_cases:
        skill_name = test_case["name"]
        skill_path = test_case["path"]
        expected_conf = test_case["expected_confidence"]
        expected_valid = test_case["expected_validity"]
        
        print(f"\n{skill_name}:")
        print(f"  Expected: {expected_conf}, {expected_valid}")
        
        result = run_maclaurin_audit(skill_name, skill_path)
        
        if result:
            audit_results.append({
                "skill": skill_name,
                "expected_confidence": expected_conf,
                "expected_validity": expected_valid,
                "actual_confidence": result["confidence"],
                "actual_validity": result["validity"],
                "audit_time": result["audit_time"]
            })
    
    print(f"\n2. Verification results:")
    print("-" * 50)
    
    if audit_results:
        print("\nSkill | Expected Confidence | Actual Confidence | Expected Validity | Actual Validity")
        print("-" * 90)
        
        for result in audit_results:
            skill = result["skill"]
            exp_conf = result["expected_confidence"]
            act_conf = result["actual_confidence"]
            exp_valid = result["expected_validity"]
            act_valid = result["actual_validity"]
            
            print(f"{skill:25} | {exp_conf:19} | {act_conf:17.3f} | {exp_valid:16} | {act_valid:14}")
        
        print(f"\n3. Hypothesis validation:")
        print("-" * 50)
        
        # 分析结果
        validation_analysis = {
            "fully_analytic_test": False,
            "not_analytic_test": False,
            "special_functions_test": False,
            "numerical_stability_test": False,
            "overall_hypothesis_supported": False
        }
        
        for result in audit_results:
            skill = result["skill"]
            act_conf = result["actual_confidence"]
            act_valid = result["actual_validity"]
            
            if skill == "fully_analytic":
                # 应得高分
                if act_conf >= 0.800 and act_valid == "valid":
                    validation_analysis["fully_analytic_test"] = True
                    print(f"fully_analytic: PASS - High confidence ({act_conf:.3f}), valid")
                else:
                    print(f"fully_analytic: FAIL - Got {act_conf:.3f}, {act_valid}")
            
            elif skill == "not_analytic_at_zero":
                # 应得低分
                if act_conf <= 0.600 and act_valid != "valid":
                    validation_analysis["not_analytic_test"] = True
                    print(f"not_analytic_at_zero: PASS - Low confidence ({act_conf:.3f}), {act_valid}")
                else:
                    print(f"not_analytic_at_zero: FAIL - Got {act_conf:.3f}, {act_valid}")
            
            elif skill == "special_functions":
                # 应得中分
                if 0.600 <= act_conf <= 0.800 and act_valid == "valid":
                    validation_analysis["special_functions_test"] = True
                    print(f"special_functions: PASS - Medium confidence ({act_conf:.3f}), valid")
                else:
                    print(f"special_functions: FAIL - Got {act_conf:.3f}, {act_valid}")
            
            elif skill == "numerically_unstable":
                # 应得中低分
                if act_conf <= 0.700 and act_valid != "valid":
                    validation_analysis["numerical_stability_test"] = True
                    print(f"numerically_unstable: PASS - Low-medium confidence ({act_conf:.3f}), {act_valid}")
                else:
                    print(f"numerically_unstable: FAIL - Got {act_conf:.3f}, {act_valid}")
        
        # 总体验证
        passed_tests = sum(1 for test in [
            validation_analysis["fully_analytic_test"],
            validation_analysis["not_analytic_test"],
            validation_analysis["special_functions_test"],
            validation_analysis["numerical_stability_test"]
        ] if test)
        
        if passed_tests >= 3:
            validation_analysis["overall_hypothesis_supported"] = True
            print(f"\nHYPOTHESIS STRONGLY SUPPORTED: {passed_tests}/4 tests passed")
            print("Maclaurin DOES measure mathematical suitability for series expansion")
        elif passed_tests >= 2:
            print(f"\nHYPOTHESIS PARTIALLY SUPPORTED: {passed_tests}/4 tests passed")
            print("Maclaurin may measure some mathematical properties")
        else:
            print(f"\nHYPOTHESIS NOT SUPPORTED: Only {passed_tests}/4 tests passed")
            print("Maclaurin may NOT measure mathematical suitability as hypothesized")
        
        print(f"\n4. Implications for AISleepGen optimization:")
        print("-" * 50)
        
        if validation_analysis["overall_hypothesis_supported"]:
            print("CONFIRMED: Maclaurin measures mathematical suitability")
            print("Correct optimization approach:")
            print("  1. Make functions analytic at x=0")
            print("  2. Ensure good convergence properties")
            print("  3. Improve numerical stability")
            print("  4. Find recurrence relations")
            print("  5. Determine optimal truncation")
        else:
            print("UNCONFIRMED: Need more analysis")
            print("Consider:")
            print("  • Analyzing algorithm source code")
            print("  • Creating more test cases")
            print("  • Testing other hypotheses")
        
        # 保存验证结果
        verification_results = {
            "verification_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "test_cases": audit_results,
            "validation_analysis": validation_analysis,
            "hypothesis_supported": validation_analysis["overall_hypothesis_supported"],
            "passed_tests": passed_tests,
            "total_tests": 4,
            "implications": "See analysis above"
        }
        
        results_file = "maclaurin_verification_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(verification_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nVerification results saved: {results_file}")
        
        return verification_results
        
    else:
        print("ERROR: No audit results obtained")
        return False

if __name__ == "__main__":
    print("MACLAURIN TRUE DETECTION PROCESS VERIFICATION")
    print("=" * 70)
    
    results = main()
    
    print(f"\n" + "=" * 70)
    if results:
        if results.get("hypothesis_supported", False):
            print("VERIFICATION COMPLETE - HYPOTHESIS CONFIRMED")
        else:
            print("VERIFICATION COMPLETE - NEEDS FURTHER ANALYSIS")
    else:
        print("VERIFICATION FAILED")
    print("=" * 70)