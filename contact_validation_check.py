#!/usr/bin/env python3
"""
联系方式有效性检查工具
基于ClawHub审核要求
"""

import os
import re
import json
import sys

def validate_email(email):
    """验证邮箱格式"""
    if not email:
        return False, "Email is empty"
    
    # 基本邮箱格式验证
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, f"Invalid email format: {email}"
    
    # 检查常见问题
    if 'example.com' in email or 'test.com' in email:
        return False, "Example/test email not allowed"
    
    if 'placeholder' in email.lower():
        return False, "Placeholder email not allowed"
    
    return True, "Valid email"

def validate_github_url(url):
    """验证GitHub URL"""
    if not url:
        return False, "GitHub URL is empty"
    
    # GitHub URL模式
    github_patterns = [
        r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$',
        r'^https://github\.com/[a-zA-Z0-9_-]+$'
    ]
    
    for pattern in github_patterns:
        if re.match(pattern, url):
            return True, "Valid GitHub URL"
    
    return False, f"Invalid GitHub URL format: {url}"

def validate_author_info(author):
    """验证作者信息"""
    if not author:
        return False, "Author is empty"
    
    # 检查占位符
    placeholders = ['your name', 'author name', 'placeholder', 'example', 'test']
    for placeholder in placeholders:
        if placeholder in author.lower():
            return False, f"Placeholder author name: {author}"
    
    # 检查最小长度
    if len(author.strip()) < 2:
        return False, "Author name too short"
    
    return True, "Valid author"

def check_package_json(file_path):
    """检查package.json文件"""
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查作者
        if 'author' in data:
            author = data['author']
            if isinstance(author, dict):
                author_str = author.get('name', '')
                email = author.get('email', '')
                url = author.get('url', '')
            else:
                author_str = str(author)
                email = ''
                url = ''
            
            # 验证作者
            valid, message = validate_author_info(author_str)
            if not valid:
                results.append(f"author: {message}")
            
            # 验证邮箱
            if email:
                valid, message = validate_email(email)
                if not valid:
                    results.append(f"email: {message}")
            
            # 验证URL
            if url and 'github.com' in url:
                valid, message = validate_github_url(url)
                if not valid:
                    results.append(f"url: {message}")
        else:
            results.append("Missing author field")
        
        # 检查repository
        if 'repository' in data:
            repo = data['repository']
            if isinstance(repo, dict):
                repo_url = repo.get('url', '')
            else:
                repo_url = str(repo)
            
            if repo_url and 'github.com' in repo_url:
                valid, message = validate_github_url(repo_url)
                if not valid:
                    results.append(f"repository: {message}")
        
    except Exception as e:
        results.append(f"Error reading package.json: {e}")
    
    return results

def check_config_yaml(file_path):
    """检查config.yaml文件"""
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析YAML中的作者信息
        author_patterns = [
            r'author\s*:\s*["\']?([^"\'\n]+)["\']?',
            r'author\s*:\s*\n\s+name\s*:\s*["\']?([^"\'\n]+)["\']?'
        ]
        
        author_found = False
        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                author = match.group(1).strip()
                author_found = True
                valid, message = validate_author_info(author)
                if not valid:
                    results.append(f"author: {message}")
                break
        
        if not author_found:
            results.append("Missing author field in config.yaml")
        
        # 检查邮箱
        email_pattern = r'email\s*:\s*["\']?([^"\'\n]+@[^"\'\n]+\.[^"\'\n]+)["\']?'
        email_match = re.search(email_pattern, content, re.IGNORECASE)
        if email_match:
            email = email_match.group(1).strip()
            valid, message = validate_email(email)
            if not valid:
                results.append(f"email: {message}")
        
        # 检查GitHub URL
        github_pattern = r'(?:github|repository|url)\s*:\s*["\']?(https://github\.com/[^"\'\n]+)["\']?'
        github_match = re.search(github_pattern, content, re.IGNORECASE)
        if github_match:
            github_url = github_match.group(1).strip()
            valid, message = validate_github_url(github_url)
            if not valid:
                results.append(f"github url: {message}")
        
    except Exception as e:
        results.append(f"Error reading config.yaml: {e}")
    
    return results

