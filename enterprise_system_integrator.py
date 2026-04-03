#!/usr/bin/env python3
"""
企业级审核框架系统集成器
将AI检测器、沙箱、区块链、Web界面等模块整合为完整系统
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnterpriseSystemIntegrator:
    """企业级系统集成器"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.dirname(os.path.abspath(__file__)))
        self.modules = {}
        self.system_status = {
            "status": "initializing",
            "modules": {},
            "health": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 发现和加载模块
        self.discover_modules()
    
    def discover_modules(self):
        """发现所有可用模块"""
        logger.info("Discovering enterprise modules...")
        
        # AI/ML模块
        ai_ml_path = self.base_dir / "ai-ml" / "inference" / "ai_security_detector.py"
        if ai_ml_path.exists():
            self.modules["ai_security_detector"] = {
                "path": ai_ml_path,
                "type": "ai_ml",
                "description": "AI驱动的安全检测器",
                "status": "available"
            }
        
        # 沙箱模块
        sandbox_path = self.base_dir / "sandbox" / "firecracker" / "sandbox_manager.py"
        if sandbox_path.exists():
            self.modules["sandbox_manager"] = {
                "path": sandbox_path,
                "type": "sandbox",
                "description": "企业级沙箱执行环境",
                "status": "available"
            }
        
        # 区块链模块
        blockchain_path = self.base_dir / "blockchain" / "verification" / "blockchain_verifier.py"
        if blockchain_path.exists():
            self.modules["blockchain_verifier"] = {
                "path": blockchain_path,
                "type": "blockchain",
                "description": "区块链验证模块",
                "status": "available"
            }
        
        # Web界面模块
        dashboard_path = self.base_dir / "dashboard" / "backend" / "main.py"
        if dashboard_path.exists():
            self.modules["dashboard_backend"] = {
                "path": dashboard_path,
                "type": "dashboard",
                "description": "Web管理界面后端",
                "status": "available"
            }
        
        # 微服务模块
        microservices_dir = self.base_dir / "microservices"
        if microservices_dir.exists():
            for service_dir in microservices_dir.iterdir():
                if service_dir.is_dir():
                    main_file = service_dir / "main.py"
                    if main_file.exists():
                        self.modules[f"microservice_{service_dir.name}"] = {
                            "path": main_file,
                            "type": "microservice",
                            "description": f"微服务: {service_dir.name}",
                            "status": "available"
                        }
        
        logger.info(f"Discovered {len(self.modules)} modules")
    
    def check_module_health(self, module_name: str) -> Dict[str, Any]:
        """检查模块健康状态"""
        module = self.modules.get(module_name)
        if not module:
            return {"status": "not_found", "error": f"Module {module_name} not found"}
        
        try:
            # 检查文件存在性
            if not module["path"].exists():
                return {"status": "unhealthy", "error": "File not found"}
            
            # 检查文件大小
            file_size = module["path"].stat().st_size
            if file_size < 100:  # 小于100字节可能是空文件
                return {"status": "unhealthy", "error": "File too small"}
            
            # 检查文件内容
            with open(module["path"], 'r', encoding='utf-8') as f:
                content = f.read(1000)  # 读取前1000字符
                if not content.strip():
                    return {"status": "unhealthy", "error": "Empty file"}
            
            return {
                "status": "healthy",
                "file_size": file_size,
                "last_modified": datetime.fromtimestamp(module["path"].stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def check_system_health(self) -> Dict[str, Any]:
        """检查系统整体健康状态"""
        logger.info("Checking system health...")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "overall_status": "healthy",
            "issues": []
        }
        
        # 检查每个模块
        for module_name in self.modules:
            module_health = self.check_module_health(module_name)
            health_report["modules"][module_name] = module_health
            
            if module_health["status"] != "healthy":
                health_report["overall_status"] = "unhealthy"
                health_report["issues"].append({
                    "module": module_name,
                    "error": module_health.get("error", "Unknown error")
                })
        
        # 检查目录结构
        required_dirs = ["microservices", "ai-ml", "sandbox", "blockchain", "dashboard"]
        for dir_name in required_dirs:
            dir_path = self.base_dir / dir_name
            if not dir_path.exists():
                health_report["overall_status"] = "unhealthy"
                health_report["issues"].append({
                    "component": "directory",
                    "error": f"Required directory missing: {dir_name}"
                })
        
        self.system_status = health_report
        return health_report
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """生成系统集成报告"""
        health = self.check_system_health()
        
        report = {
            "system_name": "Enterprise Audit Framework v3.0",
            "timestamp": datetime.now().isoformat(),
            "base_directory": str(self.base_dir),
            "health_summary": health,
            "module_summary": {
                "total_modules": len(self.modules),
                "by_type": {},
                "by_status": {"healthy": 0, "unhealthy": 0, "not_found": 0}
            },
            "architecture": {
                "layers": [
                    {
                        "name": "Presentation Layer",
                        "modules": ["dashboard_backend"],
                        "description": "Web管理界面和API网关"
                    },
                    {
                        "name": "Business Logic Layer",
                        "modules": [m for m in self.modules if "microservice" in m],
                        "description": "微服务业务逻辑"
                    },
                    {
                        "name": "AI/ML Layer",
                        "modules": ["ai_security_detector"],
                        "description": "AI驱动的分析和检测"
                    },
                    {
                        "name": "Security Layer",
                        "modules": ["sandbox_manager"],
                        "description": "安全隔离和执行环境"
                    },
                    {
                        "name": "Blockchain Layer",
                        "modules": ["blockchain_verifier"],
                        "description": "区块链验证和不可篡改存储"
                    }
                ]
            },
            "deployment_ready": health["overall_status"] == "healthy",
            "next_steps": []
        }
        
        # 统计模块类型和状态
        for module_name, module_info in self.modules.items():
            module_type = module_info["type"]
            report["module_summary"]["by_type"][module_type] = report["module_summary"]["by_type"].get(module_type, 0) + 1
        
        for module_name, health_info in health["modules"].items():
            status = health_info["status"]
            report["module_summary"]["by_status"][status] = report["module_summary"]["by_status"].get(status, 0) + 1
        
        # 生成下一步建议
        if health["overall_status"] == "healthy":
            report["next_steps"].append("✅ 系统健康，可以开始部署")
            report["next_steps"].append("🔧 运行 docker-compose up 启动所有服务")
            report["next_steps"].append("🌐 访问 http://localhost:8000 查看API网关")
            report["next_steps"].append("📊 访问 http://localhost:3000 查看监控面板")
        else:
            report["next_steps"].append("⚠️ 系统存在问题，需要修复")
            for issue in health["issues"]:
                report["next_steps"].append(f"🔧 修复: {issue['module']} - {issue['error']}")
        
        return report
    
    def create_deployment_script(self, output_path: str = None):
        """创建部署脚本"""
        if not output_path:
            output_path = self.base_dir / "deploy_enterprise.sh"
        
        script_content = f"""#!/bin/bash
# 企业级审核框架部署脚本
# 生成时间: {datetime.now().isoformat()}

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
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(output_path, 0o755)
        
        logger.info(f"部署脚本已创建: {output_path}")
        return output_path
    
    def create_test_script(self, skill_path: str = None):
        """创建测试脚本"""
        if not skill_path:
            skill_path = str(self.base_dir.parent / "releases" / "AISleepGen" / "v1.0.7_fixed")
        
        test_script = f"""#!/usr/bin/env python3
"""
        test_script += f"""
# 企业级审核框架测试脚本
import sys
import os
sys.path.append(r'{self.base_dir}')

from enterprise_system_integrator import EnterpriseSystemIntegrator

def test_enterprise_framework():
    \"\"\"测试企业级审核框架\"\"\"
    print("[TEST] 开始测试企业级审核框架 v3.0")
    print("=" * 60)
    
    # 初始化集成器
    integrator = EnterpriseSystemIntegrator()
    
    # 检查系统健康
    print("[CHECK] 检查系统健康状态...")
    health = integrator.check_system_health()
    
    if health["overall_status"] == "healthy":
        print("[OK] 系统健康状态: 良好")
        print(f"[STATS] 模块数量: {{len(integrator.modules)}}")
        
        # 生成集成报告
        print("[REPORT] 生成集成报告...")
        report = integrator.generate_integration_report()
        
        print("\\n[ARCHITECTURE] 架构层次:")
        for layer in report["architecture"]["layers"]:
            print(f"  * {{layer['name']}}: {{layer['description']}}")
            print(f"    模块: {{', '.join(layer['modules'])}}")
        
        print("\\n[STATS] 模块统计:")
        print(f"  总计: {{report['module_summary']['total_modules']}}")
        for module_type, count in report["module_summary"]["by_type"].items():
            print(f"  {{module_type}}: {{count}}")
        
        print("\\n[DEPLOYMENT] 部署就绪: 是")
        print("\\n[NEXT] 下一步:")
        for step in report["next_steps"]:
            print(f"  {{step}}")
        
    else:
        print("[ERROR] 系统健康状态: 存在问题")
        print("\\n[WARNING] 发现的问题:")
        for issue in health["issues"]:
            print(f"  * {{issue['module']}}: {{issue['error']}}")
        
        print("\\n[FIX] 需要修复以上问题才能继续")
    
    print("=" * 60)
    print("[TEST] 测试完成")

if __name__ == "__main__":
    test_enterprise_framework()
"""
        
        test_path = self.base_dir / "test_enterprise_framework.py"
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        logger.info(f"测试脚本已创建: {test_path}")
        return test_path

def main():
    """主函数"""
    print("""
    ============================================================
        企业级审核框架 v3.0 - 系统集成器                  
        Enterprise Audit Framework v3.0 - Integrator      
    ============================================================
    """)
    
    # 初始化集成器
    base_dir = os.path.dirname(os.path.abspath(__file__))
    integrator = EnterpriseSystemIntegrator(base_dir)
    
    # 检查系统健康
    print("[CHECK] 检查系统健康状态...")
    health = integrator.check_system_health()
    
    if health["overall_status"] == "healthy":
        print("[OK] 系统健康状态: 良好")
    else:
        print("[ERROR] 系统健康状态: 存在问题")
        print("\\n[WARNING] 发现的问题:")
        for issue in health["issues"]:
            print(f"  * {issue['module']}: {issue['error']}")
        print("\\n请修复以上问题后重新运行。")
        return
    
    # 生成集成报告
    print("\\n[REPORT] 生成集成报告...")
    report = integrator.generate_integration_report()
    
    # 显示报告摘要
    print("\\n[ARCHITECTURE] 架构摘要:")
    for layer in report["architecture"]["layers"]:
        print(f"  * {layer['name']}: {layer['description']}")
    
    print(f"\\n[STATS] 模块统计: 总计 {report['module_summary']['total_modules']} 个模块")
    for module_type, count in report["module_summary"]["by_type"].items():
        print(f"  {module_type}: {count}")
    
    print(f"\\n[DEPLOYMENT] 部署就绪: {'是' if report['deployment_ready'] else '否'}")
    
    # 创建部署脚本
    print("\\n[SCRIPT] 创建部署脚本...")
    deploy_script = integrator.create_deployment_script()
    print(f"  已创建: {deploy_script}")
    
    # 创建测试脚本
    print("\\n[TEST] 创建测试脚本...")
    test_script = integrator.create_test_script()
    print(f"  已创建: {test_script}")
    
    print("""
    ============================================================
                        [SUCCESS] 集成完成！                        
                                                                
      下一步操作：                                            
      1. 运行部署脚本: ./deploy_enterprise.sh                 
      2. 运行测试脚本: python test_enterprise_framework.py    
      3. 访问 http://localhost:8000 查看API网关               
      4. 访问 http://localhost:3000 查看监控面板              
    ============================================================
    """)

if __name__ == "__main__":
    main()