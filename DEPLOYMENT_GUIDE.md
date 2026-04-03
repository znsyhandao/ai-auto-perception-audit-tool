# 企业级审核框架 v3.0 - 部署指南

## 📍 当前状态
✅ 所有核心模块测试通过 (7/7)
✅ 依赖包已安装完成
✅ 部署脚本已就绪

## 🚀 部署步骤

### 步骤1: 切换到正确目录
```powershell
# 切换到企业级框架目录
cd "D:\OpenClaw_TestingFramework"

# 验证当前目录
pwd
# 应该显示: D:\OpenClaw_TestingFramework
```

### 步骤2: 运行部署脚本
```powershell
# 运行PowerShell部署脚本
.\deploy_enterprise.ps1
```

### 步骤3: 验证部署
部署完成后，访问以下服务：

1. **API网关**: http://localhost:8000
2. **监控面板**: http://localhost:3000 (用户名: admin, 密码: enterprise123)
3. **Prometheus**: http://localhost:9090
4. **RabbitMQ管理**: http://localhost:15672 (用户名: admin, 密码: enterprise123)

### 微服务端点:
- 验证服务: http://localhost:8001
- 安全服务: http://localhost:8002
- 性能服务: http://localhost:8003
- 合规服务: http://localhost:8004
- 报告服务: http://localhost:8005

## 🔧 如果遇到问题

### 问题1: Docker未安装
```powershell
# 检查Docker
docker --version

# 如果未安装，需要先安装Docker Desktop for Windows
# 下载地址: https://www.docker.com/products/docker-desktop/
```

### 问题2: Docker Compose未安装
```powershell
# 检查Docker Compose
docker-compose --version

# Docker Desktop通常包含Docker Compose
# 如果没有，可以单独安装
```

### 问题3: 端口冲突
如果端口被占用，可以修改 `docker-compose.yml` 文件中的端口映射。

## 📊 测试部署

### 测试1: 检查服务状态
```powershell
# 查看所有容器状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 测试2: 测试API网关
```powershell
# 使用curl测试API网关
curl http://localhost:8000/

# 健康检查
curl http://localhost:8000/health
```

### 测试3: 测试验证服务
```powershell
# 测试验证服务
curl http://localhost:8001/
```

## 🎯 快速命令参考

```powershell
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [服务名]

# 进入容器
docker-compose exec [服务名] bash

# 查看资源使用
docker stats
```

## 💡 生产环境建议

### 1. 安全配置
- 修改默认密码 (admin/enterprise123)
- 启用HTTPS
- 配置防火墙规则
- 设置访问控制

### 2. 监控告警
- 配置Grafana告警
- 设置Prometheus告警规则
- 集成邮件/短信通知

### 3. 备份恢复
- 定期备份数据库
- 配置数据持久化卷
- 测试恢复流程

### 4. 高可用
- 配置多个实例
- 设置负载均衡
- 实现故障转移

## 📞 支持

如果遇到任何问题，可以：

1. 查看日志: `docker-compose logs -f`
2. 检查容器状态: `docker-compose ps`
3. 重启服务: `docker-compose restart`
4. 重新部署: `docker-compose down && docker-compose up -d`

## 🎉 成功部署标志

✅ 所有容器状态为 "Up"
✅ API网关可访问 (http://localhost:8000)
✅ 监控面板可访问 (http://localhost:3000)
✅ 微服务健康检查通过
✅ 可以提交审核任务

---

**现在请运行以下命令开始部署:**
```powershell
cd "D:\OpenClaw_TestingFramework"
.\deploy_enterprise.ps1
```