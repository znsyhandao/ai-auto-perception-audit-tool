"""
简单重启验证服务
"""

import subprocess
import time
import os

print("Restarting Validator Service...")

# 查找并杀死验证服务进程
try:
    # 使用tasklist找到python进程
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                          capture_output=True, text=True)
    
    for line in result.stdout.split('\n'):
        if 'uvicorn' in line or 'validator' in line.lower():
            parts = line.split(',')
            if len(parts) > 1:
                pid = parts[1].strip('"')
                print(f"Killing Python process: {pid}")
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
except:
    pass

time.sleep(2)

# 启动新的验证服务
print("Starting new Validator Service...")
os.chdir("microservices/validator-service")
subprocess.Popen(['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8001', '--reload'])
os.chdir("../..")

print("Waiting for service to start...")
time.sleep(10)

print("Validator Service restarted!")
print("Test with: python test_ast_validation.py")