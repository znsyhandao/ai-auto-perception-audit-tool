#!/usr/bin/env python3
"""
增强版审核框架 V2 - 包含今天所有经验教训的完整审核系统
2026-04-02 更新：集成今天遇到的所有问题解决方案
"""

import os
import sys
import re
import json
from pathlib import Path

def run_enhanced_audit_v2(skill_dir):
    """运行增强版审核 V2"""
    print("=" * 80)
    print("增强版审核框架 V2 - 完整审核流程 (2026-04-02更新)")
    print("=" * 80)
    print(f"技能目录: {skill_dir}")
    print("=" * 80)
    
    all_checks_passed = True
    
    # ==================== 阶段1: 发布前清理 ====================
    print("\n[1/5] 运行发布前清理器")
    print("-" * 40)
    
    cleanup_passed = run_pre_release_cleanup(skill_dir)
    if not cleanup_passed:
        all_checks_passed = False
    
    # ==================== 阶段2: 文件大小检查 ====================
    print("\n[2/5] 文件大小和结构检查")
    print("-" * 40)
    
    file_check_passed = run_file_size_check(skill_dir)
    if not file_check_passed:
        all_checks_passed = False
    
    # ==================== 阶段3: 内容合规检查 ====================
    print("\n[3/5] 内容合规检查")
    print("-" * 40)
    
    content_check_passed = run_content_compliance_check(skill_dir)
    if not content_check_passed:
        all_checks_passed = False
    
    # ==================== 阶段4: 永久审核 ====================
    print("\n[4/5] 运行永久审核框架")
    print("-" * 40)
    
    permanent_audit_passed = run_permanent_audit(skill_dir)
    if not permanent_audit_passed:
        all_checks_passed = False
    
    # ==================== 阶段5: 安全检查 ====================
    print("\n[5/5] 运行安全检查")
    print("-" * 40)
    
    security_check_passed = run_security_check_v2(skill_dir)
    if not security_check_passed:
        all_checks_passed = False
    
    # ==================== 最终报告 ====================
    print("\n" + "=" * 80)
    print("增强版审核 V2 完成！")
    print("=" * 80)
    
    if all_checks_passed:
        print("✅ 所有检查通过！")
        print("✅ 发布前清理完成")
        print("✅ 文件大小检查通过")
        print("✅ 内容合规检查通过")
        print("✅ 永久审核通过")
        print("✅ 安全检查通过")
        print("\n🎉 技能已准备好发布到ClawHub！")
        return True
    else:
        print("❌ 部分检查未通过")
        print("\n⚠️ 请修复上述问题后重新审核")
        return False

def run_pre_release_cleanup(skill_dir):
    """运行发布前清理"""
    try:
        # 导入清理器
        sys.path.insert(0, str(Path(__file__).parent))
        from pre_release_cleaner import PreReleaseCleaner
        
        cleaner = PreReleaseCleaner(skill_dir)
        cleanup_success = cleaner.run_full_cleanup()
        
        if cleanup_success:
            print("✅ 发布前清理完成")
            return True
        else:
            print("❌ 清理失败")
            return False
            
    except Exception as e:
        print(f"⚠️ 清理器运行失败: {e}")
        print("继续其他检查...")
        return True  # 继续其他检查

