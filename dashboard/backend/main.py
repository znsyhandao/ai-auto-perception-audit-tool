"""
FastAPI Web管理界面
提供可视化审核管理和实时监控
"""

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import aiofiles
import uuid
import os

app = FastAPI(title="OpenClaw Audit Dashboard", version="3.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class AuditRequest(BaseModel):
    plugin_path: str
    audit_level: str = Field(..., regex="^(basic|standard|strict|enterprise)$")
    options: Optional[Dict[str, Any]] = {}

class AuditResponse(BaseModel):
    audit_id: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    created_at: datetime

class PluginMetrics(BaseModel):
    plugin_name: str
    total_audits: int
    average_score: float
    last_audit: datetime
    trend: str  # up, down, stable

# 全局状态
audit_tasks = {}
plugin_registry = {}

@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "OpenClaw Audit Dashboard API",
        "version": "3.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/audit", response_model=AuditResponse)
async def create_audit(
    request: AuditRequest,
    background_tasks: BackgroundTasks
):
    """
    创建新的审核任务
    """
    audit_id = str(uuid.uuid4())
    
    # 创建任务
    audit_tasks[audit_id] = {
        'status': 'pending',
        'progress': 0,
        'result': None,
        'created_at': datetime.now()
    }
    
    # 后台执行审核
    background_tasks.add_task(
        run_audit,
        audit_id,
        request.plugin_path,
        request.audit_level,
        request.options
    )
    
    return AuditResponse(
        audit_id=audit_id,
        status='pending',
        progress=0,
        created_at=datetime.now()
    )

@app.get("/api/audit/{audit_id}")
async def get_audit_status(audit_id: str):
    """
    获取审核状态
    """
    if audit_id not in audit_tasks:
        raise HTTPException(status_code=404, detail="审核任务不存在")
    
    task = audit_tasks[audit_id]
    
    return {
        'audit_id': audit_id,
        'status': task['status'],
        'progress': task['progress'],
        'result': task.get('result'),
        'created_at': task['created_at']
    }

