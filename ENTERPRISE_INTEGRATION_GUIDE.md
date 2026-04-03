# 企业级框架集成文档

## 概述
数学审核服务已成功集成到企业级审核框架中。

## 服务配置

### 数学审核服务
- **名称**: Mathematical Audit Service
- **版本**: 4.0.0
- **端口**: 8040
- **协议**: HTTP
- **健康检查**: `GET http://localhost:8040/health`

### 数学方法
服务支持以下数学定理方法：
1. **麦克劳林级数分析** - 代码复杂度特征工程
2. **泰勒级数复杂度** - 算法性能分析
3. **傅里叶变换模式** - 代码结构模式识别
4. **矩阵分解依赖** - 模块依赖分析
5. **数学证明验证** - 代码属性验证

## API端点

### 直接访问
- **健康检查**: `GET http://localhost:8040/health`
- **数学审核**: `POST http://localhost:8040/audit`
- **API文档**: `GET http://localhost:8040/docs`

### 审核请求格式
```json
{
  "skill_id": "your-skill-id",
  "skill_path": "/path/to/skill",
  "audit_types": ["maclaurin", "taylor", "fourier", "matrix", "proof"],
  "mathematical_depth": 5
}
```

## 配置文件

### 1. 服务注册表
`enterprise_service_registry.json` - 服务元数据和配置

### 2. API网关配置
`api_gateway_config.json` - 网关路由配置

### 3. 部署配置
`deployment_config.json` - 部署环境和设置

## 集成测试

运行集成测试：
```bash
python test_enterprise_integration.py
```

测试包括：
1. 服务健康检查
2. 数学审核功能测试
3. 配置文件验证

## 验证状态

### 当前状态
- ✅ 服务部署成功 (端口8040)
- ✅ 健康检查通过
- ✅ 数学审核功能正常
- ✅ 配置文件创建完成
- ✅ 集成测试通过

### 下一步
1. 集成到完整的微服务架构
2. 配置API网关路由
3. 设置服务发现和负载均衡
4. 配置监控和告警

## 技术支持

如有问题，请检查：
1. 服务日志：查看服务启动和运行日志
2. 配置文件：验证JSON格式和内容
3. 网络连接：确保端口可访问
4. 依赖检查：验证Python包依赖

## 版本历史
- **v4.0.0** (2026-03-31): 初始企业级集成版本
