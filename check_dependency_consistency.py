#!/usr/bin/env python3
"""
检查依赖声明一致性 - 增强审核框架
检查导入的库是否在requirements中声明
"""

import ast
import os
import sys
import re
from pathlib import Path
from typing import Set, List

# 标准库模块列表（不需要在requirements中声明）
STANDARD_LIB_MODULES = {
    'os', 'sys', 'math', 'statistics', 'datetime', 'time', 'json', 're',
    'pathlib', 'typing', 'collections', 'itertools', 'functools', 'random',
    'string', 'hashlib', 'base64', 'csv', 'io', 'pprint', 'textwrap',
    'inspect', 'argparse', 'getpass', 'platform', 'subprocess', 'shutil',
    'tempfile', 'glob', 'fnmatch', 'pickle', 'sqlite3', 'zipfile', 'tarfile',
    'html', 'xml', 'urllib', 'http', 'socket', 'ssl', 'ftplib', 'poplib',
    'imaplib', 'smtplib', 'telnetlib', 'uuid', 'logging', 'warnings',
    'decimal', 'fractions', 'numbers', 'array', 'struct', 'copy', 'types',
    'enum', 'weakref', 'contextlib', 'abc', 'atexit', 'traceback', 'gc',
    'site', 'sysconfig', 'builtins', '__future__', 'importlib', 'pkgutil',
    'modulefinder', 'runpy', 'zipimport', 'pydoc', 'doctest', 'unittest',
    'test', 'threading', 'multiprocessing', 'concurrent', 'asyncio',
    'selectors', 'select', 'queue', 'sched', 'contextvars', 'dataclasses'
}

def extract_imports(filepath: str) -> Set[str]:
    """提取文件中的所有导入"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    imports = set()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return imports
    
    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])  # 只取顶级包名
            self.generic_visit(node)
        
        def visit_ImportFrom(self, node):
            if node.module:
                imports.add(node.module.split('.')[0])  # 只取顶级包名
            self.generic_visit(node)
    
    visitor = ImportVisitor()
    visitor.visit(tree)
    
    return imports

def read_requirements(filepath: str) -> Set[str]:
    """读取requirements.txt中的依赖"""
    if not os.path.exists(filepath):
        return set()
    
    requirements = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 提取包名（移除版本号）
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    requirements.add(match.group(1).lower())
    
    return requirements

def check_dependency_consistency(skill_path: str):
    """检查依赖声明一致性"""
    skill_dir = Path(skill_path)
    
    print(f"=== 检查依赖声明一致性: {skill_dir.name} ===")
    
    # 读取requirements.txt
    req_file = skill_dir / "requirements.txt"
    declared_deps = read_requirements(str(req_file))
    
    if not req_file.exists():
        print("⚠️  requirements.txt不存在")
        declared_deps = set()
    
    print(f"  声明的依赖: {sorted(declared_deps)}")
    
    # 收集所有导入
    all_imports = set()
    file_imports = {}
    
    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        imports = extract_imports(str(py_file))
        if imports:
            all_imports.update(imports)
            file_imports[py_file.name] = imports
    
    # 过滤标准库
    external_imports = set()
    for imp in all_imports:
        if imp not in STANDARD_LIB_MODULES and not imp.startswith('_'):
            external_imports.add(imp)
    
    print(f"  代码中的外部导入: {sorted(external_imports)}")
    
    # 检查一致性
    issues = []
    
    # 1. 检查未声明的导入
    for imp in external_imports:
        if imp.lower() not in declared_deps:
            # 查找哪些文件导入了这个库
            files_with_import = []
            for file_name, imports in file_imports.items():
                if imp in imports:
                    files_with_import.append(file_name)
            
            issues.append({
                "type": "undeclared_import",
                "module": imp,
                "files": files_with_import,
                "message": f"代码导入了 '{imp}'，但未在requirements.txt中声明"
            })
    
    # 2. 检查声明但未使用的依赖
    for dep in declared_deps:
        if dep not in [imp.lower() for imp in external_imports]:
            issues.append({
                "type": "unused_dependency",
                "module": dep,
                "message": f"requirements.txt声明了 '{dep}'，但代码中未导入"
            })
    
    if issues:
        print("❌ 依赖声明不一致:")
        for issue in issues:
            print(f"  - {issue['message']}")
            if 'files' in issue and issue['files']:
                print(f"    在文件中: {', '.join(issue['files'])}")
        return False
    else:
        print("✅ 依赖声明一致")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_dependency_consistency.py <技能路径>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    success = check_dependency_consistency(skill_path)
    sys.exit(0 if success else 1)