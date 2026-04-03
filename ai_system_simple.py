#!/usr/bin/env python3
"""
AI系统简单启动器 - 无emoji版本
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    """主函数"""
    print("=" * 60)
    print("AI自动感知纠错升级审核框架")
    print("=" * 60)
    
    # 显示选项
    print("\n请选择操作:")
    print("1. 审核专业睡眠分析技能 (v1.1.0)")
    print("2. 运行增强版审核框架 v3.0")
    print("3. 运行发布前清理器 v2.0")
    print("4. 查看2026-04-03经验教训")
    print("5. 检查今天的记忆文件")
    print("6. 退出")
    
    choice = input("\n请输入选项 (1-6): ").strip()
    
    if choice == "1":
        audit_professional_sleep_analyzer()
    elif choice == "2":
        run_enhanced_audit_framework()
    elif choice == "3":
        run_pre_release_cleaner()
    elif choice == "4":
        show_20260403_lessons()
    elif choice == "5":
        check_todays_memory()
    elif choice == "6":
        print("退出系统")
    else:
        print("无效选项")

def audit_professional_sleep_analyzer():
    """审核专业睡眠分析技能"""
    skill_path = r"D:\openclaw\releases\professional-sleep-analyzer"
    
    if not Path(skill_path).exists():
        print(f"错误: 技能路径不存在: {skill_path}")
        return
    
    print(f"\n开始审核专业睡眠分析技能 v1.1.0")
    print(f"路径: {skill_path}")
    
    # 1. 运行增强版审核框架
    print("\n1. 运行增强版审核框架 v3.0")
    framework_path = Path(__file__).parent / "enhanced_audit_framework_v3.py"
    
    if framework_path.exists():
        cmd = f'python "{framework_path}" "{skill_path}"'
        run_command(cmd, "增强版审核框架")
    else:
        print(f"警告: 增强版审核框架 v3.0 不存在")
    
    # 2. 运行发布前清理器
    print("\n2. 运行发布前清理器 v2.0")
    cleaner_path = Path(__file__).parent / "pre_release_cleaner_v2.py"
    
    if cleaner_path.exists():
        cmd = f'python "{cleaner_path}" "{skill_path}"'
        run_command(cmd, "发布前清理器")
    else:
        print(f"警告: 发布前清理器 v2.0 不存在")
    
    # 3. 检查ZIP文件
    print("\n3. 检查ZIP文件")
    zip_file = Path(skill_path) / "skill-v1.1.0.zip"
    
    if zip_file.exists():
        print(f"找到ZIP文件: {zip_file.name}")
        
        # 检查ZIP内容
        try:
            import zipfile
            with zipfile.ZipFile(zip_file, 'r') as zf:
                files = zf.namelist()
                print(f"ZIP包含 {len(files)} 个文件:")
                for file in files:
                    print(f"  - {file}")
        except Exception as e:
            print(f"检查ZIP文件失败: {e}")
    else:
        print(f"警告: ZIP文件不存在: {zip_file.name}")

def run_enhanced_audit_framework():
    """运行增强版审核框架"""
    framework_path = Path(__file__).parent / "enhanced_audit_framework_v3.py"
    
    if not framework_path.exists():
        print(f"错误: 增强版审核框架 v3.0 不存在: {framework_path}")
        return
    
    skill_path = input("请输入技能路径: ").strip()
    if not skill_path:
        print("错误: 未提供技能路径")
        return
    
    if not Path(skill_path).exists():
        print(f"错误: 技能路径不存在: {skill_path}")
        return
    
    cmd = f'python "{framework_path}" "{skill_path}"'
    run_command(cmd, "增强版审核框架")

def run_pre_release_cleaner():
    """运行发布前清理器"""
    cleaner_path = Path(__file__).parent / "pre_release_cleaner_v2.py"
    
    if not cleaner_path.exists():
        print(f"错误: 发布前清理器 v2.0 不存在: {cleaner_path}")
        return
    
    skill_path = input("请输入技能路径: ").strip()
    if not skill_path:
        print("错误: 未提供技能路径")
        return
    
    if not Path(skill_path).exists():
        print(f"错误: 技能路径不存在: {skill_path}")
        return
    
    cmd = f'python "{cleaner_path}" "{skill_path}"'
    run_command(cmd, "发布前清理器")

def run_command(cmd, description):
    """运行命令"""
    print(f"运行: {description}")
    print(f"命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print(f"标准错误: {result.stderr}")
    except Exception as e:
        print(f"运行失败: {e}")

def show_20260403_lessons():
    """显示2026-04-03经验教训"""
    print("\n" + "=" * 60)
    print("2026-04-03 经验教训总结")
    print("=" * 60)
    
    lessons = [
        {
            "title": "版本一致性必须包括ZIP文件名",
            "problem": "ZIP文件名使用旧版本号 (skill-v1.0.0.zip)，技能内容是新版本 (v1.1.0)",
            "solution": "创建ZIP包前验证所有版本来源一致性，确保文件名与版本匹配",
            "tools_updated": [
                "enhanced_audit_framework_v3.py",
                "pre_release_cleaner_v2.py",
                "permanent_audit_ascii_v2.py"
            ]
        },
        {
            "title": "区分核心文件和临时文件",
            "problem": "审核脚本包含中文，被误认为是核心文件问题",
            "solution": "明确区分核心文件（必须100%英文）和临时文件（可含中文）",
            "tools_updated": [
                "enhanced_audit_framework_v3.py",
                "pre_release_cleaner_v2.py"
            ]
        },
        {
            "title": "AI自动感知纠错升级",
            "problem": "每次发现问题都需要手动告诉你升级框架",
            "solution": "AI自动学习经验教训，自动升级相关工具，自动验证升级结果",
            "tools_updated": [
                "ai_self_evolving_audit.py",
                "ai_audit_daemon.py",
                "start_ai_audit_system.py"
            ]
        }
    ]
    
    for i, lesson in enumerate(lessons, 1):
        print(f"\n{i}. {lesson['title']}")
        print(f"   问题: {lesson['problem']}")
        print(f"   解决方案: {lesson['solution']}")
        print(f"   更新的工具: {', '.join(lesson['tools_updated'])}")
    
    print(f"\n这些经验教训已经集成到AI审核框架中")

def check_todays_memory():
    """检查今天的记忆文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = Path.home() / ".openclaw" / "workspace" / f"memory/{today}.md"
    
    if memory_file.exists():
        print(f"\n找到今天的记忆文件: {memory_file}")
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取经验教训
            import re
            pattern = r'/remember\s+(.+?)(?=\n/remember|\n##|\n#|$)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            if matches:
                print(f"发现 {len(matches)} 个经验教训:")
                for i, match in enumerate(matches, 1):
                    lesson = match.strip()
                    lines = lesson.split('\n')
                    title = lines[0].strip()[:80]
                    print(f"  {i}. {title}")
            else:
                print("没有找到经验教训 (/remember)")
                
        except Exception as e:
            print(f"读取记忆文件失败: {e}")
    else:
        print(f"\n今天的记忆文件不存在: {memory_file}")

if __name__ == "__main__":
    main()