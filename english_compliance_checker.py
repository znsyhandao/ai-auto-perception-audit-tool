#!/usr/bin/env python3
"""
English Compliance Checker
检查文件是否全英文，防止中文字符问题
"""

import os
import re
import sys
from pathlib import Path

class EnglishComplianceChecker:
    """检查文件是否全英文"""
    
    def __init__(self):
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]')  # 中文字符范围
        self.results = {
            'passed': [],
            'failed': [],
            'total_files': 0,
            'total_chinese_chars': 0
        }
    
    def check_file(self, file_path):
        """检查单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找中文字符
            chinese_matches = list(self.chinese_pattern.finditer(content))
            chinese_count = len(chinese_matches)
            
            if chinese_count > 0:
                # 获取示例行
                lines = content.split('\n')
                examples = []
                for i, line in enumerate(lines, 1):
                    if self.chinese_pattern.search(line):
                        examples.append({
                            'line': i,
                            'content': line.strip()[:100]  # 前100个字符
                        })
                        if len(examples) >= 3:  # 最多3个示例
                            break
                
                self.results['failed'].append({
                    'file': str(file_path),
                    'chinese_count': chinese_count,
                    'examples': examples
                })
                self.results['total_chinese_chars'] += chinese_count
                return False
            else:
                self.results['passed'].append(str(file_path))
                return True
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
    
    def check_directory(self, directory, extensions=None):
        """检查目录中的所有文件"""
        dir_path = Path(directory)
        
        if extensions is None:
            extensions = ['.md', '.js', '.py', '.json', '.yaml', '.yml', '.txt']
        
        for ext in extensions:
            for file_path in dir_path.rglob(f'*{ext}'):
                # 跳过node_modules等目录
                if any(part.startswith('.') or part in ['node_modules', '__pycache__'] 
                       for part in file_path.parts):
                    continue
                
                self.results['total_files'] += 1
                self.check_file(file_path)
    
    def generate_report(self):
        """生成检查报告"""
        report = []
        report.append("# English Compliance Check Report")
        report.append("=" * 50)
        report.append(f"Total files checked: {self.results['total_files']}")
        report.append(f"Files passed: {len(self.results['passed'])}")
        report.append(f"Files failed: {len(self.results['failed'])}")
        report.append(f"Total Chinese characters found: {self.results['total_chinese_chars']}")
        report.append("")
        
        if self.results['failed']:
            report.append("## [FAIL] Files with Chinese content:")
            for failed in self.results['failed']:
                report.append(f"\n### {failed['file']}")
                report.append(f"Chinese characters: {failed['chinese_count']}")
                report.append("Examples:")
                for example in failed['examples']:
                    report.append(f"  Line {example['line']}: {example['content']}")
        
        if self.results['passed']:
            report.append("\n## [PASS] Files passed (no Chinese content):")
            for passed in self.results['passed'][:10]:  # 只显示前10个
                report.append(f"  - {passed}")
            if len(self.results['passed']) > 10:
                report.append(f"  ... and {len(self.results['passed']) - 10} more files")
        
        return '\n'.join(report)
    
    def save_report(self, output_path):
        """保存报告到文件"""
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {output_path}")
    
    def auto_fix_suggestions(self):
        """提供自动修复建议"""
        suggestions = []
        suggestions.append("# Auto-fix Suggestions for Chinese Content")
        suggestions.append("=" * 50)
        
        common_translations = {
            # 文档标题
            "发布指南": "Publishing Guide",
            "贡献指南": "Contributing Guide", 
            "需求验证计划": "Validation Plan",
            "对比分析": "Comparison Analysis",
            "解决的问题": "Problems Solved",
            "功能": "Features",
            "安装": "Installation",
            "使用": "Usage",
            "配置": "Configuration",
            "示例": "Examples",
            "许可证": "License",
            
            # 常见短语
            "感谢您": "Thank you for",
            "立即使用": "Get Started",
            "立即安装": "Install Now",
            "开始使用": "Getting Started",
            "常见问题": "FAQ",
            "故障排除": "Troubleshooting",
            "更新日志": "Changelog",
            "版本历史": "Version History",
            
            # 技术术语
            "命令行界面": "Command Line Interface",
            "图形界面": "Graphical Interface",
            "应用程序接口": "API",
            "软件开发工具包": "SDK",
            "集成开发环境": "IDE",
            
            # 项目特定
            "一致性检查": "Consistency Check",
            "元数据": "Metadata",
            "文档": "Documentation",
            "审核": "Audit",
            "验证": "Validation",
            "测试": "Testing",
            "部署": "Deployment"
        }
        
        suggestions.append("\n## Common Chinese to English Translations:")
        for chinese, english in common_translations.items():
            suggestions.append(f"- `{chinese}` → `{english}`")
        
        suggestions.append("\n## Recommended Workflow:")
        suggestions.append("1. Run this checker before any commit")
        suggestions.append("2. Use translation tools for Chinese content")
        suggestions.append("3. Keep all documentation in English")
        suggestions.append("4. Add this checker to CI/CD pipeline")
        
        return '\n'.join(suggestions)

def main():
    if len(sys.argv) < 2:
        print("Usage: python english_compliance_checker.py <directory> [output_report.md]")
        print("Example: python english_compliance_checker.py ./ openclaw-consistency-checker")
        sys.exit(1)
    
    directory = sys.argv[1]
    output_report = sys.argv[2] if len(sys.argv) > 2 else "english_compliance_report.md"
    
    checker = EnglishComplianceChecker()
    
    print(f"Checking English compliance in: {directory}")
    print("-" * 50)
    
    # 检查文件
    extensions = ['.md', '.js', '.py', '.json', '.yaml', '.yml', '.txt', '.html', '.css']
    checker.check_directory(directory, extensions)
    
    # 生成报告
    report = checker.generate_report()
    try:
        print(report)
    except UnicodeEncodeError:
        # 对于Windows控制台，使用替代字符
        safe_report = report.replace('❌', '[FAIL]').replace('✅', '[PASS]')
        print(safe_report)
    
    # 保存报告
    checker.save_report(output_report)
    
    # 提供修复建议
    suggestions = checker.auto_fix_suggestions()
    suggestions_file = "english_fix_suggestions.md"
    with open(suggestions_file, 'w', encoding='utf-8') as f:
        f.write(suggestions)
    print(f"\nFix suggestions saved to: {suggestions_file}")
    
    # 返回退出码
    if checker.results['failed']:
        print(f"\n❌ FAILED: Found {len(checker.results['failed'])} files with Chinese content")
        sys.exit(1)
    else:
        print("\n✅ PASSED: All files are in English")
        sys.exit(0)

if __name__ == "__main__":
    main()