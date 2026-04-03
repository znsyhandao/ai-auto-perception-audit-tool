#!/usr/bin/env python3
"""
安全声明验证检查器（精简版）
验证文档中的安全声明是否在代码中实际实施
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class SecurityClaimChecker:
    """验证安全声明是否实施"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
    
    def run_checks(self) -> Dict[str, any]:
        """运行所有检查"""
        print("=" * 80)
        print("安全声明验证检查 (ClawHub合规)")
        print("=" * 80)
        
        results = {}
        
        # 1. 路径限制声明验证
        print("\n[1] 路径限制声明验证")
        path_result = self.check_path_restriction_claims()
        results["path_restriction"] = path_result
        print(f"  结果: {'通过' if path_result['passed'] else '失败'}")
        if not path_result["passed"]:
            print(f"  问题: {path_result.get('issue', '未知')}")
        
        # 2. 网络访问声明验证
        print("\n[2] 网络访问声明验证")
        network_result = self.check_network_access_claims()
        results["network_access"] = network_result
        print(f"  结果: {'通过' if network_result['passed'] else '失败'}")
        
        # 3. Shell命令声明验证
        print("\n[3] Shell命令声明验证")
        shell_result = self.check_shell_command_claims()
        results["shell_commands"] = shell_result
        print(f"  结果: {'通过' if shell_result['passed'] else '失败'}")
        
        # 4. 资源限制声明验证
        print("\n[4] 资源限制声明验证")
        resource_result = self.check_resource_limit_claims()
        results["resource_limits"] = resource_result
        print(f"  结果: {'通过' if resource_result['passed'] else '失败'}")
        if not resource_result["passed"]:
            print(f"  问题: {resource_result.get('issue', '未知')}")
        
        # 5. 自动验证声明验证
        print("\n[5] 自动验证声明验证")
        auto_result = self.check_auto_validation_claims()
        results["auto_validation"] = auto_result
        print(f"  结果: {'通过' if auto_result['passed'] else '失败'}")
        
        # 总结
        all_passed = all(r["passed"] for r in results.values())
        
        print("\n" + "=" * 80)
        if all_passed:
            print("[SUCCESS] 所有安全声明验证通过")
        else:
            print("[FAILURE] 有安全声明验证失败")
            print("\n根本问题: 文档声称的安全功能在代码中未实施")
            print("修复建议:")
            for check_name, result in results.items():
                if not result["passed"]:
                    print(f"  - {check_name}: {result.get('recommendation', '请修复')}")
        print("=" * 80)
        
        return {
            "all_passed": all_passed,
            "results": results,
            "skill_path": str(self.skill_path)
        }
    
    def check_path_restriction_claims(self) -> Dict[str, any]:
        """检查路径限制声明"""
        # 检查文档中的路径限制声明
        doc_claims = self._scan_docs_for_path_restriction_claims()
        
        # 检查代码中的路径限制实施
        code_impl = self._check_code_for_path_restriction_implementation()
        
        # 验证一致性
        if doc_claims and not code_impl["implemented"]:
            return {
                "passed": False,
                "doc_claims": doc_claims,
                "code_implementation": code_impl,
                "issue": "文档声称路径限制，但代码未实施",
                "recommendation": "实施PathValidator或从文档中移除虚假声明"
            }
        
        return {
            "passed": True,
            "doc_claims": doc_claims,
            "code_implementation": code_impl,
            "consistent": True
        }
    
    def check_network_access_claims(self) -> Dict[str, any]:
        """检查网络访问声明"""
        # 检查文档声明
        doc_claims = self._scan_docs_for_network_claims()
        
        # 检查代码实现
        network_imports = self._scan_code_for_network_imports()
        
        # 如果声明无网络访问，但代码有网络导入，失败
        if doc_claims.get("no_network") and network_imports:
            return {
                "passed": False,
                "doc_claims": doc_claims,
                "network_imports": network_imports,
                "issue": "文档声明无网络访问，但代码有网络导入",
                "recommendation": "移除网络导入或更新文档声明"
            }
        
        return {
            "passed": True,
            "doc_claims": doc_claims,
            "network_imports": network_imports,
            "consistent": True
        }
    
    def check_shell_command_claims(self) -> Dict[str, any]:
        """检查Shell命令声明"""
        # 检查文档声明
        doc_claims = self._scan_docs_for_shell_claims()
        
        # 检查代码实现
        shell_commands = self._scan_code_for_shell_commands()
        
        # 如果声明无Shell命令，但代码有Shell命令，失败
        if doc_claims.get("no_shell") and shell_commands:
            return {
                "passed": False,
                "doc_claims": doc_claims,
                "shell_commands": shell_commands,
                "issue": "文档声明无Shell命令，但代码有Shell命令",
                "recommendation": "移除Shell命令或更新文档声明"
            }
        
        return {
            "passed": True,
            "doc_claims": doc_claims,
            "shell_commands": shell_commands,
            "consistent": True
        }
    
    def check_resource_limit_claims(self) -> Dict[str, any]:
        """检查资源限制声明"""
        # 检查文档声明
        doc_claims = self._scan_docs_for_resource_claims()
        
        # 检查代码实现
        code_impl = self._check_code_for_resource_implementation()
        
        # 验证每个声明
        issues = []
        for claim, claimed in doc_claims.items():
            if claimed and not code_impl.get(claim, False):
                issues.append(f"文档声称{claim}，但代码未实施")
        
        if issues:
            return {
                "passed": False,
                "doc_claims": doc_claims,
                "code_implementation": code_impl,
                "issues": issues,
                "recommendation": "实施资源限制或从文档中移除虚假声明"
            }
        
        return {
            "passed": True,
            "doc_claims": doc_claims,
            "code_implementation": code_impl,
            "consistent": True
        }
    
    def check_auto_validation_claims(self) -> Dict[str, any]:
        """检查自动验证声明"""
        # 检查文档声明
        doc_claims = self._scan_docs_for_auto_validation_claims()
        
        # 检查代码实现
        code_impl = self._check_code_for_auto_validation_implementation()
        
        # 验证每个声明
        issues = []
        for claim, claimed in doc_claims.items():
            if claimed and not code_impl.get(claim, False):
                issues.append(f"文档声称{claim}，但代码未实施")
        
        if issues:
            return {
                "passed": False,
                "doc_claims": doc_claims,
                "code_implementation": code_impl,
                "issues": issues,
                "recommendation": "实施自动验证或从文档中移除虚假声明"
            }
        
        return {
            "passed": True,
            "doc_claims": doc_claims,
            "code_implementation": code_impl,
            "consistent": True
        }
    
    # ========== 辅助方法 ==========
    
    def _scan_docs_for_path_restriction_claims(self) -> Dict[str, bool]:
        """扫描文档中的路径限制声明"""
        claims = {
            "path_restriction": False,
            "directory_restriction": False,
            "file_access_restricted": False,
        }
        
        patterns = [
            r'restricted to (?:skill|plugin) directory',
            r'limited to (?:allowed|specified) (?:directories|paths)',
            r'file access (?:restricted|limited)',
            r'path (?:validation|verification)',
        ]
        
        for file_path in self.skill_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                for pattern in patterns:
                    if re.search(pattern, content):
                        if "path" in pattern:
                            claims["path_restriction"] = True
                        elif "directory" in pattern or "file access" in pattern:
                            claims["directory_restriction"] = True
                        claims["file_access_restricted"] = True
            except:
                continue
        
        return claims
    
    def _check_code_for_path_restriction_implementation(self) -> Dict[str, any]:
        """检查代码中的路径限制实施"""
        implementation = {
            "implemented": False,
            "path_validator_found": False,
            "file_operations_restricted": False,
        }
        
        # 查找PathValidator
        for file_path in self.skill_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "PathValidator" in content or "path_validator" in content.lower():
                    implementation["path_validator_found"] = True
                    
                    if "is_path_allowed" in content or "validate_path" in content:
                        implementation["implemented"] = True
                
                # 检查文件操作是否使用路径验证
                if "file_check" in content or "check_file_exists" in content:
                    if "is_path_allowed" in content or "validate_path" in content:
                        implementation["file_operations_restricted"] = True
                        
            except:
                continue
        
        return implementation
    
    def _scan_docs_for_network_claims(self) -> Dict[str, bool]:
        """扫描文档中的网络访问声明"""
        claims = {"no_network": False}
        
        for file_path in self.skill_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                if "no network" in content or "network access: false" in content:
                    claims["no_network"] = True
            except:
                continue
        
        return claims
    
    def _scan_code_for_network_imports(self) -> List[str]:
        """扫描代码中的网络导入"""
        network_modules = [
            'socket', 'requests', 'urllib', 'http', 'ftplib', 'smtplib',
            'poplib', 'imaplib', 'telnetlib', 'asyncio', 'aiohttp',
            'websocket', 'subprocess'
        ]
        
        found = []
        
        for file_path in self.skill_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for module in network_modules:
                    if f"import {module}" in content or f"from {module}" in content:
                        found.append(f"{file_path.name}: {module}")
            except:
                continue
        
        return found
    
    def _scan_docs_for_shell_claims(self) -> Dict[str, bool]:
        """扫描文档中的Shell命令声明"""
        claims = {"no_shell": False}
        
        for file_path in self.skill_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                if "no shell" in content or "shell commands: false" in content:
                    claims["no_shell"] = True
            except:
                continue
        
        return claims
    
    def _scan_code_for_shell_commands(self) -> List[str]:
        """扫描代码中的Shell命令"""
        shell_patterns = [
            r'os\.system\(',
            r'os\.popen\(',
            r'subprocess\.',
            r'Popen\(',
        ]
        
        found = []
        
        for file_path in self.skill_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in shell_patterns:
                    if re.search(pattern, content):
                        found.append(f"{file_path.name}: {pattern}")
            except:
                continue
        
        return found
    
    def _scan_docs_for_resource_claims(self) -> Dict[str, bool]:
        """扫描文档中的资源限制声明"""
        claims = {
            "memory_limit": False,
            "time_limit": False,
        }
        
        for file_path in self.skill_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                if "memory limit" in content or "memory usage: limited" in content:
                    claims["memory_limit"] = True
                
                if "time limit" in content or "execution time: limited" in content:
                    claims["time_limit"] = True
            except:
                continue
        
        return claims
    
    def _check_code_for_resource_implementation(self) -> Dict[str, bool]:
        """检查代码中的资源限制实施"""
        implementation = {
            "memory_limit": False,
            "time_limit": False,
        }
        
        for file_path in self.skill_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                if "memory" in content and ("limit" in content or "constraint" in content):
                    implementation["memory_limit"] = True
                
                if "time" in content and ("limit" in content or "timeout" in content):
                    implementation["time_limit"] = True
            except:
                continue
        
        return implementation
    
    def _scan_docs_for_auto_validation_claims(self) -> Dict[str, bool]:
        """扫描文档中的自动验证声明"""
        claims = {
            "auto_validation": False,
            "syntax_validation": False,
        }
        
        for file_path in self.skill_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                if "automated validation" in content or "automatic validation" in content:
                    claims["auto_validation"] = True
                
                if "syntax validation" in content:
                    claims["syntax_validation"] = True
            except:
                continue
        
        return claims
    
    def _check_code_for_auto_validation_implementation(self) -> Dict[str, bool]:
        """检查代码中的自动验证实施"""
        implementation = {
            "auto_validation": False,
            "syntax_validation": False,
        }
        
        for file_path in self.skill_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                if "validate" in content and ("auto" in content or "automatic" in content):
                    implementation["auto_validation"] = True
                
                if "syntax" in content and "check" in content:
                    implementation["syntax_validation"] = True
            except:
                continue
        
        return implementation

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python security_claim_verifier_compact.py <技能路径>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    checker = SecurityClaimChecker(skill_path)
    result = checker.run_checks()
    
    # 保存结果
    report_file = Path(skill_path) / ".." / "security_claim_report.json"
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