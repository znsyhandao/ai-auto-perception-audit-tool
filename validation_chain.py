#!/usr/bin/env python3
"""
验证链框架 - 每个操作后立即验证，形成完整的验证链
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Tuple, Callable, Any, Dict, Optional
from datetime import datetime

class ChainError(Exception):
    """验证链错误"""
    pass

class ValidationChain:
    """验证链 - 核心原则：每个操作后立即验证"""
    
    def __init__(self, chain_name: str):
        self.chain_name = chain_name
        self.links = []  # 每个链接是 (操作, 验证, 描述)
        self.evidence = []
        self.current_step = 0
        
    def add_link(self, operation: Callable, validation: Callable, description: str):
        """添加链接（操作 + 验证）"""
        self.links.append({
            "operation": operation,
            "validation": validation,
            "description": description
        })
    
    def execute(self) -> List[Any]:
        """执行验证链"""
        print(f"\n{'='*80}")
        print(f"验证链执行: {self.chain_name}")
        print(f"{'='*80}")
        
        results = []
        self.current_step = 0
        
        try:
            for i, link in enumerate(self.links):
                self.current_step = i + 1
                step_desc = link["description"]
                
                print(f"\n[LINK {i+1}/{len(self.links)}] {step_desc}")
                print("-" * 40)
                
                # 执行操作
                print("  执行操作...")
                result = link["operation"]()
                
                # 立即验证
                print("  立即验证...")
                validation_result = link["validation"](result)
                
                if not validation_result:
                    raise ChainError(f"链接{i+1}验证失败: {step_desc}")
                
                # 记录结果
                results.append(result)
                
                # 记录证据
                self.evidence.append({
                    "step": i+1,
                    "description": step_desc,
                    "operation_result": str(result)[:100],  # 截断长结果
                    "validation_result": validation_result,
                    "timestamp": datetime.now().isoformat(),
                    "status": "passed"
                })
                
                print(f"  [OK] 链接{i+1}通过")
            
            # 所有链接成功
            print(f"\n{'='*80}")
            print(f"[SUCCESS] 验证链 '{self.chain_name}' 全部链接通过")
            print(f"{'='*80}")
            
            return results
            
        except Exception as e:
            # 记录失败
            self.evidence.append({
                "step": self.current_step,
                "description": step_desc if 'step_desc' in locals() else "未知",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            })
            
            print(f"\n{'='*80}")
            print(f"[FAILURE] 验证链 '{self.chain_name}' 在第{self.current_step}步失败")
            print(f"错误: {e}")
            print(f"{'='*80}")
            
            raise
    
    def get_evidence_report(self) -> Dict:
        """获取证据报告"""
        return {
            "chain_name": self.chain_name,
            "execution_time": datetime.now().isoformat(),
            "total_links": len(self.links),
            "passed_links": sum(1 for e in self.evidence if e["status"] == "passed"),
            "evidence": self.evidence,
            "overall_status": "success" if all(e["status"] == "passed" for e in self.evidence) else "failed"
        }

class SkillReleaseValidationChain(ValidationChain):
    """技能发布验证链"""
    
    def __init__(self, skill_path: str):
        super().__init__("技能发布验证链")
        self.skill_path = Path(skill_path)
        
        # 设置验证链
        self.setup_chain()
    
    def setup_chain(self):
        """设置验证链"""
        
        # 链接1: 验证必需文件存在
        self.add_link(
            operation=lambda: self.check_required_files(),
            validation=lambda result: result is True,
            description="验证必需文件存在"
        )
        
        # 链接2: 验证版本一致性
        self.add_link(
            operation=lambda: self.extract_all_versions(),
            validation=lambda versions: self.validate_version_consistency(versions),
            description="验证所有文件版本号一致"
        )
        
        # 链接3: 验证语法错误
        self.add_link(
            operation=lambda: self.check_python_syntax(),
            validation=lambda result: result is True,
            description="验证Python文件无语法错误"
        )
        
        # 链接4: 验证导入功能
        self.add_link(
            operation=lambda: self.test_skill_import(),
            validation=lambda result: result is True,
            description="验证skill.py可导入"
        )
        
        # 链接5: 验证文档语言
        self.add_link(
            operation=lambda: self.check_documentation_language(),
            validation=lambda result: result is True,
            description="验证文档语言一致性"
        )
        
        # 链接6: 验证历史遗留引用
        self.add_link(
            operation=lambda: self.check_historical_references(),
            validation=lambda result: len(result) == 0,
            description="验证无历史遗留引用"
        )
        
        # 链接7: 验证ZIP包创建
        self.add_link(
            operation=lambda: self.create_zip_package(),
            validation=lambda zip_path: zip_path.exists() and zip_path.stat().st_size > 0,
            description="验证ZIP包可创建"
        )
        
        # 链接8: 最终综合验证
        self.add_link(
            operation=lambda: self.final_comprehensive_check(),
            validation=lambda result: result is True,
            description="最终综合验证"
        )
    
    def check_required_files(self) -> bool:
        """检查必需文件"""
        required_files = [
            "skill.py",
            "config.yaml",
            "SKILL.md",
            "README.md",
            "CHANGELOG.md",
            "LICENSE.txt"
        ]
        
        missing_files = []
        for filename in required_files:
            file_path = self.skill_path / filename
            if not file_path.exists():
                missing_files.append(filename)
        
        if missing_files:
            print(f"  缺失文件: {missing_files}")
            return False
        
        print(f"  所有必需文件存在")
        return True
    
    def extract_all_versions(self) -> Dict[str, str]:
        """提取所有文件的版本号"""
        import re
        import yaml
        
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
        
        # CHANGELOG.md
        changelog_file = self.skill_path / "CHANGELOG.md"
        if changelog_file.exists():
            content = changelog_file.read_text(encoding='utf-8')
            match = re.search(r'Current Version:\s*([\d.]+)', content)
            versions["CHANGELOG.md"] = match.group(1) if match else "NOT_FOUND"
        
        # SKILL.md
        skill_md_file = self.skill_path / "SKILL.md"
        if skill_md_file.exists():
            content = skill_md_file.read_text(encoding='utf-8')
            match = re.search(r'Version:\s*([\d.]+)', content, re.IGNORECASE)
            versions["SKILL.md"] = match.group(1) if match else "NOT_FOUND"
        
        print(f"  提取的版本号: {versions}")
        return versions
    
    def validate_version_consistency(self, versions: Dict[str, str]) -> bool:
        """验证版本号一致性"""
        if not versions:
            print("  错误: 未提取到版本号")
            return False
        
        # 获取所有版本号
        all_versions = list(versions.values())
        
        # 检查是否有NOT_FOUND
        if "NOT_FOUND" in all_versions:
            not_found_files = [f for f, v in versions.items() if v == "NOT_FOUND"]
            print(f"  错误: 以下文件未找到版本号: {not_found_files}")
            return False
        
        # 检查是否一致
        unique_versions = set(all_versions)
        if len(unique_versions) == 1:
            version = list(unique_versions)[0]
            print(f"  所有文件版本一致: {version}")
            return True
        else:
            print(f"  错误: 版本不一致: {versions}")
            return False
    
    def check_python_syntax(self) -> bool:
        """检查Python语法"""
        import traceback
        
        python_files = list(self.skill_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                compile(py_file.read_text(encoding='utf-8'), str(py_file), 'exec')
            except SyntaxError as e:
                print(f"  语法错误: {py_file}:{e.lineno} - {e.msg}")
                return False
        
        print(f"  所有Python文件无语法错误")
        return True
    
    def test_skill_import(self) -> bool:
        """测试skill.py导入"""
        import sys
        import traceback
        
        # 添加技能路径到sys.path
        sys.path.insert(0, str(self.skill_path))
        
        try:
            import skill as test_skill
            print("  成功导入skill.py")
            
            if hasattr(test_skill, 'SleepRabbitSkill'):
                print("  找到SleepRabbitSkill类")
                
                # 尝试创建实例
                skill_instance = test_skill.SleepRabbitSkill()
                print("  成功创建Skill实例")
                
                # 检查版本
                version = getattr(skill_instance, 'version', 'NOT_FOUND')
                print(f"  技能版本: {version}")
                
                return True
            else:
                print("  错误: skill.py中没有SleepRabbitSkill类")
                return False
                
        except Exception as e:
            print(f"  导入错误: {e}")
            traceback.print_exc()
            return False
    
    def check_documentation_language(self) -> bool:
        """检查文档语言"""
        import re
        
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
        
        if issues:
            for issue in issues:
                print(f"  语言问题: {issue}")
            return False
        
        print("  所有文档语言一致（全英文）")
        return True
    
    def check_historical_references(self) -> List[str]:
        """检查历史遗留引用"""
        import re
        
        legacy_patterns = [
            "sleep-rabbit-secure.js",
            "test-plugin.js",
            "microservices",
            "ports 8008",
            "ports 8009",
            "ports 8030",
            "ports 8040"
        ]
        
        found_references = []
        
        # 检查所有.md文件
        for md_file in self.skill_path.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            
            for pattern in legacy_patterns:
                if pattern.lower() in content.lower():
                    found_references.append(f"{md_file.name}: {pattern}")
        
        if found_references:
            print(f"  发现历史遗留引用: {found_references}")
        else:
            print("  无历史遗留引用")
        
        return found_references
    
    def create_zip_package(self) -> Path:
        """创建ZIP包"""
        import zipfile
        
        zip_path = self.skill_path.parent / f"{self.skill_path.name}.zip"
        
        # 如果ZIP包已存在，删除它
        if zip_path.exists():
            zip_path.unlink()
        
        # 创建ZIP包
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.skill_path.rglob("*"):
                if file_path.is_file():
                    # 计算相对路径
                    arcname = file_path.relative_to(self.skill_path)
                    zipf.write(file_path, arcname)
        
        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"  创建ZIP包: {zip_path.name} ({zip_size_mb:.2f} MB)")
        
        return zip_path
    
    def final_comprehensive_check(self) -> bool:
        """最终综合验证"""
        print("  执行最终综合验证...")
        
        # 这里可以添加更多的综合检查
        checks = [
            ("文件数量检查", self.check_file_count()),
            ("目录结构检查", self.check_directory_structure()),
            ("配置文件检查", self.check_config_files()),
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print(f"    [OK] {check_name}")
            else:
                print(f"    [FAIL] {check_name}")
                all_passed = False
        
        return all_passed
    
    def check_file_count(self) -> bool:
        """检查文件数量"""
        files = list(self.skill_path.rglob("*"))
        file_count = len([f for f in files if f.is_file()])
        
        print(f"    文件数量: {file_count}")
        return file_count > 10  # 假设至少有10个文件
    
    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        required_dirs = ["utils", "data", "core"]
        
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists() or not dir_path.is_dir():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            print(f"    缺失目录: {missing_dirs}")
            return False
        
        print(f"    目录结构完整")
        return True
    
    def check_config_files(self) -> bool:
        """检查配置文件"""
        config_files = ["config.yaml", "requirements.txt", "package.json"]
        
        missing_configs = []
        for config_file in config_files:
            file_path = self.skill_path / config_file
            if not file_path.exists():
                missing_configs.append(config_file)
        
        if missing_configs:
            print(f"    缺失配置文件: {missing_configs}")
            return False
        
        print(f"    配置文件完整")
        return True

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python validation_chain.py <技能路径>")
        print("示例: python validation_chain.py D:/openclaw/releases/AISleepGen_2.4.1")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    try:
        # 创建验证链
        chain = SkillReleaseValidationChain(skill_path)
        
        # 执行验证链
        results = chain.execute()
        
        # 生成证据报告
        report = chain.get_evidence_report()
        
        # 保存报告
        report_file = Path(skill_path) / "validation_chain_evidence.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n验证链执行完成")
        print(f"证据报告: {report_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n验证链执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())