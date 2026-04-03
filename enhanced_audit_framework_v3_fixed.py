#!/usr/bin/env python3
"""
增强版审核框架 v3.0 - 修复版本
包含2026-04-03经验教训
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess


# 在调用前设置
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"
env["PYTHONUTF8"] = "1"  # 强制Python使用UTF-8模式

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='strict',  # 严格模式，发现问题就报错而不是掩盖
    env=env  # 传递环境变量
)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python enhanced_audit_framework_v3_fixed.py <技能目录>")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    
    print("=" * 60)
    print("增强版审核框架 v3.0")
    print("包含2026-04-03经验教训")
    print("=" * 60)
    
    # 运行审核
    run_audit(skill_dir)

def run_audit(skill_dir):
    """运行审核"""
    skill_path = Path(skill_dir)
    
    if not skill_path.exists():
        print(f"错误: 目录不存在: {skill_dir}")
        return
    
    print(f"审核目录: {skill_path}")
    print(f"审核时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查列表
    checks = [
        ("清理缓存文件", check_cache_files),
        ("检查必需文件", check_required_files),
        ("版本一致性检查", check_version_consistency),
        ("英文合规检查", check_english_compliance),
        ("ZIP包验证", check_zip_package),
        ("文件名版本一致性", check_filename_version_consistency)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{check_name}")
        print("-" * 40)
        
        try:
            success, message = check_func(skill_path)
            
            if success:
                print(f"通过: {message}")
                results.append((check_name, True, message))
            else:
                print(f"失败: {message}")
                results.append((check_name, False, message))
                
        except Exception as e:
            print(f"错误: {e}")
            results.append((check_name, False, f"检查出错: {e}"))
    
    # 生成报告
    generate_report(skill_path, results)

def check_cache_files(skill_path):
    """清理缓存文件"""
    import shutil
    
    cache_patterns = ["__pycache__", "*.pyc", "*.pyo"]
    cleaned = []
    
    for pattern in cache_patterns:
        for file in skill_path.rglob(pattern):
            try:
                if file.is_file():
                    file.unlink()
                    cleaned.append(str(file.relative_to(skill_path)))
                elif file.is_dir():
                    shutil.rmtree(file)
                    cleaned.append(str(file.relative_to(skill_path)))
            except:
                pass
    
    if cleaned:
        return True, f"清理了 {len(cleaned)} 个缓存文件"
    else:
        return True, "无缓存文件需要清理"

def check_required_files(skill_path):
    """检查必需文件"""
    required = ["skill.py", "SKILL.md", "README.md", "CHANGELOG.md", "requirements.txt"]
    missing = []
    
    for file in required:
        if not (skill_path / file).exists():
            missing.append(file)
    
    if missing:
        return False, f"缺少 {len(missing)} 个必需文件: {', '.join(missing)}"
    else:
        return True, f"所有 {len(required)} 个必需文件都存在"

def check_version_consistency(skill_path):
    """检查版本一致性 - 2026-04-03经验教训"""
    import re
    
    # 从skill.py提取版本
    skill_version = None
    skill_file = skill_path / "skill.py"
    
    if skill_file.exists():
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'self\.version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                skill_version = match.group(1)
        except:
            pass
    
    if not skill_version:
        return False, "无法从skill.py提取版本"
    
    # 从CHANGELOG.md提取版本
    changelog_version = None
    changelog_file = skill_path / "CHANGELOG.md"
    
    if changelog_file.exists():
        try:
            with open(changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'\[([\d.]+)\]', content)
            if match:
                changelog_version = match.group(1)
        except:
            pass
    
    # 从ZIP文件名提取版本
    zip_version = None
    zip_files = list(skill_path.glob("skill-v*.zip"))
    
    if zip_files:
        zip_file = zip_files[0]
        match = re.search(r'skill-v([\d.]+)\.zip', zip_file.name)
        if match:
            zip_version = match.group(1)
    
    # 检查一致性
    versions = {
        "skill.py": skill_version,
        "CHANGELOG.md": changelog_version,
        "ZIP文件名": zip_version
    }
    
    # 过滤None值
    actual_versions = {k: v for k, v in versions.items() if v is not None}
    
    if len(actual_versions) == 0:
        return False, "未找到任何版本信息"
    
    # 检查所有版本是否一致
    unique_versions = set(actual_versions.values())
    
    if len(unique_versions) == 1:
        version = list(unique_versions)[0]
        return True, f"所有版本一致: {version}"
    else:
        return False, f"版本不一致: {actual_versions}"

def check_english_compliance(skill_path):
    """检查英文合规性 - 2026-04-03经验教训"""
    import re
    
    # 核心文件列表（必须100%英文）
    core_files = [
        "skill.py",
        "SKILL.md",
        "README.md",
        "CHANGELOG.md",
        "requirements.txt",
        "config.yaml"
    ]
    
    issues = []
    
    for filename in core_files:
        filepath = skill_path / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查中文字符
                chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
                if chinese_chars:
                    issues.append(f"{filename}: {len(chinese_chars)} 个中文字符")
            except:
                issues.append(f"{filename}: 无法读取")
    
    if not issues:
        return True, f"所有 {len(core_files)} 个核心文件100%英文"
    else:
        return False, f"{len(issues)} 个核心文件包含中文"

def check_zip_package(skill_path):
    """ZIP包验证"""
    import zipfile
    
    zip_files = list(skill_path.glob("skill-v*.zip"))
    
    if not zip_files:
        return False, "未找到skill-v*.zip文件"
    
    zip_file = zip_files[0]
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zf:
            files_in_zip = zf.namelist()
        
        # 必需文件
        required = ["skill.py", "SKILL.md", "README.md", "CHANGELOG.md", "requirements.txt"]
        missing = []
        
        for req_file in required:
            if req_file not in files_in_zip:
                missing.append(req_file)
        
        if missing:
            return False, f"ZIP包缺少文件: {', '.join(missing)}"
        else:
            return True, f"ZIP包完整: {zip_file.name} ({len(files_in_zip)} 个文件)"
            
    except Exception as e:
        return False, f"ZIP包检查出错: {e}"

def check_filename_version_consistency(skill_path):
    """文件名版本一致性检查 - 2026-04-03关键经验教训"""
    import re
    
    # 从skill.py提取版本
    skill_version = None
    skill_file = skill_path / "skill.py"
    
    if skill_file.exists():
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'self\.version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                skill_version = match.group(1)
        except:
            pass
    
    if not skill_version:
        return False, "无法从skill.py提取版本"
    
    # 检查ZIP文件名
    expected_name = f"skill-v{skill_version}.zip"
    zip_files = list(skill_path.glob("skill-v*.zip"))
    
    if not zip_files:
        return False, f"未找到ZIP文件，期望: {expected_name}"
    
    actual_name = zip_files[0].name
    
    if actual_name == expected_name:
        return True, f"ZIP文件名正确: {actual_name}"
    else:
        return False, f"ZIP文件名不匹配: 期望 {expected_name}, 实际 {actual_name}"

def generate_report(skill_path, results):
    """生成审核报告"""
    print("\n" + "=" * 60)
    print("审核报告")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"通过检查: {passed}/{total}")
    print(f"失败检查: {total - passed}/{total}")
    
    if passed == total:
        print("\n所有检查通过！技能已准备好发布。")
    else:
        print("\n发现的问题:")
        for check_name, success, message in results:
            if not success:
                print(f"  • {check_name}: {message}")
    
    # 保存报告
    report_data = {
        "audit_date": datetime.now().isoformat(),
        "skill_directory": str(skill_path),
        "results": [
            {
                "check_name": name,
                "success": success,
                "message": message
            }
            for name, success, message in results
        ],
        "summary": {
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": total - passed
        }
    }
    
    report_path = skill_path / "enhanced_audit_v3_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n审核报告已保存: {report_path}")

if __name__ == "__main__":
    main()