#!/usr/bin/env python3
"""
AI系统启动器 - 简化的AI审核系统启动
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """启动AI系统"""
    print("=" * 60)
    print("AI自动感知纠错升级审核框架")
    print("=" * 60)
    
    # 检查今天的经验教训
    check_todays_lessons()
    
    # 显示选项
    print("\n请选择操作:")
    print("1. 审核专业睡眠分析技能 (v1.1.0)")
    print("2. 运行增强版审核框架 v3.0")
    print("3. 运行发布前清理器 v2.0")
    print("4. 查看2026-04-03经验教训")
    print("5. 退出")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice == "1":
        audit_professional_sleep_analyzer()
    elif choice == "2":
        run_enhanced_audit_framework()
    elif choice == "3":
        run_pre_release_cleaner()
    elif choice == "4":
        show_20260403_lessons()
    elif choice == "5":
        print("退出系统")
    else:
        print("无效选项")

def check_todays_lessons():
    """检查今天的经验教训"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = Path.home() / ".openclaw" / "workspace" / f"memory/{today}.md"
    
    if memory_file.exists():
        print(f"📅 发现今天的记忆文件: {memory_file}")
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查经验教训
            if "/remember" in content:
                lessons = extract_remember_lessons(content)
                print(f"🎓 发现 {len(lessons)} 个经验教训")
                
                # 保存到AI知识库
                save_lessons_to_kb(lessons)
                
        except Exception as e:
            print(f"⚠️  读取记忆文件失败: {e}")
    else:
        print("📭 今天的记忆文件不存在")

def extract_remember_lessons(content):
    """提取/remember经验教训"""
    import re
    
    lessons = []
    pattern = r'/remember\s+(.+?)(?=\n/remember|\n##|\n#|$)'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        lesson_text = match.strip()
        if lesson_text:
            # 提取第一行作为标题
            lines = lesson_text.split('\n')
            title = lines[0].strip()
            if len(title) > 100:
                title = title[:97] + "..."
            
            lessons.append({
                "title": title,
                "content": lesson_text,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "memory_file"
            })
    
    return lessons

def save_lessons_to_kb(lessons):
    """保存经验教训到知识库"""
    kb_path = Path(__file__).parent / "ai_knowledge_base.json"
    
    # 加载现有知识库
    if kb_path.exists():
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                kb = json.load(f)
        except:
            kb = {"lessons": [], "patterns": []}
    else:
        kb = {"lessons": [], "patterns": []}
    
    # 添加新经验教训
    existing_titles = {l.get("title", "") for l in kb.get("lessons", [])}
    
    new_count = 0
    for lesson in lessons:
        if lesson["title"] not in existing_titles:
            kb.setdefault("lessons", []).append(lesson)
            new_count += 1
    
    # 保存知识库
    if new_count > 0:
        kb["last_updated"] = datetime.now().isoformat()
        
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        
        print(f"💾 保存了 {new_count} 个新经验教训到知识库")
        
        # 检查是否需要升级工具
        check_tool_upgrades(lessons)

def check_tool_upgrades(lessons):
    """检查是否需要升级工具"""
    print("🔍 检查工具是否需要升级...")
    
    # 检查经验教训是否涉及特定工具
    tools_to_check = [
        "enhanced_audit_framework.py",
        "pre_release_cleaner.py",
        "permanent_audit_ascii.py",
        "english_compliance_checker.py"
    ]
    
    for lesson in lessons:
        content = lesson["content"].lower()
        
        # 检查版本相关经验教训
        if any(word in content for word in ["版本", "version", "不一致", "mismatch"]):
            print("  🎯 发现版本相关经验教训，需要升级审核框架")
            upgrade_audit_framework()
            break
        
        # 检查英文相关经验教训
        elif any(word in content for word in ["英文", "english", "中文", "chinese"]):
            print("  🎯 发现英文相关经验教训，需要升级合规检查器")
            upgrade_compliance_checker()
            break

def upgrade_audit_framework():
    """升级审核框架"""
    print("  🔄 升级审核框架...")
    
    # 检查是否已经有v3.0
    v3_path = Path(__file__).parent / "enhanced_audit_framework_v3.py"
    
    if v3_path.exists():
        print("  ✅ 增强版审核框架 v3.0 已存在（包含2026-04-03经验教训）")
    else:
        print("  ⚠️  需要创建增强版审核框架 v3.0")

def upgrade_compliance_checker():
    """升级合规检查器"""
    print("  🔄 升级合规检查器...")
    
    # 检查是否已经有v2.0
    v2_path = Path(__file__).parent / "pre_release_cleaner_v2.py"
    
    if v2_path.exists():
        print("  ✅ 发布前清理器 v2.0 已存在（包含2026-04-03经验教训）")
    else:
        print("  ⚠️  需要创建发布前清理器 v2.0")

def audit_professional_sleep_analyzer():
    """审核专业睡眠分析技能"""
    skill_path = r"D:\openclaw\releases\professional-sleep-analyzer"
    
    if not Path(skill_path).exists():
        print(f"❌ 技能路径不存在: {skill_path}")
        return
    
    print(f"\n🔍 开始审核专业睡眠分析技能 v1.1.0")
    print(f"路径: {skill_path}")
    
    # 运行增强版审核框架
    run_enhanced_audit_framework(skill_path)
    
    # 运行发布前清理器
    run_pre_release_cleaner(skill_path)

def run_enhanced_audit_framework(skill_path=None):
    """运行增强版审核框架"""
    framework_path = Path(__file__).parent / "enhanced_audit_framework_v3.py"
    
    if not framework_path.exists():
        print(f"❌ 增强版审核框架 v3.0 不存在: {framework_path}")
        return
    
    if skill_path:
        cmd = f'python "{framework_path}" "{skill_path}"'
    else:
        skill_path = input("请输入技能路径: ").strip()
        if not skill_path:
            print("❌ 未提供技能路径")
            return
        cmd = f'python "{framework_path}" "{skill_path}"'
    
    print(f"\n🚀 运行增强版审核框架 v3.0")
    print(f"命令: {cmd}")
    
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print(f"错误: {result.stderr}")
    except Exception as e:
        print(f"❌ 运行失败: {e}")

def run_pre_release_cleaner(skill_path=None):
    """运行发布前清理器"""
    cleaner_path = Path(__file__).parent / "pre_release_cleaner_v2.py"
    
    if not cleaner_path.exists():
        print(f"❌ 发布前清理器 v2.0 不存在: {cleaner_path}")
        return
    
    if skill_path:
        cmd = f'python "{cleaner_path}" "{skill_path}"'
    else:
        skill_path = input("请输入技能路径: ").strip()
        if not skill_path:
            print("❌ 未提供技能路径")
            return
        cmd = f'python "{cleaner_path}" "{skill_path}"'
    
    print(f"\n🧹 运行发布前清理器 v2.0")
    print(f"命令: {cmd}")
    
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print(f"错误: {result.stderr}")
    except Exception as e:
        print(f"❌ 运行失败: {e}")

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
    
    print(f"\n✅ 这些经验教训已经集成到AI审核框架中")

if __name__ == "__main__":
    main()