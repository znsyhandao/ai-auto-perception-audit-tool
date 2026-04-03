"""
分析矩阵实现细节
"""

import ast
import inspect
from pathlib import Path

def analyze_matrix_implementation():
    """分析矩阵实现"""
    print("ANALYZING MATRIX IMPLEMENTATION DETAILS")
    print("=" * 70)
    
    engine_file = Path("D:/OpenClaw_TestingFramework/microservices/mathematical-audit-service/mathematical_ai_engine_final.py")
    
    if not engine_file.exists():
        print(f"ERROR: Engine file not found: {engine_file}")
        return False
    
    with open(engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n1. Searching for matrix_dependency_analysis function...")
    
    # 查找函数
    lines = content.split('\n')
    in_matrix_func = False
    matrix_lines = []
    
    for i, line in enumerate(lines):
        if 'def matrix_dependency_analysis' in line:
            in_matrix_func = True
            print(f"Found at line {i+1}: {line.strip()}")
        
        if in_matrix_func:
            matrix_lines.append(line)
            if line.strip() == '' and i > 0 and 'def ' in lines[i+1]:
                in_matrix_func = False
    
    print(f"Matrix function length: {len(matrix_lines)} lines")
    
    print("\n2. Key implementation details:")
    print("-" * 50)
    
    # 提取关键部分
    key_sections = []
    current_section = []
    
    for line in matrix_lines:
        if '#' in line:
            # 注释
            comment = line[line.index('#'):].strip()
            if comment and len(current_section) > 0:
                key_sections.append(('code', '\n'.join(current_section)))
                current_section = []
            if comment:
                key_sections.append(('comment', comment))
        elif line.strip():
            current_section.append(line)
    
    if current_section:
        key_sections.append(('code', '\n'.join(current_section)))
    
    print("Implementation summary:")
    for i, (type_, content) in enumerate(key_sections[:10]):  # 只显示前10个
        if type_ == 'comment':
            print(f"  # {content}")
        elif 'adjacency_matrix' in content or 'dependency_density' in content:
            print(f"  {content.strip()}")
    
    print("\n3. Analyzing the confidence calculation issue:")
    print("-" * 50)
    
    issue_analysis = """
ISSUE ANALYSIS:

From the code:
1. matrix_dependency_analysis calculates:
   - adjacency_matrix from dependencies
   - dependency_density = sum(adjacency_matrix) / (n * n)
   
2. _calculate_confidence for "matrix":
   - base = 0.6 + (dependency_density * 0.4)
   - confidence = min(0.95, max(0.5, base))

The problem:
• Our test skills have different structures
• But all return confidence=0.700
• This suggests dependency_density is similar for all

Possible reasons:
A. The dependencies parameter passed to matrix_dependency_analysis is wrong
B. The modules parameter is wrong
C. There's default or fallback behavior
D. The algorithm detects minimal dependencies for simple skills

Key question: What are the 'modules' and 'dependencies' parameters?
"""
    
    print(issue_analysis)
    
    print("\n4. Searching for how modules/dependencies are determined:")
    print("-" * 50)
    
    # 查找调用matrix_dependency_analysis的地方
    call_patterns = []
    for i, line in enumerate(lines):
        if 'matrix_dependency_analysis' in line and 'def ' not in line:
            context_start = max(0, i-2)
            context_end = min(len(lines), i+3)
            context = '\n'.join(lines[context_start:context_end])
            call_patterns.append((i+1, context))
    
    if call_patterns:
        print(f"Found {len(call_patterns)} calls to matrix_dependency_analysis:")
        for line_num, context in call_patterns[:3]:  # 只显示前3个
            print(f"\nLine {line_num}:")
            print(context)
    else:
        print("No calls found - may be called from elsewhere")
    
    print("\n5. Hypothesis based on analysis:")
    print("-" * 50)
    
    hypotheses = [
        "H1: The algorithm receives minimal modules/dependencies for simple skills",
        "H2: There's a fallback to default values when analysis fails",
        "H3: The 'questionable' validity affects confidence calculation",
        "H4: Simple skills get a baseline confidence (0.700)",
        "H5: Real analysis only happens for complex skills"
    ]
    
    for i, hypothesis in enumerate(hypotheses, 1):
        print(f"  {i}. {hypothesis}")
    
    print("\n6. Next steps for verification:")
    print("-" * 50)
    
    next_steps = [
        "Trace the actual parameters passed to matrix_dependency_analysis",
        "Check if there's logging of modules/dependencies",
        "Create more complex test skills",
        "Examine the skill analysis that extracts modules/dependencies",
        "Check for default or fallback values in the code"
    ]
    
    for i, step in enumerate(next_steps, 1):
        print(f"  {i}. {step}")
    
    # 保存分析
    import json
    analysis = {
        "analysis_time": "2026-03-31T11:35:00Z",
        "key_finding": "All test skills return confidence=0.700 despite different structures",
        "algorithm_analysis": {
            "matrix_function_found": len(matrix_lines) > 0,
            "confidence_formula": "0.6 + (dependency_density × 0.4)",
            "confidence_range": "0.5 - 0.95",
            "calls_found": len(call_patterns)
        },
        "hypotheses": hypotheses,
        "test_results": {
            "skill_a": {"dirs": 6, "confidence": 0.700},
            "skill_b": {"dirs": 3, "confidence": 0.700},
            "skill_c": {"dirs": 1, "confidence": 0.700}
        },
        "conclusion": "Algorithm likely has baseline behavior for simple skills",
        "recommendation": "Investigate skill analysis that extracts modules/dependencies"
    }
    
    with open("matrix_implementation_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis saved: matrix_implementation_analysis.json")
    
    return True

def main():
    """主分析函数"""
    print("MATRIX ALGORITHM IMPLEMENTATION ANALYSIS")
    print("=" * 70)
    
    success = analyze_matrix_implementation()
    
    print(f"\n" + "=" * 70)
    print("IMPLEMENTATION ANALYSIS COMPLETE")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)