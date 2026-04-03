"""
Re-audit AISleepGen after fixes
"""

import requests
import json
import time

print("AISleepGen Re-Audit After Fixes")
print("=" * 50)

# Check services
print("Checking services...")
try:
    r = requests.get('http://localhost:8001/', timeout=5)
    print("Validator Service: RUNNING")
except:
    print("Validator Service: NOT RUNNING")
    exit(1)

try:
    r = requests.get('http://localhost:8002/', timeout=5)
    print("Security Service: RUNNING")
except:
    print("Security Service: NOT RUNNING")
    exit(1)

print()
print("Running re-audit...")

# Run validator audit
print("[1] Validator audit...")
validator_request = {
    'skill_id': 'aisleepgen_v1.0.7_fixed',
    'skill_path': 'D:/openclaw/releases/AISleepGen/v1.0.7_fixed',
    'validation_type': 'full'
}

try:
    response = requests.post('http://localhost:8001/validate', 
                           json=validator_request, 
                           timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Score: {result['score']}/100")
        print(f"Passed: {result['passed']}")
        print(f"Issues: {len(result.get('issues', []))}")
        
        with open('validator_result_fixed.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print(f"Failed: {response.status_code}")
        
except Exception as e:
    print(f"Error: {str(e)}")

print()
print("[2] Security scan...")
time.sleep(2)

# Run security scan
security_request = {
    'skill_id': 'aisleepgen_v1.0.7_fixed',
    'skill_path': 'D:/openclaw/releases/AISleepGen/v1.0.7_fixed',
    'scan_depth': 'standard'
}

try:
    response = requests.post('http://localhost:8002/scan',
                           json=security_request,
                           timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Security Score: {result['security_score']}/100")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Threats: {len(result.get('threats', []))}")
        
        with open('security_result_fixed.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print(f"Failed: {response.status_code}")
        
except Exception as e:
    print(f"Error: {str(e)}")

print()
print("=" * 50)
print("Re-audit completed!")
print("Check validator_result_fixed.json and security_result_fixed.json")