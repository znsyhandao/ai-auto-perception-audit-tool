#!/usr/bin/env python3
"""
发布前清理器 v2.0 - 包含2026-04-03经验教训

2026-04-03 更新的经验教训：
1. 版本一致性检查 - 确保ZIP文件名与技能版本一致
2. 区分核心文件和临时文件 - 临时文件可以包含中文
3. 智能清理 - 保留审核报告等有用文件
4. 版本验证 - 创建ZIP前验证版本一致性
"""

import os
import sys
import re
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

class PreReleaseCleanerV2:
    """发布前清理器 v2.0"""
    
    def __init__(self, skill_dir):
        self.skill_dir = Path(skill_dir)
        self.cleanup_log = []
        self.warnings = []
        self.version_issues = []
        
        # 2026-04-03经验教训：区分不同类型的文件
        self.file_categories = {
            # 核心文件 - 必须100%英文，必须包含在ZIP中
            "core_files": [
                "skill.py",
                "SKILL.md",
                "README.md",
                "CHANGELOG.md",
                "requirements.txt",
                "config.yaml"
            ],
            
            # 审核文件 - 可以包含中文，不包含在ZIP中
            "audit_files": [
                "*_audit.py",
                "*_check.py",
                "*_verify.py",
                "*_report.md",
                "*_report.json",
                "cleanup_report.md",
                "FINAL_*.md",
                "PUBLISH_*.md"
            ],
            
            # 必须清理的文件和目录
            "cleanup_patterns": [
                # Python缓存
                "__pycache__",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".pytest_cache",
                ".mypy_cache",
                
                # 临时文件
                "*.tmp",
                "*.temp",
                "*.log",
                "*.bak",
                "*.backup",
                
                # 构建文件
                "build/",
                "dist/",
                "*.egg-info",
                
                # 版本控制
                ".git/",
                ".svn/",
                ".hg/",
                
                # 编辑器文件
                ".vscode/",
                ".idea/",
                "*.swp",
                "*.swo",
                
                # 其他
                "Thumbs.db",
                ".DS_Store",
                "desktop.ini"
            ]
        }
    
    def run_full_cleanup(self):
        """运行完整清理流程"""
        print("=" * 80)
        print("发布前清理器 v2.0 - 包含2026-04-03经验教训")
        print("=" * 80)
        print(f"清理目录: {self.skill_dir}")
        print(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        steps = [
            ("检查版本一致性", self.check_version_consistency),
            ("清理缓存文件", self.clean_cache_files),
            ("检查核心文件", self.check_core_files),
            ("创建ZIP包", self.create_zip_package),
            ("生成清理报告", self.generate_cleanup_report)
        ]
        
        all_passed = True
        
        for step_name, step_func in steps:
            print(f"\n[{steps.index((step_name, step_func)) + 1}/{len(steps)}] {step_name}")
            print("-" * 40)
            
            try:
                success, message = step_func()
                
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
                    all_passed = False
                    self.warnings.append(f"{step_name}: {message}")
                    
            except Exception as e:
                print(f"⚠️  步骤出错: {e}")
                all_passed = False
                self.warnings.append(f"{step_name}出错: {e}")
        
        # 总结
        print("\n" + "=" * 80)
        print("清理总结")
        print("=" * 80)
        
        if all_passed:
            print("🎉 清理完成！技能已准备好发布。")
            
            # 显示关键信息
            zip_files = list(self.skill_dir.glob("skill-v*.zip"))
            if zip_files:
                zip_file = zip_files[0]
                print(f"\n创建的ZIP包: {zip_file.name}")
                
                # 验证版本一致性
                skill_version = self._get_skill_version()
                if skill_version:
                    expected_name = f"skill-v{skill_version}.zip"
                    if zip_file.name == expected_name:
                        print(f"✅ ZIP文件名与版本一致: v{skill_version}")
                    else:
                        print(f"⚠️  ZIP文件名与版本不一致")
                        print(f"   技能版本: v{skill_version}")
                        print(f"   ZIP文件名: {zip_file.name}")
                        print(f"   期望文件名: {expected_name}")
        else:
            print(f"⚠️  清理过程中发现 {len(self.warnings)} 个问题:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        return all_passed
    
    def check_version_consistency(self):
        """检查版本一致性 - 2026-04-03关键经验教训"""
        print("检查版本一致性...")
        
        # 从skill.py提取版本
        skill_version = self._get_skill_version()
        
        if not skill_version:
            return False, "无法从skill.py提取版本"
        
        # 从CHANGELOG.md提取版本
        changelog_version = self._get_changelog_version()
        
        # 检查现有ZIP文件版本
        zip_files = list(self.skill_dir.glob("skill-v*.zip"))
        zip_versions = []
        
        for zip_file in zip_files:
            match = re.search(r'skill-v([\d.]+)\.zip', zip_file.name)
            if match:
                zip_versions.append((zip_file.name, match.group(1)))
        
        # 验证一致性
        issues = []
        
        if changelog_version and skill_version != changelog_version:
            issues.append(f"skill.py版本({skill_version})与CHANGELOG.md版本({changelog_version})不一致")
        
        for zip_name, zip_version in zip_versions:
            if zip_version != skill_version:
                issues.append(f"技能版本({skill_version})与ZIP文件版本({zip_name}: {zip_version})不一致")
        
        if issues:
            self.version_issues = issues
            return False, f"发现 {len(issues)} 个版本不一致问题"
        else:
            version_info = f"技能版本: v{skill_version}"
            if changelog_version:
                version_info += f", CHANGELOG版本: v{changelog_version}"
            if zip_versions:
                version_info += f", ZIP文件版本: v{zip_versions[0][1]}"
            
            return True, version_info
    
    def clean_cache_files(self):
        """清理缓存文件"""
        print("清理缓存文件...")
        
        total_cleaned = 0
        
        for pattern in self.file_categories["cleanup_patterns"]:
            if pattern.endswith("/"):  # 目录模式
                dir_pattern = pattern.rstrip("/")
                for dir_path in self.skill_dir.rglob(dir_pattern):
                    if dir_path.is_dir():
                        try:
                            shutil.rmtree(dir_path)
                            self.cleanup_log.append(f"删除目录: {dir_path.relative_to(self.skill_dir)}")
                            total_cleaned += 1
                        except Exception as e:
                            self.cleanup_log.append(f"删除目录失败 {dir_path}: {e}")
            else:  # 文件模式
                for file_path in self.skill_dir.rglob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            self.cleanup_log.append(f"删除文件: {file_path.relative_to(self.skill_dir)}")
                            total_cleaned += 1
                        except Exception as e:
                            self.cleanup_log.append(f"删除文件失败 {file_path}: {e}")
        
        if total_cleaned > 0:
            return True, f"清理了 {total_cleaned} 个缓存文件/目录"
        else:
            return True, "无缓存文件需要清理"
    
    def check_core_files(self):
        """检查核心文件"""
        print("检查核心文件...")
        
        missing_files = []
        present_files = []
        
        for core_file in self.file_categories["core_files"]:
            if (self.skill_dir / core_file).exists():
                present_files.append(core_file)
            else:
                missing_files.append(core_file)
        
        if missing_files:
            return False, f"缺少 {len(missing_files)} 个核心文件: {', '.join(missing_files)}"
        else:
            return True, f"所有 {len(present_files)} 个核心文件都存在"
    
    def create_zip_package(self):
        """创建ZIP包 - 2026-04-03关键经验教训"""
        print("创建ZIP包...")
        
        # 获取技能版本
        skill_version = self._get_skill_version()
        
        if not skill_version:
            return False, "无法获取技能版本，无法创建ZIP包"
        
        # 删除旧的ZIP文件
        old_zips = list(self.skill_dir.glob("skill-v*.zip"))
        for old_zip in old_zips:
            try:
                old_zip.unlink()
                self.cleanup_log.append(f"删除旧ZIP文件: {old_zip.name}")
            except Exception as e:
                self.cleanup_log.append(f"删除旧ZIP文件失败 {old_zip}: {e}")
        
        # 创建新的ZIP文件名（确保版本一致）
        zip_filename = f"skill-v{skill_version}.zip"
        zip_path = self.skill_dir / zip_filename
        
        # 收集要添加到ZIP的文件（只包含核心文件）
        files_to_zip = []
        for core_file in self.file_categories["core_files"]:
            file_path = self.skill_dir / core_file
            if file_path.exists():
                files_to_zip.append(file_path)
        
        if not files_to_zip:
            return False, "没有核心文件可以添加到ZIP包"
        
        # 创建ZIP文件
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in files_to_zip:
                    arcname = file_path.name
                    zf.write(file_path, arcname)
                    self.cleanup_log.append(f"添加到ZIP: {arcname}")
            
            # 验证ZIP文件
            zip_size = zip_path.stat().st_size / 1024  # KB
            
            return True, f"创建ZIP包: {zip_filename} ({len(files_to_zip)} 个文件, {zip_size:.1f}KB)"
            
        except Exception as e:
            return False, f"创建ZIP包失败: {e}"
    
    def generate_cleanup_report(self):
        """生成清理报告"""
        print("生成清理报告...")
        
        report_content = f"""# 发布前清理报告 v2.0

## 清理信息
- **清理目录**: {self.skill_dir}
- **清理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **清理器版本**: 2.0 (包含2026-04-03经验教训)

## 2026-04-03经验教训
1. **版本一致性** - ZIP文件名必须与技能版本一致
2. **文件分类** - 区分核心文件（必须英文）和临时文件（可含中文）
3. **智能清理** - 保留有用的审核报告
4. **版本验证** - 创建ZIP前验证所有版本一致

## 清理日志
"""
        
        if self.cleanup_log:
            for log_entry in self.cleanup_log:
                report_content += f"- {log_entry}\n"
        else:
            report_content += "无清理操作\n"
        
        # 版本信息
        skill_version = self._get_skill_version()
        if skill_version:
            report_content += f"\n## 版本信息\n"
            report_content += f"- **技能版本**: v{skill_version}\n"
            
            changelog_version = self._get_changelog_version()
            if changelog_version:
                report_content += f"- **CHANGELOG版本**: v{changelog_version}\n"
            
            zip_files = list(self.skill_dir.glob("skill-v*.zip"))
            if zip_files:
                zip_file = zip_files[0]
                report_content += f"- **ZIP文件**: {zip_file.name}\n"
                
                # 检查版本一致性
                expected_name = f"skill-v{skill_version}.zip"
                if zip_file.name == expected_name:
                    report_content += f"- **版本一致性**: ✅ 匹配\n"
                else:
                    report_content += f"- **版本一致性**: ❌ 不匹配\n"
                    report_content += f"  期望: {expected_name}\n"
                    report_content += f"  实际: {zip_file.name}\n"
        
        # 警告信息
        if self.warnings:
            report_content += f"\n## 警告信息\n"
            for warning in self.warnings:
                report_content += f"- {warning}\n"
        
        # 版本问题
        if self.version_issues:
            report_content += f"\n## 版本不一致问题\n"
            for issue in self.version_issues:
                report_content += f"- {issue}\n"
        
        # 文件状态
        report_content += f"\n## 文件状态\n"
        
        # 核心文件
        core_present = []
        core_missing = []
        
        for core_file in self.file_categories["core_files"]:
            if (self.skill_dir / core_file).exists():
                core_present.append(core_file)
            else:
                core_missing.append(core_file)
        
        report_content += f"### 核心文件 ({len(core_present)}/{len(self.file_categories['core_files'])} 存在)\n"
        if core_present:
            for file in core_present:
                report_content += f"- ✅ {file}\n"
        if core_missing:
            for file in core_missing:
                report_content += f"- ❌ {file} (缺失)\n"
        
        report_content += f"\n### 审核文件 (不包含在ZIP中)\n"
        audit_files = []
        for pattern in self.file_categories["audit_files"]:
            for file in self.skill_dir.glob(pattern):
                if file.is_file():
                    audit_files.append(file.name)
        
        if audit_files:
            for file in sorted(set(audit_files))[:10]:  # 显示前10个
                report_content += f"- 📝 {file}\n"
            if len(audit_files) > 10:
                report_content += f"- ... 还有 {len(audit_files)-10} 个文件\n"
        else:
            report_content += "无审核文件\n"
        
        report_content += f"\n## 建议\n"
        
        if self.warnings or self.version_issues:
            report_content += "⚠️ 请修复发现的问题后重新运行清理。\n"
        else:
            report_content += "✅ 清理完成，技能已准备好发布。\n"
        
        report_content += "\n---\n"
        report_content += "*本报告由发布前清理器 v2.0 生成*\n"
        report_content += "*包含2026-04-03经验教训*\n"
        
        # 保存报告
        report_path = self.skill_dir / "cleanup_report_v2.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return True, f"清理报告已生成: {report_path}"
    
    # ==================== 辅助函数 ====================
    
    def _get_skill_version(self):
        """从skill.py提取版本"""
        skill_file = self.skill_dir / "skill.py"
        
        if not skill_file.exists():
            return None
        
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'self\.version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
            
            return None
        except:
            return None
    
    def _get_changelog_version(self):
        """从CHANGELOG.md提取版本"""
        changelog_file = self.skill_dir / "CHANGELOG.md"
        
        if not changelog_file.exists():
            return None
        
        try:
            with open(changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'\[([\d.]+)\]', content)
            if match:
                return match.group(1)
            
            return None
        except:
            return None

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python pre_release_cleaner_v2.py <技能目录>")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    
    if not Path(skill_dir).exists():
        print(f"错误: 目录不存在: {skill_dir}")
        sys.exit(1)
    
    # 运行清理
    cleaner = PreReleaseCleanerV2(skill_dir)
    success = cleaner.run_full_cleanup()
    
    # 返回退出代码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()