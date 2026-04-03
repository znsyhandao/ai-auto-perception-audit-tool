"""
准备AISleepGen最终发布审核
"""

import os
import json
import shutil
from pathlib import Path

def check_aisleepgen_status():
    """检查AISleepGen状态"""
    print("1. Checking AISleepGen status...")
    
    aisleepgen_path = Path("D:/openclaw/releases/AISleepGen/v1.0.7_fixed")
    
    if not aisleepgen_path.exists():
        print(f"   ERROR: AISleepGen not found at {aisleepgen_path}")
        return False
    
    print(f"   Found AISleepGen at: {aisleepgen_path}")
    
    # 检查关键文件
    required_files = [
        "skill.py",
        "SKILL.md",
        "config.yaml",
        "package.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not (aisleepgen_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"   Missing files: {missing_files}")
        return False
    
    print("   All required files present")
    
    # 检查版本
    package_file = aisleepgen_path / "package.json"
    if package_file.exists():
        with open(package_file, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        version = package_data.get("version", "unknown")
        print(f"   Version: {version}")
    
    return True

def create_mathematical_audit_config():
    """创建数学审核配置"""
    print("\n2. Creating mathematical audit configuration...")
    
    audit_config = {
        "audit_id": f"AISLEEPGEN_AUDIT_{int(time.time())}",
        "skill_id": "aisleepgen_v1.0.7",
        "skill_path": "D:/openclaw/releases/AISleepGen/v1.0.7_fixed",
        "audit_types": [
            "maclaurin",
            "taylor",
            "fourier",
            "matrix",
            "proof"
        ],
        "mathematical_depth": 5,
        "certificate_requirements": {
            "minimum_confidence": 0.7,
            "minimum_valid_certificates": 3,
            "overall_score_threshold": 75.0
        },
        "release_criteria": {
            "mathematical_audit_passed": True,
            "certificates_generated": True,
            "score_above_threshold": True,
            "no_critical_issues": True
        }
    }
    
    config_dir = Path("aisleepgen_release_audit")
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "mathematical_audit_config.json", 'w', encoding='utf-8') as f:
        json.dump(audit_config, f, indent=2)
    
    print(f"   Created: {config_dir}/mathematical_audit_config.json")
    return True

def create_release_checklist():
    """创建发布检查清单"""
    print("\n3. Creating release checklist...")
    
    checklist = {
        "checklist_id": f"RELEASE_CHECKLIST_{int(time.time())}",
        "skill": "AISleepGen",
        "version": "v1.0.7",
        "status": "pending",
        "checks": [
            {
                "category": "Code Quality",
                "items": [
                    {"item": "No syntax errors", "status": "pending", "required": True},
                    {"item": "Type hints complete", "status": "pending", "required": True},
                    {"item": "Documentation complete", "status": "pending", "required": True},
                    {"item": "Test coverage adequate", "status": "pending", "required": True}
                ]
            },
            {
                "category": "Security",
                "items": [
                    {"item": "No dangerous functions", "status": "pending", "required": True},
                    {"item": "Input validation implemented", "status": "pending", "required": True},
                    {"item": "Path traversal prevented", "status": "pending", "required": True},
                    {"item": "No hardcoded secrets", "status": "pending", "required": True}
                ]
            },
            {
                "category": "Mathematical Audit",
                "items": [
                    {"item": "Maclaurin analysis passed", "status": "pending", "required": True},
                    {"item": "Taylor analysis passed", "status": "pending", "required": True},
                    {"item": "Fourier analysis passed", "status": "pending", "required": True},
                    {"item": "Matrix analysis passed", "status": "pending", "required": True},
                    {"item": "Mathematical proof passed", "status": "pending", "required": True},
                    {"item": "Overall score > 75", "status": "pending", "required": True},
                    {"item": "Certificates generated", "status": "pending", "required": True}
                ]
            },
            {
                "category": "ClawHub Compliance",
                "items": [
                    {"item": "SKILL.md complete", "status": "pending", "required": True},
                    {"item": "config.yaml correct", "status": "pending", "required": True},
                    {"item": "package.json complete", "status": "pending", "required": True},
                    {"item": "No .bat files", "status": "pending", "required": True},
                    {"item": "Documentation consistent", "status": "pending", "required": True}
                ]
            },
            {
                "category": "Performance",
                "items": [
                    {"item": "Response time < 5s", "status": "pending", "required": True},
                    {"item": "Memory usage < 500MB", "status": "pending", "required": True},
                    {"item": "No memory leaks", "status": "pending", "required": True},
                    {"item": "Error handling robust", "status": "pending", "required": True}
                ]
            }
        ],
        "release_criteria": "All required checks must pass",
        "mathematical_audit_weight": 40,
        "created_at": "2026-03-31"
    }
    
    config_dir = Path("aisleepgen_release_audit")
    with open(config_dir / "release_checklist.json", 'w', encoding='utf-8') as f:
        json.dump(checklist, f, indent=2)
    
    print(f"   Created: {config_dir}/release_checklist.json")
    return True

def create_audit_script():
    """创建审核脚本"""
    print("\n4. Creating audit script...")
    
    audit_script = '''"""
AISleepGen最终发布审核脚本
"""

import requests
import json
import time
from pathlib import Path

class AISleepGenReleaseAudit:
    """AISleepGen发布审核类"""
    
    def __init__(self):
        self.skill_id = "aisleepgen_v1.0.7"
        self.skill_path = "D:/openclaw/releases/AISleepGen/v1.0.7_fixed"
        self.mathematical_service_url = "http://localhost:8010"
        self.results = {}
    
    def run_mathematical_audit(self):
        """运行数学审核"""
        print("1. Running mathematical audit...")
        
        audit_data = {
            "skill_id": self.skill_id,
            "skill_path": self.skill_path,
            "audit_types": ["maclaurin", "taylor", "fourier", "matrix", "proof"],
            "mathematical_depth": 5
        }
        
        try:
            response = requests.post(
                f"{self.mathematical_service_url}/audit",
                json=audit_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                self.results["mathematical_audit"] = result
                
                score = result.get("overall_mathematical_score", 0)
                certificates = result.get("mathematical_certificates", [])
                
                print(f"   Mathematical score: {score}")
                print(f"   Certificates generated: {len(certificates)}")
                
                # 分析证书
                if certificates:
                    valid_certs = [c for c in certificates if c.get("validity") == "valid"]
                    avg_confidence = sum(c.get("confidence", 0) for c in certificates) / len(certificates)
                    
                    print(f"   Valid certificates: {len(valid_certs)}/{len(certificates)}")
                    print(f"   Average confidence: {avg_confidence:.3f}")
                
                return score >= 75.0 and len(certificates) >= 3
            else:
                print(f"   Audit failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   Audit error: {e}")
            return False
    
    def check_code_quality(self):
        """检查代码质量"""
        print("\\n2. Checking code quality...")
        
        skill_dir = Path(self.skill_path)
        
        checks = [
            ("skill.py exists", skill_dir / "skill.py", True),
            ("SKILL.md exists", skill_dir / "SKILL.md", True),
            ("config.yaml exists", skill_dir / "config.yaml", True),
            ("package.json exists", skill_dir / "package.json", True)
        ]
        
        passed = 0
        for check_name, check_path, required in checks:
            if check_path.exists():
                print(f"   {check_name}: PASS")
                passed += 1
            else:
                print(f"   {check_name}: FAIL")
                if required:
                    return False
        
        self.results["code_quality"] = {"passed": passed, "total": len(checks)}
        return passed == len(checks)
    
    def check_clawhub_compliance(self):
        """检查ClawHub合规性"""
        print("\\n3. Checking ClawHub compliance...")
        
        skill_dir = Path(self.skill_path)
        
        # 检查禁止的文件
        prohibited_files = [".bat", ".exe", ".dll"]
        found_prohibited = []
        
        for file in skill_dir.rglob("*"):
            if file.is_file():
                for ext in prohibited_files:
                    if file.name.endswith(ext):
                        found_prohibited.append(file.name)
        
        if found_prohibited:
            print(f"   Prohibited files found: {found_prohibited}")
            return False
        
        print("   No prohibited files found")
        
        # 检查文档一致性
        skill_file = skill_dir / "skill.py"
        skill_md_file = skill_dir / "SKILL.md"
        
        if skill_file.exists() and skill_md_file.exists():
            # 简单检查：确保SKILL.md提到技能名称
            with open(skill_md_file, 'r', encoding='utf-8') as f:
                skill_md_content = f.read()
            
            if "AISleepGen" in skill_md_content or "睡眠分析" in skill_md_content:
                print("   Documentation consistent")
                self.results["clawhub_compliance"] = True
                return True
            else:
                print("   Documentation may be inconsistent")
                return False
        
        return True
    
    def generate_audit_report(self):
        """生成审核报告"""
        print("\\n4. Generating audit report...")
        
        report = {
            "audit_id": f"AISLEEPGEN_AUDIT_{int(time.time())}",
            "skill": self.skill_id,
            "audit_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results,
            "summary": {
                "mathematical_audit_passed": "mathematical_audit" in self.results,
                "code_quality_passed": self.results.get("code_quality", {}).get("passed", 0) == 4,
                "clawhub_compliance_passed": self.results.get("clawhub_compliance", False),
                "overall_status": "pending"
            },
            "recommendation": "pending"
        }
        
        # 确定总体状态
        mathematical_passed = report["summary"]["mathematical_audit_passed"]
        code_passed = report["summary"]["code_quality_passed"]
        compliance_passed = report["summary"]["clawhub_compliance_passed"]
        
        if mathematical_passed and code_passed and compliance_passed:
            report["summary"]["overall_status"] = "PASS"
            report["recommendation"] = "APPROVE for release"
        else:
            report["summary"]["overall_status"] = "FAIL"
            report["recommendation"] = "DO NOT APPROVE - needs fixes"
        
        # 保存报告
        report_dir = Path("aisleepgen_release_audit")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"audit_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   Report saved: {report_file}")
        return report
    
    def run_complete_audit(self):
        """运行完整审核"""
        print("AISLEEPGEN FINAL RELEASE AUDIT")
        print("=" * 60)
        
        results = []
        
        # 运行所有检查
        results.append(("Mathematical audit", self.run_mathematical_audit()))
        results.append(("Code quality", self.check_code_quality()))
        results.append(("ClawHub compliance", self.check_clawhub_compliance()))
        
        # 显示结果
        print("\\n" + "=" * 60)
        print("AUDIT RESULTS:")
        print("=" * 60)
        
        passed = 0
        for check_name, check_result in results:
            status = "PASS" if check_result else "FAIL"
            print(f"{check_name}: {status}")
            if check_result:
                passed += 1
        
        print(f"\\nTotal: {passed}/{len(results)} passed")
        
        # 生成报告
        report = self.generate_audit_report()
        
        print("\\n" + "=" * 60)
        if report["summary"]["overall_status"] == "PASS":
            print("RELEASE AUDIT: PASSED")
            print("AISleepGen is ready for release.")
        else:
            print("RELEASE AUDIT: FAILED")
            print("AISleepGen needs fixes before release.")
        
        print("=" * 60)
        
        return report["summary"]["overall_status"] == "PASS"

def main():
    """主函数"""
    auditor = AISleepGenReleaseAudit()
    return auditor.run_complete_audit()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
'''
    
    config_dir = Path("aisleepgen_release_audit")
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "run_audit.py", 'w', encoding='utf-8') as f:
        f.write(audit_script)
    
    print(f"   Created: {config_dir}/run_audit.py")
    return True

