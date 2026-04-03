# 🧪 OpenClaw技能测试与安全框架

## 🎯 核心原则

### 1. 安全第一，功能第二
- **发布前必须通过安全扫描**
- **安全声明必须代码支持**
- **权限必须最小化**

### 2. 测试全面，审查深入
- **功能测试**：确保所有命令工作
- **安全测试**：确保无网络、无危险代码
- **一致性测试**：确保文档与代码一致
- **合规测试**：确保符合平台规范

### 3. 流程标准化，检查自动化
- **标准化发布流程**
- **自动化安全检查**
- **系统化代码审查**

## 📋 发布前必做检查清单

### 阶段1：代码开发完成
- [ ] **功能测试**：所有命令正常工作
- [ ] **导入测试**：所有模块能正确导入
- [ ] **错误处理**：有完整的错误处理机制

### 阶段2：安全审查（发布前必须完成）
- [ ] **网络代码检查**：无requests、urllib、socket等
- [ ] **危险函数检查**：无subprocess、eval、exec等
- [ ] **路径安全检查**：无路径遍历，访问受限制
- [ ] **依赖检查**：仅Python标准库，无外部依赖
- [ ] **权限检查**：package.json权限最小化

### 阶段3：一致性验证
- [ ] **文档代码一致**：README声明与代码实现一致
- [ ] **安全声明验证**：所有安全声明有代码支持
- [ ] **功能声明验证**：所有功能都有实现

### 阶段4：最终验证
- [ ] **ClawHub规范**：符合平台要求
- [ ] **许可证合规**：正确设置许可证
- [ ] **文件结构**：符合技能结构要求

## 🚨 从AISkinX经验中学到的教训

### 2026-03-23 重大教训：ClawHub安全扫描系统性失败

#### 问题根源：
1. **测试策略错误** - 只测试功能，不测试安全

## 📁 项目结构管理经验

### 2026-03-27 新发现：项目结构混乱问题

#### 问题描述：
在修复AISleepGen时发现，项目文件夹结构极其混乱：
- **技能文件夹深埋**：`openclaw_skill` 在项目根目录下，被50多个其他文件夹包围
- **功能分散**：相关代码分散在多个文件夹中
- **维护困难**：难以找到和管理相关文件
- **发布不便**：需要从混乱的文件夹结构中提取技能文件

#### 解决方案：标准化发布文件夹结构
```
D:\openclaw\releases\                    # 统一发布文件夹
├── AISkinX_v1.0.3\                     # AISkinX发布文件夹
├── AISleepGen_v1.0.5\                  # AISleepGen发布文件夹
├── skincare-ai-v1.0.3.zip              # AISkinX发布包
└── sleep-rabbit-skill-v1.0.5.zip       # AISleepGen发布包
```

#### 核心原则：
1. **标准化原则**：所有项目使用相同的发布结构
2. **分离原则**：开发目录与发布目录分离
3. **自动化原则**：发布流程尽量自动化
4. **验证原则**：发布前必须验证结构合规性

#### 具体改进：
1. **创建标准发布脚本**：`create_release.ps1`
2. **建立发布检查工具**：`check_release_structure.ps1`
3. **文档化发布流程**：`RELEASE_PROCESS.md`
4. **版本命名规范**：`项目名_v版本号`

**详细教训记录**：`PROJECT_STRUCTURE_LESSON.md`
2. **安全意识不足** - 忽略平台安全审查要求
3. **代码审查肤浅** - 没深入检查所有文件
4. **文档代码脱节** - 没验证声明与实现一致性
5. **配置安全问题** - 忽略config.yaml中的网络配置

#### 建立的永久性改进：
1. **测试与安全框架** - 标准化发布流程
2. **安全检查脚本** - 自动化安全检查
3. **发布检查清单** - 系统化检查流程

### 🔧 新增检查项（基于AISkinX经验）

#### 1. 配置文件安全检查 ⚠️ **关键教训**
- [ ] **config.yaml零网络配置**：检查original_api_url、world_model_integrator、updates.auto_check等
- [ ] **config.yaml安全声明**：必须有`network_access: false, local_only: true, privacy_friendly: true`
- [ ] **配置与声明一致**：config.yaml与README安全声明必须100%一致
- [ ] **删除矛盾配置**：声称"100%本地"就不能有任何网络相关配置

#### 2. 文件编码检查 ⚠️ **实际遇到的问题**
- [ ] **所有文档UTF-8编码**：README.md、SKILL.md、CHANGELOG.md必须UTF-8
- [ ] **无乱码问题**：中文字符显示正常，定期检查编码
- [ ] **编码一致性**：所有文件统一UTF-8编码，避免混合编码
- [ ] **定期验证**：每次发布前验证文件编码

#### 3. 平台规范检查 ⚠️ **上传经验**
- [ ] **Owner字段兼容**：了解ClawHub最新上传要求
- [ ] **上传流程验证**：测试整个上传流程，包括登录、填写、提交
- [ ] **版本号管理**：语义化版本，每次修复递增修订版本
- [ ] **ClawHub变化**：关注平台更新，及时调整流程