def check_markdown_file(file_path):
    """检查Markdown文件中的联系方式"""
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
        
        # 检查常见联系方式模式
        patterns = [
            (r'email\s*[:=]\s*([^\s]+@[^\s]+\.[^\s]+)', 'email'),
            (r'contact\s*[:=]\s*([^\s]+@[^\s]+\.[^\s]+)', 'contact email'),
            (r'github\.com/[a-zA-Z0-9_-]+', 'github url'),
            (r'author\s*[:=]\s*([^\n]+)', 'author'),
        ]
        
        for pattern, field_type in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if field_type == 'email' or field_type == 'contact email':
                    valid, message = validate_email(match)
                    if not valid:
                        results.append(f"{field_type} in {os.path.basename(file_path)}: {message}")
                elif field_type == 'github url':
                    url = f"https://{match}" if not match.startswith('http') else match
                    valid, message = validate_github_url(url)
                    if not valid:
                        results.append(f"{field_type} in {os.path.basename(file_path)}: {message}")
        
    except Exception as e:
        results.append(f"Error reading {file_path}: {e}")
    
    return results

def check_skill_directory(directory_path):
    """检查技能目录中的联系方式"""
    
    print("=" * 80)
    print("Contact Information Validation Check")
    print("Based on ClawHub requirements")
    print("=" * 80)
    
    all_results = []
    
    # 检查package.json
    package_json = os.path.join(directory_path, "package.json")
    if os.path.exists(package_json):
        print(f"\nChecking package.json...")
        results = check_package_json(package_json)
        if results:
            print(f"  [FAIL] Issues found:")
            for result in results:
                print(f"    {result}")
                all_results.append(f"package.json: {result}")
        else:
            print(f"  [OK] No issues")
    else:
        print(f"\n[WARNING] package.json not found")
        all_results.append("Missing package.json")
    
    # 检查config.yaml
    config_yaml = os.path.join(directory_path, "config.yaml")
    if os.path.exists(config_yaml):
        print(f"\nChecking config.yaml...")
        results = check_config_yaml(config_yaml)
        if results:
            print(f"  [FAIL] Issues found:")
            for result in results:
                print(f"    {result}")
                all_results.append(f"config.yaml: {result}")
        else:
            print(f"  [OK] No issues")
    else:
        print(f"\n[WARNING] config.yaml not found")
        all_results.append("Missing config.yaml")
    
    # 检查Markdown文件
    md_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    print(f"\nChecking {len(md_files)} Markdown files...")
    for md_file in md_files:
        results = check_markdown_file(md_file)
        if results:
            filename = os.path.basename(md_file)
            print(f"  {filename}:")
            for result in results:
                print(f"    [ISSUE] {result}")
                all_results.append(f"{filename}: {result}")
    
    # 总体评估
    print(f"\n" + "=" * 80)
    print("Overall Assessment:")
    print("=" * 80)
    
    if not all_results:
        print("[SUCCESS] All contact information is valid")
        print("Author info: OK")
        print("Email format: OK")
        print("GitHub URLs: OK")
        print("Consistency: OK")
        return True
    else:
        print(f"[FAIL] Found {len(all_results)} contact information issues")
        
        print(f"\nIssues found:")
        for result in all_results:
            print(f"  - {result}")
        
        print(f"\nRecommendations:")
        print("1. Ensure author name is real (not placeholder)")
        print("2. Use valid email format (name@domain.com)")
        print("3. Use valid GitHub URLs (https://github.com/user/repo)")
        print("4. Keep contact info consistent across all files")
        print("5. Remove any example/placeholder contact info")
        
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python contact_validation_check.py <skill_directory>")
        print("Example: python contact_validation_check.py D:/openclaw/AISleepGen/openclaw_skill")
        return
    
    directory_path = sys.argv[1]
    
    if not os.path.exists(directory_path):
        print(f"[ERROR] Directory not found: {directory_path}")
        return
    
    success = check_skill_directory(directory_path)
    
    if success:
        print(f"\n[SUCCESS] Contact information validation passed")
        print("Ready for ClawHub submission")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Contact information validation failed")
        print("Fix issues before submitting to ClawHub")
        sys.exit(1)

if __name__ == "__main__":
    main()