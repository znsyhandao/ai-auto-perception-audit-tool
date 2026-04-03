"""
矩阵分解算法验证脚本
验证优化是否能被有效检测
"""

import numpy as np

def calculate_dependency_density(modules, dependencies):
    """计算依赖密度"""
    n = len(modules)
    if n == 0:
        return 0.0
    
    module_index = {module: i for i, module in enumerate(modules)}
    adjacency_matrix = np.zeros((n, n))
    
    for dep_from, dep_to in dependencies:
        if dep_from in module_index and dep_to in module_index:
            i, j = module_index[dep_from], module_index[dep_to]
            adjacency_matrix[i, j] = 1
    
    total_possible = n * n
    actual_dependencies = np.sum(adjacency_matrix)
    
    return actual_dependencies / total_possible

def calculate_confidence(density):
    """计算置信度"""
    return 0.6 + (density * 0.4)

def analyze_architecture(modules, dependencies, name):
    """分析架构"""
    density = calculate_dependency_density(modules, dependencies)
    confidence = calculate_confidence(density)
    
    print(f"\nArchitecture: {name}")
    print(f"  Modules: {len(modules)}")
    print(f"  Dependencies: {len(dependencies)}")
    print(f"  Density: {density:.4f}")
    print(f"  Confidence: {confidence:.3f}")
    
    return {
        "name": name,
        "modules": len(modules),
        "dependencies": len(dependencies),
        "density": density,
        "confidence": confidence
    }

def run_test_cases(test_cases):
    """运行测试用例"""
    print("=" * 70)
    print("MATRIX DECOMPOSITION VALIDATION TESTS")
    print("=" * 70)
    
    results = []
    
    for test_case in test_cases:
        result = analyze_architecture(
            test_case["modules"],
            test_case["dependencies"],
            test_case["name"]
        )
        results.append(result)
    
    # 分析结果
    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    if len(results) >= 2:
        # 比较第一个和最后一个（理想vs混乱）
        ideal = results[0]
        chaotic = results[1]
        
        print(f"\nComparison: {ideal['name']} vs {chaotic['name']}")
        print(f"  Density difference: {chaotic['density'] - ideal['density']:.4f}")
        print(f"  Confidence difference: {chaotic['confidence'] - ideal['confidence']:.3f}")
        
        # 验证算法是否能检测质量差异
        if chaotic['confidence'] > ideal['confidence']:
            print("  ✅ Algorithm correctly detects higher density as worse")
        else:
            print("  ⚠️ Algorithm may not correctly detect quality differences")
    
    # 检查AISleepGen优化效果
    if len(results) >= 4:
        current = results[2]
        target = results[3]
        
        print(f"\nAISleepGen Optimization Analysis:")
        print(f"  Current density: {current['density']:.4f}")
        print(f"  Target density: {target['density']:.4f}")
        print(f"  Density reduction: {current['density'] - target['density']:.4f}")
        print(f"  Confidence improvement: {target['confidence'] - current['confidence']:.3f}")
        
        if target['density'] < current['density']:
            print("  ✅ Optimization reduces dependency density")
        else:
            print("  ⚠️ Optimization does not reduce density")
    
    return results

if __name__ == "__main__":
    # 加载测试用例
    import json
    with open('matrix_test_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    results = run_test_cases(test_cases)
    
    # 保存结果
    with open('validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("Results saved to validation_results.json")
    print("=" * 70)
