"""
检查AISleepGen数学审核结果
"""

import json

def check_results():
    """检查结果"""
    print("AISLEEPGEN MATHEMATICAL AUDIT RESULTS")
    print("=" * 70)
    
    with open('aisleepgen_mathematical_audit_20260331_084657.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n1. Overall Results:")
    print(f"   Overall Score: {data['results']['overall_mathematical_score']}/100")
    print(f"   Certificates: {len(data['results'].get('mathematical_certificates', []))}")
    print(f"   Audit Time: {data['audit']['time_seconds']:.2f}s")
    
    print(f"\n2. Release Decision:")
    if data['summary']['release_ready']:
        print("   RECOMMENDED FOR RELEASE")
        print("   Mathematical score meets release criteria (≥70)")
    else:
        print("   NOT READY FOR RELEASE")
        print("   Mathematical score below release criteria (<70)")
    
    print(f"\n3. Summary Metrics:")
    print(f"   Release Ready: {data['summary']['release_ready']}")
    print(f"   Certificate Count: {data['summary']['certificate_count']}")
    print(f"   Audit Time: {data['summary']['audit_time']:.2f}s")
    
    print(f"\n4. Certificate Details:")
    certificates = data['results'].get('mathematical_certificates', [])
    for i, cert in enumerate(certificates, 1):
        theorem = cert.get('theorem', 'Unknown')
        confidence = cert.get('confidence', 0)
        validity = cert.get('validity', 'unknown')
        
        print(f"   {i}. {theorem}")
        print(f"      Confidence: {confidence:.3f}")
        print(f"      Validity: {validity}")
    
    print(f"\n" + "=" * 70)
    if data['summary']['release_ready']:
        print("CONCLUSION: AISleepGen v1.0.7_fixed is READY FOR RELEASE")
        print("Mathematical audit passed with score: {}/100".format(data['results']['overall_mathematical_score']))
    else:
        print("CONCLUSION: AISleepGen v1.0.7_fixed NEEDS IMPROVEMENT")
        print("Mathematical audit score: {}/100 (needs ≥70)".format(data['results']['overall_mathematical_score']))
    
    print("=" * 70)
    return data['summary']['release_ready']

if __name__ == "__main__":
    ready = check_results()
    exit(0 if ready else 1)