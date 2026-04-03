#!/usr/bin/env python3
"""
改进的测试套件
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

class ImprovedTestSuite:
    """改进的测试套件"""
    
    def __init__(self):
        self.test_results = {}
        self.test_cases = []
        self.setup_test_cases()
    
    def setup_test_cases(self):
        """设置测试用例"""
        # 基础功能测试
        self.test_cases.extend([
            {
                'name': 'AST Analyzer - Basic',
                'tool': 'ast_analyzer_v1.py',
                'args': ['--help'],
                'expected_exit_code': 0,
                'description': 'Test help command'
            },
            {
                'name': 'AST Analyzer - File Analysis',
                'tool': 'ast_analyzer_v1.py',
                'args': ['./test_suite_data/simple.py'],
                'expected_exit_code': 0,
                'description': 'Test simple file analysis'
            },
            {
                'name': 'Third-Party Analyzer - Basic',
                'tool': 'third_party_analyzer_v1.py',
                'args': ['./test_suite_data/simple.py', './test_suite_data/requirements.txt'],
                'expected_exit_code': 0,
                'description': 'Test third-party library analysis'
            },
            {
                'name': 'Data Flow Analyzer - Basic',
                'tool': 'data_flow_analyzer_v1.py',
                'args': ['./test_suite_data/simple.py'],
                'expected_exit_code': 0,
                'description': 'Test data flow analysis'
            },
            {
                'name': 'Performance Analyzer - Basic',
                'tool': 'performance_analyzer_v1.py',
                'args': ['./test_suite_data/simple.py'],
                'expected_exit_code': 0,
                'description': 'Test performance analysis'
            },
            {
                'name': 'Deep Analysis Suite - Basic',
                'tool': 'deep_analysis_suite.py',
                'args': ['--help'],
                'expected_exit_code': 0,
                'description': 'Test help command'
            }
        ])
    
    def run_test_case(self, test_case: Dict) -> Tuple[bool, str]:
        """运行单个测试用例"""
        tool = test_case['tool']
        args = test_case['args']
        expected_exit_code = test_case['expected_exit_code']
        
        print(f"Running: {test_case['name']}")
        print(f"  Description: {test_case['description']}")
        print(f"  Command: python {tool} {' '.join(args)}")
        
        try:
            cmd = [sys.executable, tool] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            
            if result.returncode == expected_exit_code:
                print(f"  [PASS] Exit code: {result.returncode} (expected: {expected_exit_code})")
                return True, result.stdout
            else:
                print(f"  [FAIL] Exit code: {result.returncode} (expected: {expected_exit_code})")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}...")
                return False, result.stdout
                
        except subprocess.TimeoutExpired:
            print(f"  [FAIL] Timeout after 30 seconds")
            return False, "Timeout"
        except Exception as e:
            print(f"  [ERROR] Execution error: {e}")
            return False, str(e)
    
    def create_test_files(self) -> Dict[str, str]:
        """创建测试文件"""
        test_dir = "./test_suite_data"
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        
        # 创建各种测试文件
        test_files = {}
        
        # 1. 简单文件
        simple_code = '''# simple.py
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
'''
        simple_file = os.path.join(test_dir, "simple.py")
        with open(simple_file, 'w', encoding='utf-8') as f:
            f.write(simple_code)
        test_files['simple'] = simple_file
        
        # 2. 复杂文件
        complex_code = '''# complex.py
import os
import sys
import json
from typing import List, Dict

class ComplexClass:
    def __init__(self, data: List[int]):
        self.data = data
        self.cache = {}
    
    def process(self) -> Dict[str, float]:
        """处理数据"""
        if not self.data:
            return {}
        
        # 计算统计信息
        total = sum(self.data)
        mean = total / len(self.data)
        variance = sum((x - mean) ** 2 for x in self.data) / len(self.data)
        
        return {
            "total": total,
            "mean": mean,
            "variance": variance,
            "count": len(self.data)
        }
    
    def save(self, filename: str):
        """保存结果"""
        result = self.process()
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)

def main():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    processor = ComplexClass(data)
    result = processor.process()
    print(f"Result: {result}")
    processor.save("output.json")

if __name__ == "__main__":
    main()
'''
        complex_file = os.path.join(test_dir, "complex.py")
        with open(complex_file, 'w', encoding='utf-8') as f:
            f.write(complex_code)
        test_files['complex'] = complex_file
        
        # 3. 有问题的文件
        problematic_code = '''# problematic.py
import pickle
import marshal

def dangerous():
    # 危险操作
    eval("print('dangerous')")
    exec("x = 1")
    
def infinite():
    while True:
        pass

def leak():
    f = open("temp.txt", "w")
    f.write("test")
    # 忘记关闭

def sensitive():
    password = "secret123"
    api_key = "sk_live_123456"
    return password + api_key

def inefficient():
    result = []
    for i in range(1000):
        for j in range(1000):
            result.append(i * j)
    return result
'''
        problematic_file = os.path.join(test_dir, "problematic.py")
        with open(problematic_file, 'w', encoding='utf-8') as f:
            f.write(problematic_code)
        test_files['problematic'] = problematic_file
        
        # 4. requirements.txt
        requirements = '''# requirements.txt
requests==2.28.0
numpy==1.24.0
pandas==1.5.0
scikit-learn==1.2.0
'''
        req_file = os.path.join(test_dir, "requirements.txt")
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        test_files['requirements'] = req_file
        
        print(f"Created test files in: {test_dir}")
        return test_files
    
    def run_functional_tests(self, test_files: Dict[str, str]):
        """运行功能测试"""
        print("\n" + "="*60)
        print("Functional Tests")
        print("="*60)
        
        functional_tests = [
            {
                'name': 'AST Analyzer - Simple File',
                'tool': 'ast_analyzer_v1.py',
                'args': [test_files['simple']],
                'expected_exit_code': 0,
                'description': '分析简单文件'
            },
            {
                'name': 'AST Analyzer - Problematic File',
                'tool': 'ast_analyzer_v1.py',
                'args': [test_files['problematic'], '--verbose'],
                'expected_exit_code': 1,
                'description': '分析有问题文件'
            },
            {
                'name': 'Third-Party Analyzer - With Requirements',
                'tool': 'third_party_analyzer_v1.py',
                'args': [test_files['complex'], test_files['requirements'], '--verbose'],
                'expected_exit_code': 1,  # 分析工具返回1表示发现问题，不是错误
                'description': 'Analyze dependencies'
            },
            {
                'name': 'Data Flow Analyzer - Complex File',
                'tool': 'data_flow_analyzer_v1.py',
                'args': [test_files['complex'], '--verbose'],
                'expected_exit_code': 0,
                'description': 'Analyze data flow'
            },
            {
                'name': 'Performance Analyzer - Problematic File',
                'tool': 'performance_analyzer_v1.py',
                'args': [test_files['problematic'], '--verbose'],
                'expected_exit_code': 1,
                'description': 'Analyze performance issues'
            },
            {
                'name': 'Deep Analysis Suite - All Files',
                'tool': 'deep_analysis_suite.py',
                'args': [test_files['complex'], '-r', test_files['requirements']],
                'expected_exit_code': 1,  # 分析工具返回1表示发现问题，不是错误
                'description': 'Comprehensive deep analysis'
            }
        ]
        
        for test in functional_tests:
            passed, output = self.run_test_case(test)
            self.test_results[test['name']] = passed
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("\n" + "="*60)
        print("Performance Tests")
        print("="*60)
        
        # 测试大文件分析性能
        large_file = self.create_large_test_file()
        
        performance_tests = [
            {
                'name': 'AST Analyzer - Performance',
                'tool': 'ast_analyzer_v1.py',
                'args': [large_file],
                'expected_exit_code': 0,
                'description': '大文件分析性能'
            }
        ]
        
        for test in performance_tests:
            import time
            start_time = time.time()
            passed, output = self.run_test_case(test)
            elapsed = time.time() - start_time
            
            print(f"  Time: {elapsed:.2f} seconds")
            self.test_results[test['name']] = passed and elapsed < 5.0  # 5秒内完成
        
        # 清理
        if os.path.exists(large_file):
            os.remove(large_file)
    
    def create_large_test_file(self) -> str:
        """创建大测试文件"""
        test_dir = "./test_suite_data"
        large_file = os.path.join(test_dir, "large.py")
        
        with open(large_file, 'w', encoding='utf-8') as f:
            f.write("# Large test file\n")
            f.write("import os\nimport sys\n\n")
            
            # 添加大量函数
            for i in range(100):
                f.write(f"def function_{i}():\n")
                f.write(f'    """Function {i}"""\n')
                f.write(f"    return {i} * {i}\n\n")
            
            # 添加大量类
            for i in range(20):
                f.write(f"class Class{i}:\n")
                f.write(f'    """Class {i}"""\n\n')
                f.write(f"    def __init__(self):\n")
                f.write(f"        self.value = {i}\n\n")
                for j in range(5):
                    f.write(f"    def method_{j}(self):\n")
                    f.write(f"        return self.value + {j}\n\n")
        
        print(f"Created large test file: {large_file} ({os.path.getsize(large_file)} bytes)")
        return large_file
    
    def run_error_handling_tests(self):
        """运行错误处理测试"""
        print("\n" + "="*60)
        print("Error Handling Tests")
        print("="*60)
        
        error_tests = [
            {
                'name': 'AST Analyzer - Invalid File',
                'tool': 'ast_analyzer_v1.py',
                'args': ['non_existent_file.py'],
                'expected_exit_code': 1,
                'description': '处理不存在的文件'
            },
            {
                'name': 'AST Analyzer - Invalid Syntax',
                'tool': 'ast_analyzer_v1.py',
                'args': ['--test-invalid'],
                'expected_exit_code': 1,
                'description': '处理无效语法'
            }
        ]
        
        for test in error_tests:
            passed, output = self.run_test_case(test)
            self.test_results[test['name']] = passed
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("Test Report")
        print("="*60)
        
        passed = sum(1 for r in self.test_results.values() if r)
        failed = sum(1 for r in self.test_results.values() if not r)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "PASS" if result else "FAIL"
            # Windows控制台兼容性：不使用ANSI转义码
            print(f"  {test_name:40} : {status}")
        
        # 保存报告
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': passed/total*100,
            'results': self.test_results
        }
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nReport saved to: {report_file}")
        
        return passed == total
    
    def cleanup(self):
        """清理测试文件"""
        test_dir = "./test_suite_data"
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=== Improved Test Suite ===")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python: {sys.version}")
        print()
        
        try:
            # 创建测试文件
            test_files = self.create_test_files()
            
            # 运行基础测试
            print("\n" + "="*60)
            print("Basic Tests")
            print("="*60)
            
            for test_case in self.test_cases:
                passed, output = self.run_test_case(test_case)
                self.test_results[test_case['name']] = passed
            
            # 运行功能测试
            self.run_functional_tests(test_files)
            
            # 运行性能测试
            self.run_performance_tests()
            
            # 运行错误处理测试
            self.run_error_handling_tests()
            
            # 生成报告
            all_passed = self.generate_report()
            
            # 清理
            self.cleanup()
            
            print("\n" + "="*60)
            print("Test Suite Complete")
            print("="*60)
            
            return all_passed
            
        except Exception as e:
            print(f"\n[ERROR] Test suite failed: {e}")
            self.cleanup()
            return False

def main():
    """主函数"""
    test_suite = ImprovedTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())