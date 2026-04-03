#!/usr/bin/env python3
"""
AST分析工具 v1.0
深度代码分析 - 检测无限循环、不可达代码、安全漏洞
"""

import ast
import re
from typing import List, Dict, Any, Tuple
import os

class ASTAnalyzer:
    """AST语法树分析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None
        self.issues = []
        
    def parse(self) -> bool:
        """解析Python文件为AST"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.tree = ast.parse(content)
            return True
        except SyntaxError as e:
            self.issues.append({
                'type': 'SYNTAX_ERROR',
                'message': f'语法错误: {e}',
                'line': e.lineno,
                'severity': 'HIGH'
            })
            return False
        except Exception as e:
            self.issues.append({
                'type': 'PARSE_ERROR',
                'message': f'解析错误: {e}',
                'line': 0,
                'severity': 'HIGH'
            })
            return False
    
    def detect_infinite_loops(self):
        """检测无限循环"""
        class InfiniteLoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.infinite_loops = []
                
            def visit_While(self, node):
                # 检查while True: 模式
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    self.infinite_loops.append({
                        'line': node.lineno,
                        'type': 'WHILE_TRUE',
                        'message': '检测到 while True: 可能无限循环'
                    })
                
                # 检查循环条件是否可能永远为真
                self.generic_visit(node)
                
            def visit_For(self, node):
                # 检查for循环中的break/return
                has_break_or_return = False
                
                class BreakReturnVisitor(ast.NodeVisitor):
                    def __init__(self):
                        self.found = False
                    
                    def visit_Break(self, node):
                        self.found = True
                    
                    def visit_Return(self, node):
                        self.found = True
                
                visitor = BreakReturnVisitor()
                visitor.visit(node)
                
                if not visitor.found:
                    # 检查是否遍历可迭代对象
                    if isinstance(node.iter, ast.Call):
                        func_name = self.get_function_name(node.iter.func)
                        if func_name in ['range', 'enumerate', 'zip', 'items', 'keys', 'values']:
                            # 这些通常有限，是安全的
                            pass
                        elif func_name in ['open', 'readlines']:
                            # 文件操作，通常有限
                            pass
                        else:
                            # 检查是否是已知的有限迭代
                            if isinstance(node.iter, ast.Attribute):
                                attr_name = node.iter.attr
                                if attr_name in ['items', 'keys', 'values']:
                                    # 字典方法，有限
                                    pass
                                else:
                                    self.infinite_loops.append({
                                        'line': node.lineno,
                                        'type': 'FOR_WITHOUT_EXIT',
                                        'message': 'for loop without break or return, may be infinite'
                                    })
                            else:
                                self.infinite_loops.append({
                                    'line': node.lineno,
                                    'type': 'FOR_WITHOUT_EXIT',
                                    'message': 'for loop without break or return, may be infinite'
                                })
                
                self.generic_visit(node)
            
            def get_function_name(self, node):
                """获取函数名"""
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return node.attr
                return ''
        
        visitor = InfiniteLoopVisitor()
        visitor.visit(self.tree)
        
        for loop in visitor.infinite_loops:
            self.issues.append({
                'type': 'INFINITE_LOOP',
                'message': loop['message'],
                'line': loop['line'],
                'severity': 'HIGH'
            })
    
    def detect_unreachable_code(self):
        """检测不可达代码"""
        class UnreachableCodeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.unreachable_code = []
                self.current_function = None
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = None
            
            def visit_Return(self, node):
                # 检查return语句后的代码
                parent = node.parent if hasattr(node, 'parent') else None
                if parent and isinstance(parent, ast.FunctionDef):
                    # 找到return后的语句
                    return_index = parent.body.index(node)
                    if return_index < len(parent.body) - 1:
                        for stmt in parent.body[return_index + 1:]:
                            self.unreachable_code.append({
                                'line': stmt.lineno,
                                'function': self.current_function,
                                'message': 'return语句后的不可达代码'
                            })
                
                self.generic_visit(node)
            
            def visit_If(self, node):
                # 检查if False: 或 if True:
                if isinstance(node.test, ast.Constant):
                    if node.test.value is False:
                        # if False: 分支不可达
                        for stmt in node.body:
                            self.unreachable_code.append({
                                'line': stmt.lineno,
                                'function': self.current_function,
                                'message': 'if False: 分支中的不可达代码'
                            })
                    elif node.test.value is True:
                        # if True: else分支不可达
                        for stmt in node.orelse:
                            self.unreachable_code.append({
                                'line': stmt.lineno,
                                'function': self.current_function,
                                'message': 'if True: else分支中的不可达代码'
                            })
                
                self.generic_visit(node)
        
        # 为所有节点添加parent引用
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        visitor = UnreachableCodeVisitor()
        visitor.visit(self.tree)
        
        for code in visitor.unreachable_code:
            self.issues.append({
                'type': 'UNREACHABLE_CODE',
                'message': f"{code['function']}: {code['message']}",
                'line': code['line'],
                'severity': 'MEDIUM'
            })
    
    def detect_security_vulnerabilities(self):
        """检测安全漏洞"""
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.vulnerabilities = []
                
            def visit_Call(self, node):
                # 检测危险函数调用
                func_name = self.get_function_name(node.func)
                
                dangerous_functions = {
                    'eval': '代码注入风险',
                    'exec': '代码执行风险',
                    'compile': '代码编译风险',
                    '__import__': '动态导入风险',
                    'input': '用户输入风险',
                    'open': '文件操作风险',
                    'os.system': '系统命令执行风险',
                    'subprocess.call': '子进程执行风险',
                    'pickle.loads': '反序列化风险',
                    'yaml.load': 'YAML解析风险',
                    'json.loads': 'JSON解析风险（如果来源不可信）'
                }
                
                for dangerous_func, risk in dangerous_functions.items():
                    if dangerous_func in func_name:
                        self.vulnerabilities.append({
                            'line': node.lineno,
                            'function': func_name,
                            'risk': risk
                        })
                
                self.generic_visit(node)
            
            def get_function_name(self, node):
                """获取完整的函数名"""
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self.get_function_name(node.value)}.{node.attr}"
                elif isinstance(node, ast.Call):
                    return self.get_function_name(node.func)
                return ''
        
        visitor = SecurityVisitor()
        visitor.visit(self.tree)
        
        for vuln in visitor.vulnerabilities:
            self.issues.append({
                'type': 'SECURITY_VULNERABILITY',
                'message': f"检测到危险函数调用: {vuln['function']} - {vuln['risk']}",
                'line': vuln['line'],
                'severity': 'HIGH'
            })
    
    def analyze_complexity(self):
        """分析代码复杂度"""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.functions = []
                self.current_function = None
                self.current_complexity = 0
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.current_complexity = 1  # 函数本身
                self.generic_visit(node)
                
                self.functions.append({
                    'name': self.current_function,
                    'complexity': self.current_complexity,
                    'line': node.lineno
                })
                
                self.current_function = None
                self.current_complexity = 0
            
            def visit_If(self, node):
                self.current_complexity += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                self.current_complexity += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                self.current_complexity += 1
                self.generic_visit(node)
            
            def visit_Try(self, node):
                self.current_complexity += 1
                self.generic_visit(node)
            
            def visit_ExceptHandler(self, node):
                self.current_complexity += 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(self.tree)
        
        # 评估复杂度
        for func in visitor.functions:
            if func['complexity'] > 10:
                self.issues.append({
                    'type': 'HIGH_COMPLEXITY',
                    'message': f"函数 {func['name']} 复杂度过高: {func['complexity']}",
                    'line': func['line'],
                    'severity': 'MEDIUM'
                })
            elif func['complexity'] > 20:
                self.issues.append({
                    'type': 'VERY_HIGH_COMPLEXITY',
                    'message': f"函数 {func['name']} 复杂度非常高: {func['complexity']}，建议重构",
                    'line': func['line'],
                    'severity': 'HIGH'
                })
    
    def analyze(self) -> List[Dict[str, Any]]:
        """执行完整分析"""
        if not self.parse():
            return self.issues
        
        self.detect_infinite_loops()
        self.detect_unreachable_code()
        self.detect_security_vulnerabilities()
        self.analyze_complexity()
        
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
            return "[PASS] Code quality good, no serious issues found"
        
        summary_parts = []
        if stats['high'] > 0:
            summary_parts.append(f"[HIGH] Found {stats['high']} high-risk issues")
        if stats['medium'] > 0:
            summary_parts.append(f"[MEDIUM] Found {stats['medium']} medium-risk issues")
        
        return " | ".join(summary_parts)


def analyze_file(file_path: str) -> Dict[str, Any]:
    """分析单个文件"""
    analyzer = ASTAnalyzer(file_path)
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
                        'summary': f"分析错误: {e}"
                    })
    
    return results


def print_report(report: Dict[str, Any], verbose: bool = False):
    """打印分析报告"""
    print("=" * 80)
    print("AST Deep Code Analysis Report")
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
                        print(f"    [{issue['severity']}] L{issue['line']}: {issue['message']}")
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
    
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print("AST Deep Code Analyzer v1.0")
        print("Usage: python ast_analyzer_v1.py <file_or_directory> [--verbose]")
        print("")
        print("Options:")
        print("  -h, --help     Show this help message")
        print("  -v, --verbose  Show detailed issue information")
        print("  --test         Run built-in tests")
        print("")
        print("Examples:")
        print("  python ast_analyzer_v1.py skill.py")
        print("  python ast_analyzer_v1.py . --verbose")
        print("  python ast_analyzer_v1.py --test")
        sys.exit(0)
    
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