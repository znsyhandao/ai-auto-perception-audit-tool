#!/usr/bin/env python3
"""
防错工作流程框架 - 让错误不可能发生
"""

import os
import sys
import re
import json
import shutil
from pathlib import Path
from typing import List, Tuple, Callable, Any, Dict
import traceback
from datetime import datetime

class WorkflowError(Exception):
    """工作流程错误"""
    pass

class ValidationError(Exception):
    """验证错误"""
    pass

class AtomicOperationError(Exception):
    """原子操作错误"""
    pass

class ErrorProofWorkflow:
    """防错工作流程 - 核心原则：让错误不可能发生"""
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.steps = []
        self.validations = []
        self.evidence = []
        self.backups = {}
        
    def add_step(self, operation: Callable, validation: Callable, description: str):
        """添加步骤和验证"""
        self.steps.append({
            "operation": operation,
            "validation": validation,
            "description": description
        })
        
    def execute_atomic(self):
        """原子性执行：要么全部成功，要么全部失败"""
        results = []
        
        try:
            # 执行每个步骤
            for i, step in enumerate(self.steps):
                step_desc = step["description"]
                print(f"[STEP {i+1}] {step_desc}")
                
                # 执行操作
                result = step["operation"]()
                results.append(result)
                
                # 立即验证
                if not step["validation"](result):
                    raise ValidationError(f"步骤{i+1}验证失败: {step_desc}")
                
                # 记录证据
                self.evidence.append({
                    "step": i+1,
                    "description": step_desc,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "status": "passed"
                })
                
                print(f"  [OK] 步骤{i+1}通过")
            
            # 所有步骤成功
            print(f"\n[SUCCESS] 工作流程 '{self.workflow_name}' 全部步骤通过")
            return results
            
        except Exception as e:
            # 记录失败
            self.evidence.append({
                "step": i+1,
                "description": step_desc,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            })
            
            print(f"\n[FAILURE] 工作流程 '{self.workflow_name}' 在第{i+1}步失败")
            print(f"错误: {e}")
            
            # 回滚（如果有备份）
            self.rollback()
            
            raise WorkflowError(f"工作流程失败: {e}")
    
    def rollback(self):
        """回滚到之前的状态"""
        if self.backups:
            print("[ROLLBACK] 执行回滚...")
            for file_path, backup_path in self.backups.items():
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_path)
                    print(f"  恢复: {file_path}")
    
    def create_backup(self, file_path: str):
        """创建文件备份"""
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            self.backups[file_path] = backup_path
            return backup_path
        return None
    
    def get_evidence_report(self) -> Dict:
        """获取证据报告"""
        return {
            "workflow_name": self.workflow_name,
            "execution_time": datetime.now().isoformat(),
            "total_steps": len(self.steps),
            "passed_steps": sum(1 for e in self.evidence if e["status"] == "passed"),
            "evidence": self.evidence,
            "overall_status": "success" if all(e["status"] == "passed" for e in self.evidence) else "failed"
        }

