#!/usr/bin/env python3
"""
第三方库分析工具 v1.0
分析导入的第三方库的安全性、许可证兼容性、版本漏洞
"""

import ast
import re
from typing import List, Dict, Any, Set
import os
import json

class ThirdPartyAnalyzer:
    """第三方库分析器"""
    
    def __init__(self, file_path: str, requirements_file: str = None):
        self.file_path = file_path
        self.requirements_file = requirements_file
        self.imports = set()
        self.issues = []
        
    def parse_imports(self):
        """解析Python文件中的导入语句"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            
            class ImportVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.imports = set()
                
                def visit_Import(self, node):
                    for alias in node.names:
                        self.imports.add(alias.name.split('.')[0])  # 只取顶级包名
                
                def visit_ImportFrom(self, node):
                    if node.module:
                        self.imports.add(node.module.split('.')[0])  # 只取顶级包名
            
            visitor = ImportVisitor()
            visitor.visit(tree)
            self.imports = visitor.imports
            
        except Exception as e:
            self.issues.append({
                'type': 'PARSE_ERROR',
                'message': f'Failed to parse imports: {e}',
                'line': 0,
                'severity': 'HIGH'
            })
    
    def parse_requirements(self) -> Set[str]:
        """解析requirements.txt文件"""
        requirements = set()
        
        if not self.requirements_file or not os.path.exists(self.requirements_file):
            return requirements
        
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取包名（移除版本约束）
                        match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                        if match:
                            requirements.add(match.group(1).lower())
        except Exception as e:
            self.issues.append({
                'type': 'REQUIREMENTS_PARSE_ERROR',
                'message': f'Failed to parse requirements.txt: {e}',
                'line': 0,
                'severity': 'MEDIUM'
            })
        
        return requirements
    
    def check_stdlib_only(self):
        """检查是否只使用标准库"""
        # Python标准库列表（部分）
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'datetime', 'time', 'math', 'random',
            'collections', 'itertools', 'functools', 'typing', 'pathlib',
            'hashlib', 'base64', 'csv', 'html', 'xml', 'ssl', 'socket',
            'subprocess', 'multiprocessing', 'threading', 'queue',
            'logging', 'unittest', 'doctest', 'pdb', 'traceback',
            'decimal', 'fractions', 'statistics', 'array', 'bisect',
            'heapq', 'weakref', 'copy', 'pprint', 'reprlib', 'enum',
            'graphlib', 'zoneinfo', 'dataclasses', 'contextlib',
            'abc', 'atexit', 'inspect', 'site', 'sysconfig'
        }
        
        non_stdlib = []
        for imp in self.imports:
            if imp not in stdlib_modules and not imp.startswith('_'):
                non_stdlib.append(imp)
        
        if non_stdlib:
            self.issues.append({
                'type': 'NON_STDLIB_IMPORTS',
                'message': f'Found non-standard library imports: {", ".join(non_stdlib)}',
                'line': 0,
                'severity': 'MEDIUM'
            })
    
    def check_dangerous_imports(self):
        """检查危险导入"""
        dangerous_modules = {
            'pickle': 'Unsafe deserialization risk',
            'marshal': 'Unsafe deserialization risk',
            'shelve': 'Uses pickle internally',
            'xmlrpc': 'XML-RPC security issues',
            'cgi': 'CGI security issues',
            'cgitb': 'CGI debugging may leak info',
            'webbrowser': 'May open external browsers',
            'winreg': 'Windows registry access',
            '_winreg': 'Windows registry access',
            'msvcrt': 'Microsoft C runtime',
            'ctypes': 'Low-level C access',
            'cffi': 'Foreign function interface',
            'subprocess': 'Process execution',
            'os': 'System operations (check usage)',
            'sys': 'System operations (check usage)'
        }
        
        for imp in self.imports:
            if imp in dangerous_modules:
                self.issues.append({
                    'type': 'DANGEROUS_IMPORT',
                    'message': f'Dangerous import: {imp} - {dangerous_modules[imp]}',
                    'line': 0,
                    'severity': 'HIGH'
                })
    
    def check_import_consistency(self):
        """检查导入一致性"""
        if self.requirements_file and os.path.exists(self.requirements_file):
            requirements = self.parse_requirements()
            
            # 检查代码中导入但requirements.txt中没有的
            missing_in_requirements = []
            for imp in self.imports:
                if imp.lower() not in requirements:
                    # 检查是否是标准库
                    if not self._is_stdlib_module(imp):
                        missing_in_requirements.append(imp)
            
            if missing_in_requirements:
                self.issues.append({
                    'type': 'MISSING_IN_REQUIREMENTS',
                    'message': f'Imports missing in requirements.txt: {", ".join(missing_in_requirements)}',
                    'line': 0,
                    'severity': 'MEDIUM'
                })
            
            # 检查requirements.txt中有但代码中没有导入的
            unused_requirements = []
            for req in requirements:
                if req not in [imp.lower() for imp in self.imports]:
                    unused_requirements.append(req)
            
            if unused_requirements:
                self.issues.append({
                    'type': 'UNUSED_REQUIREMENT',
                    'message': f'Requirements not used in code: {", ".join(unused_requirements)}',
                    'line': 0,
                    'severity': 'LOW'
                })
    
    def _is_stdlib_module(self, module_name: str) -> bool:
        """检查是否是标准库模块"""
        # 简化的检查，实际需要更完整的标准库列表
        stdlib_prefixes = [
            'os', 'sys', 're', 'json', 'datetime', 'time', 'math',
            'collections', 'itertools', 'functools', 'typing'
        ]
        
        for prefix in stdlib_prefixes:
            if module_name.startswith(prefix):
                return True
        
        return False
    
    def check_license_compatibility(self):
        """检查许可证兼容性（简化版）"""
        # 常见的许可证兼容性检查
        # 这里只是示例，实际需要更复杂的检查
        
        gpl_libraries = [
            'gnu', 'gpl', 'affero', 'agpl'
        ]
        
        for imp in self.imports:
            imp_lower = imp.lower()
            for gpl_keyword in gpl_libraries:
                if gpl_keyword in imp_lower:
                    self.issues.append({
                        'type': 'POTENTIAL_GPL_LICENSE',
                        'message': f'Potential GPL-licensed library: {imp} - may have license compatibility issues',
                        'line': 0,
                        'severity': 'MEDIUM'
                    })
    
    def check_version_vulnerabilities(self):
        """检查版本漏洞（简化版）"""
        # 这里只是示例，实际需要查询漏洞数据库
        
        known_vulnerable_versions = {
            'requests': '某些旧版本有漏洞',
            'urllib3': '某些版本有漏洞',
            'pyyaml': 'YAML解析漏洞',
            'jinja2': '模板注入漏洞',
            'django': 'Web框架漏洞',
            'flask': 'Web框架漏洞',
            'tornado': 'Web框架漏洞'
        }
        
        for imp in self.imports:
            if imp in known_vulnerable_versions:
                self.issues.append({
                    'type': 'POTENTIAL_VULNERABILITY',
                    'message': f'Library {imp} has known vulnerabilities: {known_vulnerable_versions[imp]}',
                    'line': 0,
                    'severity': 'HIGH'
                })
    
    def analyze(self) -> List[Dict[str, Any]]:
        """执行完整分析"""
        self.parse_imports()
        
        if not self.imports:
            self.issues.append({
                'type': 'NO_IMPORTS',
                'message': 'No imports found in the file',
                'line': 0,
                'severity': 'LOW'
            })
            return self.issues
        
        self.check_stdlib_only()
        self.check_dangerous_imports()
        self.check_import_consistency()
        self.check_license_compatibility()
        self.check_version_vulnerabilities()
        
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
            'imports': list(self.imports),
            'stats': stats,
            'issues': issues,
            'summary': self._generate_summary(stats)
        }
    
    def _generate_summary(self, stats: Dict) -> str:
        """生成摘要"""
        if stats['total'] == 0:
            return "[PASS] Third-party library analysis passed, no serious issues found"
        
        summary_parts = []
        if stats['high'] > 0:
            summary_parts.append(f"[HIGH] Found {stats['high']} high-risk library issues")
        if stats['medium'] > 0:
            summary_parts.append(f"[MEDIUM] Found {stats['medium']} medium-risk library issues")
        if stats['low'] > 0:
            summary_parts.append(f"[LOW] Found {stats['low']} low-risk library issues")
        
        return " | ".join(summary_parts)


def analyze_file(file_path: str, requirements_file: str = None) -> Dict[str, Any]:
    """分析单个文件"""
    analyzer = ThirdPartyAnalyzer(file_path, requirements_file)
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
        },
        'all_imports': set()
    }
    
    # 查找requirements.txt
    requirements_file = None
    if os.path.exists(os.path.join(directory, 'requirements.txt')):
        requirements_file = os.path.join(directory, 'requirements.txt')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    report = analyze_file(file_path, requirements_file)
                    results['files'].append(report)
                    
                    # 更新统计
                    results['total_stats']['total_files'] += 1
                    results['total_stats']['total_issues'] += report['stats']['total']
                    results['total_stats']['high_issues'] += report['stats']['high']
                    results['total_stats']['medium_issues'] += report['stats']['medium']
                    results['total_stats']['low_issues'] += report['stats']['low']
                    
                    # 收集所有导入
                    results['all_imports'].update(report['imports'])
                    
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
    print("Third-Party Library Analysis Report")
    print("=" * 80)
    
    if 'directory' in report:
        print(f"Directory: {report['directory']}")
        print(f"Files analyzed: {report['total_stats']['total_files']}")
        print(f"Total issues: {report['total_stats']['total_issues']}")
        print(f"High-risk issues: {report['total_stats']['high_issues']}")
        print(f"Medium-risk issues: {report['total_stats']['medium_issues']}")
        print(f"Low-risk issues: {report['total_stats']['low_issues']}")
        
        if report['all_imports']:
            print(f"All imports found: {', '.join(sorted(report['all_imports']))}")
        
        print("-" * 80)
        
        for file_report in report['files']:
            if 'error' in file_report:
                print(f"[ERROR] {os.path.basename(file_report['file'])}: {file_report['error']}")
            elif file_report['stats']['total'] > 0:
                print(f"[ISSUES] {os.path.basename(file_report['file'])}: {file_report['summary']}")
                if verbose:
                    for issue in file_report['issues']:
                        print(f"    [{issue['severity']}] {issue['type']} - {issue['message']}")
            else:
                print(f"[PASS] {os.path.basename(file_report['file'])}: Passed")
    else:
        # 单个文件报告
        print(f"File: {report['file']}")
        if report['imports']:
            print(f"Imports found: {', '.join(sorted(report['imports']))}")
        print(f"Total issues: {report['stats']['total']}")
        print(f"High-risk issues: {report['stats']['high']}")
        print(f"Medium-risk issues: {report['stats']['medium']}")
        print(f"Low-risk issues: {report['stats']['low']}")
        print("-" * 80)
        print(f"Summary: {report['summary']}")
        
        if verbose and report['issues']:
            print("\nDetailed issues:")
            for issue in report['issues']:
                print(f"  [{issue['severity']}] {issue['type']} - {issue['message']}")
    
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python third_party_analyzer_v1.py <file_or_directory> [requirements_file] [--verbose]")
        sys.exit(1)
    
    target = sys.argv[1]
    requirements_file = None
    verbose = '--verbose' in sys.argv
    
    # 查找requirements.txt参数
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg.endswith('.txt') and not arg.startswith('--'):
            requirements_file = arg
            break
    
    if os.path.isfile(target):
        report = analyze_file(target, requirements_file)
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