#!/usr/bin/env python3
"""
Enterprise Audit Framework v3.0 - Local Starter (No Docker)
Start all services locally without Docker
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
import signal
import atexit

class LocalStarter:
    """Local service starter without Docker"""
    
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.processes = []
        
        # Service configurations
        self.services = {
            "api-gateway": {
                "port": 8000,
                "module": "microservices.api-gateway.main",
                "description": "API Gateway - Main entry point"
            },
            "validator-service": {
                "port": 8001,
                "module": "microservices.validator-service.main",
                "description": "Validator Service - Basic validation"
            },
            "security-service": {
                "port": 8002,
                "module": "microservices.security-service.main",
                "description": "Security Service - AI-driven analysis"
            }
        }
        
        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def check_python_dependencies(self):
        """Check Python dependencies"""
        print("[CHECK] Checking Python dependencies...")
        
        required_packages = [
            ("fastapi", "fastapi"),
            ("uvicorn", "uvicorn"),
            ("redis", "redis"),
            ("pyyaml", "yaml"),
            ("scikit-learn", "sklearn"),
            ("numpy", "numpy")
        ]
        
        missing = []
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                print(f"  [OK] {package_name}")
            except ImportError:
                missing.append(package_name)
                print(f"  [MISSING] {package_name}")
        
        if missing:
            print(f"\n[WARNING] Missing packages: {', '.join(missing)}")
            print("Install with: pip install " + " ".join(missing))
            return False
        
        print("[OK] All Python dependencies satisfied")
        return True
    
    def start_service(self, service_name, service_info):
        """Start a single service"""
        print(f"[START] Starting {service_name} on port {service_info['port']}...")
        print(f"  Description: {service_info['description']}")
        
        try:
            # Import and run the service
            module_path = service_info['module'].replace('.', '/') + '.py'
            full_path = self.base_dir / module_path
            
            if not full_path.exists():
                print(f"  [ERROR] Module file not found: {full_path}")
                return False
            
            # Start the service in a subprocess
            cmd = [sys.executable, "-m", "uvicorn", 
                   f"{service_info['module']}:app",
                   "--host", "0.0.0.0",
                   "--port", str(service_info['port']),
                   "--reload"]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            self.processes.append((service_name, process))
            
            # Wait a bit for startup
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"  [OK] {service_name} started (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"  [ERROR] {service_name} failed to start")
                if stderr:
                    error_lines = stderr.split('\n')[:5]
                    for line in error_lines:
                        if line.strip():
                            print(f"    {line[:100]}")
                return False
                
        except Exception as e:
            print(f"  [ERROR] Failed to start {service_name}: {str(e)}")
            return False
    
    def start_all_services(self):
        """Start all services"""
        print("=" * 60)
        print("Enterprise Audit Framework v3.0 - Local Deployment")
        print("=" * 60)
        print()
        
        # Check dependencies
        if not self.check_python_dependencies():
            print("\n[ERROR] Missing dependencies. Please install required packages.")
            return False
        
        print()
        
        # Start services
        started_services = []
        for service_name, service_info in self.services.items():
            if self.start_service(service_name, service_info):
                started_services.append(service_name)
            else:
                print(f"[WARNING] {service_name} failed, continuing...")
        
        print()
        print("=" * 60)
        print("[SUMMARY] Startup Summary:")
        print(f"  Successfully started: {len(started_services)}/{len(self.services)} services")
        print()
        
        if started_services:
            print("[SUCCESS] Enterprise Framework is running!")
            print()
            print("Access the following services:")
            for service_name in started_services:
                port = self.services[service_name]["port"]
                print(f"  {service_name}: http://localhost:{port}")
            
            print()
            print("Test endpoints:")
            print("  API Gateway: curl http://localhost:8000/")
            print("  Health check: curl http://localhost:8000/health")
            print("  Validator: curl http://localhost:8001/")
            print("  Security: curl http://localhost:8002/")
            print()
            print("Press Ctrl+C to stop all services")
            print("=" * 60)
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[INFO] Stopping services...")
        
        return len(started_services) > 0
    
    def cleanup(self):
        """Cleanup all processes"""
        print("\n[CLEANUP] Stopping all services...")
        for service_name, process in self.processes:
            if process.poll() is None:
                print(f"  Stopping {service_name} (PID: {process.pid})...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print(f"  [OK] {service_name} stopped")
                except subprocess.TimeoutExpired:
                    print(f"  [WARNING] {service_name} not responding, killing...")
                    process.kill()
        
        print("[CLEANUP] All services stopped")
    
    def signal_handler(self, signum, frame):
        """Signal handler"""
        print(f"\n[INFO] Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)

def test_endpoints():
    """Test if endpoints are accessible"""
    print("\n" + "=" * 60)
    print("[TEST] Testing service endpoints...")
    
    import requests
    
    endpoints = [
        ("API Gateway", "http://localhost:8000/"),
        ("Validator Service", "http://localhost:8001/"),
        ("Security Service", "http://localhost:8002/")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"  [OK] {name}: {url} - Status: {response.status_code}")
            else:
                print(f"  [WARNING] {name}: {url} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {name}: {url} - {str(e)}")

def main():
    """Main function"""
    starter = LocalStarter()
    
    print("Enterprise Audit Framework v3.0 - Local Deployment")
    print("No Docker required!")
    print()
    
    try:
        success = starter.start_all_services()
        if success:
            # Test endpoints after startup
            time.sleep(5)
            test_endpoints()
            return 0
        else:
            print("[ERROR] Failed to start services")
            return 1
    except Exception as e:
        print(f"[ERROR] Error during startup: {str(e)}")
        starter.cleanup()
        return 1

if __name__ == "__main__":
    sys.exit(main())