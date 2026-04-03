"""
AISleepGen v1.0.7 完整企业级分析
"""

import requests
import json
import time
from datetime import datetime

def run_complete_analysis():
    """运行完整分析"""
    print("AISleepGen v1.0.7 - COMPLETE ENTERPRISE ANALYSIS")
    print("=" * 70)
    
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    print(f"Skill: {skill_id}")
    print(f"Path: {skill_path}")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    analysis_results = {}
    
    # 1. 深度分析服务
    print("[1] DEEP ANALYSIS SERVICE (Port 8007)")
    print("-" * 40)
    
    try:
        # 检查服务
        health = requests.get("http://localhost:8007/health", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print(f"  Service Status: {health_data.get('status', 'unknown')}")
            print(f"  Available Tools: {health_data.get('available_tools', [])}")
            
            # 运行完整深度分析
            print("  Running complete deep analysis...")
            analysis_start = time.time()
            
            analysis = requests.post(
                "http://localhost:8007/analyze",
                json={
                    "skill_id": skill_id,
                    "skill_path": skill_path,
                    "analysis_types": ["ast", "control_flow", "data_flow", "performance", "third_party"],
                    "api_key": "demo_key",
                    "timeout_seconds": 90
                },
                timeout=95
            )
            
            analysis_time = time.time() - analysis_start
            
            if analysis.status_code == 200:
                analysis_data = analysis.json()
                overall_score = analysis_data.get("overall_score", 0)
                analysis_results["deep_analysis"] = analysis_data
                
                print(f"  Analysis Time: {analysis_time:.1f}s")
                print(f"  Overall Score: {overall_score}/100")
                print()
                
                print("  Tool Results:")
                for tool, data in analysis_data.get("analysis_summary", {}).items():
                    score = data.get("score", 0)
                    issues = data.get("issues_found", 0)
                    status = data.get("status", "unknown")
                    print(f"    {tool.upper():15} Score: {score:3}/100  Issues: {issues:2}  Status: {status}")
                
                critical_issues = analysis_data.get("critical_issues", [])
                recommendations = analysis_data.get("recommendations", [])
                
                print()
                print(f"  Critical Issues: {len(critical_issues)}")
                if critical_issues:
                    for i, issue in enumerate(critical_issues[:3], 1):
                        print(f"    {i}. [{issue.get('severity', 'unknown')}] {issue.get('message', 'No message')}")
                
                print()
                print(f"  Recommendations: {len(recommendations)}")
                if recommendations:
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"    {i}. {rec}")
                        
            else:
                print(f"  Analysis Failed: HTTP {analysis.status_code}")
                print(f"  Response: {analysis.text}")
                analysis_results["deep_analysis"] = {"error": f"HTTP {analysis.status_code}"}
                
        else:
            print(f"  Service Unhealthy: HTTP {health.status_code}")
            analysis_results["deep_analysis"] = {"error": f"Service unhealthy: HTTP {health.status_code}"}
            
    except Exception as e:
        print(f"  Error: {str(e)}")
        analysis_results["deep_analysis"] = {"error": str(e)}
    
    time.sleep(2)
    
    # 2. 验证服务
    print()
    print("[2] VALIDATION SERVICE (Port 8001)")
    print("-" * 40)
    
    try:
        validation = requests.post(
            "http://localhost:8001/validate",
            json={"skill_id": skill_id, "skill_path": skill_path, "validation_type": "full"},
            timeout=10
        )
        
        if validation.status_code == 200:
            validation_data = validation.json()
            validation_score = validation_data.get("score", 0)
            analysis_results["validation"] = validation_data
            
            print(f"  Validation Score: {validation_score}/100")
            print(f"  Passed: {validation_data.get('passed', False)}")
            print(f"  Issues: {len(validation_data.get('issues', []))}")
            print(f"  Warnings: {len(validation_data.get('warnings', []))}")
            
        else:
            print(f"  Validation Failed: HTTP {validation.status_code}")
            analysis_results["validation"] = {"error": f"HTTP {validation.status_code}"}
            
    except Exception as e:
        print(f"  Error: {str(e)}")
        analysis_results["validation"] = {"error": str(e)}
    
    time.sleep(1)
    
    # 3. 安全服务
    print()
    print("[3] SECURITY SERVICE (Port 8002)")
    print("-" * 40)
    
    try:
        security = requests.post(
            "http://localhost:8002/scan",
            json={"skill_id": skill_id, "skill_path": skill_path, "scan_depth": "standard"},
            timeout=10
        )
        
        if security.status_code == 200:
            security_data = security.json()
            security_score = security_data.get("security_score", 0)
            analysis_results["security"] = security_data
            
            print(f"  Security Score: {security_score}/100")
            print(f"  Threats Found: {security_data.get('threats_found', 0)}")
            print(f"  Risk Level: {security_data.get('risk_level', 'unknown')}")
            
        else:
            print(f"  Security Scan Failed: HTTP {security.status_code}")
            analysis_results["security"] = {"error": f"HTTP {security.status_code}"}
            
    except Exception as e:
        print(f"  Error: {str(e)}")
        analysis_results["security"] = {"error": str(e)}
    
    # 4. 生成最终报告
    print()
    print("=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    
    # 计算总体得分
    scores = []
    services_passed = 0
    total_services = 0
    
    for service, results in analysis_results.items():
        total_services += 1
        
        if "error" not in results:
            if service == "deep_analysis":
                score = results.get("overall_score", 0)
                if score >= 70:
                    services_passed += 1
                print(f"{service.upper():20} Score: {score:5}/100  Status: {'PASS' if score >= 70 else 'FAIL'}")
            elif service == "validation":
                score = results.get("score", 0)
                if score >= 70:
                    services_passed += 1
                print(f"{service.upper():20} Score: {score:5}/100  Status: {'PASS' if score >= 70 else 'FAIL'}")
            elif service == "security":
                score = results.get("security_score", 0)
                if score >= 70:
                    services_passed += 1
                print(f"{service.upper():20} Score: {score:5}/100  Status: {'PASS' if score >= 70 else 'FAIL'}")
            
            # 收集分数
            actual_score = results.get("score") or results.get("overall_score") or results.get("security_score") or 0
            scores.append(actual_score)
        else:
            print(f"{service.upper():20} ERROR: {results.get('error', 'Unknown')}")
    
    # 总体评估
    if scores:
        overall_score = sum(scores) / len(scores)
    else:
        overall_score = 0
    
    print()
    print(f"Services Analyzed: {services_passed}/{total_services}")
    print(f"Overall Enterprise Score: {overall_score:.1f}/100")
    
    # 确定审核状态
    if services_passed >= 2 and overall_score >= 75:
        audit_status = "PASSED"
        recommendation = "APPROVED FOR PRODUCTION RELEASE"
        confidence = "HIGH"
    elif services_passed >= 2 and overall_score >= 65:
        audit_status = "CONDITIONAL PASS"
        recommendation = "APPROVED WITH IMPROVEMENTS RECOMMENDED"
        confidence = "MEDIUM"
    else:
        audit_status = "FAILED"
        recommendation = "REQUIRES SIGNIFICANT IMPROVEMENT"
        confidence = "LOW"
    
    print()
    print(f"AUDIT STATUS: {audit_status}")
    print(f"RECOMMENDATION: {recommendation}")
    print(f"CONFIDENCE LEVEL: {confidence}")
    
    # 生成最终报告
    final_report = {
        "enterprise_audit_report": {
            "title": "AISleepGen v1.0.7 - Complete Enterprise Audit Report",
            "audit_date": datetime.now().isoformat(),
            "audit_framework": "Enterprise Audit Framework v3.1.0",
            "audit_scope": "Deep Analysis + Validation + Security",
            "audit_duration": f"{analysis_time:.1f} seconds"
        },
        "skill_information": {
            "skill_id": skill_id,
            "skill_name": "AISleepGen - Sleep Health Analysis",
            "skill_version": "1.0.7",
            "skill_path": skill_path
        },
        "analysis_results": analysis_results,
        "executive_summary": {
            "overall_enterprise_score": round(overall_score, 1),
            "audit_status": audit_status,
            "recommendation": recommendation,
            "confidence_level": confidence,
            "services_analyzed": services_passed,
            "services_total": total_services
        },
        "detailed_scores": {
            "deep_analysis_score": analysis_results.get("deep_analysis", {}).get("overall_score", 0),
            "validation_score": analysis_results.get("validation", {}).get("score", 0),
            "security_score": analysis_results.get("security", {}).get("security_score", 0)
        },
        "audit_conclusion": {
            "verdict": audit_status,
            "release_authorization": "GRANTED" if audit_status == "PASSED" else "CONDITIONAL" if audit_status == "CONDITIONAL PASS" else "DENIED",
            "next_review_date": "2026-06-30",
            "monitoring_requirements": "Monitor first 50 downloads for feedback"
        }
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"AISleepGen_Complete_Enterprise_Audit_{timestamp}.json"
    
    with open(report_filename, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 70)
    print(f"COMPLETE AUDIT REPORT GENERATED: {report_filename}")
    print("=" * 70)
    
    return final_report

if __name__ == "__main__":
    run_complete_analysis()