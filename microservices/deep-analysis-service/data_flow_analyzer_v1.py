#!/usr/bin/env python3
"""
数据流分析工具 v1.0
分析代码中的数据流动，检测敏感数据泄露、输入验证问题、数据污染
"""

import ast
import re
from typing import List, Dict, Any, Set, Tuple
import os

class DataFlowAnalyzer:
    """数据流分析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None
        self.issues = []
        self.sensitive_patterns = [
            r'password', r'secret', r'key', r'token', r'credential',
            r'auth', r'private', r'sensitive', r'confidential',
            r'api[_-]?key', r'access[_-]?token', r'bearer',
            r'jwt', r'oauth', r'client[_-]?(id|secret)'
        ]
        
    def parse(self) -> bool:
        """解析Python文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.tree = ast.parse(content)
            return True
        except Exception as e:
            self.issues.append({
                'type': 'PARSE_ERROR',
                'message': f'Parse error: {e}',
                'line': 0,
                'severity': 'HIGH'
            })
            return False
    
    def detect_sensitive_data(self):
        """检测敏感数据"""
        class SensitiveDataVisitor(ast.NodeVisitor):
            def __init__(self, patterns):
                self.patterns = patterns
                self.sensitive_vars = set()
                self.sensitive_literals = []
                
            def visit_Assign(self, node):
                # 检查赋值语句中的敏感变量名
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        for pattern in self.patterns:
                            if re.search(pattern, var_name, re.IGNORECASE):
                                self.sensitive_vars.add(target.id)
                                break
                
                # 检查赋值值中的敏感数据
                if isinstance(node.value, ast.Constant):
                    if isinstance(node.value.value, str):
                        value = node.value.value.lower()
                        for pattern in self.patterns:
                            if re.search(pattern, value, re.IGNORECASE):
                                self.sensitive_literals.append({
                                    'line': node.lineno,
                                    'value': node.value.value[:50] + '...' if len(node.value.value) > 50 else node.value.value
                                })
                                break
                
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                # 检查函数参数中的敏感数据
                for arg in node.args.args:
                    arg_name = arg.arg.lower()
                    for pattern in self.patterns:
                        if re.search(pattern, arg_name, re.IGNORECASE):
                            self.sensitive_vars.add(arg.arg)
                            break
                
                self.generic_visit(node)
        
        visitor = SensitiveDataVisitor(self.sensitive_patterns)
        visitor.visit(self.tree)
        
        # 报告敏感变量
        if visitor.sensitive_vars:
            self.issues.append({
                'type': 'SENSITIVE_VARIABLE',
                'message': f'Found sensitive variable names: {", ".join(sorted(visitor.sensitive_vars))}',
                'line': 0,
                'severity': 'HIGH'
            })
        
        # 报告敏感字面量
        for literal in visitor.sensitive_literals:
            self.issues.append({
                'type': 'SENSITIVE_LITERAL',
                'message': f'Sensitive data in literal: {literal["value"]}',
                'line': literal['line'],
                'severity': 'HIGH'
            })
    
    def analyze_input_validation(self):
        """分析输入验证"""
        class InputValidationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.input_sources = []
                self.validation_points = []
                self.unvalidated_inputs = []
                
            def visit_Call(self, node):
                # 检测输入源
                func_name = self.get_function_name(node.func)
                input_sources = [
                    'input', 'getpass', 'argv', 'environ', 'getenv',
                    'stdin', 'read', 'load', 'parse', 'decode'
                ]
                
                for source in input_sources:
                    if source in func_name.lower():
                        self.input_sources.append({
                            'line': node.lineno,
                            'function': func_name,
                            'has_validation': False
                        })
                        break
                
                # 检测验证函数
                validation_functions = [
                    'validate', 'check', 'verify', 'sanitize',
                    'escape', 'encode', 'strip', 'replace',
                    'isdigit', 'isalpha', 'isalnum', 'match',
                    'search', 'fullmatch', 'compile'
                ]
                
                for validation in validation_functions:
                    if validation in func_name.lower():
                        self.validation_points.append({
                            'line': node.lineno,
                            'function': func_name
                        })
                        break
                
                self.generic_visit(node)
            
            def get_function_name(self, node):
                """获取函数名"""
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self.get_function_name(node.value)}.{node.attr}"
                elif isinstance(node, ast.Call):
                    return self.get_function_name(node.func)
                return ''
        
        visitor = InputValidationVisitor()
        visitor.visit(self.tree)
        
        # 分析未验证的输入
        for source in visitor.input_sources:
            # 简化的验证检查：检查输入源附近是否有验证
            # 实际需要更复杂的数据流分析
            if not source['has_validation']:
                self.issues.append({
                    'type': 'POTENTIAL_UNVALIDATED_INPUT',
                    'message': f'Input source {source["function"]} may not be properly validated',
                    'line': source['line'],
                    'severity': 'MEDIUM'
                })
    
    def detect_data_leakage(self):
        """检测数据泄露"""
        class DataLeakageVisitor(ast.NodeVisitor):
            def __init__(self):
                self.sensitive_assignments = []
                self.output_points = []
                self.potential_leaks = []
                
            def visit_Assign(self, node):
                # 检查敏感数据赋值
                if isinstance(node.value, ast.Constant):
                    value = str(node.value.value).lower()
                    sensitive_keywords = ['password', 'secret', 'key', 'token']
                    for keyword in sensitive_keywords:
                        if keyword in value:
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    self.sensitive_assignments.append({
                                        'line': node.lineno,
                                        'variable': target.id
                                    })
                
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # 检查输出点
                func_name = self.get_function_name(node.func)
                output_functions = [
                    'print', 'write', 'writelines', 'stdout',
                    'stderr', 'log', 'debug', 'info', 'warning',
                    'error', 'critical', 'send', 'post', 'put'
                ]
                
                for output_func in output_functions:
                    if output_func in func_name.lower():
                        self.output_points.append({
                            'line': node.lineno,
                            'function': func_name
                        })
                        break
                
                self.generic_visit(node)
            
            def get_function_name(self, node):
                """获取函数名"""
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self.get_function_name(node.value)}.{node.attr}"
                elif isinstance(node, ast.Call):
                    return self.get_function_name(node.func)
                return ''
        
        visitor = DataLeakageVisitor()
        visitor.visit(self.tree)
        
        # 简化的泄露检测：如果有敏感数据和输出点，标记潜在风险
        if visitor.sensitive_assignments and visitor.output_points:
            self.issues.append({
                'type': 'POTENTIAL_DATA_LEAKAGE',
                'message': f'Found {len(visitor.sensitive_assignments)} sensitive assignments and {len(visitor.output_points)} output points - potential data leakage risk',
                'line': 0,
                'severity': 'HIGH'
            })
    
    def analyze_exception_handling(self):
        """分析异常处理中的数据泄露"""
        class ExceptionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.exception_handlers = []
                self.sensitive_in_exceptions = []
                
            def visit_ExceptHandler(self, node):
                # 检查异常处理块
                handler_info = {
                    'line': node.lineno,
                    'has_sensitive_data': False
                }
                
                # 检查异常消息中是否包含敏感数据
                class SensitiveChecker(ast.NodeVisitor):
                    def __init__(self):
                        self.found_sensitive = False
                    
                    def visit_Constant(self, node):
                        if isinstance(node.value, str):
                            value = node.value.lower()
                            sensitive_keywords = ['password', 'secret', 'key', 'token', 'traceback']
                            for keyword in sensitive_keywords:
                                if keyword in value:
                                    self.found_sensitive = True
                
                checker = SensitiveChecker()
                checker.visit(node)
                
                if checker.found_sensitive:
                    self.sensitive_in_exceptions.append({
                        'line': node.lineno,
                        'message': 'Sensitive data may be exposed in exception messages'
                    })
                
                self.generic_visit(node)
        
        visitor = ExceptionVisitor()
        visitor.visit(self.tree)
        
        for exception in visitor.sensitive_in_exceptions:
            self.issues.append({
                'type': 'SENSITIVE_DATA_IN_EXCEPTION',
                'message': exception['message'],
                'line': exception['line'],
                'severity': 'MEDIUM'
            })
    
    def analyze(self) -> List[Dict[str, Any]]:
        """执行完整分析"""
        if not self.parse():
            return self.issues
        
        self.detect_sensitive_data()
        self.analyze_input_validation()
        self.detect_data_leakage()
        self.analyze_exception_handling()
        
        return self.issues
    
    def generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        issues = self.analyze()
        
        # 统计问题
        stats = {
            'total': len(issues),
            'high': len([i for i in issues if i['severity'] == 'HIGH']),
            'medium': len([i for i in issues if i['severity'] == 'MEDIUM']),
            'low': len([i for i in issues if i['severity'] == 'LOW']),
            'by_type': {}
        }
        
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in stats['by_type']:
                stats['by_type'][issue_type] = 0
            stats['by_type'][issue_type] += 1
        
        return {
            'file': self.file_path,
            'stats': stats,
            'issues': issues,
            'summary': self._generate_summary(stats)
        }
    
    def _generate_summary(self, stats: Dict) -> str:
        """生成摘要"""
        if stats['total'] == 0:
            return "[PASS] Data flow analysis passed, no serious issues found"
        
        summary_parts = []
        if stats['high'] > 0:
            summary_parts.append(f"[HIGH] Found {stats['high']} high-risk data flow issues")
        if stats['medium'] > 0:
            summary_parts.append(f"[MEDIUM] Found {stats['medium']} medium-risk data flow issues")
        
        return " | ".join(summary_parts)


