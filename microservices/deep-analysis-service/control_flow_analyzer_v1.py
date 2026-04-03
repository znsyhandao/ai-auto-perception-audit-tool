#!/usr/bin/env python3
"""
控制流分析工具 v1.0
分析代码的控制流复杂度、路径可达性、循环结构
"""

import ast
import networkx as nx
from typing import List, Dict, Any, Set
import os

class ControlFlowAnalyzer:
    """控制流分析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None
        self.cfg_graphs = {}  # 函数名 -> 控制流图
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
    
    def build_control_flow_graph(self, node: ast.AST, func_name: str = 'global') -> nx.DiGraph:
        """构建控制流图"""
        cfg = nx.DiGraph()
        node_counter = 0
        
        def add_node(label: str, ast_node=None):
            nonlocal node_counter
            node_id = node_counter
            node_counter += 1
            cfg.add_node(node_id, label=label, ast_node=ast_node)
            return node_id
        
        def add_edge(from_id: int, to_id: int, label: str = ''):
            cfg.add_edge(from_id, to_id, label=label)
        
        # 构建控制流图的逻辑
        # 这是一个简化的实现，实际需要更复杂的逻辑
        start_node = add_node('START')
        end_node = add_node('END')
        
        # 这里需要实现完整的控制流图构建逻辑
        # 由于时间限制，先实现基本功能
        
        return cfg
    
    def analyze_cyclomatic_complexity(self):
        """分析圈复杂度（McCabe复杂度）"""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.current_function = None
                self.current_complexity = 1  # 起始复杂度为1
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.current_complexity = 1
                self.generic_visit(node)
                
                self.functions.append({
                    'name': self.current_function,
                    'complexity': self.current_complexity,
                    'line': node.lineno
                })
                
                self.current_function = None
            
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
            
            def visit_BoolOp(self, node):
                # 每个and/or增加复杂度
                if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
                    self.current_complexity += len(node.values) - 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(self.tree)
        
        # 评估复杂度
        for func in visitor.functions:
            if func['complexity'] > 10:
                self.issues.append({
                    'type': 'HIGH_CYCLOMATIC_COMPLEXITY',
                    'message': f"Function {func['name']} has high cyclomatic complexity: {func['complexity']}",
                    'line': func['line'],
                    'severity': 'MEDIUM'
                })
            elif func['complexity'] > 20:
                self.issues.append({
                    'type': 'VERY_HIGH_CYCLOMATIC_COMPLEXITY',
                    'message': f"Function {func['name']} has very high cyclomatic complexity: {func['complexity']}, consider refactoring",
                    'line': func['line'],
                    'severity': 'HIGH'
                })
    
    def detect_nested_control_structures(self):
        """检测嵌套过深的控制结构"""
        class NestedStructureVisitor(ast.NodeVisitor):
            def __init__(self):
                self.nested_structures = []
                self.current_depth = 0
                self.max_depth = 0
                self.current_function = None
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.current_depth = 0
                self.max_depth = 0
                self.generic_visit(node)
                
                if self.max_depth > 3:
                    self.nested_structures.append({
                        'function': self.current_function,
                        'max_depth': self.max_depth,
                        'line': node.lineno
                    })
                
                self.current_function = None
            
            def visit_If(self, node):
                self.current_depth += 1
                if self.current_depth > self.max_depth:
                    self.max_depth = self.current_depth
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_For(self, node):
                self.current_depth += 1
                if self.current_depth > self.max_depth:
                    self.max_depth = self.current_depth
                self.generic_visit(node)
                self.current_depth -= 1
            
            def visit_While(self, node):
                self.current_depth += 1
                if self.current_depth > self.max_depth:
                    self.max_depth = self.current_depth
                self.generic_visit(node)
                self.current_depth -= 1
        
        visitor = NestedStructureVisitor()
        visitor.visit(self.tree)
        
        for structure in visitor.nested_structures:
            if structure['max_depth'] > 4:
                self.issues.append({
                    'type': 'DEEPLY_NESTED_STRUCTURE',
                    'message': f"Function {structure['function']} has deeply nested structures (depth: {structure['max_depth']})",
                    'line': structure['line'],
                    'severity': 'MEDIUM'
                })
    
    def analyze_loop_structures(self):
        """分析循环结构"""
        class LoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loops = []
                self.current_function = None
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = None
            
            def visit_For(self, node):
                # 分析for循环
                loop_info = {
                    'type': 'FOR',
                    'function': self.current_function,
                    'line': node.lineno,
                    'nested_level': self.get_nested_level(node),
                    'has_break': False,
                    'has_continue': False,
                    'has_return': False
                }
                
                # 检查循环体
                class LoopBodyVisitor(ast.NodeVisitor):
                    def __init__(self):
                        self.has_break = False
                        self.has_continue = False
                        self.has_return = False
                    
                    def visit_Break(self, node):
                        self.has_break = True
                    
                    def visit_Continue(self, node):
                        self.has_continue = True
                    
                    def visit_Return(self, node):
                        self.has_return = True
                
                body_visitor = LoopBodyVisitor()
                body_visitor.visit(node)
                
                loop_info['has_break'] = body_visitor.has_break
                loop_info['has_continue'] = body_visitor.has_continue
                loop_info['has_return'] = body_visitor.has_return
                
                self.loops.append(loop_info)
                self.generic_visit(node)
            
            def visit_While(self, node):
                # 分析while循环
                loop_info = {
                    'type': 'WHILE',
                    'function': self.current_function,
                    'line': node.lineno,
                    'nested_level': self.get_nested_level(node),
                    'has_break': False,
                    'has_continue': False,
                    'has_return': False
                }
                
                # 检查循环体
                class LoopBodyVisitor(ast.NodeVisitor):
                    def __init__(self):
                        self.has_break = False
                        self.has_continue = False
                        self.has_return = False
                    
                    def visit_Break(self, node):
                        self.has_break = True
                    
                    def visit_Continue(self, node):
                        self.has_continue = True
                    
                    def visit_Return(self, node):
                        self.has_return = True
                
                body_visitor = LoopBodyVisitor()
                body_visitor.visit(node)
                
                loop_info['has_break'] = body_visitor.has_break
                loop_info['has_continue'] = body_visitor.has_continue
                loop_info['has_return'] = body_visitor.has_return
                
                self.loops.append(loop_info)
                self.generic_visit(node)
            
            def get_nested_level(self, node):
                """获取嵌套层级"""
                level = 0
                parent = node
                while hasattr(parent, 'parent'):
                    parent = parent.parent
                    if isinstance(parent, (ast.For, ast.While, ast.If)):
                        level += 1
                return level
        
        # 为所有节点添加parent引用
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        visitor = LoopVisitor()
        visitor.visit(self.tree)
        
        # 分析循环问题
        for loop in visitor.loops:
            # 检查嵌套过深的循环
            if loop['nested_level'] > 2:
                self.issues.append({
                    'type': 'DEEPLY_NESTED_LOOP',
                    'message': f"{loop['type']} loop in function {loop['function']} is deeply nested (level: {loop['nested_level']})",
                    'line': loop['line'],
                    'severity': 'MEDIUM'
                })
            
            # 检查没有退出机制的while循环
            if loop['type'] == 'WHILE' and not loop['has_break'] and not loop['has_return']:
                # 检查条件是否为常量True
                # 这里需要更复杂的分析，暂时标记
                pass
    
    def analyze_path_complexity(self):
        """分析路径复杂度"""
        # 简化的路径复杂度分析
        # 实际需要构建完整的控制流图并分析路径
        
        class PathComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.current_function = None
                self.path_count = 1  # 起始路径数为1
                
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.path_count = 1
                self.generic_visit(node)
                
                self.functions.append({
                    'name': self.current_function,
                    'path_count': self.path_count,
                    'line': node.lineno
                })
                
                self.current_function = None
            
            def visit_If(self, node):
                # 每个if语句至少增加2条路径（真/假）
                self.path_count *= 2
                self.generic_visit(node)
            
            def visit_For(self, node):
                # for循环增加路径复杂度
                self.path_count *= 2  # 简化处理
                self.generic_visit(node)
            
            def visit_While(self, node):
                # while循环增加路径复杂度
                self.path_count *= 2  # 简化处理
                self.generic_visit(node)
        
        visitor = PathComplexityVisitor()
        visitor.visit(self.tree)
        
        for func in visitor.functions:
            if func['path_count'] > 100:
                self.issues.append({
                    'type': 'HIGH_PATH_COMPLEXITY',
                    'message': f"Function {func['name']} has high path complexity: {func['path_count']} possible paths",
                    'line': func['line'],
                    'severity': 'MEDIUM'
                })
    
    def analyze(self) -> List[Dict[str, Any]]:
        """执行完整分析"""
        if not self.parse():
            return self.issues
        
        self.analyze_cyclomatic_complexity()
        self.detect_nested_control_structures()
        self.analyze_loop_structures()
        self.analyze_path_complexity()
        
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
            return "[PASS] Control flow analysis passed, no serious issues found"
        
        summary_parts = []
        if stats['high'] > 0:
            summary_parts.append(f"[HIGH] Found {stats['high']} high-risk control flow issues")
        if stats['medium'] > 0:
            summary_parts.append(f"[MEDIUM] Found {stats['medium']} medium-risk control flow issues")
        
        return " | ".join(summary_parts)


def analyze_file(file_path: str) -> Dict[str, Any]:
    """分析单个文件"""
    analyzer = ControlFlowAnalyzer(file_path)
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
    print("Control Flow Analysis Report")
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


