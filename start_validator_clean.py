"""
启动清洁版验证服务
"""

import subprocess
import time
import os

print("Starting clean validator service...")

# 切换到验证服务目录
os.chdir("microservices/validator-service")

# 启动服务
process = subprocess.Popen(
    ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

print(f"Validator service started with PID: {process.pid}")
print("Waiting for service to start...")

time.sleep(8)

# 回到原目录
os.chdir("../..")

# 测试服务
print("Testing service...")
try:
    import requests
    response = requests.get("http://localhost:8001/health", timeout=5)
    if response.status_code == 200:
        print(f"✅ Validator service is healthy: {response.json()}")
    else:
        print(f"❌ Validator service not healthy: {response.status_code}")
except Exception as e:
    print(f"❌ Validator service test failed: {str(e)}")

print("\nValidator service should be running at: http://localhost:8001")
print("Press Ctrl+C to stop")