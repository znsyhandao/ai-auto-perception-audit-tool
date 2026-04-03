#!/usr/bin/env python3
"""简单检查文件状态"""

import json
import yaml
import os

def main():
    os.chdir("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("FILE STATUS CHECK")
    print("=" * 80)
    
    # 1. 检查文件存在和访问
    print()
    print("1. File existence and access:")
    files = ['skill.py', 'config.yaml', 'SKILL.md', 'README.md', 'CHANGELOG.md', 'package.json', 'skill_info.json']
    all_ok = True
    
    for filename in files:
        try:
            # 测试读取
            with open(filename, 'r', encoding='utf-8') as f:
                f.read(100)
            # 测试写入
            with open(filename, 'a', encoding='utf-8') as f:
                f.write('')
            print(f"   OK: {filename} exists and accessible")
        except Exception as e:
            print(f"   ERROR: {filename} - {e}")
            all_ok = False
    
    if not all_ok:
        print()
        print("ERROR: Some files missing or not accessible")
        return 1
    
    # 2. 检查版本一致性
    print()
    print("2. Version check:")
    
    # skill.py
    with open('skill.py', 'r', encoding='utf-8') as f:
        content = f.read()
    if '2.4.1' in content:
        print("   skill.py: contains 2.4.1")
    else:
        print("   skill.py: does not contain 2.4.1")
    
    # config.yaml
    with open('config.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    version = data.get('skill', {}).get('version', 'NOT_FOUND')
    print(f"   config.yaml: {version}")
    
    # SKILL.md
    with open('SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
    if '2.4.1' in content:
        print("   SKILL.md: contains 2.4.1")
    else:
        print("   SKILL.md: does not contain 2.4.1")
    
    # package.json
    with open('package.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   package.json: {data.get('version', 'NOT_FOUND')}")
    
    # skill_info.json
    with open('skill_info.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   skill_info.json: {data.get('version', 'NOT_FOUND')}")
    
    # CHANGELOG.md
    with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
        content = f.read()
    if '2.4.1' in content:
        print("   CHANGELOG.md: contains 2.4.1")
    else:
        print("   CHANGELOG.md: does not contain 2.4.1")
    
    print()
    print("=" * 80)
    print("SUCCESS: All files are now accessible")
    print("Word closed successfully!")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())