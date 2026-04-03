#!/usr/bin/env python3
"""
文档-元数据一致性检查模块
解决ClawHub扫描发现的文档矛盾问题
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.parse

class DocumentMetadataConsistency:
    """文档与元数据一致性检查"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.results = []
        
    def check_all(self) -> Dict[str, any]:
        """运行所有检查"""
        print("=" * 80)
        print("文档-元数据一致性检查")
        print("=" * 80)
        
        checks = [
            ("网络声明一致性检查", self.check_network_declaration_consistency),
            ("元数据版本一致性检查", self.check_metadata_version_consistency),
            ("来源声明校验", self.check_source_declaration),
            ("文档网络术语扫描", self.scan_docs_for_network_terms),
            ("跨文件作者一致性", self.check_author_consistency),
            ("许可证一致性检查", self.check_license_consistency),
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
        
        print("\n" + "=" * 80)
        if all_passed:
            print("[SUCCESS] 所有检查通过")
        else:
            print("[FAILURE] 有检查失败")
        print("=" * 80)
        
        return {
            "all_passed": all_passed,
            "results": self.results,
            "skill_path": str(self.skill_path)
        }
    
    def check_network_declaration_consistency(self) -> Tuple[bool, Dict]:
        """检查网络声明一致性"""
        # 从元数据获取网络访问声明
        metadata_network_access = self._get_metadata_network_access()
        
        # 扫描文档中的网络术语
        docs_network_terms = self._scan_all_docs_for_network_terms()
        
        # 逻辑：如果元数据声明无网络访问，文档中不应有网络术语
        if metadata_network_access == "false" and docs_network_terms:
            return False, {
                "metadata_network_access": metadata_network_access,
                "docs_network_terms_found": docs_network_terms,
                "conflict": "文档描述了网络行为，但元数据声明无网络访问"
            }
        
        return True, {
            "metadata_network_access": metadata_network_access,
            "docs_network_terms_found": docs_network_terms,
            "consistent": True
        }
    
    def check_metadata_version_consistency(self) -> Tuple[bool, Dict]:
        """检查元数据版本一致性"""
        versions = {}
        
        # 从各个文件提取版本号
        versions["skill_info.json"] = self._get_version_from_skill_info()
        versions["package.json"] = self._get_version_from_package_json()
        versions["config.yaml"] = self._get_version_from_config_yaml()
        versions["skill.py"] = self._get_version_from_skill_py()
        versions["SKILL.md"] = self._get_version_from_skill_md()
        versions["CHANGELOG.md"] = self._get_version_from_changelog()
        
        # 检查是否所有版本一致
        unique_versions = set(v for v in versions.values() if v is not None)
        
        if len(unique_versions) == 1:
            return True, {
                "consistent": True,
                "version": list(unique_versions)[0],
                "all_versions": versions
            }
        else:
            return False, {
                "consistent": False,
                "unique_versions": list(unique_versions),
                "all_versions": versions,
                "conflict": "多个文件版本号不一致"
            }
    
    def check_source_declaration(self) -> Tuple[bool, Dict]:
        """检查来源声明"""
        # 获取声明的来源
        declared_source = self._get_declared_source()
        
        # 检查文档中的GitHub引用
        github_refs = self._scan_for_github_references()
        
        evidence = {
            "declared_source": declared_source,
            "github_references": github_refs
        }
        
        # 如果有GitHub引用但来源不明，警告
        if github_refs and (not declared_source or declared_source == "unknown"):
            return False, {
                **evidence,
                "warning": "文档引用GitHub但注册表source为unknown",
                "recommendation": "请在metadata中明确source字段"
            }
        
        # 如果声明了来源，检查格式
        if declared_source and declared_source != "unknown":
            if not self._validate_source_url(declared_source):
                return False, {
                    **evidence,
                    "warning": "来源URL格式无效",
                    "recommendation": "请提供有效的URL"
                }
        
        return True, evidence
    
    def scan_docs_for_network_terms(self) -> Tuple[bool, Dict]:
        """扫描文档中的网络术语"""
        network_terms = self._scan_all_docs_for_network_terms()
        
        if network_terms:
            return False, {
                "network_terms_found": network_terms,
                "warning": "文档中包含网络相关术语",
                "recommendation": "如果技能100%本地运行，请从文档中移除这些术语"
            }
        
        return True, {
            "network_terms_found": [],
            "clean": True
        }
    
    def check_author_consistency(self) -> Tuple[bool, Dict]:
        """检查跨文件作者一致性"""
        authors = {}
        
        authors["package.json"] = self._get_author_from_package_json()
        authors["config.yaml"] = self._get_author_from_config_yaml()
        authors["skill_info.json"] = self._get_author_from_skill_info()
        authors["SKILL.md"] = self._get_author_from_skill_md()
        
        # 清理和标准化作者信息
        cleaned_authors = {}
        for file, author in authors.items():
            if author:
                # 提取作者名（去掉邮箱等）
                if isinstance(author, dict):
                    author_name = author.get("name", "")
                else:
                    author_name = str(author).split("(")[0].split("<")[0].strip()
                cleaned_authors[file] = author_name
        
        # 检查一致性
        unique_authors = set(v for v in cleaned_authors.values() if v)
        
        if len(unique_authors) <= 1:
            return True, {
                "consistent": True,
                "authors": cleaned_authors,
                "primary_author": list(unique_authors)[0] if unique_authors else None
            }
        else:
            return False, {
                "consistent": False,
                "authors": cleaned_authors,
                "unique_authors": list(unique_authors),
                "conflict": "多个文件作者信息不一致"
            }
    
    def check_license_consistency(self) -> Tuple[bool, Dict]:
        """检查许可证一致性"""
        licenses = {}
        
        licenses["package.json"] = self._get_license_from_package_json()
        licenses["config.yaml"] = self._get_license_from_config_yaml()
        licenses["SKILL.md"] = self._get_license_from_skill_md()
        licenses["LICENSE.txt"] = self._get_license_from_license_file()
        
        # 检查一致性
        unique_licenses = set(v for v in licenses.values() if v)
        
        if len(unique_licenses) <= 1:
            return True, {
                "consistent": True,
                "licenses": licenses,
                "license": list(unique_licenses)[0] if unique_licenses else None
            }
        else:
            return False, {
                "consistent": False,
                "licenses": licenses,
                "unique_licenses": list(unique_licenses),
                "conflict": "多个文件许可证信息不一致"
            }
    
    # ========== 辅助方法 ==========
    
    def _get_metadata_network_access(self) -> str:
        """从元数据获取网络访问声明"""
        try:
            # 检查config.yaml
            config_path = self.skill_path / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config and "security" in config:
                        security = config["security"]
                        if "runtime_network_access" in security:
                            return str(security["runtime_network_access"]).lower()
            
            # 检查package.json
            package_path = self.skill_path / "package.json"
            if package_path.exists():
                with open(package_path, 'r', encoding='utf-8') as f:
                    package = json.load(f)
                    if package and "security" in package:
                        security = package["security"]
                        if "network_access" in security:
                            return str(security["network_access"]).lower()
            
            return "unknown"
        except:
            return "unknown"
    
    def _scan_all_docs_for_network_terms(self) -> List[Dict]:
        """扫描所有文档中的网络术语"""
        network_patterns = [
            r'port\s+\d+',  # 端口号
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP地址
            r'http://', r'https://',  # HTTP协议
            r'socket', r'server', r'listening on',  # 服务器术语
            r'audit.*service', r'数学审计', r'端口',  # 审计服务
            r'api\.', r'endpoint', r'webhook',  # API术语
            r'localhost:\d+', r'127\.0\.0\.1:\d+',  # 本地服务
        ]
        
        docs_extensions = ['.md', '.txt', '.rst', '.yaml', '.yml', '.json']
        network_terms = []
        
        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in docs_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern in network_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            network_terms.append({
                                "file": str(file_path.relative_to(self.skill_path)),
                                "term": match.group(),
                                "line": self._get_line_number(content, match.start()),
                                "context": self._get_context(content, match.start())
                            })
                except:
                    continue
        
        return network_terms
    
    def _get_version_from_skill_info(self) -> Optional[str]:
        """从skill_info.json获取版本号"""
        try:
            file_path = self.skill_path / "skill_info.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("version")
        except:
            pass
        return None
    
    def _get_version_from_package_json(self) -> Optional[str]:
        """从package.json获取版本号"""
        try:
            file_path = self.skill_path / "package.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("version")
        except:
            pass
        return None
    
    def _get_version_from_config_yaml(self) -> Optional[str]:
        """从config.yaml获取版本号"""
        try:
            file_path = self.skill_path / "config.yaml"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and "skill" in data:
                        return data["skill"].get("version")
        except:
            pass
        return None
    
    def _get_version_from_skill_py(self) -> Optional[str]:
        """从skill.py获取版本号"""
        try:
            file_path = self.skill_path / "skill.py"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'version\s*=\s*[\'"]([\d.]+)[\'"]', content)
                    if match:
                        return match.group(1)
        except:
            pass
        return None
    
    def _get_version_from_skill_md(self) -> Optional[str]:
        """从SKILL.md获取版本号"""
        try:
            file_path = self.skill_path / "SKILL.md"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找版本号模式
                    patterns = [
                        r'Version\s*[:=]\s*([\d.]+)',
                        r'\*\*Version\*\*.*?([\d.]+)',
                        r'版本.*?([\d.]+)'
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            return match.group(1)
        except:
            pass
        return None
    
    def _get_version_from_changelog(self) -> Optional[str]:
        """从CHANGELOG.md获取最新版本号"""
        try:
            file_path = self.skill_path / "CHANGELOG.md"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找最新的版本号 [x.x.x]
                    match = re.search(r'\[([\d.]+)\]', content)
                    if match:
                        return match.group(1)
        except:
            pass
        return None
    
    def _get_declared_source(self) -> Optional[str]:
        """获取声明的来源"""
        sources = []
        
        # 检查skill_info.json
        try:
            file_path = self.skill_path / "skill_info.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "repository" in data:
                        sources.append(data["repository"])
                    elif "source" in data:
                        sources.append(data["source"])
        except:
            pass
        
        # 检查package.json
        try:
            file_path = self.skill_path / "package.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "repository" in data:
                        if isinstance(data["repository"], dict):
                            sources.append(data["repository"].get("url"))
                        else:
                            sources.append(data["repository"])
                    elif "homepage" in data:
                        sources.append(data["homepage"])
        except:
            pass
        
        # 返回第一个有效的来源
        for source in sources:
            if source and source != "unknown":
                return source
        
        return "unknown" if sources else None
    
    def _scan_for_github_references(self) -> List[Dict]:
        """扫描GitHub引用"""
        github_patterns = [
            r'github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+',
            r'https://github\.com/[^/\s]+/[^/\s]+',
            r'GitHub.*https://[^\s]+',
            r'仓库.*github',
        ]
        
        github_refs = []
        
        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.md', '.txt', '.yaml', '.yml', '.json', '.py']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern in github_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            github_refs.append({
                                "file": str(file_path.relative_to(self.skill_path)),
                                "reference": match.group(),
                                "line": self._get_line_number(content, match.start())
                            })
                except:
                    continue
        
        return github_refs
    
    def _validate_source_url(self, url: str) -> bool:
        """验证来源URL格式"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _get_author_from_package_json(self) -> Optional[str]:
        """从package.json获取作者"""
        try:
            file_path = self.skill_path / "package.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("author")
        except:
            pass
        return None
    
    def _get_author_from_config_yaml(self) -> Optional[str]:
        """从config.yaml获取作者"""