class VersionUpdateWorkflow(ErrorProofWorkflow):
    """版本号更新防错工作流程"""
    
    def __init__(self, new_version: str, skill_path: str):
        super().__init__(f"版本号更新到 {new_version}")
        self.new_version = new_version
        self.skill_path = Path(skill_path)
        
        # 定义需要更新的文件
        self.files_to_update = [
            self.skill_path / "skill.py",
            self.skill_path / "config.yaml",
            self.skill_path / "CHANGELOG.md",
            self.skill_path / "SKILL.md",
            self.skill_path / "README.md"
        ]
        
        # 设置工作流程步骤
        self.setup_steps()
    
    def setup_steps(self):
        """设置工作流程步骤"""
        
        # 步骤1: 验证新版本号格式
        self.add_step(
            operation=lambda: self.validate_version_format(self.new_version),
            validation=lambda result: result is True,
            description=f"验证版本号格式: {self.new_version}"
        )
        
        # 步骤2: 备份所有文件
        self.add_step(
            operation=lambda: [self.create_backup(str(f)) for f in self.files_to_update if f.exists()],
            validation=lambda backups: len(backups) == len([f for f in self.files_to_update if f.exists()]),
            description="备份所有需要更新的文件"
        )
        
        # 步骤3: 更新skill.py
        self.add_step(
            operation=lambda: self.update_file_version(self.skill_path / "skill.py", self.new_version),
            validation=lambda result: self.verify_file_version(self.skill_path / "skill.py", self.new_version),
            description="更新skill.py版本号"
        )
        
        # 步骤4: 更新config.yaml
        self.add_step(
            operation=lambda: self.update_file_version(self.skill_path / "config.yaml", self.new_version),
            validation=lambda result: self.verify_file_version(self.skill_path / "config.yaml", self.new_version),
            description="更新config.yaml版本号"
        )
        
        # 步骤5: 更新CHANGELOG.md
        self.add_step(
            operation=lambda: self.update_changelog_version(self.new_version),
            validation=lambda result: self.verify_file_version(self.skill_path / "CHANGELOG.md", self.new_version),
            description="更新CHANGELOG.md版本号"
        )
        
        # 步骤6: 更新SKILL.md
        self.add_step(
            operation=lambda: self.update_file_version(self.skill_path / "SKILL.md", self.new_version),
            validation=lambda result: self.verify_file_version(self.skill_path / "SKILL.md", self.new_version),
            description="更新SKILL.md版本号"
        )
        
        # 步骤7: 更新README.md
        self.add_step(
            operation=lambda: self.update_file_version(self.skill_path / "README.md", self.new_version),
            validation=lambda result: self.verify_file_version(self.skill_path / "README.md", self.new_version),
            description="更新README.md版本号"
        )
        
        # 步骤8: 验证所有文件版本一致
        self.add_step(
            operation=lambda: self.verify_all_versions_match(self.new_version),
            validation=lambda result: result is True,
            description="验证所有文件版本号一致"
        )
        
        # 步骤9: 验证无语法错误
        self.add_step(
            operation=lambda: self.check_syntax_errors(),
            validation=lambda result: result is True,
            description="验证所有Python文件无语法错误"
        )
        
        # 步骤10: 验证文档语言一致性
        self.add_step(
            operation=lambda: self.check_documentation_language(),
            validation=lambda result: result is True,
            description="验证文档语言一致性（全英文）"
        )
    
    def validate_version_format(self, version: str) -> bool:
        """验证版本号格式"""
        pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(pattern, version):
            raise ValidationError(f"无效的版本号格式: {version}")
        return True
    
    def update_file_version(self, file_path: Path, new_version: str) -> bool:
        """更新文件版本号"""
        if not file_path.exists():
            print(f"  警告: 文件不存在: {file_path}")
            return False
        
        content = file_path.read_text(encoding='utf-8')
        
        # 根据文件类型使用不同的更新策略
        if file_path.name == "skill.py":
            # 更新 skill.py 中的 version = "x.x.x"
            content = re.sub(r'version\s*=\s*["\']\d+\.\d+\.\d+["\']', f'version = "{new_version}"', content)
        
        elif file_path.name == "config.yaml":
            # 更新 config.yaml 中的 version: "x.x.x"
            content = re.sub(r'version:\s*["\']\d+\.\d+\.\d+["\']', f'version: "{new_version}"', content)
        
        elif file_path.name == "CHANGELOG.md":
            # 更新 CHANGELOG.md 中的当前版本号
            # 查找 "Current Version: x.x.x"
            content = re.sub(r'Current Version:\s*\d+\.\d+\.\d+', f'Current Version: {new_version}', content)
            
            # 添加新版本记录（如果不存在）
            if f'## [{new_version}]' not in content:
                # 在适当位置插入新版本
                new_entry = f'\n## [{new_version}] - {datetime.now().strftime("%Y-%m-%d")}\n### Added\n- Initial release\n'
                content = content.replace('## [Unreleased]', f'## [Unreleased]\n\n{new_entry}')
        
        elif file_path.name in ["SKILL.md", "README.md"]:
            # 更新其他文档中的版本号
            content = re.sub(r'Version:\s*\d+\.\d+\.\d+', f'Version: {new_version}', content, flags=re.IGNORECASE)
            content = re.sub(r'version\s+\d+\.\d+\.\d+', f'version {new_version}', content, flags=re.IGNORECASE)
        
        file_path.write_text(content, encoding='utf-8')
        return True
    
    def update_changelog_version(self, new_version: str) -> bool:
        """专门更新CHANGELOG.md"""
        changelog_path = self.skill_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            print("  警告: CHANGELOG.md不存在")
            return False
        
        content = changelog_path.read_text(encoding='utf-8')
        
        # 确保是英文
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        if chinese_pattern.search(content):
            print("  警告: CHANGELOG.md中有中文，建议翻译为英文")
            # 这里可以添加自动翻译或警告
        
        # 更新当前版本号
        content = re.sub(r'Current Version:\s*\d+\.\d+\.\d+', f'Current Version: {new_version}', content)
        
        changelog_path.write_text(content, encoding='utf-8')
        return True
    
    def verify_file_version(self, file_path: Path, expected_version: str) -> bool:
        """验证文件版本号"""
        if not file_path.exists():
            return False
        
        content = file_path.read_text(encoding='utf-8')
        
        # 检查版本号
        patterns = [
            r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # skill.py
            r'version:\s*["\'](\d+\.\d+\.\d+)["\']',     # config.yaml
            r'Current Version:\s*(\d+\.\d+\.\d+)',       # CHANGELOG.md
            r'Version:\s*(\d+\.\d+\.\d+)',              # 其他文档
            r'version\s+(\d+\.\d+\.\d+)'                # 其他格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match and match.group(1) == expected_version:
                return True
        
        return False
    
    def verify_all_versions_match(self, expected_version: str) -> bool:
        """验证所有文件版本号一致"""
        for file_path in self.files_to_update:
            if file_path.exists():
                if not self.verify_file_version(file_path, expected_version):
                    print(f"  错误: {file_path.name} 版本号不匹配")
                    return False
        
        print(f"  所有文件版本号一致: {expected_version}")
        return True
    
    def check_syntax_errors(self) -> bool:
        """检查语法错误"""
        python_files = list(self.skill_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                compile(py_file.read_text(encoding='utf-8'), str(py_file), 'exec')
            except SyntaxError as e:
                print(f"  语法错误: {py_file}:{e.lineno} - {e.msg}")
                return False
        
        print("  所有Python文件无语法错误")
        return True
    
    def check_documentation_language(self) -> bool:
        """检查文档语言一致性"""
        doc_files = [
            self.skill_path / "CHANGELOG.md",
            self.skill_path / "README.md",
            self.skill_path / "SKILL.md"
        ]
        
        issues = []
        
        for doc_file in doc_files:
            if doc_file.exists():
                content = doc_file.read_text(encoding='utf-8')
                
                # 检测中文字符
                chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
                
                if chinese_chars:
                    # 检查是否是Keep a Changelog文件
                    if doc_file.name == "CHANGELOG.md" and "Keep a Changelog" in content:
                        issues.append(f"{doc_file.name}: Keep a Changelog文件中有中文")
                    
                    # 检查中英文混合
                    english_words = re.findall(r'\b[a-zA-Z]{3,}\b', content)
                    if english_words and chinese_chars:
                        issues.append(f"{doc_file.name}: 中英文混合")
        
        if issues:
            for issue in issues:
                print(f"  语言问题: {issue}")
            return False
        
        print("  所有文档语言一致（全英文）")
        return True

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python error_proof_workflow.py <新版本号> <技能路径>")
        print("示例: python error_proof_workflow.py 2.4.2 D:/openclaw/releases/AISleepGen_2.4.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    skill_path = sys.argv[2]
    
    print("=" * 80)
    print("防错工作流程 - 版本号更新")
    print("=" * 80)
    print(f"新版本号: {new_version}")
    print(f"技能路径: {skill_path}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # 创建工作流程
        workflow = VersionUpdateWorkflow(new_version, skill_path)
        
        # 执行工作流程
        results = workflow.execute_atomic()
        
        # 生成证据报告
        report = workflow.get_evidence_report()
        
        # 保存报告
        report_file = Path(skill_path) / "version_update_evidence.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SUCCESS] 版本号更新完成")
        print(f"证据报告: {report_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n[FAILURE] 版本号更新失败: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())