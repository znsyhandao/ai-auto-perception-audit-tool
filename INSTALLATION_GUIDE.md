# AI自动感知进化审核工具 - 安装指南

## 🚀 快速安装

### **方法1: 克隆到OpenClaw测试框架目录（推荐）**
```bash
# 切换到OpenClaw测试框架目录
cd D:\OpenClaw_TestingFramework

# 克隆仓库
git clone https://github.com/znsyhandao/ai-auto-perception-audit-tool.git

# 进入工具目录
cd ai-auto-perception-audit-tool
```

**文件夹位置：**
```
D:\OpenClaw_TestingFramework\ai-auto-perception-audit-tool\
```

### **方法2: 克隆到用户主目录**
```bash
# 切换到用户主目录
cd ~

# 克隆仓库
git clone https://github.com/znsyhandao/ai-auto-perception-audit-tool.git

# 进入工具目录
cd ai-auto-perception-audit-tool
```

**文件夹位置：**
```
C:\Users\<用户名>\ai-auto-perception-audit-tool\
```

### **方法3: 克隆到自定义目录**
```bash
# 创建自定义目录
mkdir D:\AI_Tools

# 切换到自定义目录
cd D:\AI_Tools

# 克隆仓库
git clone https://github.com/znsyhandao/ai-auto-perception-audit-tool.git

# 进入工具目录
cd ai-auto-perception-audit-tool
```

**文件夹位置：**
```
D:\AI_Tools\ai-auto-perception-audit-tool\
```

## 📁 文件夹结构

克隆后，你会得到以下结构：

```
ai-auto-perception-audit-tool/
├── AI_AUTO_SYSTEM.py                    # 🤖 AI主程序
├── enhanced_audit_framework_v3_fixed.py # 🔍 增强版审核框架
├── ai_knowledge_base_v2.json           # 🧠 AI知识库
├── pre_release_cleaner.py              # 🧹 发布前清理器
├── permanent_audit_ascii.py            # ✅ 永久审核框架
├── README.md                           # 📖 简要说明
├── README_AI_AUTO_PERCEPTION.md       # 📚 详细文档
├── start_ai_auto_perception.bat       # 🚀 启动脚本
├── .gitignore                         # 🚫 Git忽略文件
└── LICENSE                            # 📄 MIT许可证
```

## 🔧 环境要求

### **Python版本**
- Python 3.8 或更高版本

### **系统要求**
- Windows / macOS / Linux
- Git (用于克隆)

### **OpenClaw环境（可选但推荐）**
- OpenClaw 工作空间
- 记忆文件目录 (`~/.openclaw/workspace/memory/`)

## 🎯 快速测试

### **测试安装是否成功**
```bash
# 进入工具目录
cd ai-auto-perception-audit-tool

# 运行帮助命令
python AI_AUTO_SYSTEM.py help

# 测试AI能力
python AI_AUTO_SYSTEM.py test
```

### **预期输出**
```
============================================================
AI自动感知进化系统 v1.0
============================================================

使用方法:
  python AI_AUTO_SYSTEM.py scan        - 扫描记忆文件，自动学习
  python AI_AUTO_SYSTEM.py audit <路径> - AI审核技能
  python AI_AUTO_SYSTEM.py report      - 生成AI报告
  python AI_AUTO_SYSTEM.py test        - 测试AI能力
  python AI_AUTO_SYSTEM.py help        - 显示帮助
```

## 📝 配置说明

### **1. 记忆文件路径配置**
