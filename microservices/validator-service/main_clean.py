"""
企业级审核框架 - 验证服务（清洁版）
基础功能，无语法错误
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
class ValidationRequest(BaseModel):
    """验证请求模型"""
    skill_id: str = Field(..., description="技能ID")
    skill_path: str = Field(..., description="技能路径")
    validation_type: str = Field("full", description="验证类型")

class ValidationResult(BaseModel):
    """验证结果模型"""
    skill_id: str
    passed: bool
    score: float
    issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime

# 创建FastAPI应用
app = FastAPI(
    title="企业级验证服务",
    description="技能结构验证和合规检查服务",
    version="3.0.0"
)

# 内存存储
memory_store = {}

class SkillValidator:
    """技能验证器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.issues = []
        self.warnings = []
        self.score = 100.0
        self.results = {
            "passed": True,
            "score": 100.0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "metadata": {}
        }
    
    def validate_structure(self) -> None:
        """验证文件结构"""
        required_files = ["SKILL.md", "skill.py", "config.yaml", "package.json"]
        
        for file in required_files:
            file_path = self.skill_path / file
            if not file_path.exists():
                self.issues.append({
                    "type": "missing_file",
                    "file": file,
                    "severity": "high",
                    "message": f"Required file missing: {file}"
                })
                self.score -= 10.0
    
    def validate_config_yaml(self) -> None:
        """验证config.yaml"""
        config_path = self.skill_path / "config.yaml"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                self.results["metadata"]["config"] = {
                    "version": config.get("version", "unknown"),
                    "name": config.get("name", "unknown")
                }
                
            except Exception as e:
                self.warnings.append({
                    "type": "config_error",
                    "severity": "medium",
                    "message": f"Config YAML error: {str(e)}"
                })
    
    def validate_package_json(self) -> None:
        """验证package.json"""
        package_path = self.skill_path / "package.json"
        
        if package_path.exists():
            try:
                with open(package_path, 'r', encoding='utf-8') as f:
                    package = json.load(f)
                
                self.results["metadata"]["package"] = {
                    "name": package.get("name", "unknown"),
                    "version": package.get("version", "unknown")
                }
                
            except Exception as e:
                self.warnings.append({
                    "type": "package_error",
                    "severity": "medium",
                    "message": f"Package JSON error: {str(e)}"
                })
    
    def validate_skill_py(self) -> None:
        """验证skill.py"""
        skill_py_path = self.skill_path / "skill.py"
        
        if skill_py_path.exists():
            try:
                file_size = skill_py_path.stat().st_size
                self.results["metadata"]["skill_py"] = {
                    "size": file_size,
                    "hash": "placeholder"
                }
                
                # 检查基本结构
                with open(skill_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                required_patterns = [
                    ("class.*Skill", "Skill class definition"),
                    ("def handle_command", "handle_command method"),
                    ("def get_commands", "get_commands method")
                ]
                
                for pattern, description in required_patterns:
                    if not re.search(pattern, content):
                        self.warnings.append({
                            "type": "skill_structure",
                            "severity": "low",
                            "message": f"Missing in skill.py: {description}"
                        })
                
            except Exception as e:
                self.warnings.append({
                    "type": "skill_error",
                    "severity": "medium",
                    "message": f"Skill.py error: {str(e)}"
                })
    
    def generate_recommendations(self) -> None:
        """生成建议"""
        if self.issues:
            self.results["recommendations"].append("Fix the identified issues before publishing")
        
        if self.warnings:
            self.results["recommendations"].append("Address warnings to improve quality")
        
        self.results["recommendations"].append("Test skill functionality thoroughly")
        self.results["recommendations"].append("Review security declarations in config.yaml")
    
    def validate(self) -> Dict[str, Any]:
        """执行完整验证"""
        import re  # 在这里导入避免循环
        
        self.validate_structure()
        self.validate_config_yaml()
        self.validate_package_json()
        self.validate_skill_py()
        
        # 计算最终得分
        self.score = max(0.0, min(100.0, self.score))
        self.results["passed"] = self.score >= 70.0
        self.results["score"] = self.score
        self.results["issues"] = self.issues
        self.results["warnings"] = self.warnings
        
        self.generate_recommendations()
        
        return self.results

@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "validator-service",
        "version": "3.0.0",
        "status": "running",
        "port": 8001,
        "endpoints": {
            "validate": "POST /validate - 验证技能",
            "results": "GET /validate/{skill_id} - 获取结果",
            "health": "GET /health - 健康检查"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/validate")
async def validate_skill(request: ValidationRequest):
    """验证技能"""
    # 检查技能路径是否存在
    skill_path = Path(request.skill_path)
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail="Skill path not found")
    
    # 执行验证
    validator = SkillValidator(request.skill_path)
    results = validator.validate()
    
    # 存储结果到内存
    result_key = f"validation:{request.skill_id}"
    memory_store[result_key] = {
        "skill_id": request.skill_id,
        "passed": results["passed"],
        "score": results["score"],
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    return ValidationResult(
        skill_id=request.skill_id,
        passed=results["passed"],
        score=results["score"],
        issues=results["issues"],
        warnings=results["warnings"],
        recommendations=results["recommendations"],
        metadata=results["metadata"],
        timestamp=datetime.now()
    )

@app.get("/validate/{skill_id}")
async def get_validation_result(skill_id: str):
    """获取验证结果"""
    result_key = f"validation:{skill_id}"
    result = memory_store.get(result_key)
    
    if not result:
        raise HTTPException(status_code=404, detail="Validation result not found")
    
    return {
        "skill_id": skill_id,
        "passed": result["passed"],
        "score": result["score"],
        "timestamp": result["timestamp"],
        "results": result.get("results", {})
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("启动验证服务 (端口: 8001)")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)