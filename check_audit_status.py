"""
Check AISleepGen Audit Status - Windows Console Compatible
"""

import requests
import json
import sys

def check_service(url, name):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, f"[OK] {name} is running"
        else:
            return False, f"[ERROR] {name}: Status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"[ERROR] {name}: {str(e)}"

def main():
    print("=" * 60)
    print("AISleepGen Audit Status Check")
    print("=" * 60)
    print()
    
    # Check services
    print("[CHECK] Checking services...")
    print()
    
    services = [
        ("Validator Service", "http://localhost:8001/"),
        ("Security Service", "http://localhost:8002/")
    ]
    
    all_services_ok = True
    for name, url in services:
        ok, message = check_service(url, name)
        print(message)
        if not ok:
            all_services_ok = False
    
    print()
    
    if not all_services_ok:
        print("[WARNING] Some services are not responding")
        print("Please start the services:")
        print("1. Validator: cd microservices\\validator-service && uvicorn main_fixed:app --host 0.0.0.0 --port 8001 --reload")
        print("2. Security: cd microservices\\security-service && uvicorn main_fixed:app --host 0.0.0.0 --port 8002 --reload")
        return
    
    # Check AISleepGen skill path
    print("[INFO] Checking AISleepGen skill...")
    import os
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    if os.path.exists(skill_path):
        file_count = len([f for f in os.listdir(skill_path) if os.path.isfile(os.path.join(skill_path, f))])
        print(f"  Skill path: {skill_path}")
        print(f"  Files: {file_count}")
    else:
        print(f"  [ERROR] Skill path not found: {skill_path}")
        return
    
    print()
    
    # Try to get validation result
    print("[1] Checking validation result...")
    try:
        response = requests.get("http://localhost:8001/validate/aisleepgen_v1.0.7", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"  [FOUND] Validation result exists")
            print(f"    Score: {result.get('score', 'N/A')}/100")
            print(f"    Passed: {result.get('passed', 'N/A')}")
        elif response.status_code == 404:
            print("  [INFO] No validation result yet - audit not started or in progress")
        else:
            print(f"  [ERROR] Unexpected status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not check validation: {str(e)}")
    
    print()
    
    # Try to get security scan result
    print("[2] Checking security scan result...")
    try:
        response = requests.get("http://localhost:8002/scan/aisleepgen_v1.0.7", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"  [FOUND] Security scan result exists")
            print(f"    Security Score: {result.get('security_score', 'N/A')}/100")
            print(f"    Risk Level: {result.get('risk_level', 'N/A')}")
        elif response.status_code == 404:
            print("  [INFO] No security scan result yet - scan not started or in progress")
        else:
            print(f"  [ERROR] Unexpected status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not check security scan: {str(e)}")
    
    print()
    print("=" * 60)
    print("[SUMMARY] Current Status")
    print("=" * 60)
    print()
    
    # Determine overall status
    try:
        has_validator = requests.get("http://localhost:8001/validate/aisleepgen_v1.0.7", timeout=3).status_code == 200
        has_security = requests.get("http://localhost:8002/scan/aisleepgen_v1.0.7", timeout=3).status_code == 200
        
        if has_validator and has_security:
            print("Status: COMPLETE - Both validation and security scan finished")
        elif has_validator or has_security:
            print("Status: PARTIAL - One audit component finished")
        else:
            print("Status: PENDING - Audit not started or in progress")
    except:
        print("Status: UNKNOWN - Could not determine status")
    
    print()
    print("Next steps:")
    print("1. If audit not started, run: python start_audit.py")
    print("2. If services not running, start them as shown above")
    print("3. Check service logs for detailed progress")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()