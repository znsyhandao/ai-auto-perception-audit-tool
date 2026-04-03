"""
启动所有企业级框架服务 - 最终验证版本
"""

import subprocess
import time
import os
import sys

def start_service(service_name, port, directory):
    """启动单个服务"""
    print(f"Starting {service_name} on port {port}...")
    
    if not os.path.exists(directory):
        print(f"  ERROR: Directory not found: {directory}")
        return None
    
    try:
        process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
            cwd=directory,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f"  Started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return None

def check_service_health(port, service_name):
    """检查服务健康状态"""
    import requests
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            print(f"  {service_name} (port {port}): {status}")
            return True
        else:
            print(f"  {service_name} (port {port}): HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  {service_name} (port {port}): {str(e)}")
        return False

def main():
    print("ENTERPRISE FRAMEWORK - COMPLETE VERIFICATION")
    print("=" * 60)
    print("Starting all 7 services...")
    print()
    
    services = [
        ("Validator", 8001, "microservices/validator-service"),
        ("Security", 8002, "microservices/security-service"),
        ("Performance", 8003, "microservices/performance-service"),
        ("Compliance", 8004, "microservices/compliance-service"),
        ("Reporting", 8005, "microservices/reporting-service"),
        ("Monitoring", 8006, "microservices/monitoring-service"),
        ("Deep Analysis", 8007, "microservices/deep-analysis-service")
    ]
    
    processes = []
    
    # 启动所有服务
    for service_name, port, directory in services:
        process = start_service(service_name, port, directory)
        if process:
            processes.append((service_name, port, process))
        time.sleep(2)  # 服务间启动间隔
    
    print()
    print("Waiting for services to initialize...")
    time.sleep(10)
    
    print()
    print("Checking service health...")
    print("-" * 40)
    
    healthy_services = []
    for service_name, port, _ in processes:
        if check_service_health(port, service_name):
            healthy_services.append((service_name, port))
    
    print()
    print("=" * 60)
    print(f"Services started: {len(processes)}/{len(services)}")
    print(f"Services healthy: {len(healthy_services)}/{len(services)}")
    
    if len(healthy_services) >= 5:  # 至少5个服务健康
        print("✅ Framework core services are ready!")
        return True, healthy_services
    else:
        print("⚠️  Some services failed to start")
        return False, healthy_services

if __name__ == "__main__":
    success, healthy_services = main()
    
    if success:
        print()
        print("Next steps:")
        print("1. Run complete AISleepGen analysis")
        print("2. Test service integration")
        print("3. Generate final verification report")
        print()
        print("Keep this window open to maintain services.")
    else:
        print()
        print("Framework verification failed.")
        print("Please check service logs for errors.")
    
    print("=" * 60)