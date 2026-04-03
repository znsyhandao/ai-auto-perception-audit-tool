#!/usr/bin/env python3
"""
Fix all dependencies for Enterprise Audit Framework
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package"""
    print(f"[INSTALL] Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[OK] {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install {package}: {e}")
        return False

def main():
    """Main function"""
    print("Enterprise Audit Framework - Dependency Fixer")
    print("=" * 60)
    
    # All required packages
    required_packages = [
        "fastapi",
        "uvicorn[standard]",
        "pydantic",
        "redis",
        "pyyaml",
        "scikit-learn",
        "numpy",
        "pandas",
        "httpx",
        "prometheus-client",
        "structlog",
        "python-json-logger",
        "requests",
        "aiofiles",
        "python-multipart"
    ]
    
    print(f"Installing {len(required_packages)} required packages...")
    print()
    
    success_count = 0
    for package in required_packages:
        if install_package(package):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Summary: {success_count}/{len(required_packages)} packages installed")
    
    if success_count == len(required_packages):
        print("[SUCCESS] All dependencies installed!")
        print("\nNow you can start the services:")
        print("1. API Gateway: uvicorn microservices.api-gateway.main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Open browser: http://localhost:8000")
    else:
        print("[WARNING] Some packages failed to install")
        print("\nYou can manually install missing packages:")
        print("pip install " + " ".join(required_packages))
    
    print("=" * 60)

if __name__ == "__main__":
    main()