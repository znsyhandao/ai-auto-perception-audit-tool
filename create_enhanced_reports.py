#!/usr/bin/env python3
"""
创建增强的报告格式
"""

import json
import os
from datetime import datetime

def create_html_report(data, output_file):
    """创建HTML报告"""
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deep Code Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .summary-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }
        .summary-card.high { border-left: 4px solid #dc3545; }
        .summary-card.medium { border-left: 4px solid #ffc107; }
        .summary-card.low { border-left: 4px solid #28a745; }
        .summary-card.info { border-left: 4px solid #17a2b8; }
        .issue-list { margin-top: 20px; }
        .issue-item { padding: 10px; margin: 5px 0; border-left: 4px solid #ccc; background: #f8f9fa; }
        .issue-item.high { border-left-color: #dc3545; background: #f8d7da; }
        .issue-item.medium { border-left-color: #ffc107; background: #fff3cd; }
        .issue-item.low { border-left-color: #28a745; background: #d4edda; }
        .tool-results { margin-top: 20px; }
        .tool-card { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .quality-score { font-size: 48px; font-weight: bold; text-align: center; margin: 20px 0; }
        .quality-score.excellent { color: #28a745; }
        .quality-score.good { color: #17a2b8; }
        .quality-score.fair { color: #ffc107; }
        .quality-score.poor { color: #fd7e14; }
        .quality-score.critical { color: #dc3545; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .recommendation { background: #e7f3ff; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .timestamp { color: #6c757d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Deep Code Analysis Report</h1>
            <p class="timestamp">Generated: {{timestamp}}</p>
        </div>
        
        <div class="quality-score {{quality_class}}">
            {{quality_score}}/100
            <div style="font-size: 16px; margin-top: 5px;">{{quality_level}}</div>
        </div>
        
        <div class="recommendation">
            <h3>Recommendation</h3>
            <p>{{recommendation}}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card high">
                <h3>High Risk</h3>
                <p style="font-size: 24px; font-weight: bold; color: #dc3545;">{{high_issues}}</p>
            </div>
            <div class="summary-card medium">
                <h3>Medium Risk</h3>
                <p style="font-size: 24px; font-weight: bold; color: #ffc107;">{{medium_issues}}</p>
            </div>
            <div class="summary-card low">
                <h3>Low Risk</h3>
                <p style="font-size: 24px; font-weight: bold; color: #28a745;">{{low_issues}}</p>
            </div>
            <div class="summary-card info">
                <h3>Total Issues</h3>
                <p style="font-size: 24px; font-weight: bold; color: #17a2b8;">{{total_issues}}</p>
            </div>
        </div>
        
        <h2>Issues by Tool</h2>
        <table>
            <thead>
                <tr>
                    <th>Tool</th>
                    <th>Total Issues</th>
                    <th>High</th>
                    <th>Medium</th>
                    <th>Low</th>
                </tr>
            </thead>
            <tbody>
                {{tool_rows}}
            </tbody>
        </table>
        
        <h2>Detailed Issues</h2>
        <div class="issue-list">
            {{issue_items}}
        </div>
        
        <div class="tool-results">
            <h2>Tool Results</h2>
            {{tool_details}}
        </div>
    </div>
</body>
</html>'''
    
    # 准备数据
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    quality_score = data.get('quality_assessment', {}).get('score', 0)
    quality_level = data.get('quality_assessment', {}).get('level', 'UNKNOWN')
    recommendation = data.get('quality_assessment', {}).get('recommendation', '')
    
    # 确定质量类别
    quality_class = 'critical'
    if quality_score >= 90:
        quality_class = 'excellent'
    elif quality_score >= 75:
        quality_class = 'good'
    elif quality_score >= 60:
        quality_class = 'fair'
    elif quality_score >= 40:
        quality_class = 'poor'
    
    # 统计问题
    stats = data.get('stats', {})
    high_issues = stats.get('high_issues', 0)
    medium_issues = stats.get('medium_issues', 0)
    low_issues = stats.get('low_issues', 0)
    total_issues = stats.get('total_issues', 0)
    
    # 生成工具行
    tool_rows = ''
    tool_reports = data.get('tool_reports', {})
    for tool_name, tool_data in tool_reports.items():
        if isinstance(tool_data, dict) and 'stats' in tool_data:
            tool_stats = tool_data['stats']
            tool_rows += f'''
            <tr>
                <td>{tool_name.upper()}</td>
                <td>{tool_stats.get('total', 0)}</td>
                <td>{tool_stats.get('high', 0)}</td>
                <td>{tool_stats.get('medium', 0)}</td>
                <td>{tool_stats.get('low', 0)}</td>
            </tr>'''
    
    # 生成问题项
    issue_items = ''
    detailed_issues = data.get('detailed_issues', [])
    for issue in detailed_issues:
        severity = issue.get('severity', 'LOW').lower()
        issue_items += f'''
        <div class="issue-item {severity}">
            <strong>[{issue.get('severity', 'UNKNOWN')}] [{issue.get('tool', 'UNKNOWN')}]</strong>
            <br>Line {issue.get('line', 0)}: {issue.get('type', 'Unknown')}
            <br>{issue.get('message', 'No message')}
        </div>'''
    
    # 生成工具详情
    tool_details = ''
    for tool_name, tool_data in tool_reports.items():
        if isinstance(tool_data, dict):
            tool_details += f'''
            <div class="tool-card">
                <h3>{tool_name.upper()}</h3>
                <p>Status: {'[OK]' if 'error' not in tool_data else '[ERROR]'}</p>
                {f'<p>Issues: {tool_data.get("stats", {}).get("total", 0)}</p>' if 'stats' in tool_data else ''}
            </div>'''
    
    # 替换模板变量
    html_content = html_template
    replacements = {
        '{{timestamp}}': timestamp,
        '{{quality_score}}': quality_score,
        '{{quality_level}}': quality_level,
        '{{quality_class}}': quality_class,
        '{{recommendation}}': recommendation,
        '{{high_issues}}': high_issues,
        '{{medium_issues}}': medium_issues,
        '{{low_issues}}': low_issues,
        '{{total_issues}}': total_issues,
        '{{tool_rows}}': tool_rows,
        '{{issue_items}}': issue_items,
        '{{tool_details}}': tool_details
    }
    
    for key, value in replacements.items():
        html_content = html_content.replace(key, str(value))
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report created: {output_file}")
    return output_file

def create_markdown_report(data, output_file):
    """创建Markdown报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    quality_score = data.get('quality_assessment', {}).get('score', 0)
    quality_level = data.get('quality_assessment', {}).get('level', 'UNKNOWN')
    recommendation = data.get('quality_assessment', {}).get('recommendation', '')
    
    stats = data.get('stats', {})
    high_issues = stats.get('high_issues', 0)
    medium_issues = stats.get('medium_issues', 0)
    low_issues = stats.get('low_issues', 0)
    total_issues = stats.get('total_issues', 0)
    
    markdown = f"""# Deep Code Analysis Report

**Generated**: {timestamp}
**File**: {data.get('file', 'Unknown')}

## Quality Assessment

**Score**: {quality_score}/100
**Level**: {quality_level}
**Recommendation**: {recommendation}

## Summary

| Metric | Count |
|--------|-------|
| Total Issues | {total_issues} |
| High Risk | {high_issues} |
| Medium Risk | {medium_issues} |
| Low Risk | {low_issues} |

## Issues by Tool

| Tool | Total | High | Medium | Low |
|------|-------|------|--------|-----|
"""
    
    # 添加工具行
    tool_reports = data.get('tool_reports', {})
    for tool_name, tool_data in tool_reports.items():
        if isinstance(tool_data, dict) and 'stats' in tool_data:
            tool_stats = tool_data['stats']
            markdown += f"| {tool_name.upper()} | {tool_stats.get('total', 0)} | {tool_stats.get('high', 0)} | {tool_stats.get('medium', 0)} | {tool_stats.get('low', 0)} |\n"
    
    markdown += "\n## Detailed Issues\n\n"
    
    # 添加详细问题
    detailed_issues = data.get('detailed_issues', [])
    for issue in detailed_issues:
        severity = issue.get('severity', 'LOW')
        tool = issue.get('tool', 'UNKNOWN')
        line = issue.get('line', 0)
        issue_type = issue.get('type', 'Unknown')
        message = issue.get('message', 'No message')
        
        markdown += f"### [{severity}] [{tool}] Line {line}: {issue_type}\n"
        markdown += f"{message}\n\n"
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Markdown report created: {output_file}")
    return output_file

def main():
    """主函数"""
    # 查找最新的分析报告
    report_files = [f for f in os.listdir('.') if f.startswith('deep_analysis_report_') and f.endswith('.json')]
    
    if not report_files:
        print("No analysis reports found. Run deep_analysis_suite.py first.")
        return
    
    # 使用最新的报告
    latest_report = max(report_files, key=os.path.getmtime)
    print(f"Using report: {latest_report}")
    
    # 加载数据
    with open(latest_report, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建报告
    base_name = os.path.splitext(latest_report)[0]
    html_file = create_html_report(data, f"{base_name}.html")
    md_file = create_markdown_report(data, f"{base_name}.md")
    
    print(f"\nReports created:")
    print(f"  HTML: {html_file}")
    print(f"  Markdown: {md_file}")
    print(f"\nOpen {html_file} in browser to view the report.")

if __name__ == "__main__":
    main()