"""
运行最终ClawHub检查
"""

import os
import json
import yaml
from pathlib import Path
import re

def check_skill_structure(skill_dir):
    """检查技能结构"""
    print("CHECKING SKILL STRUCTURE")
    print("=" * 70)
    
    required_files = [
        "skill.py",
        "config.yaml", 
        "README.md",
        "SKILL.md"
    ]
    
    optional_files = [
        "requirements.txt",
        "install.ps1",
        "uninstall.ps1"
    ]
    
    print(f"\nChecking: {skill_dir}")
    
    missing_files = []
    present_files = []
    
    for file in required_files:
        file_path = skill_dir / file
        if file_path.exists():
            present_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"\nRequired files:")
    for file in required_files:
        status = "✓" if file in present_files else "✗"
        print(f"  {status} {file}")
    
    if missing_files:
        print(f"\n❌ MISSING REQUIRED FILES: {missing_files}")
        return False
    
    print(f"\nOptional files:")
    for file in optional_files:
        file_path = skill_dir / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  - {file} (optional)")
    
    return True

def check_config_yaml(skill_dir):
    """检查config.yaml"""
    print(f"\nCHECKING CONFIG.YAML")
    print("=" * 70)
    
    config_file = skill_dir / "config.yaml"
    
    if not config_file.exists():
        print("❌ config.yaml not found")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        required_fields = ["skill_id", "version", "description"]
        
        print(f"\nConfig fields:")
        for field in required_fields:
            if field in config:
                print(f"  ✓ {field}: {config[field]}")
            else:
                print(f"  ✗ {field}: MISSING")
                return False
        
        # 检查版本号格式
        version = config.get("version", "")
        if re.match(r'^\d+\.\d+\.\d+$', version):
            print(f"  ✓ Version format valid: {version}")
        else:
            print(f"  ⚠️ Version format may need review: {version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False

def check_skill_py(skill_dir):
    """检查skill.py"""
    print(f"\nCHECKING SKILL.PY")
    print("=" * 70)
    
    skill_file = skill_dir / "skill.py"
    
    if not skill_file.exists():
        print("❌ skill.py not found")
        return False
    
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_patterns = [
            (r'class.*Skill', "Skill class definition"),
            (r'def.*handle_command', "handle_command method"),
            (r'def.*setup', "setup method"),
            (r'version.*=', "Version variable")
        ]
        
        print(f"\nSkill.py checks:")
        all_found = True
        
        for pattern, description in required_patterns:
            if re.search(pattern, content):
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description}")
                all_found = False
        
        # 检查版本一致性
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            py_version = version_match.group(1)
            print(f"  ✓ Python version: {py_version}")
        else:
            print(f"  ⚠️ Version not found in skill.py")
            all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error reading skill.py: {e}")
        return False

def check_documentation_consistency(skill_dir):
    """检查文档一致性"""
    print(f"\nCHECKING DOCUMENTATION CONSISTENCY")
    print("=" * 70)
    
    # 检查SKILL.md
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        print("❌ SKILL.md not found")
        return False
    
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            "## Description",
            "## Commands", 
            "## Installation",
            "## Configuration"
        ]
        
        print(f"\nSKILL.md sections:")
        all_found = True
        
        for section in required_sections:
            if section in content:
                print(f"  ✓ {section}")
            else:
                print(f"  ✗ {section}")
                all_found = False
        
        # 检查安全声明
        security_keywords = ["local", "no network", "secure", "private"]
        security_found = any(keyword in content.lower() for keyword in security_keywords)
        
        if security_found:
            print(f"  ✓ Security declarations found")
        else:
            print(f"  ⚠️ No explicit security declarations")
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error reading SKILL.md: {e}")
        return False

def check_for_prohibited_patterns(skill_dir):
    """检查禁止模式"""
    print(f"\nCHECKING FOR PROHIBITED PATTERNS")
    print("=" * 70)
    
    prohibited_patterns = [
        (r'requests\.(get|post|put|delete)', "External HTTP requests"),
        (r'urllib\.request', "URL library usage"),
        (r'socket\.', "Socket programming"),
        (r'subprocess\.', "Subprocess execution"),
        (r'os\.system', "OS system calls"),
        (r'eval\(', "Eval function"),
        (r'exec\(', "Exec function"),
        (r'__import__', "Dynamic imports")
    ]
    
    issues_found = []
    
    for py_file in skill_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern, description in prohibited_patterns:
                if re.search(pattern, content):
                    # 检查是否在注释中
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line) and not line.strip().startswith('#'):
                            issues_found.append({
                                "file": str(py_file.relative_to(skill_dir)),
                                "line": i,
                                "pattern": description,
                                "code": line.strip()[:50]
                            })
                            break
                            
        except Exception as e:
            print(f"  Error reading {py_file.name}: {e}")
    
    if issues_found:
        print(f"\n❌ PROHIBITED PATTERNS FOUND:")
        for issue in issues_found[:5]:  # 只显示前5个
            print(f"  File: {issue['file']}:{issue['line']}")
            print(f"  Pattern: {issue['pattern']}")
            print(f"  Code: {issue['code']}...")
            print()
        
        if len(issues_found) > 5:
            print(f"  ... and {len(issues_found)-5} more issues")
        
        return False
    else:
        print(f"\n✓ No prohibited patterns found")
        return True

