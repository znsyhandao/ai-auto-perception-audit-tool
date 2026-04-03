    def _auto_fix_issues(self, skill_path: str):
        """自动修复问题"""
        skill_dir = Path(skill_path)
        
        # 检查版本不一致问题
        self._fix_version_mismatch(skill_dir)
        
        # 清理缓存文件
        self._clean_cache_files(skill_dir)
        
        # 检查英文合规
        self._check_english_compliance(skill_dir)
    
    def _fix_version_mismatch(self, skill_dir: Path):
        """修复版本不一致问题"""
        print("    • 检查版本一致性...")
        
        # 从skill.py提取版本
        skill_version = None
        skill_file = skill_dir / "skill.py"
        
        if skill_file.exists():
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                match = re.search(r'self\.version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    skill_version = match.group(1)
            except:
                pass
        
        if skill_version:
            # 检查ZIP文件名
            expected_zip = f"skill-v{skill_version}.zip"
            zip_files = list(skill_dir.glob("skill-v*.zip"))
            
            if zip_files:
                actual_zip = zip_files[0]
                
                if actual_zip.name != expected_zip:
                    print(f"    ⚠️  发现版本不一致: {actual_zip.name} -> {expected_zip}")
                    
                    # 重命名ZIP文件
                    new_path = skill_dir / expected_zip
                    try:
                        actual_zip.rename(new_path)
                        print(f"    ✅ 已重命名: {new_path.name}")
                    except Exception as e:
                        print(f"    ❌ 重命名失败: {e}")
                else:
                    print(f"    ✅ ZIP文件名正确: {expected_zip}")
            else:
                print(f"    ⚠️  未找到ZIP文件")
        else:
            print(f"    ⚠️  无法从skill.py提取版本")
    
    def _clean_cache_files(self, skill_dir: Path):
        """清理缓存文件"""
        print("    • 清理缓存文件...")
        
        cache_patterns = ["__pycache__", "*.pyc", "*.pyo", "*.pyd"]
        cleaned = []
        
        for pattern in cache_patterns:
            for file in skill_dir.rglob(pattern):
                try:
                    if file.is_file():
                        file.unlink()
                        cleaned.append(str(file.relative_to(skill_dir)))
                    elif file.is_dir():
                        shutil.rmtree(file)
                        cleaned.append(str(file.relative_to(skill_dir)))
                except:
                    pass
        
        if cleaned:
            print(f"    ✅ 清理了 {len(cleaned)} 个缓存文件")
        else:
            print(f"    ✅ 无缓存文件需要清理")
    
    def _check_english_compliance(self, skill_dir: Path):
        """检查英文合规"""
        print("    • 检查英文合规...")
        
        core_files = ["skill.py", "SKILL.md", "README.md", "CHANGELOG.md", "requirements.txt"]
        issues = []
        
        for filename in core_files:
            filepath = skill_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    import re
                    chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
                    if chinese_chars:
                        issues.append(f"{filename}: {len(chinese_chars)} 个中文字符")
                except:
                    issues.append(f"{filename}: 无法读取")
        
        if not issues:
            print(f"    ✅ 所有核心文件100%英文")
        else:
            print(f"    ⚠️  发现 {len(issues)} 个文件包含中文")
            for issue in issues:
                print(f"      {issue}")
    
    def generate_ai_report(self):
        """生成AI报告"""
        print(f"\n📊 AI自动感知进化框架报告")
        print(f"=" * 60)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "ai_system_version": self.version,
            "knowledge_base": {
                "problem_patterns": len(self.problem_patterns),
                "experience_lessons": len(self.experience_lessons),
                "framework_upgrades": len(self.knowledge_base.get("framework_upgrades", []))
            },
            "capabilities": {
                "learning_mode": self.learning_mode,
                "auto_fix_mode": self.auto_fix_mode,
                "auto_upgrade_mode": self.auto_upgrade_mode
            },
            "recent_activity": {
                "last_scan": datetime.now().isoformat(),
                "files_scanned": 0,
                "lessons_learned": 0
            }
        }
        
        # 显示报告
        print(f"AI系统版本: {report['ai_system_version']}")
        print(f"知识库统计:")
        print(f"  问题模式: {report['knowledge_base']['problem_patterns']} 个")
        print(f"  经验教训: {report['knowledge_base']['experience_lessons']} 个")
        print(f"  框架升级: {report['knowledge_base']['framework_upgrades']} 次")
        print(f"系统能力:")
        print(f"  学习模式: {'启用' if report['capabilities']['learning_mode'] else '禁用'}")
        print(f"  自动修复: {'启用' if report['capabilities']['auto_fix_mode'] else '禁用'}")
        print(f"  自动升级: {'启用' if report['capabilities']['auto_upgrade_mode'] else '禁用'}")
        
        # 保存报告
        report_path = self.framework_dir / "ai_auto_perception_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n报告已保存: {report_path}")
        
        return report

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 AI自动感知进化框架启动")
    print("=" * 60)
    
    # 创建AI系统
    ai_system = AIAutoPerceptionEvolution()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scan":
            # 扫描记忆文件
            ai_system.scan_memory_files()
            
        elif command == "audit" and len(sys.argv) > 2:
            # 审核技能
            skill_path = sys.argv[2]
            ai_system.audit_skill_with_ai(skill_path)
            
        elif command == "perceive" and len(sys.argv) > 2:
            # 感知对话
            conversation_text = " ".join(sys.argv[2:])
            ai_system.auto_perceive_from_conversation(conversation_text)
            
        elif command == "report":
            # 生成报告
            ai_system.generate_ai_report()
            
        elif command == "upgrade":
            # 手动触发升级
            print("手动触发框架升级...")
            ai_system._auto_upgrade_audit_framework()
            
        else:
            print(f"未知命令: {command}")
            print("可用命令: scan, audit <技能路径>, perceive <对话文本>, report, upgrade")
    else:
        # 交互式模式
        print("\n请选择操作:")
        print("1. 扫描记忆文件，自动学习")
        print("2. 审核技能 (AI增强)")
        print("3. 感知对话中的问题")
        print("4. 生成AI报告")
        print("5. 手动升级审核框架")
        print("6. 退出")
        
        try:
            choice = input("\n请输入选项 (1-6): ").strip()
            
            if choice == "1":
                ai_system.scan_memory_files()
                
            elif choice == "2":
                skill_path = input("请输入技能路径: ").strip()
                if skill_path:
                    ai_system.audit_skill_with_ai(skill_path)
                else:
                    print("未提供技能路径")
                    
            elif choice == "3":
                print("请输入对话文本 (Ctrl+Z 结束输入):")
                conversation_lines = []
                try:
                    while True:
                        line = input()
                        conversation_lines.append(line)
                except EOFError:
                    pass
                
                conversation_text = "\n".join(conversation_lines)
                if conversation_text.strip():
                    ai_system.auto_perceive_from_conversation(conversation_text)
                else:
                    print("未提供对话文本")
                    
            elif choice == "4":
                ai_system.generate_ai_report()
                
            elif choice == "5":
                ai_system._auto_upgrade_audit_framework()
                
            elif choice == "6":
                print("退出AI系统")
                
            else:
                print("无效选项")
                
        except KeyboardInterrupt:
            print("\n\n用户中断")
        except Exception as e:
            print(f"操作出错: {e}")

if __name__ == "__main__":
    main()