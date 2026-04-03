#!/usr/bin/env python3
"""
运行工具测试
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_tool_test(tool_name, script_path, args):
    """运行工具测试"""
    print(f"\nTesting {tool_name}...")
    print(f"  Command: python {script_path} {args}")
    
    try:
        # 构建命令
        cmd = [sys.executable, script_path] + args.split()
        
        # 运行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 检查结果 - 对于分析工具，退出码1表示发现问题，不是失败
        if result.returncode in [0, 1]:  # 0=无问题，1=发现问题
            print(f"  [PASS] {tool_name} completed successfully (exit code: {result.returncode})")
            return True, result.stdout
        else:
            print(f"  [FAIL] {tool_name} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}...")
            return False, result.stdout
            
    except Exception as e:
        print(f"  [ERROR] {tool_name} execution error: {e}")
        return False, str(e)

def main():
    """主函数"""
    print("=== Running Deep Analysis Tool Tests ===")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print()
    
    test_dir = "./test_data"
    if not os.path.exists(test_dir):
        print("Test directory not found. Run create_test_files.py first.")
        return 1
    
    # 获取测试文件路径
    problematic_file = os.path.join(test_dir, "test_problematic.py")
    clean_file = os.path.join(test_dir, "test_clean.py")
    requirements_file = os.path.join(test_dir, "requirements.txt")
    
    if not os.path.exists(problematic_file):
        print(f"Test file not found: {problematic_file}")
        return 1
    
    test_results = {}
    
    # 1. 测试AST分析工具
    passed, output = run_tool_test(
        "AST Analyzer",
        "ast_analyzer_v1.py",
        f'"{problematic_file}" --verbose'
    )
    test_results['ast'] = passed
    
    # 2. 测试第三方库分析工具
    passed, output = run_tool_test(
        "Third-Party Analyzer",
        "third_party_analyzer_v1.py",
        f'"{problematic_file}" "{requirements_file}" --verbose'
    )
    test_results['third_party'] = passed
    
    # 3. 测试数据流分析工具
    passed, output = run_tool_test(
        "Data Flow Analyzer",
        "data_flow_analyzer_v1.py",
        f'"{problematic_file}" --verbose'
    )
    test_results['data_flow'] = passed
    
    # 4. 测试性能分析工具
    passed, output = run_tool_test(
        "Performance Analyzer",
        "performance_analyzer_v1.py",
        f'"{problematic_file}" --verbose'
    )
    test_results['performance'] = passed
    
    # 5. 测试控制流分析工具
    try:
        import networkx
        passed, output = run_tool_test(
            "Control Flow Analyzer",
            "control_flow_analyzer_v1.py",
            f'"{problematic_file}" --verbose'
        )
        test_results['control_flow'] = passed
    except ImportError:
        print("\n[SKIP] Control Flow Analyzer requires networkx")
        test_results['control_flow'] = None
    
    # 6. 测试综合套件
    passed, output = run_tool_test(
        "Deep Analysis Suite",
        "deep_analysis_suite.py",
        f'"{problematic_file}" -r "{requirements_file}"'
    )
    test_results['suite'] = passed
    
    # 7. 测试干净文件
    passed, output = run_tool_test(
        "Clean File Test",
        "ast_analyzer_v1.py",
        f'"{clean_file}"'
    )
    test_results['clean'] = passed
    
    # 生成测试报告
    print("\n" + "="*60)
    print("TEST REPORT")
    print("="*60)
    
    passed_count = sum(1 for r in test_results.values() if r is True)
    failed_count = sum(1 for r in test_results.values() if r is False)
    skipped_count = sum(1 for r in test_results.values() if r is None)
    total_count = len(test_results)
    
    print(f"Total Tests: {total_count}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Skipped: {skipped_count}")
    
    print("\nDetailed Results:")
    for tool, result in test_results.items():
        if result is True:
            status = "PASS"
        elif result is False:
            status = "FAIL"
        else:
            status = "SKIP"
        
        print(f"  {tool:20} : {status}")
    
    print("="*60)
    
    # 清理
    print("\nCleaning up test files...")
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
        print("  [OK] Removed test directory")
    
    print("\n=== Test Complete ===")
    
    # 返回退出码
    if failed_count == 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())