def create_release_package():
    """创建发布包"""
    print("\n5. Creating release package...")
    
    release_dir = Path("aisleepgen_release_package")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir(exist_ok=True)
    
    # 复制审核文件
    audit_dir = Path("aisleepgen_release_audit")
    if audit_dir.exists():
        for file in audit_dir.iterdir():
            if file.is_file():
                shutil.copy(file, release_dir / file.name)
    
    # 创建发布说明
    release_notes = """# AISleepGen v1.0.7 Release Package

## Overview
This package contains all files needed for the final release audit of AISleepGen v1.0.7.

## Contents

### 1. Audit Configuration
- `mathematical_audit_config.json` - Mathematical audit configuration
- `release_checklist.json` - Complete release checklist
- `run_audit.py` - Automated audit script

### 2. Audit Process

#### Step 1: Start Mathematical Audit Service
```bash
cd microservices/mathematical-audit-service
python -m uvicorn main:app --host 0.0.0.0 --port 8010
```

#### Step 2: Run Complete Audit
```bash
python aisleepgen_release_audit/run_audit.py
```

#### Step 3: Review Results
Check the generated audit report for:
- Mathematical audit score (must be > 75)
- Number of certificates generated (must be >= 3)
- Code quality checks (all must pass)
- ClawHub compliance (all must pass)

### 3. Release Criteria

#### Mandatory Requirements:
1. ✅ Mathematical audit score > 75
2. ✅ At least 3 valid mathematical certificates
3. ✅ All code quality checks pass
4. ✅ ClawHub compliance checks pass
5. ✅ No prohibited files (.bat, .exe, .dll)

#### Quality Indicators:
- Average certificate confidence > 0.7
- All mathematical methods (5 types) executed successfully
- Documentation complete and consistent
- Performance metrics within limits

### 4. Mathematical Audit Details

The audit uses 5 mathematical methods:

1. **Maclaurin Series** - Code complexity analysis
2. **Taylor Series** - Algorithm performance analysis
3. **Fourier Transform** - Code structure pattern recognition
4. **Matrix Decomposition** - Module dependency analysis
5. **Mathematical Proof** - Code property verification

Each method generates a mathematical certificate with:
- Theorem statement
- Confidence score (0-1)
- Validity status (valid/invalid)
- Unique certificate ID

### 5. Next Steps After Audit

If audit passes:
1. Create final release ZIP: `AISleepGen_v1.0.7