"""
运行测试技能审核验证假设
"""

import requests
import json
import time
from pathlib import Path

def audit_test_skill(skill_name, skill_path):
    """审核测试技能"""
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
    
    # 运行矩阵审核
    audit_data = {
        'skill_id': skill_name,
        'skill_path': str(skill_path),
        'audit_types': ['matrix'],
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
            
            # 提取矩阵结果
            certificates = result.get('mathematical_certificates', [])
            
            matrix_cert = None
            for cert in certificates:
                if "matrix" in cert.get("theorem", "").lower():
                    matrix_cert = cert
                    break
            
            if matrix_cert:
                confidence = matrix_cert.get("confidence", 0)
                validity = matrix_cert.get("validity", "unknown")
                
                print(f"  Matrix confidence: {confidence:.3f}")
                print(f"  Validity: {validity}")
                print(f"  Audit time: {audit_time:.2f}s")
                
                return {
                    'skill': skill_name,
                    'path': str(skill_path),
                    'confidence': confidence,
                    'validity': validity,
                    'audit_time': audit_time
                }
            else:
                print(f"  ERROR: Matrix certificate not found")
                return None
        else:
            print(f"  ERROR: Audit failed with HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def analyze_structure(skill_path):
    """分析技能结构"""
    path = Path(skill_path)
    
    # 统计
    py_files = list(path.rglob("*.py"))
    dirs_with_py = len(set(p.parent for p in py_files))
    total_dirs = len([d for d in path.rglob("") if d.is_dir()])
    
    # 主要目录（排除根目录）
    main_dirs = []
    for item in path.iterdir():
        if item.is_dir():
            py_count = sum(1 for _ in item.rglob("*.py"))
            if py_count > 0:
                main_dirs.append(item.name)
    
    return {
        'python_files': len(py_files),
        'dirs_with_python': dirs_with_py,
        'total_directories': total_dirs,
        'main_directories': main_dirs,
        'main_dir_count': len(main_dirs)
    }

def main():
    """主验证函数"""
    print("RUNNING TEST AUDITS TO VALIDATE DIRECTORY HYPOTHESIS")
    print("=" * 70)
    
    test_skills = [
        ("skill_a", "D:/openclaw/test_skills/skill_a"),
        ("skill_b", "D:/openclaw/test_skills/skill_b"),
        ("skill_c", "D:/openclaw/test_skills/skill_c")
    ]
    
    print("\nTest skill structures:")
    print("-" * 50)
    
    structure_data = {}
    for skill_name, skill_path in test_skills:
        structure = analyze_structure(skill_path)
        structure_data[skill_name] = structure
        
        print(f"\n{skill_name}:")
        print(f"  Python files: {structure['python_files']}")
        print(f"  Directories with Python: {structure['dirs_with_python']}")
        print(f"  Main directories: {structure['main_dir_count']}")
        print(f"  Main dirs: {', '.join(structure['main_directories'])}")
    
    print("\n" + "=" * 70)
    print("RUNNING MATHEMATICAL AUDITS")
    print("=" * 70)
    
    audit_results = []
    
    for skill_name, skill_path in test_skills:
        result = audit_test_skill(skill_name, skill_path)
        if result:
            audit_results.append(result)
    
    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    if audit_results:
        print("\nAudit results summary:")
        print("Skill | Dirs w/Python | Main Dirs | Confidence | Validity")
        print("-" * 80)
        
        for result in audit_results:
            skill_name = result['skill']
            structure = structure_data[skill_name]
            
            print(f"{skill_name:7} | {structure['dirs_with_python']:13} | {structure['main_dir_count']:9} | {result['confidence']:10.3f} | {result['validity']}")
        
        print("\nHypothesis validation:")
        print("-" * 50)
        
        # 按置信度排序
        sorted_results = sorted(audit_results, key=lambda x: x['confidence'], reverse=True)
        
        if len(sorted_results) >= 2:
            highest = sorted_results[0]
            lowest = sorted_results[-1]
            
            print(f"Highest confidence: {highest['skill']} ({highest['confidence']:.3f})")
            print(f"Lowest confidence: {lowest['skill']} ({lowest['confidence']:.3f})")
            
            # 检查是否符合假设
            skill_c_conf = next((r['confidence'] for r in audit_results if r['skill'] == 'skill_c'), 0)
            skill_a_conf = next((r['confidence'] for r in audit_results if r['skill'] == 'skill_a'), 0)
            
            if skill_c_conf > skill_a_conf:
                print("\n✅ HYPOTHESIS SUPPORTED:")
                print("  Skill C (1 dir) has higher confidence than Skill A (6 dirs)")
                print("  This suggests algorithm counts directories as modules")
            else:
                print("\n❌ HYPOTHESIS NOT SUPPORTED:")
                print("  Directory count does not correlate with confidence")
                print("  Algorithm may use different module detection")
            
            # 检查AISleepGen的置信度
            print(f"\nComparison with AISleepGen (0.700):")
            for result in audit_results:
                diff = result['confidence'] - 0.700
                print(f"  {result['skill']}: {result['confidence']:.3f} ({diff:+.3f} difference)")
        
        # 保存结果
        analysis = {
            "validation_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "hypothesis": "Algorithm counts directories (not files) as modules",
            "test_design": {
                "skill_a": "5 directories, 1 file each",
                "skill_b": "2 directories, multiple files each",
                "skill_c": "Flat structure, all files in root"
            },
            "structure_data": structure_data,
            "audit_results": audit_results,
            "analysis": {
                "sorted_by_confidence": [r['skill'] for r in sorted_results],
                "confidence_range": f"{lowest['confidence']:.3f} - {highest['confidence']:.3f}" if len(sorted_results) >= 2 else "N/A",
                "hypothesis_supported": skill_c_conf > skill_a_conf if skill_c_conf and skill_a_conf else "Inconclusive"
            }
        }
        
        with open("directory_hypothesis_validation.json", 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\nAnalysis saved: directory_hypothesis_validation.json")
    
    else:
        print("ERROR: No audit results obtained")
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    
    return len(audit_results) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)