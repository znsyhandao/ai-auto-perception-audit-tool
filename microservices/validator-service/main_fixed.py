"""
企业级审核框架 - 验证服务（修复版）
不使用Redis，使用内存存储
"""

import os
import json
import logging
import hashlib
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
    validation_type: str = Field("full", description="验证类型: basic/full")

class ValidationResult(BaseModel):
    """验证结果模型"""
    skill_id: str = Field(..., description="技能ID")
    passed: bool = Field(..., description="是否通过")
    score: float = Field(..., description="验证得分(0-100)")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="问题列表")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="警告列表")
    recommendations: List[str] = Field(default_factory=list, description="建议列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="状态: healthy/unhealthy")
    service: str = Field("validator-service", description="服务名称")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

# 应用初始化
app = FastAPI(
    title="企业级审核框架 - 验证服务（修复版）",
    description="OpenClaw技能基础验证服务 - 内存存储版本",
    version="3.0.1"
)

# 内存存储（替代Redis）
memory_store = {}

class SkillValidator:
    """技能验证器"""
    
    REQUIRED_FILES = ["SKILL.md", "skill.py", "config.yaml", "package.json"]
    RECOMMENDED_FILES = ["README.md", "CHANGELOG.md", "LICENSE.txt", "requirements.txt"]
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.results = {
            "passed": True,
            "score": 0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "metadata": {}
        }
    
    def validate_structure(self) -> None:
        """验证文件结构"""
        logger.info(f"Validating structure for: {self.skill_path}")
        
        # 检查必需文件
        for file_name in self.REQUIRED_FILES:
            file_path = self.skill_path / file_name
            if not file_path.exists():
                self.results["passed"] = False
                self.results["issues"].append({
                    "type": "missing_required_file",
                    "file": file_name,
                    "severity": "critical",
                    "message": f"Required file missing: {file_name}"
                })
            else:
                self.results["score"] += 10  # 每个必需文件10分
        
        # 检查推荐文件
        for file_name in self.RECOMMENDED_FILES:
            file_path = self.skill_path / file_name
            if not file_path.exists():
                self.results["warnings"].append({
                    "type": "missing_recommended_file",
                    "file": file_name,
                    "severity": "warning",
                    "message": f"Recommended file missing: {file_name}"
                })
            else:
                self.results["score"] += 5  # 每个推荐文件5分
    
    def validate_config_yaml(self) -> None:
        """验证config.yaml文件"""
        config_path = self.skill_path / "config.yaml"
        if not config_path.exists():
            self.results["issues"].append({
                "type": "missing_config_file",
                "severity": "critical",
                "message": "config.yaml file missing"
            })
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查必需字段
            if "skill" not in config:
                self.results["issues"].append({
                    "type": "missing_config_section",
                    "section": "skill",
                    "severity": "critical",
                    "message": "Missing 'skill' section in config.yaml"
                })
            else:
                skill_config = config["skill"]
                required_fields = ["name", "version", "description"]
                for field in required_fields:
                    if field not in skill_config:
                        self.results["issues"].append({
                            "type": "missing_config_field",
                            "field": field,
                            "severity": "critical",
                            "message": f"Missing required field in config.yaml: {field}"
                        })
                
                # 记录元数据
                self.results["metadata"]["config"] = {
                    "version": skill_config.get("version"),
                    "name": skill_config.get("name")
                }
            
            self.results["score"] += 15
            
        except yaml.YAMLError as e:
            self.results["passed"] = False
            self.results["issues"].append({
                "type": "config_yaml_error",
                "severity": "critical",
                "message": f"Invalid YAML in config.yaml: {str(e)}"
            })
        except Exception as e:
            self.results["warnings"].append({
                "type": "config_validation_error",
                "severity": "warning",
                "message": f"Error validating config.yaml: {str(e)}"
            })
    
    def validate_package_json(self) -> None:
        """验证package.json文件"""
        package_path = self.skill_path / "package.json"
        if not package_path.exists():
            self.results["warnings"].append({
                "type": "missing_package_file",
                "severity": "warning",
                "message": "package.json file missing (recommended)"
            })
            return
        
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                package_info = json.load(f)
            
            # 检查必需字段
            required_fields = ["name", "version", "description"]
            for field in required_fields:
                if field not in package_info:
                    self.results["warnings"].append({
                        "type": "missing_package_field",
                        "field": field,
                        "severity": "warning",
                        "message": f"Missing recommended field in package.json: {field}"
                    })
            
            self.results["score"] += 10
            self.results["metadata"]["package"] = {
                "name": package_info.get("name"),
                "version": package_info.get("version")
            }
            
        except json.JSONDecodeError as e:
            self.results["issues"].append({
                "type": "package_json_error",
                "severity": "critical",
                "message": f"Invalid JSON in package.json: {str(e)}"
            })
        except Exception as e:
            self.results["warnings"].append({
                "type": "package_validation_error",
                "severity": "warning",
                "message": f"Error validating package.json: {str(e)}"
            })
    
    def validate_skill_py(self) -> None:
        """验证skill.py文件"""
        skill_py_path = self.skill_path / "skill.py"
        if not skill_py_path.exists():
            self.results["passed"] = False
            self.results["issues"].append({
                "type": "missing_skill_file",
                "severity": "critical",
                "message": "skill.py file missing"
            })
            return
        
        try:
            with open(skill_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必需模式
            required_patterns = [
                ("class.*Skill", "Skill class definition"),
                ("def handle_command", "handle_command method"),
                ("def get_commands", "get_commands method")
            ]
            
            for pattern, description in required_patterns:
                if pattern not in content:
                    self.results["issues"].append({
                        "type": "missing_skill_component",
                        "component": description,
                        "severity": "critical",
                        "message": f"Missing required component in skill.py: {description}"
                    })
            
            # 检查文件大小
            file_size = os.path.getsize(skill_py_path)
            if file_size > 1024 * 100:  # 100KB限制
                self.results["warnings"].append({
                    "type": "large_skill_file",
                    "severity": "warning",
                    "message": f"skill.py is large ({file_size} bytes), consider splitting"
                })
            
            self.results["score"] += 15
            
            # 计算文件哈希
            file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            self.results["metadata"]["skill_py"] = {
                "size": file_size,
                "hash": file_hash
            }
            
        except Exception as e:
            self.results["warnings"].append({
                "type": "skill_py_validation_error",
                "severity": "warning",
                "message": f"Error validating skill.py: {str(e)}"
            })
    
    def generate_recommendations(self) -> None:
        """生成改进建议"""
        if not self.results["passed"]:
            self.results["recommendations"].append(
                "Fix critical issues before proceeding with audit"
            )
        
        if len(self.results["warnings"]) > 3:
            self.results["recommendations"].append(
                "Address warnings to improve skill quality"
            )
        
        if self.results["score"] < 70:
            self.results["recommendations"].append(
                "Improve skill structure and documentation to increase score"
            )
        
        # 添加通用建议
        self.results["recommendations"].extend([
            "Ensure all version numbers are consistent across files",
            "Add comprehensive documentation in SKILL.md",
            "Test skill functionality thoroughly",
            "Review security declarations in config.yaml"
        ])
    
    def validate(self) -> Dict[str, Any]:
        """执行完整验证"""
        logger.info(f"Starting validation for: {self.skill_path}")
        
        # 执行所有验证步骤
        self.validate_structure()
        self.validate_config_yaml()
        self.validate_package_json()
        self.validate_skill_py()
        
        # 生成建议
        self.generate_recommendations()
        
        # 确保分数在0-100范围内
        self.results["score"] = min(100, max(0, self.results["score"]))
        
        logger.info(f"Validation completed. Score: {self.results['score']}, Passed: {self.results['passed']}")
        return self.results

# 路由定义
@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "Enterprise Audit Framework - Validator Service (Fixed)",
        "version": "3.0.1",
        "status": "operational",
        "storage": "memory",
        "endpoints": ["/health", "/validate", "/validate/{skill_id}"]
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        service="validator-service-fixed",
        timestamp=datetime.now()
    )

@app.post("/validate", response_model=ValidationResult)
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
        "timestamp": result["timestamp"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_fixed:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )