"""
验证v2.3优化效果
"""

import requests
import json
import time

def run_maclaurin_audit_v2_3():
    """运行v2.3的麦克劳林审核"""
    print("VERIFYING V2.3 OPTIMIZATION EFFECTIVENESS")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v2.3_consistency_optimized"
    
    print(f"\nTesting optimized version: {skill_path}")
    print(f"Version: 2.3.0 (consistency optimized)")
    print(f"Goal: questionable → valid validity")
    
    print(f"\n1. Checking mathematical audit service...")
    
    try:
        health = requests.get('http://localhost:8010/health', timeout=5)
        if health.status_code == 200:
            print(f"  Service healthy: {health.json().get('status', 'unknown')}")
        else:
            print(f"  Service not healthy: HTTP {health.status_code}")
            return None
    except Exception as e:
        print(f"  Service error: {e}")
        return None
    
    print(f"\n2. Running Maclaurin audit...")
    
    audit_data = {
        'skill_id': 'AISleepGen_v2_3_consistency',
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
            
            print(f"  Audit completed in {audit_time:.2f}s")
            
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
                
                print(f"\n3. Maclaurin audit results:")
                print(f"   Confidence: {confidence:.3f}")
                print(f"   Validity: {validity}")
                
                # 与之前比较
                previous_confidence = 0.750
                previous_validity = "questionable"
                
                print(f"\n4. Comparison with v2.2:")
                print(f"   Confidence: {previous_confidence:.3f} → {confidence:.3f} ({'↑' if confidence > previous_confidence else '↓' if confidence < previous_confidence else '='})")
                print(f"   Validity: {previous_validity} → {validity} ({'✓ IMPROVED' if validity == 'valid' and previous_validity == 'questionable' else '⨯ NO CHANGE'})")
                
                # 总体分数
                overall_score = result.get('overall_mathematical_score', 0)
                print(f"   Overall score: {overall_score:.2f}/100")
                
                return {
                    'version': '2.3.0',
                    'confidence': confidence,
                    'validity': validity,
                    'audit_time': audit_time,
                    'overall_score': overall_score,
                    'improvement': validity == 'valid' and previous_validity == 'questionable',
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

def analyze_remaining_issues():
    """分析剩余问题"""
    print(f"\n5. ANALYZING REMAINING ISSUES (if any)")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v2.3_consistency_optimized"
    
    print(f"\nChecking for remaining conditional logic in {skill_path}")
    
    remaining_patterns = [
        "if ",
        "else:",
        "try:",
        "except",
        "raise"
    ]
    
    import os
    from pathlib import Path
    
    remaining_issues = []
    
    for py_file in Path(skill_path).rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            file_issues = []
            
            for i, line in enumerate(lines, 1):
                line_lower = line.lower().strip()
                
                for pattern in remaining_patterns:
                    if pattern in line_lower and not line_lower.startswith('#'):
                        # 检查是否在注释中
                        if '#' in line:
                            code_part = line.split('#')[0].lower()
                            if pattern in code_part:
                                file_issues.append({
                                    "line": i,
                                    "code": line.strip()[:60]
                                })
                        else:
                            file_issues.append({
                                "line": i,
                                "code": line.strip()[:60]
                            })
            
            if file_issues:
                remaining_issues.append({
                    "file": str(py_file.relative_to(skill_path)),
                    "issues": file_issues[:3]  # 只显示前3个
                })
                
        except Exception as e:
            print(f"  Error reading {py_file.name}: {e}")
    
    if remaining_issues:
        print(f"\nFound {len(remaining_issues)} files with remaining conditional logic:")
        
        for file_info in remaining_issues:
            print(f"\n{file_info['file']}:")
            for issue in file_info["issues"]:
                print(f"  Line {issue['line']}: {issue['code']}...")
        
        print(f"\nRecommendation: Address these remaining issues for full consistency")
    else:
        print(f"\nGreat! No remaining conditional logic found.")
        print(f"All functions should now be mathematically consistent.")
    
    return remaining_issues

def main():
    """主验证函数"""
    print("V2.3 OPTIMIZATION VERIFICATION")
    print("=" * 70)
    
    print("\nTesting if our refactoring improved validity:")
    print("Primary goal: questionable → valid")
    print("Secondary goal: confidence improvement")
    
    audit_result = run_maclaurin_audit_v2_3()
    
    if audit_result:
        print(f"\n" + "=" * 70)
        
        if audit_result['improvement']:
            print("🎉 SUCCESS! VALIDITY IMPROVED!")
            print(f"questionable → valid ✓")
            print(f"\nOptimization strategy worked!")
            print(f"Consistency improvements changed validity marker")
        else:
            print("⚠️ PARTIAL SUCCESS OR NO CHANGE")
            print(f"Validity: {audit_result['validity']}")
            
            if audit_result['validity'] == 'questionable':
                print(f"\nValidity still questionable - need further optimization")
                print(f"Let's analyze remaining issues...")
                
                remaining_issues = analyze_remaining_issues()
                
                if remaining_issues:
                    print(f"\nNext steps:")
                    print(f"1. Address {len(remaining_issues)} files with remaining issues")
                    print(f"2. Focus on skill.py (likely main remaining issues)")
                    print(f"3. Run audit again after fixes")
                else:
                    print(f"\nUnexpected: No remaining issues but still questionable")
                    print(f"May need to check other mathematical properties")
            else:
                print(f"\nUnexpected validity: {audit_result['validity']}")
        
        print(f"\n" + "=" * 70)
        print("VERIFICATION COMPLETE")
        print("=" * 70)
        
        # 保存结果
        verification_result = {
            "verification_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "version": "2.3.0",
            "audit_result": audit_result,
            "goal_achieved": audit_result['improvement'],
            "recommendations": [
                "If validity improved: proceed to Phase 2",
                "If not: analyze remaining issues and continue Phase 1"
            ]
        }
        
        with open("v2_3_verification_result.json", 'w', encoding='utf-8') as f:
            json.dump(verification_result, f, indent=2, ensure_ascii=False)
        
        print(f"\nVerification results saved: v2_3_verification_result.json")
        
        return audit_result
        
    else:
        print(f"\nERROR: Could not run audit")
        return False

if __name__ == "__main__":
    print("V2.3 CONSISTENCY OPTIMIZATION VERIFICATION")
    print("=" * 70)
    
    result = main()
    
    if result:
        if result.get('improvement', False):
            print("\n🎯 READY FOR PHASE 2: OPTIMIZE BORDERLINE FUNCTIONS")
        else:
            print("\n🔧 NEED FURTHER OPTIMIZATION IN PHASE 1")
    else:
        print("\n❌ VERIFICATION FAILED")