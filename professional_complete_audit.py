"""
专业完整审核 - 真实审核，不假设任何"应该没问题"
"""

import os
import sys
import json
import yaml
import re
import zipfile
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile

class ProfessionalCompleteAudit:
    """专业完整审核 - 检查ZIP文件和发布文件夹"""
    
    def __init__(self, zip_path, release_dir):
        self.zip_path = Path(zip_path)
        self.release_dir = Path(release_dir)
        self.results = []
        self.evidence = {}
        
    def check_with_evidence(self, check_name, check_func, *args):
        """带证据的检查"""
        print(f"\n{'='*80}")
        print(f"专业检查: {check_name}")
        print(f"{'='*80}")
        
        try:
            result, evidence = check_func(*args)
            
            if result:
                print(f"[PROFESSIONAL PASS] 通过")
            else:
                print(f"[PROFESSIONAL FAIL] 失败")
            
            self.results.append({
                "check_name": check_name,
                "status": "passed" if result else "failed",
                "evidence": evidence
            })
            
            self.evidence[check_name] = evidence
            
            return result
            
        except Exception as e:
            print(f"[PROFESSIONAL ERROR] 检查出错: {e}")
            
            self.results.append({
                "check_name": check_name,
                "status": "error",
                "error": str(e),
                "evidence": {}
            })
            
            return False
    
    def check_zip_integrity(self):
        """检查ZIP文件完整性"""
        evidence = {}
        
        if not self.zip_path.exists():
            evidence['error'] = "ZIP文件不存在"
            print(f"  [FAIL] ZIP文件不存在: {self.zip_path}")
            return False, evidence
        
        zip_size_mb = self.zip_path.stat().st_size / (1024 * 1024)
        evidence['zip_path'] = str(self.zip_path)
        evidence['zip_size_mb'] = round(zip_size_mb, 2)
        
        print(f"  ZIP文件: {self.zip_path.name}")
        print(f"  大小: {zip_size_mb:.2f} MB")
        
        # 检查ZIP文件是否可以解压
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                evidence['file_count'] = len(file_list)
                evidence['file_list'] = file_list[:10]  # 只记录前10个文件
                
                print(f"  文件数量: {len(file_list)}")
                print(f"  前10个文件:")
                for i, file in enumerate(file_list[:10], 1):
                    print(f"    {i}. {file}")
                
                if len(file_list) > 10:
                    print(f"    ... 还有 {len(file_list)-10} 个文件")
                
                # 检查必需文件
                required_files = [
                    "skill.py",
                    "config.yaml", 
                    "SKILL.md",
                    "README.md",
                    "CHANGELOG.md",
                    "LICENSE.txt"
                ]
                
                missing_in_zip = []
                for req_file in required_files:
                    if not any(req_file in f for f in file_list):
                        missing_in_zip.append(req_file)
                
                if missing_in_zip:
                    evidence['missing_in_zip'] = missing_in_zip
                    print(f"  [FAIL] ZIP中缺失文件: {missing_in_zip}")
                    return False, evidence
                else:
                    print(f"  [OK] ZIP包含所有必需文件")
                    
        except zipfile.BadZipFile as e:
            evidence['error'] = f"ZIP文件损坏: {e}"
            print(f"  [FAIL] ZIP文件损坏: {e}")
            return False, evidence
        
        return True, evidence
    
    def check_release_folder_integrity(self):
        """检查发布文件夹完整性"""
        evidence = {}
        
        if not self.release_dir.exists():
            evidence['error'] = "发布文件夹不存在"
            print(f"  [FAIL] 发布文件夹不存在: {self.release_dir}")
            return False, evidence
        
        # 检查必需文件
        required_files = [
            ("skill.py", "主技能文件"),
            ("config.yaml", "配置文件"),
            ("SKILL.md", "技能文档"),
            ("README.md", "用户文档"),
            ("CHANGELOG.md", "更新日志"),
            ("LICENSE.txt", "许可证文件")
        ]
        
        missing_files = []
        file_details = {}
        
        for filename, description in required_files:
            filepath = self.release_dir / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                file_details[filename] = {
                    "size_kb": round(size_kb, 1),
                    "description": description
                }
                print(f"  [OK] {filename}: {size_kb:.1f} KB ({description})")
            else:
                missing_files.append(filename)
                print(f"  [FAIL] {filename}: 缺失 ({description})")
        
        evidence['file_details'] = file_details
        
        if missing_files:
            evidence['missing_files'] = missing_files
            return False, evidence
        
        return True, evidence
    
    def check_version_consistency_both(self):
        """检查ZIP和发布文件夹的版本一致性"""
        evidence = {}
        
        # 检查发布文件夹版本
        release_versions = self._extract_versions(self.release_dir)
        evidence['release_versions'] = release_versions
        
        print("发布文件夹版本:")
        for file, version in release_versions.items():
            print(f"  {file}: {version}")
        
        # 检查ZIP文件版本
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            zip_versions = self._extract_versions(Path(temp_dir))
            evidence['zip_versions'] = zip_versions
            
            print("ZIP文件版本:")
            for file, version in zip_versions.items():
                print(f"  {file}: {version}")
        
        # 比较版本
        all_versions = {}
        all_versions.update(release_versions)
        all_versions.update(zip_versions)
        
        unique_versions = set(all_versions.values())
        
        if len(unique_versions) == 1:
            version = list(unique_versions)[0]
            evidence['consistent_version'] = version
            evidence['consistency'] = True
            print(f"  [OK] 所有文件版本一致: {version}")
            return True, evidence
        else:
            evidence['inconsistent_versions'] = all_versions
            evidence['consistency'] = False
            print(f"  [FAIL] 版本不一致:")
            for file, version in all_versions.items():
                print(f"    {file}: {version}")
            return False, evidence
    
    def _extract_versions(self, directory):
        """从目录中提取版本号"""
        versions = {}
        
        # 检查config.yaml
        config_file = directory / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    config_version = config.get('skill', {}).get('version', 'NOT_FOUND')
                    versions['config.yaml'] = config_version
            except Exception as e:
                versions['config.yaml'] = f"ERROR: {e}"
        
        # 检查skill.py
        skill_file = directory / "skill.py"
        if skill_file.exists():
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    skill_version = match.group(1) if match else 'NOT_FOUND'
                    versions['skill.py'] = skill_version
            except Exception as e:
                versions['skill.py'] = f"ERROR: {e}"
        
        # 检查SKILL.md
        skill_md_file = directory / "SKILL.md"
        if skill_md_file.exists():
            try:
                with open(skill_md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找版本号
                    patterns = [
                        r'Version:\s*([\d.]+)',
                        r'version\s+([\d.]+)',
                        r'v([\d.]+)\s+'
                    ]
                    
                    skill_md_version = 'NOT_FOUND'
                    for pattern in patterns:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            skill_md_version = match.group(1)
                            break
                    
                    versions['SKILL.md'] = skill_md_version
            except Exception as e:
                versions['SKILL.md'] = f"ERROR: {e}"
        
        # 检查CHANGELOG.md
        changelog_file = directory / "CHANGELOG.md"
        if changelog_file.exists():
            try:
                with open(changelog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'## \[([\d.]+)\]', content)
                    changelog_version = match.group(1) if match else 'NOT_FOUND'
                    versions['CHANGELOG.md'] = changelog_version
            except Exception as e:
                versions['CHANGELOG.md'] = f"ERROR: {e}"
        
        return versions
    
    def check_historical_references(self):
        """检查历史遗留引用"""
        evidence = {}
        
        legacy_patterns = [
            ("sleep-rabbit-secure.js", "历史JS包装器"),
            ("test-plugin.js", "历史测试插件"),
            ("microservices", "历史微服务引用"),
            ("ports 8008", "历史端口引用"),
            ("ports 8009", "历史端口引用"),
            ("ports 8030", "历史端口引用"),
            ("ports 8040", "历史端口引用"),
            ("Node wrapper", "历史Node包装器"),
            ("JS wrapper", "历史JS包装器"),
            ("REST APIs", "历史REST API引用")
        ]
        
        found_legacy = []
        
        # 检查发布文件夹
        for pattern, description in legacy_patterns:
            try:
                result = subprocess.run(
                    ['findstr', '/S', '/I', pattern, str(self.release_dir / "*.md")],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if result.stdout:
                    found_legacy.append({
                        "pattern": pattern,
                        "description": description,
                        "files": result.stdout.strip().split('\n')
                    })
            except Exception:
                # 如果findstr失败，使用Python搜索
                for md_file in self.release_dir.rglob("*.md"):
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if pattern.lower() in content.lower():
                                found_legacy.append({
                                    "pattern": pattern,
                                    "description": description,
                                    "file": str(md_file)
                                })
                    except Exception:
                        continue
        
        evidence['found_legacy'] = found_legacy
        
        if found_legacy:
            print(f"  [FAIL] 发现历史遗留引用:")
            for legacy in found_legacy:
                print(f"    模式: {legacy['pattern']} ({legacy['description']})")
                if 'files' in legacy:
                    for file in legacy['files'][:3]:  # 只显示前3个文件
                        print(f"      文件: {file}")
                elif 'file' in legacy:
                    print(f"      文件: {legacy['file']}")
            return False, evidence
        else:
            print(f"  [OK] 无历史遗留引用")
            return True, evidence
    
    def check_import_functionality(self):
        """检查导入功能"""
        evidence = {}
        
        test_code = f'''
import sys
import os
sys.path.insert(0, r'{self.release_dir}')

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
        
        # 检查名称
        name = getattr(skill_instance, 'name', 'NOT_FOUND')
        print(f"NAME: {{name}}")
        
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
    
    def check_zip_release_consistency(self):
        """检查ZIP和发布文件夹的一致性"""
        evidence = {}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压ZIP
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            zip_dir = Path(temp_dir)
            
            # 比较文件
            differences = []
            
            # 检查必需文件
            required_files = ["skill.py", "config.yaml", "SKILL.md", "README.md", "CHANGELOG.md"]
            
            for filename in required_files:
                release_file = self.release_dir / filename
                zip_file = zip_dir / filename
                
                if not release_file.exists():
                    differences.append(f"发布文件夹缺失: {filename}")
                elif not zip_file.exists():
                    differences.append(f"ZIP文件缺失: {filename}")
                else:
                    # 比较文件大小
                    release_size = release_file.stat().st_size
                    zip_size = zip_file.stat().st_size
                    
                    if release_size != zip_size:
                        differences.append(f"文件大小不一致: {filename} (发布: {release_size}, ZIP: {zip_size})")
                    
                    # 比较内容（简单比较）
                    try:
                        with open(release_file, 'r', encoding='utf-8') as f1:
                            release_content = f1.read()
                        with open(zip_file, 'r', encoding='utf-8') as f2:
                            zip_content = f2.read()
                        
                        if release_content != zip_content:
                            # 检查是否是空白/换行符差异
                            release_clean = release_content.replace('\r\n', '\n').strip()
                            zip_clean = zip_content.replace('\r\n', '\n').strip()
                            
                            if release_clean != zip_clean:
                                differences.append(f"内容不一致: {filename}")
                    except Exception as e:
                        differences.append(f"比较错误 {filename}: {e}")
            
            evidence['differences'] = differences
            
            if differences:
                print(f"  [FAIL] ZIP和发布文件夹不一致:")
                for diff in differences[:5]:  # 只显示前5个差异
                    print(f"    {diff}")
                if len(differences) > 5:
                    print(f"    ... 还有 {len(differences)-5} 个差异")
                return False, evidence
            else:
                print(f"  [OK] ZIP和发布文件夹完全一致")
                return True, evidence
    
    def run_complete_audit(self):
        """运行完整审核"""
        print("专业完整审核 - ZIP文件和发布文件夹")
        print("=" * 80)
        print(f"ZIP文件: {self.zip_path}")
        print(f"发布文件夹: {self.release_dir}")
        print(f"审核时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        checks = [
            ("ZIP文件完整性检查", self.check_zip_integrity),
            ("发布文件夹完整性检查", self.check_release_folder_integrity),
            ("版本一致性检查(ZIP+发布)", self.check_version_consistency_both),
            ("历史遗留引用检查", self.check_historical_references),
            ("导入功能测试", self.check_import_functionality),
            ("ZIP与发布文件夹一致性检查", self.check_zip_release_consistency)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            passed = self.check_with_evidence(check_name, check_func)
            if not passed:
                all_passed = False
        
        print(f"\n{'='*80}")
        print("专业审核总结")
        print(f"{'='*80}")
        
        passed_checks = sum(1 for r in self.results if r['status'] == 'passed')
        total_checks = len(self.results)
        
        for result in self.results:
            status_symbol = "[PASS]" if result['status'] == 'passed' else "[FAIL]"
            print(f"{status_symbol} {result['check_name']}")
        
        print(f"\n通过: {passed_checks}/{total_checks}")
        
        if all_passed:
            print(f"\n[PROFESSIONAL SUCCESS] 所有检查通过 - 真实专业完整审核通过!")
        else:
            print(f"\n[PROFESSIONAL FAILURE] 需要修复 {total_checks-passed_checks} 个问题")
        
        # 生成证据报告
        report = self.generate_evidence_report()
        
        return all_passed, report
    
    def generate_evidence_report(self):
        """生成证据报告"""
        report = {
            "audit_time": datetime.now().isoformat(),
            "zip_path": str(self.zip_path),
            "release_dir": str(self.release_dir),
            "checks": self.results,
            "evidence_summary": self.evidence,
            "passed_checks": sum(1 for r in self.results if r['status'] == 'passed'),
            "total_checks": len(self.results),
            "all_passed": all(r['status'] == 'passed' for r in self.results)
        }
        
        report_file = self.zip_path.parent / "professional_audit_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n专业证据报告已保存: {report_file}")
        
        return report

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python professional_complete_audit.py <ZIP文件路径> <发布文件夹路径>")
        print("示例: python professional_complete_audit.py D:/openclaw/releases/AISleepGen_v2.4.0_final.zip D:/openclaw/releases/AISleepGen_release")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    release_dir = sys.argv[2]
    
    if not Path(zip_path).exists():
        print(f"错误: ZIP文件不存在: {zip_path}")
        sys.exit(1)
    
    if not Path(release_dir).exists():
        print(f"错误: 发布文件夹不存在: {release_dir}")
        sys.exit(1)
    
    auditor = ProfessionalCompleteAudit(zip_path, release_dir)
    all_passed, report = auditor.run_complete_audit()
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()