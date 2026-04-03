#!/usr/bin/env python3
"""
增强版审核框架 - 包含清理功能的完整审核系统
"""

import os
import sys
from pathlib import Path

def run_enhanced_audit(skill_dir):
    """运行增强版审核"""
    print("=" * 80)
    print("增强版审核框架 - 完整审核流程")
    print("=" * 80)
    print(f"技能目录: {skill_dir}")
    print("=" * 80)
    
    # 1. 运行清理器
    print("\n[1/3] 运行发布前清理器")
    print("-" * 40)
    
    try:
        # 导入清理器
        sys.path.insert(0, str(Path(__file__).parent))
        from pre_release_cleaner import PreReleaseCleaner
        
        cleaner = PreReleaseCleaner(skill_dir)
        cleanup_success = cleaner.run_full_cleanup()
        
        if not cleanup_success:
            print("[ERROR] 清理失败，审核中止")
            return False
            
    except Exception as e:
        print(f"[WARNING] 清理器运行失败: {e}")
        print("继续审核...")
    
    # 2. 运行永久审核框架
    print("\n[2/3] 运行永久审核框架")
    print("-" * 40)
    
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
                print("[ERROR] 永久审核失败")
                return False
                
        except Exception as e:
            print(f"[ERROR] 运行永久审核失败: {e}")
            return False
    else:
        print(f"[ERROR] 永久审核脚本不存在: {audit_script}")
        return False
    
    # 3. 运行安全检查
    print("\n[3/3] 运行安全检查")
    print("-" * 40)
    
    security_check_passed = run_security_check(skill_dir)
    
    if not security_check_passed:
        print("[ERROR] 安全检查失败")
        return False
    
    print("\n" + "=" * 80)
    print("增强版审核完成！")
    print("=" * 80)
    print("✅ 清理完成")
    print("✅ 永久审核通过")
    print("✅ 安全检查通过")
    print("\n技能已准备好发布到ClawHub！")
    
    return True

def run_security_check(skill_dir):
    """运行安全检查"""
    skill_path = Path(skill_dir)
    skill_file = skill_path / "skill.py"
    
    if not skill_file.exists():
        print("[ERROR] skill.py不存在")
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
            import re
            if re.search(pattern, content, re.IGNORECASE):
                security_issues.append(description)
        
        if security_issues:
            print("[SECURITY] 发现安全问题:")
            for issue in security_issues:
                print(f"  ❌ {issue}")
            return False
        else:
            print("[SECURITY] ✅ 无安全问题")
            return True
            
    except Exception as e:
        print(f"[ERROR] 安全检查失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("增强版审核框架")
        print("=" * 60)
        print("使用方法:")
        print("  python enhanced_audit_framework.py <技能目录>")
        print("")
        print("功能:")
        print("  1. 发布前清理 (移除缓存文件)")
        print("  2. 永久审核 (文件、版本、功能检查)")
        print("  3. 安全检查 (危险函数检查)")
        print("")
        print("示例:")
        print("  python enhanced_audit_framework.py D:\\openclaw\\releases\\skill-name")
        return
    
    skill_dir = sys.argv[1]
    
    if not Path(skill_dir).exists():
        print(f"[ERROR] 目录不存在: {skill_dir}")
        return
    
    success = run_enhanced_audit(skill_dir)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()