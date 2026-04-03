"""
运行v2.1最终数学审核
"""

import requests
import json
import time
from pathlib import Path

def run_v2_1_audit():
    """运行v2.1审核"""
    print("RUNNING FINAL MATHEMATICAL AUDIT ON v2.1 (CONSOLIDATED)")
    print("=" * 70)
    
    skill_path = "D:/openclaw/releases/AISleepGen/v2.0_release"
    
    # 检查服务
    print("1. Checking mathematical audit service...")
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
    
    # 运行审核
    audit_data = {
        'skill_id': 'aisleepgen_v2.1_consolidated',
        'skill_path': skill_path,
        'audit_types': ['matrix'],  # 只运行矩阵审核，快速验证
        'mathematical_depth': 3
    }
    
    print(f"\n2. Running matrix decomposition audit...")
    print(f"   Target: {skill_path}")
    
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
            
            print(f"\n3. AUDIT COMPLETED in {audit_time:.2f}s")
            print("-" * 50)
            
            # 提取矩阵结果
            certificates = result.get('mathematical_certificates', [])
            
            matrix_cert = None
            for cert in certificates:
                if "matrix" in cert.get("theorem", "").lower():
                    matrix_cert = cert
                    break
            
            if matrix_cert:
                matrix_conf = matrix_cert.get("confidence", 0)
                matrix_valid = matrix_cert.get("validity", "unknown")
                
                print(f"Matrix Decomposition Result:")
                print(f"  Confidence: {matrix_conf:.3f}")
                print(f"  Validity: {matrix_valid}")
                
                # 与v2.0比较
                v2_conf = 0.700
                improvement = matrix_conf - v2_conf
                
                print(f"\nComparison with v2.0:")
                print(f"  v2.0 confidence: {v2_conf:.3f}")
                print(f"  v2.1 confidence: {matrix_conf:.3f}")
                print(f"  Improvement: {improvement:+.3f}")
                
                # 与v1.0.9比较
                v1_conf = 0.700
                total_improvement = matrix_conf - v1_conf
                
                print(f"\nTotal improvement from v1.0.9:")
                print(f"  v1.0.9: {v1_conf:.3f}")
                print(f"  v2.1: {matrix_conf:.3f}")
                print(f"  Total improvement: {total_improvement:+.3f}")
                
                # 目标检查
                target = 0.850
                if matrix_conf >= target:
                    print(f"\nTARGET ACHIEVED: {matrix_conf:.3f} >= {target}")
                    print("  Module consolidation successfully improved matrix confidence!")
                else:
                    print(f"\nTARGET NOT REACHED: {matrix_conf:.3f} < {target}")
                    print(f"  Gap: {target - matrix_conf:.3f}")
                
                # 保存结果
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                result_file = f"v2_1_audit_result_{timestamp}.json"
                
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"\nResult saved: {result_file}")
                
                # 创建总结
                create_summary(matrix_conf, improvement, total_improvement)
                
                return matrix_conf
            else:
                print("   ERROR: Matrix certificate not found in results")
                return None
        else:
            print(f"   ERROR: Audit failed with HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ERROR running audit: {e}")
        return None

def create_summary(matrix_confidence, v2_improvement, total_improvement):
    """创建审核总结"""
    print(f"\n4. FINAL SUMMARY")
    print("=" * 70)
    
    summary = {
        "audit_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        "skill_version": "v2.1_consolidated",
        "matrix_confidence": matrix_confidence,
        "comparisons": {
            "v1.0.9": 0.700,
            "v2.0": 0.700,
            "v2.1": matrix_confidence
        },
        "improvements": {
            "v2.0_to_v2.1": v2_improvement,
            "v1.0.9_to_v2.1": total_improvement
        },
        "target_analysis": {
            "target_confidence": 0.850,
            "current_confidence": matrix_confidence,
            "confidence_gap": 0.850 - matrix_confidence if matrix_confidence < 0.850 else 0,
            "target_achieved": matrix_confidence >= 0.850
        },
        "module_consolidation_effect": {
            "modules_before": 30,
            "modules_after": 22,
            "module_reduction": 8,
            "predicted_confidence": 0.786,  # 从验证结果
            "actual_confidence": matrix_confidence,
            "prediction_accuracy": "close" if abs(0.786 - matrix_confidence) < 0.05 else "different"
        }
    }
    
    # 显示总结
    print(f"\nv2.1 Module Consolidation Results")
    print(f"Audit time: {summary['audit_time']}")
    
    print(f"\nConfidence progression:")
    print(f"  v1.0.9: {summary['comparisons']['v1.0.9']:.3f}")
    print(f"  v2.0: {summary['comparisons']['v2.0']:.3f} (no change)")
    print(f"  v2.1: {summary['comparisons']['v2.1']:.3f}")
    
    print(f"\nImprovements:")
    print(f"  v2.0 → v2.1: {summary['improvements']['v2.0_to_v2.1']:+.3f}")
    print(f"  v1.0.9 → v2.1: {summary['improvements']['v1.0.9_to_v2.1']:+.3f}")
    
    print(f"\nModule consolidation effect:")
    print(f"  Modules: {summary['module_consolidation_effect']['modules_before']} → {summary['module_consolidation_effect']['modules_after']}")
    print(f"  Reduction: {summary['module_consolidation_effect']['module_reduction']} modules")
    print(f"  Predicted confidence: {summary['module_consolidation_effect']['predicted_confidence']:.3f}")
    print(f"  Actual confidence: {summary['module_consolidation_effect']['actual_confidence']:.3f}")
    
    print(f"\nTarget analysis:")
    print(f"  Target: {summary['target_analysis']['target_confidence']:.3f}")
    print(f"  Current: {summary['target_analysis']['current_confidence']:.3f}")
    
    if summary['target_analysis']['target_achieved']:
        print(f"  STATUS: TARGET ACHIEVED!")
        print(f"  Module consolidation successfully improved matrix confidence")
    else:
        print(f"  STATUS: Target not reached")
        print(f"  Gap: {summary['target_analysis']['confidence_gap']:.3f}")
    
    # 保存总结
    summary_file = "v2_1_audit_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nSummary saved: {summary_file}")
    
    # 建议
    print(f"\n5. RECOMMENDATION")
    print("-" * 50)
    
    if summary['target_analysis']['target_achieved']:
        print("RECOMMENDATION: RELEASE v2.1")
        print("  - Matrix confidence target achieved")
        print("  - Module consolidation successful")
        print("  - Optimization validated")
    else:
        print("RECOMMENDATION: CONTINUE OPTIMIZATION OR RELEASE WITH NOTES")
        print("  Options:")
        print("  A. Further consolidate modules (target: 15-18 modules)")
        print("  B. Optimize other dependency types")
        print("  C. Release v2.1 with transparent documentation")
        print("  D. Investigate algorithm thresholds further")
    
    return summary

def main():
    """主函数"""
    print("v2.1 FINAL MATHEMATICAL AUDIT - MODULE CONSOLIDATION VALIDATION")
    print("=" * 70)
    
    matrix_confidence = run_v2_1_audit()
    
    print(f"\n" + "=" * 70)
    if matrix_confidence is not None:
        print("AUDIT COMPLETE - RESULTS AVAILABLE")
    else:
        print("AUDIT FAILED - CHECK ERRORS")
    
    print("=" * 70)
    
    return matrix_confidence is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)