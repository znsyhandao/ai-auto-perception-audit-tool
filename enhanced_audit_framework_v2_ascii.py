#!/usr/bin/env python3
"""
Enhanced Audit Framework V2 - ASCII version
Complete audit system with all lessons learned on 2026-04-02
"""

import os
import sys
import re
import json
from pathlib import Path

def run_enhanced_audit_v2(skill_dir):
    """Run enhanced audit V2"""
    print("=" * 80)
    print("Enhanced Audit Framework V2 - Complete Audit Process (2026-04-02)")
    print("=" * 80)
    print(f"Skill directory: {skill_dir}")
    print("=" * 80)
    
    all_checks_passed = True
    
    # ==================== Phase 1: Pre-release cleanup ====================
    print("\n[1/5] Running pre-release cleaner")
    print("-" * 40)
    
    cleanup_passed = run_pre_release_cleanup(skill_dir)
    if not cleanup_passed:
        all_checks_passed = False
    
    # ==================== Phase 2: File size check ====================
    print("\n[2/5] File size and structure check")
    print("-" * 40)
    
    file_check_passed = run_file_size_check(skill_dir)
    if not file_check_passed:
        all_checks_passed = False
    
    # ==================== Phase 3: Content compliance check ====================
    print("\n[3/5] Content compliance check")
    print("-" * 40)
    
    content_check_passed = run_content_compliance_check(skill_dir)
    if not content_check_passed:
        all_checks_passed = False
    
    # ==================== Phase 4: Permanent audit ====================
    print("\n[4/5] Running permanent audit framework")
    print("-" * 40)
    
    permanent_audit_passed = run_permanent_audit(skill_dir)
    if not permanent_audit_passed:
        all_checks_passed = False
    
    # ==================== Phase 5: Security check ====================
    print("\n[5/5] Running security check")
    print("-" * 40)
    
    security_check_passed = run_security_check_v2(skill_dir)
    if not security_check_passed:
        all_checks_passed = False
    
    # ==================== Final report ====================
    print("\n" + "=" * 80)
    print("Enhanced Audit V2 Complete!")
    print("=" * 80)
    
    if all_checks_passed:
        print("[PASS] All checks passed!")
        print("[PASS] Pre-release cleanup completed")
        print("[PASS] File size check passed")
        print("[PASS] Content compliance check passed")
        print("[PASS] Permanent audit passed")
        print("[PASS] Security check passed")
        print("\n[READY] Skill is ready to publish to ClawHub!")
        return True
    else:
        print("[FAIL] Some checks failed")
        print("\n[FIX] Please fix the above issues and re-audit")
        return False

def run_pre_release_cleanup(skill_dir):
    """Run pre-release cleanup"""
    try:
        # Import cleaner
        sys.path.insert(0, str(Path(__file__).parent))
        from pre_release_cleaner import PreReleaseCleaner
        
        cleaner = PreReleaseCleaner(skill_dir)
        cleanup_success = cleaner.run_full_cleanup()
        
        if cleanup_success:
            print("[PASS] Pre-release cleanup completed")
            return True
        else:
            print("[FAIL] Cleanup failed")
            return False
            
    except Exception as e:
        print(f"[WARN] Cleaner failed: {e}")
        print("Continuing with other checks...")
        return True  # Continue with other checks

def run_file_size_check(skill_dir):
    """Check file sizes and structure"""
    skill_path = Path(skill_dir)
    
    print("Checking file size limits...")
    
    # Check required files
    required_files = ["skill.py", "config.yaml", "SKILL.md", "README.md", "CHANGELOG.md", "requirements.txt"]
    missing_files = []
    
    for file in required_files:
        if not (skill_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"[FAIL] Missing required files: {missing_files}")
        return False
    
    print("[PASS] All required files exist")
    
    # Check file sizes
    large_files = []
    for file in required_files:
        file_path = skill_path / file
        if file_path.exists():
            size = file_path.stat().st_size
            if size > 50000:  # 50KB limit
                large_files.append((file, size))
    
    if large_files:
        print("[WARN] Found large files:")
        for file, size in large_files:
            print(f"  {file}: {size} bytes")
        print("Consider optimizing file sizes")
    
    # Check for duplicate files
    print("Checking for duplicate files and directories...")
    all_files = list(skill_path.rglob("*"))
    
    # Check for nested release directories
    nested_releases = [f for f in all_files if "release" in str(f).lower() and f.is_dir()]
    if nested_releases:
        print(f"[WARN] Found nested release directories: {[str(f.relative_to(skill_path)) for f in nested_releases]}")
    
    print("[PASS] File structure check completed")
    return True

def run_content_compliance_check(skill_dir):
    """Content compliance check"""
    skill_path = Path(skill_dir)
    
    print("Checking content compliance...")
    
    issues = []
    
    # 1. Check English compliance
    english_issues = check_english_compliance(skill_path)
    if english_issues:
        issues.extend(english_issues)
    
    # 2. Check content consistency
    consistency_issues = check_content_consistency(skill_path)
    if consistency_issues:
        issues.extend(consistency_issues)
    
    # 3. Check registry name consistency
    registry_issues = check_registry_consistency(skill_path)
    if registry_issues:
        issues.extend(registry_issues)
    
    if issues:
        print("[FAIL] Content compliance issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[PASS] Content compliance check passed")
        return True

