#!/usr/bin/env python3
"""
ClawHub级别审核框架 - 根本解决方案
检查ClawHub发现的所有问题类型
"""

import ast
import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import importlib.util

# ==================== 工具函数 ====================

def safe_print(message: str):
    """安全打印（避免编码问题）"""
    # 移除Unicode表情符号
    clean_message = re.sub(r'[^\x00-\x7F]+', '', message)
    print(clean_message)

def read_file_safely(filepath: str) -> str:
    """安全读取文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='gbk') as f:
                return f.read()
        except:
            return ""

# ==================== 检查1: 依赖声明一致性 ====================

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

def extract_imports_from_code(content: str) -> Set[str]:
    """从代码中提取导入"""
    imports = set()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return imports
    
    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
            self.generic_visit(node)
        
        def visit_ImportFrom(self, node):
            if node.module:
                imports.add(node.module.split('.')[0])
            self.generic_visit(node)
    
    visitor = ImportVisitor()
    visitor.visit(tree)
    return imports

def read_requirements(filepath: str) -> Set[str]:
    """读取requirements.txt"""
    if not os.path.exists(filepath):
        return set()
    
    requirements = set()
    content = read_file_safely(filepath)
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
            if match:
                requirements.add(match.group(1).lower())
    
    return requirements

def check_dependency_consistency(skill_dir: Path) -> Tuple[bool, List[str]]:
    """检查依赖声明一致性"""
    issues = []
    
    # 读取requirements
    req_file = skill_dir / "requirements.txt"
    declared_deps = read_requirements(str(req_file))
    
    # 收集所有导入
    all_imports = set()
    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        content = read_file_safely(str(py_file))
        imports = extract_imports_from_code(content)
        all_imports.update(imports)
    
    # 过滤标准库
    external_imports = {imp for imp in all_imports 
                       if imp not in STANDARD_LIB_MODULES and not imp.startswith('_')}
    
    # 检查未声明的导入
    for imp in external_imports:
        if imp.lower() not in declared_deps:
            issues.append(f"代码导入了 '{imp}'，但未在requirements.txt中声明")
    
    # 检查声明但未使用的依赖
    for dep in declared_deps:
        if dep not in [imp.lower() for imp in external_imports]:
            issues.append(f"requirements.txt声明了 '{dep}'，但代码中未导入")
    
    return len(issues) == 0, issues

# ==================== 检查2: 方法实现完整性 ====================

def find_method_definitions(content: str) -> Dict[str, List[str]]:
    """查找方法定义"""
    definitions = {}
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return definitions
    
    class DefinitionVisitor(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)
            definitions[node.name] = methods
            self.generic_visit(node)
    
    visitor = DefinitionVisitor()
    visitor.visit(tree)
    return definitions

def find_method_calls(content: str) -> List[str]:
    """查找方法调用"""
    calls = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return calls
    
    class CallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
            elif isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            self.generic_visit(node)
    
    visitor = CallVisitor()
    visitor.visit(tree)
    return calls

def check_method_completeness(skill_dir: Path) -> Tuple[bool, List[str]]:
    """检查方法完整性"""
    issues = []
    
    # 收集所有方法定义
    all_methods = set()
    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        content = read_file_safely(str(py_file))
        definitions = find_method_definitions(content)
        for class_name, methods in definitions.items():
            for method in methods:
                all_methods.add(f"{class_name}.{method}")
    
    # 检查方法调用
    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        content = read_file_safely(str(py_file))
        calls = find_method_calls(content)
        
        for call in calls:
            # 排除内置函数和常见方法
            builtin_functions = {'print', 'len', 'str', 'int', 'float', 'list', 
                                'dict', 'set', 'tuple', 'range', 'enumerate',
                                'zip', 'map', 'filter', 'sorted', 'reversed',
                                'isinstance', 'type', 'hasattr', 'getattr'}
            
            if call in builtin_functions:
                continue
            
            # 检查是否在定义的方法中
            found = any(method.endswith(f".{call}") for method in all_methods)
            if not found:
                issues.append(f"{py_file.name}: 调用了未定义的方法 '{call}'")
    
    return len(issues) == 0, issues

# ==================== 检查3: 安全声明真实性 ====================

def extract_security_claims_from_docs(skill_dir: Path) -> List[str]:
    """从文档中提取安全声明"""
    claims = []
    
    # 检查SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = read_file_safely(str(skill_md))
        
        # 查找安全相关声明
        security_keywords = ['security', 'safe', 'protect', 'restrict', 
                            'limit', 'block', 'prevent', 'validate', 'check']
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in security_keywords:
                if keyword in line_lower and len(line.strip()) > 10:
                    claims.append(f"SKILL.md 第{i+1}行: {line.strip()}")
                    break
    
    return claims

def check_code_implementation(skill_dir: Path, claims: List[str]) -> Tuple[bool, List[str]]:
    """检查代码实现"""
    issues = []
    
    # 检查常见安全声明的实现
    for claim in claims:
        claim_lower = claim.lower()
        
        # 检查路径限制
        if 'path' in claim_lower and ('restrict' in claim_lower or 'limit' in claim_lower):
            # 检查是否有PathValidator类
            has_path_validator = False
            for py_file in skill_dir.rglob("*.py"):
                if "path_validator" in str(py_file).lower():
                    has_path_validator = True
                    break
            
            if not has_path_validator:
                issues.append(f"声明了路径限制，但未找到PathValidator实现: {claim}")
        
        # 检查符号链接
        if 'symlink' in claim_lower or 'symbolic' in claim_lower:
            # 检查是否有symlink检查
            has_symlink_check = False
            for py_file in skill_dir.rglob("*.py"):
                content = read_file_safely(str(py_file))
                if 'symlink' in content.lower() or 'is_symlink' in content:
                    has_symlink_check = True
                    break
            
            if not has_symlink_check:
                issues.append(f"声明了符号链接检查，但未找到实现: {claim}")
    
    return len(issues) == 0, issues

# ==================== 主审核函数 ====================

def run_clawhub_level_audit(skill_path: str) -> Dict[str, any]:
    """运行ClawHub级别审核"""
    skill_dir = Path(skill_path)
    
    safe_print(f"=== ClawHub级别审核: {skill_dir.name} ===")
    
    results = {
        "skill_name": skill_dir.name,
        "timestamp": "2026-04-01 18:00",
        "checks": [],
        "all_passed": True,
        "issues": []
    }
    
    # 检查1: 依赖声明一致性
    safe_print("\n[1] 检查依赖声明一致性...")
    passed, issues = check_dependency_consistency(skill_dir)
    results["checks"].append({
        "name": "依赖声明一致性",
        "passed": passed,
        "issues": issues
    })
    if not passed:
        results["all_passed"] = False
        results["issues"].extend(issues)
    
    # 检查2: 方法实现完整性
    safe_print("[2] 检查方法实现完整性...")
    passed, issues = check_method_completeness(skill_dir)
    results["checks"].append({
        "name": "方法实现完整性",
        "passed": passed,
        "issues": issues
    })
    if not passed:
        results["all_passed"] = False
        results["issues"].extend(issues)
    
    # 检查3: 安全声明真实性
    safe_print("[3] 检查安全声明真实性...")
    claims = extract_security_claims_from_docs(skill_dir)
    if claims:
        safe_print(f"  找到 {len(claims)} 个安全声明")
        passed, issues = check_code_implementation(skill_dir, claims)
        results["checks"].append({
            "name": "安全声明真实性",
            "passed": passed,
            "issues": issues
        })
        if not passed:
            results["all_passed"] = False
            results["issues"].extend(issues)
    else:
        results["checks"].append({
            "name": "安全声明真实性",
            "passed": True,
            "issues": ["没有找到安全声明"]
        })
    
    # 总结
    safe_print("\n=== 审核结果 ===")
    passed_checks = sum(1 for check in results["checks"] if check["passed"])
    total_checks = len(results["checks"])
    
    safe_print(f"通过检查: {passed_checks}/{total_checks}")
    
    if results["all_passed"]:
        safe_print("✅ 所有检查通过")
    else:
        safe_print("❌ 发现问题:")
        for issue in results["issues"]:
            safe_print(f"  - {issue}")
    
    # 保存报告
    report_file = skill_dir.parent / f"{skill_dir.name}_clawhub_audit_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    safe_print(f"报告已保存: {report_file}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        safe_print("用法: python clawhub_level_audit.py <技能路径>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    results = run_clawhub_level_audit(skill_path)
    
    sys.exit(0 if results["all_passed"] else 1)