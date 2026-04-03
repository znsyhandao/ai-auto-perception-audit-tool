"""
创建统一的深度分析服务 - 达到真正企业级标准
"""

import os
import shutil
from pathlib import Path

def create_unified_analysis_service():
    """创建统一的深度分析服务"""
    print("CREATING UNIFIED DEEP ANALYSIS SERVICE")
    print("=" * 60)
    
    # 创建服务目录
    service_dir = Path("microservices/deep-analysis-service")
    service_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Service directory: {service_dir}")
    
    # 复制所有分析工具
    tools_to_copy = [
        "ast_analyzer_v1.py",
        "control_flow_analyzer_v1.py",
        "data_flow_analyzer_v1.py",
        "performance_analyzer_v1.py",
        "third_party_analyzer_v1.py",
        "deep_analysis_suite.py"
    ]
    
    print("\nCopying analysis tools...")
    for tool in tools_to_copy:
        source = Path(tool)
        if source.exists():
            dest = service_dir / tool
            shutil.copy2(source, dest)
            print(f"  COPIED: {tool}")
        else:
            print(f"  MISSING: {tool}")
    
    # 创建统一的主服务文件
    print("\nCreating unified analysis service...")
    
    main_content = '''"""
企业级深度分析服务 - 统一分析引擎
端口: 8007
集成: AST分析 + 控制流分析 + 数据流分析 + 性能分析 + 第三方库分析
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入分析工具
try:
    from ast_analyzer_v1 import ASTAnalyzer
    from control_flow_analyzer_v1 import ControlFlowAnalyzer
    from data_flow_analyzer_v1 import DataFlowAnalyzer
    from performance_analyzer_v1 import PerformanceAnalyzer
    from third_party_analyzer_v1 import ThirdPartyAnalyzer
    from deep_analysis_suite import DeepAnalysisSuite
    
    TOOLS_AVAILABLE = True
    logger.info("All analysis tools imported successfully")
except ImportError as e:
    TOOLS_AVAILABLE = False
    logger.warning(f"Some tools not available: {e}")

# 数据模型
class AnalysisRequest(BaseModel):
    """分析请求模型"""
    skill_id: str = Field(..., description="技能ID")
    skill_path: str = Field(..., description="技能路径")
    analysis_types: List[str] = Field(
        ["ast", "control_flow", "data_flow", "performance", "third_party"],
        description="分析类型"
    )
    timeout_seconds: int = Field(60, description="超时时间")

class AnalysisResult(BaseModel):
    """分析结果模型"""
    skill_id: str
    overall_score: float
    analysis_types: Dict[str, Dict[str, Any]]
    critical_issues: List[Dict[str, Any]]
    recommendations: List[str]
    analysis_time: float
    timestamp: str

# 创建FastAPI应用
app = FastAPI(
    title="企业级深度分析服务",
    description="统一代码分析引擎 - AST + 控制流 + 数据流 + 性能 + 第三方库",
    version="3.0.0"
)

# 内存存储
analysis_results = {}

class UnifiedAnalyzer:
    """统一分析器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.results = {
            "overall_score": 100.0,
            "analysis_types": {},
            "critical_issues": [],
            "recommendations": [],
            "analysis_time": 0.0
        }
    
    async def analyze_ast(self) -> Dict[str, Any]:
        """AST分析"""
        try:
            skill_py = self.skill_path / "skill.py"
            if not skill_py.exists():
                return {"error": "skill.py not found", "score": 0}
            
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
            return {"error": "AST parse failed", "score": 0}
        except Exception as e:
            return {"error": str(e), "score": 0}
    
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
            return {"error": str(e), "score": 0}
    
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
            return {"error": str(e), "score": 0}
    
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
            return {"error": str(e), "score": 0}
    
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
            return {"error": str(e), "score": 0}
    
    async def analyze_all(self, analysis_types: List[str]) -> Dict[str, Any]:
        """执行所有分析"""
        import time
        start_time = time.time()
        
        if not TOOLS_AVAILABLE:
            return {
                "error": "Analysis tools not available",
                "overall_score": 0,
                "analysis_types": {},
                "critical_issues": [],
                "recommendations": ["Install analysis tools first"]
            }
        
        # 并行执行分析
        tasks = []
        if "ast" in analysis_types:
            tasks.append(self.analyze_ast())
        if "control_flow" in analysis_types:
            tasks.append(self.analyze_control_flow())
        if "data_flow" in analysis_types:
            tasks.append(self.analyze_data_flow())
        if "performance" in analysis_types:
            tasks.append(self.analyze_performance())
        if "third_party" in analysis_types:
            tasks.append(self.analyze_third_party())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        analysis_results = {}
        all_issues = []
        scores = []
        
        type_names = ["ast", "control_flow", "data_flow", "performance", "third_party"]
        
        for i, (type_name, result) in enumerate(zip(type_names[:len(results)], results)):
            if isinstance(result, Exception):
                analysis_results[type_name] = {
                    "error": str(result),
                    "score": 0,
                    "analysis_complete": False
                }
            else:
                analysis_results[type_name] = result
                scores.append(result.get("score", 0))
                
                # 收集关键问题
                if "issues" in result:
                    all_issues.extend(result["issues"][:2])
                if "bottlenecks" in result:
                    all_issues.extend([
                        {"type": "performance", "message": f"Performance bottleneck: {b['description']}"}
                        for b in result["bottlenecks"][:2]
                    ])
                if "vulnerabilities" in result:
                    all_issues.extend([
                        {"type": "security", "message": f"Vulnerability: {v['description']}"}
                        for v in result["vulnerabilities"][:2]
                    ])
        
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
        
        analysis_time = time.time() - start_time
        
        return {
            "overall_score": round(overall_score, 1),
            "analysis_types": analysis_results,
            "critical_issues": all_issues[:10],
            "recommendations": recommendations,
            "analysis_time": round(analysis_time, 2)
        }

@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "deep-analysis-service",
        "version": "3.0.0",
        "status": "running",
        "port": 8007,
        "tools_available": TOOLS_AVAILABLE,
        "endpoints": {
            "analyze": "POST /analyze - 深度分析",
            "results": "GET /results/{skill_id} - 获取结果",
            "health": "GET /health - 健康检查"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tools_available": TOOLS_AVAILABLE
    }

@app.post("/analyze")
async def analyze_skill(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """深度分析技能"""
    logger.info(f"Starting deep analysis: {request.skill_id}")
    
    # 检查技能路径
    skill_path = Path(request.skill_path)
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail="Skill path not found")
    
    # 执行分析
    analyzer = UnifiedAnalyzer(request.skill_path)
    results = await analyzer.analyze_all(request.analysis_types)
    
    # 添加时间戳
    results["skill_id"] = request.skill_id
    results["timestamp"] = datetime.now().isoformat()
    
    # 存储结果
    analysis_results[request.skill_id] = results
    
    logger.info(f"Deep analysis completed: {request.skill_id}")
    return results

@app.get("/results/{skill_id}")
async def get_analysis_result(skill_id: str):
    """获取分析结果"""
    if skill_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    return analysis_results[skill_id]

@app.get("/analyze/{skill_id}")
async def quick_analyze(skill_id: str, skill_path: str):
    """快速分析接口"""
    request = AnalysisRequest(
        skill_id=skill_id,
        skill_path=skill_path,
        analysis_types=["ast", "control_flow"],
        timeout_seconds=30
    )
    
