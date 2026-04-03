"""
分析当前模块结构，设计合并方案
"""

import os
from pathlib import Path

def analyze_module_structure():
    """分析模块结构"""
    print("ANALYZING CURRENT MODULE STRUCTURE FOR v2.1 OPTIMIZATION")
    print("=" * 70)
    
    release_dir = Path("D:/openclaw/releases/AISleepGen/v2.0_release")
    
    # 收集所有Python模块
    python_files = list(release_dir.rglob("*.py"))
    
    print(f"\n1. CURRENT MODULE STRUCTURE")
    print("-" * 50)
    
    # 按目录分组
    modules_by_dir = {}
    for py_file in python_files:
        rel_path = py_file.relative_to(release_dir)
        dir_path = rel_path.parent
        
        if dir_path not in modules_by_dir:
            modules_by_dir[dir_path] = []
        
        modules_by_dir[dir_path].append({
            "file": rel_path,
            "size": py_file.stat().st_size,
            "name": py_file.stem
        })
    
    # 显示目录结构
    print("Directory structure and module count:")
    total_modules = 0
    
    for dir_path in sorted(modules_by_dir.keys()):
        modules = modules_by_dir[dir_path]
        module_count = len(modules)
        total_modules += module_count
        
        print(f"  {dir_path}/")
        print(f"    Modules: {module_count}")
        
        # 显示模块详情
        for module in modules[:3]:  # 只显示前3个
            print(f"      - {module['file'].name} ({module['size']} bytes)")
        
        if len(modules) > 3:
            print(f"      ... and {len(modules)-3} more")
    
    print(f"\nTotal Python modules: {total_modules}")
    
    # 分析模块大小分布
    print(f"\n2. MODULE SIZE ANALYSIS")
    print("-" * 50)
    
    module_sizes = []
    for py_file in python_files:
        module_sizes.append(py_file.stat().st_size)
    
    if module_sizes:
        avg_size = sum(module_sizes) / len(module_sizes)
        min_size = min(module_sizes)
        max_size = max(module_sizes)
        
        print(f"Module size statistics:")
        print(f"  Average: {avg_size:.0f} bytes")
        print(f"  Minimum: {min_size} bytes")
        print(f"  Maximum: {max_size} bytes")
        
        # 大小分类
        small_modules = [s for s in module_sizes if s < 500]
        medium_modules = [s for s in module_sizes if 500 <= s < 2000]
        large_modules = [s for s in module_sizes if s >= 2000]
        
        print(f"\nModule size distribution:")
        print(f"  Small (<500B): {len(small_modules)} modules")
        print(f"  Medium (500B-2KB): {len(medium_modules)} modules")
        print(f"  Large (≥2KB): {len(large_modules)} modules")
    
    # 分析模块功能
    print(f"\n3. MODULE FUNCTION ANALYSIS")
    print("-" * 50)
    
    # 按名称分类
    module_categories = {
        "config": [],
        "utils": [],
        "interface": [],
        "core": [],
        "data": [],
        "reporting": []
    }
    
    for py_file in python_files:
        name = py_file.stem.lower()
        
        if "config" in name:
            module_categories["config"].append(py_file)
        elif "util" in name or "helper" in name or "logger" in name:
            module_categories["utils"].append(py_file)
        elif "interface" in name or "api" in name:
            module_categories["interface"].append(py_file)
        elif "core" in str(py_file.parent):
            module_categories["core"].append(py_file)
        elif "data" in str(py_file.parent):
            module_categories["data"].append(py_file)
        elif "reporting" in str(py_file.parent):
            module_categories["reporting"].append(py_file)
        else:
            # 检查父目录
            parent = py_file.parent.name.lower()
            if parent in module_categories:
                module_categories[parent].append(py_file)
            else:
                module_categories["utils"].append(py_file)  # 默认
    
    print("Module categories:")
    for category, files in module_categories.items():
        if files:
            print(f"  {category.capitalize()}: {len(files)} modules")
    
    # 识别合并机会
    print(f"\n4. MERGE OPPORTUNITIES IDENTIFICATION")
    print("-" * 50)
    
    merge_opportunities = []
    
    # 小模块合并
    small_module_files = [f for f in python_files if f.stat().st_size < 500]
    if len(small_module_files) >= 3:
        merge_opportunities.append({
            "type": "small_modules",
            "description": f"{len(small_module_files)} small modules (<500B) can be merged",
            "modules": [f.relative_to(release_dir) for f in small_module_files[:5]],
            "potential_reduction": len(small_module_files) - 1
        })
    
    # 相似功能模块合并
    for category, files in module_categories.items():
        if len(files) >= 3:
            merge_opportunities.append({
                "type": f"similar_{category}",
                "description": f"{len(files)} {category} modules can be consolidated",
                "modules": [f.relative_to(release_dir) for f in files[:3]],
                "potential_reduction": len(files) // 2
            })
    
    # 按目录合并
    for dir_path, modules in modules_by_dir.items():
        if len(modules) >= 4:
            merge_opportunities.append({
                "type": f"directory_{dir_path.name}",
                "description": f"{len(modules)} modules in {dir_path} can be merged",
                "modules": [m["file"] for m in modules[:3]],
                "potential_reduction": len(modules) // 2
            })
    
    print("Identified merge opportunities:")
    for i, opp in enumerate(merge_opportunities, 1):
        print(f"  {i}. {opp['description']}")
        print(f"     Potential reduction: {opp['potential_reduction']} modules")
    
    total_potential_reduction = sum(opp["potential_reduction"] for opp in merge_opportunities)
    print(f"\nTotal potential module reduction: {total_potential_reduction}")
    
    # 计算优化后模块数量
    optimized_module_count = total_modules - total_potential_reduction
    print(f"Current modules: {total_modules}")
    print(f"Optimized target: {optimized_module_count}")
    
    # 密度和置信度预测
    print(f"\n5. DENSITY AND CONFIDENCE PREDICTION")
    print("-" * 50)
    
    # 当前密度 (从审核结果)
    current_density = 0.2500
    current_modules = 30  # 实际模块数
    current_confidence = 0.700
    
    # 优化后预测
    optimized_modules = optimized_module_count
    # 假设依赖数量不变（实际可能减少）
    # density = dependencies / (modules²)
    # 如果依赖不变，密度变化比例 = (current_modules²) / (optimized_modules²)
    
    density_ratio = (current_modules * current_modules) / (optimized_modules * optimized_modules)
    predicted_density = current_density * density_ratio
    predicted_confidence = 0.6 + (predicted_density * 0.4)
    
    print(f"Current state:")
    print(f"  Modules: {current_modules}")
    print(f"  Density: {current_density:.4f}")
    print(f"  Confidence: {current_confidence:.3f}")
    
    print(f"\nPredicted after optimization:")
    print(f"  Modules: {optimized_modules}")
    print(f"  Density: {predicted_density:.4f}")
    print(f"  Confidence: {predicted_confidence:.3f}")
    
    print(f"\nImprovement prediction:")
    print(f"  Module reduction: {current_modules - optimized_modules} (-{(current_modules - optimized_modules)/current_modules*100:.1f}%)")
    print(f"  Density increase: {predicted_density - current_density:+.4f} ({(predicted_density/current_density-1)*100:+.1f}%)")
    print(f"  Confidence improvement: {predicted_confidence - current_confidence:+.3f}")
    
    target_confidence = 0.850
    if predicted_confidence >= target_confidence:
        print(f"  TARGET ACHIEVED: {predicted_confidence:.3f} >= {target_confidence}")
    else:
        print(f"  TARGET GAP: {target_confidence - predicted_confidence:.3f}")
    
    # 保存分析结果
    analysis = {
        "analysis_time": "2026-03-31T11:02:00Z",
        "current_state": {
            "total_modules": total_modules,
            "module_categories": {k: len(v) for k, v in module_categories.items()},
            "module_sizes": {
                "small": len(small_modules),
                "medium": len(medium_modules),
                "large": len(large_modules)
            }
        },
        "merge_opportunities": merge_opportunities,
        "optimization_prediction": {
            "current_modules": current_modules,
            "optimized_modules": optimized_modules,
            "module_reduction": current_modules - optimized_modules,
            "current_density": current_density,
            "predicted_density": predicted_density,
            "current_confidence": current_confidence,
            "predicted_confidence": predicted_confidence,
            "confidence_improvement": predicted_confidence - current_confidence,
            "target_confidence": target_confidence,
            "target_achieved": predicted_confidence >= target_confidence
        },
        "recommendation": "Proceed with module consolidation based on identified opportunities"
    }
    
    analysis_file = "module_consolidation_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        import json
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis saved: {analysis_file}")
    
    return analysis

def main():
    """主分析函数"""
    print("v2.1 MODULE CONSOLIDATION ANALYSIS")
    print("=" * 70)
    
    analysis = analyze_module_structure()
    
    print(f"\n" + "=" * 70)
    print("ANALYSIS COMPLETE - READY FOR OPTIMIZATION")
    print("=" * 70)
    
    return analysis is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)