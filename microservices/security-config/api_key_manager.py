"""
API密钥管理器 - 企业级安全特性
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self, config_dir: str = "security-config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.keys_file = self.config_dir / "api_keys.json"
        self.rate_limits_file = self.config_dir / "rate_limits.json"
        self.audit_log_file = self.config_dir / "audit_log.json"
        
        self.api_keys = self.load_api_keys()
        self.rate_limits = self.load_rate_limits()
        self.audit_log = self.load_audit_log()
    
    def load_api_keys(self) -> Dict[str, Dict]:
        """加载API密钥"""
        if self.keys_file.exists():
            with open(self.keys_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_rate_limits(self) -> Dict[str, Dict]:
        """加载速率限制"""
        if self.rate_limits_file.exists():
            with open(self.rate_limits_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_audit_log(self) -> List[Dict]:
        """加载审计日志"""
        if self.audit_log_file.exists():
            with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_api_keys(self):
        """保存API密钥"""
        with open(self.keys_file, 'w', encoding='utf-8') as f:
            json.dump(self.api_keys, f, indent=2)
    
    def save_rate_limits(self):
        """保存速率限制"""
        with open(self.rate_limits_file, 'w', encoding='utf-8') as f:
            json.dump(self.rate_limits, f, indent=2)
    
    def save_audit_log(self):
        """保存审计日志"""
        # 只保留最近1000条日志
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
        
        with open(self.audit_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, indent=2)
    
    def generate_api_key(self, name: str, permissions: List[str], 
                        rate_limit: int = 100) -> Tuple[str, str]:
        """生成新的API密钥"""
        # 生成密钥ID和密钥
        key_id = secrets.token_hex(8)
        secret_key = secrets.token_hex(32)
        
        # 创建密钥哈希
        key_hash = hashlib.sha256(secret_key.encode()).hexdigest()
        
        # 存储密钥信息
        self.api_keys[key_id] = {
            "name": name,
            "key_hash": key_hash,
            "permissions": permissions,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "enabled": True
        }
        
        # 设置速率限制
        self.rate_limits[key_id] = {
            "limit": rate_limit,
            "used_today": 0,
            "reset_date": datetime.now().date().isoformat()
        }
        
        self.save_api_keys()
        self.save_rate_limits()
        
        # 记录审计日志
        self.log_audit("api_key_generated", {
            "key_id": key_id,
            "name": name,
            "permissions": permissions
        })
        
        return key_id, secret_key
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """验证API密钥"""
        if not api_key or ':' not in api_key:
            return False, "Invalid API key format"
        
        try:
            key_id, secret_key = api_key.split(':', 1)
        except:
            return False, "Invalid API key format"
        
        if key_id not in self.api_keys:
            return False, "API key not found"
        
        key_info = self.api_keys[key_id]
        
        # 检查是否启用
        if not key_info.get("enabled", True):
            return False, "API key disabled"
        
        # 验证密钥
        key_hash = hashlib.sha256(secret_key.encode()).hexdigest()
        if key_hash != key_info["key_hash"]:
            return False, "Invalid API key"
        
        # 检查速率限制
        if not self.check_rate_limit(key_id):
            return False, "Rate limit exceeded"
        
        # 更新最后使用时间
        key_info["last_used"] = datetime.now().isoformat()
        self.save_api_keys()
        
        # 记录使用
        self.increment_rate_limit(key_id)
        
        # 记录审计日志
        self.log_audit("api_key_used", {"key_id": key_id})
        
        return True, key_id
    
    def check_rate_limit(self, key_id: str) -> bool:
        """检查速率限制"""
        if key_id not in self.rate_limits:
            return True
        
        limit_info = self.rate_limits[key_id]
        
        # 检查是否需要重置
        today = datetime.now().date().isoformat()
        if limit_info["reset_date"] != today:
            limit_info["used_today"] = 0
            limit_info["reset_date"] = today
            self.save_rate_limits()
        
        # 检查是否超过限制
        return limit_info["used_today"] < limit_info["limit"]
    
    def increment_rate_limit(self, key_id: str):
        """增加速率限制计数"""
        if key_id in self.rate_limits:
            self.rate_limits[key_id]["used_today"] += 1
            self.save_rate_limits()
    
    def get_key_info(self, key_id: str) -> Optional[Dict]:
        """获取密钥信息"""
        if key_id in self.api_keys:
            info = self.api_keys[key_id].copy()
            
            # 添加速率限制信息
            if key_id in self.rate_limits:
                info["rate_limit"] = self.rate_limits[key_id]
            
            # 计算今日剩余请求
            if key_id in self.rate_limits:
                limit_info = self.rate_limits[key_id]
                info["remaining_today"] = limit_info["limit"] - limit_info["used_today"]
            
            return info
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """撤销API密钥"""
        if key_id in self.api_keys:
            self.api_keys[key_id]["enabled"] = False
            self.save_api_keys()
            
            self.log_audit("api_key_revoked", {"key_id": key_id})
            return True
        return False
    
    def delete_api_key(self, key_id: str) -> bool:
        """删除API密钥"""
        if key_id in self.api_keys:
            del self.api_keys[key_id]
            
            if key_id in self.rate_limits:
                del self.rate_limits[key_id]
            
            self.save_api_keys()
            self.save_rate_limits()
            
            self.log_audit("api_key_deleted", {"key_id": key_id})
            return True
        return False
    
    def list_api_keys(self) -> List[Dict]:
        """列出所有API密钥"""
        keys = []
        for key_id, info in self.api_keys.items():
            key_info = info.copy()
            key_info["key_id"] = key_id
            
            # 添加速率限制信息
            if key_id in self.rate_limits:
                limit_info = self.rate_limits[key_id]
                key_info["rate_limit"] = limit_info
                key_info["remaining_today"] = limit_info["limit"] - limit_info["used_today"]
            
            keys.append(key_info)
        
        return keys
    
    def log_audit(self, action: str, details: Dict):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "ip_address": "127.0.0.1"  # 实际实现中应该获取真实IP
        }
        
        self.audit_log.append(log_entry)
        self.save_audit_log()
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        return self.audit_log[-limit:] if self.audit_log else []
    
    def cleanup_old_logs(self, days: int = 30):
        """清理旧日志"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()
        
        self.audit_log = [
            log for log in self.audit_log 
            if log["timestamp"] > cutoff_iso
        ]
        
        self.save_audit_log()

# 全局实例
api_key_manager = APIKeyManager()

if __name__ == "__main__":
    # 测试API密钥管理器
    print("Testing API Key Manager...")
    
    # 生成测试密钥
    key_id, secret_key = api_key_manager.generate_api_key(
        name="Test Client",
        permissions=["analyze", "read_results"],
        rate_limit=50
    )
    
    print(f"Generated API Key: {key_id}:{secret_key[:8]}...")
    
    # 验证密钥
    api_key = f"{key_id}:{secret_key}"
    valid, result = api_key_manager.validate_api_key(api_key)
    
    print(f"Validation: {valid}, Result: {result}")
    
    # 获取密钥信息
    info = api_key_manager.get_key_info(key_id)
    print(f"Key Info: {info['name']}, Permissions: {info['permissions']}")
    
    # 列出所有密钥
    keys = api_key_manager.list_api_keys()
    print(f"Total keys: {len(keys)}")
    
    # 获取审计日志
    logs = api_key_manager.get_audit_log(5)
    print(f"Recent audit logs: {len(logs)}")
    
    print("\nAPI Key Manager test completed!")