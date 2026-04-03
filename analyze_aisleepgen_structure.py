"""
分析AISleepGen代码结构，识别模块化问题
"""

import ast
import json
from pathlib import Path

def analyze_python_file(filepath):
    """分析Python文件结构"""
    print(f"Analyzing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        
        # 统计信息
        stats = {
            'file_size_kb': len(content) / 1024,
            'lines': len(content.split('\n')),
            'classes': 0,
            'functions': 0,
            'methods': 0,
            'imports': 0,
            'nested_functions': 0,
            'complexity_hints': []
        }
        
        # 遍历AST
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                stats['classes'] += 1
                # 检查类的方法数量
                methods = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
                if methods > 10:
                    stats['complexity_hints'].append(f"Class '{node.name}' has {methods} methods (consider splitting)")
            
            elif isinstance(node, ast.FunctionDef):
                # 检查是否在类中
                in_class = any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if node in getattr(parent, 'body', []))
                if in_class:
                    stats['methods'] += 1
                else:
                    stats['functions'] += 1
                
                # 检查函数复杂度
                if len(node.body) > 50:
                    stats['complexity_hints'].append(f"Function '{node.name}' has {len(node.body)} lines")
                
                # 检查嵌套函数
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.FunctionDef) and subnode != node:
                        stats['nested_functions'] += 1
            
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                stats['imports'] += 1
        
        return stats
        
    except SyntaxError as e:
        print(f"  Syntax error: {e}")
        return None

def analyze_skill_structure():
    """分析技能结构"""
    print("ANALYZING AISLEEPGEN CODE STRUCTURE")
    print("=" * 70)
    
    skill_path = Path("D:/openclaw/releases/AISleepGen/v1.0.7_fixed")
    
    if not skill_path.exists():
        print(f"ERROR: Skill path not found: {skill_path}")
        return False
    
    # 分析主技能文件
    main_file = skill_path / "skill.py"
    if not main_file.exists():
        print(f"ERROR: Main skill file not found: {main_file}")
        return False
    
    print(f"\n1. Main skill file analysis:")
    main_stats = analyze_python_file(main_file)
    
    if main_stats:
        print(f"   File size: {main_stats['file_size_kb']:.1f} KB")
        print(f"   Lines: {main_stats['lines']}")
        print(f"   Classes: {main_stats['classes']}")
        print(f"   Methods: {main_stats['methods']}")
        print(f"   Functions: {main_stats['functions']}")
        print(f"   Imports: {main_stats['imports']}")
        print(f"   Nested functions: {main_stats['nested_functions']}")
        
        if main_stats['complexity_hints']:
            print(f"\n   Complexity warnings:")
            for warning in main_stats['complexity_hints'][:5]:  # 显示前5个
                print(f"   - {warning}")
    
    # 分析目录结构
    print(f"\n2. Directory structure analysis:")
    files = list(skill_path.rglob("*.py"))
    print(f"   Total Python files: {len(files)}")
    
    if len(files) == 1:
        print(f"   WARNING: Only one Python file (high coupling risk)")
    
    # 检查模块化机会
    print(f"\n3. Modularization opportunities:")
    
    # 读取skill.py内容寻找功能模块
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找主要方法（简单启发式）
    import re
    method_pattern = r'def (\w+)\s*\(self[^)]*\)'
    methods = re.findall(method_pattern, content)
    
    print(f"   Found {len(methods)} methods in main class")
    
    # 按功能分组方法
    functional_groups = {
        'sleep_analysis': ['analyze_sleep', 'parse_edf', 'extract_sleep_stages'],
        'stress_assessment': ['check_stress', 'calculate_hrv', 'assess_stress_level'],
        'meditation': ['meditation_guide', 'suggest_technique', 'generate_meditation'],
        'file_operations': ['file_info', 'validate_file', 'read_file_safely'],
        'reporting': ['generate_report', 'format_results', 'create_summary'],
        'utility': ['env_check', 'calculate_statistics', 'validate_input']
    }
    
    # 实际找到的方法分组
    found_groups = {group: [] for group in functional_groups}
    other_methods = []
    
    for method in methods:
        matched = False
        for group, patterns in functional_groups.items():
            for pattern in patterns:
                if pattern in method.lower():
                    found_groups[group].append(method)
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            other_methods.append(method)
    
    print(f"\n4. Functional grouping analysis:")
    for group, methods in found_groups.items():
        if methods:
            print(f"   {group}: {len(methods)} methods")
            if len(methods) > 5:
                print(f"     → Consider separate module")
    
    if other_methods:
        print(f"   Other methods: {len(other_methods)}")
        if len(other_methods) > 10:
            print(f"     → High number of uncategorized methods")
    
    # 生成重构建议
    print(f"\n5. Refactoring recommendations:")
    
    recommendations = []
    
    # 基于分析的建议
    if main_stats['file_size_kb'] > 20:
        recommendations.append("Main file too large (>20KB), split into modules")
    
    if main_stats['methods'] > 15:
        recommendations.append(f"Too many methods ({main_stats['methods']}) in single class")
    
    if len(files) == 1:
        recommendations.append("Single Python file architecture, create module structure")
    
    # 功能分组建议
    for group, methods in found_groups.items():
        if len(methods) >= 3:
            recommendations.append(f"Create '{group}' module with {len(methods)} related methods")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print(f"   No major refactoring needed")
    
    # 保存分析报告
    report = {
        'analysis_time': '2026-03-31T08:55:00Z',
        'skill': 'AISleepGen v1.0.7_fixed',
        'main_file': str(main_file),
        'statistics': main_stats,
        'method_count': len(methods),
        'functional_groups': {k: v for k, v in found_groups.items() if v},
        'other_methods': other_methods,
        'recommendations': recommendations,
        'modularization_plan': {
            'target_structure': [
                'sleep_analyzer/',
                'stress_assessor/',
                'meditation_guide/',
                'file_utils/',
                'report_generator/',
                'skill.py (lightweight main class)'
            ]
        }
    }
    
    report_file = 'aisleepgen_structure_analysis.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n6. Analysis report saved: {report_file}")
    
    return True

def main():
    """主函数"""
    print("AISLEEPGEN MODULE STRUCTURE ANALYSIS")
    print("=" * 70)
    
    if analyze_skill_structure():
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("Ready for modularization refactoring.")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("ANALYSIS FAILED")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)