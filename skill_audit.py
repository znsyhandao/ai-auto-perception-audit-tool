#!/usr/bin/env python3
"""
OpenClaw技能审核工具 - 诚实版本
自动化执行重复性审核任务，节省时间，减少错误
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw技能审核工具 v1.0")
    print("功能：自动化检查，节省时间，减少错误")
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
    print("  python skill_audit.py audit <路径>    - 综合审核技能")
    print("  python skill_audit.py security <路径> - 安全检查")
    print("  python skill_audit.py clean <路径>    - 检查缓存文件")
    print("  python skill_audit.py version         - 显示版本")
    print("  python skill_audit.py help            - 显示帮助")
    print("\n示例:")
    print('  python skill_audit.py audit "D:\\openclaw\\releases\\skill"')
    print("\n功能说明:")
    print("  • 审核：检查版本、文档、功能等")
    print("  • 安全：检查SQL注入、硬编码密钥等")
    print("  • 清理：检查.pyc和__pycache__文件")
    print("\n限制说明:")
    print("  • 这是自动化工具，不是AI系统")
    print("  • 需要手动更新检查规则")
    print("  • 不能预测未知问题")

def show_version():
    """显示版本信息"""
    print("\n版本信息:")
    print("  OpenClaw技能审核工具 v1.0")
    print("  发布日期: 2026-04-03")
    print("  许可证: MIT")
    print("  仓库: https://github.com/znsyhandao/ai-auto-perception-audit-tool")
    print("\n包含的检查:")
    print("  ✓ 版本一致性检查")
    print("  ✓ 文档完整性检查")
    print("  ✓ 英文合规性检查")
    print("  ✓ 安全模式检查")
    print("  ✓ 缓存文件检查")
    print("  ✓ 功能测试验证")

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
            encoding='utf-8'
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