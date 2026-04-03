"""
最终企业级验证 - AISleepGen v1.0.7
所有3个核心服务现在都在运行
"""

import requests
import json
import time
from datetime import datetime

def final_verification():
    """最终验证"""
    print("=" * 70)
    print("FINAL ENTERPRISE VERIFICATION - AISleepGen v1.0.7")
    print("=" * 70)
    print(f"Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    print(f"Skill: {skill_id}")
    print(f"Path: {skill_path}")
    print()
    
    results = {}
    
    # 1. 验证服务
    print("[1] VALIDATION SERVICE (Port 8001)")
    print("-" * 40)
    
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:8001/validate",
            json={"skill_id": skill_id, "skill_path": skill_path, "validation_type": "full"},
            timeout=15
        )
        validation_time = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            results["validation"] = {
                "score": data.get("score", 0),
                "passed": data.get("passed", False),
                "issues": len(data.get("issues", [])),
                "warnings": len(data.get("warnings", [])),
                "time": round(validation_time, 2)
            }
            print(f"  Score: {data.get('score', 0)}/100")
            print(f"  Passed: {data.get('passed', False)}")
            print(f"  Time: {validation_time:.1f}s")
        else:
            print(f"  Failed: HTTP {response.status_code}")
            results["validation"] = {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"  Error: {str(e)}")
        results["validation"] = {"error": str(e)}
    
    time.sleep(1)
    
    # 2. 安全服务
    print()
    print("[2] SECURITY SERVICE (Port 8002)")
    print("-" * 40)
    
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:8002/scan",
            json={"skill_id": skill_id, "skill_path": skill_path, "scan_depth": "standard"},
            timeout=15
        )
        security_time = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            results["security"] = {
                "score": data.get("security_score", 0),
                "threats": data.get("threats_found", 0),
                "risk_level": data.get("risk_level", "unknown"),
                "time": round(security_time, 2)
            }
            print(f"  Score: {data.get('security_score', 0)}/100")
            print(f"  Threats: {data.get('threats_found', 0)}")
            print(f"  Risk Level: {data.get('risk_level', 'unknown')}")
            print(f"  Time: {security_time:.1f}s")
        else:
            print(f"  Failed: HTTP {response.status_code}")
            results["security"] = {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"  Error: {str(e)}")
        results["security"] = {"error": str(e)}
    
    time.sleep(1)
    
    # 3. 深度分析服务
    print()
    print("[3] DEEP ANALYSIS SERVICE (Port 8007)")
    print("-" * 40)
    
    try:
        # 先检查服务
        health = requests.get("http://localhost:8007/health", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print(f"  Service: {health_data.get('status', 'unknown')}")
            print(f"  Tools: {health_data.get('available_tools', [])}")
            
            # 运行分析（使用AST和Control Flow进行快速分析）
            print("  Running analysis (AST + Control Flow)...")
            start = time.time()
            
            response = requests.post(
                "http://localhost:8007/analyze",
                json={
                    "skill_id": skill_id,
                    "skill_path": skill_path,
                    "analysis_types": ["ast", "control_flow"],
                    "api_key": "demo_key",
                    "timeout_seconds": 45
                },
                timeout=50
            )
            analysis_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                results["deep_analysis"] = {
                    "overall_score": data.get("overall_score", 0),
                    "analysis_time": round(analysis_time, 2),
                    "tools_analyzed": list(data.get("analysis_summary", {}).keys()),
                    "critical_issues": len(data.get("critical_issues", [])),
                    "recommendations": len(data.get("recommendations", []))
                }
                
                print(f"  Overall Score: {data.get('overall_score', 0)}/100")
                print(f"  Analysis Time: {analysis_time:.1f}s")
                
                # 显示工具结果
                for tool, tool_data in data.get("analysis_summary", {}).items():
                    score = tool_data.get("score", 0)
                    issues = tool_data.get("issues_found", 0)
                    print(f"    {tool.upper():15} Score: {score:3}/100  Issues: {issues:2}")
                    
            else:
                print(f"  Analysis Failed: HTTP {response.status_code}")
                results["deep_analysis"] = {"error": f"HTTP {response.status_code}"}
                
        else:
            print(f"  Service Unhealthy: HTTP {health.status_code}")
            results["deep_analysis"] = {"error": f"Service unhealthy: HTTP {health.status_code}"}
            
    except Exception as e:
        print(f"  Error: {str(e)}")
        results["deep_analysis"] = {"error": str(e)}
    
    # 4. 生成最终报告
    print()
    print("=" * 70)
    print("FINAL VERIFICATION RESULTS")
    print("=" * 70)
    
    # 计算总体得分
    scores = []
    services_passed = 0
    total_services = 0
    
    print("Service Results:")
    print("-" * 40)
    
    for service, data in results.items():
        total_services += 1
        
        if "error" not in data:
            if service == "validation":
                score = data.get("score", 0)
                if score >= 70:
                    services_passed += 1
                print(f"  Validation:     {score:5}/100  {'PASS' if score >= 70 else 'FAIL'}")
                scores.append(score)
                
            elif service == "security":
                score = data.get("score", 0)
                if score >= 70:
                    services_passed += 1
                print(f"  Security:       {score:5}/100  {'PASS' if score >= 70 else 'FAIL'}")
                scores.append(score)
                
            elif service == "deep_analysis":
                score = data.get("overall_score", 0)
                if score >= 70:
                    services_passed += 1
                print(f"  Deep Analysis:  {score:5}/100  {'PASS' if score >= 70 else 'FAIL'}")
                scores.append(score)
                
        else:
            print(f"  {service.capitalize():15} ERROR: {data.get('error', 'Unknown')}")
    
    print()
    print("Summary:")
    print("-" * 40)
    
    if scores:
        overall_score = sum(scores) / len(scores)
    else:
        overall_score = 0
    
    print(f"Services Tested: {services_passed}/{total_services}")
    print(f"Overall Enterprise Score: {overall_score:.1f}/100")
    
    # 确定审核状态
    if services_passed >= 2 and overall_score >= 80:
        audit_status = "EXCELLENT"
        recommendation = "HIGHLY RECOMMENDED FOR PRODUCTION RELEASE"
        confidence = "VERY HIGH"
    elif services_passed >= 2 and overall_score >= 70:
        audit_status = "PASSED"
        recommendation = "APPROVED FOR PRODUCTION RELEASE"
        confidence = "HIGH"
    elif services_passed >= 2 and overall_score >= 60:
        audit_status = "CONDITIONAL PASS"
        recommendation = "APPROVED WITH IMPROVEMENTS RECOMMENDED"
        confidence = "MEDIUM"
    else:
        audit_status = "FAILED"
        recommendation = "REQUIRES SIGNIFICANT IMPROVEMENT"
        confidence = "LOW"
    
    print(f"Audit Status: {audit_status}")
    print(f"Recommendation: {recommendation}")
    print(f"Confidence Level: {confidence}")
    
    # 生成最终报告
    final_report = {
        "final_verification_report": {
            "title": "AISleepGen v1.0.7 - Final Enterprise Verification",
            "verification_date": datetime.now().isoformat(),
            "verification_framework": "Enterprise Audit Framework v3.1.0",
            "verification_scope": "Validation + Security + Deep Analysis"
        },
        "skill_info": {
            "skill_id": skill_id,
            "skill_name": "AISleepGen - Sleep Health Analysis",
            "skill_version": "1.0.7",
            "skill_path": skill_path
        },
        "verification_results": results,
        "executive_summary": {
            "overall_enterprise_score": round(overall_score, 1),
            "audit_status": audit_status,
            "recommendation": recommendation,
            "confidence_level": confidence,
            "services_passed": services_passed,
            "services_total": total_services
        },
        "detailed_scores": {
            "validation_score": results.get("validation", {}).get("score", 0),
            "security_score": results.get("security", {}).get("score", 0),
            "deep_analysis_score": results.get("deep_analysis", {}).get("overall_score", 0)
        },
        "verification_conclusion": {
            "final_verdict": audit_status,
            "release_authorization": "GRANTED" if "PASS" in audit_status else "CONDITIONAL" if "CONDITIONAL" in audit_status else "DENIED",
            "enterprise_ready": overall_score >= 70,
            "next_steps": [
                "Publish to ClawHub skill marketplace",
                "Monitor initial user feedback",
                "Schedule follow-up security audit in 90 days"
            ]
        }
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"AISleepGen_Final_Enterprise_Verification_{timestamp}.json"
    
    with open(report_filename, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 70)
    print(f"FINAL VERIFICATION REPORT GENERATED: {report_filename}")
    print("=" * 70)
    
    return final_report

if __name__ == "__main__":
    final_verification()