#!/usr/bin/env python3
"""
性能分析工具 v1.0
分析代码性能问题：低效算法、内存泄漏、资源管理、时间复杂度
"""

import ast
import re
from typing import List, Dict, Any, Set
import os

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None
        self.issues = []
        
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
    
    def detect_inefficient_algorithms(self):
        """检测低效算法"""
        class InefficientAlgorithmVisitor(ast.NodeVisitor):
            def __init__(self):
                self.inefficient_patterns = []
                
            def visit_For(self, node):
                # 检测嵌套循环
                nested_level = self.get_nested_level(node)
                if nested_level >= 3:
                    self.inefficient_patterns.append({
                        'line': node.lineno,
                        'type': 'DEEPLY_NESTED_LOOPS',
                        'message': f'Deeply nested loops (level: {nested_level}) - O(n^{nested_level}) complexity'
                    })
                
                # 检查循环内的列表操作
                class ListOperationVisitor(ast.NodeVisitor):
                    def __init__(self):
                        self.has_list_ops = False
                    
                    def visit_Call(self, node):
                        func_name = self.get_function_name(node.func)
                        list_operations = ['append', 'insert', 'remove', 'pop', 'index', 'count']
                        for op in list_operations:
                            if op in func_name:
                                self.has_list_ops = True
                        
                        self.generic_visit(node)
                    
                    def get_function_name(self, node):
                        if isinstance(node, ast.Name):
                            return node.id
                        elif isinstance(node, ast.Attribute):
                            return node.attr
                        return ''
                
                list_visitor = ListOperationVisitor()
                list_visitor.visit(node)
                
                if list_visitor.has_list_ops:
                    self.inefficient_patterns.append({
                        'line': node.lineno,
                        'type': 'LIST_OPERATIONS_IN_LOOP',
                        'message': 'List operations inside loop - may be O(n²) complexity'
                    })
                
                self.generic_visit(node)
            
            def get_nested_level(self, node):
                """获取嵌套层级"""
                level = 0
                parent = node
                while hasattr(parent, 'parent'):
                    parent = parent.parent
                    if isinstance(parent, (ast.For, ast.While)):
                        level += 1
                return level
        
        # 为所有节点添加parent引用
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        visitor = InefficientAlgorithmVisitor()
        visitor.visit(self.tree)
        
        for pattern in visitor.inefficient_patterns:
            self.issues.append({
                'type': pattern['type'],
                'message': pattern['message'],
                'line': pattern['line'],
                'severity': 'MEDIUM'
            })
    
    def detect_memory_issues(self):
        """检测内存问题"""
        class MemoryIssueVisitor(ast.NodeVisitor):
            def __init__(self):
                self.memory_issues = []
                
            def visit_ListComp(self, node):
                # 列表推导式通常没问题，但检查是否过大
                pass
            
            def visit_DictComp(self, node):
                # 字典推导式通常没问题
                pass
            
            def visit_Call(self, node):
                # 检测可能的内存密集型操作
                func_name = self.get_function_name(node.func)
                
                memory_intensive = [
                    'read', 'readlines', 'load', 'dump', 'dumps',
                    'decode', 'encode', 'copy', 'deepcopy'
                ]
                
                for func in memory_intensive:
                    if func in func_name.lower():
                        self.memory_issues.append({
                            'line': node.lineno,
                            'function': func_name,
                            'message': f'Memory-intensive operation: {func_name}'
                        })
                        break
                
                self.generic_visit(node)
            
            def get_function_name(self, node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self.get_function_name(node.value)}.{node.attr}"
                elif isinstance(node, ast.Call):
                    return self.get_function_name(node.func)
                return ''
        
        visitor = MemoryIssueVisitor()
        visitor.visit(self.tree)
        
        for issue in visitor.memory_issues:
            self.issues.append({
                'type': 'MEMORY_INTENSIVE_OPERATION',
                'message': issue['message'],
                'line': issue['line'],
                'severity': 'MEDIUM'
            })
    
    def analyze_resource_management(self):
        """分析资源管理"""
        class ResourceVisitor(ast.NodeVisitor):
            def __init__(self):
                self.resource_issues = []
                self.open_calls = []
                self.close_calls = []
                
            def visit_With(self, node):
                # with语句通常正确管理资源
                pass
            
            def visit_Call(self, node):
                # 检测资源打开操作
                func_name = self.get_function_name(node.func)
                
                open_functions = ['open', 'connect', 'start', 'begin']
                close_functions = ['close', 'disconnect', 'stop', 'end']
                
                for open_func in open_functions:
                    if open_func in func_name.lower():
                        self.open_calls.append({
                            'line': node.lineno,
                            'function': func_name
                        })
                        break
                
                for close_func in close_functions:
                    if close_func in func_name.lower():
                        self.close_calls.append({
                            'line': node.lineno,
                            'function': func_name
                        })
                        break
                
                self.generic_visit(node)
            
            def get_function_name(self, node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self.get_function_name(node.value)}.{node.attr}"
                elif isinstance(node, ast.Call):
                    return self.get_function_name(node.func)
                return ''
        
        visitor = ResourceVisitor()
        visitor.visit(self.tree)
        
        # 简化的资源泄漏检测
        if len(visitor.open_calls) > len(visitor.close_calls):
            self.issues.append({
                'type': 'POTENTIAL_RESOURCE_LEAK',
                'message': f'More resource open calls ({len(visitor.open_calls)}) than close calls ({len(visitor.close_calls)})',
                'line': 0,
                'severity': 'MEDIUM'
            })
    
    def detect_time_complexity_issues(self):
        """检测时间复杂度问题"""
        class TimeComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity_issues = []
                
            def visit_For(self, node):
                # 检查循环内的操作
                loop_body = node.body
                
                # 检查是否有嵌套数据结构访问
                class NestedAccessVisitor(ast.NodeVisitor):
                    def __init__(self):
                        self.has_nested_access = False
                    
                    def visit_Subscript(self, node):
                        # 检查是否是多重下标访问
                        if isinstance(node.value, ast.Subscript):
                            self.has_nested_access = True
                        
                        self.generic_visit(node)
                
                access_visitor = NestedAccessVisitor()
                access_visitor.visit(node)
                
                if access_visitor.has_nested_access:
                    self.complexity_issues.append({
                        'line': node.lineno,
                        'type': 'NESTED_DATA_ACCESS',
                        'message': 'Nested data structure access inside loop - may be O(n²) or worse'
                    })
                
                self.generic_visit(node)
            
            def visit_While(self, node):
                # while循环可能更危险
                self.complexity_issues.append({
                    'line': node.lineno,
                    'type': 'WHILE_LOOP_COMPLEXITY',
                    'message': 'While loop - ensure termination condition and complexity'
                })
                
                self.generic_visit(node)
        
        visitor = TimeComplexityVisitor()
        visitor.visit(self.tree)
        
        for issue in visitor.complexity_issues:
            self.issues.append({
                'type': issue['type'],
                'message': issue['message'],
                'line': issue['line'],
                'severity': 'MEDIUM'
            })
    
    def analyze_recursion(self):
        """分析递归问题"""
        class RecursionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.recursive_calls = []
                
            def visit_FunctionDef(self, node):
                function_name = node.name
                
                class SelfCallVisitor(ast.NodeVisitor):
                    def __init__(self, func_name):
                        self.func_name = func_name
                        self.has_self_call = False
                    
                    def visit_Call(self, node):
                        if isinstance(node.func, ast.Name) and node.func.id == self.func_name:
                            self.has_self_call = True
                        
                        self.generic_visit(node)
                
                visitor = SelfCallVisitor(function_name)
                visitor.visit(node)
                
                if visitor.has_self_call:
                    self.recursive_calls.append({
                        'line': node.lineno,
                        'function': function_name,
                        'message': f'Recursive function: {function_name}'
                    })
                
                self.generic_visit(node)
        
        visitor = RecursionVisitor()
        visitor.visit(self.tree)
        
        for call in visitor.recursive_calls:
            self.issues.append({
                'type': 'RECURSIVE_FUNCTION',
                'message': call['message'],
                'line': call['line'],
                'severity': 'MEDIUM'
            })
    
    def analyze(self) -> List[Dict[str, Any]]:
        """执行完整分析"""
        if not self.parse():
            return self.issues
        
        self.detect_inefficient_algorithms()
        self.detect_memory_issues()
        self.analyze_resource_management()
        self.detect_time_complexity_issues()
        self.analyze_recursion()
        
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
            return "[PASS] Performance analysis passed, no serious issues found"
        
        summary_parts = []
        if stats['high'] > 0:
            summary_parts.append(f"[HIGH] Found {stats['high']} high-risk performance issues")
        if stats['medium'] > 0:
            summary_parts.append(f"[MEDIUM] Found {stats['medium']} medium-risk performance issues")
        
        return " | ".join(summary_parts)


def analyze_file(file_path: str) -> Dict[str, Any]:
    """分析单个文件"""
    analyzer = PerformanceAnalyzer(file_path)
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
    print("Performance Analysis Report")
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
        print("Usage: python performance_analyzer_v1.py <file_or_directory> [--verbose]")
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