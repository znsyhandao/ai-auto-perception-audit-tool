"""
分析依赖检测机制
"""

import ast
import os
from pathlib import Path

def analyze_skill_structure():
    """分析技能结构"""
    print("ANALYZING SKILL STRUCTURE FOR DEPENDENCY DETECTION")
    print("=" * 70)
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    
    print("\n1. What the algorithm might see:")
    print("-" * 50)
    
    # 检查skill.py - 这是主要入口
    skill_file = skill_dir / "skill.py"
    if skill_file.exists():
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Main skill file: {skill_file}")
        print(f"Size: {skill_file.stat().st_size} bytes")
        
        # 分析导入
        try:
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        imports.append(f"{module}.{name.name}")
            
            print(f"Imports in skill.py: {len(imports)}")
            for imp in imports[:10]:  # 只显示前10个
                print(f"  - {imp}")
            if len(imports) > 10:
                print(f"  ... and {len(imports)-10} more")
                
        except:
            print("  Could not parse imports")
    
    print("\n2. Module detection hypothesis:")
    print("-" * 50)
    
    print("Possible ways algorithm detects modules:")
    print("A. Python files only (what we assume)")
    print("B. Directories as modules")
    print("C. Import statements as modules")
    print("D. Combined approach")
    
    # 测试不同检测方法
    print("\n3. Testing different module detection methods:")
    print("-" * 50)
    
    # 方法A: Python文件
    py_files = list(skill_dir.rglob("*.py"))
    print(f"Method A (Python files): {len(py_files)} modules")
    
    # 方法B: 目录
    all_dirs = [d for d in skill_dir.rglob("") if d.is_dir()]
    print(f"Method B (All directories): {len(all_dirs)} modules")
    
    # 方法C: 非空目录
    non_empty_dirs = []
    for d in all_dirs:
        if any(d.iterdir()):
            non_empty_dirs.append(d)
    print(f"Method C (Non-empty directories): {len(non_empty_dirs)} modules")
    
    # 方法D: 有Python文件的目录
    py_dirs = set()
    for py_file in py_files:
        py_dirs.add(py_file.parent)
    print(f"Method D (Directories with Python files): {len(py_dirs)} modules")
    
    print("\n4. Dependency detection hypothesis:")
    print("-" * 50)
    
    print("Possible ways algorithm detects dependencies:")
    print("A. Import statements (what we analyze)")
    print("B. Function calls")
    print("C. Class inheritance")
    print("D. File references")
    print("E. Directory relationships")
    
    # 分析实际的依赖关系
    print("\n5. Actual structure analysis:")
    print("-" * 50)
    
    # 目录结构
    print("Directory tree (simplified):")
    for item in skill_dir.iterdir():
        if item.is_dir():
            py_count = sum(1 for _ in item.rglob("*.py"))
            print(f"  {item.name}/ ({py_count} Python files)")
    
    print("\n6. Key insight:")
    print("-" * 50)
    
    insight = """
KEY INSIGHT: The algorithm might detect modules and dependencies DIFFERENTLY than we assume.

Our assumption:
• Modules = Python files (30 → 22)
• Dependencies = import statements + calls + inheritance

Algorithm might:
• Modules = directories with Python files (~12)
• Dependencies = directory relationships + imports

If algorithm uses directory-based module detection:
• v1.0.9: ~5 directories
• v2.0: ~12 directories  
• v2.1: ~12 directories (same as v2.0)

This could explain why confidence doesn't change!
"""
    
    print(insight)
    
    print("\n7. Testing the hypothesis:")
    print("-" * 50)
    
    # 计算如果模块=目录的情况
    dirs_with_py = len(py_dirs)
    print(f"If modules = directories with Python files: {dirs_with_py}")
    
    # 假设依赖数量
    assumed_deps = 45  # 我们的分析
    
    # 计算密度
    density = assumed_deps / (dirs_with_py * dirs_with_py) if dirs_with_py > 0 else 0
    confidence = 0.6 + (density * 0.4)
    confidence = min(0.95, max(0.5, confidence))
    
    print(f"  Density: {density:.4f}")
    print(f"  Confidence: {confidence:.3f}")
    
    # 比较
    print(f"\nComparison with actual confidence (0.700):")
    print(f"  Calculated: {confidence:.3f}")
    print(f"  Actual: 0.700")
    print(f"  Difference: {confidence - 0.700:+.3f}")
    
    # 保存分析
    import json
    analysis = {
        "analysis_time": "2026-03-31T11:26:00Z",
        "module_detection_hypotheses": {
            "python_files": len(py_files),
            "all_directories": len(all_dirs),
            "non_empty_directories": len(non_empty_dirs),
            "directories_with_python": len(py_dirs)
        },
        "dependency_detection_hypotheses": [
            "import_statements",
            "function_calls", 
            "class_inheritance",
            "file_references",
            "directory_relationships"
        ],
        "directory_based_hypothesis": {
            "directories_with_py": dirs_with_py,
            "assumed_dependencies": assumed_deps,
            "calculated_density": density,
            "calculated_confidence": confidence,
            "actual_confidence": 0.700,
            "difference": confidence - 0.700
        },
        "key_insight": "Algorithm might use directory-based module detection, not file-based",
        "explanation": "If algorithm counts directories (not files) as modules, then v2.0 and v2.1 have same module count → same density → same confidence",
        "verification_method": "Need to examine algorithm's actual module detection code"
    }
    
    with open("dependency_detection_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis saved: dependency_detection_analysis.json")
    
    return True

def main():
    """主分析函数"""
    print("DEPENDENCY DETECTION MECHANISM ANALYSIS")
    print("=" * 70)
    
    success = analyze_skill_structure()
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE - NEW HYPOTHESIS IDENTIFIED")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)