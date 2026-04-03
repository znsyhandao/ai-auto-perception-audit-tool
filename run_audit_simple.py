"""
Run AISleepGen Audit - Simple Version
"""

import requests
import json
import time

print("AISleepGen Audit - Simple Version")
print("=" * 50)

# Check services first
print("Checking services...")
try:
    r = requests.get('http://localhost:8001/', timeout=5)
    print("Validator Service: RUNNING")
except:
    print("Validator Service: NOT RUNNING - Please start it first")
    print("Command: cd microservices\\validator-service && uvicorn main_fixed:app --host 0.0.0.0 --port 8001 --reload")
    exit(1)

try:
    r = requests.get('http://localhost:8002/', timeout=5)
    print("Security Service: RUNNING")
except:
    print("Security Service: NOT RUNNING - Please start it first")
    print("Command: cd microservices\\security-service && uvicorn main_fixed:app --host 0.0.0.0 --port 8002 --reload")
    exit(1)

print()
print("Starting audit...")

# Step 1: Run validator audit
print("[1] Running validator audit...")
validator_request = {
    'skill_id': 'aisleepgen_v1.0.7',
    'skill_path': 'D:/openclaw/releases/AISleepGen/v1.0.7_fixed',
    'validation_type': 'full'
}

try:
    response = requests.post('http://localhost:8001/validate', 
                           json=validator_request, 
                           timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print("Validator audit completed!")
        print(f"  Score: {result['score']}/100")
        print(f"  Passed: {result['passed']}")
        print(f"  Issues: {len(result.get('issues', []))}")
        print(f"  Warnings: {len(result.get('warnings', []))}")
        
        # Save result
        with open('validator_result_simple.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
    else:
        print(f"Validator audit failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"Validator error: {str(e)}")

print()
print("[2] Running security scan...")
time.sleep(2)

# Step 2: Run security scan
security_request = {
    'skill_id': 'aisleepgen_v1.0.7',
    'skill_path': 'D:/openclaw/releases/AISleepGen/v1.0.7_fixed',
    'scan_depth': 'standard'
}

try:
    response = requests.post('http://localhost:8002/scan',
                           json=security_request,
                           timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print("Security scan completed!")
        print(f"  Security Score: {result['security_score']}/100")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Threats: {len(result.get('threats', []))}")
        
        # Save result
        with open('security_result_simple.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
    else:
        print(f"Security scan failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"Security scan error: {str(e)}")

print()
print("=" * 50)
print("Audit completed!")
print("Results saved to:")
print("  validator_result_simple.json")
print("  security_result_simple.json")
print()
print("View results with:")
print("  curl http://localhost:8001/validate/aisleepgen_v1.0.7")
print("  curl http://localhost:8002/scan/aisleepgen_v1.0.7")
print("=" * 50)