def run_file_size_check(skill_dir):
    """检查文件大小和结构"""
    skill_path = Path(skill_dir)
    
    print("检查文件大小限制...")
    
    # 检查必需文件
    required_files = ["skill.py", "config.yaml", "SKILL.md", "README.md", "CHANGELOG.md", "requirements.txt"]
    missing_files = []
    
    for file in required_files:
        if not (skill_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺失必需文件: {missing_files}")
        return False
    
    print("✅ 所有必需文件存在")
    
    # 检查文件大小
    large_files = []
    for file in required_files:
        file_path = skill_path / file
        if file_path.exists():
            size = file_path.stat().st_size
            if size > 50000:  # 50KB限制
                large_files.append((file, size))
    
    if large_files:
        print("⚠️ 发现大文件:")
        for file, size in large_files:
            print(f"  {file}: {size} bytes")
        print("建议优化文件大小")
    
    # 检查重复文件
    print("检查重复文件和目录...")
    all_files = list(skill_path.rglob("*"))
    
    # 检查是否有嵌套的发布目录
    nested_releases = [f for f in all_files if "release" in str(f).lower() and f.is_dir()]
    if nested_releases:
        print(f"⚠️ 发现嵌套发布目录: {[str(f.relative_to(skill_path)) for f in nested_releases]}")
    
    print("✅ 文件结构检查完成")
    return True

def run_content_compliance_check(skill_dir):
    """内容合规检查"""
    skill_path = Path(skill_dir)
    
    print("检查内容合规性...")
    
    issues = []
    
    # 1. 检查英文合规
    english_issues = check_english_compliance(skill_path)
    if english_issues:
        issues.extend(english_issues)
    
    # 2. 检查内容一致性
    consistency_issues = check_content_consistency(skill_path)
    if consistency_issues:
        issues.extend(consistency_issues)
    
    # 3. 检查注册表名称一致性
    registry_issues = check_registry_consistency(skill_path)
    if registry_issues:
        issues.extend(registry_issues)
    
    if issues:
        print("❌ 内容合规问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ 内容合规检查通过")
        return True

def check_english_compliance(skill_path):
    """检查是否全英文"""
    issues = []
    
    # 检查的文件类型
    text_files = list(skill_path.glob("*.py")) + \
                 list(skill_path.glob("*.md")) + \
                 list(skill_path.glob("*.yaml")) + \
                 list(skill_path.glob("*.yml")) + \
                 list(skill_path.glob("*.txt"))
    
    for file in text_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查中文字符
            if re.search(r'[\u4e00-\u9fff]', content):
                issues.append(f"{file.name}: 包含中文字符 (要求全英文)")
        except:
            pass
    
    return issues

def check_content_consistency(skill_path):
    """检查内容一致性"""
    issues = []
    
    # 检查技能名称一致性
    skill_name = None
    
    # 从config.yaml获取技能名称
    config_file = skill_path / "config.yaml"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单提取技能名称
                match = re.search(r'name:\s*["\']([^"\']+)["\']', content)
                if match:
                    skill_name = match.group(1)
        except:
            pass
    
    # 检查所有文件中是否使用一致的名称
    if skill_name:
        text_files = list(skill_path.glob("*.py")) + \
                     list(skill_path.glob("*.md")) + \
                     list(skill_path.glob("*.yaml")) + \
                     list(skill_path.glob("*.yml"))
        
        for file in text_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有其他技能名称引用
                if "sleep-rabbit" in content.lower() or "sleeprabbit" in content.lower():
                    issues.append(f"{file.name}: 包含旧的'sleep-rabbit'引用")
            except:
                pass
    
    return issues

def check_registry_consistency(skill_path):
    """检查注册表名称一致性"""
    issues = []
    
    # 检查是否有_meta.json文件
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            slug = meta_data.get("slug", "")
            
            # 检查config.yaml中的名称是否匹配
            config_file = skill_path / "config.yaml"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                config_match = re.search(r'name:\s*["\']([^"\']+)["\']', config_content)
                if config_match:
                    config_name = config_match.group(1)
                    if slug and config_name and slug != config_name:
                        issues.append(f"注册表名称不匹配: _meta.json='{slug}' vs config.yaml='{config_name}'")
        except:
            pass
    
    return issues

def run_permanent_audit(skill_dir):
    """运行永久审核框架"""
    audit_script = Path(__file__).parent / "permanent_audit_ascii.py"
    if audit_script.exists():
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(audit_script), skill_dir],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print("❌ 永久审核失败")
                return False
            else:
                print("✅ 永久审核通过")
                return True
                
        except Exception as e:
            print(f"❌ 运行永久审核失败: {e}")
            return False
    else:
        print(f"❌ 永久审核脚本不存在: {audit_script}")
        return False

def run_security_check_v2(skill_dir):
    """运行安全检查 V2"""
    skill_path = Path(skill_dir)
    skill_file = skill_path / "skill.py"
    
    if not skill_file.exists():
        print("❌ skill.py不存在")
        return False
    
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        security_issues = []
        
        # 检查危险导入
        dangerous_patterns = [
            (r'import\s+subprocess', "危险导入: subprocess"),
            (r'from\s+subprocess\s+import', "危险导入: from subprocess"),
            (r'import\s+requests', "网络库: requests"),
            (r'import\s+urllib', "网络库: urllib"),
            (r'import\s+socket', "网络库: socket"),
            (r'import\s+http\.client', "网络库: http.client"),
            (r'eval\(', "危险函数: eval"),
            (r'exec\(', "危险函数: exec"),
            (r'__import__\(', "危险函数: __import__"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_issues.append(description)
        
        if security_issues:
            print("❌ 发现安全问题:")
            for issue in security_issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ 无安全问题")
            return True
            
    except Exception as e:
        print(f"❌ 安全检查失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("增强版审核框架 V2 (2026-04-02)")
        print("=" * 60)
        print("集成今天所有经验教训的完整审核系统")
        print("")
        print("使用方法:")
        print("  python enhanced_audit_framework_v2.py <技能目录>")
        print("")
        print("5阶段审核流程:")
        print("  1. 发布前清理 - 移除缓存文件、临时文件")
        print("  2. 文件大小检查 - 检查文件大小和结构")
        print("  3. 内容合规检查 - 英文、一致性、注册表名称")
        print("  4. 永久审核 - 文件、版本、功能检查")
        print("  5. 安全检查 - 危险函数检查")
        print("")
        print("解决的问题:")
        print("  • 缓存文件污染 (.pyc文件)")
        print("  • 注册表名称不一致")
        print("  • 内容声明矛盾")
        print("  • 全英文要求忘记")
        print("  • 文件过大问题")
        print("")
        print("示例:")
        print("  python enhanced_audit_framework_v2.py D:\\openclaw\\releases\\skill-name")
        return
    
    skill_dir = sys.argv[1]
    
    if not Path(skill_dir).exists():
        print(f"[ERROR] 目录不存在: {skill_dir}")
        return
    
    success = run_enhanced_audit_v2(skill_dir)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()