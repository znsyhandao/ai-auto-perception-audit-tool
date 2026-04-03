"""
验证麦克劳林优化效果
"""

import requests
import json
import time
from pathlib import Path

def verify_maclaurin_improvement():
    """验证麦克劳林改进"""
    print("VERIFYING MACLAURIN OPTIMIZATION EFFECTIVENESS")
    print("=" * 70)
    
    optimized_dir = Path("D:/openclaw/releases/AISleepGen/v2.2_maclaurin_optimized")
    
    print(f"\n1. Testing optimized version:")
    print(f"   Directory: {optimized_dir}")
    print(f"   Version: v2.2.0 (Maclaurin optimized)")
    
    # 检查服务
    print(f"\n2. Checking mathematical audit service...")
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
    
    # 运行麦克劳林审核
    audit_data = {
        'skill_id': 'aisleepgen_v2.2_maclaurin_optimized',
        'skill_path': str(optimized_dir),
        'audit_types': ['maclaurin'],  # 只运行麦克劳林
        'mathematical_depth': 3
    }
    
    print(f"\n3. Running Maclaurin audit on optimized version...")
    
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
            
            print(f"\n4. AUDIT COMPLETED in {audit_time:.2f}s")
            print("-" * 50)
            
            # 提取麦克劳林结果
            certificates = result.get('mathematical_certificates', [])
            
            maclaurin_cert = None
            for cert in certificates:
                if "maclaurin" in cert.get("theorem", "").lower():
                    maclaurin_cert = cert
                    break
            
            if maclaurin_cert:
                maclaurin_conf = maclaurin_cert.get("confidence", 0)
                maclaurin_valid = maclaurin_cert.get("validity", "unknown")
                
                print(f"Maclaurin Series Result:")
                print(f"  Confidence: {maclaurin_conf:.3f}")
                print(f"  Validity: {maclaurin_valid}")
                
                # 与之前比较
                previous_conf = 0.750
                improvement = maclaurin_conf - previous_conf
                
                print(f"\nComparison with v2.1 (before optimization):")
                print(f"  v2.1 confidence: {previous_conf:.3f}")
                print(f"  v2.2 confidence: {maclaurin_conf:.3f}")
                print(f"  Improvement: {improvement:+.3f}")
                
                # 目标检查
                target_conf = 0.850
                if maclaurin_conf >= target_conf:
                    print(f"\nTARGET ACHIEVED: {maclaurin_conf:.3f} >= {target_conf}")
                    print("  Maclaurin optimization successful!")
                    target_status = "achieved"
                else:
                    print(f"\nTARGET NOT REACHED: {maclaurin_conf:.3f} < {target_conf}")
                    print(f"  Gap: {target_conf - maclaurin_conf:.3f}")
                    target_status = "not_achieved"
                
                # 运行完整审核比较总体分数
                print(f"\n5. Running complete audit for overall comparison...")
                overall_result = run_complete_audit(optimized_dir)
                
                if overall_result:
                    overall_score = overall_result.get('overall_mathematical_score', 0)
                    previous_score = 79.95
                    overall_improvement = overall_score - previous_score
                    
                    print(f"\nOverall mathematical score comparison:")
                    print(f"  v2.1 score: {previous_score:.2f}")
                    print(f"  v2.2 score: {overall_score:.2f}")
                    print(f"  Improvement: {overall_improvement:+.2f}")
                
                # 保存验证结果
                verification = {
                    "verification_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "optimized_version": "v2.2_maclaurin_optimized",
                    "maclaurin_results": {
                        "confidence": maclaurin_conf,
                        "validity": maclaurin_valid,
                        "audit_time": audit_time
                    },
                    "comparison": {
                        "previous_confidence": previous_conf,
                        "current_confidence": maclaurin_conf,
                        "improvement": improvement,
                        "improvement_percentage": (improvement / previous_conf * 100) if previous_conf > 0 else 0
                    },
                    "target_analysis": {
                        "target_confidence": target_conf,
                        "achieved": maclaurin_conf >= target_conf,
                        "confidence_gap": target_conf - maclaurin_conf if maclaurin_conf < target_conf else 0,
                        "target_status": target_status
                    },
                    "overall_results": overall_result if 'overall_result' in locals() else None
                }
                
                # 添加优化效果分析
                if improvement > 0:
                    verification["optimization_effectiveness"] = {
                        "effective": True,
                        "improvement_magnitude": "significant" if improvement >= 0.05 else "moderate" if improvement >= 0.02 else "minor",
                        "conclusion": "Optimization had positive effect"
                    }
                elif improvement == 0:
                    verification["optimization_effectiveness"] = {
                        "effective": False,
                        "improvement_magnitude": "none",
                        "conclusion": "Optimization had no measurable effect"
                    }
                else:
                    verification["optimization_effectiveness"] = {
                        "effective": False,
                        "improvement_magnitude": "negative",
                        "conclusion": "Optimization had negative effect (confidence decreased)"
                    }
                
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                result_file = f"maclaurin_optimization_verification_{timestamp}.json"
                
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(verification, f, indent=2, ensure_ascii=False)
                
                print(f"\nVerification saved: {result_file}")
                
                # 创建总结报告
                create_summary_report(verification, optimized_dir)
                
                return verification
            else:
                print("   ERROR: Maclaurin certificate not found in results")
                return None
        else:
            print(f"   ERROR: Audit failed with HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ERROR running audit: {e}")
        return None