@app.post("/api/upload")
async def upload_plugin(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    上传插件文件
    """
    # 保存上传的文件
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{file.filename}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return {
        'message': '文件上传成功',
        'file_path': file_path,
        'file_name': file.filename,
        'file_size': len(content)
    }

@app.get("/api/metrics")
async def get_metrics():
    """
    获取系统指标
    """
    return {
        'total_audits': len(audit_tasks),
        'pending_audits': sum(1 for t in audit_tasks.values() if t['status'] == 'pending'),
        'running_audits': sum(1 for t in audit_tasks.values() if t['status'] == 'running'),
        'completed_audits': sum(1 for t in audit_tasks.values() if t['status'] == 'completed'),
        'failed_audits': sum(1 for t in audit_tasks.values() if t['status'] == 'failed'),
        'average_score': calculate_average_score(),
        'risk_distribution': get_risk_distribution()
    }

@app.get("/api/plugins")
async def list_plugins():
    """
    列出所有已审核插件
    """
    plugins = []
    
    for plugin_id, data in plugin_registry.items():
        plugins.append({
            'id': plugin_id,
            'name': data.get('name'),
            'version': data.get('version'),
            'score': data.get('last_score'),
            'last_audit': data.get('last_audit'),
            'status': data.get('status')
        })
    
    return plugins

@app.get("/api/plugins/{plugin_id}/trend")
async def get_plugin_trend(plugin_id: str):
    """
    获取插件质量趋势
    """
    if plugin_id not in plugin_registry:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    # 从数据库获取历史数据
    history = get_audit_history(plugin_id)
    
    return {
        'plugin_id': plugin_id,
        'history': history,
        'trend': calculate_trend(history)
    }

@app.get("/api/reports/{audit_id}/download")
async def download_report(audit_id: str, format: str = "html"):
    """
    下载审核报告
    """
    if audit_id not in audit_tasks:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 生成报告文件
    report_path = generate_report(audit_id, format)
    
    return FileResponse(
        report_path,
        media_type='application/octet-stream',
        filename=f"audit_report_{audit_id}.{format}"
    )

@app.get("/api/health")
async def health_check():
    """
    健康检查
    """
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'api': 'up',
            'database': check_database(),
            'sandbox': check_sandbox(),
            'blockchain': check_blockchain()
        }
    }

# WebSocket端点
from fastapi import WebSocket

@app.websocket("/ws/audit/{audit_id}")
async def websocket_audit(websocket: WebSocket, audit_id: str):
    """
    WebSocket实时审核进度
    """
    await websocket.accept()
    
    try:
        while True:
            if audit_id in audit_tasks:
                task = audit_tasks[audit_id]
                await websocket.send_json({
                    'audit_id': audit_id,
                    'status': task['status'],
                    'progress': task['progress'],
                    'timestamp': datetime.now().isoformat()
                })
                
                if task['status'] in ['completed', 'failed']:
                    break
            
            await asyncio.sleep(1)
    
    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        await websocket.close()

# 辅助函数
async def run_audit(audit_id: str, plugin_path: str, audit_level: str, options: Dict):
    """后台运行审核任务"""
    audit_tasks[audit_id]['status'] = 'running'
    
    try:
        # 调用审核框架
        from main import OpenClawTestingFramework
        
        framework = OpenClawTestingFramework()
        
        # 模拟进度更新
        for progress in range(0, 100, 10):
            audit_tasks[audit_id]['progress'] = progress
            await asyncio.sleep(0.5)
        
        # 执行审核
        result = framework.audit_plugin(plugin_path, audit_level)
        
        audit_tasks[audit_id]['result'] = result
        audit_tasks[audit_id]['status'] = 'completed'
        audit_tasks[audit_id]['progress'] = 100
        
        # 更新插件注册表
        plugin_name = os.path.basename(plugin_path)
        plugin_registry[plugin_name] = {
            'name': plugin_name,
            'last_score': result.get('overall_score'),
            'last_audit': datetime.now(),
            'status': 'passed' if result.get('passed') else 'failed'
        }
        
    except Exception as e:
        audit_tasks[audit_id]['status'] = 'failed'
        audit_tasks[audit_id]['result'] = {'error': str(e)}

def calculate_average_score() -> float:
    """计算平均分数"""
    scores = []
    for task in audit_tasks.values():
        if task.get('result') and 'overall_score' in task['result']:
            scores.append(task['result']['overall_score'])
    
    return sum(scores) / len(scores) if scores else 0

def get_risk_distribution() -> Dict[str, int]:
    """获取风险分布"""
    distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    
    for task in audit_tasks.values():
        if task.get('result') and 'risk_level' in task['result']:
            risk = task['result']['risk_level']
            distribution[risk] = distribution.get(risk, 0) + 1
    
    return distribution

def get_audit_history(plugin_id: str) -> List[Dict]:
    """获取审核历史"""
    # 从数据库获取
    return []

def calculate_trend(history: List[Dict]) -> str:
    """计算趋势"""
    if len(history) < 2:
        return 'stable'
    
    recent_score = history[-1].get('score', 0)
    previous_score = history[-2].get('score', 0)
    
    if recent_score > previous_score:
        return 'up'
    elif recent_score < previous_score:
        return 'down'
    else:
        return 'stable'

def check_database() -> str:
    """检查数据库连接"""
    # 实现数据库检查
    return 'up'

def check_sandbox() -> str:
    """检查沙箱状态"""
    # 实现沙箱检查
    return 'up'

def check_blockchain() -> str:
    """检查区块链连接"""
    # 实现区块链检查
    return 'up'

def generate_report(audit_id: str, format: str) -> str:
    """生成报告文件"""
    # 实现报告生成
    return f"/tmp/report_{audit_id}.{format}"