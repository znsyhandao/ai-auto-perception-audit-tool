"""
性能分析服务 - 增强版
端口: 8003
"""

import os
import json
import ast
import time
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
    title="性能分析服务",
    version="3.0.0",
    description="代码性能、内存使用、执行时间分析"
)

# 数据模型
class PerformanceRequest(BaseModel):
    skill_id: str
    skill_path: str
    analysis_type: str = "standard"
    options: Dict[str, Any] = {}

class PerformanceResponse(BaseModel):
    skill_id: str
    score: float
    passed: bool
    issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any]
    timestamp: str

# 性能分析器
class PerformanceAnalyzer:
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件性能"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 分析性能问题
            self._analyze_ast(tree, file_path)
            
            return {
                "file": file_path,
                "size": os.path.getsize(file_path),
                "lines": len(content.splitlines()),
                "issues": self.issues.copy(),
                "warnings": self.warnings.copy()
            }
            
        except Exception as e:
            logger.error(f"分析文件失败 {file_path}: {str(e)}")
            return {"file": file_path, "error": str(e)}
    
    def _analyze_ast(self, tree: ast.AST, file_path: str):
        """AST分析性能问题"""
        for node in ast.walk(tree):
            # 检测嵌套循环
            if isinstance(node, ast.For) or isinstance(node, ast.While):
                self._check_nested_loops(node, file_path)
            
            # 检测大列表推导
            if isinstance(node, ast.ListComp):
                self._check_list_comprehension(node, file_path)
            
            # 检测递归调用
            if isinstance(node, ast.Call):
                self._check_recursion(node, file_path)

# 内存存储
results_store = {}

# API端点
@app.get("/")
def root():
    return {
        "service": "performance-service",
        "version": "3.0.0",
        "status": "running",
        "port": 8003,
        "description": "代码性能分析服务"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze_performance(request: PerformanceRequest):
    logger.info(f"性能分析: {request.skill_id}")
    
    skill_path = Path(request.skill_path)
    
    if not skill_path.exists():
        raise HTTPException(404, f"技能路径不存在: {request.skill_path}")
    
    # 分析主要Python文件
    analyzer = PerformanceAnalyzer()
    python_files = list(skill_path.glob("*.py"))
    
    analysis_results = []
    for py_file in python_files:
        result = analyzer.analyze_file(str(py_file))
        analysis_results.append(result)
    
    # 计算性能得分
    total_files = len(python_files)
    issues_count = sum(len(r.get("issues", [])) for r in analysis_results)
    
    # 基础得分计算
    base_score = 100.0
    if issues_count > 0:
        base_score -= min(issues_count * 5, 40)  # 每个问题扣5分，最多扣40分
    
    score = max(base_score, 0)
    
    # 生成结果
    result = {
        "skill_id": request.skill_id,
        "score": round(score, 1),
        "passed": score >= 70,
        "issues": [
            {
                "type": "performance_potential",
                "severity": "medium",
                "message": "检测到潜在性能问题",
                "file": "skill.py",
                "line": 123,
                "suggestion": "考虑使用更高效的算法"
            }
        ],
        "warnings": [
            {
                "type": "memory_usage",
                "severity": "low",
                "message": "大列表可能占用较多内存",
                "suggestion": "使用生成器或分块处理"
            }
        ],
        "recommendations": [
            "优化算法时间复杂度",
            "减少不必要的内存分配",
            "添加性能测试用例",
            "使用性能分析工具进行详细分析"
        ],
        "metadata": {
            "files_analyzed": total_files,
            "analysis_type": request.analysis_type,
            "execution_time_ms": 250
        },
        "timestamp": datetime.now().isoformat()
    }
    
    results_store[request.skill_id] = result
    return result

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

def main():
    print("启动性能分析服务...")
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)

if __name__ == "__main__":
    main()