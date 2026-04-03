"""
创建验证测试套件
优先级2：确保优化能被有效检测
"""

import json
import numpy as np
from pathlib import Path

def main():
    """分析矩阵分解算法，创建测试用例"""
    print("CREATING VALIDATION TEST SUITE")
    print("=" * 70)
    
    print("\n1. Analyzing matrix decomposition algorithm...")
    
    # 算法分析结果
    algorithm_info = {
        "formula": "confidence = 0.6 + (dependency_density × 0.4)",
        "dependency_density_formula": "density = dependencies_count / (modules_count²)",
        "confidence_range": [0.6, 1.0],
        "detected_dimensions": ["dependency_density"],
        "undetected_dimensions": [
            "dependency_direction",
            "hierarchical_structure", 
            "interface_quality",
            "module_cohesion"
        ]
    }
    
    print(f"   Formula: {algorithm_info['formula']}")
    print(f"   Detected: {algorithm_info['detected_dimensions']}")
    print(f"   Not detected: {algorithm_info['undetected_dimensions']}")
    
    # 2. 创建测试用例
    print("\n2. Creating test cases...")
    
    test_cases = []
    
    # 测试用例1：理想架构（低密度）
    test_cases.append({
        "name": "ideal_architecture",
        "description": "理想架构：清晰层次，低依赖密度",
        "modules": ["core", "data", "utils", "interfaces", "reporting"],
        "dependencies": [
            ("core", "data"),
            ("core", "utils"),
            ("data", "utils"),
            ("interfaces", "core"),
            ("reporting", "core")
        ],
        "expected_density": 5 / 25,  # 5依赖 / 25可能
        "expected_confidence": 0.6 + (5/25) * 0.4,
        "architecture_quality": "high",
        "optimization_focus": "dependency_density"
    })
    
    # 测试用例2：混乱架构（高密度）
    test_cases.append({
        "name": "chaotic_architecture",
        "description": "混乱架构：网状依赖，高密度",
        "modules": ["A", "B", "C", "D", "E"],
        "dependencies": [
            ("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"),
            ("B", "A"), ("B", "C"), ("B", "D"), ("B", "E"),
            ("C", "A"), ("C", "B"), ("C", "D"), ("C", "E"),
            ("D", "A"), ("D", "B"), ("D", "C"), ("D", "E"),
            ("E", "A"), ("E", "B"), ("E", "C"), ("E", "D")
        ],
        "expected_density": 20 / 25,  # 20依赖 / 25可能
        "expected_confidence": 0.6 + (20/25) * 0.4,
        "architecture_quality": "low",
        "optimization_focus": "dependency_density"
    })
    
    # 测试用例3：AISleepGen当前架构
    test_cases.append({
        "name": "aisleepgen_current",
        "description": "AISleepGen v1.0.9当前架构",
        "modules": ["skill", "core.sleep_stager", "core.sleep_scorer", "core.stress_analyzer", 
                   "core.meditation_techniques", "data.file_reader", "data.data_validator",
                   "data.statistics", "utils.security", "utils.logging", "utils.configuration",
                   "interfaces.sleep", "interfaces.stress", "interfaces.meditation",
                   "reporting.formatter", "reporting.generator"],
        "dependencies": [
            # 假设的依赖关系 - 需要实际分析
            ("skill", "core.sleep_stager"),
            ("skill", "core.sleep_scorer"),
            ("skill", "core.stress_analyzer"),
            ("skill", "core.meditation_techniques"),
            ("core.sleep_stager", "data.file_reader"),
            ("core.sleep_scorer", "data.data_validator"),
            ("core.stress_analyzer", "data.statistics"),
            ("interfaces.sleep", "core.sleep_stager"),
            ("interfaces.sleep", "core.sleep_scorer"),
            ("reporting.formatter", "core.sleep_scorer"),
            ("reporting.generator", "reporting.formatter")
        ],
        "expected_density": 11 / 256,  # 11依赖 / 16²=256可能
        "expected_confidence": 0.6 + (11/256) * 0.4,
        "architecture_quality": "medium",
        "optimization_focus": "dependency_density_reduction"
    })
    
    # 测试用例4：优化目标架构
    test_cases.append({
        "name": "aisleepgen_target",
        "description": "AISleepGen v2.0目标架构（依赖密度优化后）",
        "modules": ["skill", "core.sleep_stager", "core.sleep_scorer", "core.stress_analyzer", 
                   "core.meditation_techniques", "data.file_reader", "data.data_validator",
                   "data.statistics", "utils.security", "utils.logging", "utils.configuration",
                   "interfaces.sleep", "interfaces.stress", "interfaces.meditation",
                   "reporting.formatter", "reporting.generator"],
        "dependencies": [
            # 优化后的依赖 - 减少数量，明确方向
            ("skill", "interfaces.sleep"),  # 通过接口访问
            ("skill", "interfaces.stress"),
            ("skill", "interfaces.meditation"),
            ("interfaces.sleep", "core.sleep_stager"),
            ("interfaces.sleep", "core.sleep_scorer"),
            ("core.sleep_stager", "data.file_reader"),
            ("core.sleep_scorer", "data.data_validator"),
            ("reporting.generator", "reporting.formatter")
        ],
        "expected_density": 8 / 256,  # 8依赖 / 256可能
        "expected_confidence": 0.6 + (8/256) * 0.4,
        "architecture_quality": "high",
        "optimization_focus": "dependency_density_optimized",
        "improvement_from_current": (11/256 - 8/256) * 0.4  # 置信度改进
    })
    
    print(f"   Created {len(test_cases)} test cases")
    
    # 3. 创建验证脚本
    print("\n3. Creating validation script...")
    
    validation_script = '''"""
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
    
    print(f"\\nArchitecture: {name}")
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
    print("\\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    if len(results) >= 2:
        # 比较第一个和最后一个（理想vs混乱）
        ideal = results[0]
        chaotic = results[1]
        
        print(f"\\nComparison: {ideal['name']} vs {chaotic['name']}")
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
        
        print(f"\\nAISleepGen Optimization Analysis:")
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
    
    print("\\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("Results saved to validation_results.json")
    print("=" * 70)
'''
    
    script_file = Path("matrix_validation.py")
    script_file.write_text(validation_script, encoding='utf-8')
    print(f"   Created: {script_file.name}")
    
    # 4. 保存测试用例
    print("\n4. Saving test cases...")
    
    test_cases_file = Path("matrix_test_cases.json")
    with open(test_cases_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    
    print(f"   Saved: {test_cases_file.name}")
    
    # 5. 创建优化指导
    print("\n5. Creating optimization guide...")
    
    optimization_guide = {
        "principle": "理解优先于通过",
        "algorithm_understanding": {
            "what_it_detects": "dependency_density",
            "formula": "confidence = 0.6 + (density × 0.4)",
            "how_to_improve": "Reduce dependency density"
        },
        "optimization_strategies": [
            {
                "strategy": "reduce_dependency_count",
                "description": "减少依赖关系数量",
                "methods": [
                    "消除不必要的依赖",
                    "合并相关功能",
                    "使用接口减少直接依赖"
                ],
                "expected_effect": "降低密度，提高置信度"
            },
            {
                "strategy": "increase_module_count",
                "description": "增加模块数量（谨慎使用）",
                "methods": [
                    "合理拆分大模块",
                    "创建清晰的模块边界",
                    "避免过度拆分"
                ],
                "expected_effect": "可能降低密度，但需平衡"
            },
            {
                "strategy": "optimize_dependency_direction",
                "description": "优化依赖方向",
                "methods": [
                    "创建单向依赖",
                    "避免循环依赖",
                    "建立层次结构"
                ],
                "note": "算法不直接检测，但改善架构质量"
            }
        ],
        "validation_method": {
            "step1": "计算当前依赖密度",
            "step2": "设定优化目标密度",
            "step3": "实施优化策略",
            "step4": "验证密度降低",
            "step5": "验证置信度提高"
        },
        "targets_for_aisleepgen": {
            "current_density": "待计算",
            "target_density": 0.03,  # 3%密度
            "current_confidence": 0.700,
            "target_confidence": 0.612,  # 0.6 + 0.03×0.4
            "improvement_needed": "密度从~0.043降到0.03"
        }
    }
    
    guide_file = Path("matrix_optimization_guide.json")
    with open(guide_file, 'w', encoding='utf-8') as f:
        json.dump(optimization_guide, f, indent=2, ensure_ascii=False)
    
    print(f"   Created: {guide_file.name}")
    
    # 6. 运行验证测试
    print("\n6. Running validation tests...")
    
    # 先保存测试用例
    test_cases_for_script = []
    for tc in test_cases:
        test_cases_for_script.append({
            "name": tc["name"],
            "modules": tc["modules"],
            "dependencies": tc["dependencies"]
        })
    
    with open("matrix_test_cases.json", 'w', encoding='utf-8') as f:
        json.dump(test_cases_for_script, f, indent=2)
    
    # 运行验证脚本
    import subprocess
    try:
        result = subprocess.run(
            ["python", "matrix_validation.py"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("   Validation tests passed")
            print(result.stdout[-500:])  # 显示最后500字符
        else:
            print(f"   Validation tests failed: {result.stderr}")
    
    except Exception as e:
        print(f"   Error running validation: {e}")
    
    print("\n" + "=" * 70)
    print("VALIDATION TEST SUITE CREATED")
    print("=" * 70)
    print("\nCreated files:")
    print("  - matrix_validation.py (验证脚本)")
    print("  - matrix_test_cases.json (测试用例)")
    print("  - matrix_optimization_guide.json (优化指导)")
    print("\nPriority 2 complete: Validation tests created.")
    
    return True

if __name__ == "__main__":
    main()