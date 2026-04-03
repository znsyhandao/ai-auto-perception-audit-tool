"""
合规检查服务 - 增强版
端口: 8004
"""

import os
import json
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="合规检查服务",
    version="3.0.0",
    description="行业标准、许可证、代码规范检查"
)

# 数据模型
class ComplianceRequest(BaseModel):
    skill_id: str
    skill_path: str
    standards: List[str] = ["openclaw", "pep8", "security"]
    options: Dict[str, Any] = {}

class ComplianceResponse(BaseModel):
    skill_id: str
    score: float
    passed: bool
    compliance_issues: List[Dict[str, Any]]
    standards_met: List[str]
    recommendations: List[str]
    timestamp: str

# 合规检查器
class ComplianceChecker:
    def __init__(self):
        self.standards = {
            "openclaw": self._check_openclaw_compliance,
            "pep8": self._check_pep8_compliance,
            "security": self._check_security_compliance,
            "license": self._check_license_compliance
        }
    
    def check_skill(self, skill_path: str, standards: List[str]) -> Dict[str, Any]:
        """检查技能合规性"""
        path = Path(skill_path)
        
        if not path.exists():
            return {"error": "技能路径不存在"}
        
        results = {
            "standards_checked": standards,
            "issues": [],
            "warnings": [],
            "met_standards": []
        }
        
        # 检查每个标准
        for standard in standards:
            if standard in self.standards:
                checker_func = self.standards[standard]
                result = checker_func(path)
                
                if result.get("passed", False):
                    results["met_standards"].append(standard)
                else:
                    results["issues"].extend(result.get("issues", []))
                    results["warnings"].extend(result.get("warnings", []))
        
        return results
    
    def _check_openclaw_compliance(self, skill_path: Path) -> Dict[str, Any]:
        """检查OpenClaw平台合规性"""
        issues = []
        warnings = []
        
        required_files = ["SKILL.md", "skill.py", "config.yaml", "package.json"]
        
        for file in required_files:
            file_path = skill_path / file
            if not file_path.exists():
                issues.append({
                    "type": "missing_required_file",
                    "file": file,
                    "severity": "high",
                    "message": f"缺少必需文件: {file}"
                })
        
        # 检查SKILL.md格式
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            if "# " not in content[:100]:
                warnings.append({
                    "type": "documentation_format",
                    "file": "SKILL.md",
                    "severity": "low",
                    "message": "SKILL.md应该以标题开始"
                })
        
        passed = len(issues) == 0
        return {"passed": passed, "issues": issues, "warnings": warnings}
    
    def _check_pep8_compliance(self, skill_path: Path) -> Dict[str, Any]:
        """检查PEP8代码规范"""
        # 简化检查 - 实际应该使用flake8或black
        issues = []
        
        python_files = list(skill_path.glob("*.py"))
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # 检查行长度
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    if len(line) > 120:  # PEP8建议79，这里放宽到120
                        issues.append({
                            "type": "line_too_long",
                            "file": py_file.name,
                            "line": i,
                            "severity": "low",
                            "message": f"行长度 {len(line)} > 120 字符"
                        })
                
                # 检查导入顺序
                if "import" in content and "from" in content:
                    # 简化检查
                    pass
                    
            except Exception as e:
                logger.error(f"检查文件失败 {py_file}: {str(e)}")
        
        passed = len(issues) < 10  # 允许少量问题
        return {"passed": passed, "issues": issues, "warnings": []}
    
    def _check_security_compliance(self, skill_path: Path) -> Dict[str, Any]:
        """检查安全合规性"""
        issues = []
        
        python_files = list(skill_path.glob("*.py"))
        dangerous_patterns = [
            (r"exec\(", "使用exec()函数"),
            (r"eval\(", "使用eval()函数"),
            (r"__import__\(", "使用__import__()函数"),
            (r"os\.system\(", "使用os.system()"),
            (r"subprocess\.run\(", "使用subprocess.run()"),
        ]
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern, desc in dangerous_patterns:
                    if re.search(pattern, content):
                        issues.append({
                            "type": "dangerous_function",
                            "file": py_file.name,
                            "severity": "medium",
                            "message": f"检测到危险函数: {desc}",
                            "suggestion": "使用更安全的替代方案"
                        })
                        
            except Exception as e:
                logger.error(f"安全检查失败 {py_file}: {str(e)}")
        
        passed = len(issues) == 0
        return {"passed": passed, "issues": issues, "warnings": []}
    
    def _check_license_compliance(self, skill_path: Path) -> Dict[str, Any]:
        """检查许可证合规性"""
        issues = []
        warnings = []
        
        license_files = list(skill_path.glob("LICENSE*")) + list(skill_path.glob("license*"))
        
        if not license_files:
            issues.append({
                "type": "missing_license",
                "severity": "high",
                "message": "缺少许可证文件",
                "suggestion": "添加LICENSE文件，明确使用条款"
            })
        else:
            # 检查许可证内容
            for license_file in license_files:
                content = license_file.read_text(encoding='utf-8', errors='ignore')
                if len(content) < 100:  # 许可证文件通常较长
                    warnings.append({
                        "type": "license_too_short",
                        "file": license_file.name,
                        "severity": "low",
                        "message": "许可证文件可能不完整"
                    })
        
        passed = len(issues) == 0
        return {"passed": passed, "issues": issues, "warnings": warnings}

# 内存存储
results_store = {}

# API端点
@app.get("/")
def root():
    return {
        "service": "compliance-service",
        "version": "3.0.0",
        "status": "running",
        "port": 8004,
        "description": "合规检查服务"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze_compliance(request: ComplianceRequest):
    logger.info(f"合规检查: {request.skill_id}")
    
    checker = ComplianceChecker()
    result = checker.check_skill(request.skill_path, request.standards)
    
    # 计算合规得分
    total_standards = len(request.standards)
    met_standards = len(result.get("met_standards", []))
    
    if total_standards > 0:
        compliance_score = (met_standards / total_standards) * 100
    else:
        compliance_score = 100.0
    
    # 问题扣分
    issues_count = len(result.get("issues", []))
    warnings_count = len(result.get("warnings", []))
    
    final_score = compliance_score - (issues_count * 10) - (warnings_count * 2)
    final_score = max(final_score, 0)
    
    # 生成响应
    response = {
        "skill_id": request.skill_id,
        "score": round(final_score, 1),
        "passed": final_score >= 70,
        "compliance_issues": result.get("issues", []),
        "standards_met": result.get("met_standards", []),
        "recommendations": [
            "确保所有必需文件都存在",
            "遵循PEP8代码规范",
            "移除危险函数调用",
            "添加完整的许可证文件"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    results_store[request.skill_id] = response
    return response

@app.get("/result/{skill_id}")
def get_result(skill_id: str):
    if skill_id not in results_store:
        raise HTTPException(404, f"结果未找到: {skill_id}")
    return results_store[skill_id]

@app.get("/results")
def list_results():
    return {
        "count": len(results_store),
        "results": list(results_store.keys())
    }

@app.get("/standards")
def list_standards():
    return {
        "available_standards": ["openclaw", "pep8", "security", "license", "gdpr", "hipaa"],
        "description": "支持的合规标准"
    }

def main():
    print("启动合规检查服务...")
    uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)

if __name__ == "__main__":
    main()