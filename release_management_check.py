#!/usr/bin/env python3
"""
发布管理检查工具
基于2026-03-29 AISleepGen发布管理教训
集成到永久审核框架
"""

import os
import re
import json
import shutil
from pathlib import Path

def check_release_structure(skill_dir):
    """检查发布文件夹结构"""
    print("=== Release Structure Check ===")
    
    issues = []
    checks_passed = 0
    total_checks = 0
    
    # 检查1: 没有重复的latest文件夹
    total_checks += 1
    latest_dir = os.path.join(skill_dir, "latest")
    if os.path.exists(latest_dir) and os.path.isdir(latest_dir):
        print("[FAIL] Found 'latest' folder (should not exist in source)")
        print("  Reason: 'latest' should only exist in release directory, not source")
        issues.append("Source contains 'latest' folder (release management issue)")
    else:
        print("[OK] No 'latest' folder in source")
        checks_passed += 1
    
    # 检查2: 没有备份文件混入
    total_checks += 1
    backup_files = list(Path(skill_dir).glob("*.backup"))
    backup_files += list(Path(skill_dir).glob("*.bak"))
    backup_files += list(Path(skill_dir).glob("*.old"))
    
    if backup_files:
        print("[WARN] Found backup files in source:")
        for backup in backup_files:
            print(f"  - {backup.name}")
        issues.append(f"Source contains {len(backup_files)} backup files")
    else:
        print("[OK] No backup files in source")
        checks_passed += 1
    
    # 检查3: 没有临时检查脚本
    total_checks += 1
    temp_scripts = []
    for pattern in ["*check*.py", "*test*.py", "*fix*.py", "*verify*.py"]:
        temp_scripts += list(Path(skill_dir).glob(pattern))
    
    # 过滤掉真正的技能文件
    real_skill_files = ["skill.py"]
    temp_scripts = [f for f in temp_scripts if f.name not in real_skill_files]
    
    if temp_scripts:
        print("[WARN] Found temporary check scripts in source:")
        for script in temp_scripts[:5]:  # 只显示前5个
            print(f"  - {script.name}")
        if len(temp_scripts) > 5:
            print(f"  ... and {len(temp_scripts) - 5} more")
        issues.append(f"Source contains {len(temp_scripts)} temporary scripts")
    else:
        print("[OK] No temporary scripts in source")
        checks_passed += 1
    
    return {
        "issues": issues,
        "passed": checks_passed,
        "total": total_checks,
        "score": checks_passed / total_checks * 100 if total_checks > 0 else 100
    }

