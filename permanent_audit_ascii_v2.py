    def check_filename_version_consistency(self):
        """文件名版本一致性检查 - 2026-04-03新增"""
        evidence = {}
        
        # 从skill.py提取版本
        skill_version = self._extract_version_from_skill()
        if not skill_version:
            print(f"  [FAIL] 无法从skill.py提取版本")
            return False, evidence
        
        # 检查ZIP文件名
        expected_zip_name = f"skill-v{skill_version}.zip"
        zip_files = list(self.skill_path.glob("skill-v*.zip"))
        
        if not zip_files:
            print(f"  [FAIL] 未找到ZIP文件，期望: {expected_zip_name}")
            evidence["expected"] = expected_zip_name
            evidence["found"] = False
            return False, evidence
        
        actual_zip_name = zip_files[0].name
        evidence["expected"] = expected_zip_name
        evidence["actual"] = actual_zip_name
        
        if actual_zip_name == expected_zip_name:
            print(f"  [OK] ZIP文件名正确: {actual_zip_name}")
            evidence["matches"] = True
            return True, evidence
        else:
            print(f"  [FAIL] ZIP文件名不匹配:")
            print(f"    期望: {expected_zip_name}")
            print(f"    实际: {actual_zip_name}")
            evidence["matches"] = False
            return False, evidence
    
    def generate_audit_report(self):
        """生成审核报告"""
        report_data = {
            "audit_framework": "Permanent Audit Framework v2.0",
            "audit_date": datetime.now().isoformat(),
            "skill_directory": str(self.skill_path),
            "lessons_applied": self.lessons_applied,
            "results": self.results,
            "evidence": self.evidence,
            "summary": {
                "total_checks": len(self.results),
                "passed_checks": len([r for r in self.results if r["status"] == "passed"]),
                "failed_checks": len([r for r in self.results if r["status"] == "failed"]),
                "error_checks": len([r for r in self.results if r["status"] == "error"])
            }
        }
        
        # 保存JSON报告
        json_path = self.skill_path / "permanent_audit_v2_report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # 生成文本报告
        text_report = self._generate_text_report(report_data)
        text_path = self.skill_path / "permanent_audit_v2_report.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        print(f"\n审核报告已保存:")
        print(f"  JSON: {json_path}")
        print(f"  文本: {text_path}")
        
        return True
    
    def _generate_text_report(self, report_data):
        """生成文本报告"""
        report = "=" * 80 + "\n"
        report += "永久审核框架 v2.0 报告\n"
        report += "=" * 80 + "\n\n"
        
        report += f"技能目录: {report_data['skill_directory']}\n"
        report += f"审核时间: {report_data['audit_date']}\n"
        report += f"审核框架: {report_data['audit_framework']}\n\n"
        
        report += "包含的经验教训 (2026-04-03):\n"
        for lesson in report_data['lessons_applied']:
            report += f"  • {lesson}\n"
        
        report += "\n" + "=" * 80 + "\n"
        report += "检查结果\n"
        report += "=" * 80 + "\n\n"
        
        for result in report_data['results']:
            status_icon = "[PASS]" if result["status"] == "passed" else "[FAIL]" if result["status"] == "failed" else "[ERROR]"
            report += f"{status_icon} {result['check_name']}\n"
        
        report += "\n" + "=" * 80 + "\n"
        report += "审核总结\n"
        report += "=" * 80 + "\n\n"
        
        summary = report_data['summary']
        report += f"总检查数: {summary['total_checks']}\n"
        report += f"通过检查: {summary['passed_checks']}\n"
        report += f"失败检查: {summary['failed_checks']}\n"
        report += f"错误检查: {summary['error_checks']}\n\n"
        
        if summary['failed_checks'] == 0 and summary['error_checks'] == 0:
            report += "✅ 所有检查通过！技能已准备好发布。\n"
        else:
            report += "⚠️ 请修复发现的问题后重新运行审核。\n"
        
        report += "\n" + "=" * 80 + "\n"
        report += "关键发现\n"
        report += "=" * 80 + "\n\n"
        
        # 版本一致性
        if "版本一致性检查" in self.evidence:
            evidence = self.evidence["版本一致性检查"]
            if evidence.get("consistent", False):
                report += f"✅ 版本一致性: 通过 (版本: {evidence.get('version', '未知')})\n"
            else:
                report += f"❌ 版本一致性: 失败\n"
                if "sources" in evidence:
                    for source, version in evidence["sources"].items():
                        report += f"    {source}: {version}\n"
        
        # 文件名版本一致性
        if "文件名版本一致性" in self.evidence:
            evidence = self.evidence["文件名版本一致性"]
            if evidence.get("matches", False):
                report += f"✅ 文件名版本一致性: 通过\n"
                report += f"   ZIP文件: {evidence.get('actual', '未知')}\n"
            else:
                report += f"❌ 文件名版本一致性: 失败\n"
                report += f"   期望: {evidence.get('expected', '未知')}\n"
                report += f"   实际: {evidence.get('actual', '未知')}\n"
        
        # 英文合规
        if "英文合规检查" in self.evidence:
            evidence = self.evidence["英文合规检查"]
            if evidence.get("issues"):
                report += f"❌ 英文合规: 失败\n"
                for issue in evidence["issues"]:
                    report += f"    {issue}\n"
            else:
                report += f"✅ 英文合规: 通过\n"
                report += f"   检查了 {evidence.get('core_files_checked', 0)} 个核心文件\n"
        
        report += "\n" + "=" * 80 + "\n"
        report += "建议\n"
        report += "=" * 80 + "\n\n"
        
        if summary['failed_checks'] > 0:
            report += "1. 修复版本不一致问题（确保skill.py、CHANGELOG.md和ZIP文件名版本一致）\n"
            report += "2. 确保所有核心文件100%英文\n"
            report += "3. 移除所有危险函数和网络访问代码\n"
            report += "4. 重新运行审核框架验证修复\n"
        else:
            report += "1. 技能已通过所有审核检查\n"
            report += "2. 可以安全发布到ClawHub\n"
            report += "3. 建议在发布前进行最终功能测试\n"
        
        report += "\n" + "=" * 80 + "\n"
        report += "报告结束\n"
        report += "=" * 80 + "\n"
        
        return report
    
    # ==================== 辅助函数 ====================
    
    def _extract_version_from_skill(self):
        """从skill.py提取版本"""
        skill_file = self.skill_path / "skill.py"
        
        if not skill_file.exists():
            return None
        
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找版本定义
            patterns = [
                r'self\.version\s*=\s*["\']([^"\']+)["\']',
                r'version\s*=\s*["\']([^"\']+)["\']',
                r'VERSION\s*=\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
            
            return None
        except:
            return None
    
    def _extract_version_from_changelog(self):
        """从CHANGELOG.md提取版本"""
        changelog_file = self.skill_path / "CHANGELOG.md"
        
        if not changelog_file.exists():
            return None
        
        try:
            with open(changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找最新版本
            patterns = [
                r'\[([\d.]+)\]',  # [1.1.0]
                r'## \[([\d.]+)\]',  ## [1.1.0]
                r'版本\s*([\d.]+)',  # 版本 1.1.0
                r'v([\d.]+)\s'  # v1.1.0
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
            
            return None
        except:
            return None
    
    def _extract_version_from_zip(self):
        """从ZIP文件名提取版本"""
        zip_files = list(self.skill_path.glob("skill-v*.zip"))
        
        if not zip_files:
            return None, None
        
        zip_file = zip_files[0]
        match = re.search(r'skill-v([\d.]+)\.zip', zip_file.name)
        
        if match:
            return match.group(1), zip_file.name
        else:
            return None, zip_file.name
    
    def _count_chinese_characters(self, filepath):
        """统计文件中的中文字符数量"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 匹配中文字符
            chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
            matches = chinese_pattern.findall(content)
            
            return len(matches)
            
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(filepath, 'r', encoding='gbk') as f:
                    content = f.read()
                
                chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
                matches = chinese_pattern.findall(content)
                
                return len(matches)
                
            except:
                return -1  # 无法读取
        except:
            return -1  # 其他错误

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python permanent_audit_ascii_v2.py <技能目录>")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    
    if not Path(skill_dir).exists():
        print(f"错误: 目录不存在: {skill_dir}")
        sys.exit(1)
    
    # 运行审核
    auditor = PermanentAuditV2(skill_dir)
    success = auditor.run_full_audit()
    
    # 返回退出代码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()