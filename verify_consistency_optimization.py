"""
验证数学一致性优化效果
"""

import requests
import json
import time

def verify_optimization():
    """验证优化效果"""
    print("VERIFYING MATHEMATICAL CONSISTENCY OPTIMIZATION")
    print("=" * 70)
    
    skill_path = r"D:\openclaw\releases\AISleepGen\v2.3_consistent_math"
    
    print(f"\nTesting optimized version: {skill_path}")
    print(f"Goal: questionable → valid validity")
    
    # 检查服务
    try:
        health = requests.get('http://localhost:8010/health', timeout=5)
        if health.status_code != 200:
            print(f"Service not healthy: HTTP {health.status_code}")
            return False
    except Exception as e:
        print(f"Service error: {e}")
        return False
    
    # 运行麦克劳林审核
    audit_data = {
        'skill_id': 'aisleepgen_v2.3_consistent_math',
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
            
            certificates = result.get('mathematical_certificates', [])
            
            for cert in certificates:
                if "maclaurin" in cert.get("theorem", "").lower():
                    confidence = cert.get("confidence", 0)
                    validity = cert.get("validity", "unknown")
                    
                    print(f"\nResult: confidence={confidence:.3f}, validity={validity}")
                    print(f"Audit time: {audit_time:.2f}s")
                    
                    print(f"\nComparison with v2.2:")
                    print(f"  v2.2: 0.750 confidence, questionable validity")
                    print(f"  v2.3: {confidence:.3f} confidence, {validity} validity")
                    
                    if validity == "valid":
                        print(f"\n✅ SUCCESS! Validity changed from questionable to valid")
                        print(f"Mathematical consistency optimization worked")
                        return True, confidence, validity
                    else:
                        print(f"\n⚠️ PARTIAL SUCCESS")
                        print(f"Validity still {validity} (not valid)")
                        print(f"May need further optimization")
                        return False, confidence, validity
        
        else:
            print(f"Audit failed: HTTP {response.status_code}")
            return False, 0, "error"
            
    except Exception as e:
        print(f"Error: {e}")
        return False, 0, "error"

def analyze_if_not_valid(confidence, validity):
    """分析如果有效性未改善"""
    print(f"\nANALYSIS: Why validity is still {validity}")
    print("-" * 50)
    
    analysis = {
        "possible_reasons": [
            "Some functions still have conditional logic",
            "Exception handling not fully refactored",
            "Mixed mathematical properties persist",
            "Algorithm detects deeper inconsistencies",
            "Need more aggressive refactoring"
        ],
        "next_steps": [
            "Analyze remaining unsuitable functions in detail",
            "Check for hidden conditional logic patterns",
            "Ensure all functions use smooth mathematical utilities",
            "Consider complete mathematical rewrite of problematic functions",
            "Test individual function suitability"
        ],
        "recommendations": [
            "HIGH: Run detailed function-by-function analysis",
            "MEDIUM: Create test for each function's Maclaurin suitability",
            "LOW: Consider mathematical redesign of core algorithms"
        ]
    }
    
    for reason in analysis["possible_reasons"]:
        print(f"• {reason}")
    
    print(f"\nRecommended next steps:")
    for step in analysis["next_steps"]:
        print(f"  - {step}")
    
    return analysis

def main():
    """主验证函数"""
    print("MATHEMATICAL CONSISTENCY VERIFICATION")
    print("=" * 70)
    
    print("\nBased on Phase 1 optimization:")
    print("- Added smooth mathematical utility functions")
    print("- Refactored 7 files with conditional logic")
    print("- Goal: Change validity from questionable to valid")
    
    success, confidence, validity = verify_optimization()
    
    print(f"\n" + "=" * 70)
    
    if success:
        print("✅ OPTIMIZATION SUCCESSFUL - VALIDITY IMPROVED")
        print(f"  Validity: questionable → {validity}")
        print(f"  Confidence: {confidence:.3f}")
        
        # 保存成功结果
        result = {
            "verification_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "version": "v2.3_consistent_math",
            "success": True,
            "confidence": confidence,
            "validity": validity,
            "improvement": "questionable → valid",
            "interpretation": "Mathematical consistency optimization worked"
        }
        
    else:
        print("⚠️ OPTIMIZATION NEEDS FURTHER WORK")
        print(f"  Validity still: {validity}")
        print(f"  Confidence: {confidence:.3f}")
        
        analysis = analyze_if_not_valid(confidence, validity)
        
        # 保存需要进一步工作的结果
        result = {
            "verification_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "version": "v2.3_consistent_math",
            "success": False,
            "confidence": confidence,
            "validity": validity,
            "improvement_needed": True,
            "analysis": analysis
        }
    
    # 保存结果
    result_file = "consistency_optimization_verification.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nVerification results saved: {result_file}")
    
    print(f"\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)