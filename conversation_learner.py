#!/usr/bin/env python3
"""
对话学习模块 - 基础版本
从对话中提取经验教训，半自动更新知识库
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class ConversationLearner:
    """对话学习器 - 基础版本"""
    
    def __init__(self, knowledge_base_path: str = "ai_knowledge_base_v2.json"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base = self._load_knowledge_base()
        
        # 学习模式
        self.learning_patterns = [
            r"/learn\s+(.+?)(?:\s+\|(.+))?$",  # /learn 经验 | 类别
            r"记住(?:这个)?经验[：:]\s*(.+)",    # 记住这个经验：xxx
            r"经验教训[：:]\s*(.+)",             # 经验教训：xxx
            r"应该(?:记住|学习)[：:]\s*(.+)",     # 应该记住：xxx
        ]
        
        # 经验分类关键词
        self.category_keywords = {
            "版本管理": ["版本", "version", "v1", "v2", "升级", "更新"],
            "安全": ["安全", "注入", "密钥", "密码", "漏洞", "SQL", "XSS"],
            "文档": ["文档", "README", "CHANGELOG", "SKILL", "说明"],
            "代码质量": ["缓存", ".pyc", "__pycache__", "清理", "格式"],
            "测试": ["测试", "功能", "命令", "验证", "工作"],
            "发布": ["发布", "ZIP", "打包", "ClawHub", "审核"],
        }
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """加载知识库"""
        if not self.knowledge_base_path.exists():
            return {
                "lessons": [],
                "patterns": [],
                "upgrades": [],
                "last_updated": datetime.now().isoformat()
            }
        
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "lessons": [],
                "patterns": [],
                "upgrades": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def _save_knowledge_base(self):
        """保存知识库"""
        self.knowledge_base["last_updated"] = datetime.now().isoformat()
        
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def extract_lessons_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取经验教训"""
        lessons = []
        
        for pattern in self.learning_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                lesson_text = match.group(1).strip()
                category_hint = match.group(2).strip() if match.group(2) else ""
                
                # 确定类别
                category = self._detect_category(lesson_text, category_hint)
                
                # 创建经验对象
                lesson = {
                    "id": f"lesson_{len(self.knowledge_base['lessons']) + 1}",
                    "text": lesson_text,
                    "category": category,
                    "source": "conversation",
                    "learned_at": datetime.now().isoformat(),
                    "confidence": 0.8,  # 基础置信度
                }
                
                lessons.append(lesson)
        
        return lessons
    
    def _detect_category(self, lesson_text: str, category_hint: str) -> str:
        """检测经验类别"""
        # 如果有明确提示，使用提示
        if category_hint:
            for cat in self.category_keywords:
                if cat.lower() in category_hint.lower():
                    return cat
        
        # 否则基于关键词检测
        lesson_lower = lesson_text.lower()
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in lesson_lower:
                    return category
        
        # 默认类别
        return "通用"
    
    def learn_from_conversation(self, conversation_text: str, auto_save: bool = False) -> Dict[str, Any]:
        """从对话中学习"""
        extracted_lessons = self.extract_lessons_from_text(conversation_text)
        
        if not extracted_lessons:
            return {
                "success": False,
                "message": "未发现可学习的经验教训",
                "lessons": []
            }
        
        # 添加到知识库
        for lesson in extracted_lessons:
            # 检查是否已存在类似经验
            if not self._is_duplicate_lesson(lesson):
                self.knowledge_base["lessons"].append(lesson)
        
        if auto_save and extracted_lessons:
            self._save_knowledge_base()
        
        return {
            "success": True,
            "message": f"成功学习 {len(extracted_lessons)} 个经验教训",
            "lessons": extracted_lessons,
            "total_lessons": len(self.knowledge_base["lessons"])
        }
    
    def _is_duplicate_lesson(self, new_lesson: Dict[str, Any]) -> bool:
        """检查是否是重复的经验"""
        new_text = new_lesson["text"].lower()
        
        for existing_lesson in self.knowledge_base["lessons"]:
            existing_text = existing_lesson.get("text", "").lower()
            # 简单相似度检查（包含关系）
            if new_text in existing_text or existing_text in new_text:
                return True
        
        return False
    
    def generate_audit_rule(self, lesson: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """基于经验生成审核规则（基础版本）"""
        text = lesson["text"].lower()
        category = lesson["category"]
        
        rule_template = {
            "name": "",
            "description": lesson["text"],
            "category": category,
            "severity": "medium",
            "pattern": "",
            "fix_suggestion": "",
            "source_lesson": lesson["id"]
        }
        
        # 基于经验内容生成简单规则
        if "版本" in text or "version" in text:
            rule_template["name"] = f"版本检查规则_{lesson['id']}"
            rule_template["pattern"] = r"version\s*=\s*['\"](\d+\.\d+\.\d+)['\"]"
            rule_template["fix_suggestion"] = "确保版本号格式正确且已更新"
            rule_template["severity"] = "high"
        
        elif "缓存" in text or ".pyc" in text:
            rule_template["name"] = f"缓存文件检查规则_{lesson['id']}"
            rule_template["pattern"] = r"\.pyc$|__pycache__"
            rule_template["fix_suggestion"] = "清理Python缓存文件"
            rule_template["severity"] = "low"
        
        elif "英文" in text or "english" in text:
            rule_template["name"] = f"英文合规检查规则_{lesson['id']}"
            rule_template["pattern"] = r"[\u4e00-\u9fff]"  # 中文字符
            rule_template["fix_suggestion"] = "确保文件内容为100%英文"
            rule_template["severity"] = "medium"
        
        else:
            # 无法生成具体规则
            return None
        
        return rule_template
    
    def interactive_learning(self):
        """交互式学习模式"""
        print("=" * 60)
        print("对话学习模式")
        print("=" * 60)
        print("\n输入对话文本（输入空行结束）：")
        
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        
        conversation_text = "\n".join(lines)
        
        if not conversation_text.strip():
            print("未输入文本")
            return
        
        result = self.learn_from_conversation(conversation_text, auto_save=False)
        
        if result["success"]:
            print(f"\n✅ 发现 {len(result['lessons'])} 个经验教训：")
            for i, lesson in enumerate(result["lessons"], 1):
                print(f"{i}. [{lesson['category']}] {lesson['text']}")
            
            # 询问是否保存
            save = input("\n是否保存到知识库？(y/n): ").lower()
            if save == 'y':
                self._save_knowledge_base()
                print(f"✅ 已保存到 {self.knowledge_base_path}")
                
                # 询问是否生成规则
                generate = input("是否基于新经验生成审核规则？(y/n): ").lower()
                if generate == 'y':
                    self._generate_rules_from_new_lessons(result["lessons"])
            else:
                print("❌ 未保存")
        else:
            print(f"❌ {result['message']}")
    
    def _generate_rules_from_new_lessons(self, lessons: List[Dict[str, Any]]):
        """从新经验生成规则"""
        new_rules = []
        
        for lesson in lessons:
            rule = self.generate_audit_rule(lesson)
            if rule:
                new_rules.append(rule)
                print(f"✅ 生成规则: {rule['name']}")
        
        if new_rules:
            # 添加到知识库
            if "patterns" not in self.knowledge_base:
                self.knowledge_base["patterns"] = []
            
            self.knowledge_base["patterns"].extend(new_rules)
            self._save_knowledge_base()
            print(f"✅ 已添加 {len(new_rules)} 个新规则到知识库")
    
    def show_statistics(self):
        """显示学习统计"""
        print("=" * 60)
        print("知识库统计")
        print("=" * 60)
        
        lessons = self.knowledge_base.get("lessons", [])
        patterns = self.knowledge_base.get("patterns", [])
        
        print(f"经验教训总数: {len(lessons)}")
        print(f"审核规则总数: {len(patterns)}")
        
        # 按类别统计
        categories = {}
        for lesson in lessons:
            cat = lesson.get("category", "未知")
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n经验类别分布:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}")
        
        if lessons:
            latest = lessons[-1]
            print(f"\n最新经验: {latest['text']}")
            print(f"学习时间: {latest.get('learned_at', '未知')}")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        learner = ConversationLearner()
        
        if command == "learn" and len(sys.argv) > 2:
            # 从文件学习
            file_path = sys.argv[2]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                result = learner.learn_from_conversation(text, auto_save=True)
                print(result["message"])
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")
        
        elif command == "interactive":
            # 交互式学习
            learner.interactive_learning()
        
        elif command == "stats":
            # 显示统计
            learner.show_statistics()
        
        elif command == "help":
            show_help()
        
        else:
            print(f"未知命令: {command}")
            show_help()
    else:
        show_help()

def show_help():
    """显示帮助"""
    print("使用方法:")
    print("  python conversation_learner.py learn <文件路径>  - 从文件学习")
    print("  python conversation_learner.py interactive      - 交互式学习")
    print("  python conversation_learner.py stats            - 显示统计")
    print("  python conversation_learner.py help             - 显示帮助")
    print("\n学习格式示例:")
    print('  /learn 版本号必须更新 | 版本管理')
    print('  记住这个经验：缓存文件必须清理')
    print('  经验教训：文档必须100%英文')

if __name__ == "__main__":
    main()