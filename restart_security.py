"""
重启安全服务
"""

import subprocess
import time
import os

print("Restarting Security Service...")

# 杀死可能的安全服务进程
try:
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info['cmdline']
                if cmdline and 'security' in ' '.join(cmdline).lower():
                    print(f"Killing security service PID: {proc.info['pid']}")
                    proc.kill()
        except:
            pass
except:
    print("Note: psutil not available, skipping process kill")

# 启动安全服务
print("Starting security service on port 8002...")

service_dir = "microservices/security-service"
if not os.path.exists(service_dir):
    print(f"ERROR: Service directory not found: {service_dir}")
    exit(1)

try:
    # 在新控制台启动服务
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"],
        cwd=service_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print(f"Security service started with PID: {process.pid}")
    print("Waiting for service to start...")
    
    time.sleep(8)
    
    # 测试服务
    import requests
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print(f"Security service is healthy: {response.json()}")
        else:
            print(f"Security service not healthy: {response.status_code}")
    except Exception as e:
        print(f"Security service test failed: {str(e)}")
        print("But service might still be starting...")
        
except Exception as e:
    print(f"ERROR starting security service: {str(e)}")