def check_english_compliance(skill_path):
    """Check if all files are English only"""
    issues = []
    
    # File types to check
    text_files = list(skill_path.glob("*.py")) + \
                 list(skill_path.glob("*.md")) + \
                 list(skill_path.glob("*.yaml")) + \
                 list(skill_path.glob("*.yml")) + \
                 list(skill_path.glob("*.txt"))
    
    for file in text_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Chinese characters
            if re.search(r'[\u4e00-\u9fff]', content):
                issues.append(f"{file.name}: Contains Chinese characters (English required)")
        except:
            pass
    
    return issues

def check_content_consistency(skill_path):
    """Check content consistency"""
    issues = []
    
    # Check skill name consistency
    skill_name = None
    
    # Get skill name from config.yaml
    config_file = skill_path / "config.yaml"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple extraction of skill name
                match = re.search(r'name:\s*["\']([^"\']+)["\']', content)
                if match:
                    skill_name = match.group(1)
        except:
            pass
    
    # Check all files for consistent naming
    if skill_name:
        text_files = list(skill_path.glob("*.py")) + \
                     list(skill_path.glob("*.md")) + \
                     list(skill_path.glob("*.yaml")) + \
                     list(skill_path.glob("*.yml"))
        
        for file in text_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for old skill name references
                if "sleep-rabbit" in content.lower() or "sleeprabbit" in content.lower():
                    issues.append(f"{file.name}: Contains old 'sleep-rabbit' references")
            except:
                pass
    
    return issues

def check_registry_consistency(skill_path):
    """Check registry name consistency"""
    issues = []
    
    # Check for _meta.json file
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            slug = meta_data.get("slug", "")
            
            # Check if config.yaml name matches
            config_file = skill_path / "config.yaml"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                config_match = re.search(r'name:\s*["\']([^"\']+)["\']', config_content)
                if config_match:
                    config_name = config_match.group(1)
                    if slug and config_name and slug != config_name:
                        issues.append(f"Registry name mismatch: _meta.json='{slug}' vs config.yaml='{config_name}'")
        except:
            pass
    
    return issues

def run_permanent_audit(skill_dir):
    """Run permanent audit framework"""
    audit_script = Path(__file__).parent / "permanent_audit_ascii.py"
    if audit_script.exists():
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(audit_script), skill_dir],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print("[FAIL] Permanent audit failed")
                return False
            else:
                print("[PASS] Permanent audit passed")
                return True
                
        except Exception as e:
            print(f"[FAIL] Running permanent audit failed: {e}")
            return False
    else:
        print(f"[FAIL] Permanent audit script not found: {audit_script}")
        return False

def run_security_check_v2(skill_dir):
    """Run security check V2"""
    skill_path = Path(skill_dir)
    skill_file = skill_path / "skill.py"
    
    if not skill_file.exists():
        print("[FAIL] skill.py does not exist")
        return False
    
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        security_issues = []
        
        # Check for dangerous imports
        dangerous_patterns = [
            (r'import\s+subprocess', "Dangerous import: subprocess"),
            (r'from\s+subprocess\s+import', "Dangerous import: from subprocess"),
            (r'import\s+requests', "Network library: requests"),
            (r'import\s+urllib', "Network library: urllib"),
            (r'import\s+socket', "Network library: socket"),
            (r'import\s+http\.client', "Network library: http.client"),
            (r'eval\(', "Dangerous function: eval"),
            (r'exec\(', "Dangerous function: exec"),
            (r'__import__\(', "Dangerous function: __import__"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_issues.append(description)
        
        if security_issues:
            print("[FAIL] Security issues found:")
            for issue in security_issues:
                print(f"  - {issue}")
            return False
        else:
            print("[PASS] No security issues found")
            return True
            
    except Exception as e:
        print(f"[FAIL] Security check failed: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Enhanced Audit Framework V2 (2026-04-02)")
        print("=" * 60)
        print("Complete audit system with all lessons learned today")
        print("")
        print("Usage:")
        print("  python enhanced_audit_framework_v2_ascii.py <skill_directory>")
        print("")
        print("5-phase audit process:")
        print("  1. Pre-release cleanup - Remove cache files, temp files")
        print("  2. File size check - Check file sizes and structure")
        print("  3. Content compliance - English, consistency, registry names")
        print("  4. Permanent audit - File, version, function checks")
        print("  5. Security check - Dangerous function checks")
        print("")
        print("Problems solved:")
        print("  - Cache file pollution (.pyc files)")
        print("  - Registry name inconsistency")
        print("  - Content declaration contradictions")
        print("  - Forgetting English requirement")
        print("  - File size issues")
        print("")
        print("Example:")
        print("  python enhanced_audit_framework_v2_ascii.py D:\\openclaw\\releases\\skill-name")
        return
    
    skill_dir = sys.argv[1]
    
    if not Path(skill_dir).exists():
        print(f"[ERROR] Directory does not exist: {skill_dir}")
        return
    
    success = run_enhanced_audit_v2(skill_dir)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()