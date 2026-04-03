#!/usr/bin/env python3
"""
防错版本更新工作流程 - 要么全部成功，要么全部失败
"""

import sys
import json
import yaml
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class AtomicOperationError(Exception):
    """原子操作错误"""
    pass

class ValidationError(Exception):
    """验证错误"""
    pass

class ErrorProofVersionUpdate:
    """防错版本更新工作流程"""
    
    def __init__(self, skill_path: str, new_version: str):
        self.skill_path = Path(skill_path)
        self.new_version = new_version
        self.backups = {}
        self.evidence = []
        
        # 验证输入
        self.validate_inputs()
    
    def validate_inputs(self):
        """验证输入"""
        if not self.skill_path.exists():
            raise AtomicOperationError(f"技能路径不存在: {self.skill_path}")
        
        if not re.match(r'^\d+\.\d+\.\d+$', self.new_version):
            raise AtomicOperationError(f"无效的版本号格式: {self.new_version}")
    
    def execute_atomic(self) -> Dict:
        """原子性执行：要么全部成功，要么全部失败"""
        print("=" * 80)
        print("防错版本更新工作流程")
        print("=" * 80)
        print(f"技能路径: {self.skill_path}")
        print(f"新版本号: {self.new_version}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # 阶段1: 备份所有文件
            self.backup_all_files()
            
            # 阶段2: 执行防错更新链
            update_results = self.execute_update_chain()
            
            # 阶段3: 验证所有更新
            self.validate_all_updates()
            
            # 阶段4: 生成防错证据
            report = self.generate_error_proof_report(update_results)
            
            print("\n" + "=" * 80)
            print("✅ 防错版本更新全部成功")
            print("=" * 80)
            
            return report
            
        except Exception as e:
            print(f"\n" + "=" * 80)
            print(f"❌ 防错版本更新失败: {e}")
            print("=" * 80)
            
            # 自动回滚
            self.rollback_changes()
            
            raise AtomicOperationError(f"防错版本更新失败: {e}") from e
    
    def backup_all_files(self):
        """备份所有文件"""
        print("\n[阶段1] 备份所有文件")
        
        files_to_backup = [
            self.skill_path / "skill.py",
            self.skill_path / "config.yaml",
            self.skill_path / "SKILL.md",
            self.skill_path / "README.md",
            self.skill_path / "CHANGELOG.md",
            self.skill_path / "package.json",
            self.skill_path / "skill_info.json"
        ]
        
        for file_path in files_to_backup:
            if file_path.exists():
                backup_path = self.create_backup(file_path)
                self.backups[str(file_path)] = backup_path
                print(f"  备份: {file_path.name}")
    
    def create_backup(self, file_path: Path) -> Path:
        """创建备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}.atomic_backup_{timestamp}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def execute_update_chain(self) -> List[Dict]:
        """执行更新链"""
        print("\n[阶段2] 执行防错更新链")
        
        update_chain = [
            ("验证版本号格式", self.validate_version_format),
            ("更新skill.py", self.update_skill_py),
            ("更新config.yaml", self.update_config_yaml),
            ("更新SKILL.md", self.update_skill_md),
            ("更新package.json", self.update_package_json),
            ("更新skill_info.json", self.update_skill_info_json),
            ("更新CHANGELOG.md", self.update_changelog),
            ("验证所有更新", self.verify_all_updates),
        ]
        
        results = []
        
        for i, (step_name, step_func) in enumerate(update_chain, 1):
            print(f"\n[步骤 {i}/{len(update_chain)}] {step_name}")
            
            try:
                # 执行步骤
                success, evidence = step_func()
                
                # 立即验证
                if not success:
                    raise ValidationError(f"步骤失败: {step_name}")
                
                # 记录结果
                results.append({
                    "step": step_name,
                    "status": "success",
                    "evidence": evidence,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"  ✅ 成功")
                
                # 记录证据
                self.evidence.append({
                    "step": i,
                    "name": step_name,
                    "result": "success",
                    "evidence": str(evidence)[:100]
                })
                
            except Exception as e:
                print(f"  ❌ 失败: {e}")
                
                results.append({
                    "step": step_name,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                raise ValidationError(f"更新链在第{i}步失败: {step_name}") from e
        
        return results
    
    def validate_version_format(self) -> Tuple[bool, Dict]:
        """验证版本号格式"""
        if re.match(r'^\d+\.\d+\.\d+$', self.new_version):
            return True, {"version": self.new_version, "format": "valid"}
        else:
            return False, {"version": self.new_version, "format": "invalid"}
    
    def update_skill_py(self) -> Tuple[bool, Dict]:
        """更新skill.py"""
        file_path = self.skill_path / "skill.py"
        
        if not file_path.exists():
            return False, {"error": "文件不存在"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换版本号
        old_content = content
        content = re.sub(r'version\s*=\s*["\']([^"\']+)["\']', f'version = "{self.new_version}"', content)
        
        if content == old_content:
            return False, {"error": "未找到版本号"}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, {"file": "skill.py", "updated": True}
    
    def update_config_yaml(self) -> Tuple[bool, Dict]:
        """更新config.yaml"""
        file_path = self.skill_path / "config.yaml"
        
        if not file_path.exists():
            return False, {"error": "文件不存在"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        old_version = data.get('skill', {}).get('version', 'NOT_FOUND')
        data['skill']['version'] = self.new_version
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        return True, {
            "file": "config.yaml",
            "old_version": old_version,
            "new_version": self.new_version
        }
    
    def update_skill_md(self) -> Tuple[bool, Dict]:
        """更新SKILL.md"""
        file_path = self.skill_path / "SKILL.md"
        
        if not file_path.exists():
            return False, {"error": "文件不存在"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        old_content = content
        
        # 替换所有版本号引用
        content = re.sub(r'Version:\s*[\d.]+', f'Version: {self.new_version}', content)
        content = re.sub(r'v[\d.]+', f'v{self.new_version}', content)
        content = re.sub(r'[\d.]+ \(', f'{self.new_version} (', content)
        
        if content == old_content:
            return False, {"error": "未找到版本号"}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, {"file": "SKILL.md", "updated": True}
    
    def update_package_json(self) -> Tuple[bool, Dict]:
        """更新package.json"""
        file_path = self.skill_path / "package.json"
        
        if not file_path.exists():
            return False, {"error": "文件不存在"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        old_version = data.get('version', 'NOT_FOUND')
        data['version'] = self.new_version
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, {
            "file": "package.json",
            "old_version": old_version,
            "new_version": self.new_version
        }
    
    def update_skill_info_json(self) -> Tuple[bool, Dict]:
        """更新skill_info.json"""
        file_path = self.skill_path / "skill_info.json"
        
        if not file_path.exists():
            return False, {"error": "文件不存在"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        old_version = data.get('version', 'NOT_FOUND')
        data['version'] = self.new_version
        data['skill_id'] = f'aisleepgen_v{self.new_version.replace(".", "_")}'
        data['release_date'] = datetime.now().isoformat()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, {
            "file": "skill_info.json",
            "old_version": old_version,
            "new_version": self.new_version
        }
    
    def update_changelog(self) -> Tuple[bool, Dict]:
        """更新CHANGELOG.md"""
        file_path = self.skill_path / "CHANGELOG.md"
        
        if not file_path.exists():
            return False, {"error": "文件不存在"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保当前版本号正确
        old_content = content
        content = re.sub(r'Current Version:\s*[\d.]+', f'Current Version: {self.new_version}', content)
        
        if content == old_content:
            return False, {"error": "未找到当前版本号"}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, {"file": "CHANGELOG.md", "updated": True}
    
    def verify_all_updates(self) -> Tuple[bool, Dict]:
        """验证所有更新"""
        print("\n[验证] 检查所有文件版本一致性")
        
        versions = {}
        
        # 检查所有文件的版本号
        files_to_check = [
            ("skill.py", r'version\s*=\s*["\']([^"\']+)["\']'),
            ("config.yaml", self.extract_config_version),
            ("SKILL.md", r'Version:\s*([\d.]+)'),
            ("package.json", self.extract_json_version),
            ("skill_info.json", self.extract_json_version),
            ("CHANGELOG.md", r'Current Version:\s*([\d.]+)'),
        ]
        
        for filename, extractor in files_to_check:
            file_path = self.skill_path / filename
            
            if not file_path.exists():
                versions[filename] = "FILE_NOT_FOUND"
                continue
            
            if callable(extractor):
                version = extractor(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                match = re.search(extractor, content)
                version = match.group(1) if match else "VERSION_NOT_FOUND"
            
            versions[filename] = version
        
        # 检查一致性
        all_versions = list(versions.values())
        valid_versions = [v for v in all_versions if v not in ["FILE_NOT_FOUND", "VERSION_NOT_FOUND"]]
        
        if not valid_versions:
            return False, {"error": "未找到任何版本号", "versions": versions}
        
        unique_versions = set(valid_versions)
        
        if len(unique_versions) == 1 and list(unique_versions)[0] == self.new_version:
            return True, {
                "consistent": True,
                "version": self.new_version,
                "all_files": versions
            }
        else:
            return False, {
                "error": "版本不一致",
                "expected": self.new_version,
                "actual": versions
            }
    
    def extract_config_version(self, file_path: Path) -> str:
        """从config.yaml提取版本号"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data.get('skill', {}).get('version', 'VERSION_NOT_FOUND')
    
    def extract_json_version(self, file_path: Path) -> str:
        """从JSON文件提取版本号"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('version', 'VERSION_NOT_FOUND')
    
    def validate_all_updates(self):
        """验证所有更新"""
        print("\n[阶段3] 最终验证")
        
        # 再次验证版本一致性
        success, evidence = self.verify_all_updates()
        
        if not success:
            raise ValidationError(f"最终验证失败: {evidence.get('error', '未知错误')}")
        
        print("  ✅ 所有文件版本一致")
    
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
        
        print("  ✅ 所有更改已回滚")
    
    def generate_error_proof_report(self, update_results: List[Dict]) -> Dict:
        """生成防错证据报告"""
        print("\n[阶段4] 生成防错证据报告")
        
        success_steps = sum(1 for r in update_results if r["status"] == "success")
        total_steps = len(update_results)
        
        report = {
            "workflow": "error_proof_version_update",
            "timestamp": datetime.now().isoformat(),
            "skill_path": str(self.skill_path),
            "new_version": self.new_version,
            "results": {
                "total_steps": total_steps,
                "success_steps": success_steps,
                "failed_steps": total_steps - success_steps,
                "success_rate": round(success_steps / total_steps * 100, 2) if total_steps > 0 else 0
            },
            "update_chain": update_results,
            "evidence": self.evidence,
            "backups_created": list(self.backups.keys()),
            "overall_status": "success" if success_steps == total_steps else "failed",
            "error_proof_features": [
                "原子性操作：要么全部成功，要么全部失败",
                "自动备份和回滚",
                "更新链：每个步骤后立即验证",
                "最终验证：确保所有文件版本一致",
                "详细证据记录"
            ]
        }
        
        # 保存报告
        report_file = self.skill_path.parent / f"error_proof_version_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  防错证据报告已保存: {report_file}")
        
        return report

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python error_proof_version_update.py <技能路径> <新版本号>")
        print("示例: python error_proof_version_update.py D:/openclaw/releases/AISleepGen_2.4.1 2.4.2")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    new_version = sys.argv[2]
    
    try:
        # 创建防错版本更新工作流程
        updater = ErrorProofVersionUpdate(skill_path, new_version)
        
        # 执行防错更新
        report = updater.execute_atomic()
        
        # 显示摘要
        print("\n" + "=" * 80)
        print("防错版本更新完成摘要")
        print("=" * 80)
        print(f"总体状态: {report.get('overall_status', 'unknown')}")
        print(f"总步骤数: {report.get('results', {}).get('total_steps', 0)}")
        print(f"成功步骤: {report.get('results', {}).get('success_steps', 0)}")
        print(f"失败步骤: {report.get('results', {}).get('failed_steps', 0)}")
        print(f"成功率: {report.get('results', {}).get('success_rate', 0)}%")
        print("=" * 80)
        
        return 0 if report.get('overall_status') == 'success' else 1
        
    except Exception as e:
        print(f"\n防错版本更新系统错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())