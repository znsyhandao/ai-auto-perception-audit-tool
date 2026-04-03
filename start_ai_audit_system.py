#!/usr/bin/env python3
"""
AI审核系统启动脚本 - 自动感知、纠错、升级的智能系统
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def main():
    """启动AI审核系统"""
    print("🚀 启动AI自进化审核系统...")
    print("=" * 60)
    
    # 检查AI系统
    ai_system_path = Path(__file__).parent / "ai_self_evolving_audit.py"
    
    if not ai_system_path.exists():
        print("❌ AI系统文件不存在，正在创建...")
        create_ai_system()
    
    # 导入AI系统
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from ai_self_evolving_audit import AISelfEvolvingAudit
        
        # 创建AI系统实例
        ai_system = AISelfEvolvingAudit()
        
        print(f"✅ AI系统加载成功")
        print(f"   版本: {ai_system.version}")
        print(f"   模式: {'学习' if ai_system.learning_mode else '执行'}")
        print(f"   自动修复: {'启用' if ai_system.auto_fix_mode else '禁用'}")
        print(f"   自动升级: {'启用' if ai_system.auto_upgrade_mode else '禁用'}")
        
        # 检查是否有技能需要审核
        if len(sys.argv) > 1:
            skill_path = sys.argv[1]
            if Path(skill_path).exists():
                print(f"\n🔍 开始审核技能: {skill_path}")
                ai_system.audit_skill(skill_path)
            else:
                print(f"❌ 技能路径不存在: {skill_path}")
        else:
            # 交互式模式
            run_interactive_mode(ai_system)
            
    except ImportError as e:
        print(f"❌ 导入AI系统失败: {e}")
        print("请确保 ai_self_evolving_audit.py 文件存在且语法正确")
        sys.exit(1)
    except Exception as e:
        print(f"❌ AI系统启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_ai_system():
    """创建AI系统"""
    print("正在创建AI自进化审核系统...")
    
    # 这里可以添加从模板创建AI系统的逻辑
    print("⚠️  需要手动创建AI系统文件")
    print("请运行: python ai_self_evolving_audit.py 来初始化系统")

def run_interactive_mode(ai_system):
    """运行交互式模式"""
    print("\n" + "=" * 60)
    print("AI自进化审核系统 - 交互式模式")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 📁 审核技能")
        print("2. 🛠️  运行每日维护")
        print("3. 📊 查看系统状态")
        print("4. 🎓 学习模式")
        print("5. 🔄 手动触发升级")
        print("6. 📝 查看经验教训")
        print("7. 🚪 退出系统")
        
        try:
            choice = input("\n请输入选项 (1-7): ").strip()
            
            if choice == "1":
                skill_path = input("请输入技能路径: ").strip()
                if skill_path and Path(skill_path).exists():
                    ai_system.audit_skill(skill_path)
                else:
                    print("❌ 路径无效或不存在")
                    
            elif choice == "2":
                print("运行每日维护...")
                ai_system.run_daily_maintenance()
                
            elif choice == "3":
                show_system_status(ai_system)
                
            elif choice == "4":
                print("进入学习模式...")
                # 这里可以添加学习模式逻辑
                print("学习模式开发中...")
                
            elif choice == "5":
                print("手动触发升级...")
                # 这里可以添加手动升级逻辑
                print("手动升级开发中...")
                
            elif choice == "6":
                show_experience_lessons(ai_system)
                
            elif choice == "7":
                print("退出AI系统...")
                break
                
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出系统")
            break
        except Exception as e:
            print(f"❌ 操作出错: {e}")

def show_system_status(ai_system):
    """显示系统状态"""
    print("\n" + "=" * 60)
    print("AI系统状态")
    print("=" * 60)
    
    print(f"🤖 系统版本: {ai_system.version}")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 知识库统计
    print(f"\n📚 知识库统计:")
    print(f"   问题模式: {len(ai_system.problem_patterns)} 个")
    print(f"   经验教训: {len(ai_system.experience_lessons)} 个")
    print(f"   框架升级: {len(ai_system.framework_upgrades)} 次")
    
    # 最近的经验教训
    recent_lessons = ai_system.experience_lessons[-3:] if ai_system.experience_lessons else []
    if recent_lessons:
        print(f"\n🎓 最近的经验教训:")
        for lesson in recent_lessons:
            print(f"   • {lesson.title} ({lesson.date_learned})")
    
    # 系统能力
    print(f"\n⚡ 系统能力:")
    print(f"   学习模式: {'✅ 启用' if ai_system.learning_mode else '❌ 禁用'}")
    print(f"   自动修复: {'✅ 启用' if ai_system.auto_fix_mode else '❌ 禁用'}")
    print(f"   自动升级: {'✅ 启用' if ai_system.auto_upgrade_mode else '❌ 禁用'}")

def show_experience_lessons(ai_system):
    """显示经验教训"""
    if not ai_system.experience_lessons:
        print("📭 暂无经验教训")
        return
    
    print("\n" + "=" * 60)
    print("经验教训库")
    print("=" * 60)
    
    # 按日期分组
    lessons_by_date = {}
    for lesson in ai_system.experience_lessons:
        date = lesson.date_learned
        if date not in lessons_by_date:
            lessons_by_date[date] = []
        lessons_by_date[date].append(lesson)
    
    # 显示最近的日期
    sorted_dates = sorted(lessons_by_date.keys(), reverse=True)
    
    for date in sorted_dates[:5]:  # 显示最近5天
        print(f"\n📅 {date}:")
        for lesson in lessons_by_date[date]:
            print(f"   • {lesson.title}")
            if lesson.confidence > 0.8:
                print(f"     置信度: {lesson.confidence:.1%} ✅")
            else:
                print(f"     置信度: {lesson.confidence:.1%} ⚠️")
    
    if len(sorted_dates) > 5:
        print(f"\n... 还有 {len(sorted_dates) - 5} 天的经验教训")

if __name__ == "__main__":
    main()