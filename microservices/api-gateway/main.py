"""
企业级审核框架 - API网关服务
负责请求路由、认证、限流、监控等核心功能
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, generate_latest

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus指标
REQUEST_COUNT = Counter(
    'api_gateway_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_gateway_request_duration_seconds',
    'API request latency in seconds',
    ['method', 'endpoint']
)

# 数据模型
class AuditRequest(BaseModel):
    """审核请求模型"""
    skill_id: str = Field(..., description="技能ID")
    skill_path: str = Field(..., description="技能路径")
    priority: str = Field("normal", description="优先级: low/normal/high")
    callback_url: Optional[str] = Field(None, description="回调URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class AuditResponse(BaseModel):
    """审核响应模型"""
    audit_id: str = Field(..., description="审核ID")
    status: str = Field(..., description="状态: pending/processing/completed/failed")
    estimated_time: Optional[int] = Field(None, description="预计完成时间(秒)")
    message: Optional[str] = Field(None, description="消息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="状态: healthy/unhealthy")
    services: Dict[str, str] = Field(..., description="各服务状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

# 应用初始化
app = FastAPI(
    title="企业级审核框架 API网关",
    description="OpenClaw技能审核企业级解决方案",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis连接池
redis_pool = redis.ConnectionPool(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# 微服务端点配置
SERVICE_ENDPOINTS = {
    "validator": os.getenv("VALIDATOR_SERVICE", "http://validator-service:8001"),
    "security": os.getenv("SECURITY_SERVICE", "http://security-service:8002"),
    "performance": os.getenv("PERFORMANCE_SERVICE", "http://performance-service:8003"),
    "compliance": os.getenv("COMPLIANCE_SERVICE", "http://compliance-service:8004"),
    "reporting": os.getenv("REPORTING_SERVICE", "http://reporting-service:8005"),
}

# 依赖注入
def get_redis():
    """获取Redis连接"""
    return redis.Redis(connection_pool=redis_pool)

async def rate_limit(request: Request, redis_client: redis.Redis = Depends(get_redis)):
    """速率限制中间件"""
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # 每分钟最多100个请求
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    
    if current > 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return True

# 中间件：请求监控
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """监控所有请求"""
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # 记录指标
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "")
        response.headers["X-Response-Time"] = str(round((time.time() - start_time) * 1000, 2))
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {method} {endpoint} - {str(e)}")
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
        raise

# 路由定义
@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "Enterprise Audit Framework API Gateway",
        "version": "3.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(redis_client: redis.Redis = Depends(get_redis)):
    """健康检查端点"""
    services_status = {}
    
    # 检查Redis
    try:
        redis_client.ping()
        services_status["redis"] = "healthy"
    except:
        services_status["redis"] = "unhealthy"
    
    # 检查微服务
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, endpoint in SERVICE_ENDPOINTS.items():
            try:
                response = await client.get(f"{endpoint}/health")
                services_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                services_status[service_name] = "unhealthy"
    
    # 确定总体状态
    overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        services=services_status,
        timestamp=datetime.now()
    )

@app.post("/audit", response_model=AuditResponse, dependencies=[Depends(rate_limit)])
async def create_audit(request: AuditRequest, redis_client: redis.Redis = Depends(get_redis)):
    """创建新的审核任务"""
    # 生成审核ID
    audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.skill_id[:8]}"
    
    # 存储审核任务到Redis
    audit_data = {
        "audit_id": audit_id,
        "skill_id": request.skill_id,
        "skill_path": request.skill_path,
        "priority": request.priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "metadata": request.metadata
    }
    
    redis_client.hset(f"audit:{audit_id}", mapping=audit_data)
    redis_client.expire(f"audit:{audit_id}", 3600)  # 1小时过期
    
    # 将任务加入队列
    queue_name = f"audit_queue:{request.priority}"
    redis_client.lpush(queue_name, audit_id)
    
    logger.info(f"Created audit task: {audit_id} for skill: {request.skill_id}")
    
    return AuditResponse(
        audit_id=audit_id,
        status="pending",
        estimated_time=300,  # 默认5分钟
        message="Audit task created and queued for processing",
        created_at=datetime.now()
    )

@app.get("/audit/{audit_id}", response_model=AuditResponse)
async def get_audit_status(audit_id: str, redis_client: redis.Redis = Depends(get_redis)):
    """获取审核任务状态"""
    audit_data = redis_client.hgetall(f"audit:{audit_id}")
    
    if not audit_data:
        raise HTTPException(status_code=404, detail="Audit task not found")
    
    return AuditResponse(
        audit_id=audit_data.get("audit_id", audit_id),
        status=audit_data.get("status", "unknown"),
        estimated_time=int(audit_data.get("estimated_time", 0)) if audit_data.get("estimated_time") else None,
        message=audit_data.get("message"),
        created_at=datetime.fromisoformat(audit_data.get("created_at", datetime.now().isoformat()))
    )

@app.get("/metrics")
async def metrics():
    """Prometheus指标端点"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

@app.get("/services")
async def list_services():
    """列出所有可用的微服务"""
    return {
        "services": [
            {
                "name": name,
                "endpoint": endpoint,
                "description": {
                    "validator": "技能验证和基础检查",
                    "security": "AI驱动的安全分析",
                    "performance": "性能测试和优化建议",
                    "compliance": "合规性检查(GDPR/SOC2)",
                    "reporting": "报告生成和可视化"
                }.get(name, "Unknown service")
            }
            for name, endpoint in SERVICE_ENDPOINTS.items()
        ]
    }

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": request.url.path,
            "method": request.method,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )