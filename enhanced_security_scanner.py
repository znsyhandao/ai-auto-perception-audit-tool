#!/usr/bin/env python3
"""
增强版安全检查脚本 - 基于AISkinX经验
添加config.yaml检查、文件编码检查等
"""

import os
import sys
import re
import json
import yaml
from pathlib import Path

def print_section(title, level=1):
    """打印章节标题"""
    if level == 1:
        print(f"\n{'='*60}")
        print(f"[DETAILS] {title}")
        print(f"{'='*60}")
    else:
        print(f"\n[LIST] {title}")
        print("-" * 40)

def check_file_encoding(directory):
    """检查文件编码 - 新增：基于乱码问题"""
    print_section("1. 文件编码检查", 1)
    
    files_to_check = [
        "skill.py",
        "README.md", 
        "SKILL.md",
        "CHANGELOG.md",
        "config.yaml",
        "package.json"
    ]
    
    issues = []
    
    for filename in files_to_check:
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            issues.append(f"[ERROR] {filename}: 文件不存在")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(1000)
                
            # 检查是否有中文字符（对于中文文件）
            if filename.endswith('.md') or filename.endswith('.yaml'):
                if re.search(r'[\u4e00-\u9fff]', content):
                    print(f"[OK] {filename}: UTF-8编码正常，中文显示正确")
                else:
                    # 可能是纯英文或无中文
                    size = os.path.getsize(filepath)
                    print(f"[WARN]  {filename}: UTF-8编码，无中文字符 ({size}字节)")
            else:
                # 代码文件，检查基本可读性
                if 'import' in content or 'def ' in content or 'class ' in content:
                    print(f"[OK] {filename}: UTF-8编码正常，内容可读")
                else:
                    issues.append(f"[WARN]  {filename}: 内容可能有问题")
                    
        except UnicodeDecodeError:
            issues.append(f"[ERROR] {filename}: 编码错误，不是有效的UTF-8")
        except Exception as e:
            issues.append(f"[ERROR] {filename}: 读取失败 - {e}")
    
    if issues:
        print("\n[WARN]  发现编码问题:")
        for issue in issues:
            print(f"  {issue}")
        return False
    return True

def check_config_yaml(directory):
    """检查config.yaml安全性 - 新增：基于AISkinX经验"""
    print_section("2. config.yaml安全检查", 1)
    
    config_path = os.path.join(directory, "config.yaml")
    if not os.path.exists(config_path):
        print("[ERROR] config.yaml文件不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查危险配置（AISkinX经验）
        dangerous_patterns = [
            (r'original_api_url', '外部API端点'),
            (r'world_model_integrator', 'GPT-4集成'),
            (r'model: "gpt-', 'GPT模型配置'),
            (r'updates\.auto_check: true', '自动更新检查'),
            (r'external_apis', '外部API集成'),
            (r'http://', 'HTTP URL'),
            (r'https://', 'HTTPS URL'),
            (r'api.*url', 'API URL'),
            (r'database.*enabled: true', '数据库集成')
        ]
        
        found_dangerous = False
        for pattern, description in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"[ERROR] 发现危险配置: {description}")
                found_dangerous = True
        
        if found_dangerous:
            print("[ERROR] config.yaml包含网络相关配置（ClawHub会标记为Suspicious）")
            return False
        
        # 检查安全声明（必须有的）
        required_declarations = [
            ('network_access: false', '无网络访问声明'),
            ('local_only: true', '仅本地处理声明'),
            ('privacy_friendly: true', '隐私友好声明')
        ]
        
        missing_declarations = []
        for pattern, description in required_declarations:
            if not re.search(pattern, content):
                missing_declarations.append(description)
        
        if missing_declarations:
            print("[ERROR] config.yaml缺少安全声明:")
            for desc in missing_declarations:
                print(f"  - {desc}")
            return False
        
        print("[OK] config.yaml干净，无网络相关配置")
        print("[OK] config.yaml有明确的安全声明")
        return True
            
    except yaml.YAMLError as e:
        print(f"[ERROR] config.yaml格式错误: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] 读取config.yaml失败: {e}")
        return False

def check_network_code(directory):
    """检查网络代码"""
    print_section("3. 网络代码检查", 1)
    
    network_patterns = [
        r'import requests',
        r'from requests',
        r'import urllib',
        r'import http\.client',
        r'import socket',
        r'requests\.(get|post|put|delete)',
        r'urllib\.request',
        r'http\.client\.',
        r'socket\.',
        r'webhook',
        r'api.*call',
        r'在线验证',
        r'license.*validation'
    ]
    
    found = False
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in network_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                print(f"[ERROR] {path}: 发现网络代码 - {pattern}")
                                found = True
                except:
                    pass
    
    if found:
        print("[ERROR] 发现网络代码")
        return False
    else:
        print("[OK] 无网络代码")
        return True

