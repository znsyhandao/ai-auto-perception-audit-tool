#!/usr/bin/env python3
"""
安全模式检测器 - 短期目标实现
检测SQL注入、硬编码密钥等安全漏洞
"""

import re
import ast
import json
from pathlib import Path
from typing import List, Dict, Any

class SecurityPatternDetector:
    """安全模式检测器"""
    
    def __init__(self):
        # SQL注入模式
        self.sql_patterns = [
            r"SELECT.*FROM.*WHERE.*%s",  # 字符串拼接
            r"INSERT.*VALUES.*\+",       # 字符串连接
            r"UPDATE.*SET.*=.*\+",       # 更新语句拼接
            r"DELETE.*FROM.*WHERE.*\+",  # 删除语句拼接
            r"exec.*\(.*\+.*\)",         # 执行拼接SQL
            r"execute.*\(.*\+.*\)",      # 执行拼接SQL
        ]
        
        # 硬编码密钥模式
        self.hardcoded_patterns = [
            r"password\s*=\s*['\"].+?['\"]",      # 密码
            r"api_key\s*=\s*['\"].+?['\"]",       # API密钥
            r"secret\s*=\s*['\"].+?['\"]",        # 密钥
            r"token\s*=\s*['\"].+?['\"]",         # 令牌
            r"aws_access_key\s*=\s*['\"].+?['\"]", # AWS密钥
            r"aws_secret_key\s*=\s*['\"].+?['\"]", # AWS密钥
            r"database_password\s*=\s*['\"].+?['\"]", # 数据库密码
        ]
        
        # XSS漏洞模式
        self.xss_patterns = [
            r"response\.write\(.*\+.*\)",         # 直接输出
            r"document\.write\(.*\+.*\)",         # JS直接输出
            r"innerHTML\s*=\s*.+?\+",             # 设置innerHTML
            r"outerHTML\s*=\s*.+?\+",             # 设置outerHTML
            r"eval\(.*\+.*\)",                    # eval拼接
        ]
        
        # 命令注入模式
        self.command_injection_patterns = [
            r"os\.system\(.*\+.*\)",              # os.system拼接
            r"subprocess\.call\(.*\+.*\)",        # subprocess拼接
            r"subprocess\.Popen\(.*\+.*\)",       # subprocess拼接
            r"exec\(.*\+.*\)",                    # exec拼接
            r"eval\(.*\+.*\)",                    # eval拼接
        ]
        
    def detect_sql_injection(self, content: str) -> List[Dict[str, Any]]:
        """检测SQL注入漏洞"""
        issues = []
        
        for i, pattern in enumerate(self.sql_patterns):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                issues.append({
                    "type": "SQL注入",
                    "pattern": pattern,
                    "line": self._get_line_number(content, match.start()),
                    "code": match.group(),
                    "severity": "高危",
                    "recommendation": "使用参数化查询或ORM框架"
                })
        
        return issues
    
    def detect_hardcoded_secrets(self, content: str) -> List[Dict[str, Any]]:
        """检测硬编码密钥"""
        issues = []
        
        for i, pattern in enumerate(self.hardcoded_patterns):
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # 检查是否是测试密钥或示例
                value = match.group()
                if any(test_key in value.lower() for test_key in ["test", "example", "demo", "placeholder"]):
                    severity = "低危"
                    recommendation = "测试环境密钥，生产环境需替换"
                else:
                    severity = "高危"
                    recommendation = "使用环境变量或密钥管理服务"
                
                issues.append({
                    "type": "硬编码密钥",
                    "pattern": pattern,
                    "line": self._get_line_number(content, match.start()),
                    "code": match.group(),
                    "severity": severity,
                    "recommendation": recommendation
                })
        
        return issues
    
    def detect_xss_vulnerabilities(self, content: str) -> List[Dict[str, Any]]:
        """检测XSS漏洞"""
        issues = []
        
        for i, pattern in enumerate(self.xss_patterns):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                issues.append({
                    "type": "XSS漏洞",
                    "pattern": pattern,
                    "line": self._get_line_number(content, match.start()),
                    "code": match.group(),
                    "severity": "中危",
                    "recommendation": "对用户输入进行HTML编码和验证"
                })
        
        return issues
    
    def detect_command_injection(self, content: str) -> List[Dict[str, Any]]:
        """检测命令注入漏洞"""
        issues = []
        
        for i, pattern in enumerate(self.command_injection_patterns):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                issues.append({
                    "type": "命令注入",
                    "pattern": pattern,
                    "line": self._get_line_number(content, match.start()),
                    "code": match.group(),
                    "severity": "高危",
                    "recommendation": "使用参数化命令或白名单验证"
                })
        
        return issues
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""
        if not file_path.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                return {"error": f"无法读取文件: {file_path}"}
        
        issues = []
        
        # 检测各种安全问题
        issues.extend(self.detect_sql_injection(content))
        issues.extend(self.detect_hardcoded_secrets(content))
        issues.extend(self.detect_xss_vulnerabilities(content))
        issues.extend(self.detect_command_injection(content))
        
        return {
            "file": str(file_path),
            "total_issues": len(issues),
            "issues": issues,
            "summary": self._generate_summary(issues)
        }
    
    def analyze_directory(self, dir_path: Path, extensions=None) -> Dict[str, Any]:
        """分析整个目录"""
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.php', '.cs', '.go', '.rb']
        
        if not dir_path.exists():
            return {"error": f"目录不存在: {dir_path}"}
        
        all_issues = []
        analyzed_files = []
        
        for ext in extensions:
            for file_path in dir_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    result = self.analyze_file(file_path)
                    if "issues" in result and result["issues"]:
                        all_issues.extend(result["issues"])
                        analyzed_files.append(str(file_path))
        
        return {
            "directory": str(dir_path),
            "analyzed_files": len(analyzed_files),
            "total_issues": len(all_issues),
            "issues": all_issues,
            "summary": self._generate_summary(all_issues),
            "severity_breakdown": self._get_severity_breakdown(all_issues)
        }
    
    def _get_line_number(self, content: str, position: int) -> int:
        """获取指定位置的行号"""
        return content[:position].count('\n') + 1
    
    def _generate_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成问题摘要"""
        if not issues:
            return {"message": "未发现安全问题"}
        
        summary = {
            "高危": len([i for i in issues if i["severity"] == "高危"]),
            "中危": len([i for i in issues if i["severity"] == "中危"]),
            "低危": len([i for i in issues if i["severity"] == "低危"]),
            "问题类型": {}
        }
        
        # 统计问题类型
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in summary["问题类型"]:
                summary["问题类型"][issue_type] = 0
            summary["问题类型"][issue_type] += 1
        
        return summary
    
    def _get_severity_breakdown(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取严重性分布"""
        breakdown = {"高危": 0, "中危": 0, "低危": 0}
        for issue in issues:
            breakdown[issue["severity"]] += 1
        return breakdown

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python security_pattern_detector.py <文件或目录路径>")
        print("示例: python security_pattern_detector.py ./skill")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    detector = SecurityPatternDetector()
    
    if path.is_file():
        result = detector.analyze_file(path)
    else:
        result = detector.analyze_directory(path)
    
    # 输出结果
    print("=" * 80)
    print("安全模式检测报告")
    print("=" * 80)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        sys.exit(1)
    
    if path.is_file():
        print(f"文件: {result['file']}")
    else:
        print(f"目录: {result['directory']}")
        print(f"分析文件数: {result['analyzed_files']}")
    
    print(f"发现问题数: {result['total_issues']}")
    print()
    
    # 显示摘要
    summary = result['summary']
    if isinstance(summary, dict) and "message" in summary:
        print(summary['message'])
    else:
        print("问题摘要:")
        print(f"  高危: {summary.get('高危', 0)}")
        print(f"  中危: {summary.get('中危', 0)}")
        print(f"  低危: {summary.get('低危', 0)}")
        
        if "问题类型" in summary:
            print("\n问题类型分布:")
            for issue_type, count in summary["问题类型"].items():
                print(f"  {issue_type}: {count}")
    
    print()
    
    # 显示详细问题（最多显示10个）
    if result['issues']:
        print("详细问题（前10个）:")
        for i, issue in enumerate(result['issues'][:10]):
            print(f"{i+1}. [{issue['severity']}] {issue['type']}")
            print(f"   行号: {issue['line']}")
            print(f"   代码: {issue['code'][:100]}...")
            print(f"   建议: {issue['recommendation']}")
            print()
        
        if len(result['issues']) > 10:
            print(f"... 还有 {len(result['issues']) - 10} 个问题未显示")
    
    print("=" * 80)
    
    # 保存报告到文件
    report_file = "security_audit_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"详细报告已保存到: {report_file}")

if __name__ == "__main__":
    main()