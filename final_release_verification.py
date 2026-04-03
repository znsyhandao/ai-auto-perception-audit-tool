#!/usr/bin/env python3
"""
最终发布验证
"""

import os
import sys

def verify_release_readiness(skill_dir):
    """验证发布就绪状态"""
    print("=== FINAL RELEASE VERIFICATION ===")
    print(f"Skill directory: {skill_dir}")
    print("=" * 60)
    
    # 1. 检查必需文件
    print("\n1. REQUIRED FILES CHECK:")
    required_files = [
        ("SKILL.md", "Skill documentation"),
        ("skill.py", "Main skill implementation"),
        ("config.yaml", "Configuration file"),
        ("package.json", "Package metadata"),
        ("requirements.txt", "Dependencies"),
        ("CHANGELOG.md", "Change history"),
        ("README.md", "User documentation"),
        ("LICENSE.txt", "License file")
    ]
    
    all_files_ok = True
    for file, description in required_files:
        file_path = os.path.join(skill_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   [OK] {file}: {description} ({size} bytes)")
        else:
            print(f"   [MISSING] {file}: MISSING - {description}")
            all_files_ok = False
    
    # 2. 检查版本一致性
    print("\n2. VERSION CONSISTENCY CHECK:")
    # 简单检查：查找版本号
    version_files = ["package.json", "CHANGELOG.md"]
    versions_found = []
    
    for file in version_files:
        file_path = os.path.join(skill_dir, file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "1.0.7" in content:
                    versions_found.append(file)
                    print(f"   [OK] {file}: Contains version 1.0.7")
                else:
                    print(f"   [WARN] {file}: Version 1.0.7 not found")
    
    version_ok = len(versions_found) == len(version_files)
    
    # 3. 检查安全声明
    print("\n3. SECURITY DECLARATIONS CHECK:")
    config_path = os.path.join(skill_dir, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        security_checks = [
            ("security:", "Security section", True),
            ("local_operation: true", "Local operation declaration", True),
            ("runtime_network_access: false", "No network access", True),
            ("runtime_shell_commands: false", "No shell commands", True)
        ]
        
        security_ok = True
        for pattern, description, required in security_checks:
            found = pattern in content.lower()
            status = "[OK]" if found else ("[WARN]" if not required else "[ERROR]")
            print(f"   {status} {description}: {'Found' if found else 'Missing'}")
            if required and not found:
                security_ok = False
    else:
        print("   [ERROR] config.yaml not found")
        security_ok = False
    
    # 4. 检查技能结构
    print("\n4. SKILL STRUCTURE CHECK:")
    skill_path = os.path.join(skill_dir, "skill.py")
    if os.path.exists(skill_path):
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        structure_checks = [
            ("class SleepRabbitSkill", "Skill class definition", True),
            ("def handle_command", "OpenClaw handle_command method", True),
            ("def get_commands", "OpenClaw get_commands method", True),
            ("def execute_command", "Command execution method", True)
        ]
        
        structure_ok = True
        for pattern, description, required in structure_checks:
            found = pattern in content
            status = "[OK]" if found else ("[WARN]" if not required else "[ERROR]")
            print(f"   {status} {description}: {'Found' if found else 'Missing'}")
            if required and not found:
                structure_ok = False
    else:
        print("   [ERROR] skill.py not found")
        structure_ok = False
    
    # 5. 检查文件大小和编码
    print("\n5. FILE SIZE AND ENCODING CHECK:")
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            file_count += 1
            
            # 检查大文件
            if size > 1024 * 1024:  # 1MB
                rel_path = os.path.relpath(file_path, skill_dir)
                print(f"   [WARN] Large file: {rel_path} ({size/1024/1024:.1f} MB)")
    
    print(f"   [OK] Total: {file_count} files, {total_size/1024:.1f} KB")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("RELEASE READINESS SUMMARY:")
    print("=" * 60)
    
    checks = [
        ("Required Files", all_files_ok),
        ("Version Consistency", version_ok),
        ("Security Declarations", security_ok),
        ("Skill Structure", structure_ok)
    ]
    
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    
    for check_name, ok in checks:
        status = "[OK] PASS" if ok else "[ERROR] FAIL"
        print(f"{status} - {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n[CELEBRATE] RELEASE READY! All checks passed.")
        print("\nNext steps:")
        print("1. Create final ZIP package")
        print("2. Upload to ClawHub")
        print("3. Submit for review")
        return True
    else:
        print(f"\n[WARN] NOT READY: {total - passed} checks failed")
        print("\nRequired fixes:")
        for check_name, ok in checks:
            if not ok:
                print(f"  - Fix {check_name}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python final_release_verification.py <skill_directory>")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    
    if not os.path.exists(skill_dir):
        print(f"Error: Directory not found: {skill_dir}")
        sys.exit(1)
    
    ready = verify_release_readiness(skill_dir)
    
    if ready:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())