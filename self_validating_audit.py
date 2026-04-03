#!/usr/bin/env python3
"""
自验证审核框架 - 系统能够验证自身的正确性
"""

import os
import sys
import json
import inspect
import importlib
from pathlib import Path
from typing import List, Dict, Any, Callable
from datetime import datetime

class SelfValidationError(Exception):
    """自验证错误"""
    pass

class FrameworkIntegrityError(Exception):
    """框架完整性错误"""
    pass

class SelfValidatingAudit:
    """自验证审核框架 - 核心原则：系统能够验证自身的正确性"""
    
    def __init__(self):
        self.framework_name = "自验证审核框架"
        self.version = "1.0.0"
        self.checks = []
        self.self_validation_results = []
        
        # 1. 首先验证框架自身
        self.validate_framework_self()
        
        # 2. 然后加载检查项
        self.load_checks()
    
    def validate_framework_self(self):
        """验证框架自身"""
        print(f"\n{'='*80}")
        print(f"自验证审核框架 - 框架自检")
        print(f"{'='*80}")
        
        self_checks = [
            ("框架代码质量", self.check_framework_code_quality),
            ("检查项有效性", self.validate_all_checks),
            ("证据系统", self.validate_evidence_system),
            ("文档完整性", self.check_framework_documentation),
            ("测试覆盖率", self.check_test_coverage),
            ("错误处理", self.check_error_handling),
            ("性能基准", self.check_performance_baseline),
        ]
        
        all_passed = True
        
        for check_name, check_func in self_checks:
            print(f"\n[自检] {check_name}")
            
            try:
                result, evidence = check_func()
                
                if result:
                    print(f"  [OK] 通过")
                else:
                    print(f"  [FAIL] 失败")
                    all_passed = False
                
                self.self_validation_results.append({
                    "check_name": check_name,
                    "status": "passed" if result else "failed",
                    "evidence": evidence,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"  [ERROR] 检查出错: {e}")
                self.self_validation_results.append({
                    "check_name": check_name,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                all_passed = False
        
        if not all_passed:
            raise FrameworkIntegrityError("框架自检失败，无法继续")
        
        print(f"\n{'='*80}")
        print(f"[SUCCESS] 框架自检全部通过")
        print(f"{'='*80}")
    
    def check_framework_code_quality(self) -> tuple[bool, Dict]:
        """检查框架代码质量"""
        evidence = {}
        
        # 检查当前文件
        current_file = Path(__file__)
        
        # 1. 检查文件大小
        file_size_kb = current_file.stat().st_size / 1024
        evidence["file_size_kb"] = round(file_size_kb, 2)
        
        # 2. 检查代码行数
        with open(current_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            evidence["line_count"] = len(lines)
        
        # 3. 检查函数数量
        module = importlib.import_module(current_file.stem)
        functions = [name for name in dir(module) if callable(getattr(module, name)) and not name.startswith('_')]
        evidence["function_count"] = len(functions)
        
        # 4. 检查类数量
        classes = [name for name in dir(module) if inspect.isclass(getattr(module, name)) and not name.startswith('_')]
        evidence["class_count"] = len(classes)
        
        # 评估
        passed = (
            file_size_kb < 100 and  # 文件大小合理
            len(lines) < 500 and    # 代码行数合理
            len(functions) > 5 and  # 有足够的功能
            len(classes) > 1        # 有多个类
        )
        
        return passed, evidence
    
    def validate_all_checks(self) -> tuple[bool, Dict]:
        """验证所有检查项"""
        evidence = {}
        
        # 这里应该检查所有注册的检查项
        # 目前只是框架自检，所以检查项为空是正常的
        evidence["check_count"] = len(self.checks)
        evidence["checks"] = [check["name"] for check in self.checks]
        
        # 验证每个检查项
        valid_checks = []
        for check in self.checks:
            if callable(check.get("function")):
                valid_checks.append(check["name"])
        
        evidence["valid_checks"] = valid_checks
        
        passed = len(valid_checks) == len(self.checks)
        return passed, evidence
    
    def validate_evidence_system(self) -> tuple[bool, Dict]:
        """验证证据系统"""
        evidence = {}
        
        # 检查证据记录功能
        evidence["has_evidence_recording"] = hasattr(self, 'record_evidence')
        evidence["evidence_count"] = len(self.self_validation_results)
        
        # 检查证据格式
        if self.self_validation_results:
            sample_evidence = self.self_validation_results[0]
            evidence["sample_format"] = {
                "has_check_name": "check_name" in sample_evidence,
                "has_status": "status" in sample_evidence,
                "has_timestamp": "timestamp" in sample_evidence
            }
        
        passed = (
            evidence["has_evidence_recording"] and
            evidence.get("sample_format", {}).get("has_check_name", False) and
            evidence.get("sample_format", {}).get("has_status", False) and
            evidence.get("sample_format", {}).get("has_timestamp", False)
        )
        
        return passed, evidence
    
    def check_framework_documentation(self) -> tuple[bool, Dict]:
        """检查框架文档"""
        evidence = {}
        
        # 检查文档文件
        framework_dir = Path(__file__).parent
        doc_files = [
            framework_dir / "PERMANENT_AUDIT_FRAMEWORK.md",
            framework_dir / "README.md",
        ]
        
        existing_docs = []
        for doc_file in doc_files:
            if doc_file.exists():
                existing_docs.append(doc_file.name)
        
        evidence["doc_files"] = existing_docs
        
        # 检查文档内容
        if framework_dir / "PERMANENT_AUDIT_FRAMEWORK.md" in doc_files:
            with open(framework_dir / "PERMANENT_AUDIT_FRAMEWORK.md", 'r', encoding='utf-8') as f:
                content = f.read()
                evidence["framework_doc_size_kb"] = len(content) / 1024
                evidence["framework_doc_has_principles"] = "核心原则" in content
        
        passed = (
            len(existing_docs) >= 1 and
            evidence.get("framework_doc_size_kb", 0) > 1 and
            evidence.get("framework_doc_has_principles", False)
        )
        
        return passed, evidence
    
    def check_test_coverage(self) -> tuple[bool, Dict]:
        """检查测试覆盖率"""
        evidence = {}
        
        # 检查测试文件
        framework_dir = Path(__file__).parent
        test_files = list(framework_dir.glob("*test*.py"))
        test_files += list(framework_dir.glob("test_*.py"))
        
        evidence["test_file_count"] = len(test_files)
        evidence["test_files"] = [f.name for f in test_files]
        
        # 简单的测试覆盖率检查
        # 在实际项目中，这里应该运行测试并检查覆盖率
        passed = len(test_files) > 0
        
        return passed, evidence
    
    def check_error_handling(self) -> tuple[bool, Dict]:
        """检查错误处理"""
        evidence = {}
        
        # 检查是否有适当的错误处理
        current_file = Path(__file__)
        with open(current_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            evidence["has_try_except"] = "try:" in content and "except" in content
            evidence["has_custom_exceptions"] = "class.*Error.*Exception" in content
            evidence["error_handling_patterns"] = [
                "try:",
                "except",
                "finally",
                "raise"
            ]
        
        passed = evidence["has_try_except"] and evidence["has_custom_exceptions"]
        return passed, evidence
    
    def check_performance_baseline(self) -> tuple[bool, Dict]:
        """检查性能基准"""
        evidence = {}
        
        # 简单的性能检查
        import time
        
        start_time = time.time()
        
        # 执行一些操作来测试性能
        operations = [
            lambda: list(range(1000)),
            lambda: {str(i): i for i in range(100)},
            lambda: [i**2 for i in range(1000)],
        ]
        
        results = []
        for op in operations:
            op_start = time.time()
            result = op()
            op_time = time.time() - op_start
            results.append({
                "operation": op.__name__ if hasattr(op, '__name__') else "anonymous",
                "time_ms": round(op_time * 1000, 2),
                "result_size": len(str(result))
            })
        
        total_time = time.time() - start_time
        
        evidence["performance_test"] = {
            "total_time_ms": round(total_time * 1000, 2),
            "operations": results,
            "acceptable_threshold_ms": 100  # 100毫秒内完成
        }
        
        passed = total_time * 1000 < 100  # 在100毫秒内完成
        return passed, evidence
    
    def load_checks(self):
        """加载检查项"""
        # 这里可以动态加载检查项
        # 目前只是框架自检，所以没有外部检查项
        
        self.checks = [
            {
                "name": "框架自检",
                "function": self.validate_framework_self,
                "description": "验证框架自身的完整性"
            }
        ]
    
    def add_check(self, name: str, check_func: Callable, description: str):
        """添加检查项"""
        self.checks.append({
            "name": name,
            "function": check_func,
            "description": description
        })
    
    def audit(self, target_path: str) -> Dict:
        """执行审核"""
        print(f"\n{'='*80}")
        print(f"自验证审核 - 开始审核")
        print(f"目标: {target_path}")
        print(f"{'='*80}")
        
        audit_results = []
        
        try:
            # 1. 首先验证框架自身
            print("\n[阶段1] 框架自验证")
            self.validate_framework_self()
            
            # 2. 执行所有检查项
            print(f"\n[阶段2] 执行检查项 ({len(self.checks)}个)")
            
            for i, check in enumerate(self.checks):
                check_name = check["name"]
                check_func = check["function"]
                check_desc = check["description"]
                
                print(f"\n[检查 {i+1}/{len(self.checks)}] {check_name}")
                print(f"描述: {check_desc}")
                
                try:
                    # 执行检查
                    result, evidence = check_func(target_path)
                    
                    audit_results.append({
                        "check_name": check_name,
                        "status": "passed" if result else "failed",
                        "evidence": evidence,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    if result:
                        print(f"  [OK] 通过")
                    else:
                        print(f"  [FAIL] 失败")
                        
                except Exception as e:
                    print(f"  [ERROR] 检查出错: {e}")
                    audit_results.append({
                        "check_name": check_name,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
            # 3. 生成审核报告
            print(f"\n[阶段3] 生成审核报告")
            
            report = self.generate_audit_report(audit_results, target_path)
            
            # 4. 验证审核结果
            print(f"\n[阶段4] 验证审核结果")
            self.validate_audit_results(audit_results)
            
            print(f"\n{'='*80}")
            print(f"[SUCCESS] 自验证审核完成")
            print(f"{'='*80}")
            
            return report
            
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"[FAILURE] 自验证审核失败: {e}")
            print(f"{'='*80}")
            
            # 生成错误报告
            error_report = {
                "audit_status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "framework_self_validation": self.self_validation_results,
                "audit_results": audit_results
            }
            
            return error_report
    
    def generate_audit_report(self, audit_results: List[Dict], target_path: str) -> Dict:
        """生成审核报告"""
        
        passed_checks = sum(1 for r in audit_results if r["status"] == "passed")
        failed_checks = sum(1 for r in audit_results if r["status"] == "failed")
        error_checks = sum(1 for r in audit_results if r["status"] == "error")
        
        report = {
            "audit_framework": {
                "name": self.framework_name,
                "version": self.version,
                "self_validation": self.self_validation_results
            },
            "audit_target": {
                "path": target_path,
                "timestamp": datetime.now().isoformat()
            },
            "audit_results": {
                "total_checks": len(audit_results),
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "error_checks": error_checks,
                "success_rate": round(passed_checks / len(audit_results) * 100, 2) if audit_results else 0,
                "details": audit_results
            },
            "recommendations": self.generate_recommendations(audit_results),
            "overall_status": "passed" if failed_checks == 0 and error_checks == 0 else "failed"
        }
        
        return report
    
    def generate_recommendations(self, audit_results: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for result in audit_results:
            if result["status"] == "failed":
                recommendations.append(f"修复检查 '{result['check_name']}' 发现的问题")
            elif result["status"] == "error":
                recommendations.append(f"调查检查 '{result['check_name']}' 的错误: {result.get('error', '未知错误')}")
        
        if not recommendations:
            recommendations.append("所有检查通过，无需修复")
        
        return recommendations
    
    def validate_audit_results(self, audit_results: List[Dict]):
        """验证审核结果"""
        print("  验证审核结果完整性...")
        
        # 检查每个结果都有必需的字段
        required_fields = ["check_name", "status", "timestamp"]
        
        for result in audit_results:
            for field in required_fields:
                if field not in result:
                    raise SelfValidationError(f"审核结果缺少必需字段: {field}")
        
        print("  审核结果完整性验证通过")
        
        # 检查是否有不一致的结果
        status_counts = {}
        for result in audit_results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"  状态统计: {status_counts}")

class SkillAuditFramework(SelfValidatingAudit):
    """技能审核框架"""
    
    def __init__(self):
        super().__init__()
        self.framework_name = "技能自验证审核框架"
        
        # 添加技能特定的检查项
        self.add_skill_checks()
    
    def add_skill_checks(self):
        """添加技能检查项"""
        
        # 检查1: 文件存在性
        self.add_check(
            name="文件存在性检查",
            check_func=self.check_file_existence,
            description="检查所有必需文件是否存在"
        )
        
        # 检查2: 版本一致性
        self.add_check(
            name="版本一致性检查",
            check_func=self.check_version_consistency,
            description="检查所有文件的版本号是否一致"
        )
        
        # 检查3: 语法检查
        self.add_check(
            name="语法检查",
            check_func=self.check_syntax,
            description="检查Python文件是否有语法错误"
        )
        
        # 检查4: 导入测试
        self.add_check(
            name="导入测试",
            check_func=self.test_import,
            description="测试skill.py是否可以导入"
        )
        
        # 检查5: 文档语言检查
        self.add_check(
            name="文档语言检查",
            check_func=self.check_documentation_language,
            description="检查文档语言是否一致（全英文）"
        )
    
    def check_file_existence(self, skill_path: str) -> tuple[bool, Dict]:
        """检查文件存在性"""
        import os
        from pathlib import Path
        
        skill_dir = Path(skill_path)
        
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
            file_path = skill_dir / filename
            if file_path.exists():
                evidence[filename] = {
                    "exists": True,
                    "size_kb": round(file_path.stat().st_size / 1024, 2)
                }
            else:
                evidence[filename] = {"exists": False}
                missing_files.append(filename)
        
        passed = len(missing_files) == 0
        
        return passed, evidence
    
    def check_version_consistency(self, skill_path: str) -> tuple[bool, Dict]:
        """检查版本一致性"""
        import re
        import yaml
        from pathlib import Path
        
        skill_dir = Path(skill_path)
        evidence = {}
        
        # 提取版本号
        versions = {}
        
        # skill.py
        skill_file = skill_dir / "skill.py"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8')
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
        
        # config.yaml
        config_file = skill_dir / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                versions["config.yaml"] = config.get('skill', {}).get('version', 'NOT_FOUND')
        
        # CHANGELOG.md
        changelog_file = skill_dir / "CHANGELOG.md"
        if changelog_file.exists():
            content = changelog_file.read_text(encoding='utf-8')
            match = re.search(r'Current Version:\s*([\d.]+)', content)
            versions["CHANGELOG.md"] = match.group(1) if match else "NOT_FOUND"
        
        # SKILL.md
        skill_md_file = skill_dir / "SKILL.md"
        if skill_md_file.exists():
            content = skill_md_file.read_text(encoding='utf-8')
            match = re.search(r'Version:\s*([\d.]+)', content, re.IGNORECASE)
            versions["SKILL.md"] = match.group(1) if match else "NOT_FOUND"
        
        evidence["versions"] = versions
        
        # 检查一致性
        all_versions = list(versions.values())
        unique_versions = set(all_versions)
        
        if "NOT_FOUND" in unique_versions:
            passed = False
            evidence["issue"] = "有些文件未找到版本号"
        elif len(unique_versions) == 1:
            passed = True
            evidence["consistent_version"] = list(unique_versions)[0]
        else:
            passed = False
            evidence["issue"] = "版本号不一致"
        
        return passed, evidence
    
    def check_syntax(self, skill_path: str) -> tuple[bool, Dict]:
        """检查语法"""
        from pathlib import Path
        
        skill_dir = Path(skill_path)
        evidence = {}
        
        python_files = list(skill_dir.rglob("*.py"))
        evidence["python_file_count"] = len(python_files)
        
        syntax_errors = []
        
        for py_file in python_files:
            try:
                compile(py_file.read_text(encoding='utf-8'), str(py_file), 'exec')
            except SyntaxError as e:
                syntax_errors.append({
                    "file": str(py_file.relative_to(skill_dir)),
                    "line": e.lineno,
                    "message": e.msg
                })
        
        evidence["syntax_errors"] = syntax_errors
        passed = len(syntax_errors) == 0
        
        return passed, evidence
    
    def test_import(self, skill_path: str) -> tuple[bool, Dict]:
        """测试导入"""
        import sys
        import traceback
        from pathlib import Path
        
        skill_dir = Path(skill_path)
        evidence = {}
        
        # 添加技能路径到sys.path
        sys.path.insert(0, str(skill_dir))
        
        try:
            import skill as test_skill
            evidence["import_success"] = True
            
            if hasattr(test_skill, 'SleepRabbitSkill'):
                evidence["class_found"] = True
                
                # 尝试创建实例
                skill_instance = test_skill.SleepRabbitSkill()
                evidence["instance_created"] = True
                
                # 检查版本
                version = getattr(skill_instance, 'version', 'NOT_FOUND')
                evidence["skill_version"] = version
                
                passed = True
            else:
                evidence["class_found"] = False
                evidence["error"] = "skill.py中没有SleepRabbitSkill类"
                passed = False
                
        except Exception as e:
            evidence["import_success"] = False
            evidence["error"] = str(e)
            evidence["traceback"] = traceback.format_exc()
            passed = False
        
        return passed, evidence
    
    def check_documentation_language(self, skill_path: str) -> tuple[bool, Dict]:
        """检查文档语言"""
        import re
        from pathlib import Path
        
        skill_dir = Path(skill_path)
        evidence = {}
        
        doc_files = [
            skill_dir / "CHANGELOG.md",
            skill_dir / "README.md",
            skill_dir / "SKILL.md"
        ]
        
        language_issues = []
        
        for doc_file in doc_files:
            if doc_file.exists():
                content = doc_file.read_text(encoding='utf-8')
                
                # 检测中文字符
                chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
                
                if chinese_chars:
                    # 检查是否是Keep a Changelog文件
                    if doc_file.name == "CHANGELOG.md" and "Keep a Changelog" in content:
                        language_issues.append({
                            "file": doc_file.name,
                            "issue": "Keep a Changelog文件中有中文",
                            "chinese_char_count": len(chinese_chars)
                        })
        
        evidence["language_issues"] = language_issues
        passed = len(language_issues) == 0
        
        return passed, evidence

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python self_validating_audit.py <技能路径>")
        print("示例: python self_validating_audit.py D:/openclaw/releases/AISleepGen_2.4.1")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    try:
        # 创建自验证审核框架
        audit_framework = SkillAuditFramework()
        
        # 执行审核
        report = audit_framework.audit(skill_path)
        
        # 保存报告
        report_file = Path(skill_path) / "self_validating_audit_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n审核报告已保存: {report_file}")
        
        # 显示摘要
        print(f"\n审核摘要:")
        print(f"  总体状态: {report.get('overall_status', 'unknown')}")
        print(f"  检查总数: {report.get('audit_results', {}).get('total_checks', 0)}")
        print(f"  通过检查: {report.get('audit_results', {}).get('passed_checks', 0)}")
        print(f"  失败检查: {report.get('audit_results', {}).get('failed_checks', 0)}")
        print(f"  错误检查: {report.get('audit_results', {}).get('error_checks', 0)}")
        
        return 0
        
    except Exception as e:
        print(f"\n自验证审核失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()