#!/usr/bin/env python3
"""
文档-元数据一致性检查（精简版）
解决ClawHub扫描发现的文档矛盾问题
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DocumentMetadataChecker:
    """文档与元数据一致性检查"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
    
    def run_checks(self) -> Dict[str, any]:
        """运行所有检查"""
        print("=" * 80)
        print("文档-元数据一致性检查 (ClawHub合规)")
        print("=" * 80)
        
        results = {}
        
        # 1. 网络声明一致性检查
        print("\n[1] 网络声明一致性检查")
        network_result = self.check_network_consistency()
        results["network_consistency"] = network_result
        print(f"  结果: {'通过' if network_result['passed'] else '失败'}")
        if not network_result["passed"]:
            print(f"  问题: {network_result.get('issue', '未知')}")
        
        # 2. 元数据版本一致性检查
        print("\n[2] 元数据版本一致性检查")
        version_result = self.check_version_consistency()
        results["version_consistency"] = version_result
        print(f"  结果: {'通过' if version_result['passed'] else '失败'}")
        if not version_result["passed"]:
            print(f"  问题: 版本不一致 - {version_result.get('versions', {})}")
        
        # 3. 来源声明校验
        print("\n[3] 来源声明校验")
        source_result = self.check_source_consistency()
        results["source_consistency"] = source_result
        print(f"  结果: {'通过' if source_result['passed'] else '失败'}")
        if not source_result["passed"]:
            print(f"  问题: {source_result.get('issue', '未知')}")
        
        # 4. 作者一致性检查
        print("\n[4] 作者一致性检查")
        author_result = self.check_author_consistency()
        results["author_consistency"] = author_result
        print(f"  结果: {'通过' if author_result['passed'] else '失败'}")
        
        # 总结
        all_passed = all(r["passed"] for r in results.values())
        
        print("\n" + "=" * 80)
        if all_passed:
            print("[SUCCESS] 所有文档-元数据一致性检查通过")
        else:
            print("[FAILURE] 有文档-元数据一致性检查失败")
            print("建议修复:")
            for check_name, result in results.items():
                if not result["passed"]:
                    print(f"  - {check_name}: {result.get('recommendation', '请修复')}")
        print("=" * 80)
        
        return {
            "all_passed": all_passed,
            "results": results,
            "skill_path": str(self.skill_path)
        }
    
    def check_network_consistency(self) -> Dict[str, any]:
        """检查网络声明一致性"""
        # 获取元数据中的网络访问声明
        metadata_network = self._get_metadata_network_declaration()
        
        # 扫描文档中的网络术语
        docs_network_terms = self._scan_docs_for_network_terms()
        
        # 逻辑：如果声明无网络访问，文档中不应有网络术语
        if metadata_network == "false" and docs_network_terms:
            return {
                "passed": False,
                "metadata_network": metadata_network,
                "docs_network_terms": docs_network_terms,
                "issue": "文档描述了网络行为，但元数据声明无网络访问",
                "recommendation": "删除文档中的网络术语或更新元数据声明"
            }
        
        return {
            "passed": True,
            "metadata_network": metadata_network,
            "docs_network_terms": docs_network_terms,
            "consistent": True
        }
    
    def check_version_consistency(self) -> Dict[str, any]:
        """检查元数据版本一致性"""
        versions = {}
        
        # 从各个文件提取版本号
        files_to_check = [
            ("skill_info.json", self._get_json_version),
            ("package.json", self._get_json_version),
            ("config.yaml", self._get_yaml_version),
            ("skill.py", self._get_py_version),
            ("SKILL.md", self._get_md_version),
            ("CHANGELOG.md", self._get_changelog_version)
        ]
        
        for filename, getter in files_to_check:
            filepath = self.skill_path / filename
            if filepath.exists():
                version = getter(filepath)
                if version:
                    versions[filename] = version
        
        # 检查一致性
        unique_versions = set(versions.values())
        
        if len(unique_versions) == 1:
            return {
                "passed": True,
                "versions": versions,
                "consistent_version": list(unique_versions)[0]
            }
        else:
            return {
                "passed": False,
                "versions": versions,
                "unique_versions": list(unique_versions),
                "issue": "多个文件版本号不一致",
                "recommendation": "统一所有文件版本号"
            }
    
    def check_source_consistency(self) -> Dict[str, any]:
        """检查来源声明一致性"""
        # 获取声明的来源
        declared_source = self._get_declared_source()
        
        # 扫描文档中的GitHub引用
        github_refs = self._scan_for_github_references()
        
        # 检查一致性
        if github_refs and (not declared_source or declared_source == "unknown"):
            return {
                "passed": False,
                "declared_source": declared_source,
                "github_references": github_refs,
                "issue": "文档引用GitHub但注册表source为unknown",
                "recommendation": "在metadata中明确source字段"
            }
        
        return {
            "passed": True,
            "declared_source": declared_source,
            "github_references": github_refs,
            "consistent": True
        }
    
    def check_author_consistency(self) -> Dict[str, any]:
        """检查作者一致性"""
        authors = {}
        
        # 从各个文件提取作者
        files_to_check = [
            ("package.json", self._get_json_author),
            ("config.yaml", self._get_yaml_author),
            ("skill_info.json", self._get_json_author),
            ("SKILL.md", self._get_md_author)
        ]
        
        for filename, getter in files_to_check:
            filepath = self.skill_path / filename
            if filepath.exists():
                author = getter(filepath)
                if author:
                    authors[filename] = author
        
        # 检查一致性（允许轻微差异）
        if len(authors) == 0:
            return {
                "passed": True,
                "authors": authors,
                "note": "未找到作者信息"
            }
        
        # 提取主要作者名进行比较
        author_names = []
        for author in authors.values():
            if isinstance(author, dict):
                name = author.get("name", "")
            else:
                # 提取名字部分（去掉邮箱等）
                name = str(author).split("(")[0].split("<")[0].strip()
            if name:
                author_names.append(name.lower())
        
        unique_names = set(author_names)
        
        if len(unique_names) <= 1:
            return {
                "passed": True,
                "authors": authors,
                "consistent": True
            }
        else:
            return {
                "passed": False,
                "authors": authors,
                "unique_names": list(unique_names),
                "issue": "作者信息不一致",
                "recommendation": "统一所有文件的作者信息"
            }
    
    # ========== 辅助方法 ==========
    
    def _get_metadata_network_declaration(self) -> str:
        """获取元数据中的网络访问声明"""
        try:
            # 检查config.yaml
            config_path = self.skill_path / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config and "security" in config:
                        return str(config["security"].get("runtime_network_access", "unknown")).lower()
            
            # 检查package.json
            package_path = self.skill_path / "package.json"
            if package_path.exists():
                with open(package_path, 'r', encoding='utf-8') as f:
                    package = json.load(f)
                    if package and "security" in package:
                        return str(package["security"].get("network_access", "unknown")).lower()
        except:
            pass
        
        return "unknown"
    
    def _scan_docs_for_network_terms(self) -> List[str]:
        """扫描文档中的网络术语"""
        network_patterns = [
            r'port\s+\d+',
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            r'http://', r'https://',
            r'socket', r'server', r'listening on',
            r'audit.*service', r'数学审计', r'端口',
            r'8010', r'8080', r'3000',  # 常见端口
        ]
        
        found_terms = []
        
        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.md', '.txt', '.rst']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                    
                    for pattern in network_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_terms.append(f"{file_path.name}: 匹配到 '{pattern}'")
                except:
                    continue
        
        return found_terms
    
    def _get_json_version(self, filepath: Path) -> Optional[str]:
        """从JSON文件获取版本号"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("version")
        except:
            return None
    
    def _get_yaml_version(self, filepath: Path) -> Optional[str]:
        """从YAML文件获取版本号"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and "skill" in data:
                    return data["skill"].get("version")
        except:
            return None
    
    def _get_py_version(self, filepath: Path) -> Optional[str]:
        """从Python文件获取版本号"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*[\'"]([\d.]+)[\'"]', content)
                return match.group(1) if match else None
        except:
            return None
    
    def _get_md_version(self, filepath: Path) -> Optional[str]:
        """从Markdown文件获取版本号"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'Version\s*[:=]\s*([\d.]+)', content, re.IGNORECASE)
                return match.group(1) if match else None
        except:
            return None
    
    def _get_changelog_version(self, filepath: Path) -> Optional[str]:
        """从CHANGELOG获取最新版本号"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'\[([\d.]+)\]', content)
                return match.group(1) if match else None
        except:
            return None
    
    def _get_declared_source(self) -> Optional[str]:
        """获取声明的来源"""
        try:
            # 检查skill_info.json
            info_path = self.skill_path / "skill_info.json"
            if info_path.exists():
                with open(info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "repository" in data:
                        return data["repository"]
                    elif "source" in data:
                        return data["source"]
            
            # 检查package.json
            package_path = self.skill_path / "package.json"
            if package_path.exists():
                with open(package_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "repository" in data:
                        if isinstance(data["repository"], dict):
                            return data["repository"].get("url")
                        return data["repository"]
        except:
            pass
        
        return "unknown"
    
    def _scan_for_github_references(self) -> List[str]:
        """扫描GitHub引用"""
        github_pattern = r'github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+'
        refs = []
        
        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.md', '.txt', '.yaml', '.yml', '.json']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    matches = re.findall(github_pattern, content, re.IGNORECASE)
                    if matches:
                        refs.append(f"{file_path.name}: {matches[0]}")
                except:
                    continue
        
        return refs
    
    def _get_json_author(self, filepath: Path) -> Optional[str]:
        """从JSON文件获取作者"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("author")
        except:
            return None
    
    def _get_yaml_author(self, filepath: Path) -> Optional[str]:
        """从YAML文件获取作者"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and "skill" in data:
                    return data["skill"].get("author")
        except:
            return None
    
    def _get_md_author(self, filepath: Path) -> Optional[str]:
        """从Markdown文件获取作者"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找作者信息
                patterns = [
                    r'Author\s*[:=]\s*(.+)',
                    r'\*\*Author\*\*.*?[:=]\s*(.+)',
                    r'作者.*?[:=]\s*(.+)'
                ]
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
        except:
            pass
        return None

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python document_metadata_consistency_compact.py <技能路径>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    checker = DocumentMetadataChecker(skill_path)
    result = checker.run_checks()
    
    # 保存结果
    report_file = Path(skill_path) / ".." / "document_metadata_report.json"
    try:
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n报告已保存: {report_file}")
    except:
        pass
    
    sys.exit(0 if result["all_passed"] else 1)

if __name__ == "__main__":
    main()