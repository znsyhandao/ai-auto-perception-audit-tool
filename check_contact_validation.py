#!/usr/bin/env python3
"""
检查永久审核框架中是否有联系方式有效性检查
"""

import os

def check_framework_for_contact_validation():
    """检查框架中的联系方式验证"""
    
    framework_file = "D:/OpenClaw_TestingFramework/ONE_TIME_PERMANENT_AUDIT_FRAMEWORK.md"
    
    print("=" * 80)
    print("检查永久审核框架中的联系方式有效性检查")
    print("=" * 80)
    
    if not os.path.exists(framework_file):
        print("[ERROR] 框架文件不存在")
        return False
    
    with open(framework_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().lower()
    
    # 检查是否有明确的联系方式检查
    contact_keywords = [
        'contact', 'email', 'author', '联系方式', '作者', '邮箱',
        '联系信息', 'contact information', 'author info'
    ]
    
    validation_keywords = [
        '验证', '检查', '有效性', '真实', 'valid', 'check', 'verify'
    ]
    
    print("搜索联系方式相关检查...")
    
    found_contact = False
    found_validation = False
    
    for keyword in contact_keywords:
        if keyword in content:
            print(f"  找到: {keyword}")
            found_contact = True
    
    for keyword in validation_keywords:
        if keyword in content:
            print(f"  找到验证相关: {keyword}")
            found_validation = True
    
    # 检查具体的检查项
    print("\n检查具体的检查项列表...")
    
    # 查找检查项部分
    check_sections = [
        '检查项', 'check', '审核维度', '审核分类'
    ]
    
    has_contact_check = False
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if any(section in line for section in check_sections):
            # 检查接下来的几行
            for j in range(i, min(i+20, len(lines))):
                next_line = lines[j]
                if 'contact' in next_line or 'email' in next_line or '联系' in next_line or '作者' in next_line:
                    print(f"  在第 {j+1} 行找到联系方式检查: {next_line.strip()}")
                    has_contact_check = True
    
    print("\n" + "=" * 80)
    print("检查结果:")
    print("=" * 80)
    
    if has_contact_check:
        print("[OK] 框架中包含联系方式检查项")
        return True
    else:
        print("[严重遗漏] 框架中没有明确的联系方式有效性检查！")
        print("\n问题严重性:")
        print("1. ClawHub会验证作者联系方式的真实性和有效性")
        print("2. 虚假或无效的联系方式会导致审核失败")
        print("3. 这是基本但重要的合规要求")
        print("4. 我们的框架声称'全面'但遗漏了这个基础检查")
        
        print("\n需要立即修复:")
        print("1. 添加联系方式有效性检查到框架")
        print("2. 创建联系方式检查工具")
        print("3. 更新框架文档")
        print("4. 添加到审核流程")
        
        return False

def check_aisleepgen_contact_info():
    """检查AISleepGen的联系方式"""
    
    print("\n" + "=" * 80)
    print("检查AISleepGen的联系方式")
    print("=" * 80)
    
    files_to_check = [
        "D:/openclaw/AISleepGen/openclaw_skill/package.json",
        "D:/openclaw/AISleepGen/openclaw_skill/config.yaml",
        "D:/openclaw/AISleepGen/openclaw_skill/README.md",
        "D:/openclaw/AISleepGen/openclaw_skill/SKILL.md"
    ]
    
    contact_info_found = {}
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            print(f"\n检查 {filename}:")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 检查联系方式
                contact_patterns = [
                    ('author', '作者'),
                    ('email', '邮箱'),
                    ('contact', '联系'),
                    ('github', 'GitHub'),
                    ('url', '网址')
                ]
                
                for eng, chn in contact_patterns:
                    if eng in content.lower() or chn in content:
                        print(f"  找到: {eng}/{chn}")
                        if filename not in contact_info_found:
                            contact_info_found[filename] = []
                        contact_info_found[filename].append(f"{eng}/{chn}")
                        
            except Exception as e:
                print(f"  读取失败: {e}")
        else:
            print(f"\n文件不存在: {file_path}")
    
    print("\n" + "=" * 80)
    print("AISleepGen联系方式检查结果:")
    print("=" * 80)
    
    if contact_info_found:
        print("[OK] 找到联系方式信息")
        for file, contacts in contact_info_found.items():
            print(f"  {file}: {', '.join(contacts)}")
    else:
        print("[警告] 没有找到明确的联系方式信息")
        print("ClawHub可能会要求提供有效的作者联系方式")

def main():
    # 检查框架
    framework_has_contact_check = check_framework_for_contact_validation()
    
    # 检查AISleepGen
    check_aisleepgen_contact_info()
    
    print("\n" + "=" * 80)
    print("总体评估:")
    print("=" * 80)
    
    if not framework_has_contact_check:
        print("[紧急] 需要立即将联系方式有效性检查添加到永久审核框架")
        print("这是基本但重要的合规要求，当前框架有重大遗漏")
        
        print("\n具体需要添加:")
        print("1. 作者信息有效性检查")
        print("2. 邮箱格式验证")
        print("3. GitHub链接有效性验证")
        print("4. 联系方式一致性检查")
        
        return False
    else:
        print("[OK] 框架包含联系方式检查")
        return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n[检查完成] 联系方式检查已包含在框架中")
    else:
        print("\n[紧急] 需要立即修复框架遗漏")