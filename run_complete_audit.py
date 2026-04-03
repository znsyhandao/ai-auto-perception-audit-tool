"""
运行AISleepGen完整审核
"""

import requests
import json
import time
from datetime import datetime

def run_complete_audit():
    """运行完整审核"""
    print("RUNNING COMPLETE AUDIT ON AISleepGen v1.0.7")
    print("=" * 70)
    
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    print(f"Skill: {skill_id}")
    print(f"Path: {skill_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    audit_results = {}
    
    # 1. 深度分析服务
    print("[1] Deep Analysis Service (Port 8007)...")
    try:
        # 检查服务健康
        health = requests.get("http://localhost:8007/health", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print(f"  Service: {health_data.get('status', 'unknown')}")
            print(f"  Tools available: {health_data.get('available_tools', [])}")
            
            # 执行深度分析
            print("  Running deep analysis with all tools...")
            analysis = requests.post(
                "http://localhost:8007/analyze",
                json={
                    "skill_id": skill_id,
                    "skill_path": skill_path,
                    "analysis_types": ["ast", "control_flow", "data_flow", "performance", "third_party"],
                    "api_key": "demo_key",
                    "timeout_seconds": 60
                },
                timeout=65
            )
            
            if analysis.status_code == 200:
                analysis_data = analysis.json()
                overall_score = analysis_data.get("overall_score", 0)
                audit_results["deep_analysis"] = analysis_data
                
                print(f"  Overall Score: {overall_score}/100")
                print(f"  Analysis Time: {analysis_data.get('analysis_time', 0)}s")
                
                # 显示各工具结果
                for tool, data in analysis_data.get("analysis_summary", {}).items():
                    score = data.get("score", 0)
                    issues = data.get("issues_found", 0)
                    status = data.get("status", "unknown")
                    print(f"    {tool.upper():15} Score: {score:3}/100  Issues: {issues:2}")
                
                print(f"  Critical Issues: {len(analysis_data.get('critical_issues', []))}")
                print(f"  Recommendations: {len(analysis_data.get('recommendations', []))}")
                
            else:
                print(f"  Analysis failed: HTTP {analysis.status_code}")
                audit_results["deep_analysis"] = {"error": f"HTTP {analysis.status_code}"}
                
        else:
            print(f"  Service not healthy: HTTP {health.status_code}")
            audit_results["deep_analysis"] = {"error": f"Service unhealthy: HTTP {health.status_code}"}
            
    except Exception as e:
        print(f"  Error: {str(e)}")
        audit_results["deep_analysis"] = {"error": str(e)}
    
    time.sleep(2)
    
    # 2. 验证服务
    print()
    print("[2] Validation Service (Port 8001)...")
    try:
        response = requests.post(
            "http://localhost:8001/validate",
            json={"skill_id": skill_id, "skill_path": skill_path, "validation_type": "full"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            score = data.get("score", 0)
            audit_results["validation"] = data
            print(f"  Validation Score: {score}/100")
            print(f"  Passed: {data.get('passed', False)}")
        else:
            print(f"  Validation failed: HTTP {response.status_code}")
            audit_results["validation"] = {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"  Error: {str(e)}")
        audit_results["validation"] = {"error": str(e)}
    
    time.sleep(1)
    
    # 3. 安全服务
    print()
    print("[3] Security Service (Port 8002)...")
    try:
        response = requests.post(
            "http://localhost:8002/scan",
            json={"skill_id": skill_id, "skill_path": skill_path, "scan_depth": "standard"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            score = data.get("security_score", 0)
            audit_results["security"] = data
            print(f"  Security Score: {score}/100")
            print(f"  Threats: {data.get('threats_found', 0)}")
        else:
            print(f"  Security scan failed: HTTP {response.status_code}")
            audit_results["security"] = {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"  Error: {str(e)}")
        audit_results["security"] = {"error": str(e)}
    
    # 4. 总结
    print()
    print("=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    
    scores = []
    services_tested = 0
    services_passed = 0
    
    for service, results in audit_results.items():
        if "error" not in results:
            services_tested += 1
            
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
            
            if "score" in results or "overall_score" in results or "security_score" in results:
                actual_score = results.get("score") or results.get("overall_score") or results.get("security_score") or 0
                scores.append(actual_score)
        else:
            print(f"{service.upper():20} ERROR: {results.get('error', 'Unknown')}")
    
    # 计算总体得分
    if scores:
        overall_score = sum(scores) / len(scores)
    else:
        overall_score = 0
    
    print()
    print(f"Services Tested: {services_tested}/3")
    print(f"Services Passed: {services_passed}/3")
    print(f"Overall Audit Score: {overall_score:.1f}/100")
    
    # 审核结论
    if services_tested >= 2 and overall_score >= 70:
        audit_status = "PASSED"
        recommendation = "APPROVED FOR PUBLICATION"
    elif services_tested >= 2 and overall_score >= 50:
        audit_status = "CONDITIONAL PASS"
        recommendation = "APPROVED WITH IMPROVEMENTS RECOMMENDED"
    else:
        audit_status = "FAILED"
        recommendation = "REQUIRES SIGNIFICANT IMPROVEMENT"
    
    print()
    print(f"AUDIT STATUS: {audit_status}")
    print(f"RECOMMENDATION: {recommendation}")
    
    # 保存审核报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "audit_report": {
            "title": "AISleepGen v1.0.7 - Complete Audit Report",
            "audit_date": datetime.now().isoformat(),
            "audit_framework": "Enterprise Audit Framework v3.1.0",
            "audit_scope": "Deep Analysis + Validation + Security"
        },
        "skill_info": {
            "skill_id": skill_id,
            "skill_path": skill_path,
            "version": "1.0.7"
        },
        "audit_results": audit_results,
        "summary": {
            "services_tested": services_tested,
            "services_passed": services_passed,
            "overall_score": round(overall_score, 1),
            "audit_status": audit_status,
            "recommendation": recommendation
        },
        "detailed_scores": {
            "deep_analysis_score": audit_results.get("deep_analysis", {}).get("overall_score", 0),
            "validation_score": audit_results.get("validation", {}).get("score", 0),
            "security_score": audit_results.get("security", {}).get("security_score", 0)
        }
    }
    
    filename = f"AISleepGen_Complete_Audit_Report_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"Complete audit report saved: {filename}")
    print("=" * 70)
    
    return report

if __name__ == "__main__":
    run_complete_audit()