#!/usr/bin/env python3
"""
OpenClaw技能安全检查脚本
发布前必须运行，确保技能安全合规
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

class SecurityScanner:
    """安全检查器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues = []
        self.stats = {
            "files_scanned": 0,
            "issues_found": 0,
            "security_level": "unknown"
        }
        
        # 安全检查模式
        self.check_patterns = {
            "network": [
                (r'import requests', "网络库导入"),
                (r'from requests', "网络库导入"),
                (r'import urllib', "网络库导入"),
                (r'import http\.client', "网络库导入"),
                (r'import socket', "网络库导入"),
                (r'requests\.(get|post|put|delete)', "网络请求"),
                (r'urllib\.request', "网络请求"),
                (r'http\.client\.', "网络请求"),
                (r'socket\.', "网络套接字"),
                (r'webhook', "Webhook功能"),
                (r'api.*call', "API调用"),
                (r'在线验证', "在线验证"),
                (r'license.*validation', "许可证验证")
            ],
            "dangerous": [
                (r'subprocess\.', "子进程执行"),
                (r'os\.system\(', "系统命令执行"),
                (r'eval\(', "eval函数"),
                (r'exec\(', "exec函数"),
                (r'__import__\(', "动态导入"),
                (r'open\(.*[\'"]w[\'"]', "文件写入"),
                (r'shutil\.rmtree', "目录删除"),
                (r'os\.remove', "文件删除"),
                (r'os\.unlink', "文件删除")
            ],
            "path_traversal": [
                (r'\.\./', "路径遍历(/)"),
                (r'\.\.\\', "路径遍历(\\)"),
                (r'上级目录', "上级目录访问"),
                (r'遍历.*目录', "目录遍历"),
                (r'os\.walk\(', "目录遍历函数")
            ],
            "external_deps": [
                (r'import numpy', "外部依赖: numpy"),
                (r'import pandas', "外部依赖: pandas"),
                (r'import tensorflow', "外部依赖: tensorflow"),
                (r'import torch', "外部依赖: torch"),
                (r'import sklearn', "外部依赖: scikit-learn"),
                (r'import cv2', "外部依赖: opencv"),
                (r'import PIL', "外部依赖: pillow"),
                (r'import yaml', "外部依赖: pyyaml"),
                (r'import flask', "外部依赖: flask"),
                (r'import django', "外部依赖: django"),
                (r'import fastapi', "外部依赖: fastapi")
            ],
            "privacy": [
                (r'数据上传', "数据上传"),
                (r'用户数据.*收集', "数据收集"),
                (r'跟踪', "用户跟踪"),
                (r'analytics', "分析跟踪"),
                (r'telemetry', "遥测数据")
            ]
        }
    
    def log(self, message: str, level: str = "info"):
        """日志记录"""
        if self.verbose or level == "error":
            prefix = {
                "info": "ℹ️ ",
                "warning": "[WARN] ",
                "error": "[ERROR] ",
                "success": "[OK] "
            }.get(level, "  ")
            print(f"{prefix} {message}")
    
    def scan_file(self, file_path: str) -> List[Dict]:
        """扫描单个文件"""
        self.stats["files_scanned"] += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                self.log(f"无法读取文件: {file_path}", "error")
                return []
        
        file_issues = []
        
        for category, patterns in self.check_patterns.items():
            for pattern, description in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 获取上下文
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].replace('\n', ' ')
                    
                    issue = {
                        "file": file_path,
                        "category": category,
                        "pattern": pattern,
                        "description": description,
                        "line": self._get_line_number(content, match.start()),
                        "context": context.strip()
                    }
                    
                    file_issues.append(issue)
                    self.stats["issues_found"] += 1
        
        return file_issues
    
    def _get_line_number(self, content: str, position: int) -> int:
        """获取行号"""
        return content[:position].count('\n') + 1
    
    def scan_directory(self, directory: str) -> Dict:
        """扫描目录"""
        self.log(f"开始安全检查: {directory}")
        self.log("=" * 60)
        
        all_issues = []
        
        # 扫描所有Python文件
        for root, dirs, files in os.walk(directory):
            # 跳过一些目录
            if '__pycache__' in root or '.git' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_issues = self.scan_file(file_path)
                    
                    if file_issues:
                        all_issues.extend(file_issues)
                        self.log(f"发现问题: {file_path} ({len(file_issues)}个)", "warning")
        
        # 扫描配置文件
        config_files = ['package.json', 'config.yaml', 'config.yml']
        for config_file in config_files:
            config_path = os.path.join(directory, config_file)
            if os.path.exists(config_path):
                self._check_config_file(config_path, all_issues)
        
        # 扫描文档文件
        doc_files = ['README.md', 'SKILL.md']
        for doc_file in doc_files:
            doc_path = os.path.join(directory, doc_file)
            if os.path.exists(doc_path):
                self._check_documentation(doc_path, all_issues)
        
        return {
            "directory": directory,
            "issues": all_issues,
            "stats": self.stats,
            "summary": self._generate_summary(all_issues)
        }
    
    def _check_config_file(self, config_path: str, all_issues: List):
        """检查配置文件"""
        if config_path.endswith('.json'):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 检查package.json权限
                if 'openclaw' in config and 'permissions' in config['openclaw']:
                    permissions = config['openclaw']['permissions']
                    if 'network' in permissions:
                        all_issues.append({
                            "file": config_path,
                            "category": "permission",
                            "pattern": "network permission",
                            "description": "配置文件请求网络权限",
                            "line": 1,
                            "context": f"permissions: {permissions}"
                        })
                
                # 检查其他配置
                if 'scripts' in config:
                    for script_name, script in config['scripts'].items():
                        if 'install' in script_name.lower() and script:
                            all_issues.append({
                                "file": config_path,
                                "category": "install",
                                "pattern": "install script",
                                "description": "包含安装脚本",
                                "line": 1,
                                "context": f"{script_name}: {script}"
                            })
            
            except json.JSONDecodeError as e:
                self.log(f"JSON解析错误: {config_path} - {e}", "error")
    
    def _check_documentation(self, doc_path: str, all_issues: List):
        """检查文档文件"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查控制字符
            control_chars = re.findall(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', content)
            if control_chars:
                all_issues.append({
                    "file": doc_path,
                    "category": "documentation",
                    "pattern": "control characters",
                    "description": "文档中包含控制字符",
                    "line": 1,
                    "context": f"发现 {len(control_chars)} 个控制字符"
                })
            
            # 检查不一致的安全声明
            security_claims = [
                ("零依赖", "检查外部依赖"),
                ("无网络", "检查网络代码"),
                ("本地处理", "检查外部API"),
                ("隐私安全", "检查数据上传"),
                ("100%本地", "检查网络功能")
            ]
            
            for claim, check in security_claims:
                if claim in content:
                    # 标记需要验证的声明
                    all_issues.append({
                        "file": doc_path,
                        "category": "consistency",
                        "pattern": f"security claim: {claim}",
                        "description": f"安全声明需要验证: {claim}",
                        "line": content.find(claim) + 1,
                        "context": f"声明: {claim} -> 需要验证: {check}"
                    })
        
        except Exception as e:
            self.log(f"文档检查错误: {doc_path} - {e}", "error")
    
    def _generate_summary(self, issues: List[Dict]) -> Dict:
        """生成摘要"""
        by_category = {}
        for issue in issues:
            category = issue["category"]
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1
        
        # 计算安全等级
        critical_issues = len([i for i in issues if i["category"] in ["network", "dangerous"]])
        
        if critical_issues > 0:
            security_level = "critical"
        elif len(issues) > 0:
            security_level = "warning"
        else:
            security_level = "safe"
        
        return {
            "by_category": by_category,
            "security_level": security_level,
            "total_issues": len(issues),
            "critical_issues": critical_issues
        }
    
    def print_report(self, scan_result: Dict):
        """打印报告"""
        issues = scan_result["issues"]
        summary = scan_result["summary"]
        stats = scan_result["stats"]
        
        print("\n" + "=" * 60)
        print("[DASHBOARD] 安全检查报告")
        print("=" * 60)
        
        print(f"\n[FOLDER] 扫描目录: {scan_result['directory']}")
        print(f"[DOC] 扫描文件: {stats['files_scanned']} 个")
        print(f"[DETAILS] 发现问题: {stats['issues_found']} 个")
        print(f"[SHIELD] 安全等级: {summary['security_level'].upper()}")
        
        if summary['by_category']:
            print("\n[LIST] 问题分类:")
            for category, count in summary['by_category'].items():
                print(f"  - {category}: {count} 个")
        
        if issues:
            print("\n[ERROR] 详细问题:")
            
            # 按文件分组
            issues_by_file = {}
            for issue in issues:
                file = issue["file"]
                if file not in issues_by_file:
                    issues_by_file[file] = []
                issues_by_file[file].append(issue)
            
            for file, file_issues in issues_by_file.items():
                print(f"\n[DOC] {file}:")
                for issue in file_issues:
                    print(f"  - 行 {issue['line']}: {issue['description']}")
                    print(f"    模式: {issue['pattern']}")
                    if self.verbose:
                        print(f"    上下文: ...{issue['context']}...")
                    print()
        
        # 建议
        print("\n[IDEA] 建议:")
        if summary['security_level'] == 'critical':
            print("  [ERROR] 发现严重安全问题，禁止发布！")
            print("  [WRENCH] 必须修复所有网络和危险代码问题")
        elif summary['security_level'] == 'warning':
            print("  [WARN]  发现警告问题，建议修复后再发布")
            print("  [DETAILS] 检查路径安全和依赖问题")
        else:
            print("  [OK] 安全检查通过，可以继续发布流程")
        
        print("\n" + "=" * 60)
    
    def save_report(self, scan_result: Dict, output_path: str):
        """保存报告到文件"""
        report = {
            "scan_time": self._get_timestamp(),
            "scan_result": scan_result
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"报告已保存: {output_path}", "success")
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="OpenClaw技能安全检查工具")
    parser.add_argument("directory", help="要扫描的目录路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-o", "--output", help="输出报告文件路径")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在: {args.directory}")
        sys.exit(1)
    
    scanner = SecurityScanner(verbose=args.verbose)
    scan_result = scanner.scan_directory(args.directory)
    
    if args.json:
        print(json.dumps(scan_result, ensure_ascii=False, indent=2))
    else:
        scanner.print_report(scan_result)
    
    if args.output:
        scanner.save_report(scan_result, args.output)
    
    # 返回退出代码
    if scan_result["summary"]["security_level"] == "critical":
        sys.exit(1)
    elif scan_result["summary"]["security_level"] == "warning":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()