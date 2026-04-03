"""
快速运行AISleepGen深度分析
"""

import requests
import json
from datetime import datetime

def run_quick_analysis():
    """运行快速分析"""
    print("QUICK ANALYSIS - AISleepGen v1.0.7")
    print("=" * 50)
    
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    print(f"Skill: {skill_id}")
    print(f"Path: {skill_path}")
    print()
    
    try:
        # 运行快速分析（只使用AST和Control Flow）
        print("Running quick analysis (AST + Control Flow)...")
        response = requests.post(
            "http://localhost:8007/analyze",
            json={
                "skill_id": skill_id,
                "skill_path": skill_path,
                "analysis_types": ["ast", "control_flow"],
                "api_key": "demo_key",
                "timeout_seconds": 30
            },
            timeout=35
        )
        
        if response.status_code == 200:
            data = response.json()
            overall_score = data.get("overall_score", 0)
            analysis_time = data.get("analysis_time", 0)
            
            print(f"Analysis completed in {analysis_time} seconds")
            print(f"Overall Score: {overall_score}/100")
            print()
            
            print("Tool Results:")
            for tool, result in data.get("analysis_summary", {}).items():
                score = result.get("score", 0)
                issues = result.get("issues_found", 0)
                status = result.get("status", "unknown")
                print(f"  {tool.upper():15} Score: {score:3}/100  Issues: {issues:2}  Status: {status}")
            
            print()
            critical_issues = data.get("critical_issues", [])
            recommendations = data.get("recommendations", [])
            
            print(f"Critical Issues Found: {len(critical_issues)}")
            if critical_issues:
                for i, issue in enumerate(critical_issues[:3], 1):
                    print(f"  {i}. {issue.get('type', 'unknown')}: {issue.get('message', 'No message')}")
            
            print()
            print(f"Recommendations: {len(recommendations)}")
            if recommendations:
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"  {i}. {rec}")
            
            # 生成报告
            report = {
                "quick_analysis_report": {
                    "title": "AISleepGen v1.0.7 - Quick Deep Analysis",
                    "analysis_date": datetime.now().isoformat(),
                    "analysis_scope": "AST + Control Flow Analysis",
                    "analysis_time_seconds": analysis_time
                },
                "results": {
                    "overall_score": overall_score,
                    "analysis_summary": data.get("analysis_summary", {}),
                    "critical_issues_count": len(critical_issues),
                    "recommendations_count": len(recommendations),
                    "passing_status": "PASS" if overall_score >= 70 else "FAIL"
                },
                "interpretation": {
                    "score_meaning": get_score_meaning(overall_score),
                    "recommendation": get_recommendation(overall_score),
                    "confidence": "MEDIUM"  # 因为是快速分析
                }
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AISleepGen_Quick_Analysis_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print()
            print("=" * 50)
            print(f"Report saved: {filename}")
            print(f"Overall Status: {'PASS' if overall_score >= 70 else 'FAIL'}")
            print(f"Recommendation: {get_recommendation(overall_score)}")
            print("=" * 50)
            
            return report
            
        else:
            print(f"Analysis failed: HTTP {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_score_meaning(score):
    """解释得分含义"""
    if score >= 90:
        return "EXCELLENT - Code quality is very high"
    elif score >= 80:
        return "GOOD - Code quality is good, minor improvements possible"
    elif score >= 70:
        return "ACCEPTABLE - Code quality is acceptable, some improvements recommended"
    elif score >= 60:
        return "NEEDS IMPROVEMENT - Significant improvements needed"
    else:
        return "POOR - Major improvements required"

def get_recommendation(score):
    """根据得分给出建议"""
    if score >= 85:
        return "APPROVED FOR PRODUCTION RELEASE"
    elif score >= 75:
        return "APPROVED WITH MINOR IMPROVEMENTS RECOMMENDED"
    elif score >= 65:
        return "CONDITIONAL APPROVAL - IMPROVEMENTS REQUIRED"
    else:
        return "NOT APPROVED - SIGNIFICANT IMPROVEMENTS NEEDED"

if __name__ == "__main__":
    run_quick_analysis()