def check_dangerous_functions(directory):
    """检查危险函数"""
    print_section("4. 危险函数检查", 1)
    
    dangerous_patterns = [
        r'subprocess\.',
        r'os\.system\(',
        r'eval\(',
        r'exec\(',
        r'__import__\(',
        r'open\(.*[\'\"][wax][\'\"].*\)',
        r'shutil\.rmtree',
        r'os\.remove',
        r'os\.unlink'
    ]
    
    found = False
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in dangerous_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                print(f"[ERROR] {path}: 发现危险函数 - {pattern}")
                                found = True
                except:
                    pass
    
    if found:
        print("[ERROR] 发现危险函数")
        return False
    else:
        print("[OK] 无危险函数")
        return True

def check_external_dependencies(directory):
    """检查外部依赖"""
    print_section("5. 外部依赖检查", 1)
    
    dependency_patterns = [
        r'import numpy',
        r'import pandas',
        r'import torch',
        r'import tensorflow',
        r'import sklearn',
        r'import cv2',
        r'import PIL',
        r'import yaml',
        r'import flask',
        r'import django',
        r'import fastapi'
    ]
    
    found = False
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in dependency_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                print(f"[ERROR] {path}: 发现外部依赖 - {pattern}")
                                found = True
                except:
                    pass
    
    if found:
        print("[ERROR] 发现外部依赖")
        return False
    else:
        print("[OK] 仅使用Python标准库")
        return True

def check_package_json(directory):
    """检查package.json"""
    print_section("6. package.json检查", 1)
    
    package_path = os.path.join(directory, "package.json")
    if not os.path.exists(package_path):
        print("[ERROR] package.json文件不存在")
        return False
    
    try:
        with open(package_path, 'r', encoding='utf-8') as f:
            package = json.load(f)
        
        # 检查版本号
        version = package.get('version', '')
        if not version:
            print("[ERROR] 缺少版本号")
            return False
        else:
            print(f"[OK] 版本号: {version}")
        
        # 检查权限
        permissions = package.get('openclaw', {}).get('permissions', '')
        if permissions == 'filesystem':
            print("[OK] 权限最小化 (仅filesystem)")
            return True
        else:
            print(f"[ERROR] 权限过大: {permissions}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"[ERROR] package.json格式错误: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] 读取package.json失败: {e}")
        return False

def check_documentation_consistency(directory):
    """检查文档一致性"""
    print_section("7. 文档一致性检查", 1)
    
    readme_path = os.path.join(directory, "README.md")
    if not os.path.exists(readme_path):
        print("[ERROR] README.md文件不存在")
        return False
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme = f.read()
        
        # 检查README中的关键声明
        declarations = {
            "100%本地处理": "100%本地处理" in readme or "本地处理" in readme,
            "无网络访问": "无网络访问" in readme or "无网络" in readme,
            "零依赖": "零依赖" in readme,
            "隐私安全": "隐私安全" in readme or "隐私保护" in readme,
            "权限最小化": "权限最小化" in readme or "仅filesystem" in readme
        }
        
        missing = []
        for decl, has in declarations.items():
            if has:
                print(f"[OK] {decl}")
            else:
                print(f"[ERROR] {decl}")
                missing.append(decl)
        
        if missing:
            print(f"[ERROR] README缺少{len(missing)}个关键声明")
            return False
        else:
            print("[OK] README文档声明完整")
            return True
            
    except Exception as e:
        print(f"[ERROR] 读取README失败: {e}")
        return False

def check_skill_structure(directory):
    """检查技能结构"""
    print_section("8. 技能结构检查", 1)
    
    required_files = [
        "skill.py",
        "README.md",
        "package.json",
        "LICENSE.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(directory, file)):
            missing_files.append(file)
    
    if missing_files:
        print("[ERROR] 缺少必要文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("[OK] 技能结构完整")
    
    # 检查文件大小（避免token限制）
    large_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.md', '.yaml', '.json')):
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                if size > 20000:  # 20KB以上可能有问题
                    large_files.append((file, size))
    
    if large_files:
        print("[WARN]  发现大文件（可能触发token限制）:")
        for file, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
            size_kb = size / 1024
            print(f"  {file:30} - {size_kb:.2f}KB")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python enhanced_security_scanner.py <技能目录>")
        print("示例: python enhanced_security_scanner.py ./my-skill")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"错误: {directory} 不是有效目录")
        sys.exit(1)
    
    print("=" * 60)
    print("[MICROSCOPE] 增强版安全检查 - 基于AISkinX经验")
    print("=" * 60)
    print(f"检查目录: {directory}")
    print("=" * 60)
    
    checks = [
        ("文件编码检查", check_file_encoding),
        ("config.yaml检查", check_config_yaml),
        ("网络代码检查", check_network_code),
        ("危险函数检查", check_dangerous_functions),
        ("外部依赖检查", check_external_dependencies),
        ("package.json检查", check_package_json),
        ("文档一致性检查", check_documentation_consistency),
        ("技能结构检查", check_skill_structure)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func(directory)
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}检查失败: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("[DASHBOARD] 检查结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] 通过" if result else "[ERROR] 失败"
        print(f"{status} - {name}")
    
    print(f"\n[TARGET] 总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n[CELEBRATE] 所有检查通过！可以安全发布")
        sys.exit(0)
    else:
        print("\n[ERROR] 检查未通过，需要修复问题")
        sys.exit(1)

if __name__ == "__main__":
    main()