def analyze_file(file_path: str) -> Dict[str, Any]:
    """分析单个文件"""
    analyzer = DataFlowAnalyzer(file_path)
    return analyzer.generate_report()


def analyze_directory(directory: str) -> Dict[str, Any]:
    """分析目录中的所有Python文件"""
    results = {
        'directory': directory,
        'files': [],
        'total_stats': {
            'total_files': 0,
            'total_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0
        }
    }
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    report = analyze_file(file_path)
                    results['files'].append(report)
                    
                    # 更新统计
                    results['total_stats']['total_files'] += 1
                    results['total_stats']['total_issues'] += report['stats']['total']
                    results['total_stats']['high_issues'] += report['stats']['high']
                    results['total_stats']['medium_issues'] += report['stats']['medium']
                    results['total_stats']['low_issues'] += report['stats']['low']
                    
                except Exception as e:
                    results['files'].append({
                        'file': file_path,
                        'error': str(e),
                        'stats': {'total': 0, 'high': 0, 'medium': 0, 'low': 0},
                        'issues': [],
                        'summary': f"Analysis error: {e}"
                    })
    
    return results


def print_report(report: Dict[str, Any], verbose: bool = False):
    """打印分析报告"""
    print("=" * 80)
    print("Data Flow Analysis Report")
    print("=" * 80)
    
    if 'directory' in report:
        print(f"Directory: {report['directory']}")
        print(f"Files analyzed: {report['total_stats']['total_files']}")
        print(f"Total issues: {report['total_stats']['total_issues']}")
        print(f"High-risk issues: {report['total_stats']['high_issues']}")
        print(f"Medium-risk issues: {report['total_stats']['medium_issues']}")
        print(f"Low-risk issues: {report['total_stats']['low_issues']}")
        print("-" * 80)
        
        for file_report in report['files']:
            if 'error' in file_report:
                print(f"[ERROR] {os.path.basename(file_report['file'])}: {file_report['error']}")
            elif file_report['stats']['total'] > 0:
                print(f"[ISSUES] {os.path.basename(file_report['file'])}: {file_report['summary']}")
                if verbose:
                    for issue in file_report['issues']:
                        print(f"    [{issue['severity']}] L{issue['line']}: {issue['type']} - {issue['message']}")
            else:
                print(f"[PASS] {os.path.basename(file_report['file'])}: Passed")
    else:
        # 单个文件报告
        print(f"File: {report['file']}")
        print(f"Total issues: {report['stats']['total']}")
        print(f"High-risk issues: {report['stats']['high']}")
        print(f"Medium-risk issues: {report['stats']['medium']}")
        print(f"Low-risk issues: {report['stats']['low']}")
        print("-" * 80)
        print(f"Summary: {report['summary']}")
        
        if verbose and report['issues']:
            print("\nDetailed issues:")
            for issue in report['issues']:
                print(f"  [{issue['severity']}] L{issue['line']}: {issue['type']} - {issue['message']}")
    
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_flow_analyzer_v1.py <file_or_directory> [--verbose]")
        sys.exit(1)
    
    target = sys.argv[1]
    verbose = '--verbose' in sys.argv
    
    if os.path.isfile(target):
        report = analyze_file(target)
    elif os.path.isdir(target):
        report = analyze_directory(target)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    print_report(report, verbose)
    
    # 如果有高危问题，返回非零退出码
    if 'total_stats' in report:
        if report['total_stats']['high_issues'] > 0:
            sys.exit(1)
    else:
        if report['stats']['high'] > 0:
            sys.exit(1)