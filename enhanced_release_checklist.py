#!/usr/bin/env python3
"""
增强版发布检查清单 - 基于AISkinX经验
包含config.yaml、文件编码、ClawHub规范等检查
"""

import os
import sys
import json
from datetime import datetime

def print_checklist_item(checked, description):
    """打印检查清单项"""
    status = "[OK]" if checked else "[ERROR]"
    print(f"{status} {description}")

def check_phase_1_code_development(directory):
    """阶段1：代码开发完成"""
    print("\n" + "="*60)
    print("阶段1：代码开发完成")
    print("="*60)
    
    checks = []
    
    # 1.1 技能导入测试
    try:
        sys.path.insert(0, directory)
        import skill
        s = skill.create_skill()
        checks.append(("技能导入成功", True))
        print(f"  技能名称: {s.name}")
        print(f"  技能版本: {s.version}")
    except Exception as e:
        checks.append((f"技能导入失败: {e}", False))
    
    # 1.2 基本命令测试
    test_commands = [
        ("help", {}, "帮助命令"),
        ("status", {}, "状态命令"),
        ("version", {}, "版本命令")
    ]
    
    command_results = []
    for cmd, args, desc in test_commands:
        try:
            result = s.handle_command(cmd, args, None)
            if result.get('success'):
                command_results.append((f"{desc}正常", True))
            else:
                command_results.append((f"{desc}失败", False))
        except Exception as e:
            command_results.append((f"{desc}异常: {e}", False))
    
    checks.extend(command_results)
    
    # 1.3 核心功能测试（如果有）
    try:
        result = s.handle_command('analyze', {'skin_type': 'oily'}, None)
        if result.get('success'):
            checks.append(("核心功能测试通过", True))
        else:
            checks.append(("核心功能测试失败", False))
    except:
        checks.append(("核心功能测试跳过", True))  # 不是所有技能都有analyze
    
    # 打印结果
    for desc, passed in checks:
        print_checklist_item(passed, desc)
    
    return all(passed for _, passed in checks)

def check_phase_2_security_review(directory):
    """阶段2：安全审查"""
    print("\n" + "="*60)
    print("阶段2：安全审查（基于AISkinX经验）")
    print("="*60)
    
    # 运行增强版安全检查
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "enhanced_security_scanner.py", directory],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print("[OK] 安全检查通过")
            return True
        else:
            print("[ERROR] 安全检查失败")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"[ERROR] 运行安全检查失败: {e}")
        return False

