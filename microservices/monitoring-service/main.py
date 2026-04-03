"""
企业级审核框架 - 监控服务
端口: 8006
功能: 实时服务健康监控、性能指标收集、告警系统、日志聚合
"""

import os
import json
import time
import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
class ServiceStatus(BaseModel):
    """服务状态模型"""
    service: str
    status: str
    response_time: float
    last_check: str
    uptime: float

class Alert(BaseModel):
    """告警模型"""
    id: str
    service: str
    level: str
    message: str
    timestamp: str
    resolved: bool

class Metric(BaseModel):
    """指标模型"""
    service: str
    metric_type: str
    value: float
    timestamp: str

# 创建FastAPI应用
app = FastAPI(
    title="企业级监控服务",
    description="实时服务监控和性能指标收集服务",
    version="3.0.0"
)

# 监控配置
SERVICES_TO_MONITOR = {
    "validator": {"url": "http://localhost:8001/health", "port": 8001},
    "security": {"url": "http://localhost:8002/health", "port": 8002},
    "performance": {"url": "http://localhost:8003/health", "port": 8003},
    "compliance": {"url": "http://localhost:8004/health", "port": 8004},
    "reporting": {"url": "http://localhost:8005/health", "port": 8005},
    "monitoring": {"url": "http://localhost:8006/health", "port": 8006}
}

# 内存存储
service_status = {}
alerts = []
metrics = []
service_metrics = {}

# 监控线程控制
monitoring_active = False
monitoring_thread = None

def check_service(service_name, config):
    """检查单个服务状态"""
    try:
        start_time = time.time()
        response = requests.get(config["url"], timeout=5)
        response_time = (time.time() - start_time) * 1000  # 毫秒
        
        if response.status_code == 200:
            status = "healthy"
            # 记录指标
            record_metric(service_name, "response_time", response_time)
            record_metric(service_name, "status_code", response.status_code)
        else:
            status = "unhealthy"
            create_alert(service_name, "warning", f"服务返回状态码: {response.status_code}")
        
        return {
            "service": service_name,
            "status": status,
            "response_time": response_time,
            "last_check": datetime.now().isoformat(),
            "uptime": service_status.get(service_name, {}).get("uptime", 0) + 1 if status == "healthy" else 0
        }
        
    except requests.exceptions.RequestException as e:
        create_alert(service_name, "critical", f"服务不可达: {str(e)}")
        return {
            "service": service_name,
            "status": "down",
            "response_time": 0,
            "last_check": datetime.now().isoformat(),
            "uptime": 0
        }

def record_metric(service_name, metric_type, value):
    """记录指标"""
    metric = {
        "service": service_name,
        "metric_type": metric_type,
        "value": value,
        "timestamp": datetime.now().isoformat()
    }
    metrics.append(metric)
    
    # 保留最近1000个指标
    if len(metrics) > 1000:
        metrics.pop(0)
    
    # 按服务聚合指标
    if service_name not in service_metrics:
        service_metrics[service_name] = {}
    
    if metric_type not in service_metrics[service_name]:
        service_metrics[service_name][metric_type] = []
    
    service_metrics[service_name][metric_type].append(metric)
    
    # 保留最近100个指标
    if len(service_metrics[service_name][metric_type]) > 100:
        service_metrics[service_name][metric_type].pop(0)

def create_alert(service_name, level, message):
    """创建告警"""
    alert_id = f"alert_{len(alerts) + 1:04d}"
    alert = {
        "id": alert_id,
        "service": service_name,
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "resolved": False
    }
    alerts.append(alert)
    logger.warning(f"告警创建: {service_name} - {level} - {message}")
    
    # 保留最近100个告警
    if len(alerts) > 100:
        alerts.pop(0)
    
    return alert

def monitoring_loop():
    """监控循环"""
    global monitoring_active
    while monitoring_active:
        try:
            for service_name, config in SERVICES_TO_MONITOR.items():
                status = check_service(service_name, config)
                service_status[service_name] = status
            
            # 记录系统指标
            record_metric("system", "active_services", sum(1 for s in service_status.values() if s["status"] == "healthy"))
            record_metric("system", "total_alerts", len([a for a in alerts if not a["resolved"]]))
            
            time.sleep(10)  # 每10秒检查一次
            
        except Exception as e:
            logger.error(f"监控循环错误: {str(e)}")
            time.sleep(30)

