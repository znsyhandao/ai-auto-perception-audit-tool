#!/usr/bin/env python3
"""
检查发布文件完整性 - 简单版本（无外部依赖）
"""

import os
import sys
import json

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
            size = os.path.getsize(file_path)
            print(f"  [OK] {file} ({size} bytes)")
        else:
            print(f"  [MISSING] {file} - MISSING")
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
            # 查找版本号
            import re
            version_match = re.search(r'version:\s*([\d.]+)', content)
            if version_match:
                versions['SKILL.md'] = version_match.group(1)
    
    # 检查package.json
    package_json_path = os.path.join(skill_dir, "package.json")
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                versions['package.json'] = data.get('version', 'N/A')
        except:
            versions['package.json'] = 'ERROR'
    
    # 检查CHANGELOG.md
    changelog_path = os.path.join(skill_dir, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找最新版本
            import re
            version_match = re.search(r'## \[([\d.]+)\]', content)
            if version_match:
                versions['CHANGELOG.md'] = version_match.group(1)
    
    # 显示版本
    all_versions = [v for v in versions.values() if v not in ['N/A', 'ERROR']]
    
    if not all_versions:
        print("  [WARN] No version information found")
        return False
    
    consistent = len(set(all_versions)) == 1
    
    for file, version in versions.items():
        status = "[OK]" if version not in ['N/A', 'ERROR'] else "[ERROR]"
        print(f"  {status} {file}: {version}")
    
    if consistent:
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
            content = f.read()
        
        # 简单检查安全声明
        has_local = 'local_operation: true' in content or 'local_operation: True' in content
        has_security_section = 'security:' in content
        
        print(f"  Security section: {'[OK] Found' if has_security_section else '[ERROR] Missing'}")
        print(f"  Local operation: {'[OK] Declared' if has_local else '[WARN] Not declared'}")
        
        return has_security_section and has_local
            
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
                    # print(f"  [OK] {os.path.relpath(file_path, skill_dir)}")
                except UnicodeDecodeError:
                    print(f"  [ERROR] {os.path.relpath(file_path, skill_dir)} - Non-UTF-8 encoding")
                    problematic_files.append(file_path)
                except Exception as e:
                    print(f"  [WARN] {os.path.relpath(file_path, skill_dir)} - Error: {e}")
    
    if problematic_files:
        print(f"  Found {len(problematic_files)} files with encoding issues")
        return False
    else:
        print("  [OK] All files are UTF-8 encoded")
        return True

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
                        print(f"  [ERROR] {os.path.relpath(file_path, skill_dir)} - Contains: {', '.join(found_patterns[:2])}")
                        problematic_files.append(file_path)
                    # else:
                    #     print(f"  [OK] {os.path.relpath(file_path, skill_dir)}")
                        
                except Exception as e:
                    print(f"  [WARN] {os.path.relpath(file_path, skill_dir)} - Error: {e}")
    
    if problematic_files:
        print(f"  Found {len(problematic_files)} files with prohibited content")
        return False
    else:
        print("  [OK] No prohibited content found")
        return True

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
        
        required_patterns = [
            'def handle_command',
            'def get_commands',
            'class.*Skill'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            import re
            if not re.search(pattern, content):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"  [ERROR] Missing patterns: {', '.join(missing_patterns)}")
            return False
        else:
            print("  [OK] All required patterns found")
            return True
            
    except Exception as e:
        print(f"  [ERROR] Error reading skill.py: {e}")
        return False

def check_directory_structure(skill_dir):
    """检查目录结构"""
    print("\n=== Checking Directory Structure ===")
    
    # 检查是否有禁止的目录
    prohibited_dirs = ['node_modules', '__pycache__', '.git', '.vscode']
    
    found_prohibited = []
    for root, dirs, files in os.walk(skill_dir):
        for dir_name in dirs:
            if dir_name in prohibited_dirs:
                found_prohibited.append(os.path.join(root, dir_name))
    
    if found_prohibited:
        print(f"  [ERROR] Found prohibited directories:")
        for dir_path in found_prohibited:
            print(f"     - {os.path.relpath(dir_path, skill_dir)}")
        return False
    else:
        print("  [OK] No prohibited directories found")
        return True

def check_file_sizes(skill_dir):
    """检查文件大小"""
    print("\n=== Checking File Sizes ===")
    
    large_files = []
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            file_count += 1
            
            # 检查是否过大（> 1MB）
            if size > 1024 * 1024:  # 1MB
                large_files.append((os.path.relpath(file_path, skill_dir), size))
    
    print(f"  Total files: {file_count}")
    print(f"  Total size: {total_size / 1024:.1f} KB")
    
    if large_files:
        print(f"  [WARN] Large files found (> 1MB):")
        for file_path, size in large_files:
            print(f"     - {file_path}: {size / 1024 / 1024:.1f} MB")
        return False
    else:
        print("  [OK] No excessively large files")
        return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python check_release_files_simple.py <skill_directory>")
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
        ("Skill Structure", check_skill_structure(skill_dir)),
        ("Directory Structure", check_directory_structure(skill_dir)),
        ("File Sizes", check_file_sizes(skill_dir))
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
                print(f"[PASS] {check_name}")
                passed_count += 1
            else:
                print(f"[FAIL] {check_name} (Missing: {', '.join(check_result)})")
        else:
            # 其他检查返回布尔值
            if check_result:
                print(f"[PASS] {check_name}")
                passed_count += 1
            else:
                print(f"[FAIL] {check_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} checks passed")
    
    if passed_count == total_count:
        print("\n[SUCCESS] ALL CHECKS PASSED! Ready for ClawHub release.")
        return 0
    else:
        print(f"\n[WARNING] {total_count - passed_count} checks failed. Fix before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main())