"""
企业级深度分析服务 - 统一分析引擎
端口: 8007
集成: AST分析 + 控制流分析 + 数据流分析 + 性能分析 + 第三方库分析
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 尝试导入分析工具
TOOLS_AVAILABLE = False
ANALYSIS_TOOLS = {}

try:
    # AST分析器
    from ast_analyzer_v1 import ASTAnalyzer
    ANALYSIS_TOOLS['ast'] = ASTAnalyzer
    logger.info("AST analyzer imported")
except ImportError as e:
    logger.warning(f"AST analyzer not available: {e}")

try:
    # 控制流分析器
    from control_flow_analyzer_v1 import ControlFlowAnalyzer
    ANALYSIS_TOOLS['control_flow'] = ControlFlowAnalyzer
    logger.info("Control flow analyzer imported")
except ImportError as e:
    logger.warning(f"Control flow analyzer not available: {e}")

try:
    # 数据流分析器
    from data_flow_analyzer_v1 import DataFlowAnalyzer
    ANALYSIS_TOOLS['data_flow'] = DataFlowAnalyzer
    logger.info("Data flow analyzer imported")
except ImportError as e:
    logger.warning(f"Data flow analyzer not available: {e}")

try:
    # 性能分析器
    from performance_analyzer_v1 import PerformanceAnalyzer
    ANALYSIS_TOOLS['performance'] = PerformanceAnalyzer
    logger.info("Performance analyzer imported")
except ImportError as e:
    logger.warning(f"Performance analyzer not available: {e}")

try:
    # 第三方库分析器
    from third_party_analyzer_v1 import ThirdPartyAnalyzer
    ANALYSIS_TOOLS['third_party'] = ThirdPartyAnalyzer
    logger.info("Third party analyzer imported")
except ImportError as e:
    logger.warning(f"Third party analyzer not available: {e}")

TOOLS_AVAILABLE = len(ANALYSIS_TOOLS) > 0
logger.info(f"Total tools available: {len(ANALYSIS_TOOLS)}/{5}")

# 数据模型
class AnalysisRequest(BaseModel):
    """分析请求模型"""
    skill_id: str = Field(..., description="技能ID")
    skill_path: str = Field(..., description="技能路径")
    analysis_types: List[str] = Field(
        default=["ast", "control_flow", "data_flow", "performance", "third_party"],
        description="分析类型"
    )
    api_key: Optional[str] = Field(None, description="API密钥")
    timeout_seconds: int = Field(60, description="超时时间")

class AnalysisResult(BaseModel):
    """分析结果模型"""
    skill_id: str
    overall_score: float
    analysis_summary: Dict[str, Any]
    detailed_results: Dict[str, Any]
    critical_issues: List[Dict[str, Any]]
    recommendations: List[str]
    analysis_time: float
    timestamp: str

# 创建FastAPI应用
app = FastAPI(
    title="企业级深度分析服务",
    description="统一代码分析引擎 - AST + 控制流 + 数据流 + 性能 + 第三方库",
    version="3.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 内存存储
analysis_results = {}
api_keys = {"demo_key": {"rate_limit": 100, "used": 0}}

# API密钥验证
def verify_api_key(api_key: Optional[str] = None):
    """验证API密钥"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if api_key not in api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # 检查速率限制
    key_info = api_keys[api_key]
    if key_info["used"] >= key_info["rate_limit"]:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    key_info["used"] += 1
    return True

