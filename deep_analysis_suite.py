#!/usr/bin/env python3
"""
深度分析套件 v1.0
集成所有深度分析工具，提供一站式深度代码分析
"""

import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

# 导入所有深度分析工具
try:
    from ast_analyzer_v1 import analyze_file as ast_analyze
    from control_flow_analyzer_v1 import analyze_file as control_flow_analyze
    from third_party_analyzer_v1 import analyze_file as third_party_analyze
    from data_flow_analyzer_v1 import analyze_file as data_flow_analyze
    from performance_analyzer_v1 import analyze_file as performance_analyze
except ImportError as e:
    print(f"Error importing analysis tools: {e}")
    print("Make sure all analysis tools are in the same directory")
    sys.exit(1)

class DeepAnalysisSuite:
    """深度分析套件"""
    
    def __init__(self, file_path: str, requirements_file: str = None):
        self.file_path = file_path
        self.requirements_file = requirements_file
        self.all_reports = {}
        self.combined_issues = []
        
    def run_all_analyses(self):
        """运行所有深度分析"""
        print(f"Running deep analysis on: {self.file_path}")
        print("=" * 80)
        
        # 1. AST分析
        print("1. Running AST analysis...")
        try:
            self.all_reports['ast'] = ast_analyze(self.file_path)
            print(f"   [OK] AST analysis completed: {self.all_reports['ast']['stats']['total']} issues")
        except Exception as e:
            print(f"   [ERROR] AST analysis failed: {e}")
            self.all_reports['ast'] = {'error': str(e)}
        
        # 2. 控制流分析
        print("2. Running control flow analysis...")
        try:
            self.all_reports['control_flow'] = control_flow_analyze(self.file_path)
            print(f"   [OK] Control flow analysis completed: {self.all_reports['control_flow']['stats']['total']} issues")
        except Exception as e:
            print(f"   [ERROR] Control flow analysis failed: {e}")
            self.all_reports['control_flow'] = {'error': str(e)}
        
        # 3. 第三方库分析
        print("3. Running third-party library analysis...")
        try:
            self.all_reports['third_party'] = third_party_analyze(self.file_path, self.requirements_file)
            print(f"   [OK] Third-party analysis completed: {self.all_reports['third_party']['stats']['total']} issues")
        except Exception as e:
            print(f"   [ERROR] Third-party analysis failed: {e}")
            self.all_reports['third_party'] = {'error': str(e)}
        
        # 4. 数据流分析
        print("4. Running data flow analysis...")
        try:
            self.all_reports['data_flow'] = data_flow_analyze(self.file_path)
            print(f"   [OK] Data flow analysis completed: {self.all_reports['data_flow']['stats']['total']} issues")
        except Exception as e:
            print(f"   [ERROR] Data flow analysis failed: {e}")
            self.all_reports['data_flow'] = {'error': str(e)}
        
        # 5. 性能分析
        print("5. Running performance analysis...")
        try:
            self.all_reports['performance'] = performance_analyze(self.file_path)
            print(f"   [OK] Performance analysis completed: {self.all_reports['performance']['stats']['total']} issues")
        except Exception as e:
            print(f"   [ERROR] Performance analysis failed: {e}")
            self.all_reports['performance'] = {'error': str(e)}
        
        print("=" * 80)
        print("All analyses completed!")
    
    def combine_results(self):
        """合并所有分析结果"""
        total_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0
        
        for tool_name, report in self.all_reports.items():
            if 'error' in report:
                continue
            
            total_issues += report['stats']['total']
            high_issues += report['stats']['high']
            medium_issues += report['stats']['medium']
            low_issues += report['stats']['low']
            
            # 收集所有问题
            if 'issues' in report:
                for issue in report['issues']:
                    issue['tool'] = tool_name
                    self.combined_issues.append(issue)
        
        return {
            'total_issues': total_issues,
            'high_issues': high_issues,
            'medium_issues': medium_issues,
            'low_issues': low_issues,
            'tools_analyzed': len([r for r in self.all_reports.values() if 'error' not in r]),
            'tools_failed': len([r for r in self.all_reports.values() if 'error' in r])
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        stats = self.combine_results()
        
        # 按严重性排序问题
        self.combined_issues.sort(key=lambda x: (
            0 if x['severity'] == 'HIGH' else 
            1 if x['severity'] == 'MEDIUM' else 2,
            x['line']
        ))
        
        # 生成摘要
        summary_parts = []
        if stats['high_issues'] > 0:
            summary_parts.append(f"[HIGH] {stats['high_issues']} issues")
        if stats['medium_issues'] > 0:
            summary_parts.append(f"[MEDIUM] {stats['medium_issues']} issues")
        if stats['low_issues'] > 0:
            summary_parts.append(f"[LOW] {stats['low_issues']} issues")
        
        summary = " | ".join(summary_parts) if summary_parts else "[PASS] No issues found"
        
        # 评估代码质量
        quality_score = self._calculate_quality_score(stats)
        quality_level = self._get_quality_level(quality_score)
        
        return {
            'file': self.file_path,
            'analysis_time': datetime.now().isoformat(),
            'stats': stats,
            'quality_assessment': {
                'score': quality_score,
                'level': quality_level,
                'recommendation': self._get_recommendation(quality_level)
            },
            'summary': summary,
            'detailed_issues': self.combined_issues,
            'tool_reports': self.all_reports
        }
    
    def _calculate_quality_score(self, stats: Dict) -> float:
        """计算代码质量分数"""
        max_score = 100
        
        # 扣分规则
        deductions = 0
        deductions += stats['high_issues'] * 10  # 每个高危问题扣10分
        deductions += stats['medium_issues'] * 5  # 每个中危问题扣5分
        deductions += stats['low_issues'] * 2  # 每个低危问题扣2分
        
        # 工具失败扣分
        deductions += self.all_reports.get('tools_failed', 0) * 20
        
        score = max(0, max_score - deductions)
        return round(score, 1)
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 75:
            return "GOOD"
        elif score >= 60:
            return "FAIR"
        elif score >= 40:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _get_recommendation(self, quality_level: str) -> str:
        """获取建议"""
        recommendations = {
            "EXCELLENT": "Code quality is excellent. Ready for production.",
            "GOOD": "Code quality is good. Some minor improvements suggested.",
            "FAIR": "Code quality is fair. Consider addressing the identified issues.",
            "POOR": "Code quality is poor. Significant improvements needed before production.",
            "CRITICAL": "Code quality is critical. Major security and performance issues found."
        }
        return recommendations.get(quality_level, "Unknown quality level")
    
    def print_comprehensive_report(self, verbose: bool = False):
        """打印综合报告"""
        report = self.generate_comprehensive_report()
        
        print("=" * 80)
        print("DEEP CODE ANALYSIS COMPREHENSIVE REPORT")
        print("=" * 80)
        print(f"File: {report['file']}")
        print(f"Analysis Time: {report['analysis_time']}")
        print(f"Tools Analyzed: {report['stats']['tools_analyzed']}/5")
        print(f"Tools Failed: {report['stats']['tools_failed']}")
        print("-" * 80)
        
        # 质量评估
        print("QUALITY ASSESSMENT:")
        print(f"  Score: {report['quality_assessment']['score']}/100")
        print(f"  Level: {report['quality_assessment']['level']}")
        print(f"  Recommendation: {report['quality_assessment']['recommendation']}")
        print("-" * 80)
        
        # 问题统计
        print("ISSUE STATISTICS:")
        print(f"  Total Issues: {report['stats']['total_issues']}")
        print(f"  High-risk: {report['stats']['high_issues']}")
        print(f"  Medium-risk: {report['stats']['medium_issues']}")
        print(f"  Low-risk: {report['stats']['low_issues']}")
        print(f"  Summary: {report['summary']}")
        print("-" * 80)
        
        # 工具详情
        print("TOOL DETAILS:")
        for tool_name, tool_report in report['tool_reports'].items():
            if 'error' in tool_report:
                print(f"  {tool_name.upper()}: FAILED - {tool_report['error']}")
            else:
                stats = tool_report['stats']
                print(f"  {tool_name.upper()}: {stats['total']} issues ({stats['high']}H/{stats['medium']}M/{stats['low']}L)")
        
        print("-" * 80)
        
        # 详细问题
        if verbose and report['detailed_issues']:
            print("DETAILED ISSUES:")
            for issue in report['detailed_issues']:
                print(f"  [{issue['severity']}] [{issue['tool']}] L{issue['line']}: {issue['type']}")
                print(f"      {issue['message']}")
        
        print("=" * 80)
        
        # 保存报告
        self._save_report(report)
    
    def _save_report(self, report: Dict[str, Any]):
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deep_analysis_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Report saved to: {filename}")


def analyze_file(file_path: str, requirements_file: str = None, verbose: bool = False):
    """分析单个文件"""
    suite = DeepAnalysisSuite(file_path, requirements_file)
    suite.run_all_analyses()
    suite.print_comprehensive_report(verbose)
    
    # 返回退出码
    report = suite.generate_comprehensive_report()
    if report['stats']['high_issues'] > 0:
        return 1
    return 0


def analyze_directory(directory: str, verbose: bool = False):
    """分析目录"""
    print(f"Analyzing directory: {directory}")
    print("=" * 80)
    
    total_files = 0
    total_issues = 0
    files_with_issues = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"\nAnalyzing: {file_path}")
                
                try:
                    # 查找requirements.txt
                    req_file = None
                    if os.path.exists(os.path.join(directory, 'requirements.txt')):
                        req_file = os.path.join(directory, 'requirements.txt')
                    
                    suite = DeepAnalysisSuite(file_path, req_file)
                    suite.run_all_analyses()
                    report = suite.generate_comprehensive_report()
                    
                    total_files += 1
                    total_issues += report['stats']['total_issues']
                    
                    if report['stats']['total_issues'] > 0:
                        files_with_issues += 1
                        print(f"  Issues found: {report['stats']['total_issues']} (H:{report['stats']['high_issues']}/M:{report['stats']['medium_issues']}/L:{report['stats']['low_issues']})")
                    else:
                        print(f"  No issues found")
                        
                except Exception as e:
                    print(f"  Analysis failed: {e}")
    
    print("\n" + "=" * 80)
    print("DIRECTORY ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total Python files: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues found: {total_issues}")
    print("=" * 80)
    
    if files_with_issues > 0:
        return 1
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deep Code Analysis Suite")
    parser.add_argument("target", help="File or directory to analyze")
    parser.add_argument("-r", "--requirements", help="Requirements.txt file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-d", "--directory", action="store_true", help="Analyze directory")
    
    args = parser.parse_args()
    
    if args.directory:
        exit_code = analyze_directory(args.target, args.verbose)
    else:
        exit_code = analyze_file(args.target, args.requirements, args.verbose)
    
    sys.exit(exit_code)