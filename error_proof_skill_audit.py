#!/usr/bin/env python3
"""
防错技能审核系统 - 最先进的防错审核
"""

import os
import sys
import json
import re
import yaml
import zipfile
import shutil
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Callable
import tempfile

class AuditError(Exception):
    """审核错误"""
    pass

class ValidationError(Exception):
    """验证错误"""
    pass

class AtomicOperationError(Exception):
    """原子操作错误"""
    pass

class ErrorProofSkillAudit:
    """防错技能审核 - 最先进的防错系统"""
    
    def __init__(self, skill_path: str, zip_path: str):
        self.skill_path = Path(skill_path)
        self.zip_path = Path(zip_path)
        self.evidence = []
        self.backups = {}
        self.results = []
        
        # 验证输入
        self.validate_inputs()
        
    def validate_inputs(self):
        """验证输入"""
        if not self.skill_path.exists():
            raise AuditError(f"技能路径不存在: {self.skill_path}")
        
        if not self.zip_path.exists():
            print(f"警告: ZIP文件不存在，将创建: {self.zip_path}")
    
    def execute_atomic_audit(self) -> Dict:
        """原子性审核：要么全部成功，要么全部失败"""
        print(f"\n{'='*80}")
        print(f"防错技能审核系统 - 开始审核")
        print(f"{'='*80}")
        print(f"技能路径: {self.skill_path}")
        print(f"ZIP文件: {self.zip_path}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        try:
            # 1. 备份关键文件
            self.backup_critical_files()
            
            # 2. 执行防错审核链
            audit_results = self.execute_error_proof_chain()
            
            # 3. 生成防错证据报告
            report = self.generate_error_proof_report(audit_results)
            
            # 4. 验证审核完整性
            self.validate_audit_integrity(audit_results)
            
            print(f"\n{'='*80}")
            print(f"[SUCCESS] 防错审核全部通过")
            print(f"{'='*80}")
            
            return report
            
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"[FAILURE] 防错审核失败: {e}")
            print(f"{'='*80}")
            
            # 自动回滚
            self.rollback_changes()
            
            # 生成错误报告
            error_report = self.generate_error_report(e)
            
            raise AuditError(f"防错审核失败: {e}") from e
    
    def backup_critical_files(self):
        """备份关键文件"""
        print("\n[阶段1] 备份关键文件")
        
        critical_files = [
            self.skill_path / "skill.py",
            self.skill_path / "config.yaml",
            self.skill_path / "CHANGELOG.md",
            self.skill_path / "SKILL.md",
            self.skill_path / "README.md"
        ]
        
        for file_path in critical_files:
            if file_path.exists():
                backup_path = self.create_backup(file_path)
                self.backups[str(file_path)] = backup_path
                print(f"  备份: {file_path.name} -> {backup_path.name}")
    
    def create_backup(self, file_path: Path) -> Path:
        """创建备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def execute_error_proof_chain(self) -> List[Dict]:
        """执行防错审核链"""
        print("\n[阶段2] 执行防错审核链")
        
        # 定义审核链
        audit_chain = [
            ("验证必需文件存在", self.check_required_files),
            ("验证版本一致性", self.check_version_consistency),
            ("验证语法正确性", self.check_syntax),
            ("验证导入功能", self.test_import),
            ("验证文档语言", self.check_documentation_language),
            ("验证历史遗留引用", self.check_historical_references),
            ("验证配置正确性", self.check_configuration),
            ("验证目录结构", self.check_directory_structure),
            ("创建ZIP包", self.create_zip_package),
            ("验证ZIP完整性", self.verify_zip_integrity),
            ("验证ZIP与文件夹一致性", self.verify_zip_folder_consistency),
            ("最终综合验证", self.final_comprehensive_check),
        ]
        
        results = []
        
        for i, (check_name, check_func) in enumerate(audit_chain, 1):
            print(f"\n[检查 {i}/{len(audit_chain)}] {check_name}")
            
            try:
                # 执行检查
                passed, evidence = check_func()
                
                # 立即验证
                if not passed:
                    raise ValidationError(f"检查失败: {check_name}")
                
                # 记录结果
                results.append({
                    "check_name": check_name,
                    "status": "passed",
                    "evidence": evidence,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"  [OK] 通过")
                
                # 记录证据
                self.evidence.append({
                    "step": i,
                    "check": check_name,
                    "result": "passed",
                    "evidence_summary": str(evidence)[:100]
                })
                
            except Exception as e:
                print(f"  [FAIL] 失败: {e}")
                
                results.append({
                    "check_name": check_name,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                raise ValidationError(f"审核链在第{i}步失败: {check_name}") from e
        
        return results
    
    def check_required_files(self) -> Tuple[bool, Dict]:
        """检查必需文件"""
        required_files = [
            "skill.py",
            "config.yaml",
            "SKILL.md",
            "README.md",
            "CHANGELOG.md",
            "LICENSE.txt"
        ]
        
        evidence = {}
        missing_files = []
        
        for filename in required_files:
            file_path = self.skill_path / filename
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                evidence[filename] = {
                    "exists": True,
                    "size_kb": round(size_kb, 2),
                    "path": str(file_path)
                }
            else:
                evidence[filename] = {"exists": False}
                missing_files.append(filename)
        
        passed = len(missing_files) == 0
        
        if missing_files:
            evidence["missing_files"] = missing_files
        
        return passed, evidence
    
    def check_version_consistency(self) -> Tuple[bool, Dict]:
        """检查版本一致性"""
        evidence = {}
        versions = {}
        
        # 提取所有文件的版本号
        files_to_check = [
            ("skill.py", r'version\s*=\s*["\']([^"\']+)["\']'),
            ("config.yaml", self.extract_config_version),
            ("CHANGELOG.md", r'Current Version:\s*([\d.]+)'),
            ("SKILL.md", (r'Version:\s*([\d.]+)', re.IGNORECASE)),
            ("README.md", (r'version\s+([\d.]+)', re.IGNORECASE)),
        ]
        
        for file_info in files_to_check:
            if len(file_info) == 3:
                filename, pattern, flags = file_info
            else:
                filename, pattern = file_info
                flags = 0
            
            file_path = self.skill_path / filename
            
            if not file_path.exists():
                versions[filename] = "FILE_NOT_FOUND"
                continue
            
            content = file_path.read_text(encoding='utf-8')
            
            if callable(pattern):
                # 如果是函数，调用它
                version = pattern(content)
                versions[filename] = version
            else:
                # 如果是正则表达式
                match = re.search(pattern, content, flags)
                versions[filename] = match.group(1) if match else "VERSION_NOT_FOUND"
        
        evidence["versions"] = versions
        
        # 检查一致性
        all_versions = list(versions.values())
        valid_versions = [v for v in all_versions if v not in ["FILE_NOT_FOUND", "VERSION_NOT_FOUND"]]
        
        if not valid_versions:
            return False, {"error": "未找到任何版本号", **evidence}
        
        unique_versions = set(valid_versions)
        
        if len(unique_versions) == 1:
            evidence["consistent_version"] = list(unique_versions)[0]
            passed = True
        else:
            evidence["inconsistent_versions"] = dict(versions)
            passed = False
        
        return passed, evidence
    
    def extract_config_version(self, content: str) -> str:
        """从config.yaml提取版本号"""
        try:
            config = yaml.safe_load(content)
            version = config.get('skill', {}).get('version', 'VERSION_NOT_FOUND')
            return version
        except Exception as e:
            return f"PARSE_ERROR: {e}"
    
    def check_syntax(self) -> Tuple[bool, Dict]:
        """检查语法"""
        evidence = {}
        syntax_errors = []
        
        python_files = list(self.skill_path.rglob("*.py"))
        evidence["python_file_count"] = len(python_files)
        
        for py_file in python_files:
            try:
                compile(py_file.read_text(encoding='utf-8'), str(py_file), 'exec')
            except SyntaxError as e:
                syntax_errors.append({
                    "file": str(py_file.relative_to(self.skill_path)),
                    "line": e.lineno,
                    "message": e.msg,
                    "error": str(e)
                })
        
        evidence["syntax_errors"] = syntax_errors
        passed = len(syntax_errors) == 0
        
        return passed, evidence
    
    def test_import(self) -> Tuple[bool, Dict]:
        """测试导入"""
        import sys
        
        evidence = {}
        
        # 添加技能路径到sys.path
        original_sys_path = sys.path.copy()
        sys.path.insert(0, str(self.skill_path))
        
        try:
            import skill as test_skill
            evidence["import_success"] = True
            
            if hasattr(test_skill, 'SleepRabbitSkill'):
                evidence["class_found"] = True
                
                # 尝试创建实例
                try:
                    skill_instance = test_skill.SleepRabbitSkill()
                    evidence["instance_created"] = True
                    
                    # 检查版本
                    version = getattr(skill_instance, 'version', 'NOT_FOUND')
                    evidence["skill_version"] = version
                    
                    # 检查名称
                    name = getattr(skill_instance, 'name', 'NOT_FOUND')
                    evidence["skill_name"] = name
                    
                except Exception as e:
                    evidence["instance_error"] = str(e)
                    evidence["instance_created"] = False
            else:
                evidence["class_found"] = False
            
        except Exception as e:
            evidence["import_success"] = False
            evidence["import_error"] = str(e)
            evidence["traceback"] = traceback.format_exc()
        
        finally:
            # 恢复sys.path
            sys.path = original_sys_path
        
        passed = (
            evidence.get("import_success", False) and
            evidence.get("class_found", False) and
            evidence.get("instance_created", False)
        )
        
        return passed, evidence
    
    def check_documentation_language(self) -> Tuple[bool, Dict]:
        """检查文档语言"""
        evidence = {}
        language_issues = []
        
        doc_files = [
            self.skill_path / "CHANGELOG.md",
            self.skill_path / "README.md",
            self.skill_path / "SKILL.md"
        ]
        
        for doc_file in doc_files:
            if doc_file.exists():
                content = doc_file.read_text(encoding='utf-8')
                
                # 检测中文字符
                chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
                
                if chinese_chars:
                    issue = {
                        "file": doc_file.name,
                        "chinese_char_count": len(chinese_chars),
                        "sample": content[:200]
                    }
                    
                    # 检查是否是Keep a Changelog文件
                    if doc_file.name == "CHANGELOG.md" and "Keep a Changelog" in content:
                        issue["issue"] = "Keep a Changelog文件中有中文"
                    
                    language_issues.append(issue)
        
        evidence["language_issues"] = language_issues
        passed = len(language_issues) == 0
        
        return passed, evidence
    
    def check_historical_references(self) -> Tuple[bool, Dict]:
        """检查历史遗留引用"""
        evidence = {}
        found_references = []
        
        legacy_patterns = [
            "sleep-rabbit-secure.js",
            "test-plugin.js",
            "microservices",
            "ports 8008",
            "ports 8009",
            "ports 8030",
            "ports 8040",
            "Node wrapper",
            "JS wrapper",
            "REST APIs"
        ]
        
        # 检查所有.md文件
        for md_file in self.skill_path.rglob("*.md"):
            if md_file.exists():
                content = md_file.read_text(encoding='utf-8')
                
                for pattern in legacy_patterns:
                    if pattern.lower() in content.lower():
                        found_references.append({
                            "file": md_file.name,
                            "pattern": pattern,
                            "context": self.extract_context(content, pattern)
                        })
        
        evidence["historical_references"] = found_references
        passed = len(found_references) == 0
        
        return passed, evidence
    
    def extract_context(self, content: str, pattern: str, context_chars: int = 50) -> str:
        """提取上下文"""
        pattern_lower = pattern.lower()
        content_lower = content.lower()
        
        index = content_lower.find(pattern_lower)
        if index == -1:
            return "未找到"
        
        start = max(0, index - context_chars)
        end = min(len(content), index + len(pattern) + context_chars)
        
        return content[start:end]
    
    def check_configuration(self) -> Tuple[bool, Dict]:
        """检查配置"""
        evidence = {}
        config_issues = []
        
        config_file = self.skill_path / "config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                evidence["config_parsed"] = True
                
                # 检查必需字段
                required_fields = ["skill", "version", "name", "description"]
                skill_config = config.get('skill', {})
                
                for field in required_fields:
                    if field not in skill_config:
                        config_issues.append(f"缺失字段: skill.{field}")
                
                # 检查版本格式
                version = skill_config.get('version', '')
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    config_issues.append(f"无效的版本格式: {version}")
                
                evidence["skill_config"] = skill_config
                
            except Exception as e:
                evidence["config_parsed"] = False
                evidence["config_error"] = str(e)
                config_issues.append(f"配置文件解析错误: {e}")
        else:
            config_issues.append("配置文件不存在")
        
        evidence["config_issues"] = config_issues
        passed = len(config_issues) == 0
        
        return passed, evidence
    
    def check_directory_structure(self) -> Tuple[bool, Dict]:
        """检查目录结构"""
        evidence = {}
        structure_issues = []
        
        # 检查必需目录
        required_dirs = ["utils", "data", "core"]
        
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # 检查目录是否为空
                files_in_dir = list(dir_path.rglob("*"))
                if len(files_in_dir) == 0:
                    structure_issues.append(f"目录为空: {dir_name}")
            else:
                structure_issues.append(f"缺失目录: {dir_name}")
        
        # 检查文件分布
        all_files = list(self.skill_path.rglob("*"))
        file_count = len([f for f in all_files if f.is_file()])
        dir_count = len([f for f in all_files if f.is_dir()])
        
        evidence["file_count"] = file_count
        evidence["dir_count"] = dir_count
        evidence["total_items"] = len(all_files)
        
        if file_count < 10:
            structure_issues.append(f"文件数量过少: {file_count}")
        
        evidence["structure_issues"] = structure_issues
        passed = len(structure_issues) == 0
        
        return passed, evidence
    
    def create_zip_package(self) -> Tuple[bool, Dict]:
        """创建ZIP包"""
        evidence = {}
        
        # 如果ZIP文件已存在，删除它
        if self.zip_path.exists():
            self.zip_path.unlink()
        
        try:
            # 创建ZIP包
            with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.skill_path.rglob("*"):
                    if file_path.is_file():
                        # 计算相对路径
                        arcname = file_path.relative_to(self.skill_path)
                        zipf.write(file_path, arcname)
            
            zip_size = self.zip_path.stat().st_size
            zip_size_mb = zip_size / (1024 * 1024)
            
            evidence["zip_created"] = True
            evidence["zip_size_bytes"] = zip_size
            evidence["zip_size_mb"] = round(zip_size_mb, 2)
            evidence["zip_path"] = str(self.zip_path)
            
            print(f"  创建ZIP包: {self.zip_path.name} ({zip_size_mb:.2f} MB)")
            
            passed = True
            
        except Exception as e:
            evidence["zip_created"] = False
            evidence["zip_error"] = str(e)
            passed = False
        
        return passed, evidence
    
    def verify_zip_integrity(self) -> Tuple[bool, Dict]:
        """验证ZIP完整性"""
        evidence = {}
        
        if not self.zip_path.exists():
            evidence["error"] = "ZIP文件不存在"
            return False, evidence
        
        try:
            # 验证ZIP文件
            with zipfile.ZipFile(self.zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                evidence["file_count_in_zip"] = len(file_list)
                evidence["file_list_sample"] = file_list[:10]  # 只显示前10个文件
                
                # 检查必需文件是否在ZIP中
                required_files = ["skill.py", "config.yaml", "SKILL.md", "README.md", "CHANGELOG.md"]
                missing_in_zip = []
                
                for req_file in required_files:
                    if not any(req_file in f for f in file_list):
                        missing_in_zip.append(req_file)
                
                if missing_in_zip:
                    evidence["missing_in_zip"] = missing_in_zip
                    return False, evidence
            
            evidence["zip_integrity"] = True
            passed = True
            
        except zipfile.BadZipFile as e:
            evidence["zip_integrity"] = False
            evidence["error"] = f"ZIP文件损坏: {e}"
            passed = False
        
        return passed, evidence
    
    def verify_zip_folder_consistency(self) -> Tuple[bool, Dict]:
        """验证ZIP与文件夹一致性"""
        evidence = {}
        differences = []
        
        if not self.zip_path.exists():
            evidence["error"] = "ZIP文件不存在"
            return False, evidence
        
        # 创建临时目录解压ZIP
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # 解压ZIP
            with zipfile.ZipFile(self.zip_path, 'r') as zipf:
                zipf.extractall(temp_dir_path)
            
            # 比较文件
            zip_files = set()
            for file_path in temp_dir_path.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(temp_dir_path)
                    zip_files.add(str(rel_path))
            
            skill_files = set()
            for file_path in self.skill_path.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.skill_path)
                    skill_files.add(str(rel_path))
            
            # 检查差异
            files_only_in_zip = zip_files - skill_files
            files_only_in_skill = skill_files - zip_files
            
            if files_only_in_zip:
                differences.append(f"ZIP中有但文件夹中没有: {list(files_only_in_zip)[:5]}")
            
            if files_only_in_skill:
                differences.append(f"文件夹中有但ZIP中没有: {list(files_only_in_skill)[:5]}")
            
            # 检查文件内容（抽样检查）
            common_files = zip_files & skill_files
            sample_files = list(common_files)[:3]  # 检查前3个共同文件
            
            content_differences = []
            for file_name in sample_files:
                zip_file_path = temp_dir_path / file_name
                skill_file_path = self.skill_path / file_name
                
                if zip_file_path.exists() and skill_file_path.exists():
                    zip_content = zip_file_path.read_text(encoding='utf-8')
                    skill_content = skill_file_path.read_text(encoding='utf-8')
                    
                    if zip_content != skill_content:
                        # 检查是否是空白/换行符差异
                        zip_clean = zip_content.replace('\r\n', '\n').strip()
                        skill_clean = skill_content.replace('\r\n', '\n').strip()
                        
                        if zip_clean != skill_clean:
                            content_differences.append(file_name)
            
            if content_differences:
                differences.append(f"内容不一致的文件: {content_differences}")
        
        evidence["differences"] = differences
        passed = len(differences) == 0
        
        return passed, evidence
    
    def final_comprehensive_check(self) -> Tuple[bool, Dict]:
        """最终综合验证"""
        evidence = {}
        final_issues = []
        
        # 1. 检查版本号策略
        changelog_file = self.skill_path / "CHANGELOG.md"
        if changelog_file.exists():
            content = changelog_file.read_text(encoding='utf-8')
            
            # 检查是否有失败的版本升级
            if "failed" in content.lower() or "失败" in content.lower():
                final_issues.append("CHANGELOG中提到失败版本")
        
        # 2. 检查安全声明一致性
        skill_md_file = self.skill_path / "SKILL.md"
        if skill_md_file.exists():
            content = skill_md_file.read_text(encoding='utf-8')
            
            # 检查安全声明
            security_keywords = ["security", "安全", "local", "network", "网络"]
            found_keywords = [kw for kw in security_keywords if kw.lower() in content.lower()]
            
            if found_keywords:
                evidence["security_keywords_found"] = found_keywords
        
        # 3. 检查文件编码
        text_files = list(self.skill_path.rglob("*.py")) + list(self.skill_path.rglob("*.md")) + list(self.skill_path.rglob("*.txt"))
        
        encoding_issues = []
        for file_path in text_files[:5]:  # 检查前5个文件
            try:
                content = file_path.read_text(encoding='utf-8')
                # 检查是否有编码问题
                if '�' in content:
                    encoding_issues.append(file_path.name)
            except UnicodeDecodeError:
                encoding_issues.append(f"{file_path.name}: Unicode解码错误")
        
        if encoding_issues:
            final_issues.append(f"编码问题: {encoding_issues}")
        
        evidence["final_issues"] = final_issues
        passed = len(final_issues) == 0
        
        return passed, evidence
    
    def rollback_changes(self):
        """回滚更改"""
        print("\n[回滚] 执行自动回滚...")
        
        if self.backups:
            for original_path, backup_path in self.backups.items():
                original_path = Path(original_path)
                backup_path = Path(backup_path)
                
                if backup_path.exists():
                    shutil.copy2(backup_path, original_path)
                    print(f"  恢复: {original_path.name}")
        
        # 删除可能创建的ZIP文件
        if self.zip_path.exists():
            try:
                self.zip_path.unlink()
                print(f"  删除: {self.zip_path.name}")
            except:
                pass
    
    def validate_audit_integrity(self, audit_results: List[Dict]):
        """验证审核完整性"""
        print("\n[阶段3] 验证审核完整性")
        
        # 检查所有结果都有必需字段
        required_fields = ["check_name", "status", "timestamp"]
        
        for result in audit_results:
            for field in required_fields:
                if field not in result:
                    raise ValidationError(f"审核结果缺少必需字段: {field}")
        
        # 检查通过率
        passed_checks = sum(1 for r in audit_results if r["status"] == "passed")
        total_checks = len(audit_results)
        
        if passed_checks != total_checks:
            raise ValidationError(f"审核完整性失败: {passed_checks}/{total_checks} 通过")
        
        print(f"  审核完整性验证通过: {passed_checks}/{total_checks}")
    
    def generate_error_proof_report(self, audit_results: List[Dict]) -> Dict:
        """生成防错证据报告"""
        print("\n[阶段4] 生成防错证据报告")
        
        passed_checks = sum(1 for r in audit_results if r["status"] == "passed")
        failed_checks = sum(1 for r in audit_results if r["status"] == "failed")
        error_checks = sum(1 for r in audit_results if r["status"] == "error")
        
        report = {
            "audit_system": "防错技能审核系统",
            "audit_version": "1.0.0",
            "audit_timestamp": datetime.now().isoformat(),
            "skill_path": str(self.skill_path),
            "zip_path": str(self.zip_path),
            "audit_summary": {
                "total_checks": len(audit_results),
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "error_checks": error_checks,
                "success_rate": round(passed_checks / len(audit_results) * 100, 2) if audit_results else 0
            },
            "audit_chain": audit_results,
            "evidence": self.evidence,
            "backups_created": list(self.backups.keys()),
            "overall_status": "passed" if failed_checks == 0 and error_checks == 0 else "failed",
            "recommendations": self.generate_recommendations(audit_results),
            "error_proof_features": [
                "原子性操作：要么全部成功，要么全部失败",
                "自动备份和回滚",
                "验证链：每个操作后立即验证",
                "完整性验证：审核过程自我验证",
                "详细证据记录：所有检查都有具体证据"
            ]
        }
        
        # 保存报告
        report_file = self.skill_path.parent / f"error_proof_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  防错证据报告已保存: {report_file}")
        
        return report
    
    def generate_recommendations(self, audit_results: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for result in audit_results:
            if result["status"] == "failed":
                recommendations.append(f"修复: {result['check_name']}")
            elif result["status"] == "error":
                recommendations.append(f"调查: {result['check_name']} - {result.get('error', '未知错误')}")
        
        if not recommendations:
            recommendations.append("所有检查通过，技能准备就绪")
        
        return recommendations
    
    def generate_error_report(self, error: Exception) -> Dict:
        """生成错误报告"""
        return {
            "audit_status": "failed",
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
            "backups_available": list(self.backups.keys()),
            "evidence_collected": self.evidence,
            "recommendation": "检查错误详情并修复问题后重试"
        }

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python error_proof_skill_audit.py <技能文件夹路径> <ZIP文件路径>")
        print("示例: python error_proof_skill_audit.py D:/openclaw/releases/AISleepGen_2.4.1 D:/openclaw/releases/AISleepGen_v2.4.1.zip")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    zip_path = sys.argv[2]
    
    try:
        # 创建防错审核系统
        auditor = ErrorProofSkillAudit(skill_path, zip_path)
        
        # 执行防错审核
        report = auditor.execute_atomic_audit()
        
        # 显示摘要
        print(f"\n{'='*80}")
        print("防错审核完成摘要")
        print(f"{'='*80}")
        print(f"总体状态: {report.get('overall_status', 'unknown')}")
        print(f"检查总数: {report.get('audit_summary', {}).get('total_checks', 0)}")
        print(f"通过检查: {report.get('audit_summary', {}).get('passed_checks', 0)}")
        print(f"失败检查: {report.get('audit_summary', {}).get('failed_checks', 0)}")
        print(f"错误检查: {report.get('audit_summary', {}).get('error_checks', 0)}")
        print(f"成功率: {report.get('audit_summary', {}).get('success_rate', 0)}%")
        print(f"{'='*80}")
        
        # 显示建议
        print("\n建议:")
        for i, rec in enumerate(report.get('recommendations', []), 1):
            print(f"  {i}. {rec}")
        
        return 0 if report.get('overall_status') == 'passed' else 1
        
    except Exception as e:
        print(f"\n防错审核系统错误: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())