"""
终极发布检查 - 不假设任何"应该没问题"
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
import subprocess

def check_with_context(description, check_func):
    """带上下文的检查"""
    print(f"\n{'='*60}")
    print(f"检查: {description}")
    print(f"{'='*60}")
    
    try:
        result = check_func()
        if result:
            print(f"✓ 通过")
        else:
            print(f"✗ 失败")
        return result
    except Exception as e:
        print(f"⚠️ 检查出错: {e}")
        return False

def check_version_consistency():
    """检查所有文件版本一致性"""
    print("\n1. 检查版本一致性...")
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen_release")
    
    version_sources = {}
    
    # 1. 检查config.yaml
    config_file = skill_dir / "config.yaml"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            version_sources['config.yaml'] = config.get('version', 'NOT_FOUND')
    
    # 2. 检查skill.py
    skill_file = skill_dir / "skill.py"
    if skill_file.exists():
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            version_sources['skill.py'] = match.group(1) if match else 'NOT_FOUND'
    
    # 3. 检查CHANGELOG.md
    changelog_file = skill_dir / "CHANGELOG.md"
    if changelog_file.exists():
        with open(changelog_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找最新版本
            match = re.search(r'## \[([\d.]+)\]', content)
            version_sources['CHANGELOG.md'] = match.group(1) if match else 'NOT_FOUND'
    
    print(f"版本来源:")
    for source, version in version_sources.items():
        print(f"  {source}: {version}")
    
    # 检查一致性
    versions = list(version_sources.values())
    if len(set(versions)) == 1 and versions[0] != 'NOT_FOUND':
        print(f"✓ 所有文件版本一致: {versions[0]}")
        return True
    else:
        print(f"✗ 版本不一致!")
        return False

def check_required_files():
    """检查必需文件"""
    print("\n2. 检查必需文件...")
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen_release")
    
    required_files = [
        ("skill.py", "主技能文件"),
        ("config.yaml", "配置文件"),
        ("SKILL.md", "技能文档"),
        ("README.md", "用户文档"),
        ("CHANGELOG.md", "更新日志"),
        ("LICENSE.txt", "许可证文件")
    ]
    
    missing_files = []
    
    for filename, description in required_files:
        filepath = skill_dir / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  ✓ {filename} ({description}): {size_kb:.1f} KB")
        else:
            print(f"  ✗ {filename} ({description}): 缺失")
            missing_files.append(filename)
    
    if missing_files:
        print(f"✗ 缺失文件: {missing_files}")
        return False
    else:
        print(f"✓ 所有必需文件存在")
        return True

def check_skill_structure():
    """检查技能结构"""
    print("\n3. 检查技能结构...")
    
    skill_file = Path("D:/openclaw/releases/AISleepGen_release/skill.py")
    
    if not skill_file.exists():
        print("✗ skill.py 不存在")
        return False
    
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_patterns = [
        (r'class.*Skill.*:', "Skill类定义"),
        (r'def handle_command', "handle_command方法"),
        (r'def setup', "setup方法"),
        (r'def cleanup', "cleanup方法"),
        (r'def get_command_info', "get_command_info方法")
    ]
    
    missing_patterns = []
    
    for pattern, description in required_patterns:
        if not re.search(pattern, content):
            missing_patterns.append(description)
            print(f"  ✗ 缺失: {description}")
        else:
            print(f"  ✓ 存在: {description}")
    
    if missing_patterns:
        print(f"✗ 缺失必要结构: {missing_patterns}")
        return False
    else:
        print(f"✓ 技能结构完整")
        return True

def check_config_yaml():
    """检查config.yaml"""
    print("\n4. 检查config.yaml...")
    
    config_file = Path("D:/openclaw/releases/AISleepGen_release/config.yaml")
    
    if not config_file.exists():
        print("✗ config.yaml 不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        required_fields = [
            ("skill_id", "技能ID"),
            ("version", "版本号"),
            ("description", "描述"),
            ("author", "作者"),
            ("license", "许可证")
        ]
        
        missing_fields = []
        
        for field, description in required_fields:
            if field not in config:
                missing_fields.append(description)
                print(f"  ✗ 缺失: {description} ({field})")
            else:
                print(f"  ✓ 存在: {description}: {config[field]}")
        
        # 检查安全声明
        security_declared = any(keyword in str(config).lower() 
                              for keyword in ['local', 'no network', 'secure', 'private'])
        
        if security_declared:
            print(f"  ✓ 安全声明存在")
        else:
            print(f"  ⚠️ 无明确安全声明")
        
        if missing_fields:
            print(f"✗ 缺失必要字段: {missing_fields}")
            return False
        else:
            print(f"✓ config.yaml 完整")
            return True
            
    except Exception as e:
        print(f"✗ 解析config.yaml出错: {e}")
        return False

def check_for_prohibited_code():
    """检查禁止代码"""
    print("\n5. 检查禁止代码...")
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen_release")
    
    prohibited_patterns = [
        (r'requests\.(get|post|put|delete)', "HTTP请求"),
        (r'urllib\.request', "URL库"),
        (r'socket\.', "套接字"),
        (r'subprocess\.', "子进程"),
        (r'os\.system', "系统调用"),
        (r'eval\(', "eval函数"),
        (r'exec\(', "exec函数"),
        (r'__import__', "动态导入")
    ]
    
    issues = []
    
    for py_file in skill_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern, description in prohibited_patterns:
                if re.search(pattern, content):
                    # 检查是否在注释中
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line) and not line.strip().startswith('#'):
                            issues.append({
                                "file": str(py_file.relative_to(skill_dir)),
                                "line": i,
                                "issue": description,
                                "code": line.strip()[:50]
                            })
                            break
        except Exception as e:
            print(f"  读取文件出错 {py_file}: {e}")
    
    if issues:
        print(f"✗ 发现禁止代码:")
        for issue in issues[:3]:  # 只显示前3个
            print(f"  文件: {issue['file']}:{issue['line']}")
            print(f"  问题: {issue['issue']}")
            print(f"  代码: {issue['code']}...")
        if len(issues) > 3:
            print(f"  ... 还有 {len(issues)-3} 个问题")
        return False
    else:
        print(f"✓ 无禁止代码")
        return True

def run_basic_function_test():
    """运行基本功能测试"""
    print("\n6. 运行基本功能测试...")
    
    skill_dir = Path("D:/openclaw/releases/AISleepGen_release")
    
    # 测试skill.py是否可以导入
    test_code = '''
import sys
import os
sys.path.insert(0, r'{skill_dir}')

try:
    # 尝试导入skill模块
    import skill as test_skill
    print("✓ skill.py 可以导入")
    
    # 检查是否有Skill类
    if hasattr(test_skill, 'Skill'):
        print("✓ 找到Skill类")
        
        # 尝试创建实例
        skill_instance = test_skill.Skill()
        print("✓ 可以创建Skill实例")
        
        # 检查必要方法
        required_methods = ['handle_command', 'setup', 'cleanup', 'get_command_info']
        missing_methods = []
        
        for method in required_methods:
            if hasattr(skill_instance, method):
                print(f"  ✓ 实例有方法: {method}")
            else:
                missing_methods.append(method)
                print(f"  ✗ 实例缺失方法: {method}")
        
        if missing_methods:
            print(f"✗ 实例缺失方法: {missing_methods}")
            return False
        else:
            print("✓ Skill实例完整")
            return True
            
    else:
        print("✗ skill.py 中没有Skill类")
        return False
        
except Exception as e:
    print(f"✗ 导入/测试出错: {e}")
    import traceback
    traceback.print_exc()
    return False
'''.format(skill_dir=str(skill_dir))
    
    # 运行测试
    try:
        result = subprocess.run(
            [sys.executable, '-c', test_code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("✗ 测试超时")
        return False
    except Exception as e:
        print(f"✗ 运行测试出错: {e}")
        return False

def check_zip_package():
    """检查ZIP包"""
    print("\n7. 检查ZIP包...")
    
    zip_path = Path("D:/openclaw/releases/AISleepGen_v2.4.0.zip")
    
    if not zip_path.exists():
        print("✗ ZIP包不存在")
        return False
    
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  ZIP包: {zip_path}")
    print(f"  大小: {zip_size_mb:.2f} MB")
    
    if zip_size_mb < 0.01:
        print("⚠️ ZIP包可能太小")
        return False
    elif zip_size_mb > 10:
        print("⚠️ ZIP包可能太大")
        return False
    else:
        print(f"✓ ZIP包大小正常")
        return True

def main():
    """主检查函数"""
    print("终极发布检查 - 不假设任何'应该没问题'")
    print("=" * 60)
    
    checks = [
        ("版本一致性", check_version_consistency),
        ("必需文件", check_required_files),
        ("技能结构", check_skill_structure),
        ("配置文件", check_config_yaml),
        ("禁止代码", check_for_prohibited_code),
        ("功能测试", run_basic_function_test),
        ("ZIP包", check_zip_package)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*60}")
        print(f"检查项目: {check_name}")
        print(f"{'='*60}")
        
        try:
            result = check_func()
            results.append((check_name, result))
            
            if result:
                print(f"✓ {check_name}: 通过")
            else:
                print(f"✗ {check_name}: 失败")
        except Exception as e:
            print(f"⚠️ {check_name}: 检查出错 - {e}")
            results.append((check_name, False))
    
    print(f"\n{'='*60}")
    print("检查总结")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print(f"\n🎉 所有检查通过 - 真正准备好发布了!")
        return True
    else:
        print(f"\n🔧 需要修复 {total-passed} 个问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)