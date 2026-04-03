#!/usr/bin/env python3
"""
OpenClaw技能审核工具 v2.0 - 集成基础学习功能
自动化执行重复性审核任务，支持从对话中学习经验
"""

import os
import sys
import subprocess
from pathlib import Path

# 尝试导入学习模块
try:
    from conversation_learner import ConversationLearner
    HAS_LEARNING = True
except ImportError:
    HAS_LEARNING = False
    print("⚠️  注意：对话学习模块未找到，学习功能不可用")

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw技能审核工具 v2.0")
    print("功能：自动化检查 + 基础学习能力")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == "audit" and len(sys.argv) > 2:
        audit_skill(sys.argv[2])
    elif command == "security" and len(sys.argv) > 2:
        security_check(sys.argv[2])
    elif command == "clean" and len(sys.argv) > 2:
        check_cache_files(sys.argv[2])
    elif command == "learn":
        if HAS_LEARNING:
            run_learning()
        else:
            print("❌ 学习功能不可用，请确保 conversation_learner.py 存在")
    elif command == "stats":
        if HAS_LEARNING:
            show_learning_stats()
        else:
            print("❌ 学习功能不可用")
    elif command == "help":
        show_help()
    elif command == "version":
        show_version()
    else:
        print(f"未知命令: {command}")
        show_help()

def show_help():
    """显示帮助"""
    print("\n使用方法:")
    print("  python skill_audit_v2.py audit <路径>    - 综合审核技能")
    print("  python skill_audit_v2.py security <路径> - 安全检查")
    print("  python skill_audit_v2.py clean <路径>    - 检查缓存文件")
    if HAS_LEARNING:
        print("  python skill_audit_v2.py learn          - 交互式学习")
        print("  python skill_audit_v2.py stats          - 显示学习统计")
    print("  python skill_audit_v2.py version         - 显示版本")
    print("  python skill_audit_v2.py help            - 显示帮助")
    
    print("\n学习功能说明:")
    if HAS_LEARNING:
        print("  ✅ 支持从对话中提取经验教训")
        print("  ✅ 支持半自动更新知识库")
        print("  ✅ 支持基于经验生成审核规则")
    else:
        print("  ❌ 学习功能当前不可用")
    
    print("\n学习格式示例:")
    print('  /learn 版本号必须更新 | 版本管理')
    print('  记住这个经验：缓存文件必须清理')
    print('  经验教训：文档必须100%英文')
    
    print("\n限制说明:")
    print("  • 学习功能是基础的，不是真正的AI")
    print("  • 需要特定格式的输入")
    print("  • 生成的规则可能不完善")

def show_version():
    """显示版本信息"""
    print("\n版本信息:")
    print("  OpenClaw技能审核工具 v2.0")
    print("  发布日期: 2026-04-03")
    print("  许可证: MIT")
    print("  仓库: https://github.com/znsyhandao/ai-auto-perception-audit-tool")
    
    print("\n包含的功能:")
    print("  ✓ 版本一致性检查")
    print("  ✓ 文档完整性检查")
    print("  ✓ 英文合规性检查")
    print("  ✓ 安全模式检查")
    print("  ✓ 缓存文件检查")
    print("  ✓ 功能测试验证")
    
    if HAS_LEARNING:
        print("  ✓ 基础对话学习功能")
    else:
        print("  ✗ 对话学习功能（未启用）")
    
    print("\n学习能力说明:")
    print("  • 可以：从特定格式对话中提取经验")
    print("  • 可以：半自动更新知识库")
    print("  • 不能：理解自然语言对话")
    print("  • 不能：自动进化审核规则")
    print("  • 不是：真正的AI学习系统")

def run_learning():
    """运行学习功能"""
    if not HAS_LEARNING:
        print("❌ 学习模块未找到")
        return
    
    print("\n" + "=" * 60)
    print("对话学习模式")
    print("=" * 60)
    print("\n请输入对话文本（使用特定格式）：")
    print("示例格式:")
    print('  /learn 版本号必须更新 | 版本管理')
    print('  记住这个经验：缓存文件必须清理')
    print('  经验教训：ZIP文件名必须匹配版本号')
    print("\n输入空行结束：")
    
    learner = ConversationLearner()
    learner.interactive_learning()

def show_learning_stats():
    """显示学习统计"""
    if not HAS_LEARNING:
        print("❌ 学习模块未找到")
        return
    
    learner = ConversationLearner()
    learner.show_statistics()

def audit_skill(skill_path):
    """综合审核技能"""
    print(f"\n开始审核: {skill_path}")
    print("-" * 60)
    
    # 1. 基础审核框架
    print("\n1. 运行基础审核...")
    run_tool("permanent_audit_ascii.py", skill_path)
    
    # 2. 增强审核
    print("\n2. 运行增强审核...")
    run_tool("enhanced_audit_framework_v3_fixed.py", skill_path)
    
    # 3. 安全检查
    print("\n3. 运行安全检查...")
    security_check(skill_path)
    
    # 4. 缓存检查
    print("\n4. 检查缓存文件...")
    check_cache_files(skill_path)
    
    print("\n" + "-" * 60)
    print("审核完成！")
    print("生成的报告:")
    print("  • permanent_audit_report.json")
    print("  • enhanced_audit_v3_report.json")
    print("  • security_audit_report.json")
    print("  • cache_check_report.json")
    
    # 5. 学习机会
    if HAS_LEARNING:
        print("\n💡 学习机会:")
        print("  如果审核中发现新问题，可以使用:")
        print("    python skill_audit_v2.py learn")
        print("  来记录经验教训")

def security_check(skill_path):
    """安全检查"""
    print("运行安全检查...")
    run_tool("security_pattern_detector.py", skill_path)

def check_cache_files(skill_path):
    """检查缓存文件"""
    print("检查缓存文件...")
    run_tool("pre_release_cleaner.py", skill_path, check_only=True)

def run_tool(tool_name, skill_path, check_only=False):
    """运行指定的工具"""
    tool_path = Path(tool_name)
    if not tool_path.exists():
        print(f"  ❌ 工具未找到: {tool_name}")
        return
    
    try:
        cmd = [sys.executable, tool_name, skill_path]
        if check_only:
            cmd.append("--check-only")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='gbk',  # Windows中文系统使用gbk
            errors='replace'  # 遇到无法解码的字符时替换为�而不是崩溃
        )
        
        # 显示简要输出
        lines = result.stdout.split('\n')
        for line in lines[:10]:  # 只显示前10行
            if line.strip():
                print(f"  {line}")
        
        if len(lines) > 10:
            print(f"  ... 还有 {len(lines)-10} 行输出")
        
        if result.returncode != 0:
            print(f"  ⚠️  工具返回错误码: {result.returncode}")
            
    except Exception as e:
        print(f"  ❌ 运行工具失败: {e}")

if __name__ == "__main__":
    main()