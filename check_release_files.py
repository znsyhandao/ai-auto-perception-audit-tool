#!/usr/bin/env python3
"""
检查发布文件完整性
"""

import os
import sys
import json
import yaml

def check_required_files(skill_dir):
    """检查必需文件"""
    print("=== Checking Required Files ===")
    
    required_files = [
        "SKILL.md",
        "skill.py", 
        "config.yaml",
        "package.json",
        "requirements.txt",
        "CHANGELOG.md",
        "README.md",
        "LICENSE.txt"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if os.path.exists(file_path):
            print(f"  [OK] {file}")
        else:
            print(f"  [ERROR] {file} - MISSING")
            missing_files.append(file)
    
    return missing_files

def check_version_consistency(skill_dir):
    """检查版本一致性"""
    print("\n=== Checking Version Consistency ===")
    
    versions = {}
    
    # 检查SKILL.md
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "version:" in content:
                for line in content.split('\n'):
                    if "version:" in line:
                        versions['SKILL.md'] = line.split(':')[1].strip()
                        break
    
    # 检查package.json
    package_json_path = os.path.join(skill_dir, "package.json")
    if os.path.exists(package_json_path):
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            versions['package.json'] = data.get('version', 'N/A')
    
    # 检查CHANGELOG.md
    changelog_path = os.path.join(skill_dir, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找最新版本
            for line in content.split('\n'):
                if line.startswith('## [') and '] - ' in line:
                    versions['CHANGELOG.md'] = line.split('[')[1].split(']')[0]
                    break
    
    # 显示版本
    all_versions = list(versions.values())
    consistent = len(set(all_versions)) == 1
    
    for file, version in versions.items():
        print(f"  {file}: {version}")
    
    if consistent and all_versions:
        print(f"  [OK] All versions consistent: {all_versions[0]}")
    else:
        print(f"  [ERROR] Version inconsistency detected")
        print(f"     Found versions: {set(all_versions)}")
    
    return consistent

def check_security_declarations(skill_dir):
    """检查安全声明"""
    print("\n=== Checking Security Declarations ===")
    
    config_path = os.path.join(skill_dir, "config.yaml")
    if not os.path.exists(config_path):
        print("  [ERROR] config.yaml not found")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        security = config.get('security', {})
        
        print(f"  Local operation: {security.get('local_operation', 'Not specified')}")
        print(f"  Network access: {security.get('network_access', 'Not specified')}")
        print(f"  File access: {security.get('file_access', 'Not specified')}")
        
        # 检查关键安全声明
        if security.get('local_operation') == True:
            print("  [OK] Local operation declared")
            return True
        else:
            print("  [WARN] Local operation not explicitly declared")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Error reading config.yaml: {e}")
        return False

def check_file_encodings(skill_dir):
    """检查文件编码"""
    print("\n=== Checking File Encodings ===")
    
    text_extensions = ['.md', '.py', '.json', '.yaml', '.txt', '.js']
    problematic_files = []
    
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            if any(file.endswith(ext) for ext in text_extensions):
                file_path = os.path.join(root, file)
                try:
                    # 尝试用UTF-8读取
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read()
                    print(f"  [OK] {os.path.relpath(file_path, skill_dir)}")
                except UnicodeDecodeError:
                    print(f"  [ERROR] {os.path.relpath(file_path, skill_dir)} - Non-UTF-8 encoding")
                    problematic_files.append(file_path)
                except Exception as e:
                    print(f"  [WARN] {os.path.relpath(file_path, skill_dir)} - Error: {e}")
    
    return len(problematic_files) == 0

def check_for_prohibited_content(skill_dir):
    """检查禁止内容"""
    print("\n=== Checking for Prohibited Content ===")
    
    prohibited_patterns = [
        'child_process.exec',
        'exec(',
        'system(',
        'subprocess.call',
        'os.system',
        'eval(',
        '__import__'
    ]
    
    problematic_files = []
    
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            if file.endswith(('.py', '.js')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    found_patterns = []
                    for pattern in prohibited_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if found_patterns:
                        print(f"  [ERROR] {os.path.relpath(file_path, skill_dir)} - Contains: {', '.join(found_patterns)}")
                        problematic_files.append(file_path)
                    else:
                        print(f"  [OK] {os.path.relpath(file_path, skill_dir)}")
                        
                except Exception as e:
                    print(f"  [WARN] {os.path.relpath(file_path, skill_dir)} - Error: {e}")
    
    return len(problematic_files) == 0

def check_skill_structure(skill_dir):
    """检查技能结构"""
    print("\n=== Checking Skill Structure ===")
    
    skill_py_path = os.path.join(skill_dir, "skill.py")
    if not os.path.exists(skill_py_path):
        print("  [ERROR] skill.py not found")
        return False
    
    try:
        with open(skill_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_methods = [
            'def handle_command',
            'def get_commands',
            'class Skill'
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"  [ERROR] Missing methods: {', '.join(missing_methods)}")
            return False
        else:
            print("  [OK] All required methods found")
            return True
            
    except Exception as e:
        print(f"  [ERROR] Error reading skill.py: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python check_release_files.py <skill_directory>")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    
    if not os.path.exists(skill_dir):
        print(f"Error: Directory not found: {skill_dir}")
        sys.exit(1)
    
    print(f"Checking release files in: {skill_dir}")
    print("=" * 60)
    
    # 运行所有检查
    checks = [
        ("Required Files", check_required_files(skill_dir)),
        ("Version Consistency", check_version_consistency(skill_dir)),
        ("Security Declarations", check_security_declarations(skill_dir)),
        ("File Encodings", check_file_encodings(skill_dir)),
        ("Prohibited Content", check_for_prohibited_content(skill_dir)),
        ("Skill Structure", check_skill_structure(skill_dir))
    ]
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed_count = 0
    total_count = len(checks)
    
    for check_name, check_result in checks:
        if check_name == "Required Files":
            # 对于必需文件检查，结果是缺失文件列表
            if isinstance(check_result, list) and len(check_result) == 0:
                print(f"[OK] {check_name}: PASS")
                passed_count += 1
            else:
                print(f"[ERROR] {check_name}: FAIL (Missing: {', '.join(check_result)})")
        else:
            # 其他检查返回布尔值
            if check_result:
                print(f"[OK] {check_name}: PASS")
                passed_count += 1
            else:
                print(f"[ERROR] {check_name}: FAIL")
    
    print(f"\nTotal: {passed_count}/{total_count} checks passed")
    
    if passed_count == total_count:
        print("\n[CELEBRATE] ALL CHECKS PASSED! Ready for ClawHub release.")
        return 0
    else:
        print(f"\n[WARN] {total_count - passed_count} checks failed. Fix before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main())