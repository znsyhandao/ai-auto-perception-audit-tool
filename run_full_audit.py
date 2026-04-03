"""
企业级审核框架 - 完整审核示例
调用所有6个微服务进行完整审核
"""

import requests
import json
import time
from datetime import datetime

def check_service(url, name):
    """检查服务状态"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, f"{name}: 健康 ✅"
        else:
            return False, f"{name}: 不健康 ❌ (状态码: {response.status_code})"
    except Exception as e:
        return False, f"{name}: 不可达 ❌ ({str(e)})"

def run_full_audit(skill_id, skill_path):
    """运行完整审核"""
    print("=" * 60)
    print("企业级审核框架 - 完整审核")
    print("=" * 60)
    print(f"技能ID: {skill_id}")
    print(f"技能路径: {skill_path}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查所有服务
    print("[1] 检查服务状态...")
    services = [
        ("验证服务", "http://localhost:8001/health"),
        ("安全服务", "http://localhost:8002/health"),
        ("性能服务", "http://localhost:8003/health"),
        ("合规服务", "http://localhost:8004/health"),
        ("报告服务", "http://localhost:8005/health"),
        ("监控服务", "http://localhost:8006/health")
    ]
    
    all_healthy = True
    for name, url in services:
        healthy, message = check_service(url, name)
        print(f"  {message}")
        if not healthy:
            all_healthy = False
    
    if not all_healthy:
        print("❌ 部分服务不可用，请先启动所有服务")
        print("运行: .\start_all_services.ps1")
        return
    
    print()
    print("[2] 开始完整审核流程...")
    
    audit_results = {}
    
    # 步骤1: 验证审核
    print("  [1/6] 验证审核...")
    try:
        response = requests.post(
            "http://localhost:8001/validate",
            json={
                "skill_id": skill_id,
                "skill_path": skill_path,
                "validation_type": "full"
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            audit_results["validation"] = result
            print(f"    得分: {result['score']}/100 ✅")
        else:
            print(f"    失败: {response.status_code} ❌")
    except Exception as e:
        print(f"    错误: {str(e)} ❌")
    
    time.sleep(2)
    
    # 步骤2: 安全扫描
    print("  [2/6] 安全扫描...")
    try:
        response = requests.post(
            "http://localhost:8002/scan",
            json={
                "skill_id": skill_id,
                "skill_path": skill_path,
                "scan_depth": "standard"
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            audit_results["security"] = result
            print(f"    安全得分: {result['security_score']}/100 ✅")
        else:
            print(f"    失败: {response.status_code} ❌")
    except Exception as e:
        print(f"    错误: {str(e)} ❌")
    
    time.sleep(2)
    
    # 步骤3: 性能分析
    print("  [3/6] 性能分析...")
    try:
        response = requests.post(
            "http://localhost:8003/analyze",
            json={
                "skill_id": skill_id,
                "skill_path": skill_path,
                "analysis_type": "full"
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            audit_results["performance"] = result
            print(f"    性能得分: {result['performance_score']}/100 ✅")
        else:
            print(f"    失败: {response.status_code} ❌")
    except Exception as e:
        print(f"    错误: {str(e)} ❌")
    
    time.sleep(2)
    
    # 步骤4: 合规检查
    print("  [4/6] 合规检查...")
    try:
        response = requests.post(
            "http://localhost:8004/check",
            json={
                "skill_id": skill_id,
                "skill_path": skill_path,
                "standards": ["opensource", "security", "code_quality"]
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            audit_results["compliance"] = result
            print(f"    合规得分: {result['compliance_score']}/100 ✅")
        else:
            print(f"    失败: {response.status_code} ❌")
    except Exception as e:
        print(f"    错误: {str(e)} ❌")
    
    time.sleep(2)
    
    # 步骤5: 生成报告
    print("  [5/6] 生成报告...")
    try:
        response = requests.post(
            "http://localhost:8005/generate",
            json={
                "skill_id": skill_id,
                "report_type": "full",
                "format": "json",
                "include_data": True
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            audit_results["report"] = result
            print(f"    报告ID: {result['report_id']} ✅")
        else:
            print(f"    失败: {response.status_code} ❌")
    except Exception as e:
        print(f"    错误: {str(e)} ❌")
    
    time.sleep(2)
    
    # 步骤6: 查看监控
    print("  [6/6] 查看监控状态...")
    try:
        response = requests.get("http://localhost:8006/status", timeout=10)
        if response.status_code == 200:
            result = response.json()
            audit_results["monitoring"] = result
            healthy_count = result["summary"]["healthy"]
            total_count = result["summary"]["total"]
            print(f"    服务状态: {healthy_count}/{total_count} 健康 ✅")
        else:
            print(f"    失败: {response.status_code} ❌")
    except Exception as e:
        print(f"    错误: {str(e)} ❌")
    
    print()
    print("[3] 计算总体得分...")
    
    # 计算总体得分
    scores = []
    if "validation" in audit_results:
        scores.append(audit_results["validation"].get("score", 0))
    if "security" in audit_results:
        scores.append(audit_results["security"].get("security_score", 0))
    if "performance" in audit_results:
        scores.append(audit_results["performance"].get("performance_score", 0))
    if "compliance" in audit_results:
        scores.append(audit_results["compliance"].get("compliance_score", 0))
    
    if scores:
        overall_score = sum(scores) / len(scores)
        
        # 确定风险等级
        if overall_score >= 90:
            risk_level = "很低"
            status = "优秀"
        elif overall_score >= 80:
            risk_level = "低"
            status = "良好"
        elif overall_score >= 70:
            risk_level = "中"
            status = "一般"
        elif overall_score >= 60:
            risk_level = "高"
            status = "需要改进"
        else:
            risk_level = "很高"
            status = "不通过"
        
        print(f"  总体得分: {overall_score:.1f}/100")
        print(f"  风险等级: {risk_level}")
        print(f"  审核状态: {status}")
    else:
        print("  无法计算总体得分")
    
    print()
    print("[4] 保存审核结果...")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"full_audit_{skill_id}_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "skill_id": skill_id,
            "skill_path": skill_path,
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score if 'overall_score' in locals() else None,
            "risk_level": risk_level if 'risk_level' in locals() else None,
            "status": status if 'status' in locals() else None,
            "results": audit_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  结果已保存: {filename}")
    
    print()
    print("=" * 60)
    print("完整审核完成!")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 查看详细报告: http://localhost:8005/reports/")
    print("2. 监控服务状态: http://localhost:8006/status")
    print("3. 查看告警: http://localhost:8006/alerts")
    print("4. 分析指标: http://localhost:8006/metrics")
    print()
    print(f"审核用时: {(datetime.now() - datetime.strptime(audit_results.get('timestamp', datetime.now().isoformat()), '%Y-%m-%dT%H:%M:%S.%f')).seconds} 秒")

if __name__ == "__main__":
    # 默认使用AISleepGen进行测试
    skill_id = "aisleepgen_v1.0.7"
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    print("企业级审核框架 - 完整审核示例")
    print("使用默认技能进行测试:")
    print(f"  技能ID: {skill_id}")
    print(f"  技能路径: {skill_path}")
    print()
    
    # 可以自定义技能
    custom = input("使用自定义技能? (y/n): ").strip().lower()
    if custom == "y":
        skill_id = input("输入技能ID: ").strip()
        skill_path = input("输入技能路径: ").strip()
    
    run_full_audit(skill_id, skill_path)