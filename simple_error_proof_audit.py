#!/usr/bin/env python3
"""
简化防错审核 - 核心功能，无复杂错误
"""

import os
import sys
import json
import re
import yaml
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

class SimpleErrorProofAudit:
    """简化防错审核"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.results = []
        self.evidence = []
        
    def run_audit(self):
        """运行审核"""
        print(f"\n{'='*80}")
        print("简化防错审核系统")
        print(f"{'='*80}")
        
        checks = [
            ("检查必需文件", self.check_required_files),
            ("检查版本号", self.check_version),
            ("检查语法", self.check_syntax),
            ("检查导入", self.check_import),
            ("检查文档语言", self.check_docs_language),
            ("检查历史引用", self.check_historical_refs),
            ("检查.pyc文件", self.check_pyc_files),  # 新增
            ("创建ZIP包", self.create_zip),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            print(f"\n[检查] {check_name}")
            
            try:
                passed, evidence = check_func()
                
                if passed:
                    print(f"  [OK] 通过")
                else:
                    print(f"  [FAIL] 失败")
                    all_passed = False
                
                self.results.append({
                    "check": check_name,
                    "passed": passed,
                    "evidence": evidence
                })
                
            except Exception as e:
                print(f"  [ERROR] 错误: {e}")
                all_passed = False
                self.results.append({
                    "check": check_name,
                    "error": str(e)
                })
        
        # 生成报告
        report = self.generate_report(all_passed)
        
        print(f"\n{'='*80}")
        if all_passed:
            print("[SUCCESS] 所有检查通过")
        else:
            print("[FAILURE] 有检查失败")
        print(f"{'='*80}")
        
        return report
    
    def check_required_files(self):
        """检查必需文件"""
        required = ["skill.py", "config.yaml", "SKILL.md", "README.md", "CHANGELOG.md", "LICENSE.txt"]
        
        missing = []
        for filename in required:
            if not (self.skill_path / filename).exists():
                missing.append(filename)
        
        return len(missing) == 0, {"missing": missing}
    
    def check_version(self):
        """检查版本号"""
        versions = {}
        
        # skill.py
        skill_file = self.skill_path / "skill.py"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8')
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
        
        # config.yaml
        config_file = self.skill_path / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                versions["config.yaml"] = config.get('skill', {}).get('version', 'NOT_FOUND')
        
        # 检查一致性
        all_versions = list(versions.values())
        valid_versions = [v for v in all_versions if v != "NOT_FOUND"]
        
        if not valid_versions:
            return False, {"error": "未找到版本号", "versions": versions}
        
        unique_versions = set(valid_versions)
        
        if len(unique_versions) == 1:
            return True, {"consistent_version": list(unique_versions)[0], "versions": versions}
        else:
            return False, {"inconsistent": versions}
    
    def check_syntax(self):
        """检查语法"""
        python_files = list(self.skill_path.rglob("*.py"))
        
        errors = []
        for py_file in python_files:
            try:
                compile(py_file.read_text(encoding='utf-8'), str(py_file), 'exec')
            except SyntaxError as e:
                errors.append(f"{py_file.name}:{e.lineno} - {e.msg}")
        
        return len(errors) == 0, {"errors": errors}
    
    def check_import(self):
        """检查导入"""
        import sys
        
        # 添加路径
        sys.path.insert(0, str(self.skill_path))
        
        try:
            import skill
            if hasattr(skill, 'SleepRabbitSkill'):
                instance = skill.SleepRabbitSkill()
                return True, {
                    "imported": True,
                    "class_found": True,
                    "instance_created": True,
                    "version": getattr(instance, 'version', 'NOT_FOUND')
                }
            else:
                return False, {"imported": True, "class_found": False}
        except Exception as e:
            return False, {"imported": False, "error": str(e)}
    
    def check_docs_language(self):
        """检查文档语言"""
        issues = []
        
        for doc_file in [self.skill_path / "CHANGELOG.md", self.skill_path / "README.md", self.skill_path / "SKILL.md"]:
            if doc_file.exists():
                content = doc_file.read_text(encoding='utf-8')
                # 检查中文
                if re.search(r'[\u4e00-\u9fff]', content):
                    issues.append(doc_file.name)
        
        return len(issues) == 0, {"files_with_chinese": issues}
    
    def check_historical_refs(self):
        """检查历史引用"""
        refs = []
        patterns = ["sleep-rabbit-secure.js", "test-plugin.js", "microservices"]
        
        for md_file in self.skill_path.rglob("*.md"):
            if md_file.exists():
                content = md_file.read_text(encoding='utf-8')
                for pattern in patterns:
                    if pattern in content:
                        refs.append(f"{md_file.name}: {pattern}")
        
        return len(refs) == 0, {"historical_refs": refs}
    
    def check_pyc_files(self):
        """检查.pyc文件"""
        pyc_files = list(self.skill_path.rglob("*.pyc"))
        pycache_dirs = list(self.skill_path.rglob("__pycache__"))
        
        return len(pyc_files) == 0 and len(pycache_dirs) == 0, {
            "pyc_files": [str(f.relative_to(self.skill_path)) for f in pyc_files],
            "pycache_dirs": [str(d.relative_to(self.skill_path)) for d in pycache_dirs]
        }
    
    def create_zip(self):
        """创建ZIP包"""
        zip_path = self.skill_path.parent / f"{self.skill_path.name}.zip"
        
        if zip_path.exists():
            zip_path.unlink()
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.skill_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.skill_path)
                    zipf.write(file_path, arcname)
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        
        return True, {
            "zip_created": True,
            "path": str(zip_path),
            "size_mb": round(size_mb, 2)
        }
    
    def generate_report(self, all_passed):
        """生成报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "skill_path": str(self.skill_path),
            "all_passed": all_passed,
            "results": self.results,
            "summary": {
                "total_checks": len(self.results),
                "passed_checks": sum(1 for r in self.results if r.get('passed', False)),
                "failed_checks": sum(1 for r in self.results if not r.get('passed', True)),
            }
        }
        
        # 保存报告
        report_file = self.skill_path.parent / "simple_error_proof_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

def main():
    if len(sys.argv) != 2:
        print("用法: python simple_error_proof_audit.py <技能路径>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    auditor = SimpleErrorProofAudit(skill_path)
    report = auditor.run_audit()
    
    print(f"\n报告已保存: {skill_path}/../simple_error_proof_report.json")
    
    # 显示摘要
    summary = report.get('summary', {})
    print(f"\n检查摘要:")
    print(f"  总检查数: {summary.get('total_checks', 0)}")
    print(f"  通过检查: {summary.get('passed_checks', 0)}")
    print(f"  失败检查: {summary.get('failed_checks', 0)}")
    
    # 显示问题
    for result in report.get('results', []):
        if not result.get('passed', False):
            print(f"\n问题: {result.get('check')}")
            if 'error' in result:
                print(f"  错误: {result['error']}")
            if 'evidence' in result:
                print(f"  证据: {result['evidence']}")
    
    return 0 if report.get('all_passed', False) else 1

if __name__ == "__main__":
    sys.exit(main())