def check_changelog_consistency(skill_dir):
    """检查CHANGELOG.md版本一致性"""
    print("\n=== CHANGELOG Consistency Check ===")
    
    issues = []
    checks_passed = 0
    total_checks = 0
    
    changelog_path = os.path.join(skill_dir, "CHANGELOG.md")
    
    # 检查1: CHANGELOG.md存在
    total_checks += 1
    if not os.path.exists(changelog_path):
        print("[FAIL] CHANGELOG.md not found")
        issues.append("CHANGELOG.md file missing")
        return {
            "issues": issues,
            "passed": checks_passed,
            "total": total_checks,
            "score": 0
        }
    else:
        print("[OK] CHANGELOG.md exists")
        checks_passed += 1
    
    # 读取CHANGELOG内容
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查2: 包含当前版本记录
    total_checks += 1
    
    # 从config.yaml获取当前版本
    config_path = os.path.join(skill_dir, "config.yaml")
    current_version = None
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
            match = re.search(r'version:\s*["\']?(\d+\.\d+\.\d+)["\']?', config_content)
            if match:
                current_version = match.group(1)
    
    if current_version:
        # 检查CHANGELOG是否包含当前版本
        version_pattern = f"## \\[{current_version}\\]"
        if re.search(version_pattern, content):
            print(f"[OK] CHANGELOG.md contains current version: {current_version}")
            checks_passed += 1
        else:
            print(f"[FAIL] CHANGELOG.md missing current version: {current_version}")
            issues.append(f"CHANGELOG.md missing version {current_version}")
    else:
        print("[WARN] Could not determine current version from config.yaml")
        issues.append("Could not determine current version")
    
    # 检查3: 最后更新日期合理
    total_checks += 1
    last_updated_match = re.search(r'\*\*Last Updated\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    current_version_match = re.search(r'\*\*Current Version\*\*:\s*(\d+\.\d+\.\d+)', content)
    
    if last_updated_match and current_version_match:
        print(f"[OK] CHANGELOG has last updated and current version")
        checks_passed += 1
    else:
        print("[WARN] CHANGELOG missing last updated or current version")
        issues.append("CHANGELOG missing metadata")
    
    return {
        "issues": issues,
        "passed": checks_passed,
        "total": total_checks,
        "score": checks_passed / total_checks * 100 if total_checks > 0 else 100
    }

def check_version_consistency_extended(skill_dir):
    """扩展的版本一致性检查（包括CHANGELOG）"""
    print("\n=== Extended Version Consistency Check ===")
    
    versions = {}
    issues = []
    checks_passed = 0
    total_checks = 0
    
    # 检查config.yaml
    total_checks += 1
    config_path = os.path.join(skill_dir, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'version:\s*["\']?(\d+\.\d+\.\d+)["\']?', content)
            if match:
                versions['config.yaml'] = match.group(1)
                print(f"[OK] config.yaml: {versions['config.yaml']}")
                checks_passed += 1
            else:
                print("[FAIL] config.yaml: No version found")
                issues.append("config.yaml missing version")
    else:
        print("[FAIL] config.yaml not found")
        issues.append("config.yaml missing")
    
    # 检查package.json
    total_checks += 1
    package_path = os.path.join(skill_dir, "package.json")
    if os.path.exists(package_path):
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'version' in data:
                    versions['package.json'] = data['version']
                    print(f"[OK] package.json: {versions['package.json']}")
                    checks_passed += 1
                else:
                    print("[FAIL] package.json: No version field")
                    issues.append("package.json missing version")
        except json.JSONDecodeError:
            print("[FAIL] package.json: Invalid JSON")
            issues.append("package.json invalid JSON")
    else:
        print("[FAIL] package.json not found")
        issues.append("package.json missing")
    
    # 检查CHANGELOG.md中的当前版本
    total_checks += 1
    changelog_path = os.path.join(skill_dir, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找当前版本声明
            current_match = re.search(r'\*\*Current Version\*\*:\s*(\d+\.\d+\.\d+)', content)
            if current_match:
                versions['CHANGELOG.current'] = current_match.group(1)
                print(f"[OK] CHANGELOG current version: {versions['CHANGELOG.current']}")
                checks_passed += 1
            else:
                print("[WARN] CHANGELOG: No current version declared")
                issues.append("CHANGELOG missing current version")
    else:
        print("[FAIL] CHANGELOG.md not found")
        issues.append("CHANGELOG.md missing")
    
    # 检查版本一致性
    if len(versions) >= 2:
        unique_versions = set(versions.values())
        if len(unique_versions) == 1:
            print(f"[OK] All versions consistent: {list(unique_versions)[0]}")
        else:
            print("[FAIL] Version mismatch:")
            for file, version in versions.items():
                print(f"  {file}: {version}")
            issues.append(f"Version mismatch: {versions}")
    
    return {
        "issues": issues,
        "passed": checks_passed,
        "total": total_checks,
        "score": checks_passed / total_checks * 100 if total_checks > 0 else 100,
        "versions": versions
    }

def generate_recommendations(results):
    """生成修复建议"""
    print("\n=== Release Management Recommendations ===")
    
    recommendations = []
    
    # 基于检查结果生成建议
    if results['release_structure']['score'] < 100:
        recommendations.append("1. Clean up source directory:")
        recommendations.append("   - Remove 'latest' folder if it exists")
        recommendations.append("   - Remove backup files (*.backup, *.bak, *.old)")
        recommendations.append("   - Remove temporary check scripts")
    
    if results['changelog_consistency']['score'] < 100:
        recommendations.append("2. Fix CHANGELOG.md:")
        recommendations.append("   - Ensure it contains current version")
        recommendations.append("   - Update last updated date")
        recommendations.append("   - Add missing version entries")
    
    if results['version_consistency']['score'] < 100:
        recommendations.append("3. Fix version consistency:")
        recommendations.append("   - Update all files to same version")
        recommendations.append("   - Check config.yaml, package.json, CHANGELOG.md")
        recommendations.append("   - Update code files if they contain version")
    
    if not recommendations:
        recommendations.append("[OK] All release management checks passed!")
        recommendations.append("[OK] Ready for professional release")
    
    return recommendations

def main():
    import sys
    
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认检查当前目录
        skill_dir = os.getcwd()
    
    print("Release Management Audit Tool")
    print("Based on 2026-03-29 AISleepGen release management lessons")
    print("=" * 60)
    print(f"Checking: {skill_dir}")
    
    # 运行所有检查
    results = {}
    
    results['release_structure'] = check_release_structure(skill_dir)
    results['changelog_consistency'] = check_changelog_consistency(skill_dir)
    results['version_consistency'] = check_version_consistency_extended(skill_dir)
    
    # 计算总体分数
    total_passed = sum(r['passed'] for r in results.values())
    total_checks = sum(r['total'] for r in results.values())
    overall_score = total_passed / total_checks * 100 if total_checks > 0 else 100
    
    # 汇总问题
    all_issues = []
    for category, result in results.items():
        all_issues.extend(result['issues'])
    
    # 显示总结
    print("\n" + "=" * 60)
    print("RELEASE MANAGEMENT AUDIT SUMMARY")
    print("=" * 60)
    
    print(f"\nOverall Score: {overall_score:.1f}%")
    print(f"Checks Passed: {total_passed}/{total_checks}")
    
    for category, result in results.items():
        category_name = category.replace('_', ' ').title()
        print(f"  {category_name}: {result['score']:.1f}%")
    
    if all_issues:
        print(f"\nFound {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] No issues found!")
    
    # 生成建议
    recommendations = generate_recommendations(results)
    print("\n" + "\n".join(recommendations))
    
    print("\n" + "=" * 60)
    print("Based on AISkinX permanent audit principles:")
    print("  - Concretization: Specific checks for release management")
    print("  - Verifiability: All issues can be verified")
    print("  - Automation: Automated release management checks")
    print("  - Documentation: Permanent record of lessons learned")

if __name__ == "__main__":
    main()