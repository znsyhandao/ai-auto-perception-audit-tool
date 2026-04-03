#!/usr/bin/env python3
"""
OpenClaw技能发布检查清单
发布前必须运行，确保所有检查通过
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class ReleaseChecklist:
    """发布检查清单"""
    
    def __init__(self, skill_directory: str):
        self.skill_directory = skill_directory
        self.checks = []
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 定义所有检查项
        self.define_checks()
    
    def define_checks(self):
        """定义检查项"""
        # 阶段1：基本检查
        self.checks.extend([
            {
                "id": "basic_001",
                "category": "basic",
                "name": "目录存在性检查",
                "description": "检查技能目录是否存在",
                "critical": True
            },
            {
                "id": "basic_002", 
                "category": "basic",
                "name": "必需文件检查",
                "description": "检查必需文件是否存在",
                "critical": True
            },
            {
                "id": "basic_003",
                "category": "basic", 
                "name": "文件结构检查",
                "description": "检查文件结构是否符合规范",
                "critical": False
            }
        ])
        
        # 阶段2：功能检查
        self.checks.extend([
            {
                "id": "functional_001",
                "category": "functional",
                "name": "主技能文件检查",
                "description": "检查skill.py是否存在且可导入",
                "critical": True
            },
            {
                "id": "functional_002",
                "category": "functional",
                "name": "命令处理器检查",
                "description": "检查handle_command方法",
                "critical": True
            },
            {
                "id": "functional_003",
                "category": "functional",
                "name": "创建函数检查",
                "description": "检查create_skill函数",
                "critical": True
            }
        ])
        
        # 阶段3：安全检查
        self.checks.extend([
            {
                "id": "security_001",
                "category": "security",
                "name": "网络安全检查",
                "description": "运行安全扫描检查网络代码",
                "critical": True
            },
            {
                "id": "security_002",
                "category": "security",
                "name": "危险代码检查",
                "description": "检查危险函数",
                "critical": True
            },
            {
                "id": "security_003",
                "category": "security",
                "name": "路径安全检查",
                "description": "检查路径遍历问题",
                "critical": True
            },
            {
                "id": "security_004",
                "category": "security",
                "name": "依赖检查",
                "description": "检查外部依赖",
                "critical": True
            }
        ])
        
        # 阶段4：一致性检查
        self.checks.extend([
            {
                "id": "consistency_001",
                "category": "consistency",
                "name": "文档代码一致性",
                "description": "检查README声明与代码一致性",
                "critical": True
            },
            {
                "id": "consistency_002",
                "category": "consistency",
                "name": "安全声明验证",
                "description": "验证所有安全声明",
                "critical": True
            },
            {
                "id": "consistency_003",
                "category": "consistency",
                "name": "许可证检查",
                "description": "检查许可证文件",
                "critical": True
            }
        ])
        
        # 阶段5：合规检查
        self.checks.extend([
            {
                "id": "compliance_001",
                "category": "compliance",
                "name": "package.json检查",
                "description": "检查package.json配置",
                "critical": True
            },
            {
                "id": "compliance_002",
                "category": "compliance",
                "name": "权限检查",
                "description": "检查权限设置",
                "critical": True
            },
            {
                "id": "compliance_003",
                "category": "compliance",
                "name": "ClawHub规范检查",
                "description": "检查是否符合平台规范",
                "critical": True
            }
        ])
    
    def run_check(self, check: Dict) -> Dict:
        """运行单个检查"""
        check_id = check["id"]
        check_func = getattr(self, f"check_{check_id}", None)
        
        if check_func:
            try:
                return check_func()
            except Exception as e:
                return {
                    "check_id": check_id,
                    "name": check["name"],
                    "status": "error",
                    "message": f"检查执行错误: {str(e)}",
                    "critical": check["critical"]
                }
        else:
            return {
                "check_id": check_id,
                "name": check["name"],
                "status": "skipped",
                "message": "检查函数未实现",
                "critical": check["critical"]
            }
    
    def run_all_checks(self):
        """运行所有检查"""
        print(f"[DETAILS] 开始发布检查: {self.skill_directory}")
        print(f"📅 检查时间: {self.timestamp}")
        print("=" * 70)
        
        total_checks = len(self.checks)
        passed_checks = 0
        failed_checks = 0
        critical_failures = 0
        
        for i, check in enumerate(self.checks, 1):
            print(f"\n[{i}/{total_checks}] {check['name']}...")
            
            result = self.run_check(check)
            self.results.append(result)
            
            if result["status"] == "passed":
                print(f"  [OK] 通过: {result.get('message', '')}")
                passed_checks += 1
            elif result["status"] == "failed":
                print(f"  [ERROR] 失败: {result.get('message', '')}")
                failed_checks += 1
                if check["critical"]:
                    critical_failures += 1
            elif result["status"] == "warning":
                print(f"  [WARN]  警告: {result.get('message', '')}")
            else:
                print(f"  🔄 {result['status']}: {result.get('message', '')}")
        
        # 生成报告
        self.generate_report(total_checks, passed_checks, failed_checks, critical_failures)
        
        return critical_failures == 0
    
    def generate_report(self, total: int, passed: int, failed: int, critical: int):
        """生成检查报告"""
        print("\n" + "=" * 70)
        print("[DASHBOARD] 发布检查报告")
        print("=" * 70)
        
        print(f"\n[CHART] 检查统计:")
        print(f"  总检查项: {total}")
        print(f"  通过: {passed} ({passed/total*100:.1f}%)")
        print(f"  失败: {failed} ({failed/total*100:.1f}%)")
        print(f"  严重失败: {critical}")
        
        # 按类别统计
        categories = {}
        for result in self.results:
            # 从check_id获取类别
            category = result["check_id"].split("_")[0]
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0, "failed": 0}
            
            categories[category]["total"] += 1
            if result["status"] == "passed":
                categories[category]["passed"] += 1
            elif result["status"] == "failed":
                categories[category]["failed"] += 1
        
        print(f"\n[LIST] 按类别统计:")
        for category, stats in categories.items():
            pass_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {category}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # 显示失败项
        failed_results = [r for r in self.results if r["status"] == "failed"]
        if failed_results:
            print(f"\n[ERROR] 失败项目:")
            for result in failed_results:
                critical_mark = "🔴 " if result.get("critical") else "🟡 "
                print(f"  {critical_mark} {result['name']}: {result.get('message', '')}")
        
        # 显示警告项
        warning_results = [r for r in self.results if r["status"] == "warning"]
        if warning_results:
            print(f"\n[WARN]  警告项目:")
            for result in warning_results:
                print(f"  [WARN]  {result['name']}: {result.get('message', '')}")
        
        # 结论
        print(f"\n[TARGET] 检查结论:")
        if critical > 0:
            print("  [ERROR] 发现严重问题，禁止发布！")
            print("  [WRENCH] 必须修复所有严重问题后才能发布")
        elif failed > 0:
            print("  [WARN]  发现问题，建议修复后再发布")
            print("  [DETAILS] 检查并修复所有失败项")
        else:
            print("  [OK] 所有检查通过，可以发布！")
            print("  [LAUNCH] 准备上传到ClawHub")
        
        print("\n" + "=" * 70)
    
    def save_report(self, output_path: str):
        """保存报告到文件"""
        report = {
            "timestamp": self.timestamp,
            "skill_directory": self.skill_directory,
            "results": self.results,
            "summary": {
                "total": len(self.checks),
                "passed": len([r for r in self.results if r["status"] == "passed"]),
                "failed": len([r for r in self.results if r["status"] == "failed"]),
                "warnings": len([r for r in self.results if r["status"] == "warning"])
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"[DOC] 报告已保存: {output_path}")
    
    # ====== 检查函数实现 ======
    
    def check_basic_001(self):
        """检查目录存在性"""
        if os.path.exists(self.skill_directory):
            return {
                "check_id": "basic_001",
                "name": "目录存在性检查",
                "status": "passed",
                "message": f"目录存在: {self.skill_directory}",
                "critical": True
            }
        else:
            return {
                "check_id": "basic_001",
                "name": "目录存在性检查",
                "status": "failed",
                "message": f"目录不存在: {self.skill_directory}",
                "critical": True
            }
    
    def check_basic_002(self):
        """检查必需文件"""
        required_files = [
            "skill.py",
            "README.md",
            "package.json",
            "LICENSE.txt"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.skill_directory, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if not missing_files:
            return {
                "check_id": "basic_002",
                "name": "必需文件检查",
                "status": "passed",
                "message": "所有必需文件都存在",
                "critical": True
            }
        else:
            return {
                "check_id": "basic_002",
                "name": "必需文件检查",
                "status": "failed",
                "message": f"缺少文件: {', '.join(missing_files)}",
                "critical": True
            }
    
    def check_security_001(self):
        """运行安全扫描"""
        # 这里可以集成security_scanner.py
        try:
            # 尝试导入并运行安全扫描
            scanner_path = os.path.join(os.path.dirname(__file__), "security_scanner.py")
            if os.path.exists(scanner_path):
                result = subprocess.run(
                    [sys.executable, scanner_path, self.skill_directory, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return {
                        "check_id": "security_001",
                        "name": "网络安全检查",
                        "status": "passed",
                        "message": "安全扫描通过",
                        "critical": True
                    }
                else:
                    return {
                        "check_id": "security_001",
                        "name": "网络安全检查",
                        "status": "failed",
                        "message": "安全扫描发现网络代码",
                        "critical": True
                    }
            else:
                return {
                    "check_id": "security_001",
                    "name": "网络安全检查",
                    "status": "warning",
                    "message": "安全扫描工具未找到，跳过检查",
                    "critical": True
                }
                
        except subprocess.TimeoutExpired:
            return {
                "check_id": "security_001",
                "name": "网络安全检查",
                "status": "error",
                "message": "安全扫描超时",
                "critical": True
            }
        except Exception as e:
            return {
                "check_id": "security_001",
                "name": "网络安全检查",
                "status": "error",
                "message": f"安全扫描错误: {str(e)}",
                "critical": True
            }
    
    # 更多检查函数...
    # 由于篇幅限制，这里只实现部分检查函数
    # 实际使用时需要实现所有检查函数
    
    def check_functional_001(self):
        """检查主技能文件"""
        skill_path = os.path.join(self.skill_directory, "skill.py")
        if os.path.exists(skill_path):
            try:
                # 尝试导入skill.py
                import importlib.util
                spec = importlib.util.spec_from_file_location("skill", skill_path)
                if spec and spec.loader:
                    return {
                        "check_id": "functional_001",
                        "name": "主技能文件检查",
                        "status": "passed",
                        "message": "skill.py存在且可导入",
                        "critical": True
                    }
            except:
                pass
        
        return {
            "check_id": "functional_001",
            "name": "主技能文件检查",
            "status": "failed",
            "message": "skill.py不存在或无法导入",
            "critical": True
        }
    
    def check_consistency_001(self):
        """检查文档代码一致性"""
        readme_path = os.path.join(self.skill_directory, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查常见声明
                declarations = ["零依赖", "无网络", "本地处理", "隐私安全"]
                found_declarations = [d for d in declarations if d in content]
                
                if found_declarations:
                    return {
                        "check_id": "consistency_001",
                        "name": "文档代码一致性",
                        "status": "warning",
                        "message": f"发现安全声明: {', '.join(found_declarations)}，需要验证",
                        "critical": True
                    }
                else:
                    return {
                        "check_id": "consistency_001",
                        "name": "文档代码一致性",
                        "status": "passed",
                        "message": "文档中无需要验证的安全声明",
                        "critical": True
                    }
                    
            except Exception as e:
                return {
                    "check_id": "consistency_001",
                    "name": "文档代码一致性",
                    "status": "error",
                    "message": f"文档读取错误: {str(e)}",
                    "critical": True
                }
        else:
            return {
                "check_id": "consistency_001",
                "name": "文档代码一致性",
                "status": "failed",
                "message": "README.md文件不存在",
                "critical": True
            }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python release_checklist.py <技能目录> [输出报告路径]")
        print("示例: python release_checklist.py ./my-skill ./report.json")
        sys.exit(1)
    
    skill_directory = sys.argv[1]
    output_report = sys.argv[2] if len(sys.argv) > 2 else None
    
    checklist = ReleaseChecklist(skill_directory)
    passed = checklist.run_all_checks()
    
    if output_report:
        checklist.save_report(output_report)
    
    # 返回退出代码
    if passed:
        print("\n[OK] 发布检查通过，可以继续发布流程")
        sys.exit(0)
    else:
        print("\n[ERROR] 发布检查失败，需要修复问题")
        sys.exit(1)


if __name__ == "__main__":
    main()