"""
基于数学定理的审核服务 - 简化修复版本
端口: 8010
"""

import os
import json
import logging
import numpy as np
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
class MathematicalAuditRequest(BaseModel):
    """数学审核请求模型"""
    skill_id: str = Field(..., description="技能ID")
    skill_path: str = Field(..., description="技能路径")
    audit_types: List[str] = Field(
        default=["maclaurin", "taylor", "fourier", "matrix", "proof"],
        description="审核类型"
    )
    mathematical_depth: int = Field(5, description="数学分析深度")

class MathematicalAuditResult(BaseModel):
    """数学审核结果模型"""
    skill_id: str
    overall_mathematical_score: float
    audit_results: Dict[str, Any]
    mathematical_certificates: List[Dict[str, Any]]
    audit_time: float
    timestamp: str

# 导入数学AI引擎
try:
    from mathematical_ai_engine_final import MathematicalAIEngineFinal
    math_engine = MathematicalAIEngineFinal()
    logger.info("Mathematical AI Engine loaded successfully")
except ImportError as e:
    logger.error(f"Failed to load Mathematical AI Engine: {e}")
    math_engine = None

# 创建FastAPI应用
app = FastAPI(
    title="基于数学定理的审核服务",
    description="麦克劳林级数驱动的AI引擎 - 数学可验证的代码审核",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class MathematicalAuditor:
    """数学审核器 - 简化版本"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
    
    def run_complete_audit(self, audit_types: List[str]) -> Dict[str, Any]:
        """运行完整数学审核 - 直接使用数学引擎"""
        import time
        
        start_time = time.time()
        
        if not math_engine:
            return {
                "error": "Mathematical engine not available",
                "overall_mathematical_score": 0,
                "audit_results": {},
                "mathematical_certificates": [],
                "audit_time": 0
            }
        
        # 直接使用数学引擎运行审核
        result = math_engine.run_complete_mathematical_audit(self.skill_path, audit_types)
        
        audit_time = time.time() - start_time
        result["audit_time"] = round(audit_time, 2)
        
        return result

# API端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "mathematical_audit_service",
        "version": "4.0.0",
        "timestamp": datetime.now().isoformat(),
        "mathematical_engine": "available" if math_engine else "unavailable",
        "available_audits": ["maclaurin", "taylor", "fourier", "matrix", "proof"]
    }

@app.post("/audit", response_model=MathematicalAuditResult)
async def run_mathematical_audit(request: MathematicalAuditRequest):
    """运行数学审核"""
    logger.info(f"Starting mathematical audit for skill: {request.skill_id}")
    
    # 创建审核器
    auditor = MathematicalAuditor(request.skill_path)
    
    # 运行审核
    result = auditor.run_complete_audit(request.audit_types)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # 返回结果
    return MathematicalAuditResult(
        skill_id=request.skill_id,
        overall_mathematical_score=result["overall_mathematical_score"],
        audit_results=result["audit_results"],
        mathematical_certificates=result["mathematical_certificates"],
        audit_time=result["audit_time"],
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)