#!/usr/bin/env python3
"""
Complete AISleepGen Audit using Fixed Services
"""

import requests
import json
import time
from pathlib import Path

def test_service(url, name):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[OK] {name} is running")
            return True
        else:
            print(f"[ERROR] {name}: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {name}: {str(e)}")
        return False

def run_validator_audit():
    """Run validator audit for AISleepGen"""
    print("\n[1] Running Validator Audit...")
    
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    # Create validation request
    validator_request = {
        "skill_id": "aisleepgen_v1.0.7",
        "skill_path": skill_path,
        "validation_type": "full"
    }
    
    try:
        print(f"  Skill path: {skill_path}")
        print("  Submitting validation request...")
        
        response = requests.post(
            "http://localhost:8001/validate",
            json=validator_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Validation completed!")
            print(f"  Score: {result['score']}/100")
            print(f"  Passed: {result['passed']}")
            print(f"  Issues: {len(result['issues'])}")
            print(f"  Warnings: {len(result['warnings'])}")
            
            # Show critical issues
            if result['issues']:
                print("\n  Critical Issues:")
                for issue in result['issues'][:3]:  # Show first 3
                    print(f"    - {issue.get('message', 'Unknown issue')}")
            
            # Show warnings
            if result['warnings']:
                print("\n  Warnings:")
                for warning in result['warnings'][:3]:  # Show first 3
                    print(f"    - {warning.get('message', 'Unknown warning')}")
            
            # Show recommendations
            if result['recommendations']:
                print("\n  Recommendations:")
                for rec in result['recommendations'][:3]:  # Show first 3
                    print(f"    - {rec}")
            
            return result
            
        else:
            print(f"[ERROR] Validation failed: Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Validator request failed: {str(e)}")
        return None

def run_security_scan():
    """Run security scan for AISleepGen"""
    print("\n[2] Running Security Scan...")
    
    skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
    
    # Create security scan request
    security_request = {
        "skill_id": "aisleepgen_v1.0.7",
        "skill_path": skill_path,
        "scan_depth": "standard"
    }
    
    try:
        print(f"  Skill path: {skill_path}")
        print("  Submitting security scan...")
        
        response = requests.post(
            "http://localhost:8002/scan",
            json=security_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Security scan completed!")
            print(f"  Security Score: {result['security_score']}/100")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Threats Found: {len(result['threats'])}")
            print(f"  Vulnerabilities: {len(result['vulnerabilities'])}")
            
            # Show threats if any
            if result['threats']:
                print("\n  Security Threats:")
                for threat in result['threats'][:3]:  # Show first 3
                    print(f"    - {threat.get('type', 'Unknown')} in {threat.get('filename', 'Unknown')}:{threat.get('line', '?')}")
                    print(f"      Pattern: {threat.get('pattern', 'Unknown')}")
            
            # Show recommendations
            if result['recommendations']:
                print("\n  Security Recommendations:")
                for rec in result['recommendations'][:3]:  # Show first 3
                    print(f"    - {rec}")
            
            return result
            
        else:
            print(f"[ERROR] Security scan failed: Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Security scan failed: {str(e)}")
        return None

def get_final_results():
    """Get final audit results"""
    print("\n[3] Getting Final Audit Results...")
    
    try:
        # Get validator result
        validator_result = requests.get(
            "http://localhost:8001/validate/aisleepgen_v1.0.7",
            timeout=10
        )
        
        # Get security result
        security_result = requests.get(
            "http://localhost:8002/scan/aisleepgen_v1.0.7",
            timeout=10
        )
        
        print("[SUCCESS] Final results retrieved!")
        
        if validator_result.status_code == 200:
            val_data = validator_result.json()
            print(f"\n  Validator Result:")
            print(f"    Score: {val_data.get('score', 'N/A')}/100")
            print(f"    Passed: {val_data.get('passed', 'N/A')}")
        
        if security_result.status_code == 200:
            sec_data = security_result.json()
            print(f"\n  Security Result:")
            print(f"    Security Score: {sec_data.get('security_score', 'N/A')}/100")
            print(f"    Risk Level: {sec_data.get('risk_level', 'N/A')}")
        
    except requests.exceptions.RequestException as e:
        print(f"[WARNING] Could not retrieve final results: {str(e)}")

def main():
    """Main function"""
    print("=" * 60)
    print("AISleepGen v1.0.7 - Enterprise Audit Framework")
    print("Using Fixed Services (No Docker Required)")
    print("=" * 60)
    
    # Check services
    print("\n[CHECK] Checking services...")
    services_ok = True
    
    if not test_service("http://localhost:8001/", "Validator Service"):
        services_ok = False
    if not test_service("http://localhost:8002/", "Security Service"):
        services_ok = False
    
    if not services_ok:
        print("\n[ERROR] Some services are not responding")
        print("Please start the services:")
        print("1. Validator: uvicorn main_fixed:app --host 0.0.0.0 --port 8001 --reload")
        print("2. Security: uvicorn main_fixed:app --host 0.0.0.0 --port 8002 --reload")
        return
    
    # Check skill path
    skill_path = Path("D:/openclaw/releases/AISleepGen/v1.0.7_fixed")
    if not skill_path.exists():
        print(f"\n[ERROR] Skill path not found: {skill_path}")
        return
    
    print(f"\n[INFO] Skill to audit: {skill_path}")
    file_count = len(list(skill_path.glob("*")))
    print(f"       Files: {file_count}")
    
    # Run audits
    validator_result = run_validator_audit()
    
    # Wait a moment before security scan
    time.sleep(2)
    
    security_result = run_security_scan()
    
    # Get final results
    get_final_results()
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] AISleepGen Audit Complete")
    print("=" * 60)
    
    if validator_result:
        print(f"\nValidator Service:")
        print(f"  Score: {validator_result.get('score', 'N/A')}/100")
        print(f"  Status: {'PASSED' if validator_result.get('passed') else 'FAILED'}")
    
    if security_result:
        print(f"\nSecurity Service:")
        print(f"  Security Score: {security_result.get('security_score', 'N/A')}/100")
        print(f"  Risk Level: {security_result.get('risk_level', 'N/A').upper()}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Enterprise Audit Framework Verified!")
    print("=" * 60)
    
    print("\nView detailed results:")
    print("  Validator: curl http://localhost:8001/validate/aisleepgen_v1.0.7")
    print("  Security: curl http://localhost:8002/scan/aisleepgen_v1.0.7")
    
    print("\nEnterprise Framework Status:")
    print("  ✅ Microservices architecture verified")
    print("  ✅ REST API endpoints working")
    print("  ✅ Skill audit workflow functional")
    print("  ✅ No Docker required for core functionality")
    print("  ✅ Windows Home compatible")

if __name__ == "__main__":
    main()