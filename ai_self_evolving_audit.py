    def _save_framework_upgrades(self):
        """保存框架升级记录"""
        upgrades_path = self.framework_dir / "framework_upgrades.json"
        
        data = {
            "upgrades": [u.to_dict() for u in self.framework_upgrades],
            "metadata": {
                "total_upgrades": len(self.framework_upgrades),
                "current_version": self.version,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        with open(upgrades_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def audit_skill(self, skill_path: str):
        """审核技能 - 使用AI增强的审核"""
        print(f"\n🔍 AI审核技能: {skill_path}")
        
        # 1. 运行传统审核
        traditional_results = self._run_traditional_audit(skill_path)
        
        # 2. AI分析
        ai_analysis = self._analyze_with_ai(skill_path, traditional_results)
        
        # 3. 自动修复（如果启用）
        if self.auto_fix_mode and ai_analysis.get("fixable_issues"):
            self._auto_fix_issues(skill_path, ai_analysis["fixable_issues"])
        
        # 4. 学习新经验教训
        if self.learning_mode:
            self._learn_from_audit(skill_path, traditional_results, ai_analysis)
        
        # 5. 生成AI增强的报告
        report = self._generate_ai_enhanced_report(skill_path, traditional_results, ai_analysis)
        
        return report
    
    def _run_traditional_audit(self, skill_path: str) -> Dict:
        """运行传统审核"""
        # 这里可以集成现有的审核框架
        results = {
            "version_consistency": self._check_version_consistency(skill_path),
            "english_compliance": self._check_english_compliance(skill_path),
            "security": self._check_security(skill_path),
            "file_structure": self._check_file_structure(skill_path),
            "functionality": self._check_functionality(skill_path)
        }
        
        return results
    
    def _analyze_with_ai(self, skill_path: str, traditional_results: Dict) -> Dict:
        """使用AI分析"""
        analysis = {
            "problem_patterns_matched": [],
            "confidence_scores": {},
            "recommendations": [],
            "fixable_issues": [],
            "potential_risks": []
        }
        
        # 匹配问题模式
        for pattern in self.problem_patterns:
            if self._pattern_matches(skill_path, pattern):
                analysis["problem_patterns_matched"].append(pattern.pattern_id)
                
                if pattern.auto_fixable:
                    analysis["fixable_issues"].append({
                        "pattern_id": pattern.pattern_id,
                        "description": pattern.description,
                        "fix_script": pattern.fix_script
                    })
        
        # 生成推荐
        for lesson in self.experience_lessons[-5:]:  # 最近5个经验教训
            analysis["recommendations"].append({
                "lesson_id": lesson.lesson_id,
                "title": lesson.title,
                "recommendation": lesson.solution[:100] + "..." if len(lesson.solution) > 100 else lesson.solution
            })
        
        return analysis
    
    def _pattern_matches(self, skill_path: str, pattern: ProblemPattern) -> bool:
        """检查问题模式是否匹配"""
        skill_dir = Path(skill_path)
        
        # 检查症状
        symptoms_matched = 0
        
        for symptom in pattern.symptoms:
            if self._check_symptom(skill_dir, symptom):
                symptoms_matched += 1
        
        # 如果匹配至少一个症状，认为模式匹配
        return symptoms_matched > 0
    
    def _check_symptom(self, skill_dir: Path, symptom: str) -> bool:
        """检查症状"""
        symptom_lower = symptom.lower()
        
        # 版本不一致症状
        if "zip" in symptom_lower and "version" in symptom_lower:
            zip_files = list(skill_dir.glob("skill-v*.zip"))
            if zip_files:
                zip_file = zip_files[0]
                # 检查版本格式
                import re
                match = re.search(r'skill-v([\d.]+)\.zip', zip_file.name)
                if match:
                    zip_version = match.group(1)
                    
                    # 检查skill.py版本
                    skill_version = self._get_skill_version(skill_dir)
                    if skill_version and skill_version != zip_version:
                        return True
        
        # 中文内容症状
        elif "中文" in symptom_lower or "chinese" in symptom_lower:
            core_files = ["skill.py", "SKILL.md", "README.md", "CHANGELOG.md"]
            for file in core_files:
                filepath = skill_dir / file
                if filepath.exists():
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        import re
                        chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
                        if chinese_chars:
                            return True
                    except:
                        pass
        
        return False
    
    def _get_skill_version(self, skill_dir: Path) -> Optional[str]:
        """获取技能版本"""
        skill_file = skill_dir / "skill.py"
        
        if skill_file.exists():
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                match = re.search(r'self\.version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
            except:
                pass
        
        return None
    
    def _auto_fix_issues(self, skill_path: str, fixable_issues: List[Dict]):
        """自动修复问题"""
        print(f"\n🔧 AI自动修复 {len(fixable_issues)} 个问题...")
        
        for issue in fixable_issues:
            pattern_id = issue["pattern_id"]
            fix_script = issue.get("fix_script")
            
            if fix_script:
                fix_script_path = self.framework_dir / fix_script
                
                if fix_script_path.exists():
                    print(f"  运行修复脚本: {fix_script}")
                    
                    try:
                        # 执行修复脚本
                        import subprocess
                        result = subprocess.run(
                            [sys.executable, str(fix_script_path), skill_path],
                            capture_output=True,
                            text=True,
                            encoding='utf-8'
                        )
                        
                        if result.returncode == 0:
                            print(f"    ✅ 修复成功: {issue['description']}")
                        else:
                            print(f"    ❌ 修复失败: {result.stderr}")
                            
                    except Exception as e:
                        print(f"    ⚠️  修复出错: {e}")
                else:
                    print(f"   ⚠️  修复脚本不存在: {fix_script}")
    
    def _learn_from_audit(self, skill_path: str, traditional_results: Dict, ai_analysis: Dict):
        """从审核中学习"""
        # 检查是否有新的问题模式
        new_patterns = []
        
        for issue in ai_analysis.get("fixable_issues", []):
            pattern_id = issue["pattern_id"]
            
            # 检查是否已经知道这个模式
            known_pattern = any(p.pattern_id == pattern_id for p in self.problem_patterns)
            
            if not known_pattern:
                # 发现新问题模式
                new_pattern = ProblemPattern(
                    pattern_id=f"new_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description=issue["description"],
                    symptoms=["待分析"],
                    root_cause="待分析",
                    solution="待分析",
                    first_seen=datetime.now().strftime("%Y-%m-%d"),
                    last_seen=datetime.now().strftime("%Y-%m-%d"),
                    occurrence_count=1,
                    severity="medium",
                    auto_fixable=False
                )
                
                new_patterns.append(new_pattern)
                print(f"  🎯 发现新问题模式: {issue['description']}")
        
        # 添加到问题模式
        if new_patterns:
            self.problem_patterns.extend(new_patterns)
            self._save_knowledge_base()
            
            # 创建新的经验教训
            for pattern in new_patterns:
                new_lesson = ExperienceLesson(
                    lesson_id=f"lesson_from_pattern_{pattern.pattern_id}",
                    title=f"新问题模式: {pattern.description}",
                    problem_pattern_id=pattern.pattern_id,
                    date_learned=datetime.now().strftime("%Y-%m-%d"),
                    context=f"在审核 {skill_path} 时发现",
                    solution="需要进一步分析",
                    tools_updated=[],
                    tests_added=[],
                    prevention_measures=["增加相关检查"],
                    confidence=0.70
                )
                
                self.experience_lessons.append(new_lesson)
            
            self._save_experience_lessons()
    
    def _generate_ai_enhanced_report(self, skill_path: str, traditional_results: Dict, ai_analysis: Dict) -> Dict:
        """生成AI增强的报告"""
        report = {
            "skill_path": skill_path,
            "audit_date": datetime.now().isoformat(),
            "ai_system_version": self.version,
            "traditional_results": traditional_results,
            "ai_analysis": ai_analysis,
            "recommendations": ai_analysis.get("recommendations", []),
            "applied_fixes": [],
            "learned_lessons": []
        }
        
        # 保存报告
        report_path = Path(skill_path) / "ai_enhanced_audit_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 AI增强报告已保存: {report_path}")
        
        return report
    
    def run_daily_maintenance(self):
        """运行每日维护"""
        print(f"\n🔄 AI系统每日维护...")
        
        # 1. 清理旧备份
        self._clean_old_backups()
        
        # 2. 优化知识库
        self._optimize_knowledge_base()
        
        # 3. 检查工具更新
        self._check_for_tool_updates()
        
        # 4. 生成维护报告
        self._generate_maintenance_report()
        
        print(f"\n✅ 每日维护完成")
    
    def _clean_old_backups(self):
        """清理旧备份"""
        backup_dir = self.framework_dir / "backups"
        
        if backup_dir.exists():
            backup_folders = [d for d in backup_dir.iterdir() if d.is_dir()]
            
            # 保留最近7天的备份
            for folder in backup_folders:
                try:
                    folder_date = datetime.strptime(folder.name[:8], "%Y%m%d")
                    days_old = (datetime.now() - folder_date).days
                    
                    if days_old > 7:
                        import shutil
                        shutil.rmtree(folder)
                        print(f"  清理旧备份: {folder.name} ({days_old} 天前)")
                except:
                    pass
    
    def _optimize_knowledge_base(self):
        """优化知识库"""
        # 合并相似的问题模式
        merged_patterns = []
        
        for pattern in self.problem_patterns:
            # 检查是否与已有模式相似
            similar = False
            
            for merged in merged_patterns:
                if self._patterns_are_similar(pattern, merged):
                    # 合并模式
                    merged.occurrence_count += pattern.occurrence_count
                    merged.last_seen = max(merged.last_seen, pattern.last_seen)
                    similar = True
                    break
            
            if not similar:
                merged_patterns.append(pattern)
        
        # 更新问题模式
        if len(merged_patterns) < len(self.problem_patterns):
            self.problem_patterns = merged_patterns
            self._save_knowledge_base()
            print(f"  优化知识库: 合并了 {len(self.problem_patterns) - len(merged_patterns)} 个相似模式")
    
    def _patterns_are_similar(self, pattern1: ProblemPattern, pattern2: ProblemPattern) -> bool:
        """检查两个问题模式是否相似"""
        # 简单的关键词相似性检查
        keywords1 = set(pattern1.description.lower().split())
        keywords2 = set(pattern2.description.lower().split())
        
        common_keywords = keywords1.intersection(keywords2)
        similarity = len(common_keywords) / max(len(keywords1), len(keywords2))
        
        return similarity > 0.6  # 60%相似度
    
    def _check_for_tool_updates(self):
        """检查工具更新"""
        # 检查是否有新版本的工具
        print(f"  检查工具更新...")
        # 这里可以添加检查GitHub或其他源的逻辑
    
    def _generate_maintenance_report(self):
        """生成维护报告"""
        report = {
            "maintenance_date": datetime.now().isoformat(),
            "ai_system_version": self.version,
            "knowledge_base_stats": {
                "problem_patterns": len(self.problem_patterns),
                "experience_lessons": len(self.experience_lessons),
                "framework_upgrades": len(self.framework_upgrades)
            },
            "backup_status": "正常",
            "optimization_performed": True,
            "next_maintenance": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        report_path = self.framework_dir / "ai_maintenance_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

def main():
    """主函数"""
    print("🤖 AI自进化审核框架启动...")
    
    # 创建AI系统
    ai_system = AISelfEvolvingAudit()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "audit" and len(sys.argv) > 2:
            # 审核技能
            skill_path = sys.argv[2]
            ai_system.audit_skill(skill_path)
            
        elif command == "maintenance":
            # 运行每日维护
            ai_system.run_daily_maintenance()
            
        elif command == "learn":
            # 手动学习模式
            print("进入学习模式...")
            # 这里可以添加交互式学习
            
        elif command == "upgrade":
            # 手动触发升级
            print("手动触发升级...")
            # 这里可以添加手动升级逻辑
            
        else:
            print(f"未知命令: {command}")
            print("可用命令: audit <技能路径>, maintenance, learn, upgrade")
    else:
        # 交互式模式
        print("\n交互式模式:")
        print("1. 审核技能")
        print("2. 运行每日维护")
        print("3. 查看系统状态")
        print("4. 退出")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "1":
            skill_path = input("请输入技能路径: ").strip()
            if skill_path:
                ai_system.audit_skill(skill_path)
        elif choice == "2":
            ai_system.run_daily_maintenance()
        elif choice == "3":
            print(f"\n系统状态:")
            print(f"版本: {ai_system.version}")
            print(f"问题模式: {len(ai_system.problem_patterns)} 个")
            print(f"经验教训: {len(ai_system.experience_lessons)} 个")
            print(f"框架升级: {len(ai_system.framework_upgrades)} 次")
        elif choice == "4":
            print("退出系统")
        else:
            print("无效选择")

if __name__ == "__main__":
    main()