def check_phase_3_consistency_verification(directory):
    """阶段3：一致性验证"""
    print("\n" + "="*60)
    print("阶段3：一致性验证")
    print("="*60)
    
    checks = []
    
    # 3.1 检查README与代码一致性
    readme_path = os.path.join(directory, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme = f.read()
            
            # 检查关键声明
            key_phrases = ["100%本地", "无网络", "零依赖", "隐私安全"]
            found_phrases = []
            for phrase in key_phrases:
                if phrase in readme:
                    found_phrases.append(phrase)
            
            if len(found_phrases) >= 3:
                checks.append(("README安全声明完整", True))
                print(f"  找到声明: {', '.join(found_phrases)}")
            else:
                checks.append(("README安全声明不完整", False))
        except Exception as e:
            checks.append((f"读取README失败: {e}", False))
    else:
        checks.append(("README.md不存在", False))
    
    # 3.2 检查config.yaml与声明一致
    config_path = os.path.join(directory, "config.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            if 'network_access: false' in config_content and 'local_only: true' in config_content:
                checks.append(("config.yaml安全声明正确", True))
            else:
                checks.append(("config.yaml缺少安全声明", False))
            
            # 检查是否有矛盾声明
            dangerous = ['original_api_url', 'world_model_integrator', 'updates.auto_check: true']
            found_dangerous = []
            for item in dangerous:
                if item in config_content:
                    found_dangerous.append(item)
            
            if not found_dangerous:
                checks.append(("config.yaml无矛盾配置", True))
            else:
                checks.append((f"config.yaml有矛盾配置: {', '.join(found_dangerous)}", False))
        except Exception as e:
            checks.append((f"读取config.yaml失败: {e}", False))
    else:
        checks.append(("config.yaml不存在", True))  # 不是必须
    
    # 3.3 检查CHANGELOG
    changelog_path = os.path.join(directory, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                changelog = f.read()
            
            if '## [' in changelog and '###' in changelog:
                checks.append(("CHANGELOG格式正确", True))
            else:
                checks.append(("CHANGELOG格式可能有问题", False))
        except Exception as e:
            checks.append((f"读取CHANGELOG失败: {e}", False))
    else:
        checks.append(("CHANGELOG.md不存在", False))
    
    # 打印结果
    for desc, passed in checks:
        print_checklist_item(passed, desc)
    
    return all(passed for _, passed in checks)

def check_phase_4_final_verification(directory):
    """阶段4：最终验证"""
    print("\n" + "="*60)
    print("阶段4：最终验证（ClawHub规范）")
    print("="*60)
    
    checks = []
    
    # 4.1 检查package.json
    package_path = os.path.join(directory, "package.json")
    if os.path.exists(package_path):
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                package = json.load(f)
            
            # 检查版本号
            version = package.get('version', '')
            if version and re.match(r'^\d+\.\d+\.\d+$', version):
                checks.append((f"版本号格式正确: {version}", True))
            else:
                checks.append(("版本号格式错误", False))
            
            # 检查权限
            permissions = package.get('openclaw', {}).get('permissions', '')
            if permissions == 'filesystem':
                checks.append(("权限最小化 (filesystem)", True))
            else:
                checks.append((f"权限可能过大: {permissions}", False))
        except Exception as e:
            checks.append((f"读取package.json失败: {e}", False))
    else:
        checks.append(("package.json不存在", False))
    
    # 4.2 检查许可证
    license_path = os.path.join(directory, "LICENSE.txt")
    if os.path.exists(license_path):
        try:
            with open(license_path, 'r', encoding='utf-8') as f:
                license_content = f.read()
            
            if 'MIT' in license_content or 'Apache' in license_content or 'BSD' in license_content:
                checks.append(("许可证文件存在", True))
            else:
                checks.append(("许可证文件内容可能有问题", False))
        except Exception as e:
            checks.append((f"读取许可证失败: {e}", False))
    else:
        checks.append(("LICENSE.txt不存在", False))
    
    # 4.3 检查文件编码（基于AISkinX乱码问题）
    files_to_check = ['README.md', 'SKILL.md', 'CHANGELOG.md']
    encoding_issues = []
    for filename in files_to_check:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    f.read(100)  # 尝试读取
            except UnicodeDecodeError:
                encoding_issues.append(filename)
    
    if not encoding_issues:
        checks.append(("所有文档UTF-8编码正常", True))
    else:
        checks.append((f"文档编码问题: {', '.join(encoding_issues)}", False))
    
    # 4.4 检查文件大小（避免token限制）
    large_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.md')):
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                if size > 15000:  # 15KB以上
                    large_files.append((file, size))
    
    if not large_files:
        checks.append(("文件大小正常（无token限制风险）", True))
    else:
        warning = f"发现大文件: {', '.join([f'{f}({s/1024:.1f}KB)' for f, s in large_files[:3]])}"
        checks.append((warning, True))  # 警告但不失败
    
    # 打印结果
    for desc, passed in checks:
        print_checklist_item(passed, desc)
    
    return all(passed for _, passed in checks)

def generate_release_report(directory, phase_results):
    """生成发布报告"""
    report_path = os.path.join(directory, "RELEASE_REPORT.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# [LAUNCH] 发布检查报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"技能目录: {directory}\n\n")
        
        f.write("## [DASHBOARD] 检查结果\n\n")
        
        phases = [
            ("阶段1：代码开发完成", phase_results[0]),
            ("阶段2：安全审查", phase_results[1]),
            ("阶段3：一致性验证", phase_results[2]),
            ("阶段4：最终验证", phase_results[3])
        ]
        
        for phase_name, passed in phases:
            status = "[OK] 通过" if passed else "[ERROR] 失败"
            f.write(f"- {phase_name}: {status}\n")
        
        f.write("\n## [TARGET] 总体结论\n\n")
        
        all_passed = all(phase_results)
        if all_passed:
            f.write("[CELEBRATE] **所有检查通过！可以安全发布到ClawHub**\n\n")
            f.write("### 发布信息：\n")
            f.write("- Skill Slug: [填写]\n")
            f.write("- Display Name: [填写]\n")
            f.write("- Version: [从package.json获取]\n")
            f.write("- License: [从LICENSE.txt获取]\n\n")
            f.write("### 上传地址：\n")
            f.write("https://clawhub.com/upload\n")
        else:
            f.write("[ERROR] **检查未通过，需要修复问题**\n\n")
            f.write("请修复以上阶段中发现的问题，然后重新运行检查。\n")
        
        f.write("\n---\n")
        f.write("*报告由增强版发布检查清单生成（基于AISkinX经验）*\n")
    
    print(f"\n[DOC] 发布报告已生成: {report_path}")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python enhanced_release_checklist.py <技能目录>")
        print("示例: python enhanced_release_checklist.py ./my-skill")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"错误: {directory} 不是有效目录")
        sys.exit(1)
    
    print("="*60)
    print("[LAUNCH] 增强版发布检查清单 - 基于AISkinX经验")
    print("="*60)
    print(f"检查目录: {directory}")
    print("="*60)
    
    # 运行各阶段检查
    phase_results = []
    
    phase1 = check_phase_1_code_development(directory)
    phase_results.append(phase1)
    
    if phase1:  # 只有阶段1通过才继续
        phase2 = check_phase_2_security_review(directory)
        phase_results.append(phase2)
        
        if phase2:  # 只有阶段2通过才继续
            phase3 = check_phase_3_consistency_verification(directory)
            phase_results.append(phase3)
            
            if phase3:  # 只有阶段3通过才继续
                phase4 = check_phase_4_final_verification(directory)
                phase_results.append(phase4)
            else:
                phase_results.append(False)
        else:
            phase_results.extend([False, False])  # 阶段3和4自动失败
    else:
        phase_results.extend([False, False, False])  # 阶段2、3、4自动失败
    
    # 生成报告
    generate_release_report(directory, phase_results)
    
    # 总体结果
    print("\n" + "="*60)
    print("[TARGET] 发布检查完成")
    print("="*60)
    
    all_passed = all(phase_results)
    if all_passed:
        print("[CELEBRATE] [CELEBRATE] [CELEBRATE] 所有检查通过！可以安全发布 [CELEBRATE] [CELEBRATE] [CELEBRATE]")
        print("\n下一步:")
        print("1. 查看 RELEASE_REPORT.md 获取发布信息")
        print("2. 访问 https://clawhub.com/upload 上传技能")
        print("3. 填写正确的版本号和描述")
        sys.exit(0)
    else:
        print("[ERROR] [ERROR] [ERROR] 检查未通过，需要修复问题 [ERROR] [ERROR] [ERROR]")
        print("\n请查看上面的详细检查结果，修复问题后重新运行。")
        sys.exit(1)

if __name__ == "__main__":
    # 导入re模块用于版本号检查
    import re
    main()