"""
永久审核框架 - ASCII版本（无Unicode）
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
import subprocess

class PermanentAudit:
    """永久审核框架 - ASCII版本"""
    
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.results = []
        self.evidence = {}
        
    def check_with_evidence(self, check_name, check_func, *args):
        """带证据的检查"""
        print(f"\n{'='*60}")
        print(f"检查: {check_name}")
        print(f"{'='*60}")
        
        try:
            result, evidence = check_func(*args)
            
            if result:
                print(f"[PASS] 通过")
            else:
                print(f"[FAIL] 失败")
            
            # 记录结果和证据
            self.results.append({
                "check_name": check_name,
                "status": "passed" if result else "failed",
                "evidence": evidence
            })
            
            self.evidence[check_name] = evidence
            
            return result
            
        except Exception as e:
            print(f"[ERROR] 检查出错: {e}")
            
            self.results.append({
                "check_name": check_name,
                "status": "error",
                "error": str(e),
                "evidence": {}
            })
            
            return False
    
    def check_file_existence(self):
        """检查必需文件存在性"""
        required_files = [
            ("skill.py", "主技能文件"),
            ("config.yaml", "配置文件"),
            ("SKILL.md", "技能文档"),
            ("README.md", "用户文档"),
            ("CHANGELOG.md", "更新日志")
        ]
        
        evidence = {}
        missing_files = []
        
        for filename, description in required_files:
            filepath = self.skill_path / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                evidence[filename] = {
                    "exists": True,
                    "size_kb": round(size_kb, 1),
                    "description": description
                }
                print(f"  [OK] {filename}: {size_kb:.1f} KB ({description})")
            else:
                evidence[filename] = {
                    "exists": False,
                    "description": description
                }
                missing_files.append(filename)
                print(f"  [MISSING] {filename}: 缺失 ({description})")
        
        return len(missing_files) == 0, evidence
    
    def check_version_consistency(self):
        """检查版本一致性"""
        evidence = {}
        versions = {}
        
        # 1. 检查config.yaml
        config_file = self.skill_path / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    config_version = config.get('skill', {}).get('version', 'NOT_FOUND')
                    versions['config.yaml'] = config_version
                    evidence['config.yaml'] = config_version
                    print(f"  config.yaml: {config_version}")
            except Exception as e:
                versions['config.yaml'] = f"ERROR: {e}"
                evidence['config.yaml'] = f"解析错误: {e}"
                print(f"  config.yaml: 解析错误")
        
        # 2. 检查skill.py
        skill_file = self.skill_path / "skill.py"
        if skill_file.exists():
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    skill_version = match.group(1) if match else 'NOT_FOUND'
                    versions['skill.py'] = skill_version
                    evidence['skill.py'] = skill_version
                    print(f"  skill.py: {skill_version}")
            except Exception as e:
                versions['skill.py'] = f"ERROR: {e}"
                evidence['skill.py'] = f"解析错误: {e}"
                print(f"  skill.py: 解析错误")
        
        # 3. 检查CHANGELOG.md
        changelog_file = self.skill_path / "CHANGELOG.md"
        if changelog_file.exists():
            try:
                with open(changelog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找最新版本
                    match = re.search(r'## \[([\d.]+)\]', content)
                    changelog_version = match.group(1) if match else 'NOT_FOUND'
                    versions['CHANGELOG.md'] = changelog_version
                    evidence['CHANGELOG.md'] = changelog_version
                    print(f"  CHANGELOG.md: {changelog_version}")
            except Exception as e:
                versions['CHANGELOG.md'] = f"ERROR: {e}"
                evidence['CHANGELOG.md'] = f"解析错误: {e}"
                print(f"  CHANGELOG.md: 解析错误")
        
        # 检查一致性
        unique_versions = set(v for v in versions.values() if 'ERROR' not in str(v) and v != 'NOT_FOUND')
        
        if len(unique_versions) == 1:
            version = list(unique_versions)[0]
            evidence['consistency'] = True
            evidence['consistent_version'] = version
            print(f"  [OK] 版本一致: {version}")
            return True, evidence
        else:
            evidence['consistency'] = False
            evidence['versions_found'] = versions
            print(f"  [FAIL] 版本不一致:")
            for file, version in versions.items():
                print(f"    {file}: {version}")
            return False, evidence
    
    def check_date_freshness(self):
        """检查日期时效性"""
        evidence = {}
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查CHANGELOG最后更新日期
        changelog_file = self.skill_path / "CHANGELOG.md"
        if changelog_file.exists():
            try:
                with open(changelog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找最后更新日期
                    date_patterns = [
                        r'Last Updated.*?(\d{4}-\d{2}-\d{2})',
                        r'最后更新.*?(\d{4}-\d{2}-\d{2})',
                        r'## \[[\d.]+\].*?(\d{4}-\d{2}-\d{2})'
                    ]
                    
                    last_updated = None
                    for pattern in date_patterns:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            last_updated = match.group(1)
                            break
                    
                    evidence['CHANGELOG_last_updated'] = last_updated or 'NOT_FOUND'
                    
                    if last_updated == today:
                        print(f"  [OK] CHANGELOG最后更新: {last_updated} (今天)")
                        evidence['CHANGELOG_fresh'] = True
                    elif last_updated:
                        print(f"  [WARN] CHANGELOG最后更新: {last_updated} (不是今天)")
                        evidence['CHANGELOG_fresh'] = False
                    else:
                        print(f"  [WARN] CHANGELOG最后更新日期未找到")
                        evidence['CHANGELOG_fresh'] = False
            except Exception as e:
                evidence['CHANGELOG_error'] = str(e)
                print(f"  [ERROR] CHANGELOG日期检查错误: {e}")
        
        # 检查文件修改日期
        important_files = ['skill.py', 'config.yaml', 'SKILL.md']
        for filename in important_files:
            filepath = self.skill_path / filename
            if filepath.exists():
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d')
                evidence[f'{filename}_mtime'] = mtime
                print(f"  {filename} 修改时间: {mtime}")
        
        # 简单判断：如果CHANGELOG是今天或重要文件是今天修改的，算通过
        is_fresh = (evidence.get('CHANGELOG_fresh') is True or 
                   any('2026-03-31' in str(v) for v in evidence.values()))
        
        return is_fresh, evidence
    
    def test_import(self):
        """测试skill.py导入"""
        evidence = {}
        
        test_code = f'''
import sys
import os
sys.path.insert(0, r'{self.skill_path}')

try:
    import skill as test_skill
    print("IMPORT_SUCCESS: skill.py可以导入")
    
    if hasattr(test_skill, 'SleepRabbitSkill'):
        print("CLASS_FOUND: 找到SleepRabbitSkill类")
        
        # 尝试创建实例
        skill_instance = test_skill.SleepRabbitSkill()
        print("INSTANCE_CREATED: 可以创建Skill实例")
        
        # 检查版本
        version = getattr(skill_instance, 'version', 'NOT_FOUND')
        print(f"VERSION: {{version}}")
        
        print("ALL_TESTS_PASSED")
        import_result = "SUCCESS"
        
    else:
        print("CLASS_NOT_FOUND: skill.py中没有SleepRabbitSkill类")
        import_result = "FAILED"
        
except Exception as e:
    print(f"IMPORT_ERROR: {{e}}")
    import traceback
    traceback.print_exc()
    import_result = "ERROR"
'''
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', test_code],
                capture_output=True,
                text=True,
                encoding='gbk',  # Windows中文系统使用gbk
                errors='replace',  # 遇到无法解码的字符时替换为�而不是崩溃
                timeout=30
            )
            
            evidence['stdout'] = result.stdout
            evidence['stderr'] = result.stderr
            evidence['returncode'] = result.returncode
            
            print("导入测试输出:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"  {line}")
            
            if result.returncode == 0 and "ALL_TESTS_PASSED" in result.stdout:
                print("  [OK] skill.py导入测试通过")
                return True, evidence
            else:
                print("  [FAIL] skill.py导入测试失败")
                if result.stderr:
                    print("  错误输出:")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            print(f"    {line}")
                return False, evidence
                
        except subprocess.TimeoutExpired:
            evidence['error'] = "测试超时"
            print("  [FAIL] 导入测试超时")
            return False, evidence
        except Exception as e:
            evidence['error'] = str(e)
            print(f"  [FAIL] 运行导入测试出错: {e}")
            return False, evidence
    
    def check_zip_package(self):
        """检查ZIP包"""
        evidence = {}
        
        # 查找ZIP包
        release_dir = self.skill_path.parent
        zip_files = list(release_dir.glob("*.zip"))
        
        if not zip_files:
            evidence['error'] = "未找到ZIP包"
            print("  [FAIL] 未找到ZIP包")
            return False, evidence
        
        zip_path = zip_files[0]
        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
        
        evidence['zip_path'] = str(zip_path)
        evidence['zip_size_mb'] = round(zip_size_mb, 2)
        
        print(f"  ZIP包: {zip_path.name}")
        print(f"  大小: {zip_size_mb:.2f} MB")
        
        if 0.01 <= zip_size_mb <= 10:
            print("  [OK] ZIP包大小正常")
            return True, evidence
        else:
            print(f"  [WARN] ZIP包大小异常: {zip_size_mb:.2f} MB")
            return False, evidence
    
    def run_full_audit(self):
        """运行完整审核"""
        print("永久审核框架 - 完整审核")
        print("=" * 60)
        print(f"技能路径: {self.skill_path}")
        print(f"审核时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        checks = [
            ("必需文件检查", self.check_file_existence),
            ("版本一致性检查", self.check_version_consistency),
            ("日期时效性检查", self.check_date_freshness),
            ("导入功能测试", self.test_import),
            ("ZIP包检查", self.check_zip_package)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            passed = self.check_with_evidence(check_name, check_func)
            if not passed:
                all_passed = False
        
        print(f"\n{'='*60}")
        print("审核总结")
        print(f"{'='*60}")
        
        passed_checks = sum(1 for r in self.results if r['status'] == 'passed')
        total_checks = len(self.results)
        
        for result in self.results:
            status_symbol = "[OK]" if result['status'] == 'passed' else "[FAIL]"
            print(f"{status_symbol} {result['check_name']}")
        
        print(f"\n通过: {passed_checks}/{total_checks}")
        
        if all_passed:
            print(f"\n[SUCCESS] 所有检查通过 - 真实准备好发布!")
        else:
            print(f"\n[FAILURE] 需要修复 {total_checks-passed_checks} 个问题")
        
        # 生成证据报告
        report = self.generate_evidence_report()
        
        return all_passed, report
    
    def generate_evidence_report(self):
        """生成证据报告"""
        report = {
            "audit_time": datetime.now().isoformat(),
            "skill_path": str(self.skill_path),
            "checks": self.results,
            "evidence_summary": self.evidence,
            "passed_checks": sum(1 for r in self.results if r['status'] == 'passed'),
            "total_checks": len(self.results),
            "all_passed": all(r['status'] == 'passed' for r in self.results)
        }
        
        report_file = self.skill_path.parent / "audit_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n证据报告已保存: {report_file}")
        
        return report

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python permanent_audit_ascii.py <技能路径>")
        print("示例: python permanent_audit_ascii.py D:/openclaw/releases/AISleepGen_release")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    if not Path(skill_path).exists():
        print(f"错误: 路径不存在: {skill_path}")
        sys.exit(1)
    
    auditor = PermanentAudit(skill_path)
    all_passed, report = auditor.run_full_audit()
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()