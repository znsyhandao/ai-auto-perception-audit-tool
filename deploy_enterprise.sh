#!/bin/bash
# 企业级审核框架部署脚本
# 生成时间: 2026-03-30T13:48:48.822287

set -e

echo "[START] 开始部署企业级审核框架 v3.0"
echo "=========================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[ERROR] Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "[OK] Docker和Docker Compose已安装"

# 创建必要的目录
echo "[DIR] 创建数据目录..."
mkdir -p data/mongodb data/redis data/timescaledb data/neo4j data/prometheus data/grafana data/rabbitmq

# 设置权限
echo "[PERM] 设置目录权限..."
chmod -R 755 data/

# 启动服务
echo "[SERVICE] 启动企业级审核框架服务..."
docker-compose up -d

echo "[WAIT] 等待服务启动..."
sleep 10

# 检查服务状态
echo "[STATUS] 检查服务状态..."
docker-compose ps

echo ""
echo "=========================================="
echo "[SUCCESS] 部署完成！"
echo ""
echo "访问以下服务："
echo "API网关: http://localhost:8000"
echo "监控面板: http://localhost:3000 (admin/enterprise123)"
echo "Prometheus: http://localhost:9090"
echo "RabbitMQ管理: http://localhost:15672 (admin/enterprise123)"
echo ""
echo "微服务端点："
echo "验证服务: http://localhost:8001"
echo "安全服务: http://localhost:8002"
echo "性能服务: http://localhost:8003"
echo "合规服务: http://localhost:8004"
echo "报告服务: http://localhost:8005"
echo ""
echo "使用以下命令管理服务："
echo "查看日志: docker-compose logs -f"
echo "重启服务: docker-compose restart"
echo "停止服务: docker-compose down"
echo "=========================================="