#### 4. 发布前最终验证 ⚠️ **全面检查**
- [ ] **模拟ClawHub扫描**：运行类似安全检查，预测平台反应
- [ ] **用户视角测试**：从用户角度测试安装、使用、卸载
- [ ] **回滚计划**：准备好问题修复和版本回滚方案
- [ ] **沟通准备**：准备好与平台支持沟通的材料

### 📚 从AISkinX v1.0.0 → v1.0.2 学到的具体教训

#### 教训1：config.yaml是安全扫描重点
- **问题**：v1.0.0的config.yaml包含`original_api_url`、`world_model_integrator`等
- **后果**：ClawHub标记为"Suspicious - high confidence"
- **解决**：v1.0.2彻底清理config.yaml，添加安全声明
- **检查**：现在必须检查config.yaml的每个配置项

#### 教训2：文件编码问题容易被忽略
- **问题**：SKILL.md、README.md出现乱码
- **后果**：影响文档可读性，可能影响扫描
- **解决**：重新创建文件，确保UTF-8编码
- **检查**：现在必须验证所有文档文件的编码

#### 教训3：声明与代码必须100%一致
- **问题**：README说"100%本地"，但config.yaml有网络配置
- **后果**：平台认为声明虚假，标记为高风险
- **解决**：确保所有声明都有代码支持
- **检查**：现在必须验证每个安全声明

#### 教训4：平台规范可能变化
- **问题**：ClawHub添加Owner字段，上传流程变化
- **后果**：无法提交新版本
- **解决**：联系支持，了解新要求
- **检查**：现在必须测试上传流程

### 🛡️ 增强的安全检查流程

#### 阶段0：开发前准备
1. **明确安全要求**：100%本地、无网络、零依赖
2. **设计安全架构**：三层保护（隐私、文件、代码）
3. **制定检查清单**：基于本框架

#### 阶段1：开发中检查
1. **实时安全审查**：每完成一个功能就检查安全
2. **配置安全设计**：从一开始就设计安全的config.yaml
3. **文档同步更新**：代码和文档同步更新

#### 阶段2：发布前全面检查
1. **运行增强检查**：使用`enhanced_security_scanner.py`
2. **运行发布清单**：使用`enhanced_release_checklist.py`
3. **生成检查报告**：查看`RELEASE_REPORT.md`

#### 阶段3：上传后监控
1. **监控安全扫描**：关注ClawHub扫描结果
2. **准备快速响应**：有问题立即修复
3. **记录经验教训**：更新本框架

## 🔧 自动化检查工具

### 1. 安全检查脚本 (`security_scanner.py`)
```python
#!/usr/bin/env python3
"""
安全检查脚本 - 发布前必须运行
"""

import os
import re
import sys
from pathlib import Path

def check_network_code(file_path):
    """检查网络代码"""
    patterns = [
        r'import requests',
        r'from requests',
        r'import urllib',
        r'import http\.client',
        r'import socket',
        r'requests\.(get|post|put|delete)',
        r'urllib\.request',
        r'http\.client\.'
    ]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    for pattern in patterns:
        if re.search(pattern, content):
            issues.append(f"网络代码: {pattern}")
    
    return issues

def check_dangerous_functions(file_path):
    """检查危险函数"""
    patterns = [
        r'subprocess\.',
        r'os\.system\(',
        r'eval\(',
        r'exec\(',
        r'__import__\(',
        r'open\(.*[\'"]w[\'"]'
    ]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    for pattern in patterns:
        if re.search(pattern, content):
            issues.append(f"危险函数: {pattern}")
    
    return issues

def check_path_traversal(file_path):
    """检查路径遍历"""
    patterns = [
        r'\.\./',
        r'\.\.\\',
        r'上级目录',
        r'遍历.*目录'
    ]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    for pattern in patterns:
        if re.search(pattern, content):
            issues.append(f"路径遍历: {pattern}")
    
    return issues

def check_external_deps(file_path):
    """检查外部依赖"""
    external_libs = [
        'numpy', 'pandas', 'tensorflow', 'torch',
        'scikit-learn', 'opencv', 'pillow', 'yaml',
        'flask', 'django', 'fastapi'
    ]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    for lib in external_libs:
        if f'import {lib}' in content or f'from {lib}' in content:
            issues.append(f"外部依赖: {lib}")
    
    return issues

def scan_directory(directory):
    """扫描目录"""
    all_issues = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                issues = []
                
                issues.extend(check_network_code(file_path))
                issues.extend(check_dangerous_functions(file_path))
                issues.extend(check_path_traversal(file_path))
                issues.extend(check_external_deps(file_path))
                
                if issues:
                    all_issues[file_path] = issues
    
    return all_issues

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python security_scanner.py <目录路径>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    print(f"🔍 安全检查: {directory}")
    print("=" * 60)
    
    issues = scan_directory(directory)
    
    if not issues:
        print("✅ 无安全问题")
        return 0
    
    print("❌ 发现安全问题:")
    for file_path, file_issues in issues.items():
        print(f"\n📄 {file_path}:")
        for issue in file_issues:
            print(f"  • {issue}")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 2. 增强版安全检查脚本 (`enhanced_security_scanner.py`)
```python
#!/usr/bin/env python3
"""
增强版安全检查脚本 - 基于AISkinX经验
包含config.yaml检查、文件编码检查等
"""