class UnifiedAnalyzer:
    """统一分析器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.results = {
            "overall_score": 100.0,
            "analysis_summary": {},
            "detailed_results": {},
            "critical_issues": [],
            "recommendations": [],
            "analysis_time": 0.0
        }
    
    async def analyze_ast(self) -> Dict[str, Any]:
        """AST分析"""
        try:
            skill_py = self.skill_path / "skill.py"
            if not skill_py.exists():
                return {"error": "skill.py not found", "score": 0, "analysis_complete": False}
            
            analyzer = ASTAnalyzer(str(skill_py))
            if analyzer.parse():
                analyzer.detect_infinite_loops()
                analyzer.detect_unreachable_code()
                analyzer.detect_security_issues()
                analyzer.detect_code_smells()
                
                score = max(0, 100 - len(analyzer.issues) * 5)
                
                return {
                    "score": score,
                    "issues_found": len(analyzer.issues),
                    "issues": analyzer.issues[:5],
                    "analysis_complete": True
                }
            return {"error": "AST parse failed", "score": 0, "analysis_complete": False}
        except Exception as e:
            return {"error": str(e), "score": 0, "analysis_complete": False}
    
    async def analyze_control_flow(self) -> Dict[str, Any]:
        """控制流分析"""
        try:
            analyzer = ControlFlowAnalyzer(str(self.skill_path))
            result = analyzer.analyze()
            
            score = result.get("score", 80)
            issues = result.get("issues", [])
            
            return {
                "score": score,
                "issues_found": len(issues),
                "issues": issues[:5],
                "analysis_complete": True
            }
        except Exception as e:
            return {"error": str(e), "score": 0, "analysis_complete": False}
    
    async def analyze_data_flow(self) -> Dict[str, Any]:
        """数据流分析"""
        try:
            analyzer = DataFlowAnalyzer(str(self.skill_path))
            result = analyzer.analyze()
            
            score = result.get("score", 85)
            issues = result.get("issues", [])
            
            return {
                "score": score,
                "issues_found": len(issues),
                "issues": issues[:5],
                "analysis_complete": True
            }
        except Exception as e:
            return {"error": str(e), "score": 0, "analysis_complete": False}
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """性能分析"""
        try:
            analyzer = PerformanceAnalyzer(str(self.skill_path))
            result = analyzer.analyze()
            
            score = result.get("score", 75)
            bottlenecks = result.get("bottlenecks", [])
            
            return {
                "score": score,
                "bottlenecks_found": len(bottlenecks),
                "bottlenecks": bottlenecks[:3],
                "analysis_complete": True
            }
        except Exception as e:
            return {"error": str(e), "score": 0, "analysis_complete": False}
    
    async def analyze_third_party(self) -> Dict[str, Any]:
        """第三方库分析"""
        try:
            analyzer = ThirdPartyAnalyzer(str(self.skill_path))
            result = analyzer.analyze()
            
            score = result.get("score", 90)
            vulnerabilities = result.get("vulnerabilities", [])
            
            return {
                "score": score,
                "vulnerabilities_found": len(vulnerabilities),
                "vulnerabilities": vulnerabilities[:3],
                "analysis_complete": True
            }
        except Exception as e:
            return {"error": str(e), "score": 0, "analysis_complete": False}
    
    async def analyze_all(self, analysis_types: List[str]) -> Dict[str, Any]:
        """执行所有分析"""
        start_time = time.time()
        
        if not TOOLS_AVAILABLE:
            return {
                "error": "Analysis tools not available",
                "overall_score": 0,
                "analysis_summary": {},
                "detailed_results": {},
                "critical_issues": [],
                "recommendations": ["Install analysis tools first"],
                "analysis_time": 0
            }
        
        # 并行执行分析
        tasks = []
        if "ast" in analysis_types and "ast" in ANALYSIS_TOOLS:
            tasks.append(self.analyze_ast())
        if "control_flow" in analysis_types and "control_flow" in ANALYSIS_TOOLS:
            tasks.append(self.analyze_control_flow())
        if "data_flow" in analysis_types and "data_flow" in ANALYSIS_TOOLS:
            tasks.append(self.analyze_data_flow())
        if "performance" in analysis_types and "performance" in ANALYSIS_TOOLS:
            tasks.append(self.analyze_performance())
        if "third_party" in analysis_types and "third_party" in ANALYSIS_TOOLS:
            tasks.append(self.analyze_third_party())
        
        if not tasks:
            return {
                "error": "No analysis types available",
                "overall_score": 0,
                "analysis_summary": {},
                "detailed_results": {},
                "critical_issues": [],
                "recommendations": ["Select valid analysis types"],
                "analysis_time": 0
            }
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        analysis_summary = {}
        detailed_results = {}
        all_issues = []
        scores = []
        
        type_names = ["ast", "control_flow", "data_flow", "performance", "third_party"]
        available_types = [t for t in type_names if t in analysis_types and t in ANALYSIS_TOOLS]
        
        for i, (type_name, result) in enumerate(zip(available_types, results)):
            if isinstance(result, Exception):
                analysis_summary[type_name] = {
                    "status": "error",
                    "error": str(result),
                    "score": 0
                }
                detailed_results[type_name] = {"error": str(result)}
            else:
                score = result.get("score", 0)
                analysis_summary[type_name] = {
                    "status": "success" if result.get("analysis_complete", False) else "partial",
                    "score": score,
                    "issues_found": result.get("issues_found", 0) or result.get("bottlenecks_found", 0) or result.get("vulnerabilities_found", 0)
                }
                detailed_results[type_name] = result
                scores.append(score)
                
                # 收集关键问题
                if "issues" in result:
                    for issue in result["issues"][:2]:
                        all_issues.append({
                            "type": type_name,
                            "severity": issue.get("severity", "medium"),
                            "message": issue.get("message", "Unknown issue"),
                            "location": issue.get("location", "unknown")
                        })
                if "bottlenecks" in result:
                    for bottleneck in result["bottlenecks"][:2]:
                        all_issues.append({
                            "type": "performance",
                            "severity": "high",
                            "message": f"Performance bottleneck: {bottleneck.get('description', 'Unknown')}",
                            "location": bottleneck.get("location", "unknown")
                        })
                if "vulnerabilities" in result:
                    for vuln in result["vulnerabilities"][:2]:
                        all_issues.append({
                            "type": "security",
                            "severity": "critical",
                            "message": f"Vulnerability: {vuln.get('description', 'Unknown')}",
                            "location": vuln.get("location", "unknown")
                        })
        
        # 计算总体得分
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # 生成建议
        recommendations = []
        if overall_score < 70:
            recommendations.append("Significant code quality issues need attention")
        elif overall_score < 85:
            recommendations.append("Some improvements recommended")
        else:
            recommendations.append("Code quality is good")
        
        if all_issues:
            recommendations.append(f"Address {len(all_issues)} identified issues")
        
        # 按严重性排序问题
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "medium"), 3))
        
        analysis_time = time.time() - start_time
        
        return {
            "overall_score": round(overall_score, 1),
            "analysis_summary": analysis_summary,
            "detailed_results": detailed_results,
            "critical_issues": all_issues[:10],
            "recommendations": recommendations,
            "analysis_time": round(analysis_time, 2)
        }

@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "deep-analysis-service",
        "version": "3.1.0",
        "status": "running",
        "port": 8007,
        "tools_available": TOOLS_AVAILABLE,
        "available_tools": list(ANALYSIS_TOOLS.keys()),
        "endpoints": {
            "analyze": "POST /analyze - 深度分析",
            "results": "GET /results/{skill_id} - 获取结果",
            "health": "GET /health - 健康检查",
            "stats": "GET /stats - 服务统计"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tools_available": TOOLS_AVAILABLE,
        "available_tools": list(ANALYSIS_TOOLS.keys()),
        "memory_usage": len(analysis_results)
    }

@app.get("/stats")
async def get_stats():
    """获取服务统计"""
    return {
        "total_analyses": len(analysis_results),
        "tools_available": len(ANALYSIS_TOOLS),
        "api_keys": len(api_keys),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
async def analyze_skill(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    api_key_verified: bool = Depends(lambda api_key: verify_api_key(api_key) if api_key else True)
):
    """深度分析技能"""
    logger.info(f"Starting deep analysis: {request.skill_id}")
    
    # 检查技能路径
    skill_path = Path(request.skill_path)
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail="Skill path not found")
    
    # 执行分析
    analyzer = UnifiedAnalyzer(request.skill_path)
    results = await analyzer.analyze_all(request.analysis_types)
    
    # 添加元数据
    results["skill_id"] = request.skill_id
    results["timestamp"] = datetime.now().isoformat()
    results["analysis_types"] = request.analysis_types
    
    # 存储结果
    analysis_results[request.skill_id] = {
        "results": results,
        "request_time": datetime.now().isoformat(),
        "api_key_used": request.api_key is not None
    }
    
    logger.info(f"Deep analysis completed: {request.skill_id}, score: {results.get('overall_score', 0)}")
    return results

@app.get("/results/{skill_id}")
async def get_analysis_result(skill_id: str):
    """获取分析结果"""
    if skill_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    return analysis_results[skill_id]["results"]

@app.get("/analyze/quick")
async def quick_analyze(skill_id: str, skill_path: str):
    """快速分析接口"""
    request = AnalysisRequest(
        skill_id=skill_id,
        skill_path=skill_path,
        analysis_types=["ast", "control_flow"],
        timeout_seconds=30
    )
    
    analyzer = UnifiedAnalyzer(skill_path)
    results = await analyzer.analyze_all(request.analysis_types)
    
    results["skill_id"] = skill_id
    results["timestamp"] = datetime.now().isoformat()
    
    return {
        "quick_analysis": True,
        "score": results.get("overall_score", 0),
        "critical_issues_count": len(results.get("critical_issues", [])),
        "recommendations": results.get("recommendations", []),
        "analysis_time": results.get("analysis_time", 0)
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Deep Analysis Service (port: 8007)")
    logger.info(f"Available tools: {list(ANALYSIS_TOOLS.keys())}")
    uvicorn.run(app, host="0.0.0.0", port=8007, reload=True)