"""
启动统一深度分析服务
"""

import subprocess
import time
import os
import sys

def start_deep_analysis_service():
    """启动深度分析服务"""
    print("Starting Unified Deep Analysis Service...")
    print("=" * 60)
    
    # 检查依赖
    print("Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        print("  FastAPI and uvicorn: OK")
    except ImportError:
        print("  ERROR: FastAPI or uvicorn not installed")
        print("  Run: pip install fastapi uvicorn")
        return False
    
    # 检查分析工具
    print("\nChecking analysis tools...")
    tools_dir = os.getcwd()
    required_tools = [
        "ast_analyzer_v1.py",
        "control_flow_analyzer_v1.py",
        "data_flow_analyzer_v1.py",
        "performance_analyzer_v1.py",
        "third_party_analyzer_v1.py"
    ]
    
    missing_tools = []
    for tool in required_tools:
        tool_path = os.path.join(tools_dir, tool)
        if os.path.exists(tool_path):
            print(f"  {tool}: OK")
        else:
            print(f"  {tool}: MISSING")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\nWARNING: {len(missing_tools)} tools missing")
        print("Service will run with limited functionality")
    
    # 切换到服务目录
    service_dir = "microservices/deep-analysis-service"
    if not os.path.exists(service_dir):
        print(f"\nERROR: Service directory not found: {service_dir}")
        return False
    
    # 复制分析工具到服务目录
    print("\nCopying analysis tools to service directory...")
    for tool in required_tools:
        source = os.path.join(tools_dir, tool)
        dest = os.path.join(service_dir, tool)
        if os.path.exists(source) and not os.path.exists(dest):
            import shutil
            shutil.copy2(source, dest)
            print(f"  Copied: {tool}")
    
    print("\nStarting service on port 8007...")
    
    # 启动服务
    try:
        process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007", "--reload"],
            cwd=service_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"Service started with PID: {process.pid}")
        print("Waiting for service to initialize...")
        
        time.sleep(8)
        
        # 测试服务
        print("\nTesting service...")
        try:
            import requests
            response = requests.get("http://localhost:8007/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"  Service health: {health_data.get('status', 'unknown')}")
                print(f"  Tools available: {health_data.get('tools_available', False)}")
                print(f"  Available tools: {health_data.get('available_tools', [])}")
                
                if health_data.get('tools_available'):
                    print("\n✅ Deep Analysis Service is running and ready!")
                else:
                    print("\n⚠️  Service running but some tools unavailable")
                
                print(f"\nService URL: http://localhost:8007")
                print(f"API Docs: http://localhost:8007/docs")
                print(f"Redoc: http://localhost:8007/redoc")
                
                return True
            else:
                print(f"  Service not healthy: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Service test failed: {str(e)}")
            print("  But service might still be starting...")
            return True
            
    except Exception as e:
        print(f"ERROR starting service: {str(e)}")
        return False

if __name__ == "__main__":
    success = start_deep_analysis_service()
    if success:
        print("\n" + "=" * 60)
        print("Deep Analysis Service started successfully!")
        print("=" * 60)
        print("\nKeep this window open to keep the service running.")
        print("Press Ctrl+C to stop the service.")
    else:
        print("\n" + "=" * 60)
        print("Failed to start Deep Analysis Service")
        print("=" * 60)
        sys.exit(1)