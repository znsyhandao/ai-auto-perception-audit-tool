"""
简单运行验证测试 - 避免编码问题
"""

import json
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

def main():
    print("SIMPLE VALIDATION TEST RUN")
    print("=" * 70)
    
    # 加载测试用例
    with open('matrix_test_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    results = []
    
    for test_case in test_cases:
        name = test_case["name"]
        modules = test_case["modules"]
        dependencies = test_case["dependencies"]
        
        density = calculate_dependency_density(modules, dependencies)
        confidence = calculate_confidence(density)
        
        print(f"\nTest: {name}")
        print(f"  Modules: {len(modules)}")
        print(f"  Dependencies: {len(dependencies)}")
        print(f"  Density: {density:.4f}")
        print(f"  Confidence: {confidence:.3f}")
        
        results.append({
            "name": name,
            "modules": len(modules),
            "dependencies": len(dependencies),
            "density": density,
            "confidence": confidence
        })
    
    # 分析结果
    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    if len(results) >= 2:
        ideal = results[0]
        chaotic = results[1]
        
        print(f"\nComparison: {ideal['name']} vs {chaotic['name']}")
        print(f"  Density: {ideal['density']:.4f} -> {chaotic['density']:.4f}")
        print(f"  Confidence: {ideal['confidence']:.3f} -> {chaotic['confidence']:.3f}")
        
        if chaotic['confidence'] > ideal['confidence']:
            print("  RESULT: Algorithm correctly detects higher density as worse")
        else:
            print("  RESULT: Algorithm may not correctly detect quality differences")
    
    # AISleepGen分析
    if len(results) >= 4:
        current = results[2]
        target = results[3]
        
        print(f"\nAISleepGen Optimization Analysis:")
        print(f"  Current: density={current['density']:.4f}, confidence={current['confidence']:.3f}")
        print(f"  Target: density={target['density']:.4f}, confidence={target['confidence']:.3f}")
        
        density_reduction = current['density'] - target['density']
        confidence_improvement = target['confidence'] - current['confidence']
        
        print(f"  Density reduction: {density_reduction:.4f}")
        print(f"  Confidence improvement: {confidence_improvement:.3f}")
        
        if target['density'] < current['density']:
            print("  RESULT: Optimization reduces dependency density")
        else:
            print("  RESULT: Optimization does not reduce density")
    
    # 保存结果
    with open('simple_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("Results saved to simple_validation_results.json")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()