def run_complete_audit(skill_path):
    """运行完整审核"""
    audit_data = {
        'skill_id': 'aisleepgen_v2.2_complete',
        'skill_path': str(skill_path),
        'audit_types': ['maclaurin', 'taylor', 'fourier', 'matrix', 'proof'],
        'mathematical_depth': 3
    }
    
    try:
        response = requests.post(
            'http://localhost:8010/audit',
            json=audit_data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   Complete audit failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ERROR in complete audit: {e}")
        return None

def create_summary_report(verification, optimized_dir):
    """创建总结报告"""
    print(f"\n6. CREATING OPTIMIZATION SUMMARY REPORT")
    print("-" * 50)
    
    maclaurin_conf = verification["maclaurin_results"]["confidence"]
    previous_conf = verification["comparison"]["previous_confidence"]
    improvement = verification["comparison"]["improvement"]
    target_achieved = verification["target_analysis"]["achieved"]
    
    summary = f"""# Maclaurin Optimization Verification Report

## Verification Summary

**Verification Date**: {verification["verification_time"]}  
**Optimized Version**: {verification["optimized_version"]}  
**Verification Status**: {'SUCCESS' if target_achieved else 'PARTIAL SUCCESS' if improvement > 0 else 'NO IMPROVEMENT'}

## Results

### Maclaurin Confidence
- **Before optimization (v2.1)**: {previous_conf:.3f}
- **After optimization (v2.2)**: {maclaurin_conf:.3f}
- **Improvement**: {improvement:+.3f} ({verification["comparison"]["improvement_percentage"]:.1f}%)

### Target Achievement
- **Target confidence**: 0.850
- **Achieved**: {'✅ YES' if target_achieved else '❌ NO'}
- **Confidence gap**: {verification["target_analysis"]["confidence_gap"]:.3f}

### Optimization Effectiveness
- **Effective**: {'✅ YES' if verification["optimization_effectiveness"]["effective"] else '❌ NO'}
- **Improvement magnitude**: {verification["optimization_effectiveness"]["improvement_magnitude"]}
- **Conclusion**: {verification["optimization_effectiveness"]["conclusion"]}

## Analysis

### What Worked
Based on the "Understanding over passing" principle:
1. **Deep analysis** identified key Maclaurin dimensions
2. **Targeted optimizations** addressed specific mathematical properties
3. **Scientific verification** measured actual improvement

### What We Learned
1. **Algorithm response**: Maclaurin algorithm {'responded positively' if improvement > 0 else 'did not respond' if improvement == 0 else 'responded negatively'} to optimizations
2. **Optimization strategy**: {'Effective' if improvement > 0 else 'Ineffective'} for this algorithm
3. **Method validation**: The "understanding first" approach {'was validated' if improvement > 0 else 'needs refinement'}

## Next Steps

### If Target Achieved (≥0.850):
1. ✅ Celebrate success - principle validated
2. ✅ Prepare v2.2 release with optimization documentation
3. ✅ Apply same approach to other audit types
4. ✅ Share learning with team

### If Target Not Achieved but Improvement > 0:
1. 🔄 Analyze why target not reached
2. 🔄 Refine optimization strategies
3. 🔄 Consider additional optimization dimensions
4. 🔄 Run another iteration if time permits

### If No Improvement or Negative:
1. 🔍 Deep analysis of algorithm behavior
2. 🔍 Re-evaluate optimization assumptions
3. 🔍 Consider algorithm limitations
4. 🔍 Focus on other audit types instead

## Technical Details

### Optimization Dimensions Targeted:
1. Function smoothness (mathematical continuity)
2. Numerical stability (computation conditioning)
3. Algorithm convergence (iterative behavior)
4. Mathematical correctness (foundation strength)

### Files Modified:
- See `optimization_results.json` in {optimized_dir}

### Audit Details:
- Audit time: {verification["maclaurin_results"]["audit_time"]:.2f}s
- Validity: {verification["maclaurin_results"]["validity"]}

## Conclusion

The "Understanding over passing" principle {'was successfully applied' if improvement > 0 else 'needs refinement'}.

**Key takeaway**: {'Deep understanding led to effective optimization' if improvement > 0 else 'Even with understanding, algorithm response may be limited'}.

---
*Verification completed: {verification["verification_time"]}*
*Principle applied: Understanding over passing*
"""
    
    report_file = optimized_dir / "MACLAURIN_OPTIMIZATION_VERIFICATION.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary report created: {report_file}")
    
    return report_file

