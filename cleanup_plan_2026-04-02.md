# OpenClaw Testing Framework 清理计划
## 2026-04-02

## 🚨 发现问题

### 当前状态：
- **400+ 文件** - 过于庞大
- **大量不相关目录** - ai-ml, blockchain, ci-cd 等
- **重复的审核脚本** - 多个版本相同工具
- **历史报告堆积** - 大量JSON报告文件

### 核心问题：
1. **目录污染** - 不相关的项目文件混入
2. **版本混乱** - 多个版本的相同工具
3. **资源浪费** - 占用空间，影响性能
4. **维护困难** - 难以找到真正有用的工具

## 🎯 清理目标

### 保留的核心工具：
1. **增强版审核框架 V2** - `enhanced_audit_framework_v2_ascii.py`
2. **发布前清理器** - `pre_release_cleaner.py`
3. **永久审核框架** - `permanent_audit_ascii.py`
4. **英文合规检查器** - `english_compliance_checker.py`
5. **内存优化器** - `memory_optimizer.py`
6. **工作流程拦截器** - `WORKFLOW_INTERCEPTOR_V3_ASCII.py` (在workspace)

### 删除的内容：
1. **不相关目录** - ai-ml, blockchain, ci-cd, dashboard, database 等
2. **重复脚本** - 多个版本的AISleepGen审核工具
3. **历史报告** - 旧的JSON报告文件
4. **测试文件** - 开发过程中的测试文件
5. **备份文件** - 旧版本的备份

## 🔧 清理步骤

### 阶段1: 备份重要文件
1. 备份当前有效的工具
2. 备份配置文件和模板

### 阶段2: 删除不相关目录
```
删除:
- ai-ml/
- blockchain/
- ci-cd/
- dashboard/
- database/
- distributed/
- enterprise_integration/
- microservices/
- monitoring/
- sandbox/
- static/
```

### 阶段3: 清理重复文件
1. 保留最新版本的审核工具
2. 删除旧版本的重复工具
3. 删除历史报告文件

### 阶段4: 重建精简结构
```
新结构:
D:\OpenClaw_TestingFramework\
├── core_tools\          # 核心工具
├── templates\          # 模板文件
├── config\            # 配置文件
├── reports\           # 当前报告 (定期清理)
└── backups\           # 重要备份
```

## 📋 清理清单

### 要删除的目录：
- [ ] ai-ml
- [ ] blockchain
- [ ] ci-cd
- [ ] dashboard
- [ ] database
- [ ] distributed
- [ ] enterprise_integration
- [ ] microservices
- [ ] monitoring
- [ ] sandbox
- [ ] static

### 要保留的文件：
- [ ] enhanced_audit_framework_v2_ascii.py
- [ ] pre_release_cleaner.py
- [ ] permanent_audit_ascii.py
- [ ] english_compliance_checker.py
- [ ] memory_optimizer.py
- [ ] WORKFLOW_INTERCEPTOR_V3_ASCII.py (在workspace)

### 要清理的文件类型：
- [ ] *.json (历史报告)
- [ ] *.txt (临时文件)
- [ ] *.bak (备份文件)
- [ ] *.tmp (临时文件)
- [ ] *.log (日志文件)

## 🛡️ 安全措施

### 备份策略：
1. **完整备份** - 清理前备份整个目录
2. **选择性恢复** - 只恢复真正需要的文件
3. **验证备份** - 确保备份可恢复

### 验证步骤：
1. 清理后测试核心工具是否工作
2. 验证文件数量大幅减少
3. 确保没有误删重要文件

## 📊 预期效果

### 清理前：
- 400+ 文件
- 多个不相关目录
- 混乱的结构
- 维护困难

### 清理后：
- ~20 个核心文件
- 清晰的结构
- 易于维护
- 快速访问

## 🔄 定期维护计划

### 每日：
- 清理临时文件
- 删除旧的报告文件

### 每周：
- 优化文件大小
- 备份重要配置

### 每月：
- 全面清理和优化
- 更新工具版本

## 🎯 最终目标

创建一个**精简、高效、易维护**的OpenClaw测试框架，只包含真正有用的审核工具，避免重复今天发现的文件污染问题。