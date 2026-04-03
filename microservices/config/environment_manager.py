"""
环境变量管理器 - 生产环境配置
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

class EnvironmentManager:
    """环境变量管理器"""
    
    def __init__(self, env_file: str = ".env", config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.env_file = Path(env_file)
        self.config_file = self.config_dir / "environment.yaml"
        
        # 加载环境变量
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # 加载配置
        self.config = self.load_config()
        
        # 设置默认值
        self.set_defaults()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def set_defaults(self):
        """设置默认配置"""
        defaults = {
            "services": {
                "validator": {
                    "port": 8001,
                    "host": "0.0.0.0",
                    "debug": False,
                    "log_level": "INFO"
                },
                "security": {
                    "port": 8002,
                    "host": "0.0.0.0",
                    "debug": False,
                    "log_level": "INFO"
                },
                "performance": {
                    "port": 8003,
                    "host": "0.0.0.0",
                    "debug": False,
                    "log_level": "INFO"
                },
                "compliance": {
                    "port": 8004,
                    "host": "0.0.0.0",
                    "debug": False,
                    "log_level": "INFO"
                },
                "reporting": {
                    "port": 8005,
                    "host": "0.0.0.0",
                    "debug": False,
                    "log_level": "INFO"
                },
                "monitoring": {
                    "port": 8006,
                    "host": "0.0.0.0",
                    "debug": False,
                    "log_level": "INFO"
                },
                "deep_analysis": {
                    "port": 8007,
                    "host": "0.0.0.0",
                    "debug": False,
                    "log_level": "INFO"
                }
            },
            "security": {
                "api_key_required": False,
                "rate_limit_enabled": True,
                "audit_log_enabled": True,
                "cors_enabled": True,
                "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
            },
            "database": {
                "type": "memory",  # memory, sqlite, postgres
                "connection_string": "",
                "pool_size": 10,
                "timeout": 30
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_enabled": True,
                "file_path": "logs/enterprise_framework.log",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "monitoring": {
                "metrics_enabled": True,
                "health_check_interval": 30,
                "alert_enabled": False,
                "alert_email": "",
                "alert_webhook": ""
            },
            "performance": {
                "cache_enabled": True,
                "cache_ttl": 300,
                "compression_enabled": True,
                "timeout_seconds": 60
            }
        }
        
        # 合并默认配置
        for section, values in defaults.items():
            if section not in self.config:
                self.config[section] = values
            else:
                for key, value in values.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
        
        self.save_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 首先检查环境变量
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            # 尝试转换为适当类型
            try:
                if env_value.lower() in ['true', 'false']:
                    return env_value.lower() == 'true'
                elif env_value.isdigit():
                    return int(env_value)
                elif env_value.replace('.', '', 1).isdigit():
                    return float(env_value)
                return env_value
            except:
                return env_value
        
        # 然后检查配置文件
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = True):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到正确位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        if save:
            self.save_config()
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """获取服务配置"""
        service_key = f"services.{service_name}"
        config = self.get(service_key, {})
        
        # 确保有基本配置
        if not config:
            config = {
                "port": 8000,
                "host": "0.0.0.0",
                "debug": False,
                "log_level": "INFO"
            }
        
        return config
    
    def generate_env_file(self, output_file: str = ".env.example"):
        """生成环境变量示例文件"""
        env_vars = [
            "# 企业级审核框架 - 环境变量配置",
            "# 复制此文件为 .env 并修改值",
            "",
            "# 服务配置",
            "VALIDATOR_PORT=8001",
            "VALIDATOR_HOST=0.0.0.0",
            "VALIDATOR_DEBUG=false",
            "",
            "SECURITY_PORT=8002",
            "SECURITY_HOST=0.0.0.0",
            "SECURITY_DEBUG=false",
            "",
            "PERFORMANCE_PORT=8003",
            "PERFORMANCE_HOST=0.0.0.0",
            "PERFORMANCE_DEBUG=false",
            "",
            "COMPLIANCE_PORT=8004",
            "COMPLIANCE_HOST=0.0.0.0",
            "COMPLIANCE_DEBUG=false",
            "",
            "REPORTING_PORT=8005",
            "REPORTING_HOST=0.0.0.0",
            "REPORTING_DEBUG=false",
            "",
            "MONITORING_PORT=8006",
            "MONITORING_HOST=0.0.0.0",
            "MONITORING_DEBUG=false",
            "",
            "DEEP_ANALYSIS_PORT=8007",
            "DEEP_ANALYSIS_HOST=0.0.0.0",
            "DEEP_ANALYSIS_DEBUG=false",
            "",
            "# 安全配置",
            "API_KEY_REQUIRED=false",
            "RATE_LIMIT_ENABLED=true",
            "AUDIT_LOG_ENABLED=true",
            "CORS_ENABLED=true",
            "",
            "# 数据库配置",
            "DATABASE_TYPE=memory",
            "DATABASE_CONNECTION_STRING=",
            "",
            "# 日志配置",
            "LOG_LEVEL=INFO",
            "LOG_FILE_ENABLED=true",
            "LOG_FILE_PATH=logs/enterprise_framework.log",
            "",
            "# 监控配置",
            "METRICS_ENABLED=true",
            "HEALTH_CHECK_INTERVAL=30",
            "",
            "# 性能配置",
            "CACHE_ENABLED=true",
            "CACHE_TTL=300",
            "COMPRESSION_ENABLED=true",
            "",
            "# API密钥（用于测试）",
            "API_KEY_DEMO=demo_key",
            ""
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_vars))
        
        print(f"Environment file generated: {output_file}")
    
    def validate_config(self) -> Dict[str, List[str]]:
        """验证配置"""
        errors = []
        warnings = []
        
        # 检查端口冲突
        ports = set()
        for service_name in ["validator", "security", "performance", "compliance", 
                           "reporting", "monitoring", "deep_analysis"]:
            port = self.get(f"services.{service_name}.port")
            if port:
                if port in ports:
                    errors.append(f"Port conflict: {service_name} uses port {port}")
                else:
                    ports.add(port)
        
        # 检查安全配置
        if self.get("security.api_key_required") and not self.get("security.api_key_demo"):
            warnings.append("API key required but no demo key provided")
        
        # 检查日志配置
        if self.get("logging.file_enabled"):
            log_path = self.get("logging.file_path")
            if not log_path:
                warnings.append("File logging enabled but no file path specified")
        
        return {"errors": errors, "warnings": warnings}

# 全局实例
env_manager = EnvironmentManager()

if __name__ == "__main__":
    print("Testing Environment Manager...")
    
    # 获取配置
    validator_port = env_manager.get("services.validator.port")
    print(f"Validator port: {validator_port}")
    
    # 设置配置
    env_manager.set("services.validator.debug", True)
    print(f"Validator debug: {env_manager.get('services.validator.debug')}")
    
    # 获取服务配置
    service_config = env_manager.get_service_config("validator")
    print(f"Validator config: {service_config}")
    
    # 生成环境文件
    env_manager.generate_env_file()
    
    # 验证配置
    validation = env_manager.validate_config()
    print(f"Validation errors: {validation['errors']}")
    print(f"Validation warnings: {validation['warnings']}")
    
    print("\nEnvironment Manager test completed!")