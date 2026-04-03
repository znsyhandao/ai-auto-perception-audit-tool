"""
企业级审核框架 - 安全服务（修复版）
简化版本，不使用Redis和AI模型
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
class SecurityScanRequest(BaseModel):
    """安全扫描请求模型"""
    skill_id: str = Field(..., description="技能ID")
    skill_path: str = Field(..., description="技能路径")
    scan_depth: str = Field("standard", description="扫描深度: quick/standard/deep")

class SecurityScanResult(BaseModel):
    """安全扫描结果模型"""
    skill_id: str = Field(..., description="技能ID")
    security_score: float = Field(..., description="安全得分(0-100)")
    risk_level: str = Field(..., description="风险等级: low/medium/high/critical")
    threats: List[Dict[str, Any]] = Field(default_factory=list, description="威胁列表")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="漏洞列表")
    recommendations: List[str] = Field(default_factory=list, description="安全建议")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="状态: healthy/unhealthy")
    service: str = Field("security-service", description="服务名称")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

# 应用初始化
app = FastAPI(
    title="企业级审核框架 - 安全服务（修复版）",
    description="简化安全扫描服务 - 内存存储版本",
    version="3.0.1"
)

# 内存存储
memory_store = {}

class SimpleSecurityScanner:
    """简化安全扫描器"""
    
    # 基本模式检测
    DANGEROUS_PATTERNS = {
        "exec_shell": [
            "os.system",
            "subprocess.run",
            "subprocess.call",
            "subprocess.Popen",
            "eval(",
            "exec(",
            "__import__("
        ],
        "file_operations": [
            "open(",
            "shutil.rmtree",
            "os.remove",
            "os.unlink"
        ],
        "network_calls": [
            "requests.get",
            "requests.post",
            "socket.",
            "urllib."
        ]
    }
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.results = {
            "security_score": 100,  # 初始满分
            "risk_level": "low",
            "threats": [],
            "vulnerabilities": [],
            "recommendations": [],
            "metadata": {
                "files_scanned": 0,
                "patterns_found": 0
            }
        }
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """扫描单个文件"""
        threats = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # 检查每一行
                for line_num, line in enumerate(lines, 1):
                    for category, patterns in self.DANGEROUS_PATTERNS.items():
                        for pattern in patterns:
                            if pattern in line:
                                threat = {
                                    "type": category,
                                    "pattern": pattern,
                                    "line": line_num,
                                    "filename": file_path.name,
                                    "code_snippet": line.strip()[:100],
                                    "severity": self.get_severity(category),
                                    "confidence": "medium"
                                }
                                threats.append(threat)
                                self.results["metadata"]["patterns_found"] += 1
                                
        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {str(e)}")
        
        return threats
    
    def get_severity(self, category: str) -> str:
        """获取威胁严重性"""
        severity_map = {
            "exec_shell": "high",
            "file_operations": "medium",
            "network_calls": "medium"
        }
        return severity_map.get(category, "low")
    
    def calculate_security_score(self) -> None:
        """计算安全得分"""
        base_score = 100
        
        # 根据威胁扣分
        for threat in self.results["threats"]:
            severity = threat["severity"]
            if severity == "high":
                base_score -= 15
            elif severity == "medium":
                base_score -= 8
            elif severity == "low":
                base_score -= 3
        
        # 确保分数在0-100范围内
        self.results["security_score"] = max(0, min(100, base_score))
        
        # 确定风险等级
        if self.results["security_score"] >= 80:
            self.results["risk_level"] = "low"
        elif self.results["security_score"] >= 60:
            self.results["risk_level"] = "medium"
        elif self.results["security_score"] >= 40:
            self.results["risk_level"] = "high"
        else:
            self.results["risk_level"] = "critical"
    
    def generate_recommendations(self) -> None:
        """生成安全建议"""
        recommendations = []
        
        # 根据威胁类型生成建议
        threat_types = set(threat["type"] for threat in self.results["threats"])
        for threat_type in threat_types:
            if threat_type == "exec_shell":
                recommendations.append("Avoid using os.system() or subprocess calls; use safer alternatives")
            elif threat_type == "file_operations":
                recommendations.append("Implement proper file access controls and validation")
            elif threat_type == "network_calls":
                recommendations.append("Ensure network calls are properly authenticated and encrypted")
        
        # 通用建议
        if self.results["security_score"] < 70:
            recommendations.extend([
                "Conduct a thorough security review of all code",
                "Implement input validation for all user inputs",
                "Add logging and monitoring for security events"
            ])
        
        self.results["recommendations"] = recommendations
    
    def scan(self) -> Dict[str, Any]:
        """执行安全扫描"""
        logger.info(f"Starting security scan for: {self.skill_path}")
        
        # 扫描所有Python文件
        for file_path in self.skill_path.rglob("*.py"):
            if file_path.is_file():
                threats = self.scan_file(file_path)
                self.results["threats"].extend(threats)
                self.results["metadata"]["files_scanned"] += 1
        
        # 扫描JavaScript文件
        for file_path in self.skill_path.rglob("*.js"):
            if file_path.is_file():
                threats = self.scan_file(file_path)
                self.results["threats"].extend(threats)
                self.results["metadata"]["files_scanned"] += 1
        
        # 计算得分和生成建议
        self.calculate_security_score()
        self.generate_recommendations()
        
        logger.info(f"Security scan completed. Score: {self.results['security_score']}, Risk: {self.results['risk_level']}")
        return self.results

# 路由定义
@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "Enterprise Audit Framework - Security Service (Fixed)",
        "version": "3.0.1",
        "status": "operational",
        "storage": "memory",
        "endpoints": ["/health", "/scan", "/scan/{skill_id}"]
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        service="security-service-fixed",
        timestamp=datetime.now()
    )

@app.post("/scan", response_model=SecurityScanResult)
async def scan_skill(request: SecurityScanRequest):
    """执行安全扫描"""
    # 检查技能路径是否存在
    skill_path = Path(request.skill_path)
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail="Skill path not found")
    
    # 执行安全扫描
    scanner = SimpleSecurityScanner(request.skill_path)
    results = scanner.scan()
    
    # 存储结果到内存
    result_key = f"security:{request.skill_id}"
    memory_store[result_key] = {
        "skill_id": request.skill_id,
        "security_score": results["security_score"],
        "risk_level": results["risk_level"],
        "threat_count": len(results["threats"]),
        "vulnerability_count": len(results["vulnerabilities"]),
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    return SecurityScanResult(
        skill_id=request.skill_id,
        security_score=results["security_score"],
        risk_level=results["risk_level"],
        threats=results["threats"],
        vulnerabilities=results["vulnerabilities"],
        recommendations=results["recommendations"],
        metadata=results["metadata"],
        timestamp=datetime.now()
    )

@app.get("/scan/{skill_id}")
async def get_security_result(skill_id: str):
    """获取安全扫描结果"""
    result_key = f"security:{skill_id}"
    result = memory_store.get(result_key)
    
    if not result:
        raise HTTPException(status_code=404, detail="Security scan result not found")
    
    return {
        "skill_id": skill_id,
        "security_score": result["security_score"],
        "risk_level": result["risk_level"],
        "threat_count": result["threat_count"],
        "vulnerability_count": result["vulnerability_count"],
        "timestamp": result["timestamp"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_fixed:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )