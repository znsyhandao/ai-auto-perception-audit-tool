#!/usr/bin/env python3
"""
Check if Enterprise Framework services are running
"""

import sys
import socket
import time

def check_port(port, service_name):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"[OK] {service_name} (port {port}) is running")
            return True
        else:
            print(f"[NOT RUNNING] {service_name} (port {port}) is not responding")
            return False
    except Exception as e:
        print(f"[ERROR] Checking {service_name}: {str(e)}")
        return False

def main():
    """Main check function"""
    print("Enterprise Audit Framework - Service Status Check")
    print("=" * 60)
    
    services = [
        (8000, "API Gateway"),
        (8001, "Validator Service"),
        (8002, "Security Service"),
        (8003, "Performance Service"),
        (8004, "Compliance Service"),
        (8005, "Reporting Service")
    ]
    
    running_services = []
    
    for port, name in services:
        if check_port(port, name):
            running_services.append(name)
    
    print("\n" + "=" * 60)
    print(f"Summary: {len(running_services)}/{len(services)} services running")
    
    if running_services:
        print("\nRunning services:")
        for service in running_services:
            print(f"  • {service}")
        
        print("\nAccess URLs:")
        for port, name in services:
            if name in running_services:
                print(f"  {name}: http://localhost:{port}")
    
    print("\n" + "=" * 60)
    
    if 8000 in [port for port, _ in services if check_port(port, _)]:
        print("[SUCCESS] API Gateway is running!")
        print("Open browser to: http://localhost:8000")
    else:
        print("[WARNING] API Gateway is not running")
        print("\nTo start API Gateway:")
        print("  cd microservices\\api-gateway")
        print("  uvicorn main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()