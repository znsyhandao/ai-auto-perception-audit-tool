# AI Auto-Perception Evolution Audit Tool

## 🎯 Project Overview

**AI Auto-Perception Evolution Audit Tool** is an intelligent system that can automatically perceive problems in conversations, learn experience lessons, evolve audit frameworks, and fix discovered issues.

## 🤖 Core Features

### **1. AI Auto-Perception**
- Automatically scans memory files (`memory/YYYY-MM-DD.md`)
- Extracts `/remember` experience lessons
- Identifies problem patterns and solutions

### **2. AI Auto-Learning**
- Learns from conversations and memory files
- Builds and maintains knowledge base (`ai_knowledge_base_v2.json`)
- Calculates confidence and relevance

### **3. AI Auto-Evolution**
- Automatically upgrades audit frameworks with new experiences
- Adds new check rules automatically
- Validates upgrade results

### **4. AI Auto-Fix**
- Automatically fixes version inconsistencies
- Automatically cleans cache files
- Automatically verifies English compliance

## 📁 File Structure

```
ai-auto-perception-audit-tool/
├── AI_AUTO_SYSTEM.py                    # AI Main Program
├── enhanced_audit_framework_v3_fixed.py # Enhanced Audit Framework
├── ai_knowledge_base_v2.json           # AI Knowledge Base
├── pre_release_cleaner.py              # Pre-release Cleaner
├── permanent_audit_ascii.py            # Permanent Audit Framework
├── README.md                           # This Document
├── README_AI_AUTO_PERCEPTION.md       # Detailed Documentation (Chinese)
├── start_ai_auto_perception.bat       # Startup Script
└── .gitignore                         # Git Ignore File
```

## 🚀 Quick Start

### **Requirements**
- Python 3.8+
- OpenClaw workspace environment

### **Usage**

#### **1. AI Auto-Learning**
```bash
python AI_AUTO_SYSTEM.py scan
```
Scans memory files and automatically learns experience lessons.

#### **2. AI Audit Skill**
```bash
python AI_AUTO_SYSTEM.py audit "skill_path"
```
Audits a skill using the AI auto-perception evolution system.

#### **3. Generate AI Report**
```bash
python AI_AUTO_SYSTEM.py report
```
Generates AI system status report.

#### **4. Test AI Capabilities**
```bash
python AI_AUTO_SYSTEM.py test
```
Tests all AI functionalities.

## 🔧 Core Functions Explained

### **AI Auto-Perception**
The system automatically scans `~/.openclaw/workspace/memory/` directory and extracts experience lessons.

### **Knowledge Base System**
- **Problem Patterns**: Stores identified problem patterns
- **Experience Lessons**: Stores learned experience lessons
- **Framework Upgrades**: Records audit framework upgrade history

### **Auto-Fix Functions**
1. **Version Consistency Check**: Ensures ZIP filename matches skill version
2. **Cache File Cleanup**: Automatically cleans `__pycache__` and `.pyc` files
3. **English Compliance Check**: Verifies core files are 100% English

## 📊 Included 2026-04-03 Experience Lessons

The system has learned 8 key experience lessons:

1. **Version numbers must be updated** - Update version number for each major improvement
2. **Filename version consistency** - ZIP filename must match skill version (skill-v1.1.0.zip)
3. **100% English requirement** - ClawHub审核要求所有文件100%英文
4. **Complete documentation set** - Skills need SKILL.md, README.md, CHANGELOG.md
5. **Functionality testing required** - Must test all commands before release
6. **Clean cache files** - Must clean __pycache__ and .pyc files before release
7. **Security verification** - Ensure no dangerous functions, no network access
8. **Detail checking** - Check all filenames, version references, and documentation consistency

## 🎯 Use Cases

### **Case 1: Natural Language Audit**
User says: "Audit my plugin"
AI automatically executes the complete audit process.

### **Case 2: Batch Audit**
Audit multiple skills, AI automatically learns and applies experience lessons.

### **Case 3: Framework Upgrade**
When new problems are discovered, AI automatically upgrades audit frameworks.

## 🔍 Technical Architecture

### **Core Modules**
1. **Perception Module**: Scans memory files, extracts experience lessons
2. **Learning Module**: Builds and maintains knowledge base
3. **Audit Module**: Runs enhanced audit framework
4. **Fix Module**: Automatically fixes discovered problems
5. **Evolution Module**: Upgrades audit frameworks

### **Data Flow**
```
Conversation/Memory Files → AI Perception → Learn Experience → Upgrade Framework → Audit Skill → Fix Problems → Generate Report
```

## 📈 Performance Metrics

### **Verified Functions**
- ✅ Auto-Learning: 8 experience lessons
- ✅ Auto-Audit: 6/6 checks passed
- ✅ Auto-Fix: Version consistency, cache cleanup, English compliance
- ✅ Auto-Report: Generates AI-enhanced reports

### **Processing Speed**
- Memory file scanning: < 1 second
- Skill audit: < 5 seconds
- Auto-fix: < 2 seconds

## 🛠️ Extension Development

### **Adding New Check Rules**
1. Add new check function in `enhanced_audit_framework_v3_fixed.py`
2. Add corresponding problem pattern in knowledge base
3. AI will automatically learn and apply new rules

### **Integrating Other Tools**
The system is modular and can easily integrate:
- Other audit frameworks
- Security scanning tools
- Performance testing tools

## 📝 License

MIT License

## 🤝 Contribution Guidelines

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support & Feedback

If you have questions or suggestions, please submit an Issue.

## 🎉 Acknowledgments

Thanks to the OpenClaw community for support and contributions.

---

**AI Auto-Perception Evolution Audit Tool - Making Audits Smarter!** 🚀