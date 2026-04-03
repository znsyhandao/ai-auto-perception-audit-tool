#!/usr/bin/env python3
"""
企业级审核框架 - 本地启动脚本
不依赖Docker，直接在本地启动所有服务
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
import signal
import atexit

class LocalEnterpriseStarter:
    """本地企业级框架启动器"""
    
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.processes = []
        self.services = {
            "api-gateway": {
                "port": 8000,
                "path": self.base_dir / "microservices" / "api-gateway" / "main.py",
                "command": ["python", "main.py"],
                "cwd": self.base_dir / "microservices" / "api-gateway"
            },
            "validator-service": {
                "port": 8001,
                "path": self.base_dir / "microservices" / "validator-service" / "main.py",
                "command": ["python", "main.py"],
                "cwd": self.base_dir / "microservices" / "validator-service"
            },
            "security-service": {
                "port": 8002,
                "path": self.base_dir / "microservices" / "security-service" / "main.py",
                "command": ["python", "main.py"],
                "cwd": self.base_dir / "microservices" / "security-service"
            }
        }
        
        # 注册退出处理
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def check_service_file(self, service_name, service_info):
        """检查服务文件"""
        if not service_info["path"].exists():
            print(f"[ERROR] {service_name} 文件不存在: {service_info['path']}")
            return False
        
        file_size = service_info["path"].stat().st_size
        if file_size < 100:
            print(f"[ERROR] {service_name} 文件太小: {file_size} 字节")
            return False
        
        return True
    
    def start_service(self, service_name, service_info):
        """启动单个服务"""
        print(f"[START] 启动 {service_name} (端口: {service_info['port']})...")
        
        try:
            # 切换到服务目录
            os.chdir(service_info["cwd"])
            
            # 启动服务
            process = subprocess.Popen(
                service_info["command"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            self.processes.append((service_name, process))
            
            # 等待服务启动
            time.sleep(2)
            
            # 检查服务是否运行
            if process.poll() is None:
                print(f"[OK] {service_name} 启动成功 (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"[ERROR] {service_name} 启动失败")
                if stderr:
                    print(f"  错误: {stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 启动 {service_name} 时出错: {str(e)}")
            return False
        finally:
            # 切换回原始目录
            os.chdir(self.base_dir)
    
    def start_all_services(self):
        """启动所有服务"""
        print("=" * 60)
        print("企业级审核框架 v3.0 - 本地启动")
        print("=" * 60)
        print()
        
        # 检查所有服务文件
        print("[CHECK] 检查服务文件...")
        for service_name, service_info in self.services.items():
            if not self.check_service_file(service_name, service_info):
                print(f"[ERROR] {service_name} 检查失败，无法启动")
                return False
        
        print("[OK] 所有服务文件检查通过")
        print()
        
        # 启动服务
        started_services = []
        for service_name, service_info in self.services.items():
            if self.start_service(service_name, service_info):
                started_services.append(service_name)
            else:
                print(f"[WARNING] {service_name} 启动失败，继续启动其他服务...")
        
        print()
        print("=" * 60)
        print("[SUMMARY] 启动摘要:")
        print(f"  成功启动: {len(started_services)}/{len(self.services)} 个服务")
        print(f"  失败: {len(self.services) - len(started_services)} 个服务")
        print()
        
        if started_services:
            print("[SUCCESS] 企业级框架已启动!")
            print()
            print("访问以下服务:")
            for service_name in started_services:
                port = self.services[service_name]["port"]
                print(f"  {service_name}: http://localhost:{port}")
            
            print()
            print("测试API网关:")
            print("  curl http://localhost:8000/")
            print("  curl http://localhost:8000/health")
            print()
            print("测试验证服务:")
            print("  curl http://localhost:8001/")
            print()
            print("测试安全服务:")
            print("  curl http://localhost:8002/")
            print()
            print("按 Ctrl+C 停止所有服务")
            print("=" * 60)
            
            # 保持运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[INFO] 收到停止信号，正在关闭服务...")
        
        return len(started_services) > 0
    
    def cleanup(self):
        """清理所有进程"""
        print("\n[CLEANUP] 正在停止所有服务...")
        for service_name, process in self.processes:
            if process.poll() is None:
                print(f"  停止 {service_name} (PID: {process.pid})...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print(f"  [OK] {service_name} 已停止")
                except subprocess.TimeoutExpired:
                    print(f"  [WARNING] {service_name} 未响应，强制终止...")
                    process.kill()
        
        print("[CLEANUP] 所有服务已停止")
    
    def signal_handler(self, signum, frame):
        """信号处理"""
        print(f"\n[INFO] 收到信号 {signum}，正在关闭...")
        self.cleanup()
        sys.exit(0)

def main():
    """主函数"""
    starter = LocalEnterpriseStarter()
    
    try:
        success = starter.start_all_services()
        if success:
            return 0
        else:
            print("[ERROR] 服务启动失败")
            return 1
    except Exception as e:
        print(f"[ERROR] 启动过程中出错: {str(e)}")
        starter.cleanup()
        return 1

if __name__ == "__main__":
    sys.exit(main())