def main():
    """主函数"""
    print("MACLAURIN OPTIMIZATION VERIFICATION")
    print("=" * 70)
    
    print("\nVerifying 'Understanding over passing' principle:")
    print("1. Optimized based on deep algorithm understanding")
    print("2. Now verifying if optimization was effective")
    print("3. Measuring actual improvement vs target")
    
    verification = verify_maclaurin_improvement()
    
    print(f"\n" + "=" * 70)
    
    if verification:
        maclaurin_conf = verification["maclaurin_results"]["confidence"]
        previous_conf = verification["comparison"]["previous_confidence"]
        improvement = verification["comparison"]["improvement"]
        target_achieved = verification["target_analysis"]["achieved"]
        
        print("VERIFICATION COMPLETE - RESULTS:")
        print("=" * 70)
        
        print(f"\nMaclaurin confidence:")
        print(f"  Before: {previous_conf:.3f}")
        print(f"  After:  {maclaurin_conf:.3f}")
        print(f"  Change: {improvement:+.3f}")
        
        print(f"\nTarget (0.850): {'✅ ACHIEVED' if target_achieved else '❌ NOT ACHIEVED'}")
        
        if improvement > 0:
            print(f"\n✅ OPTIMIZATION EFFECTIVE: Confidence improved by {improvement:+.3f}")
            print(f"   'Understanding over passing' principle validated")
        elif improvement == 0:
            print(f"\n⚠️ NO IMPROVEMENT: Confidence unchanged")
            print(f"   Optimization had no measurable effect")
        else:
            print(f"\n❌ NEGATIVE EFFECT: Confidence decreased by {-improvement:.3f}")
            print(f"   Optimization had negative impact")
        
        print(f"\nNext steps based on results...")
        
    else:
        print("VERIFICATION FAILED - CHECK ERRORS")
        print("=" * 70)
    
    return verification is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)