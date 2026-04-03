"""
清理环境 - 停止所有服务，清理临时文件
"""

import os
import signal
import subprocess
import time

def stop_mathematical_services():
    """停止数学审核服务"""
    print("Stopping mathematical audit services...")
    
    # 检查并停止端口8000-8010的服务
    ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8030, 8040]
    
    for port in ports:
        try:
            # 查找占用端口的进程
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        pid = parts[-1]
                        print(f"  Found service on port {port}, PID: {pid}")
                        
                        # 尝试停止进程
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=False)
                            print(f"    Stopped PID {pid}")
                        except:
                            print(f"    Failed to stop PID {pid}")
        
        except Exception as e:
            print(f"  Error checking port {port}: {e}")
    
    print("  Mathematical services stopped")

def cleanup_temp_files():
    """清理临时文件"""
    print("Cleaning temporary files...")
    
    temp_files = [
        # 临时Python文件
        "*.pyc",
        "__pycache__",
        
        # 临时数据文件
        "*.tmp",
        "*.temp",
        
        # 日志文件
        "*.log",
        
        # 临时审核报告
        "temp_*.json",
        "temp_*.md"
    ]
    
    # 清理当前目录
    for pattern in temp_files:
        try:
            if os.path.exists(pattern):
                if os.path.isdir(pattern):
                    import shutil
                    shutil.rmtree(pattern)
                    print(f"  Removed directory: {pattern}")
                else:
                    os.remove(pattern)
                    print(f"  Removed file: {pattern}")
        except Exception as e:
            print(f"  Error cleaning {pattern}: {e}")
    
    print("  Temporary files cleaned")

def verify_clean_environment():
    """验证环境是否干净"""
    print("Verifying clean environment...")
    
    # 检查数学服务端口
    math_ports = [8030, 8040, 8009, 8010]
    any_ports_open = False
    
    for port in math_ports:
        try:
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout and 'LISTENING' in result.stdout:
                print(f"  WARNING: Port {port} still in use")
                any_ports_open = True
            else:
                print(f"  Port {port}: clean")
        
        except Exception as e:
            print(f"  Error checking port {port}: {e}")
    
    # 检查Python进程
    try:
        result = subprocess.run(
            'tasklist | findstr python',
            shell=True,
            capture_output=True,
            text=True
        )
        
        python_count = len([line for line in result.stdout.split('\n') if line.strip()])
        print(f"  Python processes running: {python_count}")
        
        if python_count > 5:  # 正常应该有少量Python进程
            print(f"  WARNING: High number of Python processes ({python_count})")
    
    except Exception as e:
        print(f"  Error checking Python processes: {e}")
    
    return not any_ports_open

def main():
    """主清理函数"""
    print("=" * 70)
    print("ENVIRONMENT CLEANUP")
    print("=" * 70)
    
    # 1. 停止服务
    stop_mathematical_services()
    
    # 2. 清理文件
    cleanup_temp_files()
    
    # 3. 等待一下
    print("\nWaiting for processes to terminate...")
    time.sleep(2)
    
    # 4. 验证清理
    print("\n" + "=" * 70)
    clean = verify_clean_environment()
    
    print("\n" + "=" * 70)
    if clean:
        print("ENVIRONMENT CLEANUP COMPLETE")
        print("All mathematical services stopped")
        print("Temporary files cleaned")
        print("Environment ready for fresh start")
    else:
        print("ENVIRONMENT CLEANUP PARTIAL")
        print("Some services may still be running")
        print("Consider manual cleanup if needed")
    
    print("=" * 70)
    
    return clean

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)