@app.get("/")
async def root():
    """服务状态"""
    return {
        "service": "monitoring-service",
        "version": "3.0.0",
        "status": "running",
        "port": 8006,
        "endpoints": {
            "status": "GET /status - 所有服务状态",
            "alerts": "GET /alerts - 告警列表",
            "metrics": "GET /metrics - 指标数据",
            "start": "POST /start - 开始监控",
            "stop": "POST /stop - 停止监控",
            "health": "GET /health - 健康检查"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "monitoring_active": monitoring_active,
        "services_monitored": len(SERVICES_TO_MONITOR)
    }

@app.get("/status")
async def get_all_status():
    """获取所有服务状态"""
    return {
        "timestamp": datetime.now().isoformat(),
        "monitoring_active": monitoring_active,
        "services": service_status,
        "summary": {
            "total": len(service_status),
            "healthy": sum(1 for s in service_status.values() if s["status"] == "healthy"),
            "unhealthy": sum(1 for s in service_status.values() if s["status"] == "unhealthy"),
            "down": sum(1 for s in service_status.values() if s["status"] == "down")
        }
    }

@app.get("/status/{service_name}")
async def get_service_status(service_name: str):
    """获取单个服务状态"""
    if service_name not in service_status:
        raise HTTPException(status_code=404, detail="服务未找到")
    
    return service_status[service_name]

@app.get("/alerts")
async def get_alerts(resolved: bool = False, limit: int = 50):
    """获取告警列表"""
    filtered_alerts = [a for a in alerts if a["resolved"] == resolved]
    return {
        "total": len(filtered_alerts),
        "resolved": resolved,
        "alerts": sorted(filtered_alerts, key=lambda x: x["timestamp"], reverse=True)[:limit]
    }

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """解决告警"""
    for alert in alerts:
        if alert["id"] == alert_id:
            alert["resolved"] = True
            alert["resolved_at"] = datetime.now().isoformat()
            return {"message": "告警已解决", "alert": alert}
    
    raise HTTPException(status_code=404, detail="告警未找到")

@app.get("/metrics")
async def get_metrics(service: Optional[str] = None, metric_type: Optional[str] = None, limit: int = 100):
    """获取指标数据"""
    filtered_metrics = metrics
    
    if service:
        filtered_metrics = [m for m in filtered_metrics if m["service"] == service]
    
    if metric_type:
        filtered_metrics = [m for m in filtered_metrics if m["metric_type"] == metric_type]
    
    return {
        "total": len(filtered_metrics),
        "metrics": sorted(filtered_metrics, key=lambda x: x["timestamp"], reverse=True)[:limit]
    }

@app.get("/metrics/summary/{service_name}")
async def get_metrics_summary(service_name: str, hours: int = 24):
    """获取指标摘要"""
    if service_name not in service_metrics:
        return {"service": service_name, "metrics": {}}
    
    time_threshold = datetime.now() - timedelta(hours=hours)
    
    summary = {}
    for metric_type, metric_list in service_metrics[service_name].items():
        recent_metrics = [
            m for m in metric_list 
            if datetime.fromisoformat(m["timestamp"]) > time_threshold
        ]
        
        if recent_metrics:
            values = [m["value"] for m in recent_metrics]
            summary[metric_type] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else 0
            }
    
    return {
        "service": service_name,
        "time_range": f"last_{hours}_hours",
        "metrics": summary
    }

@app.post("/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """开始监控"""
    global monitoring_active, monitoring_thread
    
    if monitoring_active:
        return {"message": "监控已在运行", "status": "already_running"}
    
    monitoring_active = True
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    
    logger.info("监控服务已启动")
    return {"message": "监控已启动", "status": "started"}

@app.post("/stop")
async def stop_monitoring():
    """停止监控"""
    global monitoring_active
    
    if not monitoring_active:
        return {"message": "监控未运行", "status": "already_stopped"}
    
    monitoring_active = False
    
    if monitoring_thread and monitoring_thread.is_alive():
        monitoring_thread.join(timeout=5)
    
    logger.info("监控服务已停止")
    return {"message": "监控已停止", "status": "stopped"}

@app.on_event("startup")
async def startup_event():
    """应用启动时自动开始监控"""
    background_tasks = BackgroundTasks()
    await start_monitoring(background_tasks)

if __name__ == "__main__":
    import uvicorn
    logger.info("启动监控服务 (端口: 8006)")
    uvicorn.run(app, host="0.0.0.0", port=8006, reload=True)