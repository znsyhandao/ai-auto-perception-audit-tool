#!/usr/bin/env python3
"""
检查缺失方法 - 增强审核框架
检查代码中调用的方法是否真的存在
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, Set, List

def find_method_calls(filepath: str) -> Dict[str, List[str]]:
    """查找文件中所有的方法调用"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"syntax_error": [f"语法错误: {e}"]}
    
    method_calls = []
    
    class MethodCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute):
                # 方法调用: obj.method()
                method_name = node.func.attr
                method_calls.append(method_name)
            elif isinstance(node.func, ast.Name):
                # 函数调用: function()
                method_calls.append(node.func.id)
            self.generic_visit(node)
    
    visitor = MethodCallVisitor()
    visitor.visit(tree)
    
    return {"method_calls": method_calls}

def find_class_methods(filepath: str) -> Dict[str, List[str]]:
    """查找类中定义的方法"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {"class_methods": []}
    
    class_methods = {}
    
    class ClassVisitor(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)
            class_methods[node.name] = methods
            self.generic_visit(node)
    
    visitor = ClassVisitor()
    visitor.visit(tree)
    
    return class_methods

def check_missing_methods(skill_path: str):
    """检查缺失方法"""
    skill_dir = Path(skill_path)
    
    print(f"=== 检查缺失方法: {skill_dir.name} ===")
    
    # 收集所有方法定义
    all_methods = set()
    defined_methods = {}
    
    # 首先收集所有定义的方法
    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        class_methods = find_class_methods(str(py_file))
        for class_name, methods in class_methods.items():
            for method in methods:
                full_method_name = f"{class_name}.{method}"
                all_methods.add(full_method_name)
                defined_methods.setdefault(py_file.name, set()).add(full_method_name)
    
    # 检查方法调用
    missing_methods = []
    
    for py_file in skill_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        method_calls = find_method_calls(str(py_file))
        
        if "syntax_error" in method_calls:
            print(f"  ❌ {py_file.name}: {method_calls['syntax_error'][0]}")
            continue
            
        for call in method_calls.get("method_calls", []):
            # 检查是否在定义的方法中
            found = False
            for defined in all_methods:
                if defined.endswith(f".{call}"):
                    found = True
                    break
            
            if not found and call not in ["print", "len", "str", "int", "float", "list", "dict", "set", "tuple"]:
                # 排除内置函数
                missing_methods.append({
                    "file": py_file.name,
                    "method": call,
                    "line": "未知"  # 简化版本，不追踪行号
                })
    
    if missing_methods:
        print("❌ 发现缺失方法:")
        for item in missing_methods:
            print(f"  - {item['file']}: 调用了未定义的方法 '{item['method']}'")
        return False
    else:
        print("✅ 没有缺失方法")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_missing_methods.py <技能路径>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    success = check_missing_methods(skill_path)
    sys.exit(0 if success else 1)