import os
import sys
import re
import json
import yaml
from pathlib import Path

def print_section(title, level=1):
    """打印章节标题"""
    if level == 1:
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    else:
        print(f"\n📋 {title}")
        print("-" * 40)

def check_file_encoding(directory):
    """检查文件编码 - 新增：基于乱码问题"""
    print_section("1. 文件编码检查", 1)
    
    files_to_check = [
        "skill.py",
        "README.md", 
        "SKILL.md",
        "CHANGELOG.md",
        "config.yaml",
        "package.json"
    ]
    
    issues = []
    
    for filename in files_to_check:
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            issues.append(f"❌ {filename}: 文件不存在")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(1000)
                
            # 检查是否有中文字符（对于中文文件）
            if filename.endswith('.md') or filename.endswith('.yaml'):
                if re.search(r'[\u4e00-\u9fff]', content):
                    print(f"✅ {filename}: UTF-8编码正常，中文显示正确")
                else:
                    # 可能是纯英文或无中文
                    size = os.path.getsize(filepath)
                    print(f"⚠️  {filename}: UTF-8编码，无中文字符 ({size}字节)")
            else:
                # 代码文件，检查基本可读性
                if 'import' in content or 'def ' in content or 'class ' in content:
                    print(f"✅ {filename}: UTF-8编码正常，内容可读")
                else:
                    issues.append(f"⚠️  {filename}: 内容可能有问题")
                    
        except UnicodeDecodeError:
            issues.append(f"❌ {filename}: 编码错误，不是有效的UTF-8")
        except Exception as e:
            issues.append(f"❌ {filename}: 读取失败 - {e}")
    
    if issues:
        print("\n⚠️  发现编码问题:")
        for issue in issues:
            print(f"  {issue}")
        return False
    return True

def check_config_yaml(directory):
    """检查config.yaml安全性 - 新增：基于AISkinX经验"""
    print_section("2. config.yaml安全检查", 1)
    
    config_path = os.path.join(directory, "config.yaml")
    if not os.path.exists(config_path):
        print("❌ config.yaml文件不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查危险配置（AISkinX经验）
        dangerous_patterns = [
            (r'original_api_url', '外部API端点'),
            (r'world_model_integrator', 'GPT-4集成'),
            (r'model: "gpt-', 'GPT模型配置'),
            (r'updates\.auto_check: true', '自动更新检查'),
            (r'external_apis', '外部API集成'),
            (r'http://', 'HTTP URL'),
            (r'https://', 'HTTPS URL'),
            (r'api.*url', 'API URL'),
            (r'database.*enabled: true', '数据库集成')
        ]
        
        found_dangerous = False
        for pattern, description in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"❌ 发现危险配置: {description}")
                found_dangerous = True
        
        if found_dangerous:
            print("❌ config.yaml包含网络相关配置（ClawHub会标记为Suspicious）")
            return False
        
        # 检查安全声明（必须有的）
        required_declarations = [
            ('network_access: false', '无网络访问声明'),
            ('local_only: true', '仅本地处理声明'),
            ('privacy_friendly: true', '隐私友好声明')
        ]
        
        missing_declarations = []
        for pattern, description in required_declarations:
            if not re.search(pattern, content):
                missing_declarations.append(description)
        
        if missing_declarations:
            print("❌ config.yaml缺少安全声明:")
            for desc in missing_declarations:
                print(f"  - {desc}")
            return False
        
        print("✅ config.yaml干净，无网络相关配置")
        print("✅ config.yaml有明确的安全声明")
        return True
            
    except yaml.YAMLError as e:
        print(f"❌ config.yaml格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取config.yaml失败: {e}")
        return False

def check_network_code(directory):
    """检查网络代码"""
    print_section("3. 网络代码检查", 1)
    
    network_patterns = [
        r'import requests',
        r'from requests',
        r'import urllib',
        r'import http\.client',
        r'import socket',
        r'requests\.(get|post|put|delete)',
        r'urllib\.request',
        r'http\.client\.',
        r'socket\.',
        r'webhook',
        r'api.*call',
        r'在线验证',
        r'license.*validation'
    ]
    
    found = False
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in network_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                print(f"❌ {path}: 发现网络代码 - {pattern}")
                                found = True
                except:
                    pass
    
    if found:
        print("❌ 发现网络代码