def check_file_sizes(skill_dir):
    """检查文件大小"""
    print(f"\nCHECKING FILE SIZES")
    print("=" * 70)
    
    size_issues = []
    
    for file_path in skill_dir.rglob("*"):
        if file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            
            # 检查过大文件
            if size_kb > 100:  # 大于100KB
                size_issues.append({
                    "file": str(file_path.relative_to(skill_dir)),
                    "size_kb": round(size_kb, 1)
                })
    
    if size_issues:
        print(f"\n⚠️ LARGE FILES FOUND:")
        for issue in size_issues:
            print(f"  {issue['file']}: {issue['size_kb']} KB")
        
        print(f"\nRecommendation: Consider splitting large files")
        return False
    else:
        print(f"\n✓ All files under 100KB")
        return True

def create_release_package(skill_dir):
    """创建发布包"""
    print(f"\nCREATING RELEASE PACKAGE")
    print("=" * 70)
    
    release_dir = Path("D:/openclaw/releases/AISleepGen_release")
    
    if release_dir.exists():
        import shutil
        shutil.rmtree(release_dir)
    
    # 复制文件
    import shutil
    shutil.copytree(skill_dir, release_dir)
    
    print(f"Release directory created: {release_dir}")
    
    # 创建ZIP包
    import zipfile
    zip_path = Path("D:/openclaw/releases/AISleepGen_v2.4.0.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, release_dir.parent)
                zipf.write(file_path, arcname)
    
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    print(f"ZIP package created: {zip_path}")
    print(f"ZIP size: {zip_size_mb:.2f} MB")
    
    # 创建发布清单
    file_count = sum(1 for _ in release_dir.rglob("*") if _.is_file())
    py_file_count = sum(1 for _ in release_dir.rglob("*.py"))
    
    release_manifest = {
        "release_time": "2026-03-31T15:45:00Z",
        "skill_id": "aisleepgen-sleep-health",
        "version": "2.4.0",
        "release_directory": str(release_dir),
        "zip_package": str(zip_path),
        "zip_size_mb": round(zip_size_mb, 2),
        "file_count": file_count,
        "python_file_count": py_file_count,
        "checks_passed": [
            "Structure check",
            "Config validation", 
            "Skill.py validation",
            "Documentation check",
            "Security patterns check",
            "File size check"
        ]
    }
    
    manifest_file = release_dir / "RELEASE_MANIFEST.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(release_manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Release manifest created: {manifest_file}")
    
    return release_dir, zip_path, release_manifest

def main():
    """主检查函数"""
    print("AISLEEPGEN FINAL CLAWHUB CHECK")
    print("=" * 70)
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen/v2.4_final_optimized")
    
    print(f"\nSkill: AISleepGen v2.4.0")
    print(f"Directory: {skill_dir}")
    
    print(f"\nRunning comprehensive ClawHub-style checks...")
    
    checks = [
        ("Skill Structure", check_skill_structure(skill_dir)),
        ("Config YAML", check_config_yaml(skill_dir)),
        ("Skill.py", check_skill_py(skill_dir)),
        ("Documentation", check_documentation_consistency(skill_dir)),
        ("Security Patterns", check_for_prohibited_patterns(skill_dir)),
        ("File Sizes", check_file_sizes(skill_dir))
    ]
    
    print(f"\n" + "=" * 70)
    print("CHECK SUMMARY")
    print("=" * 70)
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, result in checks:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {check_name}: {status}")
        if result:
            passed_checks += 1
    
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"\nPassed: {passed_checks}/{total_checks} ({success_rate:.0f}%)")
    
    if passed_checks == total_checks:
        print(f"\n🎉 ALL CHECKS PASSED - READY FOR RELEASE")
        
        print(f"\nCreating release package...")
        release_dir, zip_path, manifest = create_release_package(skill_dir)
        
        print(f"\n" + "=" * 70)
        print("RELEASE PACKAGE READY")
        print("=" * 70)
        
        print(f"\nRelease directory: {release_dir}")
        print(f"ZIP package: {zip_path}")
        print(f"ZIP size: {manifest['zip_size_mb']} MB")
        print(f"Files: {manifest['file_count']} total, {manifest['python_file_count']} Python")
        
        print(f"\n✅ AISleepGen v2.4.0 is READY FOR CLAWHUB RELEASE")
        
        return True, release_dir, zip_path
    else:
        print(f"\n❌ CHECKS FAILED - NEEDS FIXES BEFORE RELEASE")
        print(f"Please address the failed checks above")
        
        return False, None, None

if __name__ == "__main__":
    print("FINAL PRE-RELEASE CHECK FOR AISLEEPGEN")
    print("=" * 70)
    
    success, release_dir, zip_path = main()
    
    if success:
        print(f"\n🎯 NEXT STEP: Upload to ClawHub")
        print(f"ZIP package: {zip_path}")
        print(f"Skill ID: aisleepgen-sleep-health")
        print(f"Version: 2.4.0")
    else:
        print(f"\n🔧 NEEDS FIXES BEFORE RELEASE")