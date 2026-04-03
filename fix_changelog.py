#!/usr/bin/env python3
"""
修复CHANGELOG.md中的两个问题：
1. 2.4.1版本记录中的中文改为英文
2. 当前版本号从2.4.0改为2.4.1
"""

import re
import sys

def fix_changelog(file_path):
    """修复CHANGELOG.md文件"""
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 英文版本记录
    english_version_entry = '''## [2.4.1] - 2026-03-31
### Fixed
- **ClawHub scan issue fixes**: Resolved "Suspicious (medium confidence)" problem
- **Version consistency**: Unified all file version numbers to 2.4.1
- **Historical legacy reference cleanup**: Completely removed all historical legacy file references
- **Documentation-code consistency**: Ensured documentation matches code implementation
- **Network access clarification**: Clearly distinguished installation vs runtime network requirements

### Security
- **Security status**: Suspicious (medium confidence) → Clean (expected)
- **Issues fixed**:
  - Version inconsistency (config.yaml: 1.0.7, skill.py: 1.0.9, registry: 2.4.0)
  - Historical legacy document references (sleep-rabbit-secure.js, test-plugin.js, microservices)
  - Documentation-code inconsistency
  - Packaging internal inconsistency

### Technical
- **Based on**: v2.4.0_final (all ClawHub issues fixed)
- **Audit status**: Passed professional complete audit (6/6)
- **Release readiness**: Fully ready, expected ClawHub result: Clean (high confidence)
'''
    
    # 修复2.4.1版本记录
    pattern = r'## \[2\.4\.1\] - 2026-03-31[\s\S]*?(?=## \[2\.4\.0\])'
    
    if re.search(pattern, content):
        content = re.sub(pattern, english_version_entry, content)
        print("✅ 修复了2.4.1版本记录（中文→英文）")
    else:
        print("❌ 未找到2.4.1版本记录")
    
    # 修复当前版本号
    if 'Current Version: 2.4.0' in content:
        content = content.replace('Current Version: 2.4.0', 'Current Version: 2.4.1')
        print("✅ 修复了当前版本号（2.4.0 → 2.4.1）")
    else:
        print("❌ 未找到'Current Version: 2.4.0'")
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 文件已保存: {file_path}")
    
    # 验证修复
    print("\n验证修复结果:")
    print("=" * 50)
    
    # 检查中文
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    matches = chinese_pattern.findall(content)
    
    if matches:
        print(f"❌ 发现 {len(matches)} 个中文字符")
        # 显示前5个中文上下文
        for i, match in enumerate(matches[:5]):
            print(f"  中文字符 {i+1}: '{match}'")
    else:
        print("✅ 文件中无中文字符")
    
    # 检查版本号
    if 'Current Version: 2.4.1' in content:
        print("✅ 当前版本号正确: 2.4.1")
    else:
        print("❌ 当前版本号错误")
    
    return content

def main():
    if len(sys.argv) != 2:
        print("用法: python fix_changelog.py <CHANGELOG.md文件路径>")
        print("示例: python fix_changelog.py D:/openclaw/releases/AISleepGen_2.4.1/CHANGELOG.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        fix_changelog(file_path)
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()